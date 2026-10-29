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
test('recent records are an ordered subset of all and show the same current status',()=>{
 const a=app();a.context.events=[{...event,id:'older',changedAt:'2026-10-01T01:00:00Z',latestDate:'2026-10-10'},
  {...event,id:'corrected',changedAt:'2026-10-10T01:00:00Z',latestDate:'2026-02-25',status:'completed',updateKind:'correction'},
  {...event,id:'new-filing',changedAt:'2026-10-09T01:00:00Z',latestDate:'2026-10-08',updateKind:'new_filing'}];
 a.run('spinDash.hk.data={events,changes:[{eventId:"gone",at:"2026-10-10T03:00:00Z",kind:"new"}]};spinDash.hk.view="all"');
 assert.equal(a.run('spinVisible(spinDash.hk,{}).map(e=>e.id).join(",")'),'older,new-filing,corrected');
 a.run('spinDash.hk.view="changes"');assert.equal(a.run('spinVisible(spinDash.hk,{},Date.parse("2026-10-10T12:00:00Z")).map(e=>e.id).join(",")'),'older,new-filing');
 const html=a.run('spinCard(events[1])');assert.ok(!html.includes('档案信息修正')); assert.match(html,/公告：2026-02-25/);assert.match(html,/公告称已完成/);
 assert.equal(a.run('spinDash.us.view'),'all');
});
test('issuer updates group multiple targets without losing links or before/after values',()=>{
 const a=app();a.context.events=[event,{...event,id:'us:P:second',targetName:'Different project',mergedIds:['us:P:old']},{...event,id:'us:OTHER:one',parentTicker:'OTHER',parentName:'Other'}];
 a.context.changes=[{eventId:event.id,at:new Date().toISOString(),kind:'updated',fields:['status'],fromStatus:'announced',toStatus:'approved'},{eventId:'us:P:old',at:new Date().toISOString(),kind:'updated',fields:['targetName'],before:{targetName:'Prior name'},after:{targetName:'Different project'}},{eventId:'us:OTHER:one',at:new Date().toISOString(),kind:'new'}];
 const html=a.run('spinChangesHTML({events,changes},true)');
 assert.equal(a.run('spinChangeGroups({events,changes}).length'),2);
 assert.match(html,/2 次更新 · 2 个对应档案/);
 assert.match(html,/data-open-event="us:P:second"/);assert.ok(!html.includes('data-open-event="us:P:old"'));
 assert.match(html,/Prior name → Different project/);assert.match(html,/最近原公告 2026-09-16/);
 a.run('spinDash.us.data={events,changes};spinDash.us.view="changes"');assert.equal(a.run('spinVisible(spinDash.us,{},Date.parse("2026-09-17")).length'),3);
});
test('auto watch includes every introduction, persists across refresh and preserves manual notes',()=>{
 const a=app();a.context.events=[{...event,id:'hk:1',type:{code:'intro_hk'}},{...event,id:'hk:2',type:'intro_th'},{...event,id:'hk:3',type:{code:'reit_sh',is_reit:true}}];
 a.run('spinSave("hk:1",{note:"keep",read:"v1"});spinSave("manual",{watch:true});spinAutoWatchIntroductions({events})');
 assert.equal(a.run('spinPrefs()["hk:1"].watch'),true);assert.equal(a.run('spinPrefs()["hk:2"].autoIntro'),true);
 assert.equal(a.run('spinPrefs()["hk:1"].note'),'keep');assert.equal(a.run('spinPrefs()["hk:1"].read'),'v1');assert.equal(a.run('spinPrefs()["manual"].watch'),true);assert.equal(a.run('spinPrefs()["hk:3"]'),undefined);
 a.run('spinSave("hk:1",{watch:false});spinAutoWatchIntroductions({events})');assert.equal(a.run('spinPrefs()["hk:1"].watch'),true);
 a.context.events.push({...event,id:'hk:new',type:{code:'intro_hk',is_reit:true}});a.run('spinAutoWatchIntroductions({events})');assert.equal(a.run('spinPrefs()["hk:new"].watch'),true);
});
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
 assert.match(html,/8 次更新 · 1 个对应档案/);
 assert.equal((html.match(/<strong>Parent<\/strong>/g)||[]).length,1);
 assert.equal((html.match(/新收录分拆线索/g)||[]).length,8);
});
test('cards show key facts without internal data checklists',()=>{
 const a=app();a.context.event=event;
 const html=a.run('spinCard(event)');assert.match(html,/分拆 \/ 分派标的：/);assert.ok(!/状态依据|公司对应关系|待补全 \/ 核实|研究待办/.test(html));assert.match(html,/公告：/);
 assert.equal(a.run("spinTypeName('carveout')"),'分拆上市');
 assert.equal(a.run("spinIssuerName({parentName:'Example Inc. (ABC)',parentTicker:'ABC'})"),'Example Inc.');
});

