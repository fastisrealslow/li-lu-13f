const assert = require('node:assert/strict');
const {test} = require('node:test');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');

function app() {
  const nodes = new Map();
  const element = id => {
    if (!nodes.has(id)) {
      const classes = new Set();
      nodes.set(id, {innerHTML: '', textContent: '', style: {},
        setAttribute(k, v) { this[k] = v; },
        classList: {contains: x => classes.has(x), add(...xs) { xs.forEach(x => classes.add(x)); },
          remove(...xs) { xs.forEach(x => classes.delete(x)); },
          toggle(x, on) { on ? classes.add(x) : classes.delete(x); }},
        addEventListener() {}});
    }
    return nodes.get(id);
  };
  const context = vm.createContext({console, setTimeout, clearTimeout, AbortController, Date,
    localStorage: {getItem: () => null, setItem() {}},
    document: {readyState: 'loading', addEventListener() {},
      getElementById: element, querySelectorAll: () => []},
    fetch: async url => ({ok: true, json: async () =>
      JSON.parse(fs.readFileSync(path.join(root, url.split('?')[0]), 'utf8'))}),
  });
  vm.runInContext(fs.readFileSync(path.join(root, 'app.js'), 'utf8'), context);
  // Keep real switching, price loading and quarterly table rendering. Other
  // visualizations are outside this regression and need no canvas/DOM emulator.
  vm.runInContext(`renderInvestorBtns = renderSummary = renderHoldings =
    renderHistoryChart = renderTimelineTable = renderInsights =
    updateInvestorContent = () => {};`, context);
  return {context, element, run: code => vm.runInContext(code, context)};
}

test('quarterly rows and headers refresh for all investors without leaving the tab', async () => {
  const a = app();
  await a.run('loadInvestorConfig()');
  await a.run("switchInvestor('lilu')");
  a.run("switchTab('changes')");
  const investors = JSON.parse(fs.readFileSync(path.join(root, 'investors.json'))).investors;
  for (const inv of investors) {
    await a.run(`switchInvestor(${JSON.stringify(inv.id)})`);
    const current = JSON.parse(fs.readFileSync(path.join(root, inv.dataFile))).current;
    const rows = a.element('changesBody').innerHTML;
    if (['webb','ackman'].includes(inv.id)) {
      assert.match(rows, /历史披露快照|申报主体与范围变更/);
      assert.ok(!rows.includes('新进'));
      continue;
    }
    assert.ok((rows.match(/<tr>/g) || []).length >= current.holdings.length, inv.id);
    assert.equal(a.run('data.current.holdings.length'), current.holdings.length, 'Current holdings count must exclude exits');
    for (const h of current.holdings) assert.ok(rows.includes(`>${h.ticker.replace(/^\?/, '')}</span>`), `${inv.id}: ${h.ticker}`);
    assert.equal(a.element('chCS').textContent, `${current.quarter} 持股`);
    assert.equal(a.element('tab-changes').classList.contains('d-none'), false);
    assert.equal(a.element('tab-current').classList.contains('d-none'), true);
  }
});

function deferred() {
  let resolve;
  const promise = new Promise(r => { resolve = r; });
  return {promise, resolve};
}

for (const slowFile of ['buffett.json', 'prices_buffett.json', 'buffett_hk.json']) {
  test(`late ${slowFile} response cannot overwrite a later investor choice`, async () => {
    const a = app();
    await a.run('loadInvestorConfig()');
    await a.run("switchInvestor('lilu')");
    a.run("switchTab('changes')");
    const gate = deferred(), started = deferred();
    const fetchFile = a.context.fetch;
    a.context.fetch = async url => {
      if (url.split('?')[0] === slowFile) { started.resolve(); await gate.promise; }
      return fetchFile(url);
    };
    const oldRequest = a.run("switchInvestor('buffett')");
    await started.promise;
    await a.run("switchInvestor('pabrai')");
    const expectedRows = a.element('changesBody').innerHTML;
    const expectedPrices = a.run('JSON.stringify(prices)');
    gate.resolve();
    await oldRequest;
    assert.equal(a.run('investor'), 'pabrai');
    assert.equal(a.element('changesBody').innerHTML, expectedRows);
    assert.equal(a.run('JSON.stringify(prices)'), expectedPrices);
    assert.equal(a.run('data.current.holdings.length'),
      JSON.parse(fs.readFileSync(path.join(root, 'pabrai_data.json'))).current.holdings.length);
  });
}


