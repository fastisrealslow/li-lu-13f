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
        classList: {contains: x => classes.has(x),
          toggle(x, on) { on ? classes.add(x) : classes.delete(x); }},
        addEventListener() {}});
    }
    return nodes.get(id);
  };
  const context = vm.createContext({console, setTimeout, Date,
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
    assert.equal((rows.match(/<tr>/g) || []).length, current.holdings.length, inv.id);
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

for (const slowFile of ['buffett.json', 'prices_buffett.json']) {
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
