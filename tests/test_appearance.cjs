const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const KEY='13f-site-appearance';
function app(saved,blocked=false){
  const store=new Map(saved===undefined?[]:[[KEY,saved]]),writes=[],attributes={},events={},windowEvents={},messages=[];
  const label={textContent:''};
  const button={setAttribute:(k,v)=>attributes[k]=v,querySelector:()=>label};
  const root={setAttribute:(k,v)=>attributes[k]=v};
  const frame={contentWindow:{postMessage:(data,origin)=>messages.push({data,origin})}};
  const win={location:{origin:'https://example.test'},localStorage:{getItem:k=>{if(blocked)throw Error('blocked');return store.get(k)??null;},setItem:(k,v)=>{if(blocked)throw Error('blocked');store.set(k,v);writes.push([k,v]);}},addEventListener:(k,f)=>windowEvents[k]=f};win.parent=win;
  const doc={documentElement:root,querySelectorAll:s=>s==='iframe'?[frame]:[button],addEventListener:(k,f)=>events[k]=f};
  vm.runInNewContext(fs.readFileSync(path.join(__dirname,'../appearance.js'),'utf8'),{window:win,document:doc});
  return {win,doc,store,writes,attributes,label,events,windowEvents,messages,button};
}
test('new visitors keep the current appearance without writing a preference',()=>{
  const a=app();assert.equal(a.win.SiteAppearance.current(),'current');assert.equal(a.attributes['data-appearance'],'current');
  assert.equal(a.attributes['aria-checked'],'false');assert.equal(a.writes.length,0);
});
test('a saved almanac choice is restored before the DOM is ready and survives switching back',()=>{
  const a=app('almanac');assert.equal(a.attributes['data-appearance'],'almanac');assert.equal(a.attributes['aria-checked'],'true');
  a.events.click({target:{closest:s=>s==='[data-appearance-toggle]'?a.button:null}});
  assert.equal(a.store.get(KEY),'current');assert.equal(a.attributes['aria-checked'],'false');
  assert.equal(app(a.store.get(KEY)).attributes['data-appearance'],'current');
});
test('unknown stored choices and blocked storage cannot disable the appearance control',()=>{
  assert.equal(app('unrecognized').attributes['data-appearance'],'current');
  const a=app(undefined,true);assert.doesNotThrow(()=>a.win.SiteAppearance.set('almanac'));
  assert.equal(a.attributes['data-appearance'],'almanac');assert.equal(a.attributes['aria-checked'],'true');
});
test('changes in another tab or clearing storage update this tab without another write',()=>{
  const a=app();a.store.set(KEY,'almanac');a.windowEvents.storage({key:KEY});assert.equal(a.attributes['data-appearance'],'almanac');
  a.store.clear();a.windowEvents.storage({key:null});assert.equal(a.attributes['data-appearance'],'current');assert.equal(a.writes.length,0);
});
test('game frames inherit the choice and cannot be controlled by unrelated windows',()=>{
  const a=app();a.win.SiteAppearance.set('almanac');assert.equal(a.messages.at(-1).data.theme,'almanac');
  assert.equal(a.messages.at(-1).origin,'https://example.test');
  const parent={};a.win.parent=parent;
  for(const [source,origin] of [[{},'https://example.test'],[parent,'https://outside.test']])
    a.windowEvents.message({source,origin,data:{type:'13f:appearance',theme:'current'}});
  assert.equal(a.win.SiteAppearance.current(),'almanac');
  a.windowEvents.message({source:parent,origin:'https://example.test',data:{type:'13f:appearance',theme:'current'}});
  assert.equal(a.win.SiteAppearance.current(),'current');
});
test('a language switch changes control labels without touching investment or game storage',()=>{
  const a=app();a.store.set('lang','en');a.events.click({target:{closest:s=>s==='#langBtn'?{}:null}});
  assert.equal(a.label.textContent,'Book');a.win.SiteAppearance.set('almanac');
  assert.ok(a.writes.every(([key])=>key===KEY));assert.equal(a.store.get('lang'),'en');
});
