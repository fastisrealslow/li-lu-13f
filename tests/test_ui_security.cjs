const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm');
const root=path.resolve(__dirname,'..');
function app(){
  const nodes=new Map(),el=id=>{if(!nodes.has(id))nodes.set(id,{innerHTML:'',textContent:''});return nodes.get(id);};
  const ctx=vm.createContext({console:{error(){},log(){}},Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},getElementById:el},window:{}});
  vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'),ctx);
  return {ctx,el,run:s=>vm.runInContext(s,ctx)};
}
test('external ticker and company text remain text in quarterly and summary tables',()=>{
  const a=app();a.ctx.snapshot=JSON.parse(fs.readFileSync(path.join(root,'data.json')));
  a.run('data=snapshot;data.current.holdings[0].cnName=\'<img src=x onerror="alert(1)">\';data.current.holdings[0].ticker=\'<svg onload="alert(1)">\';renderChanges();renderSummary()');
  const html=a.el('changesBody').innerHTML+a.el('summaryCards').innerHTML;
  assert.doesNotMatch(html,/<img|<svg/);assert.match(html,/&lt;img/);assert.match(html,/&lt;svg/);
  assert.match(a.run('fmtTicker("<script>bad</script>")'),/&lt;script&gt;/);
});
test('company names cannot resolve inherited object properties as translations',()=>{
  const a=app();for(const name of ['constructor','__proto__','toString']){a.ctx.name=name;assert.equal(a.run('cn(name)'),name);}
});
test('malformed investor identifiers and paths cannot become inline navigation code or external data requests',async()=>{
  for(const inv of [{id:"x');alert(1)//",dataFile:'data.json',pricesFile:'prices.json'}, {id:'lilu',dataFile:'https://outside.test/data.json',pricesFile:'prices.json'}]){
    const a=app();a.ctx.fetch=async()=>({ok:true,json:async()=>({investors:[inv]})});
    assert.equal(await a.run('loadInvestorConfig()'),false);assert.equal(a.run('INVESTORS.length'),0);
  }
});
