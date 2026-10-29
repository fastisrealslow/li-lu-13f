const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),vm=require('node:vm'),path=require('node:path');
function app(){const context=vm.createContext({console,setTimeout,clearTimeout,AbortController,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},querySelectorAll:()=>[]}});vm.runInContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),context);return {context,run:code=>vm.runInContext(code,context)};}
const holding={ticker:'GOOGL',cusip:'02079K305',putCall:'',shareType:'SH',shares:10};
const snapshot={meta:{instrumentHistoryTickers:['GOOGL'],instrumentHistoryFrom:'2020 Q1'},current:{quarter:'2026 Q2'},history:{holdings:{'2020 Q1':[holding],'2026 Q1':[holding]}}};
const prices={costBasis:{GOOGL:{recent:{buy:100,quarter:'2026 Q1'},allTime:{avg:50,first:'2020 Q1',last:'2026 Q2'}}}};
function fixture(){const a=app();a.context.holding=structuredClone(holding);a.context.snapshot=structuredClone(snapshot);a.context.quote=structuredClone(prices);return a;}
test('verified share classes display valid estimates instead of blanket history suppression',()=>{const a=fixture();assert.equal(a.run('holdingCostState(holding,snapshot,quote).basis.recent.buy'),100);a.run('snapshot.history.holdings["2026 Q1"][0].cusip="different"');assert.equal(a.run('holdingCostState(holding,snapshot,quote).reason'),'classes');});
test('old averages remain hidden until verified splits are recalculated',()=>{const a=fixture();a.run('snapshot.meta.shareActions=[{ticker:"GOOGL",quarter:"2022 Q3"}]');assert.equal(a.run('holdingCostState(holding,snapshot,quote).basis.allTime'),null);a.run('quote.costBasis.GOOGL.splitAdjustedThrough="2026 Q2"');assert.equal(a.run('holdingCostState(holding,snapshot,quote).basis.allTime.avg'),50);});
test('reentry never uses a recent estimate from before the current holding run',()=>{const a=fixture();a.run('quote.costBasis.GOOGL.allTime.first="2026 Q2"');assert.equal(a.run('holdingCostState(holding,snapshot,quote).reason'),'stale_cost');});
test('units, options, principal and archive retain explicit reasons',()=>{for(const [reason,code] of [['units','snapshot.current.valueQuality={}'],['option','holding.putCall="CALL"'],['principal','holding.shareType="PRN"'],['archive','snapshot.meta.snapshotType="archived"']]){const a=fixture();a.run(code);assert.equal(a.run('holdingCostState(holding,snapshot,quote).reason'),reason);}});
test('cost differences render negative, zero and small positive values',()=>{const a=fixture();assert.match(a.run('costGapHTML(costGap(150,100))'),/现价高于加仓参考价.*50.0%/);assert.match(a.run('costGapHTML(costGap(100,100))'),/现价等于加仓参考价.*0.0%/);assert.match(a.run('costGapHTML(costGap(95,100))'),/现价低于加仓参考价.*5.0%/);assert.equal(a.run('costGap(0,100)'),null);assert.equal(a.run('costGap(100,0)'),null);assert.ok(!a.run('costGapHTML(null)').includes('NaN'));});

test('price labels distinguish holding span from actual buying-quarter count',()=>{const a=fixture();assert.equal(a.run("costSpanText({first:'2020 Q1',last:'2026 Q2',buy_quarters:10})"),'覆盖26个季度 · 2020 Q1–2026 Q2 · 其中10季加仓');assert.ok(!a.run("costSpanText({avg:100})").includes('NaN'));});
test('unverified value quarters cannot supply recent or spanning average estimates',()=>{const a=fixture();a.run('snapshot.history.excludedValueQuarters=["2024 Q3"]');const state=a.run('holdingCostState(holding,snapshot,quote)');assert.equal(state.basis.allTime,null);assert.equal(state.averageReason,'units');a.run('snapshot.history.excludedValueQuarters=["2026 Q1"]');assert.equal(a.run('holdingCostState(holding,snapshot,quote).reason'),'units');});

