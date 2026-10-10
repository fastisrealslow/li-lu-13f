/* Shared arithmetic and progress rules. USD throughout; display converts to 亿 explicitly. */
(function(root, factory) {
  const model = factory();
  if (typeof module === 'object' && module.exports) module.exports = model;
  else root.TrialsModel = model;
})(typeof globalThis !== 'undefined' ? globalThis : this, function() {
  'use strict';
  const DEFAULTS = Object.freeze({market:25, share:50, margin:4, multiple:18});
  const LIMITS = {market:[0,100,.5], share:[0,100,1], margin:[0,10,.5], multiple:[5,40,1]};
  function parameters(input) {
    return Object.fromEntries(Object.entries(LIMITS).map(([key, [min,max,step]]) => {
      const v = input && input[key];
      const n = typeof v === 'number' && Number.isFinite(v) ? v : DEFAULTS[key];
      return [key, Math.round(Math.min(max, Math.max(min,n)) / step) * step];
    }));
  }
  function calculate(input) {
    const p = parameters(input);
    const servings = 8e9 * 8 * 365 * p.market / 100 * p.share / 100;
    const profit = servings * p.margin / 100;
    return {params:p, servings, profit, value:profit * p.multiple,
      neededMultiple:profit > 0 ? 2e12 / profit : null,
      marginHalvedValue:profit * .5 * p.multiple,
      shareHalvedValue:profit * .5 * p.multiple,
      lowerMultipleValue:profit * 12};
  }
  const MISSIONS = [
    {title:'还原演讲算式', detail:'将行业占饮水份额调到 25%、公司份额 50%、每份净利 4 美分。估值倍数由你选择。',
      pass:p => p.market === 25 && p.share === 50 && p.margin === 4,
      feedback:'算对了：年销量 2.92 万亿份，年利润 1,168 亿美元。演讲将利润约写为 1,170 亿美元；倍数是本游戏新增的分析变量。'},
    {title:'检验利润减半', detail:'保持 25% 和 50% 两项份额，把每份净利改为 2 美分，并使用 18 倍估值。',
      pass:p => p.market === 25 && p.share === 50 && p.margin === 2 && p.multiple === 18,
      feedback:'年利润只剩 584 亿美元，18 倍对应 1.0512 万亿美元。规模够大仍不意味着任何利润率都能实现目标。'},
    {title:'检验估值收缩', detail:'把每份净利恢复到 4 美分，两项份额保持 25% 和 50%，再把估值倍数降到 12。',
      pass:p => p.market === 25 && p.share === 50 && p.margin === 4 && p.multiple === 12,
      feedback:'经营利润仍是 1,168 亿美元，估值降为 1.4016 万亿美元。销量、利润与估值是三层不同的问题。'}
  ];
  // Final board: a deliberately simple, fully disclosed teaching model, not company forecasts.
  function simulate(alloc) {
    const a = ['product','brand','channel'].map(k => Number.isInteger(alloc && alloc[k]) ? alloc[k] : 0);
    const valid = a.every(n => n >= 0 && n <= 10) && a.reduce((x,y)=>x+y,0) === 10;
    const margin = 1 + a[0] * .6;
    const share = Math.min(80, 10 + a[1] * 8);
    const market = Math.min(40, 10 + a[2] * 5);
    const servings = 8e9 * 8 * 365 * market / 100 * share / 100;
    const profit = servings * margin / 100;
    const base = {servings,profit,value:profit*18,neededMultiple:profit>0?2e12/profit:null};
    return {valid, product:a[0], brand:a[1], channel:a[2], market,share,margin,
      balanced:valid && a.every(n=>n>=2), weakest:['product','brand','channel'][a.indexOf(Math.min(...a))],
      ...base};
  }
  return {DEFAULTS,LIMITS,MISSIONS,parameters,calculate,simulate};
});