test('refresh reloads only the selected investor and bypasses the browser cache', async () => {
  const a = app();
  await a.run('loadInvestorConfig()');
  const investors = JSON.parse(fs.readFileSync(path.join(root, 'investors.json'))).investors;
  for (const inv of investors) {
    await a.run(`switchInvestor(${JSON.stringify(inv.id)})`);
    const requests = [], fetchFile = a.context.fetch;
    a.context.fetch = async (url, options) => { requests.push({url, options}); return fetchFile(url, options); };
    await a.run('refreshLive()');
    a.context.fetch = fetchFile;
    assert.equal(a.run('investor'), inv.id);
    for (const file of [inv.dataFile, inv.pricesFile, 'run_status.json']) {
      const request = requests.find(r => r.url.split('?')[0] === file);
      assert.ok(request, `${inv.id}: ${file}`);
      assert.equal(request.options.cache, 'no-store');
      assert.ok(request.options.signal instanceof AbortSignal);
    }
    assert.ok(requests.every(r => !r.url.startsWith('http')), 'Refresh uses published snapshots');
    assert.equal(a.element('btnRefresh').disabled, false);
  }
});

for (const slowFile of ['data.json', 'prices.json']) {
  test(`refresh with delayed ${slowFile} cannot overwrite a new investor`, async () => {
    const a = app();
    await a.run('loadInvestorConfig()');
    await a.run("switchInvestor('lilu')");
    const gate = deferred(), started = deferred(), fetchFile = a.context.fetch;
    a.context.fetch = async (url, opts) => {
      if (url.split('?')[0] === slowFile) { started.resolve(); await gate.promise; }
      return fetchFile(url, opts);
    };
    const refresh = a.run('refreshLive()');
    await started.promise;
    await a.run("switchInvestor('pabrai')");
    const expected = a.run('JSON.stringify({data, prices})');
    gate.resolve();
    await refresh;
    assert.equal(a.run('investor'), 'pabrai');
    assert.equal(a.run('JSON.stringify({data, prices})'), expected);
  });
}

test('failed selection preserves the prior investor, holdings, and prices', async () => {
  const a = app();
  await a.run('loadInvestorConfig()');
  await a.run("switchInvestor('lilu')");
  const expected = a.run('JSON.stringify({data, prices})');
  a.context.fetch = async () => ({ok:false, status:503});
  assert.equal(await a.run("switchInvestor('buffett')"), false);
  assert.equal(a.run('investor'), 'lilu');
  assert.equal(a.run('JSON.stringify({data, prices})'), expected);
  assert.match(a.element('dataSource').textContent, /加载失败/);
});

test('aborted refresh releases button and retains the displayed holdings', async () => {
  const a = app();
  await a.run('loadInvestorConfig()');
  await a.run("switchInvestor('lilu')");
  const expected = a.run('JSON.stringify(data)');
  a.context.setTimeout = callback => setTimeout(callback, 1);
  a.context.fetch = async (url, {signal} = {}) => {
    if (!signal) return {ok:false};
    return new Promise((_, reject) => signal.addEventListener('abort', () => reject(new Error('aborted'))));
  };
  await a.run('refreshLive()');
  assert.equal(a.element('btnRefresh').disabled, false);
  assert.equal(a.run('JSON.stringify(data)'), expected);
});

