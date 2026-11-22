const {test} = require('node:test');
const assert = require('node:assert/strict');

const token = 'a'.repeat(64);
const env = {PREMIUM_MCP_TOKEN: token};
const worker = import('../premium-mcp/worker.mjs').then(module => module.default);

async function send(method, params, {key = token, bindings = env} = {}) {
  const headers = {'Content-Type': 'application/json'};
  if (key) headers.Authorization = 'Bearer ' + key;
  return (await worker).fetch(new Request('https://preview.example/mcp', {
    method: 'POST', headers, body: JSON.stringify({jsonrpc: '2.0', id: 1, method, params})
  }), bindings);
}

test('all tool access requires a configured secret and a matching bearer credential', async () => {
  assert.equal((await send('tools/list', {}, {bindings: {}})).status, 503);
  assert.equal((await send('tools/list', {}, {key: null})).status, 401);
  assert.equal((await send('tools/call', {}, {key: 'b'.repeat(64)})).status, 401);
  const list = await (await send('tools/list')).json();
  assert.equal(list.result.tools[0].name, 'compare_investor_changes');
  assert.equal(list.result.tools[1].name, 'export_watchlist_report');
  assert.equal(list.result.tools[0].annotations.readOnlyHint, true);
});

test('watchlist CSV includes evidence and coverage, and never forwards the origin credential', async () => {
  const original = global.fetch;
  const args = {investors: ['lilu'], tickers: ['PDD', '01211.HK'], days: 90};
  const input = {name: 'export_watchlist_report', arguments: args};
  let coverage = [{source: 'sec_13f', status: 'comparable', investorName: '李录'},
    {source: 'hkex_interests', status: 'source_unavailable', investorName: '李录'}];
  try {
    global.fetch = async (url, options) => {
      assert.equal(url, 'https://li-lu-13f.pages.dev/mcp');
      assert.equal(new Headers(options.headers).has('Authorization'), false);
      const request = JSON.parse(options.body);
      assert.equal(request.params.name, 'get_watchlist_updates');
      assert.equal(request.params.arguments.limit, 50);
      return Response.json({result: {content: [{type: 'text', text: JSON.stringify({data: {
        watchlist: {investors: args.investors, tickers: args.tickers}, window: {since: '2026-09-01', through: '2026-11-22'},
        updates: {total: 51, nextOffset: 50, items: [
          {kind: 'sec_13f', ticker: 'PDD', date: '2026-11-16', sourceURL: 'https://www.sec.gov/Archives/edgar/data/1/2/index.html'}
        ]}, coverage
      }})}]}});
    };
    const r = (await (await send('tools/call', input)).json()).result;
    assert.equal(r.structuredContent.incompleteSourceCount, 1);
    assert.equal(r.structuredContent.nextOffset, 50);
    assert.match(r.content[0].text, /公告日 \/ publicationDate/);
    assert.match(r.content[0].text, /sec\.gov\/Archives\/edgar\/data/);
    assert.match(r.content[0].text, /"coverage","hkex_interests"/);
    assert.match(r.content[0].text, /source_unavailable/);
    coverage = coverage.slice(1);
    const failure = (await (await send('tools/call', input)).json()).result;
    assert.equal(failure.isError, true);
  } finally {
    global.fetch = original;
  }
});

test('comparison and CSV preserve report scopes, partial failures and instrument identity', async () => {
  const original = global.fetch;
  const people = ['investor_a', 'investor_b', 'investor_c', 'investor_d'].map(id => ({id, name: id, source13F: true}));
  const file = id => 'browser/' + id + '-quarterly-changes-' + 'a'.repeat(24) + '.json';
  const source = 'https://www.sec.gov/Archives/edgar/data/123/000123.html';
  const a = {version: 1, investor: 'investor_a', quarter: '2026 Q3', previousQuarter: '2026 Q2',
    comparisonState: 'comparable', filingSource: source, rows: [
      {ticker: 'BRK/B', cusip: '084670702', cnName: '=DUMMY()', shareType: 'SH', category: 'trimmed', shares: 15, prevShares: 20, sharesDelta: -5},
      {ticker: 'BRK/B', cusip: '084670702', putCall: 'Put', category: 'new', shares: 20, prevShares: 0, sharesDelta: 20}
    ]};
  const b = {version: 1, investor: 'investor_b', quarter: '2026 Q2', displayScope: {limit: 50}, comparisonState: 'comparable', rows: []};
  const c = {version: 1, investor: 'investor_c', quarter: '2026 Q1', comparisonState: 'gap', rows: []};
  global.fetch = async url => {
    const path = new URL(url).pathname.replace('/li-lu-13f/', '');
    const fixtures = {
      'investors.json': {investors: people},
      'browser/manifest.json': {investors: Object.fromEntries(people.map(p => [p.id, {quarterlyChanges: {file: file(p.id)}}]))},
      [file('investor_a')]: a, [file('investor_b')]: b, [file('investor_c')]: c
    };
    return Object.hasOwn(fixtures, path) ? Response.json(fixtures[path]) : new Response(null, {status: 503});
  };
  try {
    const call = async args => {
      const reply = await (await send('tools/call', {name: 'compare_investor_changes', arguments: args})).json();
      assert(!reply.error && !reply.result.isError, JSON.stringify(reply));
      return reply.result.content[0].text;
    };
    const report = JSON.parse(await call({ticker: 'brk-b'}));
    assert.equal(report.matchedInvestors, 1);
    assert.equal(report.unavailableInvestors, 1);
    assert.deepEqual(report.rows.map(r => r.result),
      ['matched', 'matched', 'no_match_in_reported_scope', 'comparison_unavailable', 'source_unavailable']);
    assert.equal(report.rows[0].filingUrl, source);
    assert.equal(report.rows[1].putCall, 'Put');
    assert.equal(report.rows[2].displayLimit, 50);
    assert.equal(report.rows[2].quarter, '2026 Q2');
    const csv = await call({ticker: 'BRK.B', format: 'csv'});
    assert(csv.startsWith('\uFEFFinvestorId,'));
    assert(csv.includes('"\'=DUMMY()"'));
    assert(csv.includes(',15,20,-5,'));
    assert(csv.includes('comparison_unavailable'));
  } finally {
    global.fetch = original;
  }
});
