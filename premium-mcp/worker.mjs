const dataRoot = 'https://fastisrealslow.github.io/li-lu-13f/';
const encoder = new TextEncoder();
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
  annotations: {readOnlyHint: true, destructiveHint: false, idempotentHint: true, openWorldHint: false}
};

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

function csv(report) {
  const columns = [
    'investorId', 'investorName', 'investorNameEn', 'quarter', 'previousQuarter', 'comparisonState',
    'displayLimit', 'result', 'ticker', 'cusip', 'securityName', 'securityClass', 'putCall', 'quantityType',
    'category', 'currentQuantity', 'previousQuantity', 'quantityDelta', 'quantityChangePct',
    'splitFactor', 'scopeEntry', 'filingUrl', 'previousFilingUrl'
  ];
  const cell = value => {
    if (value == null) return '';
    if (typeof value === 'number' || typeof value === 'boolean') return String(value);
    const text = /^[\s\uFEFF]*[=+@-]|^[\t\r\n]/.test(value) ? "'" + value : String(value);
    return '"' + text.replaceAll('"', '""') + '"';
  };
  return '\uFEFF' + [columns.join(','), ...report.rows.map(row =>
    columns.map(key => cell(key === 'splitFactor' ? row.splitAdjustment?.factor : row[key])).join(',')
  )].join('\r\n') + '\r\n';
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
        serverInfo: {name: 'investment-research-premium', version: '0.1.0'}});
    }
    if (message.method === 'ping') return reply({});
    if (message.method === 'tools/list') return reply({tools: [tool]});
    if (message.method !== 'tools/call') return fail(-32601, 'Method not found');
    const args = message.params?.arguments;
    if (message.params?.name !== tool.name || !args || typeof args !== 'object' || Array.isArray(args) ||
        Object.keys(args).some(key => !['ticker', 'format'].includes(key)) ||
        typeof args.ticker !== 'string' || !/^[A-Z0-9][A-Z0-9./-]{0,14}$/i.test(args.ticker.trim()) ||
        (Object.hasOwn(args, 'format') && !['json', 'csv'].includes(args.format))) {
      return fail(-32602, 'Provide a valid US ticker and an optional format of json or csv');
    }
    try {
      const report = await compare(canonicalTicker(args.ticker));
      return reply({content: [{type: 'text', text: args.format === 'csv' ? csv(report) : JSON.stringify(report)}]});
    } catch {
      return reply({isError: true, content: [{type: 'text', text: 'Published comparisons could not be loaded. Please retry.'}]});
    }
  }
};
