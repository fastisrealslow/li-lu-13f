const dataRoot = 'https://fastisrealslow.github.io/li-lu-13f/';
const publicMcp = 'https://li-lu-13f.pages.dev/mcp';
const encoder = new TextEncoder();
const readOnly = {readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false};
const tool = {
  name: 'compare_investor_changes',
  description: 'Compare one security across investors’ latest published 13F comparisons. Reports may cover different quarters. Unavailable data or a missing match is not evidence of zero holdings. Option and principal rows are separate. Optionally return a CSV.',
  inputSchema: {
    type: 'object', required: ['ticker'], additionalProperties: false,
    properties: {
      ticker: {type: 'string', description: 'US ticker as filed or displayed, e.g. NVDA or BRK.B.'},
      format: {type: 'string', enum: ['json', 'csv'], default: 'json'}
    }
  },
  annotations: readOnly
};
const watchlistTool = {
  name: 'export_watchlist_report',
  description: 'Export a bilingual CSV of selected investors’ US 13F changes, Hong Kong interest forms and issuer spin-off filings. A separate row type reports coverage so an empty result is not mistaken for no change.',
  inputSchema: {
    type: 'object', required: ['investors', 'tickers'], additionalProperties: false,
    properties: {
      investors: {type: 'array', minItems: 1, maxItems: 5, uniqueItems: true, items: {type: 'string', maxLength: 31}},
      tickers: {type: 'array', minItems: 1, maxItems: 12, uniqueItems: true, items: {type: 'string', maxLength: 20}},
      days: {type: 'integer', minimum: 1, maximum: 90, default: 30},
      offset: {type: 'integer', minimum: 0, maximum: 500, default: 0, description: 'Use the preceding response’s nextOffset to export the next page.'}
    }
  },
  annotations: readOnly
};

function toolArguments(method, args) {
  if (!args || typeof args !== 'object' || Array.isArray(args)) return null;
  const keys = Object.keys(args);
  if (method === tool.name) {
    if (keys.some(key => !['ticker', 'format'].includes(key)) ||
        typeof args.ticker !== 'string' || !/^[A-Z0-9][A-Z0-9./-]{0,14}$/i.test(args.ticker.trim()) ||
        (Object.hasOwn(args, 'format') && !['json', 'csv'].includes(args.format))) return null;
    return {ticker: canonicalTicker(args.ticker), format: args.format};
  }
  if (method !== watchlistTool.name || keys.some(key => !['investors', 'tickers', 'days', 'offset'].includes(key))) return null;
  const validList = (value, max, pattern) => Array.isArray(value) && value.length >= 1 && value.length <= max &&
    new Set(value).size === value.length && value.every(item => typeof item === 'string' && pattern.test(item));
  const days = Object.hasOwn(args, 'days') ? args.days : 30;
  const offset = Object.hasOwn(args, 'offset') ? args.offset : 0;
  if (!validList(args.investors, 5, /^[a-z][a-z0-9_]{0,30}$/) ||
      !validList(args.tickers, 12, /^[A-Z0-9][A-Z0-9./-]{0,19}$/i) ||
      !Number.isInteger(days) || days < 1 || days > 90 ||
      !Number.isInteger(offset) || offset < 0 || offset > 500) return null;
  return {investors: args.investors, tickers: args.tickers, days, offset};
}

function json(body, status = 200, headers = {}) {
  return Response.json(body, {status, headers: {'Cache-Control': 'no-store', ...headers}});
}

async function authorized(request, secret) {
  const supplied = /^Bearer ([A-Za-z0-9_-]{32,128})$/i.exec(request.headers.get('Authorization') ?? '')?.[1];
  if (!supplied) return false;
  const hash = token => crypto.subtle.digest('SHA-256', encoder.encode(token));
  const [actual, expected] = (await Promise.all([hash(supplied), hash(secret)])).map(x => new Uint8Array(x));
  let difference = 0;
  for (let i = 0; i < expected.length; i++) difference |= actual[i] ^ expected[i];
  return difference === 0;
}

