const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
function app() {
  const nodes = new Map();
  const calls = [];
  const ctx = new Proxy({}, {get(_, key) {
    if (key === 'createLinearGradient') return () => ({addColorStop(){}});
    return (...args) => { args.filter(x => typeof x === 'number').forEach(x => assert.ok(Number.isFinite(x), key)); calls.push([key, ...args]); };
  }, set(){return true;}});
  const el = id => {
    if (!nodes.has(id)) nodes.set(id, {innerHTML:'',textContent:'',style:{},width:800,height:360,
      parentElement:{clientWidth:832,style:{},appendChild(){}},getContext:()=>ctx,remove(){},
      getBoundingClientRect:()=>({left:0,top:0,width:800,height:360})});
    return nodes.get(id);
  };
  const context = vm.createContext({console,Date,localStorage:{getItem:()=>null},window:{innerWidth:1000},
    document:{readyState:'loading',addEventListener(){},getElementById:el,createElement:()=>el('tooltip')}});
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../app.js'),'utf8'),context);
  return {context,el,calls,run:code=>vm.runInContext(code,context)};
}
test('history aligns sorted quarters, uses exact holdings totals and rejects invalid points',()=>{
  const a=app();
  const result=JSON.parse(a.run(`JSON.stringify(historySeries({quarters:['2020 Q2','2020 Q1','2020 Q3','2020 Q4','2021 Q1','bad','2020 Q1'],values:[6000,0,null,-4,NaN,7,0],holdings:{'2020 Q2':[{value:5657250000}]}}))`));
  assert.deepEqual(result,{quarters:['2020 Q1','2020 Q2'],values:[0,5657.25]});
});
test('gaps use calendar spacing, break the line, and suppress spurious QoQ percentages',()=>{
  const a=app();a.run("var qs=['2020 Q1','2020 Q2','2021 Q1'], vs=[100,200,50]");
  assert.equal(a.run('historyX(qs,1)'),.25);
  assert.equal(a.run('historyChange(qs,vs,1)'),1);
  assert.equal(a.run('historyChange(qs,vs,2)'),null);
  assert.equal(a.run('historySegments(qs).length'),2);
  assert.equal(a.run("historyChange(['2020 Q1','2020 Q2'],[0,100],1)"),null);
  assert.equal(a.run("historyChange(['2020 Q1','2020 Q2'],[100,100],1)"),0);
});
test('small portfolios have usable axes and currency follows the investor',()=>{
  const a=app();
  assert.ok(a.run('historyRange([2,3]).maxV')<4);
  assert.ok(a.run('historyRange([0]).maxV')>0);
  assert.equal(a.run("investor='webb';historyMoney(1234.56)"),'HK$1.23B');
  assert.equal(a.run("investor='lilu';historyMoney(12.345,3)"),'US$12.345M');
  const text=a.run("generateHistoryInsight(['2020 Q1','2020 Q3'],[100,50])");
  assert.match(text,/-50.0%/);assert.match(text,/缺失季度/);assert.ok(!text.includes('重大持仓调整'));
});
test('desktop and mobile render gaps and single zero values without NaN and clear stale state',()=>{
  const a=app();
  for(const width of [1000,375]) {
    a.context.window.innerWidth=width;
    for(const history of [{quarters:['2020 Q1'],values:[0]}, {quarters:['2020 Q1','2020 Q2','2021 Q1'],values:[1,2,4]}]) {
      a.context.sample=history;a.run('data={history:sample};renderHistoryChart()');
      assert.ok(!/NaN|Infinity/.test(a.el('historyMobileWrap').innerHTML));
    }
  }
  assert.equal((a.el('historyMobileWrap').innerHTML.match(/<polyline /g)||[]).length,2);
  a.run('data={};renderHistoryChart()');
  assert.equal(a.el('historyMobileWrap').innerHTML,'');
  assert.equal(a.el('historyChart').onmousemove,null);
  assert.match(a.el('historyInsight').innerHTML,/暂无历史数据/);
});
test('timeline remaining share ratio is not labeled sold percentage',async()=>{
  const a=app();
  await a.run(`data={history:{holdings:{'2020 Q1':[{ticker:'A',name:'A',shares:100,value:100}], '2020 Q2':[{ticker:'A',name:'A',shares:30,value:30}]}}}; renderHKHoldings=()=>{};renderTimelineTable()`);
  assert.match(a.el('timelineCanvas').innerHTML,/持股为峰值的 30%/);
  assert.ok(!a.el('timelineCanvas').innerHTML.includes('30% 已减持'));
});

