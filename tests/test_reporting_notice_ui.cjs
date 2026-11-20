const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function context(){const c=vm.createContext({console,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){}}});vm.runInContext(fs.readFileSync('app.js','utf8'),c);return c;}
const snapshot=()=>({meta:{managerCIK:'0000949509',reportingNotice:{status:'verified',managerCIK:'0000949509',form:'13F-NT',periodEnd:'2026-09-30',quarter:'2026 Q3',otherManagers:[{name:'Manager <img src=x onerror=alert(1)>'}]}},current:{periodEnd:'2026-06-30',quarter:'2026 Q2',holdings:[{ticker:'KEEP',shares:12}]}});
test('notice explains separate reporting and preserves the independent portfolio in both languages',()=>{
 const c=context();c.sample=snapshot();const before=JSON.stringify(c.sample);
 let html=vm.runInContext('reportingNoticeHTML(sample)',c);assert.match(html,/2026 Q3/);assert.match(html,/2026 Q2/);assert.match(html,/最近独立/);assert.ok(!html.includes('<img'));assert.match(html,/&lt;img/);
 html=vm.runInContext("lang='en';reportingNoticeHTML(sample)",c);assert.match(html,/Latest independent holdings/);assert.equal(JSON.stringify(c.sample),before);
});
test('an unverified or retired notice creates no misleading status',()=>{
 const c=context();c.sample=snapshot();c.sample.meta.reportingNotice.status='pending';assert.equal(vm.runInContext('reportingNoticeHTML(sample)',c),'');
 c.sample.meta.reportingNotice.status='verified';c.sample.current.periodEnd='2026-09-30';assert.equal(vm.runInContext('reportingNoticeHTML(sample)',c),'');
});
