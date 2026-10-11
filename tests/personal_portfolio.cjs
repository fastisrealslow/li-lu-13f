const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {rank,esc}=require('../personal_portfolio.js');
const root=path.resolve(__dirname,'..');

test('personal tab follows trials and remains a separate panel',()=>{
  const html=fs.readFileSync(path.join(root,'index.html'),'utf8');
  assert(html.indexOf("switchTab('personal')")>html.indexOf("switchTab('game')"));
  assert(html.includes('id="tab-personal"'));
  const app=fs.readFileSync(path.join(root,'app.js'),'utf8');
  assert(app.includes("'game','personal'"));assert(app.includes("name==='personal'"));
});

test('ranking uses the two unrounded ratios, preserves ties, and excludes invalid denominators',()=>{
  const rows=[{id:'a',status:'ranked',earningsYield:.1,returnOnCapital:.2},
    {id:'b',status:'ranked',earningsYield:.1,returnOnCapital:.3},
    {id:'negative',status:'not_ranked',earningsYield:1,returnOnCapital:null}];
  const result=rank(rows);assert.equal(result[0].id,'b');assert.equal(rows[0].earningsRank,1);
  assert.equal(result[2].id,'negative');assert.equal(result[2].overallRank,undefined);
});

test('all eight report-backed holdings stay visible in both annual modes',()=>{
  const data=JSON.parse(fs.readFileSync(path.join(root,'personal_portfolio.json'),'utf8'));
  for(const years of ['1','3']){
    const rows=rank(data.companies.map(c=>({...c.results[c.listings[0].ticker][years],id:c.id})));
    assert.equal(rows.length,8);assert.equal(new Set(rows.map(r=>r.id)).size,8);
    rows.filter(r=>r.status==='ranked').forEach(r=>assert.equal(r.rankSum,r.earningsRank+r.capitalRank));
  }
});

test('financial-source evidence is safely escaped',()=>{
  assert.equal(esc('<script>"&'), '&lt;script&gt;&quot;&amp;');
});