test('quarterly comparison includes exits and matches renamed securities without changing current holdings', () => {
  const a = app();
  a.run(`data = {current: {quarter:'2026 Q2', prevQuarter:'2026 Q1', holdings:[
    {ticker:'NEW', cusip:'111', name:'Renamed', shares:80, value:800},
    {ticker:'BRK/B', name:'Berkshire', shares:10, value:500},
    {ticker:'BUY', name:'New holding', shares:4, value:40}
  ], previousHoldings:[
    {ticker:'OLD', cusip:'111', name:'Old name', shares:100, value:1000},
    {ticker:'BRK.B', name:'Berkshire', shares:10, value:400},
    {ticker:'SOLD', name:'Exited holding', shares:30, value:300}
  ]}}; renderChanges();`);
  const rows = JSON.parse(a.run('JSON.stringify(quarterlyHoldings())'));
  assert.deepEqual(rows.map(h => [h.ticker, h.prevShares, h.shares]), [['NEW',100,80], ['BRK/B',10,10], ['BUY',0,4], ['SOLD',30,0]]);
  const html = a.element('changesBody').innerHTML;
  assert.match(html, /清仓/);
  assert.match(html, /-30 \(-100.0%\)/);
  assert.match(html, /-\$300/);
  assert.equal(a.run('data.current.holdings.length'), 3);
  a.run("lang = 'en'; renderChanges()");
  assert.match(a.element('changesBody').innerHTML, /Exited/);
  assert.equal(a.element('chCS').textContent, '2026 Q2 Shares');
});

test('legacy history supplies missing liquidation rows', () => {
  const a = app();
  a.run(`data = {current:{quarter:'2026 Q2', prevQuarter:'2026 Q1', holdings:[
    {ticker:'KEEP', shares:10, value:100, prevShares:8, prevValue:80}
  ]}, history:{holdings:{'2026 Q1':[
    {ticker:'KEEP', shares:8, value:80}, {ticker:'SOLD', shares:5, value:50}
  ]}}}; renderChanges();`);
  const exits = JSON.parse(a.run('JSON.stringify(quarterlyHoldings().filter(h => h.exited).map(h => h.ticker))'));
  assert.deepEqual(exits, ['SOLD']);
  assert.match(a.element('changesBody').innerHTML, /清仓/);
});

test('different share classes do not match merely because issuer names are equal', () => {
  const a = app();
  assert.equal(a.run("sameSecurity({ticker:'GOOGL', name:'Alphabet', cls:'A'}, {ticker:'GOOG', name:'Alphabet', cls:'C'})"), false);
  assert.equal(a.run("sameSecurity({ticker:'ABC', cusip:'111'}, {ticker:'ABC', cusip:'222'})"), false);
  assert.equal(a.run("sameSecurity({ticker:'CB', name:'CHUBB', cls:'COM'}, {ticker:'?CHUBB', name:'CHUBB', cls:'COM'})"), true);
});

test('decreases have negative quantities and all used coal sectors are translated', () => {
  const a = app();
  assert.match(a.run('fmtShareChg(1744050, 1810831)'), /-66,781 \(-3.7%\)/);
  for (const sector of ['煤炭','油气钻探','冶金/煤炭']) assert.equal(a.run(`ts(${JSON.stringify(sector)})`), sector);
});

test('status distinguishes success, degradation, failure, incomplete and stale records', () => {
  const a = app();
  const now = Date.now();
  const complete = {schemaVersion:2, run_id:new Date(now).toISOString(), completedAt:new Date(now).toISOString(), steps:{metadata:{status:'ok'}}};
  const health = value => JSON.parse(a.run(`JSON.stringify(runHealth(${JSON.stringify(value)}, ${now}))`));
  assert.equal(health(complete).state, 'ok');
  assert.equal(health({...complete, steps:{metadata:{status:'warn'}}}).state, 'warn');
  assert.equal(health({...complete, steps:{metadata:{status:'fail'}}}).state, 'fail');
  assert.match(health({...complete, completedAt:undefined}).label, /尚未完成/);
  assert.match(health({...complete, completedAt:new Date(now - 37*3600000).toISOString()}).label, /过期/);
  assert.equal(health({...complete, schemaVersion:undefined}).state, 'warn');
  assert.equal(health(null).state, 'warn');
});

test('status messages distinguish historical coverage from a failed holdings load', () => {
  const a = app();
  const message = {status:'warn', msg:'lilu 历史缺 4 季：已补查SEC历史索引，仍无可用原始持仓报告；不作零持仓'};
  assert.match(a.run(`statusStepMessage('lilu_13f', ${JSON.stringify(message)})`), /缺 4 个季度.*不表示最新持仓加载失败/);
  a.run("lang='en'");
  assert.match(a.run(`statusStepMessage('lilu_13f', ${JSON.stringify(message)})`), /4 early historical quarters.*not a failure to load/);
  assert.equal(a.run("statusStepMessage('lilu_13f', {status:'fail',msg:'HTTP 503'})"), 'HTTP 503');
});

