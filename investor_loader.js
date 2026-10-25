/* Immutable browser files are generated during deployment from validated data. */
(function(root){
  const snapshots=new Map(),histories=new Map();
  let manifest=null,manifestAt=0,manifestRequest=null,manifestVersion=0;
  const asset=value=>value && /^browser\/[a-z][a-z0-9_]*-(?:current|history)-[a-f0-9]{24}\.json$/.test(value.file||'');
  const remember=(cache,key,value,limit)=>{cache.delete(key);cache.set(key,value);while(cache.size>limit)cache.delete(cache.keys().next().value);return value;};
  async function fetchAsset(entry,options){
    const compressed=typeof DecompressionStream==='function'&&entry.gzipFile===entry.file+'.gz';
    const response=await fetch(compressed?entry.gzipFile:entry.file,options);
    if(!response.ok)return {response};
    // Content-Encoding is decoded by fetch itself; ordinary .gz files need a stream decoder.
    const value=compressed&&!/\bgzip\b/i.test(response.headers?.get('content-encoding')||'')
      ? await new Response(response.body.pipeThrough(new DecompressionStream('gzip'))).json()
      : await response.json();
    return {response,value};
  }
  async function getManifest(fresh=false){
    if(!fresh&&Date.now()-manifestAt<300000)return manifest;
    if(!fresh&&manifestRequest)return manifestRequest;
    const version=++manifestVersion,ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),5000);
    const request=(async()=>{
      try{
        const response=await fetch('browser/manifest.json?v=1&t='+Math.floor(Date.now()/300000),{cache:'no-store',signal:ctrl.signal});
        if(!response.ok)throw Error('Browser manifest unavailable');
        const value=await response.json();if(value.version!==1||!value.investors)throw Error('Invalid browser manifest');
        for(const [id,entry] of Object.entries(value.investors))if(!/^[a-z][a-z0-9_]{0,30}$/.test(id)||!asset(entry.snapshot)||!asset(entry.history)||!entry.snapshot.file.startsWith('browser/'+id+'-current-')||!entry.history.file.startsWith('browser/'+id+'-history-'))throw Error('Invalid browser asset');
        if(version===manifestVersion){manifest=value;manifestAt=Date.now();}
        return value;
      }catch(error){if(version===manifestVersion){manifestAt=Date.now()-270000;}return manifest;}
      finally{clearTimeout(timer);if(version===manifestVersion)manifestRequest=null;}
    })();manifestRequest=request;return request;
  }
  async function load(id,{fresh=false,signal,retried=false}={}){
    const available=await getManifest(fresh),entry=available?.investors&&Object.prototype.hasOwnProperty.call(available.investors,id)?available.investors[id]:null;
    if(!entry)return null;
    if(signal?.aborted)throw Error('Selection superseded');
    if(!fresh&&snapshots.has(entry.snapshot.file))return remember(snapshots,entry.snapshot.file,snapshots.get(entry.snapshot.file),3);
    const {response,value}=await fetchAsset(entry.snapshot,{signal,cache:fresh?'no-store':'default'});
    if(response.status===404&&!retried){await getManifest(true);return load(id,{signal,retried:true});}
    if(!response.ok)throw Error('Investor snapshot HTTP '+response.status);
    if(value.version!==1||value.investor!==id||!value.data?.current||!value.prices?.quotes||Array.isArray(value.prices.quotes)||!asset(value.history)||value.history.file!==entry.history.file||value.data.browserProjection?.version!==1||value.insights?.schemaVersion!==2||!value.insights.entries)throw Error('Invalid investor snapshot');
    for(const [kind,digest] of Object.entries(value.data.browserProjection.sources||{}))if(!/^[a-f0-9]{64}$/.test(digest)||value.insights.entries[kind+':'+id]?.source?.browserSource!==digest)throw Error('Investor insight source mismatch');
    return remember(snapshots,entry.snapshot.file,value,3);
  }
  async function history(entry,{signal}={}){
    if(!asset(entry))throw Error('Invalid history path');
    if(histories.has(entry.file))return histories.get(entry.file);
    const {response,value}=await fetchAsset(entry,{signal,cache:'default'});
    if(!response.ok){const error=Error('History HTTP '+response.status);error.status=response.status;throw error;}
    const id=/^browser\/([a-z][a-z0-9_]*)-history-/.exec(entry.file)[1];if(value.version!==1||value.investor!==id||!value.history?.holdings||!value.exitPerf)throw Error('Invalid history snapshot');
    return remember(histories,entry.file,value,1);
  }
  root.InvestorSnapshots={load,history,getManifest};
})(globalThis);