async function load(path, signal) {
  const response = await fetch(dataRoot + path, {signal, redirect: 'error', cf: {cacheTtl: 120}});
  if (!response.ok) throw new Error('Published data unavailable');
  return response.json();
}

function canonicalTicker(value) {
  return String(value ?? '').trim().toUpperCase().replace(/[./-]([AB])$/, '.$1');
}

function secUrl(source) {
  const url = typeof source === 'string' ? source : source?.url;
  return /^https:\/\/www\.sec\.gov\/Archives\/edgar\/data\/\d+\/[\d\w./-]+$/.test(url ?? '') ? url : null;
}

function investorRows(person, snapshot, ticker) {
  const base = {
    investorId: person.id, investorName: person.name, investorNameEn: person.nameEn,
    quarter: snapshot.quarter, previousQuarter: snapshot.previousQuarter,
    comparisonState: snapshot.comparisonState, displayLimit: snapshot.displayScope?.limit ?? null,
    filingUrl: secUrl(snapshot.filingSource), previousFilingUrl: secUrl(snapshot.previousFilingSource)
  };
  const positions = snapshot.rows.filter(row => canonicalTicker(row.ticker) === ticker);
  if (!positions.length) {
    const comparable = ['comparable', 'partial', 'scope_partial'].includes(snapshot.comparisonState);
    return [{...base, result: comparable ? 'no_match_in_reported_scope' : 'comparison_unavailable'}];
  }
  return positions.map(row => ({
    ...base, result: 'matched', ticker: row.ticker, cusip: row.cusip ?? null,
    securityName: row.cnName || row.name, securityClass: row.cls ?? null,
    putCall: row.putCall || null, quantityType: row.shareType || 'SH',
    category: row.category, currentQuantity: row.shares, previousQuantity: row.prevShares ?? null,
    quantityDelta: row.sharesDelta ?? null, quantityChangePct: row.sharesChangePct ?? null,
    splitAdjustment: row.shareAdjustment ?? null, scopeEntry: row.scopeEntry === true
  }));
}

async function compare(ticker) {
  const signal = AbortSignal.timeout(9000);
  const [registry, manifest] = await Promise.all([load('investors.json', signal), load('browser/manifest.json', signal)]);
  const people = registry.investors.filter(p => p.source13F && /^[a-z][a-z0-9_]{0,30}$/.test(p.id));
  if (!people.length || !manifest.investors) throw new Error('No published investor data');
  const rows = [];
  let unavailableInvestors = 0;
  // Workers permit six simultaneous outgoing connections per invocation.
  for (let start = 0; start < people.length; start += 5) {
    const batch = people.slice(start, start + 5);
    const results = await Promise.allSettled(batch.map(async person => {
      const file = manifest.investors[person.id]?.quarterlyChanges?.file;
      if (!new RegExp('^browser/' + person.id + '-quarterly-changes-[a-f0-9]{24}\\.json$').test(file ?? '')) {
        throw new Error('Comparison not published');
      }
      const snapshot = await load(file, signal);
      if (snapshot.version !== 1 || snapshot.investor !== person.id || !Array.isArray(snapshot.rows)) {
        throw new Error('Invalid published comparison');
      }
      return investorRows(person, snapshot, ticker);
    }));
    results.forEach((result, index) => {
      if (result.status === 'fulfilled') rows.push(...result.value);
      else {
        const person = batch[index];
        unavailableInvestors++;
        rows.push({investorId: person.id, investorName: person.name, investorNameEn: person.nameEn, result: 'source_unavailable'});
      }
    });
  }
  if (unavailableInvestors === people.length) throw new Error('All investor sources unavailable');
  const priority = row => row.result === 'matched' ? 0 : row.result === 'no_match_in_reported_scope' ? 1 : 2;
  rows.sort((a, b) => priority(a) - priority(b));
  return {
    ticker, source: dataRoot, retrievedAt: new Date().toISOString(),
    investorCount: people.length,
    matchedInvestors: new Set(rows.filter(row => row.result === 'matched').map(row => row.investorId)).size,
    unavailableInvestors,
    notes: ['Compare each investor against their own previous report. See quarter and comparisonState.',
      'A missing match is not zero holdings. A display limit restricts the securities included.',
      'Options show reported underlying quantities; PRN rows show principal amounts.'],
    rows
  };
}