test('unverified historical snapshots are not charted as confirmed values',async()=>{
 const a=app();
 a.run("data={history:{quarters:['2026 Q1'],values:[14791],verification:{status:'unverified'}}};renderHistoryChart()");
 assert.equal(a.run('historySeries(data.history).values.length'),0);
 assert.match(a.el('historyInsight').innerHTML,/缺少可比、带日期/);
 await a.run('renderHKHoldings=()=>{};renderTimelineTable()');
 assert.match(a.el('timelineCanvas').innerHTML,/暂不展示/);
});

test('HK search-derived active status and old peak are not current evidence',()=>{
  const a=app();
  const result=JSON.parse(a.run(`JSON.stringify(hkEvidenceView({current_status:'active',last_disclosure:'2026',peak_known:true,peak_shares:57404700}))`));
  assert.equal(result.status,'当前持仓未核实');
  assert.equal(result.latest,undefined);
});
test('main table accepts only recent original manager holdings and never adds overlapping interests',()=>{
  const a=app();
  // A fetch timeout in live JSON must not turn a positive evidence test into a flaky deployment failure.
  const fixture=JSON.parse(fs.readFileSync(path.join(__dirname,'fixtures/hk_current_manager.json'),'utf8'));
  const now=Date.parse(fixture.audit.checkedAt)+3600000;
  const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../investors.json'),'utf8')).investors;
  a.context.now=now;
  for(const inv of cfg){
    a.context.config=inv;
    a.context.payload=structuredClone(fixture);
    const rows=JSON.parse(a.run("JSON.stringify(latestReportedHKHoldings(payload,config,'2026 Q2',now))"));
    if(inv.id==='duan'){
      assert.equal(rows.length,1);
      assert.equal(rows[0].ticker,'09992.HK');
      assert.equal(rows[0].shares,106716000);
      assert.equal(rows[0].asOf,'2026-09-01');
      assert.match(rows[0].sourceURL,/NSForm2.aspx/);
    }else assert.equal(rows.length,0,inv.id);
  }
  a.context.config=cfg.find(x=>x.id==='duan');
  const payload=structuredClone(fixture);
  for(const mutate of [p=>p.audit.status='partial',p=>p.audit.checkedAt='2026-09-01T00:00:00Z',p=>p.holdings.forEach(h=>h.verified_disclosures?.forEach(r=>r.event_date='2024-01-01')),p=>p.holdings.forEach(h=>h.verified_disclosures?.forEach(r=>r.pct=4.99)),p=>p.holdings.forEach(h=>h.verified_disclosures?.forEach(r=>r.verification='search_result'))]){
    a.context.payload=structuredClone(payload);mutate(a.context.payload);
    assert.equal(a.run("latestReportedHKHoldings(payload,config,'2026 Q2',now).length"),0);
  }
});
test('HK dated disclosures display historic quantities only with primary evidence',()=>{
  const a=app();
  const result=JSON.parse(a.run(`JSON.stringify(hkEvidenceView({verified_disclosures:[{event_date:'2021-01-15',shares:1274411000,pct:6.42,filing_ref:'CS20210120E00331',source_url:'https://di.hkex.com.hk/di/NSAllFormList.aspx'},{event_date:'2026',shares:99,pct:9,source_url:'https://example.com'}]}))`));
  assert.equal(result.latest.shares,1274411000);
  assert.equal(result.latest.event_date,'2021-01-15');
  assert.equal(result.status,'当前持仓未核实');
});

