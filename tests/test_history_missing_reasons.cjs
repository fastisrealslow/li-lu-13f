const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('node:fs'),vm=require('node:vm');
function app(){const c=vm.createContext({console,setTimeout,clearTimeout,AbortController,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){},querySelectorAll:()=>[]}});vm.runInContext(fs.readFileSync('app.js','utf8'),c);return code=>vm.runInContext(code,c);}
test('missing price reasons distinguish identity, reference quote and historical boundary',()=>{
 const run=app();run('data={meta:{costHistoryFrom:"2012 Q1"}};prices={quotes:{}}');
 assert.match(run('tradeQuoteHTML({ticker:"?Unverified",cusip:"x"})'),/身份待核实/);
 assert.match(run('tradeQuoteHTML({ticker:"KNOWN",cusip:"x"})'),/暂无可靠市场报价/);
 assert.match(run('tradeHistoryCoverage({ticker:"WFC",quarters:[]},"buy")'),/2012 Q1/);
 assert.match(run('tradeHistoryCoverage({ticker:"?Unknown",quarters:[]},"buy")'),/身份待核实/);
 assert.match(run('tradeHistoryCoverage({ticker:"WFC",quarters:[{quarter:"2013 Q1",buy:1}],missingBuyQuarters:1},"buy")'),/尚缺 1/);
 run('prices.quotes.KNOWN={c:10,status:"filing_reference"}');assert.match(run('tradeQuoteHTML({ticker:"KNOWN",cusip:"x"})'),/不代表现价/);
});