function csv(rows, columns) {
  const cell = value => {
    if (value == null) return '';
    if (typeof value === 'number' || typeof value === 'boolean') return String(value);
    const text = /^[\s\uFEFF]*[=+@-]|^[\t\r\n]/.test(value) ? "'" + value : String(value);
    return '"' + text.replaceAll('"', '""') + '"';
  };
  return '\uFEFF' + [columns.map(([, title]) => title).join(','), ...rows.map(row =>
    columns.map(([key]) => cell(row[key])).join(',')
  )].join('\r\n') + '\r\n';
}

function comparisonCsv(report) {
  const keys = [
    'investorId', 'investorName', 'investorNameEn', 'quarter', 'previousQuarter', 'comparisonState',
    'displayLimit', 'result', 'ticker', 'cusip', 'securityName', 'securityClass', 'putCall', 'quantityType',
    'category', 'currentQuantity', 'previousQuantity', 'quantityDelta', 'quantityChangePct',
    'splitFactor', 'scopeEntry', 'filingUrl', 'previousFilingUrl'
  ];
  return csv(report.rows.map(row => ({...row, splitFactor: row.splitAdjustment?.factor})), keys.map(key => [key, key]));
}

async function watchlistExport(args) {
  // Reuse the public service's source selection and publication-date rules.
  // Limit export size and expose pagination rather than silently dropping rows.
  const response = await fetch(publicMcp, {
    method: 'POST', redirect: 'error', signal: AbortSignal.timeout(14000),
    headers: {'Content-Type': 'application/json', Accept: 'application/json'},
    body: JSON.stringify({jsonrpc: '2.0', id: 1, method: 'tools/call',
      params: {name: 'get_watchlist_updates', arguments: {...args, limit: 50}}})
  });
  if (!response.ok) throw new Error('Watchlist source unavailable');
  const result = (await response.json()).result;
  if (result?.isError || result?.content?.[0]?.type !== 'text') throw new Error('Watchlist source unavailable');
  const {data} = JSON.parse(result.content[0].text);
  if (!Array.isArray(data?.updates?.items) || !Array.isArray(data.coverage) || !data.window || !data.watchlist) {
    throw new Error('Invalid watchlist report');
  }
  if (!data.coverage.some(entry => !['source_unavailable', 'not_configured', 'not_applicable'].includes(entry.status))) {
    throw new Error('No watchlist sources available');
  }
  const columns = [
    ['rowType', '记录类型 / rowType'], ['source', '来源类型 / source'],
    ['investorName', '投资人 / investor'], ['ticker', '代码 / ticker'], ['name', '名称 / name'],
    ['date', '公告日 / publicationDate'], ['eventDate', '事件日 / eventDate'],
    ['quarter', '报告期 / quarter'], ['previousQuarter', '比较期 / previousQuarter'],
    ['status', '变化或核验状态 / status'], ['entity', '港股申报主体 / reportingEntity'],
    ['shareClass', '股份类别 / shareClass'], ['quantityType', '证券单位 / quantityType'], ['putCall', '期权 / putCall'],
    ['previousQuantity', '之前申报数量 / previousQuantity'], ['currentQuantity', '本次申报数量 / currentQuantity'],
    ['quantityDelta', '申报数量变化 / quantityDelta'], ['quantityChangePct', '申报数量变化百分比 / quantityChangePct'],
    ['reportedInterestShares', '港股申报权益股数 / reportedInterestShares'],
    ['reportedInterestPct', '港股申报权益比例 / reportedInterestPct'],
    ['longInterestChange', '港股多头权益变化 / longInterestChange'],
    ['title', '公告标题 / title'], ['targetName', '分拆标的 / spinOffTarget'],
    ['sourceURL', '原文 / originalSource'], ['checkedAt', '数据检查时间 / checkedAt'],
    ['displayLimit', '比较持仓上限 / displayLimit'], ['pendingNoticeCount', '待核验公告数 / pendingNoticeCount'],
    ['note', '说明 / note']
  ];
  const updates = data.updates.items.map(row => ({...row, rowType: 'update', source: row.kind,
    status: row.category || row.announcementStatus || row.position}));
  const coverage = data.coverage.map(row => ({...row, rowType: 'coverage', date: row.filingDate,
    checkedAt: row.checkedAt, displayLimit: row.displayScope?.limit, note: row.sourceStatus}));
  const summary = {
    window: data.window, watchlist: data.watchlist, exported: updates.length,
    totalMatching: data.updates.total, offset: args.offset, nextOffset: data.updates.nextOffset,
    truncated: data.updates.nextOffset != null,
    incompleteSourceCount: data.coverage.filter(row =>
      ['source_unavailable', 'partial', 'scope_partial', 'unverified', 'history_pending'].includes(row.status)).length,
    notes: data.notes
  };
  const metadata = [{rowType: 'report', status: summary.truncated ? 'truncated' : 'complete_page',
    note: JSON.stringify(summary)}];
  return {csv: csv([...metadata, ...updates, ...coverage], columns), summary};
}

