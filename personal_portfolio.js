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
  const operand = n => n < 0 ? `(${compact(n)})` : compact(n);
  function capitalReading(r) {
    const known=finite(r.ebit) && finite(r.investedCapital);
    return {known, applicable:known && r.investedCapital>0,
      arithmetic:known && r.investedCapital!==0 ? r.ebit/r.investedCapital : null,
      label:!known?tr('待更新','Pending'):r.investedCapital<=0?tr('不适用','Not applicable'):pct(r.returnOnCapital)};
  }
  function explanations(c,r,eligible) {
    if (!r.balanceComponents || !r.annualComponents?.length) return [];
    const parts=r.annualComponents,avg=key=>parts.reduce((s,p)=>s+p[key],0)/parts.length;
    const b=r.balanceComponents, latest=c.latestBalance || [...c.annuals].sort((a,b)=>b.end.localeCompare(a.end))[0],f=latest.facts;
    const unit=tr(`（${c.currency}，金额单位：亿元）`,` (${c.currency}, amounts in millions)`);
    const period=r.years===3?tr('三年平均','Three-year average'):tr('本年度','Annual');
    const netFunding=b.debt+f.minorityInterest.value+f.preferredEquity.value-b.cashLike;
    const notes=[{title:tr('盈利收益率为什么是这个数','What drives earnings yield'),body:tr(
      `${period} EBIT 为 ${compact(r.ebit)}，报价折算的全部普通股市值为 ${compact(r.equityValue)}。借款及租赁 ${compact(b.debt)}＋少数股东权益 ${compact(f.minorityInterest.value)}＋其他融资资本 ${compact(f.preferredEquity.value)}−可抵扣现金／存款／证券 ${compact(b.cashLike)}，净调整为 ${compact(netFunding)}。${netFunding<0?'现金抵扣使 EV 小于市值':'净融资使 EV 不低于市值'}，EV 为 ${compact(r.enterpriseValue)}${r.equityValue>0?`（市值的 ${pct(r.enterpriseValue/r.equityValue)}）`:''}。${r.enterpriseValue>0?`EBIT ÷ EV = ${pct(r.earningsYield)}；同一 EBIT 直接除以市值为 ${pct(r.ebit/r.equityValue)}，这个对照只解释 EV 分母的影响，不用于排名。`:'EV 非正数，此指标不适用。'}${unit}`,
      `${period} EBIT ${compact(r.ebit)}; all ordinary equity ${compact(r.equityValue)}. Debt/leases ${compact(b.debt)} + minorities ${compact(f.minorityInterest.value)} + other financing ${compact(f.preferredEquity.value)} − eligible cash ${compact(b.cashLike)} = net EV adjustment ${compact(netFunding)}. EV ${compact(r.enterpriseValue)} (${pct(r.enterpriseValue/r.equityValue)} of equity). ${r.enterpriseValue>0?`EBIT / EV = ${pct(r.earningsYield)}; EBIT / equity = ${pct(r.ebit/r.equityValue)} is a denominator comparison only.`:'Non-positive EV: earnings yield is not applicable.'}${unit}`)}];
    const wc=avg('workingCapital'),fixed=avg('fixedCapital'),reading=capitalReading(r);
    notes.push({title:tr('资本分母为什么大／小／为负','What drives the capital denominator'),body:tr(
      `${period}经营性流动资产 ${compact(avg('operatingCurrentAssets'))}−经营性流动负债 ${compact(avg('operatingCurrentLiabilities'))}=净运营资本 ${compact(wc)}。再加有形固定资本 ${compact(fixed)}，有形经营资本为 ${compact(r.investedCapital)}。${!reading.applicable?(r.investedCapital<0?`经营性流动负债超过经营性流动资产，差额还大于有形固定资本，因此分母为负。代入相除的算术商是 ${pct(reading.arithmetic)}，但不能用它衡量投入正资本的回报，ROC 标记为“不适用”，不进入联合排名。${r.ebit>0?'EBIT 为正，这个负商不表示公司亏损。':''}`:'分母为零，不能相除，ROC 不适用。'):`${wc<0?'负的净运营资本缩小了资本分母':'净运营资本为正，增加了资本分母'}，${compact(r.ebit)} ÷ ${compact(r.investedCapital)} = ${pct(r.returnOnCapital)}。${fixed>0 && wc<0?`如果仅观察 EBIT / 有形固定资本，算术比值为 ${pct(r.ebit/fixed)}；加上负运营资本后分母更小，ROC 比值随之变化。这个对照不替代正式公式。`:''}`}${r.capitalCaution?` ${r.capitalCaution}。`:''}${unit}`,
      `${period} operating current assets ${compact(avg('operatingCurrentAssets'))} − operating current liabilities ${compact(avg('operatingCurrentLiabilities'))} = net working capital ${compact(wc)}. Add tangible fixed capital ${compact(fixed)}: tangible operating capital ${compact(r.investedCapital)}. ${!reading.applicable?(r.investedCapital<0?`The working-capital deficit exceeds fixed capital. Arithmetic quotient ${pct(reading.arithmetic)} is not a meaningful return on positive invested capital and is excluded from ranking. ${r.ebit>0?'EBIT is positive; this negative quotient does not indicate a loss.':''}`:'Zero denominator: division is undefined.'):`${wc<0?'Negative working capital reduces':'Positive working capital increases'} the denominator. ROC = ${pct(r.returnOnCapital)}.${fixed>0 && wc<0?` EBIT / fixed capital alone is ${pct(r.ebit/fixed)}, shown only to explain the denominator effect.`:''}`}${r.capitalCaution?' Some annual capital balances are non-positive; the average ratio is sensitive to the denominator.':''}${unit}`)});
    const selected=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,r.years||1);
    if (selected.every(p=>p.facts.otherGains)) {
      const gains=selected.reduce((s,p)=>s+p.facts.otherGains.value,0)/selected.length;
      notes.push({title:tr('利润里保留了哪些其他收益','Other gains included in earnings'),body:tr(`${period}“其他收益净额”为 ${compact(gains)}，已包含在报表经营利润及本页 EBIT 中，不再重复相加。本页只按列明项目调整 EBIT，未把所有投资处置／估值收益扣成“经常性利润”。该项的年报原文在逐项依据中。${unit}`,`${period} other net gains ${compact(gains)} are already included in operating profit and this EBIT. They are not added again. This is not a normalized recurring-profit measure; inspect the original-report evidence below.${unit}`)});
    }
    if (finite(eligible)) notes.push({title:tr('这次排名比较了谁','Ranking population'),body:r.status==='ranked'?tr(`当前模式下，8 只持仓中只有 ${eligible} 只同时满足 EBIT、EV 和有形经营资本为正。${c.name}的盈利收益率第 ${r.earningsRank} 名，ROC 第 ${r.capitalRank} 名，名次之和 ${r.rankSum}，综合第 ${r.overallRank} 名。“第 1”只指这些可排序持仓中的比较，不代表全市场排名。`,`Only ${eligible} of eight holdings have positive EBIT, EV and tangible capital in this mode. Earnings rank ${r.earningsRank}; ROC rank ${r.capitalRank}; sum ${r.rankSum}; overall rank ${r.overallRank}. Ranks apply only to eligible holdings, not the whole market.`):tr(`当前模式共有 ${eligible} 只持仓可参与联合排名。本公司未参与，原因：${r.reason}。有可计算的盈利收益率仍会显示，不能把未参与联合排名理解为财报数据缺失。`,`${eligible} holdings qualify for combined ranking. This company does not qualify: ${r.reason}. Available earnings yield remains visible; exclusion is not missing financial data.`)});
    return notes;
  }
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
      ${['otherGains','currentAssets','cash','restrictedCash','currentFinancialAssets','otherNonOperatingCurrentAssets','currentLiabilities','currentDebt','currentLeases','currentNonOperatingLiabilities','ppe','rou','operatingInvestmentProperty','landUseRights','noncurrentDebt','noncurrentLeases','minorityInterest','preferredEquity','noncurrentCashLike','ordinaryShares'].filter(k=>f[k]).map(k=>factRow(c,f[k])).join('')}
      ${factRow(c,p.evCashLikeFinancialAssets)}</tbody></table></div></details>`;
  }
  function equations(c,r) {
    const years=r.years || windowYears;
    const ps=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,years);
    const latest=c.latestBalance || ps[0], f=latest.facts, b=r.balanceComponents;
    if (!b) return '';
    const perYear=ps.map((p,i) => {
      const f=p.facts,a=r.annualComponents[i];
      return `<div class="pp-equation"><p class="pp-small">${esc(c.currency)} · ${tr('金额单位：亿元','Amounts in millions')}</p><strong>${p.end.slice(0,4)} · ${tr('① 税前利润 EBIT（按列明项调整）','① EBIT with disclosed adjustments')}</strong><p class="pp-symbolic">${tr('报表经营利润＋列明的调整项','Reported operating profit + listed adjustments')}</p><p>${compact(f.operatingProfit.value)}${p.ebitAdjustments.map(x=>` ${x.value>=0?'+':'−'} ${compact(Math.abs(x.value))} (${esc(x.label)})`).join('')} = <b>${compact(a.ebit)}</b></p>
        <strong>${tr('② 经营性流动资产','② Operating current assets')}</strong><p class="pp-symbolic">${tr('流动资产−现金−受限现金−流动金融资产−其他非经营流动资产','Current assets − cash − restricted cash − current financial assets − other non-operating current assets')}</p><p>${compact(f.currentAssets.value)} − ${compact(f.cash.value)} − ${compact(f.restrictedCash.value)} − ${compact(f.currentFinancialAssets.value)} − ${compact(f.otherNonOperatingCurrentAssets.value)} = <b>${compact(a.operatingCurrentAssets)}</b></p>
        <strong>${tr('③ 经营性流动负债','③ Operating current liabilities')}</strong><p class="pp-symbolic">${tr('流动负债−流动借款−流动租赁负债−其他非经营流动负债','Current liabilities − current debt − current leases − other non-operating current liabilities')}</p><p>${compact(f.currentLiabilities.value)} − ${compact(f.currentDebt.value)} − ${compact(f.currentLeases.value)} − ${compact(f.currentNonOperatingLiabilities.value)} = <b>${compact(a.operatingCurrentLiabilities)}</b></p>
        <strong>${tr('④ 净运营资本','④ Net operating working capital')}</strong><p class="pp-symbolic">${tr('② 经营性流动资产−③ 经营性流动负债','② Operating current assets − ③ operating current liabilities')}</p><p>${compact(a.operatingCurrentAssets)} − ${compact(a.operatingCurrentLiabilities)} = <b>${compact(a.workingCapital)}</b></p>
        <strong>${tr('⑤ 有形固定资本','⑤ Net tangible fixed capital')}</strong><p class="pp-symbolic">${tr('固定资产及在建工程净额＋使用权资产＋经营性投资物业＋单独列示土地使用权。','Net PPE and construction + ROU assets + operating property + separately disclosed land rights.')}</p><p>${compact(f.ppe.value)} + ${compact(f.rou.value)} + ${compact(f.operatingInvestmentProperty.value)} + ${compact(f.landUseRights.value)} = <b>${compact(a.fixedCapital)}</b></p>
        <strong>${tr('⑥ 有形经营资本（ROC 分母）','⑥ Tangible operating capital (ROC denominator)')}</strong><p class="pp-symbolic">${tr('净运营资本＋有形固定资本','Net working capital + tangible fixed capital')}</p><p>${operand(a.workingCapital)} + ${operand(a.fixedCapital)} = <b>${compact(a.investedCapital)}</b></p></div>`;
    }).join('');
    const q=r.quote;
    const fx=new Intl.NumberFormat('zh-CN',{maximumFractionDigits:6}).format(q.fxToReportCurrency);
    return `<div class="pp-equations">${perYear}<div class="pp-equation"><strong>${tr('报价换算为公司全部普通股市值','Quote → all ordinary equity')}</strong><p>${exact(q.price)} ${esc(q.currency)} × ${exact(f.ordinaryShares.value)} ${tr('股','shares')} ÷ ${q.ordinarySharesPerQuoteUnit} × ${fx} = <b>${compact(r.equityValue)} ${esc(c.currency)}</b></p><p class="pp-small">${tr('港股每份报价对应 1 股；美股每份 ADS 对应财报注明的普通股数量。这里算公司全部市值，双重上市不相加。','HK quotes are per ordinary share; US quotes are per ADS. Dual listings are not added together.')} ${esc(q.fxDate?tr('汇率日期：','FX date: ')+q.fxDate:'')}</p>
      <strong>${tr('企业价值 EV','Enterprise value EV')}</strong><p>${compact(r.equityValue)} + ${compact(b.debt)} (${tr('借款＋租赁','debt + leases')}) + ${compact(f.minorityInterest.value)} (${tr('少数股东','minorities')}) + ${compact(f.preferredEquity.value)} (${tr('其他融资资本','other financing capital')}) − ${compact(b.cashLike)} (${tr('可抵扣现金与存款／证券','eligible cash / deposits / securities')}) = <b>${compact(r.enterpriseValue)}</b></p>
      <p class="pp-small">${tr('EV 抵扣项：非受限现金','EV offsets: unrestricted cash')} ${compact(f.cash.value)} + ${tr('可抵扣流动存款／证券','eligible current deposits / securities')} ${compact(latest.evCashLikeFinancialAssets.value)} + ${tr('非受限长期存款','unrestricted long-term deposits')} ${compact(f.noncurrentCashLike.value)} = ${compact(b.cashLike)}。</p>
      <p class="pp-small">${tr('受限现金不抵扣 EV；抵扣的流动证券范围见逐项财报依据。资产负债表日期：','Restricted cash does not reduce EV. Eligible securities are identified in the ledger. Balance date: ')}${latest.end}。</p>
      <strong>${tr('盈利收益率','Earnings yield')}</strong><p class="pp-symbolic">${tr('盈利收益率＝EBIT ÷ 企业价值 EV','Earnings yield = EBIT / enterprise value EV')}</p><p>${operand(r.ebit)} ÷ ${operand(r.enterpriseValue)} ${tr('（相同货币单位）','(same currency units)')} = <b>${r.enterpriseValue>0?pct(r.earningsYield):tr('不适用：EV 非正数','Not applicable: non-positive EV')}</b></p>
      <strong>${tr('税前有形资本回报率 ROC','Pre-tax tangible return on capital ROC')}</strong><p class="pp-symbolic">ROC = EBIT ÷ (${tr('净运营资本＋有形固定资本','net working capital + tangible fixed capital')})</p>
      ${years===3?`<p class="pp-small">${tr('三年：平均 EBIT ÷（平均净运营资本＋平均有形固定资本），不是三个百分比的平均。','Three years: average EBIT / (average working capital + average fixed capital), not an average of percentages.')}</p><p>${tr('平均 EBIT','Average EBIT')} = (${r.annualComponents.map(p=>operand(p.ebit)).join(' + ')}) ÷ 3 = ${compact(r.ebit)}<br>${tr('平均有形经营资本','Average tangible operating capital')} = (${r.annualComponents.map(p=>operand(p.investedCapital)).join(' + ')}) ÷ 3 = ${compact(r.investedCapital)}</p>`:''}
      <p>${operand(r.ebit)} ÷ ${operand(r.investedCapital)} ${tr('（相同货币单位）','(same currency units)')}${r.investedCapital!==0?` = <b>${pct(capitalReading(r).arithmetic)}</b>`:` → <b>${tr('分母为零，不能相除','Zero denominator: undefined')}</b>`}</p>
      ${r.investedCapital<0?`<p class="pp-negative-meaning"><b>${tr('这个负数代表什么？','What does this negative balance mean?')}</b> ${tr('它表示：按本页扣除现金、金融资产且不计商誉等无形资产的口径，经营性负债超过计入的经营资产。供应商账期、客户预付款等可能形成这种资金结构；具体原因要看财报的应付款与预收款项目。这个数不是“总资产减总负债”，不等于公司净资产为负，也不表示经营不需要资金。','Under this measure, cash, financial assets and goodwill/intangibles are excluded, and operating liabilities exceed the operating assets counted. Supplier credit or customer prepayments may contribute; the actual mix must be checked in the payables and deferred-revenue notes. This balance is not total assets minus total liabilities: it does not mean negative equity or that operations require no funding.')}</p>`:''}
      ${r.investedCapital<=0?`<p class="pp-invalid"><b>${tr('ROC 不适用，不参与联合排名。','ROC is not applicable and is excluded from combined ranking.')}</b> ${r.investedCapital<0?tr('上面的负百分比只展示算术结果。分母是负的有形经营资本，不能把它当成投入正资本的回报率；EBIT 为正时，也不代表公司亏损。','The negative percentage is arithmetic only. A negative capital base cannot measure returns on positive capital, and positive EBIT does not indicate a loss.'):''}</p>`:''}
      </div></div>`;
  }
  function companyCard(c,r,eligible) {
    const q=r.quote, latest=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end))[0];
    const choice=listingChoices[c.id] || c.listings[0].ticker;
    const stale=q && (Date.now()-Date.parse(q.asOf)>7*86400000);
    const selectedPeriods=[...c.annuals].sort((a,b)=>b.end.localeCompare(a.end)).slice(0,windowYears);
    const verdict=(r.investedCapital<0 && r.ebit>0?tr(`有形经营资本为 ${compact(r.investedCapital)}：净运营资本的负额超过固定资本。EBIT 为正，ROC 不适用。`,`Tangible capital ${compact(r.investedCapital)}: the working-capital deficit exceeds fixed capital. EBIT is positive; ROC is not applicable.`):r.reason) || r.capitalCaution || (r.balanceComponents && r.enterpriseValue>0
      ? tr(`EV 为市值的 ${pct(r.enterpriseValue/r.equityValue)}；${r.annualComponents.reduce((s,a)=>s+a.workingCapital,0)<0?'负净运营资本缩小 ROC 分母':'净运营资本计入 ROC 分母'}。展开看数字推导。`, `EV is ${pct(r.enterpriseValue/r.equityValue)} of equity; ${r.annualComponents.reduce((s,a)=>s+a.workingCapital,0)<0?'negative working capital reduces':'working capital enters'} the ROC denominator. Expand for the numbers.`)
      : tr('参考财报计算，展开查看依据','Expand to inspect the calculation'));
    return `<details class="pp-company" data-company="${esc(c.id)}"><summary>
      <div class="pp-name"><span class="pp-rank">${r.overallRank || '—'}</span><div><strong>${esc(en()?c.nameEn:c.name)}</strong><small>${esc(displayTicker(choice))} · ${esc(c.currency)} ${tr('财报','reports')}</small></div></div>
      <div class="pp-metric"><small>${tr('盈利收益率 EBIT / EV','Earnings yield EBIT / EV')}</small><b class="${r.enterpriseValue<=0?'pp-na':''}">${r.enterpriseValue<=0?tr('不适用','Not applicable'):pct(r.earningsYield)}</b><span>${r.earningsRank?tr('第 ','#')+r.earningsRank+tr(' 名',''):tr('不参与联合排名','Excluded from combined rank')}</span></div>
      <div class="pp-metric"><small>${tr('资本回报率 ROC（税前）','Pre-tax ROC')}</small><b class="${r.investedCapital<=0?'pp-na':''}">${capitalReading(r).label}</b><span>${r.investedCapital<=0?tr('有形资本非正数','Non-positive tangible capital'):r.capitalRank?tr('第 ','#')+r.capitalRank+tr(' 名',''):tr('不参与联合排名','Excluded from combined rank')}</span></div>
      <div class="pp-score"><small>${tr('名次之和','Rank sum')}</small><b>${r.rankSum || '—'}</b><span>${tr('越小越靠前','Lower ranks first')}</span></div>
      <div class="pp-verdict"><p>${esc(verdict)}</p>${selectedPeriods.some(p=>p.audited===false)?`<small>${tr('含未审计全年可比数','Includes unaudited calendar-year comparatives')}</small>`:''}<small>${q?tr('收盘价 ','Close ')+exact(q.price)+' '+esc(q.currency)+' · '+esc(q.asOf.slice(0,10)):''}${stale?' · '+tr('沿用历史报价','Older quote retained'):''}</small></div>
      <span class="pp-open">${tr('计算依据','Calculation')} <span aria-hidden="true">＋</span></span></summary>
      <div class="pp-detail"><div class="pp-detail-top"><h3>${esc(c.name)} · ${tr('每一步如何算','How each step is calculated')}</h3>${c.listings.length>1?`<label>${tr('报价市场','Quote market')} <select data-listing="${esc(c.id)}" aria-label="${esc(c.name)} 报价市场">${c.listings.map(l=>`<option value="${esc(l.ticker)}"${l.ticker===choice?' selected':''}>${esc(displayTicker(l.ticker))} · ${l.currency}${l.ordinarySharesPerQuoteUnit>1?' · ADS ×'+l.ordinarySharesPerQuoteUnit:''}</option>`).join('')}</select></label>`:''}</div>
      ${c.notes.map(n=>`<p class="pp-note">${esc(n)}</p>`).join('')}
      ${c.listings.length>1?`<p class="pp-small">${tr('两个上市代码属于同一家公司，共用财报、EBIT 和 ROC。切换报价市场只会改变市值、EV 和盈利收益率，不重复计入持仓。','Both listings are one company with the same statements, EBIT and ROC. Changing the quote market changes equity value, EV and earnings yield only; the holding is counted once.')}</p>`:''}
      ${q?`<p class="pp-small">${tr('参考价','Reference price')} ${exact(q.price)} ${esc(q.currency)} · ${esc(q.asOf)} · <a href="${esc(q.sourceUrl)}" target="_blank" rel="noopener noreferrer">${tr('行情来源','Quote source')} ↗</a></p>`:''}
      ${q?.fxSourceUrl?`<p class="pp-small"><a href="${esc(q.fxSourceUrl)}" target="_blank" rel="noopener noreferrer">${tr('汇率来源','FX source')} ↗</a> · ${esc(q.fxDate)}</p>`:''}
      ${c.adsConversion?`<p class="pp-small">ADS ${tr('换算依据','conversion evidence')}：${esc(c.adsConversion.evidence)} · ${sourceLink(c,c.adsConversion)}</p>`:''}
      ${r.status==='incomplete'?`<p>${esc(r.reason)}</p>`:equations(c,r)}
      <div class="pp-explanations">${explanations(c,r,eligible).map(n=>`<section><h4>${esc(n.title)}</h4><p>${esc(n.body)}</p></section>`).join('')}</div>
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
      <div class="pp-list">${rows.map(r=>companyCard(data.companies.find(c=>c.id===r.id),r,eligible)).join('')}</div>
      <details class="pp-method"><summary>${tr('统一计算口径与自动更新','Method and automatic updates')}</summary><p class="pp-note">${tr('本页 ROC 是神奇公式的“税前有形资本回报率”。常见 ROIC 通常用税后经营利润 NOPAT ÷ 投入资本（常采用期初或平均资本，资本范围也可能不同）。名称有时混用，但这两套计算口径不能直接比较；本页不把 ROC 改名为税后 ROIC。','This ROC is the Magic Formula’s pre-tax tangible-capital measure. Common ROIC uses after-tax operating profit (NOPAT) / invested capital, often opening or average capital with a different asset scope. Names are sometimes interchangeable, but the formulas are not directly comparable.')} <a href="https://pages.stern.nyu.edu/~adamodar/pdfiles/papers/returnmeasures.pdf" target="_blank" rel="noopener noreferrer">${tr('ROIC 定义依据（NYU Stern）','ROIC definitions (NYU Stern)')} ↗</a></p><p>${tr('EBIT / EV 为盈利收益率；EBIT /（净运营资本＋有形固定资本）为资本回报率。固定资本采用财报期末净账面值，包含使用权资产并将租赁负债计入 EV；酒店经营物业与单独列示的土地使用权按公司附注计入。不是 EBITDA，也不是净利润。','Earnings yield is EBIT / EV; ROC is EBIT / (net working capital + net tangible fixed capital). Net book values include ROU assets, operating hotel property and separately disclosed land rights; lease liabilities enter EV. EBIT is neither EBITDA nor net income.')}</p><p>${tr('只从 SEC 20-F、港交所／发行人年报、巨潮资讯年报读取财务数字。报价与汇率单独更新，保留实际交易日期。自动识别新年报，按公司规则读取、校验，再重算两种年限；格式变化或来源失败时保留上一版已核实数据，并在公司明细显示状态。AI 不补造缺失数字。','Financial inputs come only from original SEC, HKEX/issuer and CNINFO reports. Prices and FX are updated separately with trading dates. New reports are discovered and validated automatically; failed extraction retains the last verified ledger with a company-level status. AI never invents financial inputs.')}</p><p>${tr('所有加减项下方都有来源与原始文本。表内百分比和亿元为展示舍入，实际排名使用未舍入数值。','Every input links to its original report and evidence. Displayed amounts are rounded; rankings use unrounded values.')}</p></details></section>`;
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
  if (typeof module !== 'undefined') module.exports={rank,esc,capitalReading,explanations,equations};
})(typeof window !== 'undefined' ? window : globalThis);
