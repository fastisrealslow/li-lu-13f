const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const gate=()=>{let resolve,reject;const promise=new Promise((a,b)=>{resolve=a;reject=b});return {promise,resolve,reject}};
function bundle(id,price){return {version:1,investor:id,data:{meta:{lastUpdated:new Date().toISOString()},current:{quarter:'2026 Q2',prevQuarter:'2026 Q1',totalValue:price*10,holdings:[{ticker:id.toUpperCase(),shares:10,value:price*10}],previousHoldings:[]},history:{quarters:[],values:[],holdings:{}},browserProjection:{version:1,sources:{}}},prices:{quotes:{[id.toUpperCase()]:{c:price,t:Date.now()/1000}},costBasis:{}},hk:null,insights:{schemaVersion:2,entries:{}},history:{file:`browser/${id}-history-${'a'.repeat(24)}.json`}}}
function app(loader){const nodes=new Map(),calls=[];const element=id=>{if(!nodes.has(id)){const classes=new Set();nodes.set(id,{innerHTML:'',textContent:'',hidden:true,value:'',style:{},classList:{contains:k=>classes.has(k),toggle(k,on){on?classes.add(k):classes.delete(k)},add:k=>classes.add(k),remove:k=>classes.delete(k)},setAttribute(){}})}return nodes.get(id)};const c=vm.createContext({console,Date,AbortController,setTimeout,clearTimeout,localStorage:{getItem:()=>null,setItem(){}},window:{},InvestorSnapshots:loader,document:{readyState:'loading',addEventListener(){},body:{classList:{toggle(){}}},getElementById:element,querySelectorAll:()=>[]}});vm.runInContext(fs.readFileSync('app.js','utf8'),c);c.record=name=>calls.push(name);vm.runInContext("INVESTORS=['old','large'];INVESTOR_CFG_BY_ID={old:{id:'old',name:'旧投资人',nameEn:'Old'},large:{id:'large',name:'大组合',nameEn:'Large'}};INVESTOR_LABELS={old:'旧投资人',large:'大组合'};INVESTOR_LABELS_EN={old:'Old',large:'Large'};renderInvestorBtns=renderSummary=updateInvestorContent=()=>{};renderHoldings=()=>record('holdings');renderChanges=()=>record('changes');renderHistoryChart=()=>record('chart');renderTimelineTable=()=>record('timeline');renderHKDisclosures=()=>{};renderScopedInsight=kind=>{if(kind==='history')record('history-insight')};renderInsights=()=>record('insights');",c);return {c,run:s=>vm.runInContext(s,c),element,calls}}
test('a slow selection shows progress and commits holdings and quotes together',async()=>{const delayed=gate(),a=app({load:async id=>id==='large'?delayed.promise:bundle(id,10)});await a.run("switchInvestor('old')");a.calls.length=0;const pending=a.run("switchInvestor('large')");await Promise.resolve();assert.equal(a.run('investor'),'old');assert.equal(a.run('prices.quotes.OLD.c'),10);assert.equal(a.element('investorLoadState').hidden,false);assert.match(a.element('investorLoadState').textContent,/大组合/);delayed.resolve(bundle('large',42));assert.equal(await pending,true);assert.equal(a.run('investor'),'large');assert.equal(a.run('prices.quotes.LARGE.c'),42);assert.deepEqual(a.calls,['holdings']);});
test('a failed selection retains the old quote and releases the loading state',async()=>{let fail=false;const a=app({load:async id=>{if(fail)throw Error('network down');return bundle(id,10)}});await a.run("switchInvestor('old')");fail=true;assert.equal(await a.run("switchInvestor('large')"),false);assert.equal(a.run('investor'),'old');assert.equal(a.run('prices.quotes.OLD.c'),10);assert.match(a.element('investorLoadState').textContent,/重新选择/);assert.equal(a.element('investorSelect').value,'old');});
test('late history cannot overwrite the next investor and is loaded only when its tab opens',async()=>{const delayed=gate(),seen=[];const a=app({load:async id=>bundle(id,id==='large'?42:10),history:async(asset,options)=>{seen.push(options.signal);return asset.file.includes('large-history')?delayed.promise:Promise.resolve({version:1,investor:'old',history:{holdings:{}},exitPerf:{}})}});await a.run("switchInvestor('large')");assert.equal(seen.length,0);a.run("switchTab('history')");assert.ok(a.calls.includes('history-insight'));const waiting=a.run('_historyRequest.promise');assert.equal(seen.length,1);await a.run("switchInvestor('old')");assert.equal(seen[0].aborted,true);delayed.resolve({version:1,history:{holdings:{wrong:[{ticker:'LARGE'}]}},exitPerf:{}});await waiting;assert.equal(a.run('investor'),'old');assert.equal(a.run('data.history.holdings.wrong'),undefined);assert.equal(a.run('prices.quotes.OLD.c'),10);});
test('mobile pagination retains every security and keeps the current area after resizing',()=>{const a=app({});a.c.window.innerWidth=390;a.c.rows=Array.from({length:1791},(_,i)=>({ticker:'T'+i,cusip:String(i)}));a.run("investor='large'");const seen=[];for(let page=0;page<36;page++){a.c.page=page;a.run("_portfolioViews.current={investor:'large',query:'',page}");const rows=Array.from(a.run("portfolioVisibleIndexes('current',rows)"));assert.ok(rows.length<=50);seen.push(...rows)}assert.equal(new Set(seen).size,1791);a.c.window.innerWidth=1440;assert.ok(Array.from(a.run("portfolioVisibleIndexes('current',rows)")).includes(1750));});

