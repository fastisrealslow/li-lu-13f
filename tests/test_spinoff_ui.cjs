const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
function app() {
 const memory=new Map();
 const context=vm.createContext({lang:'zh',URL,Date,console,localStorage:{getItem:k=>memory.get(k),setItem:(k,v)=>memory.set(k,v)}});
 vm.runInContext(fs.readFileSync(path.join(__dirname,'../spinoff_ui.js'),'utf8'),context);
 return {run:code=>vm.runInContext(code,context),context};
}
const event={id:'us:P:unresolved',parentTicker:'P',parentName:'Parent',targetName:'Child',targetTicker:'C',type:'spinoff',status:'needs_review',missing:['evidence'],identityVerified:false,latestDate:'2026-09-16',dates:{distributionDate:{date:'2026-09-20'}},announcements:[],fingerprint:'v1'};
test('watchlist, unread, upcoming and search filters use event identity',()=>{
 const a=app(); a.context.event=event;
 a.run("spinDash.us.data={events:[event],changes:[]}; spinSave(event.id,{watch:true,read:'v1',note:'研究'}); spinDash.us.view='watch'");
 assert.equal(a.run('spinVisible(spinDash.us,spinPrefs()).length'),1);
 a.run("spinDash.us.view='unread'"); assert.equal(a.run('spinVisible(spinDash.us,spinPrefs()).length'),0);
 a.run("spinDash.us.view='upcoming'"); assert.equal(a.run("spinVisible(spinDash.us,spinPrefs(),Date.parse('2026-09-16')).length"),1);
 a.run("spinDash.us.query='NO_MATCH'"); assert.equal(a.run('spinVisible(spinDash.us,spinPrefs()).length'),0);
 assert.equal(a.run('spinPrefs()[event.id].note'),'研究');
});
test('completion prevents stale planned dates appearing as upcoming',()=>{
 const a=app();a.context.event={...event,status:'completed'};
 assert.equal(a.run("spinUpcoming(event,Date.parse('2026-09-16')).length"),0);
});
test('all types include REIT and filtered counts use the same population',()=>{
 const a=app(); a.context.event=event;
 a.run("spinDash.hk.data={events:[event,{...event,id:'reit',type:{is_reit:true}}]}");
 assert.equal(a.run('spinBaseEvents(spinDash.hk).length'),2);
 a.run("spinDash.hk.type='reit'");assert.equal(a.run('spinVisible(spinDash.hk,{}).length'),1);
});
test('source text and notes are escaped and unsafe URLs rejected',()=>{
 const a=app(); a.context.event={...event,targetName:'<img src=x onerror=alert(1)>',announcements:[{title:'<script>bad</script>',date:'2026-09-16',url:'javascript:alert(1)',direct:false}]};
 const html=a.run("spinCard(event,{note:'</textarea><script>bad</script>'})");
 assert.ok(!html.includes('<script>'));assert.ok(!html.includes('href="javascript:'));assert.ok(html.includes('&lt;img'));
 assert.equal(a.run("spinURL('https://user:pass@example.org')"),'');
});
test('language changes render fresh status and dossier text',()=>{
 const a=app();a.context.event=event;
 assert.match(a.run('spinCard(event)'),/待核实/);a.run("lang='en'");assert.match(a.run('spinCard(event)'),/Needs review/);
});
test('storage failure is reported without breaking research views',()=>{
 const a=app();a.context.localStorage.setItem=()=>{throw new Error('blocked')};
 assert.equal(a.run("spinSave('id',{watch:true})"),false);
 assert.equal(a.run('spinStorageFailed'),true);
});
function asyncApp() {
 const a=app();a.context.AbortController=AbortController;a.context.setTimeout=setTimeout;a.context.clearTimeout=clearTimeout;
 const root={innerHTML:'',querySelector:()=>({disabled:false,textContent:''})};
 a.context.document={getElementById:()=>root};a.run('spinPaint = market => { spinDash[market].painted=spinDash[market].data.updatedAt; }');
 return a;
}
test('failed refresh retains the last successful dataset',async()=>{
 const a=asyncApp();a.run("spinDash.us.data={events:[],updatedAt:'old'}");a.context.fetch=async()=>({ok:false,status:503});
 await a.run("renderSpinoffDashboard('us',true)");
 assert.equal(a.run('spinDash.us.data.updatedAt'),'old');assert.equal(a.run('spinDash.us.error'),true);
});
test('late refresh cannot overwrite a newer response',async()=>{
 const a=asyncApp();let finish;let calls=0;
 a.context.fetch=async()=>++calls===1 ? new Promise(r=>{finish=r}) : {ok:true,json:async()=>({eventsSchemaVersion:1,events:[],updatedAt:'new'})};
 const old=a.run("renderSpinoffDashboard('us',true)");
 await a.run("renderSpinoffDashboard('us',true)");
 finish({ok:true,json:async()=>({eventsSchemaVersion:1,events:[],updatedAt:'old'})});await old;
 assert.equal(a.run('spinDash.us.data.updatedAt'),'new');
});
test('change feed names companies, explains new leads, and escapes source text',()=>{
 const a=app();a.context.event={...event,parentName:'中国中车 <script>bad</script>'};
 const html=a.run("spinChangesHTML({events:[event],changes:[{eventId:event.id,at:new Date().toISOString(),kind:'new',fields:['status'],toStatus:'needs_review'}]})");
 assert.match(html,/中国中车 &lt;script&gt;/);assert.ok(!html.includes('<script>'));
 assert.match(html,/新收录分拆线索/);assert.ok(!html.includes('待核实 → 待核实'));
 assert.match(html,/data-open-event=/);
});
test('exact change snapshots distinguish historical values from current records',()=>{
 const a=app();a.context.event=event;
 assert.equal(a.run("spinChangeDescription({kind:'updated',fields:['targetName'],before:{targetName:'Old'},after:{targetName:'New'}},event)"),'分拆标的: Old → New');
 const legacy=a.run("spinChangeDescription({kind:'updated',fields:['targetName']},event)");
 assert.match(legacy,/未保存修改前内容/);assert.match(legacy,/当前记录：Child/);assert.ok(!legacy.includes('→'));
});
test('empty change records are excluded and all changes remain accessible',()=>{
 const a=app();a.context.event=event;
 assert.equal(a.run("spinRecentChanges({changes:[{at:new Date().toISOString(),kind:'updated',fields:[]}]}).length"),0);
 const html=a.run("spinChangesHTML({events:[event],changes:Array.from({length:8},()=>({eventId:event.id,at:new Date().toISOString(),kind:'new',toStatus:'needs_review'}))})");
 assert.match(html,/查看全部 8 条变化/);
});
test('cards identify missing fields and translate spin-off types',()=>{
 const a=app();a.context.event=event;
 const html=a.run('spinCard(event)');assert.match(html,/分拆标的：/);assert.match(html,/状态依据、公司对应关系/);assert.match(html,/最新公告：/);
 assert.equal(a.run("spinTypeName('carveout')"),'分拆上市');
 assert.equal(a.run("spinIssuerName({parentName:'Example Inc. (ABC)',parentTicker:'ABC'})"),'Example Inc.');
});