test('status drawer separates messages, escapes source text, and omits steps absent from that run', async () => {
  const a = app();
  const now = new Date().toISOString();
  a.context.fetch = async () => ({ok:true, json:async () => ({runs:[{
    schemaVersion:2, run_id:now, completedAt:now,
    steps:{lilu_13f:{status:'warn',ts:now,msg:'历史缺 4 季'},
      custom:{status:'fail',label:'<img src=x onerror=alert(1)>',msg:'<script>bad()</script>'}}
  }]})});
  await a.run('renderStatusDrawer()');
  const html = a.element('statusDrawerBody').innerHTML;
  assert.match(html, /class="status-step-message"/);
  assert.match(html, /不表示最新持仓加载失败/);
  assert.match(html, /&lt;script&gt;/);
  assert.doesNotMatch(html, /<script>|<img |data-step="vinall_13f"/);
  assert.equal((html.match(/data-step=/g) || []).length, 2);
});

test('independent AI summary matches exact investor snapshot, not just quarter',()=>{
  const a=app();
  a.run("data={current:{quarter:'2026Q2',holdings:[{ticker:'AAA',shares:10,value:100}]}}; _aiSupplement={entries:{'investor:lilu':{source:aiInvestorSource(data),renderVersion:4,mode:'model_selection',summary:'已有摘要'}}}");
  assert.equal(a.run("aiMatchingEntry('investor:lilu',aiInvestorSource(data)).summary"),'已有摘要');
  a.run("const s=_aiSupplement.entries['investor:lilu'].source; _aiSupplement.entries['investor:lilu'].source=Object.fromEntries(Object.entries(s).reverse())");
  assert.equal(a.run("aiMatchingEntry('investor:lilu',aiInvestorSource(data)).summary"),'已有摘要');
  a.run('data.current.holdings[0].shares=20');
  assert.equal(a.run("aiMatchingEntry('investor:lilu',aiInvestorSource(data))"),null);
  assert.equal(a.run("aiMatchingEntry('investor:buffett',aiInvestorSource(data))"),null);
  assert.equal(a.run("aiEscape('<script>')"),'&lt;script&gt;');
});


test('unverified and stale summaries cannot reappear through fallback',()=>{
  const a=app();
  a.run("data={meta:{aiSummary:'增持阿里巴巴，旧的错误摘要'},current:{quarter:'2026 Q2',holdings:[{ticker:'BABA',cnName:'阿里巴巴',shares:2000000,value:10}],previousHoldings:[{ticker:'BABA',shares:3465000,value:12}]}}; _aiSupplement={entries:{'investor:lilu':{source:aiInvestorSource(data),summary:'旧的错误摘要'}}}");
  assert.equal(a.run("aiMatchingEntry('investor:lilu',aiInvestorSource(data))"),null);
  const text=a.run('aiInvestorFallback(data)');
  assert.match(text,/阿里巴巴（BABA）：减持42.3%/);
  assert.doesNotMatch(text,/旧的错误摘要|阿里巴巴（BABA）：增持/);
  a.run('delete data.current.previousHoldings');
  assert.match(a.run('aiInvestorFallback(data)'),/上季股数未知/);
});

test('value fallback binds weights and directions to investors without implying equity ownership',()=>{
  const a=app();
  const text=a.run("aiValueFallback([{ticker:'BN',cnName:'布鲁克菲尔德',investors:[{id:'akre',name:'阿克瑞',weight:10.1,chg:'trimmed'},{id:'ackman',name:'阿克曼',weight:17.6,chg:'hold'}]}])");
  assert.match(text,/阿克瑞：布鲁克菲尔德（BN）减持，占其披露组合市值10.1%/);
  assert.match(text,/阿克曼：布鲁克菲尔德（BN）股数不变，占其披露组合市值17.6%/);
  assert.doesNotMatch(text,/持股比例|股权/);
});

