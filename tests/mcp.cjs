const {test}=require('node:test');const assert=require('node:assert/strict');const fs=require('node:fs');
const modulePromise=import('data:text/javascript;base64,'+Buffer.from(fs.readFileSync('functions/mcp.js')).toString('base64'));
async function send(method,params={},headers={}){const {onRequest}=await modulePromise;return onRequest({request:new Request('https://li-lu-13f.pages.dev/mcp',{method:'POST',headers:{'Content-Type':'application/json',...headers},body:JSON.stringify({jsonrpc:'2.0',id:1,method,params})})});}
test('MCP initialize and read-only discovery',async()=>{const r=await(await send('initialize')).json();assert.equal(r.result.protocolVersion,'2025-06-18');const list=await(await send('tools/list')).json();assert.equal(list.result.tools.length,14);assert(list.result.tools.every(t=>t.annotations.readOnlyHint));});
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

test('research tools preserve the published scope, evidence and ranking',async()=>{
 const original=global.fetch;
 const path='browser/lilu-quarterly-changes-'+'a'.repeat(24)+'.json';
 const data={
  'investors.json':{investors:[{id:'lilu',source13F:true,hkFile:'hk_holdings.json'}]},
  'browser/manifest.json':{investors:{lilu:{quarterlyChanges:{file:path}}}},
  [path]:{investor:'lilu',version:1,quarter:'2026 Q3',stats:{added:1,exited:1},
   rows:[{ticker:'TME',category:'added'},{ticker:'PDD',category:'exited'}]},
  'hk_holdings.json':{investor:'lilu',audit:{status:'history_pending'},holdings:[
   {ticker:'01211.HK',name:'BYD',verified_disclosures:[{event_date:'2025-01-01',shares:50}],
    pending_newer_notices:[{date:'2026-09-01'}]}
  ]},
  'spinoff_us.json':{eventsSchemaVersion:1,events:[
   {id:'a',parentName:'Parent A',latestDate:'2025-10-01',recordUpdatedAt:'2026-11-01'},
   {id:'b',parentName:'Parent B',announcements:[{date:'2026-10-01',url:'https://www.sec.gov/test',direct:true}]}
  ]},
  'value_screen.json':{candidates:[{ticker:'ONE'},{ticker:'TWO'}]}
 };
 const invoke=async(name,args)=>{
  const r=await(await send('tools/call',{name,arguments:args})).json();
  assert(!r.result.isError,JSON.stringify(r));
  return JSON.parse(r.result.content[0].text).data;
 };
 try{
  global.fetch=async url=>{
   const file=new URL(url).pathname.replace('/li-lu-13f/','');
   assert(file in data,file);
   return Response.json(data[file]);
  };
  const changes=await invoke('get_quarterly_changes',{investor:'lilu',category:'exited'});
  assert.equal(changes.stats.added,1);
  assert.deepEqual(changes.changes.items,[{ticker:'PDD',category:'exited'}]);
  const hk=await invoke('get_hk_disclosures',{investor:'lilu',query:'1211'});
  assert.equal(hk.verification.status,'history_pending');
  assert.equal(hk.disclosures.items[0].verifiedDisclosures[0].event_date,'2025-01-01');
  assert.equal(hk.disclosures.items[0].pendingNewerNotices.length,1);
  const spin=await invoke('get_spinoff_events',{market:'us',limit:1});
  assert.equal(spin.records.items[0].id,'b');
  assert.equal(spin.records.nextOffset,1);
  const screen=await invoke('get_value_screen',{query:'two'});
  assert.equal(screen.candidates.items[0].rank,2);
 }finally{global.fetch=original;}
});

test('cross-market brief uses HK publication dates and isolates a failed market',async()=>{
 const original=global.fetch;
 const path='browser/lilu-quarterly-changes-'+'a'.repeat(24)+'.json';
 const date=days=>new Date(Date.now()-days*86400000).toISOString().slice(0,10);
 const form={entity:'Li Lu',share_class:'H Shares',position:'long',verification:'hkex_form',
  form_url:'https://di.hkex.com.hk/di/NSForm1.aspx?fn=1',shares:20};
 const fixtures={
  'investors.json':{investors:[{id:'lilu',name:'李录',source13F:true,hkFile:'hk_holdings.json'}]},
  'browser/manifest.json':{investors:{lilu:{quarterlyChanges:{file:path}}}},
  [path]:{investor:'lilu',version:1,quarter:'2026 Q3',rows:[
   {ticker:'PDD',category:'added'},{ticker:'GOOG',category:'hold'}]},
  'hk_holdings.json':{investor:'lilu',audit:{status:'history_pending'},holdings:[
   {ticker:'01211.HK',verified_disclosures:[
    {...form,filing_ref:'historical',event_date:date(320),filing_date:date(319)},
    {...form,filing_ref:'filed-recently',event_date:date(40),filing_date:date(2)},
    {...form,filing_ref:'superseded',event_date:date(1),filing_date:date(1),superseded_by:'filed-recently'},
    {...form,filing_ref:'index-only',event_date:date(1),filing_date:date(1),verification:'hkex_notice_table'}
   ],pending_newer_notices:[{date:date(1)}]}
  ]}
 };
 try{
  global.fetch=async url=>{
   const key=new URL(url).pathname.replace('/li-lu-13f/','');
   return fixtures[key]?Response.json(fixtures[key]):new Response(null,{status:503});
  };
  const brief=async()=>{
   const r=await(await send('tools/call',{name:'get_investor_disclosure_brief',arguments:{investor:'lilu',days:7}})).json();
   assert(!r.result.isError,JSON.stringify(r));
   return JSON.parse(r.result.content[0].text).data;
  };
  const d=await brief();
  assert.equal(d.us13f.quarter,'2026 Q3');
  assert.deepEqual(d.us13f.changes.items.map(r=>r.ticker),['PDD']);
  assert.equal(d.hongKong.recentWindow.total,1);
  assert.equal(d.hongKong.latestBySecurity.items[0].filingRef,'filed-recently');
  assert.equal(d.hongKong.pendingNoticeCount,1);
  delete fixtures['hk_holdings.json'];
  const partial=await brief();
  assert.equal(partial.us13f.status,'published');
  assert.equal(partial.hongKong.status,'source_unavailable');
 }finally{global.fetch=original;}
});