export default {
  async fetch(request, env) {
    if (new URL(request.url).pathname !== '/mcp') return json({error: 'Not found'}, 404);
    if (request.method !== 'POST') return json({error: 'Method not allowed'}, 405, {Allow: 'POST'});
    const secret = env.PREMIUM_MCP_TOKEN;
    if (!/^[A-Za-z0-9_-]{32,128}$/.test(secret ?? '')) return json({error: 'Service unavailable'}, 503);
    if (!await authorized(request, secret)) return json({error: 'Authorization required'}, 401, {
      'WWW-Authenticate': 'Bearer realm="Investment Research Premium"'
    });
    if (!request.headers.get('Content-Type')?.startsWith('application/json')) return json({error: 'JSON required'}, 415);
    if (Number(request.headers.get('Content-Length')) > 8192) return json({error: 'Request too large'}, 413);
    const raw = await request.text();
    if (raw.length > 8192) return json({error: 'Request too large'}, 413);
    let message;
    try { message = JSON.parse(raw); } catch {
      return json({jsonrpc: '2.0', id: null, error: {code: -32700, message: 'Parse error'}}, 400);
    }
    if (!message || message.jsonrpc !== '2.0' || typeof message.method !== 'string') {
      return json({jsonrpc: '2.0', id: null, error: {code: -32600, message: 'Invalid request'}}, 400);
    }
    if (!Object.hasOwn(message, 'id')) return new Response(null, {status: 202});
    const reply = result => json({jsonrpc: '2.0', id: message.id, result});
    const fail = (code, text) => json({jsonrpc: '2.0', id: message.id, error: {code, message: text}});
    if (message.method === 'initialize') {
      return reply({protocolVersion: '2025-06-18', capabilities: {tools: {listChanged: false}},
        serverInfo: {name: 'investment-research-premium', version: '0.2.0'}});
    }
    if (message.method === 'ping') return reply({});
    if (message.method === 'tools/list') return reply({tools: [tool, watchlistTool]});
    if (message.method !== 'tools/call') return fail(-32601, 'Method not found');
    const name = message.params?.name;
    const args = toolArguments(name, message.params?.arguments);
    if (!args) return fail(-32602, 'Invalid tool or arguments; see tools/list');
    try {
      if (name === watchlistTool.name) {
        const report = await watchlistExport(args);
        return reply({content: [{type: 'text', text: report.csv}], structuredContent: report.summary});
      }
      const report = await compare(args.ticker);
      return reply({content: [{type: 'text', text: args.format === 'csv' ? comparisonCsv(report) : JSON.stringify(report)}]});
    } catch {
      return reply({isError: true, content: [{type: 'text', text: 'Published comparisons could not be loaded. Please retry.'}]});
    }
  }
};
