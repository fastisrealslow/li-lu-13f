const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..'),read=f=>JSON.parse(fs.readFileSync(path.join(root,f)));
async function reader(unsafe,workId,textDocument){
  const catalog=read('archive/catalog.json'),index=read('archive/explanations/index.json');
  const work=catalog.works.find(w=>workId?w.id===workId:w.investor==='lilu'&&index.entries[w.id]?.reviewStatus==='verified');
  const entry=index.entries[work.id],note=read(entry.file);
  if(unsafe){work.sources.find(s=>s.url===note.sourceURL).url=unsafe;note.sourceURL=unsafe;}
  if(!textDocument){delete work.fullTextFile;delete work.fullTextStatus;}
  if(textDocument){textDocument.workId=work.id;work.fullTextStatus='ready';work.fullTextFile='archive/texts/'+work.id+'.json';}
  const nodes=new Map(),element=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:'',options:[],setAttribute(){},querySelector(){return {textContent:''};},events:{},addEventListener(k,f){this.events[k]=f;}});return nodes.get(id);};
  let url='https://example.test/archive.html?investor='+work.investor+'&work='+work.id;
  const context={URL,URLSearchParams,console,crypto:require('node:crypto').webcrypto,TextEncoder,window:{},location:{get href(){return url;},get search(){return new URL(url).search;}},history:{replaceState(_,__,value){url=String(value);}},document:{getElementById:element,documentElement:{}},fetch:async input=>({ok:true,json:async()=>{
    const file=input.split('?')[0];return file==='archive/catalog.json'?catalog:file==='investors.json'?read(file):file==='archive/guides.json'?read(file):file==='archive/explanations/index.json'?index:file===entry.file?note:file===work.fullTextFile?textDocument:read(file);
  }})};
  vm.runInNewContext(fs.readFileSync(path.join(root,'archive.js'),'utf8'),context);
  for(let i=0;i<200&&!element('archiveReader').innerHTML.includes('<h1>');i++)await new Promise(r=>setTimeout(r,10));
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

test('complete originals open first, preserve anchors, escape text and label provenance',async()=>{
  const original='Original <script>text</script>.\n';
  const doc={kind:'verbatim_text',reviewStatus:'verified',originalLanguage:'en',originalText:original,
    sourceDigest:require('node:crypto').createHash('sha256').update(original).digest('hex'),
    sourceURL:'https://example.test/original',rights:{verified:true,allowPublication:true,allowTranslation:true,evidence:'用户于 2026-10-29 确认全文和翻译发布授权'},
    segments:[{id:'p1',page:3,original,en:original,zh:'译文。'}]};
  const a=await reader(undefined,undefined,doc);
  const html=a.element('archiveReader').innerHTML;
  assert.match(html,/非官方译文/);assert.match(html,/原件第 3/);assert.match(html,/译文。/);
  assert.match(html,/data-view="original" aria-pressed="true"/);assert.doesNotMatch(html,/<script>/);
  assert.match(html,/用户于 2026-10-29/);assert.match(html,/https:\/\/example.test\/original/);
});
test('Chinese originals need no invented English translation',async()=>{
  const original='中文原文。';
  const doc={kind:'verbatim_text',reviewStatus:'verified',originalLanguage:'zh',languages:['zh'],originalText:original,
    sourceDigest:require('node:crypto').createHash('sha256').update(original).digest('hex'),
    rights:{verified:true,allowPublication:true,allowTranslation:true,evidence:'User confirmation'},segments:[{id:'p1',original,zh:original}]};
  const a=await reader(undefined,undefined,doc);const html=a.element('archiveReader').innerHTML;
  assert.match(html,/中文原文。/);assert.doesNotMatch(html,/data-mode="en"|data-mode="bilingual"|data-download="en"/);
});

test('translation tables and lists preserve rows, columns and safe text',async()=>{
 const original='Table source.';
 const doc={kind:'verbatim_text',reviewStatus:'verified',originalLanguage:'en',originalText:original,
 sourceDigest:require('node:crypto').createHash('sha256').update(original).digest('hex'),rights:{verified:true,allowPublication:true,allowTranslation:true,evidence:'User confirmation'},
 segments:[{id:'table',original,en:original,zh:'2024\t2023\n47,437\t37,350',zhBlocks:[{type:'table',headers:['2024','2023'],rows:[['47,437','37,350']]},{type:'list',items:['<script>unsafe</script>','Second item']}]}]};
 const a=await reader(undefined,undefined,doc);const html=a.element('archiveReader').innerHTML;
 assert.match(html,/<th scope="col">2024<\/th><th scope="col">2023/);assert.match(html,/<td>47,437<\/td><td>37,350/);assert.match(html,/<li>&lt;script&gt;/);assert.doesNotMatch(html,/<script>/);
});