test('actual listing dates are labeled as confirmed, not scheduled distributions',()=>{
 const a=app();a.context.event={...event,status:'completed',dates:{listingDate:{date:'2025-10-15',kind:'actual',url:'https://www1.hkexnews.hk/listedco/completion.pdf'}}};
 const html=a.run('spinCard(event)');
 assert.match(html,/上市日 · 2025-10-15/);assert.match(html,/公告确认已发生/);assert.ok(!html.includes('计划日期，可能调整'));
 a.run("lang='en'");assert.match(a.run('spinCard(event)'),/Listing date · 2025-10-15/);
});

test('paused dossiers have their own status and no stale upcoming dates',()=>{
 const a=app();a.context.event={...event,status:'paused'};
 assert.match(a.run('spinCard(event)'),/暂不推进/);
 assert.equal(a.run("spinUpcoming(event,Date.parse('2026-09-16')).length"),0);
 a.run("spinDash.hk.data={events:[event]};spinDash.hk.status='paused'");
 assert.equal(a.run('spinVisible(spinDash.hk,{}).length'),1);
});
test('identity gaps and business names remain clear without source excerpts',()=>{
 const a=app();a.context.event={...event,targetName:'',identityState:'unconfirmed_event'};
 assert.match(a.run('spinCard(event)'),/尚未确认关联分拆/);
 a.context.event={...event,targetName:'光伏業務',identityKind:'business',identityEvidence:{date:'2026-01-01',url:'https://www1.hkexnews.hk/filing.pdf',quote:'<script>分立光伏業務</script>'}};
 const html=a.run('spinCard(event)');
 assert.match(html,/业务 \/ 项目/);assert.ok(!/名称来源|查看名称原文/.test(html));
 assert.ok(!html.includes('<script>'));assert.ok(!html.includes('&lt;script&gt;分立'));
});
test('unconfirmed leads remain accessible separately from identified events',()=>{
 const a=app();a.context.event=event;
 a.run("spinDash.us.data={events:[event,{...event,id:'lead',targetName:'',identityState:'unconfirmed_event'}]};spinDash.us.view='confirmed'");
 assert.equal(a.run('spinVisible(spinDash.us,{}).length'),1);
 a.run("spinDash.us.view='unconfirmed'");assert.equal(a.run('spinVisible(spinDash.us,{})[0].id'),'lead');
 a.run("spinDash.us.view='all'");assert.equal(a.run('spinVisible(spinDash.us,{}).length'),2);
});
test('merged dossier names retain old watchlists and notes once',()=>{
 const a=app();a.context.event={...event,mergedIds:['old']};
 a.run("spinSave('old',{watch:true,note:'原笔记'});spinSave(event.id,{note:'新笔记'});spinDash.us.data={events:[event]}");
 assert.equal(a.run('spinPrefs()[event.id].watch'),true);
 assert.equal(a.run('spinPrefs()[event.id].note'),'新笔记\n\n原笔记');
 assert.equal(a.run('spinPrefs()[event.id].note'),'新笔记\n\n原笔记');
 a.run("spinSave(event.id,{note:'修改后的笔记'})");
 assert.equal(a.run('spinPrefs()[event.id].note'),'修改后的笔记');
});

