const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const root = path.join(__dirname, '..');
const read = name => JSON.parse(fs.readFileSync(path.join(root, name), 'utf8'));
function app() {
  const nodes = new Map();
  const el = id => {
    if (!nodes.has(id)) nodes.set(id, {innerHTML:'', style:{}});
    return nodes.get(id);
  };
  const context = vm.createContext({console, Date, localStorage:{getItem:()=>null}, window:{innerWidth:1440},
    document:{readyState:'loading', addEventListener(){}, getElementById:el}});
  vm.runInContext(fs.readFileSync(path.join(root, 'app.js'), 'utf8'), context);
  context.config = read('investors.json').investors;
  context.artifact = read('ai_supplement.json');
  const run = code => vm.runInContext(code, context);
  run('INVESTOR_CFG_BY_ID=Object.fromEntries(config.map(c=>[c.id,c]));_aiSupplement=artifact');
  return {context, el, run};
}
test('published summaries match each investor and each independent tab source in both languages', () => {
  const a = app();
  for (const cfg of a.context.config) {
    a.context.snapshot = read(cfg.dataFile);
    a.context.id = cfg.id;
    a.run('investor=id;data=snapshot');
    for (const kind of ['holdings','history']) {
      a.context.kind = kind;
      if (!a.context.artifact.entries[kind+':'+cfg.id]) continue;
      for (const language of ['zh','en']) {
        a.context.language = language;
        assert.equal(a.run('lang=language;!!scopedSummaryEntry(kind,data)'), true, `${kind}/${cfg.id}/${language}`);
        a.run('renderScopedInsight(kind)');
        const html=a.el(kind==='holdings'?'holdingsInsight':'historyInsight').innerHTML;
        assert.ok(html.includes('briefing-headline'),`${kind}/${cfg.id}/${language}`);
        assert.ok(html.includes('briefing-lead'),`${kind}/${cfg.id}/${language}`);
        assert.ok(!html.includes('scope-lens'));
        assert.ok(!html.includes('重点（非完整名单）'));
      }
    }
    a.run("lang='zh';renderInsights()");
    const contents=['holdingsInsight','changesAISummary','historyInsight'].map(id=>a.el(id).innerHTML);
    assert.equal(new Set(contents).size, 3, cfg.id);
  }
});
test('historical corrections invalidate history alone; current corrections invalidate both tab summaries', () => {
  const a=app();a.context.snapshot=read('data.json');
  a.run("investor='lilu';data=snapshot");
  assert.ok(a.run("scopedSummaryEntry('holdings',data)"));
  assert.ok(a.run("scopedSummaryEntry('history',data)"));
  a.run('data.history.holdings[Object.keys(data.history.holdings)[0]][0].value+=1');
  assert.ok(a.run("scopedSummaryEntry('holdings',data)"));
  assert.equal(a.run("scopedSummaryEntry('history',data)"),null);
  a.run('data.current.holdings[0].shares+=1');
  assert.equal(a.run("scopedSummaryEntry('holdings',data)"),null);
});
test('invalid selected text and omission of a mandatory option limitation cannot display as AI', () => {
  const a=app();
  const cfg=a.context.config.find(c=>a.context.artifact.entries['holdings:'+c.id]?.facts.requiredIds.length);
  assert.ok(cfg);
  a.context.id=cfg.id;a.context.snapshot=read(cfg.dataFile);
  a.run("investor=id;data=snapshot;_aiSupplement.entries['holdings:'+id].summary+='错误数字 999'");
  assert.equal(a.run("scopedSummaryEntry('holdings',data)"),null);
  a.context.artifact=read('ai_supplement.json');a.run('_aiSupplement=artifact');
  a.run("_aiSupplement.entries['holdings:'+id].selection.factIds=['f0']");
  assert.equal(a.run("scopedSummaryEntry('holdings',data)"),null);
});
test('value overview counts qualifying holders and preserves opposite share directions', () => {
  const a=app();a.context.rows=[
    {ticker:'MIX',mos:25,totalHolders:3,investors:[{chg:'added'},{chg:'trimmed'}]},
    {ticker:'SOLO',mos:10,totalHolders:4,investors:[{chg:'new'}]},
    {ticker:'HOLD',mos:30,investors:[{chg:'hold'}]}
  ];
  const zh=a.run('valueScreenOverview(rows,false)');
  assert.match(zh,/本轮 3 只/);assert.match(zh,/其中 2 只价格/);assert.match(zh,/1 只同时有至少两位/);
  assert.match(zh,/2 只出现新建仓或增持，1 只出现减持/);assert.match(zh,/1 只存在方向分歧（MIX）/);
  assert.match(a.run('valueScreenOverview(rows,true)'),/These groups can overlap/);
});
test('narrative headings and evidence are escaped and generic advice does not replace the figures',()=>{
  const a=app();a.context.b={version:1,headline:['<img src=x>','<img src=x>'],lead:['90% 与 10%','90% and 10%'],details:[{label:['重点','Evidence'],text:['<script>bad</script>','<script>bad</script>']}],notes:[]};
  const html=a.run('briefingHTML(b)');
  assert.match(html,/&lt;img/);assert.match(html,/&lt;script/);assert.ok(!html.includes('<script>'));
  assert.match(html,/90% 与 10%/);
  assert.ok(!html.includes('scope-lens'));
});
test('model topic ordering preserves the whole narrative and rejects foreign topics',()=>{
  const a=app();a.context.b={version:1,headline:['主线','Main point'],lead:['50%','50%'],details:[{label:['第一','First'],text:['10%','10%']},{label:['第二','Second'],text:['20%','20%']},{label:['第三','Third'],text:['30%','30%']}],notes:[]};
  const ordered=JSON.parse(a.run("JSON.stringify(orderedBriefing(b,['t2','t0']))"));
  assert.deepEqual(ordered.details.map(d=>d.text[0]),['30%','10%','20%']);
  assert.deepEqual(ordered.headline,a.context.b.headline);assert.equal(ordered.lead[0],'50%');
  assert.equal(a.run("orderedBriefing(b,['t0','t0'])"),null);
  assert.equal(a.run("orderedBriefing(b,['t999'])"),null);
});
test('reporting scope changes break chart lines and never produce a cross-scope growth claim', () => {
  const a=app();a.run("data={current:{quarter:'2026 Q2'},meta:{reportingTransition:{comparisonScopeChanged:true,fromQuarter:'2026 Q2'}}}");
  assert.equal(a.run("historySegments(['2026 Q1','2026 Q2']).length"),2);
  const text=a.run("generateHistoryInsight(['2026 Q1','2026 Q2'],[10,1000])");
  assert.ok(!text.includes('9900'));assert.match(text,/申报范围/);
});
test('an older empty value response cannot replace a newer language result', async () => {
  const a=app();let release;let requests=0;
  a.context.fetch=()=>++requests===1?new Promise(resolve=>release=resolve):Promise.resolve({ok:true,json:async()=>({candidates:[]})});
  const older=a.run("lang='zh';renderHomework()");
  await a.run("lang='en';renderHomework()");
  release({ok:true,json:async()=>({candidates:[]})});await older;
  assert.match(a.el('homeworkContent').innerHTML,/No stocks/);
  assert.ok(!a.el('homeworkContent').innerHTML.includes('暂无'));
});
test('a value cache hit cancels older requests and caches never cross languages', async () => {
  const a=app();let release;
  a.context.fetch=()=>new Promise(resolve=>release=resolve);
  const older=a.run("lang='zh';renderHomework()");
  a.run("_homeworkCache='newer cached result';_homeworkCachedAt=Date.now();_homeworkCachedLanguage='zh'");
  await a.run('renderHomework()');
  release({ok:true,json:async()=>({candidates:[]})});await older;
  assert.equal(a.el('homeworkContent').innerHTML,'newer cached result');
  a.context.fetch=async()=>({ok:true,json:async()=>({candidates:[]})});
  await a.run("lang='en';renderHomework()");
  assert.match(a.el('homeworkContent').innerHTML,/No stocks/);
});