test('closed option details never force table layout; opened details track visible columns',()=>{
  const a=app({});let reads=0;const cell={colSpan:7};let open=false;
  a.c.getComputedStyle=()=>{reads++;return {display:'table-cell'}};
  a.c.document.querySelectorAll=selector=>selector.includes(':not([hidden])')?(open?[cell]:[]):[{}, {}, {}, {}];
  a.run('syncOptionDetailColumns()');assert.equal(reads,0);
  open=true;a.run('syncOptionDetailColumns()');assert.equal(reads,4);assert.equal(cell.colSpan,4);
});
test('arrival of full history renders the timeline without redrawing the overview chart',async()=>{
  const delayed=gate(),a=app({load:async id=>bundle(id,10),history:async()=>delayed.promise});
  await a.run("switchInvestor('old')");a.run("switchTab('history')");const waiting=a.run('_historyRequest.promise');
  const before=a.calls.filter(x=>x==='chart').length;
  delayed.resolve({history:{holdings:{}},exitPerf:{}});await waiting;
  assert.equal(a.calls.filter(x=>x==='chart').length,before);
  assert.equal(a.calls.filter(x=>x==='timeline').length,1);
});

test('medium mobile portfolios paginate without omitting any securities',()=>{
  const a=app({});a.c.window.innerWidth=390;a.c.rows=Array.from({length:131},(_,i)=>({ticker:'T'+i,cusip:String(i)}));a.run("investor='large'");const seen=[];
  for(let page=0;page<3;page++){a.c.page=page;a.run("_portfolioViews.current={investor:'large',query:'',page}");seen.push(...Array.from(a.run("portfolioVisibleIndexes('current',rows)")));}
  assert.equal(new Set(seen).size,131);assert.match(a.element('holdingsControls').innerHTML,/上一页/);
});
test('timeline calculations reuse an immutable history and invalidate replaced records',()=>{
  const a=app({});a.run("data={meta:{},current:{holdings:[]},history:{holdings:{'2025 Q1':[{ticker:'OLD',name:'Example',cls:'COM',shares:10,value:20}]}}};globalThis.firstModel=timelineModel(data)");
  assert.equal(a.run('timelineModel({...data,history:{...data.history}})===firstModel'),true);
  a.run("data.history={holdings:{'2025 Q2':[{ticker:'NEW',name:'New',cls:'COM',shares:20,value:30}]}}");
  assert.equal(a.run('timelineModel(data)===firstModel'),false);
  assert.equal(a.run('timelineModel(data).entries[0].ticker'),'NEW');
});
