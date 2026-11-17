/* Reassemble immutable price ledgers without discarding historical evidence. */
(function(root){
  const own=(o,k)=>Object.prototype.hasOwnProperty.call(o,k);
  const object=x=>x!==null&&typeof x==='object'&&!Array.isArray(x);
  const safeKey=k=>!['__proto__','prototype','constructor'].includes(k);
  async function resolve(value,{signal,fresh=false}={}){
    if(!object(value)||!own(value,'_priceShards'))return value;
    const manifest=value._priceShards;
    if(!object(manifest)||manifest.version!==1||manifest.field!=='tradePrices'||own(value,'tradePrices')||!/^[a-f0-9]{64}$/.test(manifest.sha256||'')||!Array.isArray(manifest.files)||!manifest.files.length||manifest.files.length>256)throw Error('Invalid price shard manifest');
    if(!root.crypto?.subtle)throw Error('Price shard integrity verification unavailable');
    const paths=new Set(),ledger=Object.create(null);
    for(const part of manifest.files){
      if(!object(part)||!/^price_shards\/[a-zA-Z0-9_-]+-[a-f0-9]{64}\.json$/.test(part.file||'')||!/^[a-f0-9]{64}$/.test(part.sha256||'')||!part.file.endsWith('-'+part.sha256+'.json')||!Number.isSafeInteger(part.bytes)||part.bytes<=0||part.bytes>25*1024*1024||paths.has(part.file))throw Error('Invalid price shard descriptor');
      paths.add(part.file);
    }
    if(own(manifest,'sequenceSha256')){
      const sequence=manifest.files.map(p=>p.file+'\t'+p.sha256+'\t'+p.bytes+'\n').join('');
      const digest=Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256',new TextEncoder().encode(sequence))),x=>x.toString(16).padStart(2,'0')).join('');
      if(digest!==manifest.sequenceSha256)throw Error('Price shard sequence mismatch');
    }
    // Do not expose partial data if a later shard is missing, corrupt or aborted.
    async function fetchPart(part){
      if(signal?.aborted)throw Error('Price loading aborted');
      const response=await fetch(part.file,{signal,cache:fresh?'no-store':'default'});
      if(!response.ok)throw Error('Price shard HTTP '+response.status);
      const bytes=await response.arrayBuffer();
      if(bytes.byteLength!==part.bytes)throw Error('Price shard size mismatch');
      const digest=Array.from(new Uint8Array(await root.crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
      if(digest!==part.sha256)throw Error('Price shard digest mismatch');
      const data=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(bytes));
      if(!object(data))throw Error('Invalid price shard contents');
      return data;
    }
    for(let index=0;index<manifest.files.length;index+=4){
      const batch=await Promise.all(manifest.files.slice(index,index+4).map(fetchPart));
      for(const data of batch)for(const [key,item] of Object.entries(data)){
        if(!safeKey(key))throw Error('Unsafe price shard key');
        if(object(item)){
          if(own(ledger,key)&&!object(ledger[key]))throw Error('Conflicting price shard field');
          if(!own(ledger,key))ledger[key]=Object.create(null);
          for(const [entry,record] of Object.entries(item)){
            if(!safeKey(entry)||own(ledger[key],entry))throw Error('Duplicate or unsafe price shard entry');
            ledger[key][entry]=record;
          }
        }else{
          if(own(ledger,key))throw Error('Duplicate price shard field');
          ledger[key]=item;
        }
      }
    }
    if(signal?.aborted)throw Error('Price loading aborted');
    const result={...value,tradePrices:ledger};delete result._priceShards;
    return result;
  }
  root.PriceShards={resolve};
})(globalThis);