test('quarterly insights follow tables and archived HK interests have no duplicate display',()=>{
  const html=fs.readFileSync(path.join(__dirname,'../index.html'),'utf8');
  assert.ok(html.indexOf('id="holdingsInsight"')>html.indexOf('id="holdingsBody"'));
  assert.ok(html.indexOf('id="changesInsight"')>html.indexOf('id="changesBody"'));
  assert.ok(html.indexOf('id="historyInsight"')>html.indexOf('id="timelineCanvas"'));
  assert.ok(!html.includes('id="currentHKHoldings"'));
  assert.ok(!html.includes('id="hkHoldingsTable"'));
});
test('distinctive quotations retain source links in both languages',()=>{
  const a=app();
  a.context.document.querySelector=a.el;
  a.context.document.querySelectorAll=()=>[];
  const cfg=JSON.parse(fs.readFileSync(path.join(__dirname,'../investors.json'),'utf8')).investors;
  a.context.cfg=cfg;
  a.run('INVESTOR_CFG_BY_ID=Object.fromEntries(cfg.map(x=>[x.id,x]));data={}');
  for(const [id,zh,en] of [['lilu','宏观是我们必须接受的','The macro'],['pabrai','正面我赢','Heads I win'],['webb','阳光是最好的消毒剂','Sunlight is the best disinfectant']]){
    a.run(`investor='${id}';lang='zh';updateInvestorContent()`);
    assert.ok(a.el('.quote-block blockquote').textContent.includes(zh));
    assert.match(a.el('.quote-block .attr').innerHTML,/href="https:\/\//);
    a.run("lang='en';updateInvestorContent()");
    assert.ok(a.el('.quote-block blockquote').textContent.includes(en));
  }
});

test('superseded HK filings cannot replace a corrected record',()=>{
  const a=app();
  const base={event_date:'2025-05-08',shares:100,pct:5,source_url:'https://di.hkex.com.hk/di/NSForm1.aspx'};
  a.context.sample={verified_disclosures:[{...base,filing_ref:'IS20250513E00008',shares:120},{...base,event_date:'2025-06-01',filing_ref:'IS20250510E00001',superseded_by:'IS20250513E00008'}]};
  assert.equal(a.run('hkEvidenceView(sample).latest.shares'),120);
  assert.equal(a.run('hkEvidenceView(sample).records.length'),1);
});

test('history distinguishes completed source searches from fetch failures',()=>{
  const a=app();
  a.run("data={history:{coverage:{expandedLookup:{status:'checked',checkedAt:'2026-09-21T03:00:00Z'}}}}");
  let text=a.run("generateHistoryInsight(['2018 Q3','2019 Q4'],[100,200])");
  assert.match(text,/已补查 SEC 历史总索引（2026-09-21）/);
  assert.match(text,/仍未取得可核实/);
  a.run("data.history.coverage.expandedLookup.status='partial'");
  text=a.run("generateHistoryInsight(['2018 Q3','2019 Q4'],[100,200])");
  assert.match(text,/尚未完成，将自动重试/);
  assert.ok(!text.includes('已补查 SEC'));
});

test('RV Capital biography and investment principles render in both languages',()=>{
  const a=app();
  a.context.document.querySelector=selector=>a.el(selector);
  a.context.document.querySelectorAll=()=>[];
  a.context.sample=JSON.parse(fs.readFileSync(path.join(__dirname,'../vinall.json'),'utf8'));
  a.context.profileConfig=JSON.parse(fs.readFileSync(path.join(__dirname,'../investors.json'),'utf8')).investors.find(x=>x.id==='vinall');
  a.run("investor='vinall';data=sample;INVESTOR_CFG_BY_ID.vinall=profileConfig");
  for (const language of ['zh','en']) {
    a.run(`lang='${language}';updateInvestorContent()`);
    assert.match(a.el('.ref-text').innerHTML,/RV Capital/);
    assert.match(a.el('.ref-text').innerHTML,/Business Owner Fund/);
    assert.match(a.el('.ref-text').innerHTML,/CIK=1766596/);
    assert.equal((a.el('.phil-grid').innerHTML.match(/class="phil-card"/g)||[]).length,6);
    assert.ok(!a.el('.ref-grid .timeline').innerHTML.includes('Himalaya'));
    assert.match(a.el('.articles-grid').innerHTML,/rvcapital.ch\/articles-en/);
    assert.equal(a.el('[data-i18n="footerTitle"]').textContent,language==='en'?'Rob Vinall 13F Tracker':'罗布·维纳尔 13F 持仓追踪');
  }
});

test('quarterly UI and summary retain the split-adjusted comparison',()=>{
  const a=app();
  a.run(`data={current:{quarter:'2026 Q2',prevQuarter:'2026 Q1',holdings:[{ticker:'CVNA',shares:1763296,value:116060143,prevShares:1886490,shareAdjustment:{reportedShares:377298,factor:5}}],previousHoldings:[{ticker:'CVNA',shares:377298,value:118818309}]}}`);
  assert.equal(a.run('quarterlyHoldings()[0].prevShares'),1886490);
  a.run('renderChanges()');
  assert.match(a.el('changesBody').innerHTML,/-6.5%/);
  assert.match(a.el('changesBody').innerHTML,/377,298/);
  assert.match(a.run('aiInvestorFallback(data)'),/减持6.5%（拆股调整后）/);
});

test('verified profiles have matching source links for every investor in both languages',()=>{
 const a=app();
 a.context.document.querySelector=selector=>a.el(selector);
 a.context.document.querySelectorAll=()=>[];
 const configs=JSON.parse(fs.readFileSync(path.join(__dirname,'../investors.json'),'utf8')).investors;
 for (const cfg of configs) {
   a.context.cfg=cfg;
   a.context.sample=JSON.parse(fs.readFileSync(path.join(__dirname,'../'+cfg.dataFile),'utf8'));
   for (const language of ['zh','en']) {
     a.run(`lang='${language}';investor=cfg.id;INVESTOR_CFG_BY_ID[cfg.id]=cfg;data=sample;updateInvestorContent()`);
     assert.equal((a.el('.phil-grid').innerHTML.match(/class="phil-card"/g)||[]).length,6,cfg.id);
     if(cfg.cik) assert.match(a.el('.ref-text').innerHTML,new RegExp('CIK='+cfg.cik));
     for(const item of cfg.profile.resources) assert.ok(a.el('.articles-grid').innerHTML.includes(item.url.replace(/&/g,'&amp;')),cfg.id+': '+item.url);
     assert.match(a.el('.ref-text').innerHTML,/2026-10-09/);
   }
 }
});
test('missing or stale quotes cannot produce a margin-of-safety badge',()=>{
 const a=app();
 a.context.document.querySelector=selector=>a.el(selector);
 a.context.document.getElementById=id=>id==='priceFoot'?null:a.el(id);
 for(const q of [{error:true},{c:5,stale:true}]) {
  a.context.quote=q;
  a.run("data={current:{quarter:'2026 Q2',totalValue:100,holdings:[{ticker:'ABC',name:'ABC',shares:10,value:100}]}}; prices={quotes:{ABC:quote},costBasis:{ABC:{recent:{buy:20,quarter:'2026 Q1',source:'yahoo'}}}};renderHoldings()");
  assert.ok(!a.el('holdingsBody').innerHTML.includes('mosPulse'));
  assert.match(a.el('holdingsBody').innerHTML,/暂无报价/);
 }
});
test('unverified value units are excluded from historical valuation series',()=>{
 const a=app();
 assert.equal(a.run("historySeries({quarters:['2025 Q4','2026 Q1'],values:[5000,5],excludedValueQuarters:['2026 Q1']}).quarters.length"),1);
});
