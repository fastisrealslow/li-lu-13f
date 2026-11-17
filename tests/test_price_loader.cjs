const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
const {createHash,webcrypto}=require('node:crypto');
const hash=b=>createHash('sha256').update(b).digest('hex');
function setup(chunks,override){
 const bodies=new Map();
 const files=chunks.map(x=>{const b=Buffer.from(JSON.stringify(x)),sha256=hash(b),file=`price_shards/prices_test-${sha256}.json`;bodies.set(file,b);return {file,sha256,bytes:b.length};});
 const input={quotes:{TEST:{c:12}},_priceShards:{version:1,field:'tradePrices',sha256:'a'.repeat(64),files}};
 const calls=[];const context={crypto:webcrypto,TextDecoder,TextEncoder,Uint8Array,fetch:async(file,options)=>{calls.push([file,options]);const b=bodies.get(file);return override?override(file,b):new Response(b);}};
 vm.runInNewContext(fs.readFileSync('price_loader.js','utf8'),context);
 return {input,calls,resolve:context.PriceShards.resolve};
}
test('unsharded prices pass through unchanged',async()=>{const s=setup([]),v={quotes:{}};assert.equal(await s.resolve(v),v);});
test('all ledger fields and historical entries reconstruct without mutating input',async()=>{
 const s=setup([{version:1,entries:{old:{price:1.25}}},{entries:{new:{price:8}},quoteRefresh:{OLD:{date:'2001-01-01'}}},{quoteRefresh:{NEW:{date:'2026-01-01'}}}]);
 const before=JSON.stringify(s.input);const x=await s.resolve(s.input,{fresh:true});
 assert.deepEqual(JSON.parse(JSON.stringify(x)),{quotes:{TEST:{c:12}},tradePrices:{version:1,entries:{old:{price:1.25},new:{price:8}},quoteRefresh:{OLD:{date:'2001-01-01'},NEW:{date:'2026-01-01'}}}});
 assert.equal(JSON.stringify(s.input),before);assert.ok(s.calls.every(c=>c[1].cache==='no-store'));
});
test('missing, corrupted and truncated shards fail closed',async()=>{
 for(const mode of ['missing','corrupt','short']){
  const s=setup([{version:1},{entries:{old:1}}],(file,b)=>file.includes('never')?new Response(b):mode==='missing'?new Response('',{status:404}):new Response(mode==='short'?b.subarray(1):Buffer.alloc(b.length,32)));
  const before=JSON.stringify(s.input);await assert.rejects(s.resolve(s.input),/HTTP|size mismatch|digest mismatch/);assert.equal(JSON.stringify(s.input),before);
 }
});
test('duplicate entries, scalar fields and unsafe paths cannot overwrite history',async()=>{
 for(const chunks of [[{entries:{old:1}},{entries:{old:2}}],[{version:1},{version:2}],[{entries:{}},{entries:1}]])await assert.rejects(setup(chunks).resolve(setup(chunks).input),/Duplicate|Conflicting/);
 const s=setup([{version:1}]);s.input._priceShards.files[0].file='../private.json';await assert.rejects(s.resolve(s.input),/descriptor/);assert.equal(s.calls.length,0);
});
test('aborted loads never return partial prices',async()=>{const s=setup([{version:1}]);await assert.rejects(s.resolve(s.input,{signal:{aborted:true}}),/aborted/);assert.equal(s.calls.length,0);});
test('shard script is loaded before app and investor JSON resolves the marker',()=>{
 const html=fs.readFileSync('index.html','utf8'),app=fs.readFileSync('app.js','utf8');assert.ok(html.indexOf('price_loader.js')<html.indexOf('app.js?v='));assert.match(app,/PriceShards\.resolve\(value,\{signal,fresh\}\)/);
});

test('a bound shard sequence rejects omissions, reordering and extra shards before fetching',async()=>{
 for(const mode of ['omit','reorder','extra']){
  const s=setup([{version:1},{entries:{old:1}},{entries:{new:2}}]);const m=s.input._priceShards;
  m.sequenceSha256=hash(Buffer.from(m.files.map(p=>p.file+'\t'+p.sha256+'\t'+p.bytes+'\n').join('')));
  if(mode==='omit')m.files.pop();else if(mode==='reorder')m.files.reverse();else m.files.push({...m.files[0]});
  await assert.rejects(s.resolve(s.input),/sequence mismatch|descriptor/);assert.equal(s.calls.length,0);
 }
 const s=setup([{version:1},{entries:{old:1}}]);const m=s.input._priceShards;
 m.sequenceSha256=hash(Buffer.from(m.files.map(p=>p.file+'\t'+p.sha256+'\t'+p.bytes+'\n').join('')));
 assert.equal((await s.resolve(s.input)).tradePrices.entries.old,1);
});

test('Python-written manifests reconstruct the same complete ledger in JavaScript',async()=>{
 const os=require('node:os'),path=require('node:path'),{spawnSync}=require('node:child_process');
 const dir=fs.mkdtempSync(path.join(os.tmpdir(),'price-contract-'));
 try{
  const script="import json,sys; from pathlib import Path; from price_storage import write_prices; v={'quotes':{'T':{'c':1.0}},'tradePrices':{'version':1,'entries':{str(i):{'price':i+0.5,'proof':'原始材料'*40} for i in range(20)},'quoteRefresh':{'T':{'date':'2026-11-17'}}}}; write_prices(Path(sys.argv[1])/'prices.json',v,limit=6000,chunk_size=1000); print(json.dumps(v))";
  const py=spawnSync('python3',['-c',script,dir],{encoding:'utf8'});assert.equal(py.status,0,py.stderr);
  const context={crypto:webcrypto,TextDecoder,TextEncoder,Uint8Array,fetch:async file=>new Response(fs.readFileSync(path.join(dir,file)))};
  vm.runInNewContext(fs.readFileSync('price_loader.js','utf8'),context);
  const actual=await context.PriceShards.resolve(JSON.parse(fs.readFileSync(path.join(dir,'prices.json'))));
  assert.deepEqual(JSON.parse(JSON.stringify(actual)),JSON.parse(py.stdout));
 }finally{fs.rmSync(dir,{recursive:true,force:true});}
});
