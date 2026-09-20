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
  assert.match(a.el('historyInsight').textContent,/暂无历史数据/);
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
 assert.match(a.el('historyInsight').textContent,/无法与披露日期核对/);
 await a.run('renderHKHoldings=()=>{};renderTimelineTable()');
 assert.match(a.el('timelineCanvas').innerHTML,/暂不展示/);
});
