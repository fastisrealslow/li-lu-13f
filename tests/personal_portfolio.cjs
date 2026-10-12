const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {rank,esc,capitalReading,explanations,equations}=require('../personal_portfolio.js');
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

test('negative capital distinguishes arithmetic from a usable ROC and zero never divides',()=>{
  const negative=capitalReading({ebit:12310000000,investedCapital:-3407000000,returnOnCapital:null});
  assert.equal(negative.label,'不适用');assert.equal(negative.applicable,false);
  assert(Math.abs(negative.arithmetic-(-3.6131493982976224))<1e-12);
  const zero=capitalReading({ebit:1,investedCapital:0,returnOnCapital:null});
  assert.equal(zero.arithmetic,null);assert.equal(zero.applicable,false);
  const loss=capitalReading({ebit:-1,investedCapital:10,returnOnCapital:-.1});
  assert.equal(loss.label,'-10.00%');assert.equal(loss.applicable,true);
  assert.equal(capitalReading({}).label,'待更新');
});

test('every holding explains actual EV and capital numbers in both modes with ranking scope',()=>{
  const data=JSON.parse(fs.readFileSync(path.join(root,'personal_portfolio.json'),'utf8'));
  for(const years of ['1','3']){
    const rows=rank(data.companies.map(c=>({...c.results[c.listings[0].ticker][years],id:c.id})));
    const eligible=rows.filter(r=>r.status==='ranked').length;
    for(const r of rows){
      const c=data.companies.find(c=>c.id===r.id),notes=explanations(c,r,eligible);
      assert(notes.some(n=>n.title.includes('盈利收益率')));
      assert(notes.some(n=>n.title.includes('资本分母')));
      const text=notes.map(n=>n.body).join(' ');
      assert(!/NaN|Infinity|undefined/.test(text));
      if(r.status==='ranked')assert(text.includes(`只有 ${eligible} 只`));
      if(r.investedCapital<0 && r.ebit>0)assert(text.includes('不表示公司亏损'));
      const html=equations(c,r);
      assert(html.includes('ROC = EBIT ÷ (净运营资本＋有形固定资本)'));
      assert(html.includes('经营性流动资产'));
      if(r.investedCapital<0){assert(html.includes('负百分比只展示算术结果'));assert(html.includes('不等于公司净资产为负'));assert(html.includes('供应商账期、客户预付款'));assert(!html.includes('= <b>—</b>'));}
      if(years==='3')assert(html.includes('平均有形经营资本'));
    }
  }
});

test('explanations respond to new prices without changing the capital diagnosis',()=>{
  const data=JSON.parse(fs.readFileSync(path.join(root,'personal_portfolio.json'),'utf8'));
  const c=data.companies.find(c=>c.id==='lining'),r=c.results[c.listings[0].ticker]['1'];
  const higher={...r,equityValue:r.equityValue*2,enterpriseValue:r.enterpriseValue+r.equityValue};
  higher.earningsYield=r.ebit/higher.enterpriseValue;
  const old=explanations(c,r),next=explanations(c,higher);
  assert.notEqual(old[0].body,next[0].body);assert.equal(old[1].body,next[1].body);
});

test('Tencent Music other gains are identified as already included, never added twice',()=>{
  const data=JSON.parse(fs.readFileSync(path.join(root,'personal_portfolio.json'),'utf8'));
  const c=data.companies.find(c=>c.id==='tme'),r=c.results[c.listings[0].ticker]['1'];
  const notes=explanations(c,r);
  assert(notes.some(n=>n.body.includes('不再重复相加')));
});
