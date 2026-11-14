const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const asset=(id,kind,rev='a')=>({file:`browser/${id}-${kind}-${rev.repeat(24)}.json`});
const overview=id=>({version:1,investor:id,data:{current:{quarter:'2026 Q2',holdings:[],totalValue:0},browserProjection:{version:1,sources:{}}},prices:{quotes:{}},insights:{schemaVersion:2,entries:{}},history:asset(id,'history')});
function loader(fetch,platform={}){const c=vm.createContext({fetch,Date,AbortController,setTimeout,clearTimeout,...platform});vm.runInContext(fs.readFileSync('investor_loader.js','utf8'),c);return c.InvestorSnapshots;}
const response=value=>({ok:true,status:200,json:async()=>value});
test('a second visit reuses the snapshot and never requests history until asked',async()=>{const calls=[],payload=overview('test'),manifest={version:1,investors:{test:{snapshot:asset('test','current'),history:payload.history}}};const l=loader(async url=>{calls.push(url);return response(url.startsWith('browser/manifest')?manifest:url.includes('-current-')?payload:{version:1,investor:'test',history:{holdings:{}},exitPerf:{}})});await l.load('test');await l.load('test');assert.equal(calls.length,2);assert.ok(!calls.some(p=>p.includes('-history-')));await l.history(payload.history);await l.history(payload.history);assert.equal(calls.filter(p=>p.includes('-history-')).length,1);});
test('a file retired by a new deployment refreshes its manifest once',async()=>{let revision='a',manifests=0;const l=loader(async url=>{if(url.startsWith('browser/manifest')){manifests++;return response({version:1,investors:{test:{snapshot:asset('test','current',revision),history:asset('test','history')}}});}if(url.includes('-current-'+ 'a'.repeat(24))){revision='b';return {ok:false,status:404}}return response(overview('test'));});assert.equal((await l.load('test')).investor,'test');assert.equal(manifests,2);});
test('snapshot identities and insight proofs cannot cross investors',async()=>{let body=overview('other');const l=loader(async url=>response(url.startsWith('browser/manifest')?{version:1,investors:{test:{snapshot:asset('test','current'),history:asset('test','history')}}}:body));await assert.rejects(l.load('test'),/Invalid investor/);body=overview('test');body.data.browserProjection.sources={holdings:'f'.repeat(64)};await assert.rejects(l.load('test'),/source mismatch/);});
test('fresh requests bypass the in-memory snapshot cache',async()=>{let requests=0;const l=loader(async(url,options)=>{if(url.startsWith('browser/manifest'))return response({version:1,investors:{test:{snapshot:asset('test','current'),history:asset('test','history')}}});requests++;if(requests>1)assert.equal(options.cache,'no-store');return response(overview('test'));});await l.load('test');await l.load('test',{fresh:true});assert.equal(requests,2);});

test('compressed current and history assets decode to the original data and reject unsafe compressed paths',async()=>{const {gzipSync}=require('node:zlib'),payload=overview('test'),snapshot=asset('test','current');snapshot.gzipFile=snapshot.file+'.gz';payload.history.gzipFile=payload.history.file+'.gz';const calls=[],manifest={version:1,investors:{test:{snapshot,history:payload.history}}},historical={version:1,investor:'test',history:{holdings:{}},exitPerf:{}};const fetch=async url=>{calls.push(url);if(url.startsWith('browser/manifest'))return response(manifest);const value=url.includes('-current-')?payload:historical;return url.endsWith('.gz')?new Response(gzipSync(JSON.stringify(value))):new Response(JSON.stringify(value));};const l=loader(fetch,{DecompressionStream,Response});assert.equal((await l.load('test')).investor,'test');assert.equal((await l.history(payload.history)).investor,'test');assert.equal(calls.filter(p=>p.endsWith('.json.gz')).length,2);snapshot.gzipFile='https://example.org/unsafe.gz';const fallback=loader(fetch,{DecompressionStream,Response});await fallback.load('test');assert.equal(calls.at(-1),snapshot.file);});

test('switching across the whole investor list reuses bounded current snapshots',async()=>{
  const ids=Array.from({length:17},(_,i)=>'fund'+i),calls=[];
  const manifest={version:1,investors:Object.fromEntries(ids.map(id=>[id,{snapshot:{...asset(id,'current'),bytes:250000},history:asset(id,'history')}]))};
  const l=loader(async url=>{calls.push(url);return response(url.startsWith('browser/manifest')?manifest:overview(/browser\/(fund\d+)-/.exec(url)[1]));});
  for(const id of [...ids,...ids])await l.load(id);
  assert.equal(calls.filter(url=>url.includes('-current-')).length,17);
});
test('current snapshot memory budget evicts oldest entries instead of growing without bound',async()=>{
  const ids=['one','two','three'],calls=[];
  const manifest={version:1,investors:Object.fromEntries(ids.map(id=>[id,{snapshot:{...asset(id,'current'),bytes:4*1024*1024},history:asset(id,'history')}]))};
  const l=loader(async url=>{calls.push(url);return response(url.startsWith('browser/manifest')?manifest:overview(/browser\/([a-z]+)-/.exec(url)[1]));});
  for(const id of [...ids,'two','one'])await l.load(id);
  assert.equal(calls.filter(url=>url.includes('-current-')).length,4);
});
test('returning to a previously viewed history does not decode it again',async()=>{
  const calls=[],l=loader(async url=>{calls.push(url);return response({version:1,investor:/browser\/([a-z]+)-/.exec(url)[1],history:{holdings:{}},exitPerf:{}});});
  for(const id of ['one','two','three','one'])await l.history({...asset(id,'history'),bytes:1000000});
  assert.equal(calls.length,3);
});
