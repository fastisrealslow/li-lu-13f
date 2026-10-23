const test=require('node:test');
const assert=require('node:assert/strict');
const vm=require('node:vm');
const fs=require('node:fs');
const path=require('node:path');

test('archive counts cannot overwrite a later investor switch',async()=>{
  let resolve;
  const count={textContent:''},host={innerHTML:'',querySelector:()=>count};
  const context={window:{},document:{getElementById:()=>host},fetch:url=>url==='archive/catalog.json'?new Promise(r=>{resolve=r;}):Promise.resolve({ok:true,json:async()=>url==='archive/guides.json'?{guides:{}}:{entries:{y:{}}}})};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../archive_entry.js'),'utf8'),context);
  const first=context.window.SpeechArchive.updateInvestor({id:'lilu',name:'李录',nameEn:'Li Lu'},false);
  const second=context.window.SpeechArchive.updateInvestor({id:'pabrai',name:'帕伯莱',nameEn:'Pabrai'},false);
  resolve({ok:true,json:async()=>({updatedAt:'2026-10-13',works:[{investor:'lilu',noteFile:'x'},{investor:'lilu'},{investor:'pabrai',fullTextFile:'archive/texts/y.json',fullTextStatus:'ready'}]})});
  await Promise.all([first,second]);
  assert.match(host.innerHTML,/investor=pabrai/);
  assert.match(count.textContent,/已建档 1 篇 · 已有导读 0 篇/);
});

test('archive preview escapes profile content and remains useful on fetch failure',async()=>{
  const count={textContent:''},host={innerHTML:'',querySelector:()=>count};
  const context={window:{},document:{getElementById:()=>host},fetch:async()=>({ok:false})};
  vm.createContext(context);
  vm.runInContext(fs.readFileSync(path.join(__dirname,'../archive_entry.js'),'utf8'),context);
  await context.window.SpeechArchive.updateInvestor({id:'lilu',name:'<script>unsafe</script>'},false);
  assert.doesNotMatch(host.innerHTML,/<script>/);
  const destination=new URL(host.innerHTML.match(/<a href="([^"]+)"/)[1],'https://example.test/');
  assert.equal(destination.pathname,'/archive.html');
  assert.equal(destination.searchParams.get('investor'),'lilu');
  assert.match(count.textContent,/查看已有资料/);
});

test('an unreviewed generated file cannot inflate the displayed completed-work count',async()=>{
  const count={textContent:''},host={innerHTML:'',querySelector:()=>count};
  const works=['a','b'].map(id=>({id,investor:'lilu',date:'2026',title:{en:id,zh:id}}));
  const payloads={'archive/catalog.json':{works},'archive/guides.json':{guides:{}},'archive/explanations/index.json':{entries:{a:{catalogDate:'2026',catalogTitle:'a',reviewStatus:'verified'},b:{catalogDate:'2026',catalogTitle:'b'}}}};
  const context={window:{},document:{getElementById:()=>host},fetch:async url=>({ok:true,json:async()=>payloads[url.split('?')[0]]})};
  vm.createContext(context);vm.runInContext(fs.readFileSync(path.join(__dirname,'../archive_entry.js'),'utf8'),context);
  await context.window.SpeechArchive.updateInvestor({id:'lilu',name:'李录'},false);
  assert.match(count.textContent,/已建档 2 篇 · 已有导读 1 篇/);
});
