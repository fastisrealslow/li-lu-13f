const test=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const vm=require('node:vm');
const path=require('node:path');
const root=path.join(__dirname,'..');
const read=p=>JSON.parse(fs.readFileSync(path.join(root,p),'utf8'));
test('every displayed stock and eligible HK supplemental row has a recent matching quote',()=>{
  const c=vm.createContext({console,Date,window:{innerWidth:1440},localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){}}});
  vm.runInContext(fs.readFileSync(path.join(root,'app.js'),'utf8'),c);
  for(const cfg of read('investors.json').investors){
    const d=read(cfg.dataFile),p=read(cfg.pricesFile);
    for(const h of d.current.holdings.filter(h=>!h.shareType||h.shareType==='SH')){
      const q=p.quotes[h.ticker],event=read('security_lifecycle.json').events[h.cusip];
      if(/\bWARRANT\b/i.test(h.cls||'')&&q?.status==='filing_reference'){assert.equal(q.cusip,h.cusip);assert.equal(q.filedUnitValue,h.value/h.shares);assert.equal(q.asOf,d.current.periodEnd);assert.equal(q.sourceURL,d.current.sourceFiling);continue;}
      if(event&&event.ticker===h.ticker&&event.effectiveDate<=new Date().toISOString().slice(0,10)){assert.equal(q?.status,'ceased_trading');assert.deepEqual(q.event,event);assert.match(event.sourceURL,/^https:\/\//);continue;}
      assert.ok(!h.ticker.startsWith('?')&&q?.c>0&&Number.isFinite(q.t)&&q.t*1000<=Date.now()+600000&&Date.now()-q.t*1000<=7*86400000&&!q.error&&!q.stale,`${cfg.id}/${h.ticker}`);
    }
    if(!cfg.hkFile)continue;
    c.cfg=cfg;c.snapshot=d;c.quotes=p;c.hk=read(cfg.hkFile);
    const rows=vm.runInContext('prices=quotes;latestReportedHKHoldings(hk,cfg,snapshot.current.quarter)',c);
    for(const h of rows){c.h=h;assert.equal(vm.runInContext('hkQuoteState(h.ticker,h.shareClass).usable',c),true,`${cfg.id}/${h.ticker} HK supplement`);}
  }
});
test('every quoted listing in the personal portfolio has a dated positive price',()=>{
  function check(value,company,seen){
    if(!value||typeof value!=='object')return;
    if(value.quote){const q=value.quote,at=Date.parse(q.asOf+'T00:00:00Z');assert.ok(q.price>0&&q.ticker&&Number.isFinite(at)&&at<=Date.now()&&Date.now()-at<=7*86400000,company);seen.add(q.ticker);}
    for(const item of Object.values(value))if(item&&typeof item==='object')check(item,company,seen);
  }
  for(const company of read('personal_portfolio.json').companies){const seen=new Set();check(company.results,company.id,seen);for(const listing of company.listings)assert.ok(seen.has(listing.ticker),company.id+'/'+listing.ticker);}
});