test("expanded scope uses the current security price proxy without inventing its acquisition or old-manager average",()=>{const a=fixture();a.run('snapshot.meta.reportingTransition={fromQuarter:"2026 Q2",comparisonScopeChanged:true};holding.value=2000;snapshot.current.holdings=[holding]');const state=a.run("holdingCostState(holding,snapshot,quote)");assert.equal(state.basis.recent.buy,200);assert.equal(state.basis.recent.kind,'quarter_reference');assert.equal(state.basis.allTime,null);});
test("a newly filed ordinary holding has a dated price reference while its historical estimate is being calculated",()=>{const a=fixture();a.run('holding.value=2000;snapshot.current.holdings=[holding];quote.costBasis={}');const state=a.run("holdingCostState(holding,snapshot,quote)");assert.equal(state.basis.recent.buy,200);assert.equal(state.basis.recent.quarter,'2026 Q2');assert.equal(state.basis.allTime,null);assert.match(a.run('costGapHTML(10,null,false,"quarter_reference")'),/本季季末价/);a.run('snapshot.current.valueQuality={status:"units_unverified"}');assert.equal(a.run('holdingCostState(holding,snapshot,quote).reason'),'units');});
test('a security can keep predecessor cost history only when the SEC manager bridge covers every source row',()=>{const a=fixture();a.run('holding.value=100;snapshot.meta.reportingTransition={fromQuarter:"2026 Q2",comparisonScopeChanged:true,fromCIK:"1"};snapshot.current.holdings=[holding];snapshot.current.reportingScope={quarter:"2026 Q2",managers:{"7":{cik:"0001"},"8":{cik:"2"}}};snapshot.history.filing_sources={"2026 Q1":{cik:"1"}};holding.managerAllocations=[{managerIds:["7","8"],shares:10,value:100}];snapshot.history.holdings["2026 Q2"]=[holding]');assert.equal(a.run('holdingCostState(holding,snapshot,quote).basis.recent.buy'),100);a.run('holding.managerAllocations=[{managerIds:["7"],shares:6,value:60},{managerIds:["8"],shares:4,value:40}]');assert.equal(a.run('holdingCostState(holding,snapshot,quote).basis.recent.kind'),'quarter_reference');});

test('quote dates follow the listing market and never fabricate missing or future dates',()=>{
  const a=app();
  a.context.quote={t:Date.parse('2026-01-03T01:00:00Z')/1000};
  assert.equal(a.run("quoteDateText(quote,'GOOGL')"),'2026-01-02');
  assert.equal(a.run("quoteDateText(quote,'0700.HK')"),'2026-01-03');
  for(const q of [{},{t:null},{t:0},{t:NaN},{t:(Date.now()+86400000)/1000}]){
    a.context.quote=q;assert.equal(a.run("quoteDateText(quote,'GOOGL')"),'');
  }
});

test('legend follows rendered gap categories without invented position percentages or mismatched reference types',()=>{
  const a=app();a.run('data={current:{},meta:{snapshotType:"archive"}}');
  const html=a.run('holdingsLegendHTML([],[-12,0,8,12,20])');
  for(const text of ['高于参考价','等于参考价','不足 10%','10% 至不足 20%','至少 20%'])assert.ok(html.includes(text),text);
  assert.doesNotMatch(html,/25.0%|15.0%|5.0%|加仓参考价/);
  assert.doesNotMatch(a.run('holdingsLegendHTML([],[-12])'),/至少 20%|不足 10%/);
  assert.equal(a.run('costGap(80,100)'),20);
  assert.match(a.run("t('priceNote')"),/（参考价－现价）÷参考价/);
  assert.match(a.run("lang='en';t('priceNote')"),/\(reference − price\) \/ reference/);
});

test('option references are underlying nominal prices, with no invented premium or contract divisor',()=>{
 const a=app();a.run('data={current:{quarter:"2026 Q2"}}');
 a.context.h={putCall:'Put',shareType:'SH',value:12000,shares:100};
 assert.equal(a.run('optionNotionalReference(h).price'),120);
 assert.equal(a.run('optionNotionalReference(h).quarter'),'2026 Q2');
 a.run('h.shareType="CONTRACTS"');assert.equal(a.run('optionNotionalReference(h)'),null);
 a.run('h.shareType="SH";data.current.valueQuality={}');assert.equal(a.run('optionNotionalReference(h)'),null);
});
