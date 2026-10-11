/* Personal holdings are an independent, report-backed dataset. */
(function (root) {
  'use strict';
  const esc = v => String(v ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const finite = v => typeof v === 'number' && Number.isFinite(v);
  function rank(rows) {
    rows.forEach(r=>['earningsRank','capitalRank','rankSum','overallRank'].forEach(k=>delete r[k]));
    const eligible = rows.filter(r => r.status === 'ranked' && finite(r.earningsYield) && finite(r.returnOnCapital));
    for (const [metric, field] of [['earningsYield','earningsRank'],['returnOnCapital','capitalRank']]) {
      let previous, place;
      [...eligible].sort((a,b) => b[metric]-a[metric]).forEach((r,i) => {
        if (previous === undefined || Math.abs(r[metric]-previous) > Math.max(1e-12,Math.abs(previous)*1e-12)) place=i+1;
        r[field]=place;previous=r[metric];
      });
    }
    eligible.forEach(r => r.rankSum=r.earningsRank+r.capitalRank);
    let previous, place;
    const ordered = eligible.sort((a,b) => a.rankSum-b.rankSum || a.id.localeCompare(b.id));
    ordered.forEach((r,i) => {if (r.rankSum!==previous) place=i+1;r.overallRank=place;previous=r.rankSum;});
    return [...ordered,...rows.filter(r => !eligible.includes(r))];
  }
  let data, pending, windowYears=1, error='', listingChoices={};
  try { listingChoices=JSON.parse(localStorage.getItem('personalListingChoices') || '{}'); } catch (_) {}
  const en = () => typeof lang !== 'undefined' && lang === 'en';
  const tr = (zh,english) => en() ? english : zh;
  const pct = n => finite(n) ? (n*100).toFixed(2)+'%' : '—';
  const exact = n => finite(n) ? new Intl.NumberFormat('zh-CN',{maximumFractionDigits:2}).format(n) : '—';
  const displayTicker = ticker => /\.HK$/.test(ticker) ? ticker.replace(/\.HK$/, '').padStart(5,'0')+'.HK' : ticker;
  const displayDate = stamp => {const d=new Date(stamp);return Number.isFinite(d.getTime()) ? d.toLocaleString('sv-SE',{timeZone:'Asia/Shanghai'}).slice(0,16) : stamp;};
  const compact = n => !finite(n) ? '—' : en() ? (n/1e6).toFixed(2)+'m' : (n/1e8).toFixed(2)+' 亿';
  function sourceLink(c,f) {
    const s=c.sources[f?.sourceId];if (!s) return '';
    const url=s.url+(f.page ? '#page='+f.page : '');
    return `<a href="${esc(url)}" target="_blank" rel="noopener noreferrer">${esc(s.title)}${f.page?' · PDF '+f.page:''} ↗</a>`;
  }
  function factRow(c,f,operation='') {
    return `<tr><td>${esc(operation)} ${esc(f.label)}</td><td>${exact(operation?Math.abs(f.value):f.value)}</td><td>${sourceLink(c,f)}<details class="pp-evidence"><summary>${tr('原始依据','Evidence')}</summary><p>${esc(f.evidence)}</p>${f.policy?`<p>${tr('这是明确的报表分类政策；不是把读取失败当成零。','This is a disclosed classification policy, not a missing-data fallback.')}</p>`:''}</details></td></tr>`;
  }
  function ledger(c,p) {
    const f=p.facts;
    return `<details class="pp-year"><summary>${p.end.slice(0,4)} ${tr('年度逐项数据','annual ledger')}${p.audited===false?' · '+tr('全年可比数据未审计','unaudited calendar comparison'):''}</summary>
      <p class="pp-small">${tr('下列数字为财报货币的元，保留财报精度。加减号对应下方计算；商誉、品牌无形资产及长期股权投资不计入有形资本。','Amounts use the report currency’s base unit. Goodwill, brand intangibles and long-term equity investments are excluded from tangible capital.')} · ${esc(c.currency)}</p>
      <div class="pp-ledger-scroll"><table class="pp-ledger"><thead><tr><th>${tr('财报项目 / 处理','Financial input')}</th><th>${tr('金额 / 股数','Amount / shares')}</th><th>${tr('原始财报','Original report')}</th></tr></thead><tbody>
      ${factRow(c,f.operatingProfit)}${p.ebitAdjustments.map(a => factRow(c,a,a.value>=0?'+':'−')).join('')}
      ${['currentAssets','cash','restrictedCash','currentFinancialAssets','otherNonOperatingCurrentAssets','currentLiabilities','currentDebt','currentLeases','currentNonOperatingLiabilities','ppe','rou','operatingInvestmentProperty','landUseRights','noncurrentDebt','noncurrentLeases','minorityInterest','preferredEquity','noncurrentCashLike','ordinaryShares'].filter(k=>f[k]).map(k=>factRow(c,f[k])).join('')}
      ${factRow(c,p.evCashLikeFinancialAssets)}</tbody></table></div></details>`;
  }
  function equations(c,r) {
    const ps=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,windowYears);
    const latest=c.latestBalance || ps[0], f=latest.facts, b=r.balanceComponents;
    if (!b) return '';
    const perYear=ps.map((p,i) => {
      const f=p.facts,a=r.annualComponents[i];
      return `<div class="pp-equation"><strong>${p.end.slice(0,4)} · ${tr('经营利润 EBIT','Operating EBIT')}</strong><p>${compact(f.operatingProfit.value)}${p.ebitAdjustments.map(x=>` ${x.value>=0?'+':'−'} ${compact(Math.abs(x.value))} (${esc(x.label)})`).join('')} = <b>${compact(a.ebit)}</b></p>
        <strong>${tr('净运营资本','Net operating working capital')}</strong><p class="pp-small">${tr('流动资产减现金、受限资金、金融资产及应收利息等，再减流动负债（先剔除借款、租赁及非经营负债）。','Current assets less cash, restricted cash, financial assets and non-operating receivables, less current liabilities excluding financing and non-operating liabilities.')}</p><p>(${compact(f.currentAssets.value)} − ${compact(f.cash.value)} − ${compact(f.restrictedCash.value)} − ${compact(f.currentFinancialAssets.value)} − ${compact(f.otherNonOperatingCurrentAssets.value)}) − (${compact(f.currentLiabilities.value)} − ${compact(f.currentDebt.value)} − ${compact(f.currentLeases.value)} − ${compact(f.currentNonOperatingLiabilities.value)}) = <b>${compact(a.workingCapital)}</b></p>
        <strong>${tr('有形固定资本','Net tangible fixed capital')}</strong><p class="pp-small">${tr('固定资产及在建工程净额＋使用权资产＋经营性投资物业＋单独列示土地使用权。','Net PPE and construction + ROU assets + operating property + separately disclosed land rights.')}</p><p>${compact(f.ppe.value)} + ${compact(f.rou.value)} + ${compact(f.operatingInvestmentProperty.value)} + ${compact(f.landUseRights.value)} = <b>${compact(a.fixedCapital)}</b></p>
        <strong>${tr('投入资本','Invested capital')}</strong><p>${compact(a.workingCapital)} + ${compact(a.fixedCapital)} = <b>${compact(a.investedCapital)}</b></p></div>`;
    }).join('');
    const q=r.quote;
    const fx=new Intl.NumberFormat('zh-CN',{maximumFractionDigits:6}).format(q.fxToReportCurrency);
    return `<div class="pp-equations">${perYear}<div class="pp-equation"><strong>${tr('报价换算为公司全部普通股市值','Quote → all ordinary equity')}</strong><p>${exact(q.price)} ${esc(q.currency)} × ${exact(f.ordinaryShares.value)} ${tr('股','shares')} ÷ ${q.ordinarySharesPerQuoteUnit} × ${fx} = <b>${compact(r.equityValue)} ${esc(c.currency)}</b></p><p class="pp-small">${tr('港股每份报价对应 1 股；美股每份 ADS 对应财报注明的普通股数量。这里算公司全部市值，双重上市不相加。','HK quotes are per ordinary share; US quotes are per ADS. Dual listings are not added together.')} ${esc(q.fxDate?tr('汇率日期：','FX date: ')+q.fxDate:'')}</p>
      <strong>${tr('企业价值 EV','Enterprise value EV')}</strong><p>${compact(r.equityValue)} + ${compact(b.debt)} (${tr('借款＋租赁','debt + leases')}) + ${compact(f.minorityInterest.value)} (${tr('少数股东','minorities')}) + ${compact(f.preferredEquity.value)} (${tr('其他融资资本','other financing capital')}) − ${compact(b.cashLike)} (${tr('可抵扣现金与存款／证券','eligible cash / deposits / securities')}) = <b>${compact(r.enterpriseValue)}</b></p>
      <p class="pp-small">${tr('EV 抵扣项：非受限现金','EV offsets: unrestricted cash')} ${compact(f.cash.value)} + ${tr('可抵扣流动存款／证券','eligible current deposits / securities')} ${compact(latest.evCashLikeFinancialAssets.value)} + ${tr('非受限长期存款','unrestricted long-term deposits')} ${compact(f.noncurrentCashLike.value)} = ${compact(b.cashLike)}。</p>
      <p class="pp-small">${tr('受限现金不抵扣 EV；抵扣的流动证券范围见逐项财报依据。资产负债表日期：','Restricted cash does not reduce EV. Eligible securities are identified in the ledger. Balance date: ')}${latest.end}。</p>
      <strong>${tr('两个指标','The two metrics')}</strong><p>${windowYears===3?tr('三年平均 EBIT','Three-year average EBIT'): 'EBIT'} ${compact(r.ebit)} ÷ EV ${compact(r.enterpriseValue)} = <b>${pct(r.earningsYield)}</b></p><p>${windowYears===3?tr('三年平均 EBIT','Three-year average EBIT'): 'EBIT'} ${compact(r.ebit)} ÷ ${windowYears===3?tr('三年平均投入资本','average invested capital'):tr('投入资本','invested capital')} ${compact(r.investedCapital)} = <b>${pct(r.returnOnCapital)}</b></p></div></div>`;
  }
  function companyCard(c,r) {
    const q=r.quote, latest=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end))[0];
    const choice=listingChoices[c.id] || c.listings[0].ticker;
    const stale=q && (Date.now()-Date.parse(q.asOf)>7*86400000);
    const selectedPeriods=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,windowYears);
    const verdict=r.reason || r.capitalCaution || (r.earningsYield!=null && r.returnOnCapital!=null
      ? tr(`每 100 元企业价值对应 ${exact(r.earningsYield*100)} 元经营利润；每 100 元投入资本赚 ${exact(r.returnOnCapital*100)} 元。`, `EBIT per 100 of EV: ${exact(r.earningsYield*100)}; EBIT per 100 of capital: ${exact(r.returnOnCapital*100)}.`)
      : tr('参考财报计算，展开查看依据','Expand to inspect the calculation'));
    return `<details class="pp-company" data-company="${esc(c.id)}"><summary>
      <div class="pp-name"><span class="pp-rank">${r.overallRank || '—'}</span><div><strong>${esc(en()?c.nameEn:c.name)}</strong><small>${esc(displayTicker(choice))} · ${esc(c.currency)} ${tr('财报','reports')}</small></div></div>
      <div class="pp-metric"><small>${tr('盈利收益率 EBIT / EV','Earnings yield EBIT / EV')}</small><b>${pct(r.earningsYield)}</b><span>${r.earningsRank?tr('第 ','#')+r.earningsRank+tr(' 名',''):tr('不参与排名','Unranked')}</span></div>
      <div class="pp-metric"><small>${tr('资本回报率 ROC','Return on capital ROC')}</small><b>${pct(r.returnOnCapital)}</b><span>${r.capitalRank?tr('第 ','#')+r.capitalRank+tr(' 名',''):tr('不参与排名','Unranked')}</span></div>
      <div class="pp-score"><small>${tr('名次之和','Rank sum')}</small><b>${r.rankSum || '—'}</b><span>${tr('越小越靠前','Lower ranks first')}</span></div>
      <div class="pp-verdict"><p>${esc(verdict)}</p>${selectedPeriods.some(p=>p.audited===false)?`<small>${tr('含未审计全年可比数','Includes unaudited calendar-year comparatives')}</small>`:''}<small>${q?tr('收盘价 ','Close ')+exact(q.price)+' '+esc(q.currency)+' · '+esc(q.asOf.slice(0,10)):''}${stale?' · '+tr('沿用历史报价','Older quote retained'):''}</small></div>
      <span class="pp-open">${tr('计算依据','Calculation')} <span aria-hidden="true">＋</span></span></summary>
      <div class="pp-detail"><div class="pp-detail-top"><h3>${esc(c.name)} · ${tr('每一步如何算','How each step is calculated')}</h3>${c.listings.length>1?`<label>${tr('报价市场','Quote market')} <select data-listing="${esc(c.id)}" aria-label="${esc(c.name)} 报价市场">${c.listings.map(l=>`<option value="${esc(l.ticker)}"${l.ticker===choice?' selected':''}>${esc(displayTicker(l.ticker))} · ${l.currency}${l.ordinarySharesPerQuoteUnit>1?' · ADS ×'+l.ordinarySharesPerQuoteUnit:''}</option>`).join('')}</select></label>`:''}</div>
      ${c.notes.map(n=>`<p class="pp-note">${esc(n)}</p>`).join('')}
      ${q?`<p class="pp-small">${tr('参考价','Reference price')} ${exact(q.price)} ${esc(q.currency)} · ${esc(q.asOf)} · <a href="${esc(q.sourceUrl)}" target="_blank" rel="noopener noreferrer">${tr('行情来源','Quote source')} ↗</a></p>`:''}
      ${q?.fxSourceUrl?`<p class="pp-small"><a href="${esc(q.fxSourceUrl)}" target="_blank" rel="noopener noreferrer">${tr('汇率来源','FX source')} ↗</a> · ${esc(q.fxDate)}</p>`:''}
      ${c.adsConversion?`<p class="pp-small">ADS ${tr('换算依据','conversion evidence')}：${esc(c.adsConversion.evidence)} · ${sourceLink(c,c.adsConversion)}</p>`:''}
      ${r.status==='incomplete'?`<p>${esc(r.reason)}</p>`:equations(c,r)}
      ${windowYears===3?`<p class="pp-note">${tr('三年模式：先分别计算各年 EBIT 和投入资本，再取算术平均；两者相除。盈利收益率分母仍是当前股价与注明日期的资产负债表计算的 EV，不是平均历史收益率。','Three-year mode divides average EBIT by average capital. Earnings yield uses the current quoted EV, not an average of historical percentages.')}</p>`:''}
      ${[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,windowYears).map(p=>ledger(c,p)).join('')}
      ${c.financialStatus?.message?`<p class="pp-note">${esc(c.financialStatus.message)}</p>`:''}</div></details>`;
  }
  function render() {
    const el=document.getElementById('personalContent');if (!el) return;
    if (!data) {el.innerHTML=`<div class="pp-loading">${error?esc(error):tr('正在读取财报计算依据…','Loading report calculations…')}${error?'<button data-retry>重新读取</button>':''}</div>`;return;}
    const rows=rank(data.companies.map(c => {
      const ticker=listingChoices[c.id] || c.listings[0].ticker;
      const r=c.results?.[ticker]?.[String(windowYears)];
      return {...(r || {status:'incomplete',reason:tr('报价暂不可用，财报依据已保留','Quote unavailable; report evidence retained')}),id:c.id};
    }));
    const eligible=rows.filter(r=>r.status==='ranked').length;
    const periods=[...new Set(data.companies.flatMap(c=>[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,windowYears).map(p=>p.end.slice(0,4))))].sort().join(' / ');
    el.innerHTML=`<section class="pp-dashboard"><div class="pp-heading"><div><p class="pp-eyebrow">${tr('我的持仓 · 财报计算','MY HOLDINGS · REPORT CALCULATIONS')}</p><h2>${tr('神奇公式','The Magic Formula')}</h2><p>${tr('用两个数字看公司：经营利润相对企业价值有多高，经营投入的资本赚得有多好。','Two measures: operating earnings relative to enterprise value, and earnings relative to invested capital.')}</p></div><div class="pp-window" role="group" aria-label="计算年限"><button data-years="1" aria-pressed="${windowYears===1}">${tr('最近完整年度','Latest full year')}</button><button data-years="3" aria-pressed="${windowYears===3}">${tr('三年平均','3-year average')}</button></div></div>
      <div class="pp-context"><span>${data.companies.length} ${tr('只持仓','holdings')} · ${eligible} ${tr('只参与本组合排序','ranked within this portfolio')}</span><span>${tr('财报年度','Report years')} ${periods}</span><span>${tr('更新检查','Update check')} ${esc(displayDate(data.checkedAt || data.updatedAt))} ${tr('北京时间','China time')}</span></div>
      <div class="pp-rules"><p><strong>${tr('排序规则','Ranking')}</strong> ${tr('盈利收益率、资本回报率各自从高到低排，两个名次相加；总和越小越靠前。只比较这 8 家公司。','Rank each metric from high to low and add both ranks. A lower sum ranks first, within these eight companies.')}</p><p>${tr('展开公司即可看加减项和原始财报。亏损、投入资本或 EV 非正数的公司保留数据，说明原因，不强行排名。','Expand a company to inspect arithmetic and source filings. Losses and non-positive denominators remain visible without a misleading ranking.')}</p></div>
      ${error?`<p class="pp-note" role="status">${esc(error)} ${tr('当前仍显示上次读取成功的数据。','The last successful dataset remains visible.')}</p>`:''}
      <div class="pp-list">${rows.map(r=>companyCard(data.companies.find(c=>c.id===r.id),r)).join('')}</div>
      <details class="pp-method"><summary>${tr('统一计算口径与自动更新','Method and automatic updates')}</summary><p>${tr('EBIT / EV 为盈利收益率；EBIT /（净运营资本＋有形固定资本）为资本回报率。固定资本采用财报期末净账面值，包含使用权资产并将租赁负债计入 EV；酒店经营物业与单独列示的土地使用权按公司附注计入。不是 EBITDA，也不是净利润。','Earnings yield is EBIT / EV; ROC is EBIT / (net working capital + net tangible fixed capital). Net book values include ROU assets, operating hotel property and separately disclosed land rights; lease liabilities enter EV. EBIT is neither EBITDA nor net income.')}</p><p>${tr('只从 SEC 20-F、港交所／发行人年报、巨潮资讯年报读取财务数字。报价与汇率单独更新，保留实际交易日期。自动识别新年报，按公司规则读取、校验，再重算两种年限；格式变化或来源失败时保留上一版已核实数据，并在公司明细显示状态。AI 不补造缺失数字。','Financial inputs come only from original SEC, HKEX/issuer and CNINFO reports. Prices and FX are updated separately with trading dates. New reports are discovered and validated automatically; failed extraction retains the last verified ledger with a company-level status. AI never invents financial inputs.')}</p><p>${tr('所有加减项下方都有来源与原始文本。表内百分比和亿元为展示舍入，实际排名使用未舍入数值。','Every input links to its original report and evidence. Displayed amounts are rounded; rankings use unrounded values.')}</p></details></section>`;
    el.querySelectorAll('[data-years]').forEach(b=>b.addEventListener('click',()=>{windowYears=Number(b.dataset.years);render();}));
    el.querySelectorAll('[data-listing]').forEach(s=>s.addEventListener('change',()=>{const id=s.dataset.listing;listingChoices[id]=s.value;try{localStorage.setItem('personalListingChoices',JSON.stringify(listingChoices));}catch(_){}render();el.querySelector(`[data-company="${id}"]`).open=true;}));
  }
  async function load(force=false) {
    if (pending) return pending;
    if (data && !force) {render();return;}
    error='';render();
    const controller=new AbortController(), timeout=setTimeout(()=>controller.abort(),25000);
    pending=(async()=>{try{const res=await fetch('personal_portfolio.json',{cache:'no-cache',signal:controller.signal});if(!res.ok)throw Error('HTTP '+res.status);const next=await res.json();if(next.version!==1 || !Array.isArray(next.companies))throw Error('Invalid portfolio');data=next;}catch(e){error=tr('持仓数据读取失败，可重新读取。','Could not load the portfolio. Please retry.');}finally{clearTimeout(timeout);pending=null;render();document.querySelector('[data-retry]')?.addEventListener('click',()=>load(true));}})();
    return pending;
  }
  root.renderPersonalPortfolio=load;
  if (typeof document !== 'undefined') document.addEventListener('DOMContentLoaded',()=>{if(location.hash==='#personal')switchTab('personal');});
  if (typeof module !== 'undefined') module.exports={rank,esc};
})(typeof window !== 'undefined' ? window : globalThis);
