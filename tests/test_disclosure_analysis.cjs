const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
function app(){
  const c=vm.createContext({console,Date,window:{innerWidth:1440},localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},getElementById:()=>({innerHTML:'',style:{}})}});
  for(const file of ['app.js','disclosure_analysis.js'])vm.runInContext(fs.readFileSync(path.join(root,file),'utf8'),c);
  return {c,run:s=>vm.runInContext(s,c)};
}
test('expanded analyses differ by tab and use split-adjusted shares without creating trades',()=>{
  const a=app();a.c.snapshot={current:{quarter:'2026 Q2',prevQuarter:'2026 Q1',holdings:[{ticker:'ABC',cusip:'123456789',shares:100,value:1500,shareAdjustment:{reportedShares:10,factor:10}}],previousHoldings:[{ticker:'ABC',cusip:'123456789',shares:10,value:1000}]},history:{}};
  const h=a.run("window.DisclosureAnalysis.render('holdings',snapshot)");
  const q=a.run("window.DisclosureAnalysis.render('changes',snapshot)");
  assert.match(h,/100 → 100（按拆股后可比口径）/);
  assert.match(q,/股数未变/);assert.match(q,/500 美元/);assert.doesNotMatch(q,/NaN|Infinity/);
  assert.notEqual(h,q);
});
test('historical analysis sorts available quarters, excludes invalid scopes and never fills missing filings',()=>{
  const a=app();const row={ticker:'ABC',cusip:'123456789',shares:10,value:100};
  a.c.snapshot={current:{holdings:[row]},history:{quarters:['2024 Q4','2023 Q1','2024 Q2','2024 Q3'],excludedValueQuarters:['2024 Q3'],holdings:{'2024 Q4':[row],'2023 Q1':[row],'2024 Q2':[row],'2024 Q3':[row]}}};
  let html=a.run("window.DisclosureAnalysis.render('history',snapshot)");
  assert.match(html,/这 3 份可用披露/);assert.ok(html.indexOf('2023 Q1')<html.indexOf('2024 Q2'));
  assert.doesNotMatch(html,/2023 Q2|2024 Q3|NaN/);
  a.c.snapshot.meta={reportingTransition:{comparisonScopeChanged:true,fromQuarter:'2024 Q2'}};
  html=a.run("window.DisclosureAnalysis.render('history',snapshot)");assert.doesNotMatch(html,/2023 Q1/);
});
test('all current investors have substantial bilingual holdings detail where figures are verified',()=>{
  const a=app();
  for(const p of read('investors.json').investors){
    a.c.snapshot=read(p.dataFile);
    for(const en of [false,true]){
      a.c.en=en;const html=a.run("window.DisclosureAnalysis.render('holdings',snapshot,en)");
      if(a.c.snapshot.meta?.portfolioMode==='public_projects'||a.c.snapshot.meta?.snapshotType||a.c.snapshot.current.valueQuality)assert.equal(html,'');
      else {assert.ok(html.length>600,p.id);assert.doesNotMatch(html,/NaN|Infinity|undefined/);}
    }
  }
});
test('option notional is distinguished from premium, principal units and unsafe issuer text remain correct',()=>{
  const a=app();a.c.snapshot=read('tests/fixtures/appaloosa-2026-q2.json');
  let html=a.run("window.DisclosureAnalysis.render('holdings',snapshot)");
  assert.match(html,/25,000 股/);assert.match(html,/0.16%/);assert.match(html,/不是投入权利金/);
  a.c.snapshot.current.holdings=[{ticker:'<img>',name:'<script>',shares:100,value:100,shareType:'PRN'}];
  html=a.run("window.DisclosureAnalysis.render('holdings',snapshot)");assert.doesNotMatch(html,/<script>|<img>/);assert.match(html,/本金/);
});
test('value detail preserves holder dates, directions and distinct allocation denominators',()=>{
  const a=app();a.c.rows=[{ticker:'TEST',mos:25,price:3,buy:4,investors:[{name:'甲',chg:'added',weight:10,reportQuarter:'2026 Q2'},{name:'乙',chg:'trimmed',weight:20,reportQuarter:'2026 Q1'}]}];
  const html=a.run('window.DisclosureAnalysis.value(rows)');
  for(const text of ['2026 Q2','2026 Q1','股数增加','股数减少','10.00%','20.00%','不能相加','不是相对企业内在价值'])assert.ok(html.includes(text),text);
});
test('quarterly detail includes every share change and refuses excluded prior-quarter money',()=>{
  const a=app();const old=Array.from({length:20},(_,i)=>({ticker:'TEST'+i,shares:10,value:100+i}));
  a.c.snapshot={current:{quarter:'2026 Q2',prevQuarter:'2026 Q1',previousHoldings:old,holdings:old.map(h=>({...h,shares:9,value:h.value+10}))},history:{}};
  const html=a.run("window.DisclosureAnalysis.render('changes',snapshot)");
  assert.match(html,/全部 20 项股数变化/);assert.match(html,/TEST19/);assert.match(html,/TEST0/);
  assert.match(html,/减持10.0%/);assert.match(html,/\$10.00 → \$12.22/);
  a.c.snapshot.history.excludedValueQuarters=['2026 Q1'];
  assert.equal(a.run("window.DisclosureAnalysis.render('changes',snapshot)"),'');
});
