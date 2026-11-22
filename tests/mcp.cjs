const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const modulePromise=import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync('functions/mcp.js')).toString('base64'));
async function send(method,params={},headers={}){const {onRequest}=await modulePromise;return onRequest({request:new Request('https://li-lu-13f.pages.dev/mcp',{method:'POST',headers:{'Content-Type':'application/json',...headers},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})})});}
test('MCP initialize and read-only discovery',async()=>{const r=await(await send('initialize')).json();assert.equal(r.result.protocolVersion,'2025-06-18');const list=await(await send('tools/list')).json();assert.equal(list.result.tools.length,8);assert(list.result.tools.every(t=>t.annotations.readOnlyHint));});
test('unknown origins and methods rejected',async()=>{assert.equal((await send('ping',{}, {Origin:'https://evil.example'})).status,403);const r=await(await send('execute_shell')).json();assert.equal(r.error.code,-32601);});
test('invalid arguments never access upstream',async()=>{const r=await(await send('tools/call',{name:'get_reading_guide',arguments:{work_id:'a',url:'https://evil.example'}})).json();assert.equal(r.result.isError,true);});
test('holdings only return a summary that matches the full current source',async()=>{
 const original=global.fetch;
 const registry=JSON.parse(fs.readFileSync('investors.json'));
 const investor=registry.investors.find(p=>p.id==='lilu');
 const snapshot={
  meta:{aiSummary:'Legacy summary',aiSummaryQuarter:'2026 Q2',aiSummaryUpdatedAt:'legacy'},
  current:{quarter:'2026 Q3',prevQuarter:'2026 Q2',holdings:[{ticker:'PDD',shares:100},{ticker:'TME',shares:20}]},
  history:{holdings:{'2026 Q2':[{ticker:'PDD',shares:75}]}}
 };
 const row=(ticker,shares)=>[ticker,null,shares,...Array(9).fill(null)];
 const entry={
  renderVersion:4,mode:'deterministic',summary:'Current summary',generatedAt:'2026-11-22T00:00:00Z',
  source:{holdings:[row('PDD',100),row('TME',20)],previousHoldings:[row('PDD',75)],
   quarter:'2026 Q3',prevQuarter:'2026 Q2',scope:null,snapshotType:null,valueQuality:null}
 };
 const artifact={entries:{'investor:lilu':entry}};
 try{
  let missing=false;
  global.fetch=async url=>{
   const file=new URL(url).pathname.replace('/li-lu-13f/','');
   if(file===investor.dataFile)return Response.json(snapshot);
   if(file==='ai_supplement.json')return missing ? new Response(null,{status:503}) : Response.json(artifact);
   return Response.json(JSON.parse(fs.readFileSync(file)));
  };
  const holdings=async()=>{
   const r=await(await send('tools/call',{name:'get_holdings',arguments:{investor:'lilu',limit:1}})).json();
   assert(!r.result.isError,JSON.stringify(r));
   return JSON.parse(r.result.content[0].text).data;
  };
  const matching=await holdings();
  assert.equal(matching.meta.aiSummary,entry.summary);
  assert.equal(matching.meta.aiSummaryQuarter,matching.quarter);
  assert.equal(matching.meta.aiSummaryUpdatedAt,entry.generatedAt);
  entry.source.holdings.at(-1)[2]+=1;
  for(const absent of [false,true]){
   missing=absent;
   const d=await holdings();
   assert.equal(d.holdings.items.length,1);
   assert(!Object.keys(d.meta).some(key=>key.startsWith('aiSummary')));
  }
 }finally{global.fetch=original;}
});
test('reads real fixture, paginates holdings and returns quote timestamps',async()=>{const original=global.fetch;try{global.fetch=async url=>{const file=new URL(url).pathname.replace('/li-lu-13f/','');return Response.json(JSON.parse(fs.readFileSync(file)));};const r=await(await send('tools/call',{name:'get_holdings',arguments:{investor:'lilu',limit:2}})).json();assert(!r.result.isError,JSON.stringify(r));const d=JSON.parse(r.result.content[0].text).data;assert.equal(d.holdings.items.length,2);assert(d.quarter);assert(d.quoteUpdated);const hist=await(await send('tools/call',{name:'get_history',arguments:{investor:'lilu',quarter:'2016 Q4',limit:1}})).json();assert(!hist.result.isError);assert.equal(JSON.parse(hist.result.content[0].text).data.holdings.items.length,1);}finally{global.fetch=original;}});
