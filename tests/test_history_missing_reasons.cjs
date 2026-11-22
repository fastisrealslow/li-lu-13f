const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function app(){const c=vm.createContext({console,setTimeout,clearTimeout,AbortController,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},querySelectorAll:()=>[]}});vm.runInContext(fs.readFileSync('app.js','utf8'),c);return code=>vm.runInContext(code,c);}
test('missing price reasons distinguish identity, reference quote and historical boundary',()=>{
 const run=app();run('data={meta:{costHistoryFrom:"2012 Q1"}};prices={quotes:{}}');
 assert.match(run('tradeQuoteHTML({ticker:"?Unverified",cusip:"x"})'),/身份待核实/);
 assert.match(run('tradeQuoteHTML({ticker:"KNOWN",cusip:"x"})'),/暂无可靠市场报价/);
 assert.match(run('tradeHistoryCoverage({ticker:"WFC",quarters:[]},"buy")'),/暂无符合条件.*组合估价起点.*2012 Q1/);
 assert.doesNotMatch(run('tradeHistoryCoverage({ticker:"RECENT",quarters:[]},"buy")'),/更早申报|仅在|由于/);
 assert.match(run('tradeHistoryCoverage({ticker:"?Unknown",quarters:[]},"buy")'),/身份待核实/);
 assert.match(run('tradeHistoryCoverage({ticker:"WFC",quarters:[{quarter:"2013 Q1",buy:1}],missingBuyQuarters:1},"buy")'),/尚缺 1/);
 run('prices.quotes.KNOWN={c:10,status:"filing_reference"}');assert.match(run('tradeQuoteHTML({ticker:"KNOWN",cusip:"x"})'),/不代表现价/);
});

test('archive-only gaps stay in details but do not set the live update light',()=>{
 const run=app();
 const archive={status:'warn',msg:'tepper 历史缺 1 季（2004 Q2）：补查未完成或原表未核实，后续重试；不作零持仓'};
 const row={schemaVersion:2,completedAt:'2026-11-22T02:42:33Z',steps:{tepper_13f:archive,lilu_13f:{status:'ok'}}};
 const now=Date.parse(row.completedAt),check=()=>run('runHealth('+JSON.stringify(row)+','+now+').state');
 assert.equal(check(),'ok');
 assert.match(run('statusStepMessage("tepper_13f",'+JSON.stringify(archive)+')'),/历史持仓缺/);
 assert.match(run('statusStepMessage("tepper_13f",'+JSON.stringify(archive)+')'),/2004 Q2/);
 row.steps.quotes={status:'warn',msg:'当前股价不可用'};
 assert.equal(check(),'warn');
 delete row.steps.quotes;
 row.steps.tepper_13f={...archive,msg:archive.msg+'；最新报告未获取'};
 assert.equal(check(),'warn');
 row.steps.tepper_13f={...archive,status:'fail'};
 assert.equal(check(),'fail');
 row.steps.tepper_13f=archive;
 assert.equal(run('runHealth('+JSON.stringify(row)+','+(now+37*3600000)+').state'),'warn');
});