test('watchlist returns only selected securities and dated, source-backed events',async()=>{
 const original=global.fetch;
 const date=days=>new Date(Date.now()-days*86400000).toISOString().slice(0,10);
 const path='browser/duan-quarterly-changes-'+'a'.repeat(24)+'.json';
 const sec='https://www.sec.gov/Archives/edgar/data/100/123/index.htm';
 const hkForm='https://di.hkex.com.hk/di/NSForm1.aspx?fn=1';
 const notice='https://www1.hkexnews.hk/listedco/listconews/sehk/2026/11/spinoff.pdf';
 const currentForm={filing_ref:'new',verification:'hkex_form',event_date:date(19),filing_date:date(1),form_url:hkForm};
 const fixtures={
  'investors.json':{investors:[{id:'duan',name:'段永平',source13F:true,hkFile:'duan_hk.json'}]},
  'browser/manifest.json':{investors:{duan:{quarterlyChanges:{file:path}}}},
  [path]:{investor:'duan',version:1,quarter:'2026 Q3',previousQuarter:'2026 Q2',filingDate:date(3),
   filingSource:sec,comparisonState:'comparable',rows:[
    {ticker:'BRK/B',category:'trimmed',prevShares:100,shares:50,sharesDelta:-50},
    {ticker:'PDD',category:'added',prevShares:0,shares:15,sharesDelta:15}
   ]},
  'duan_hk.json':{investor:'duan',audit:{status:'checked'},holdings:[
   {ticker:'09992.HK',verified_disclosures:[currentForm,{...currentForm},{...currentForm,filing_ref:'old',event_date:date(60),filing_date:date(60)}]}
  ]},
  'spinoff.json':{eventsSchemaVersion:1,events:[
   {id:'verified',parentTicker:'00191.HK',status:'announced',identityVerified:true,
    evidence:{status:'announced',url:notice,date:date(2)},
    announcements:[{direct:true,date:date(2),url:notice},{direct:true,date:date(0),url:notice+'?candidate=1'}]},
   {id:'not-verified',parentTicker:'09992.HK',status:'needs_review',
    announcements:[{direct:true,date:date(0),url:notice}]}
  ]}
 };
 try{
  global.fetch=async url=>{
   const file=new URL(url).pathname.replace('/li-lu-13f/','');
   return fixtures[file]?Response.json(fixtures[file]):new Response(null,{status:503});
  };
  const args={investors:['duan'],tickers:['US.BRK.B','HK.9992','191'],days:10,limit:2};
  const run=async arguments_=>{
   const r=await(await send('tools/call',{name:'get_watchlist_updates',arguments:arguments_})).json();
   assert(!r.result.isError,JSON.stringify(r));
   return JSON.parse(r.result.content[0].text).data;
  };
  const first=await run(args);
  assert.deepEqual(first.watchlist.tickers,['BRK.B','09992.HK','00191.HK']);
  assert.deepEqual(first.updates.items.map(r=>r.kind),['hkex_interests','spinoff']);
  assert.equal(first.updates.total,3);
  assert.equal(first.updates.items[0].eventDate,date(19));
  assert.equal(first.updates.items[0].date,date(1));
  assert.equal(first.coverage.find(r=>r.source==='us_spinoff').status,'source_unavailable');
  const second=await run({...args,offset:first.updates.nextOffset});
  assert.equal(second.updates.items[0].ticker,'BRK/B');
  assert.equal(second.updates.items[0].sourceURL,sec);
  assert.equal(second.updates.items[0].quantityDelta,-50);
  const invalid=await(await send('tools/call',{name:'get_watchlist_updates',arguments:{...args,tickers:['x','x']}})).json();
  assert.equal(invalid.result.isError,true);
 }finally{global.fetch=original;}
});