test('introduction listing filter works with search, status and both type formats',()=>{
 const a=app();a.context.event=event;
 a.run(`spinDash.hk.data={events:[
   {...event,id:'intro1',parentName:'中国旅游',status:'announced',type:{code:'intro_hk'}},
   {...event,id:'intro2',parentName:'岚图汽车',status:'completed',type:'intro_hk'},
   {...event,id:'ipo',type:{code:'ipo_hk'}},
   {...event,id:'distribution',type:'distribution'},
   {...event,id:'reit',type:{code:'reit',is_reit:true}}
 ]};spinDash.hk.type='intro'`);
 assert.equal(a.run('spinBaseEvents(spinDash.hk).length'),2);
 assert.equal(a.run('spinVisible(spinDash.hk,{}).length'),2);
 a.run("spinDash.hk.status='completed'");assert.equal(a.run('spinVisible(spinDash.hk,{}).length'),1);
 a.run("spinDash.hk.status='all';spinDash.hk.query='中国旅游'");
 assert.equal(a.run('spinBaseEvents(spinDash.hk).length'),1);
 assert.equal(a.run('spinVisible(spinDash.hk,{})[0].id'),'intro1');
});
test('selecting watchlist clears conflicting filters and prior update highlights',()=>{
 const a=app();a.context.events=[event,{...event,id:'new',targetName:'',identityState:'missing_name'}];
 a.run('spinDash.us.data={events};spinSave(events[0].id,{watch:true});Object.assign(spinDash.us,{query:"wrong",type:"reit",status:"terminated",linkedEvent:"old"});spinSelectView(spinDash.us,"watch")');
 assert.equal(a.run('spinVisible(spinDash.us,spinPrefs()).length'),1);
 assert.equal(a.run('spinDash.us.query'),'');assert.equal(a.run('spinDash.us.linkedEvent'),null);
 a.run('spinSelectView(spinDash.us,"confirmed")');assert.equal(a.run('spinVisible(spinDash.us,{}).length'),1);
 a.run('spinSelectView(spinDash.us,"unconfirmed")');assert.equal(a.run('spinVisible(spinDash.us,{}).length'),1);
});
test('joint filings link the same verified fund across issuers without joining unrelated projects',()=>{
 const a=app();a.context.events=[{...event,identityKind:'instrument',announcements:[{title:'聯合公告',date:'2026-09-27'}]},{...event,id:'us:Q:one',parentName:'Second issuer',parentTicker:'Q',announcements:[{title:'聯合公告',date:'2026-09-27'}]},{...event,id:'us:Z:one',parentTicker:'Z',announcements:[{title:'Different filing',date:'2026-09-27'}]}];
 assert.equal(a.run('spinJointRecords({events},events[0]).length'),1);
 const html=a.run('spinCard(events[0],{},spinJointRecords({events},events[0]))');assert.match(html,/同一项目/);assert.match(html,/data-open-event="us:Q:one"/);
 a.context.events[0].targetName='';assert.equal(a.run('spinJointRecords({events},events[0]).length'),0);
});
test('a repaired HK followup is one row in all, recent and watched views and preserves both notes',()=>{
 const a=app();const repaired={...event,id:'hk:00308:unresolved',mergedIds:['hk:00308:duplicate'],market:'hk',parentTicker:'00308.HK',parentName:'香港中旅',targetName:'中旅港澳文旅控股有限公司',type:{code:'intro_hk'},latestDate:'2026-10-26',recordUpdatedAt:'2026-10-28T00:00:00Z',status:'record_set',dates:{recordDate:{date:'2026-11-20',url:'https://example.org/new.pdf'}},announcements:[{date:'2026-10-26',url:'https://example.org/new.pdf',title:'新公告',direct:true},{date:'2026-05-20',url:'https://example.org/old.pdf',title:'原公告',direct:true}]};
 a.context.repaired=repaired;
 a.run("spinSave(repaired.id,{watch:true,note:'原档案笔记'});spinSave(repaired.mergedIds[0],{watch:true,note:'新公告笔记'});spinDash.hk.data={events:[repaired]};spinAutoWatchIntroductions(spinDash.hk.data)");
 for(const view of ['all','changes','watch']){
  a.context.view=view;
  assert.equal(a.run("spinDash.hk.view=view;spinVisible(spinDash.hk,spinPrefs(),Date.parse(repaired.recordUpdatedAt)+1000).length"),1);
 }
 assert.equal(a.run('spinPrefs()[repaired.id].note'),'原档案笔记\n\n新公告笔记');
 assert.equal(a.run('spinPrefs()[repaired.id].note'),'原档案笔记\n\n新公告笔记');
 const html=a.run('spinCard(repaired)');assert.ok(html.includes('2026-10-26'));assert.ok(html.includes('2026-11-20'));
});
test('source archive retains every old document, orders publication dates and marks only confirmed latest files',()=>{
 const a=app();a.context.dossier={...event,announcements:[
  {url:'https://example.org/old.pdf',date:'2026-05-20',title:'旧公告',direct:true},
  {url:'https://example.org/sibling.pdf',date:'2026-10-28',title:'其他项目公告',direct:true,relevance:'unverified'},
  {url:'https://example.org/current.pdf',date:'2026-10-26',title:'最新公告',direct:true},
  {url:'https://example.org/material.pdf',date:'2026-09-01',title:'历史材料',direct:true},
  {url:'https://example.org/companion.pdf',date:'2026-10-26',title:'同日材料',direct:true}
 ]};
 let html=a.run('spinCard(dossier)');const section=html.slice(html.indexOf('sd-announcements'),html.indexOf('sd-announcements')+5000);
 assert.match(section,/公告与历史材料/);
 assert.ok(section.indexOf('current.pdf')<section.indexOf('material.pdf'));
 assert.ok(section.indexOf('material.pdf')<section.indexOf('old.pdf'));
 const latestLinks=[...section.matchAll(/class="sd-file-latest">最新<\/span><a href="([^"]+)"/g)].map(m=>m[1]);
 assert.deepEqual(latestLinks,['https://example.org/current.pdf','https://example.org/companion.pdf']);
 assert.ok(section.includes('sibling.pdf'));
 assert.equal(a.run('dossier.announcements[0].date'),'2026-05-20');
 a.run("lang='en'");html=a.run('spinCard(dossier)');assert.match(html,/Filings & source archive/);assert.match(html,/class="sd-file-latest">Latest/);
});

