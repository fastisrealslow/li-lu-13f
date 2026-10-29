const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),{performance}=require('node:perf_hooks');
const H=require('../history_explorer.js');
const read=f=>JSON.parse(fs.readFileSync(f,'utf8'));
const row=(n=10,more={})=>({ticker:'TEST',name:'Test',cusip:'123456789',cls:'COM',shares:n,value:n*100,shareType:'SH',putCall:'',...more});
const fixture=()=>({meta:{},current:{quarter:'2020 Q4'},history:{holdings:{'2020 Q1':[row()],'2020 Q2':[],'2020 Q4':[row(15)]}}});
test('missing report differs from absent security, reappearances and adjacent comparisons',()=>{
 const m=H.model(fixture()),k=H.securityKey(row(),'2020 Q1');
 assert.equal(m.point(k,'2020 Q2').shares,0);assert.equal(m.point(k,'2020 Q2').status,'absent');
 assert.equal(m.point(k,'2020 Q3').shares,null);assert.equal(m.change(k,'2020 Q4').kind,'unknown');
 assert.equal(m.change(k,'2020 Q2').kind,'absent');
 const x=fixture();x.history.holdings['2020 Q3']=[];const r=H.model(x);assert.equal(r.change(k,'2020 Q4').kind,'reappeared');assert.equal(r.change(k,'2020 Q4').delta,15);
});
test('evidenced economic transition links 1:1 legal identities, never options or another class',()=>{
 const a=row(50,{ticker:'GOOG',cusip:'38259P706',cls:'CL C'}),b={...a,cusip:'02079K107',cls:'CAP STK CL C'};
 assert.equal(H.securityKey(a,'2015 Q3'),H.securityKey(b,'2015 Q4'));
 for(const diff of [{putCall:'Put'},{putCall:'Call'},{shareType:'PRN'},{cls:'CL A'}])assert.notEqual(H.securityKey({...a,...diff},'2015 Q3'),H.securityKey(b,'2015 Q4'));
 assert.notEqual(H.securityKey(a,'2015 Q4'),H.securityKey(b,'2015 Q4'));
 const m=H.model({history:{holdings:{'2015 Q3':[a],'2015 Q4':[b]}}}),key=H.securityKey(b,'2015 Q4');
 assert.equal(m.securities.size,1);assert.equal(m.change(key,'2015 Q4').kind,'action');assert.equal(m.change(key,'2015 Q4').delta,null);assert.equal(m.reports.get('2015 Q3').rows[0].cusip,a.cusip);
});
test('split quarters and manager scope changes do not claim net transactions',()=>{
 const x={history:{holdings:{'2022 Q2':[row(10)],'2022 Q3':[row(200)]}}},key=H.securityKey(row(),'2022 Q3');
 const m=H.model(x,{actions:()=>[{quarter:'2022 Q3',factor:20}]});assert.equal(m.change(key,'2022 Q3').kind,'action');assert.equal(m.change(key,'2022 Q3').delta,null);
 x.meta={reportingTransition:{comparisonScopeChanged:true,fromQuarter:'2022 Q3'}};assert.equal(H.model(x).change(key,'2022 Q3').kind,'unknown');
});
test('unverified value quarter retains shares without fabricating zero values or weights',()=>{
 const x=fixture();x.history.excludedValueQuarters=['2020 Q1'];const m=H.model(x),k=H.securityKey(row(),'2020 Q1');
 assert.equal(m.point(k,'2020 Q1').shares,10);assert.equal(m.point(k,'2020 Q1').value,null);assert.equal(m.point(k,'2020 Q1').weight,null);assert.equal(m.portfolio('2020 Q1').total,null);
 const webb=H.model(read('webb.json'));assert.equal(webb.disabled,true);
});
test('all 17 model histories preserve rows, values, shares and source data',()=>{
 for(const person of read('investors.json').investors){const data=read(person.dataFile),original=JSON.stringify(data),m=H.model(data);
  for(const [q,rows]of Object.entries(data.history?.holdings||{})){const r=m.reports.get(q);for(const field of ['shares','value'])assert.equal(r.rows.reduce((s,h)=>s+h[field],0),rows.reduce((s,h)=>s+h[field],0),person.id+' '+q+' '+field);}
  assert.equal(JSON.stringify(data),original);
 }
});
test('Greenblatt complete history contains exited old positions, stable sorting and bounded pages',()=>{
 const data=read('greenblatt.json'),start=performance.now(),m=H.model(data);
 assert.equal(m.keys.length,63);assert.equal(m.reports.get('2010 Q4').positions.size,358);assert.ok(m.securities.size>=4600);
 const report=m.portfolio('2010 Q4'),old=report.rows.find(h=>!m.reports.get(m.currentQuarter).positions.has(h.key));assert.ok(old);
 const found=m.listed({q:'2010 Q4',query:old.cusip,size:50});assert.ok(found.rows.some(h=>h.key===old.key));
 const page=m.listed({q:m.currentQuarter,size:50});assert.ok(page.rows.length<=50);assert.equal(new Set(page.rows.map(h=>h.key)).size,page.rows.length);
 const all=[];for(let i=0;i<page.pages;i++)all.push(...m.listed({q:m.currentQuarter,page:i,size:50}).rows.map(h=>h.key));assert.equal(all.length,new Set(all).size);
 const max=m.listed({q:m.currentQuarter,size:99999});assert.ok(max.rows.length<=100);
 assert.ok(performance.now()-start<8000,'complete model and all pages complete within 8 seconds');
});
test('Li Lu GOOGL unchanged share run exposes weight drift; PDD share growth remains separate',()=>{
 const m=H.model(read('data.json')),a=[...m.securities].find(([key,s])=>s.row.ticker==='GOOGL'),b=[...m.securities].find(([key,s])=>s.row.ticker==='PDD');
 const points=m.series(a[0],'2024 Q3','2026 Q2');assert.equal(points.length,8);assert.ok(points.every(p=>p.shares===2543300));assert.ok(Math.abs(points[0].weight-17.06)<.02);assert.ok(Math.abs(points.at(-1).weight-24.55)<.02);
 assert.equal(m.change(b[0],'2026 Q2').shares,10761119);assert.equal(m.change(b[0],'2026 Q2').previousShares,4608000);
});
