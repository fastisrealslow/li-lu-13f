const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=f=>JSON.parse(fs.readFileSync(path.join(root,f)));
async function reader(unsafe,workId){
  const catalog=read('archive/catalog.json'),index=read('archive/explanations/index.json');
  const work=catalog.works.find(w=>workId?w.id===workId:w.investor==='lilu'&&index.entries[w.id]?.reviewStatus==='verified');
  const entry=index.entries[work.id],note=read(entry.file);
  if(unsafe){work.sources.find(s=>s.url===note.sourceURL).url=unsafe;note.sourceURL=unsafe;}
  const nodes=new Map(),element=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',options:[],setAttribute(){},querySelector(){return {textContent:''};},events:{},addEventListener(k,f){this.events[k]=f;}});return nodes.get(id);};
  let url='https://example.test/archive.html?investor='+work.investor+'&work='+work.id;
  const context={URL,URLSearchParams,console,window:{},location:{get href(){return url;},get search(){return new URL(url).search;}},history:{replaceState(_,__,value){url=String(value);}},document:{getElementById:element,documentElement:{}},fetch:async input=>({ok:true,json:async()=>{
    const file=input.split('?')[0];return file==='archive/catalog.json'?catalog:file==='investors.json'?read(file):file==='archive/guides.json'?read(file):file==='archive/explanations/index.json'?index:file===entry.file?note:read(file);
  }})};
  vm.runInNewContext(fs.readFileSync(path.join(root,'archive.js'),'utf8'),context);
  for(let i=0;i<10&&!element('archiveReader').innerHTML.includes('<h1>');i++)await new Promise(setImmediate);
  assert.match(element('archiveReader').innerHTML,/<h1>/);
  return {element,url:()=>url};
}
test('approved reading guides reject script, credential and unsupported source links',async()=>{
  for(const url of ['javascript:alert(1)','https://user:pass@example.test/','data:text/html,<script>alert(1)</script>','https://example.test/\nscript']){
    const a=await reader(url);assert.doesNotMatch(a.element('archiveReader').innerHTML,/<a href=/);
    assert.match(a.element('archiveReader').innerHTML,/archive-text-unavailable/);
  }
  const ok=await reader();assert.match(ok.element('archiveReader').innerHTML,/<a href="https:\/\//);
  const legacy=await reader('http://example.test/original');assert.match(legacy.element('archiveReader').innerHTML,/<a href="http:\/\/example.test\/original"/);
});
test('returning to the collection removes the old work from the bookmark URL',async()=>{
  const a=await reader();assert.ok(new URL(a.url()).searchParams.has('work'));
  a.element('archiveWork').events.change({target:{value:''}});
  assert.equal(new URL(a.url()).searchParams.has('work'),false);assert.equal(new URL(a.url()).searchParams.get('investor'),'lilu');
});
test('the stricter link checks retain every approved reading guide',async()=>{
  for(const [id,entry] of Object.entries(read('archive/explanations/index.json').entries)){
    if(entry.reviewStatus!=='verified')continue;
    const a=await reader(undefined,id);assert.doesNotMatch(a.element('archiveReader').innerHTML,/archive-text-unavailable/,id);
    assert.match(a.element('archiveReader').innerHTML,/<a href="https:\/\//,id);
  }
});
