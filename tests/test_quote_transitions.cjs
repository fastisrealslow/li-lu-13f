const {test}=require('node:test'),assert=require('node:assert/strict'),fs=require('fs'),vm=require('vm');
const c=vm.createContext({console,Date,localStorage:{getItem:()=>null},document:{readyState:'loading',addEventListener(){}}});
vm.runInContext(fs.readFileSync('app.js','utf8'),c);
test('INDV route is labelled and cannot attach to the old SUPN class',()=>{
 c.h={ticker:'INDV',cusip:'45579U109'};c.q={c:29.72,t:Date.now()/1000,quotedForCUSIP:'45579U109',quoteTransition:{ticker:'INDV',cusip:'45579U109',sourceURL:'https://www.nasdaqtrader.com/TraderNews.aspx?id=ECA2026-742',note:'现以 SUPN 交易；特别股息未计入收益',noteEn:'Now SUPN; dividend excluded'}};
 assert.match(vm.runInContext('quoteTransitionHTML(h,q)',c),/SUPN.*特别股息/);
 assert.equal(vm.runInContext('quoteTransitionHTML({...h,cusip:"868459108"},q)',c),'');
 vm.runInContext('data={current:{quarter:"2026 Q2",periodEnd:"2026-06-30"}};prices={quotes:{INDV:q},corporateActions:{"45579U109":{preserveCost:false,effectiveDate:"2026-11-03"}},costBasis:{INDV:{recent:{buy:40}}}}',c);
 assert.equal(vm.runInContext('holdingCostState(h).reason',c),'corporate_action');
 assert.match(vm.runInContext('tradeQuoteHTML(h)',c),/29.72.*SUPN/);
 vm.runInContext('prices.tradePrices={entries:{"45579U109":{ticker:"INDV",cusip:"45579U109",quarters:[{quarter:"2026 Q2",averageCost:40}]}}}',c);
 assert.doesNotMatch(vm.runInContext('tradePriceCells(h).average',c),/40.00/);
});