test('publication dates outrank corrections and a genuinely newer filing can overtake China Travel',()=>{
 const a=app();a.context.payload={events:[
  {...event,id:'hk:00308',parentTicker:'00308.HK',latestDate:'2026-10-26',recordUpdatedAt:'2026-10-28T00:00:00Z',announcements:[{date:'2026-10-26',direct:true,url:'https://www1.hkexnews.hk/new.pdf',relevance:'candidate'}]},
  {...event,id:'hk:00842',parentTicker:'00842.HK',latestDate:'2026-04-01',recordUpdatedAt:'2026-10-29T00:00:00Z'}]};
 a.run('spinDash.hk.data=payload;spinDash.hk.view="all"');
 assert.equal(a.run('spinVisible(spinDash.hk,{})[0].parentTicker'),'00308.HK');
 a.run('payload.events[1].recordUpdatedAt="2099-01-01T00:00:00Z"');
 assert.equal(a.run('spinVisible(spinDash.hk,{})[0].parentTicker'),'00308.HK');
 a.run('payload.events.push({...payload.events[1],id:"future",parentTicker:"NEW",latestDate:"2026-10-30",announcements:[]})');
 assert.equal(a.run('spinVisible(spinDash.hk,{})[0].parentTicker'),'NEW');
 a.context.e={latestDate:'2099-01-01',announcements:[{date:'2026-10-26',direct:true,url:'https://www1.hkexnews.hk/a.pdf',relevance:'candidate'},{date:'2099-01-01',direct:true,url:'https://www1.hkexnews.hk/b.pdf',relevance:'unverified'}]};
 assert.equal(a.run('spinAnnouncementDate(e)'),'2026-10-26');
});