test('complete facts and rendered summaries agree with Python for every published investor',async()=>{
  const a=app();await a.run('loadInvestorConfig()');
  const {execFileSync}=require('node:child_process');
  const expected=JSON.parse(execFileSync('python3',['-c',"import json;from ai_supplement import tasks; print(json.dumps(tasks('.'),ensure_ascii=False))"],{cwd:root,encoding:'utf8'}));
  const cache=JSON.parse(fs.readFileSync(path.join(root,'ai_supplement.json')));
  for(const task of expected.filter(t=>t.id.startsWith('investor:'))) {
    const id=task.id.split(':')[1];await a.run(`switchInvestor('${id}')`);
    const source=JSON.parse(a.run('JSON.stringify(aiInvestorSource(data))'));
    assert.deepEqual(source,task.source,id+' source');
    const facts=JSON.parse(a.run('JSON.stringify((({rows,...facts})=>facts)(portfolioFacts(data,INVESTOR_CFG_BY_ID[investor].name)))'));
    const {briefing,...comparisonFacts}=task.facts;
    assert.deepEqual(facts,comparisonFacts,id+' complete facts');
    a.context.baseBriefing=briefing;a.context.topicIds=cache.entries[task.id].selection.topicIds || [];
    assert.deepEqual(cache.entries[task.id].briefing,JSON.parse(a.run('JSON.stringify(orderedBriefing(baseBriefing,topicIds))')),id+' published narrative');
    if(facts.comparisonState==='comparable') {
      const entry=cache.entries[task.id];
      const summary=a.run(`investorSummary(data,${JSON.stringify(entry.selection.factIds)},INVESTOR_CFG_BY_ID[investor].name,false)`);
      assert.equal(summary,entry.summary,id+' exact summary');
    }
  }
  const value=expected.find(t=>t.id==='value');
  if(value) assert.equal(a.run(`aiValueFromSource(${JSON.stringify(value.source)},${JSON.stringify(cache.entries.value.selection.factIds)})`),cache.entries.value.summary);
});

test('tiny reductions are visible, duplicate rows combine, and option categories stay separate',()=>{
  const a=app();
  const rows=JSON.parse(a.run(`JSON.stringify(quarterlyHoldings({current:{holdings:[{ticker:'A',cusip:'1',shares:40,value:40},{ticker:'A',cusip:'1',shares:59,value:59},{ticker:'A',cusip:'1',shares:5,value:5,putCall:'Put'}],previousHoldings:[{ticker:'A',cusip:'1',shares:100,value:100}]}}))`));
  assert.equal(rows.length,2);assert.equal(rows[0].shares,99);assert.equal(rows[0].prevShares,100);assert.equal(rows[1].prevShares,0);
  assert.match(a.run('fmtShareChg(99999,100000)'),/-1.*0.05/);
  assert.doesNotMatch(a.run('fmtShareChg(99999,100000)'),/0.0%/);
  assert.match(a.run('fmtShareChg(1,null)'),/待比较/);
});

test('HK comparisons keep different owners and share classes separate',()=>{
  const a=app();
  const base={event_date:'2026-06-01',shares:100,pct:5,filing_ref:'FIRST',source_url:'https://di.hkex.com.hk/di/NSForm1.aspx',verification:'hkex_form',share_class:'H Shares',entity:'Person'};
  a.context.hkSample=[{ticker:'01211.HK',verified_disclosures:[base,{...base,event_date:'2026-07-01',shares:90,filing_ref:'SECOND'},{...base,event_date:'2026-08-01',shares:1000,entity:'Other owner',filing_ref:'OTHER'},{...base,event_date:'2026-09-01',share_class:'A Shares',shares:10,filing_ref:'A'}]}];
  const groups=JSON.parse(a.run('JSON.stringify(hkDisclosureGroups(hkSample))'));
  assert.equal(groups.length,3);
  const h=groups.find(g=>g.entity==='Person' && g.shareClass==='H Shares');
  assert.equal(h.latest.shares,90);assert.equal(h.previous.shares,100);
  assert.equal(groups.find(g=>g.entity==='Other owner').previous,undefined);
  assert.equal(groups.find(g=>g.shareClass==='A Shares').previous,undefined);
});
