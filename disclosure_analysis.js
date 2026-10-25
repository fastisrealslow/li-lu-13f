/* Longer, source-derived numerical analysis behind the concise tab conclusions. */
(function(){
  const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const sum=rows=>rows.reduce((n,h)=>n+h.value,0);
  const valid=rows=>Array.isArray(rows)&&rows.length&&rows.every(h=>Number.isFinite(h.value)&&h.value>=0);
  const percent=n=>n>0&&n<.01?'<0.01':n.toFixed(2);
  const quantity=n=>Number.isFinite(n)?n.toLocaleString('en-US'):'—';
  const money=(n,en)=>en?'US$'+quantity(Math.round(n)):Math.abs(n)>=1e8?(n/1e8).toFixed(2)+' 亿美元':Math.abs(n)<1e4?quantity(Math.round(n))+' 美元':(n/1e4).toFixed(2)+' 万美元';
  const perUnit=n=>'$'+n.toFixed(n>0&&n<.01?4:2);
  const stock=(h,en)=>((en?h.name:h.cnName)||h.name||h.ticker)+` (${h.ticker}${h.putCall?' '+h.putCall.toUpperCase():''})`;
  const unit=(h,en)=>h.putCall?(en?'underlying shares':'标的股数'):h.shareType&&h.shareType!=='SH'?(en?'principal':'本金'):(en?'shares':'股数');
  const key=h=>/^[A-Z0-9]{9}$/.test(h.cusip||'')?h.cusip.slice(0,6):h.ticker;
  const quarter=q=>{const m=/^(\d{4}) ?Q([1-4])$/.exec(q||'');return m?Number(m[1])*4+Number(m[2]):null;};
  const section=(heading,items)=>({heading,items});
  function holdings(d,en){
    const rows=consolidateHoldings(d.current.holdings),total=sum(rows),groups=new Map();
    for(const h of rows.filter(h=>!h.putCall&&(!h.shareType||h.shareType==='SH'))){if(!groups.has(key(h)))groups.set(key(h),[]);groups.get(key(h)).push(h);}
    const issuers=[...groups.values()].sort((a,b)=>sum(b)-sum(a)),top=issuers.slice(0,8),result=[];
    result.push(section(en?'Issuer concentration':'公司层面的集中度',top.map(g=>{
      const value=sum(g),names=g.map(h=>stock(h,en)).join(en?'; ':'、');
      return en?`${names}: ${money(value,en)}, ${percent(value/total*100)}% of reported value.${g.length>1?' These share classes belong to one issuer.':''}`:`${names}：合计申报 ${money(value,en)}，占本期 ${percent(value/total*100)}%。${g.length>1?'这几项股份属于同一家公司，分列不等于分散到不同企业。':''}`;
    })));
    const ranked=rows.slice().sort((a,b)=>b.value-a.value);let running=0,k=0;
    for(const h of ranked){running+=h.value;k++;if(running/total>=.8)break;}
    const small=rows.filter(h=>h.value/total<.01),tail=sum(small);
    result.push(section(en?'Core and smaller positions':'核心与尾部的实际规模',[
      en?`The largest ${k} securities account for ${percent(running/total*100)}% of reported value. The other ${rows.length-k} account for ${percent((total-running)/total*100)}%.`:`按申报金额从大到小排列，前 ${k} 项已覆盖 ${percent(running/total*100)}%；其余 ${rows.length-k} 项合计 ${percent((total-running)/total*100)}%。因此，理解组合变化时，这些头部证券的影响更大。`,
      en?`${small.length} positions each below 1% together report ${money(tail,en)}, or ${percent(tail/total*100)}%.`:`各自不足 1% 的 ${small.length} 项合计 ${money(tail,en)}，占 ${percent(tail/total*100)}%。小仓位数量与它们实际占用的申报金额，需要分开看。`
    ]));
    if(comparisonState(d)==='comparable'&&!(d.history?.excludedValueQuarters||[]).includes(d.current.prevQuarter)){
      const old=d.current.previousHoldings??d.history?.holdings?.[d.current.prevQuarter],oldTotal=valid(old)?sum(old):0;
      const previousRows=consolidateHoldings(old||[]),comparisonRows=quarterlyHoldings(d);
      if(oldTotal>0)result.push(section(en?'How the largest weights changed':'头部仓位与上季的差异',ranked.slice(0,8).map(h=>{
        const previous=previousRows.find(p=>sameSecurity(h,p)),value=previous?.value||0,now=h.value/total*100,before=value/oldTotal*100,delta=now-before;
        const comparison=comparisonRows.find(p=>sameSecurity(h,p)),oldShares=comparison?.prevShares??previous?.shares??0;
        const split=comparison?.shareAdjustment?(en?' (split adjusted)':'（按拆股后可比口径）'):'';
        return en?`${stock(h,en)}: ${percent(before)}% → ${percent(now)}% (${delta>=0?'+':''}${delta.toFixed(2)} percentage points); ${unit(h,en)} ${quantity(oldShares)} → ${quantity(h.shares)}${split}. ${comparison?changeText(comparison,true):''}`:`${stock(h,en)}：申报占比 ${percent(before)}% → ${percent(now)}%，变化 ${delta>=0?'+':''}${delta.toFixed(2)} 个百分点；${unit(h,en)} ${quantity(oldShares)} → ${quantity(h.shares)}${split}。${comparison?changeText(comparison,false):''}。`;
      })));
    }
    const options=rows.filter(h=>h.putCall);
    if(options.length)result.push(section(en?'Option notional scale':'期权覆盖的标的规模',options.map(h=>en?`${stock(h,en)} covers ${quantity(h.shares)} underlying shares and reports ${money(h.value,en)}, ${percent(h.value/total*100)}% notional weight. This is not premium invested or a delta-adjusted stock position.`:`${stock(h,en)} 覆盖标的 ${quantity(h.shares)} 股，标的名义金额 ${money(h.value,en)}，占申报总值 ${percent(h.value/total*100)}%。这说明覆盖标的的规模，不是投入权利金，也不能直接转换成同方向、同比例的正股仓位。`)));
    const principal=rows.filter(h=>h.shareType&&h.shareType!=='SH'&&!h.putCall);
    if(principal.length)result.push(section(en?'Principal-denominated securities':'以本金申报的证券',principal.map(h=>en?`${stock(h,en)}: reported principal ${quantity(h.shares)}, reported market value ${money(h.value,en)}, ${percent(h.value/total*100)}% of the filing.`:`${stock(h,en)}：申报本金 ${quantity(h.shares)}，申报市值 ${money(h.value,en)}，占本期 ${percent(h.value/total*100)}%。`)));
    return result.filter(s=>s.items.length);
  }
  function changes(d,en){
    const previous=d.current.previousHoldings??d.history?.holdings?.[d.current.prevQuarter];
    if(comparisonState(d)!=='comparable'||!valid(previous)||(d.history?.excludedValueQuarters||[]).includes(d.current.prevQuarter))return [];
    const rows=quarterlyHoldings(d),total=sum(rows),before=rows.reduce((s,h)=>s+(h.prevValue||0),0);
    if(!before||!rows.every(h=>Number.isFinite(h.prevValue)))return [];
    const ranked=rows.slice().sort((a,b)=>Math.abs(b.value-b.prevValue)-Math.abs(a.value-a.prevValue));
    const changed=ranked.filter(h=>h.shares!==h.prevShares),unchanged=ranked.filter(h=>h.shares===h.prevShares&&h.value!==h.prevValue).slice(0,5);
    const up=rows.filter(h=>h.value>h.prevValue),down=rows.filter(h=>h.value<h.prevValue);
    const increase=up.reduce((s,h)=>s+h.value-h.prevValue,0),decrease=down.reduce((s,h)=>s+h.prevValue-h.value,0);
    const entrants=rows.filter(h=>h.shares>0&&!h.prevShares),exits=rows.filter(h=>!h.shares&&h.prevShares>0),continuing=rows.filter(h=>h.shares>0&&h.prevShares>0);
    const detail=h=>{
      const now=total?h.value/total*100:0,old=h.prevValue/before*100,split=h.shareAdjustment?(en?' (split adjusted)':'（按拆股后可比口径）'):'';
      let extra='';
      if(h.prevShares>0&&h.shares>0){
        const oldUnit=h.prevValue/h.prevShares,newUnit=h.value/h.shares;
        if(h.shares===h.prevShares||((h.shares-h.prevShares)*(h.value-h.prevValue)<0))extra=en?` Filed value per ${h.shareType==='PRN'?'unit of principal':h.putCall?'underlying share':'share'} ${perUnit(oldUnit)} → ${perUnit(newUnit)}.`:` 每${h.shareType==='PRN'?'单位本金':h.putCall?'股标的':'股'}申报价值 ${perUnit(oldUnit)} → ${perUnit(newUnit)}。`;
      }
      return en?`${stock(h,en)}: ${changeText(h,true)}; ${unit(h,en)} ${quantity(h.prevShares)} → ${quantity(h.shares)}${split}; reported value ${money(h.prevValue,en)} → ${money(h.value,en)}; weight ${percent(old)}% → ${percent(now)}%.${extra}`:`${stock(h,en)}：${changeText(h,false)}；${unit(h,en)} ${quantity(h.prevShares)} → ${quantity(h.shares)}${split}；申报金额 ${money(h.prevValue,en)} → ${money(h.value,en)}；申报占比 ${percent(old)}% → ${percent(now)}%。${extra}`;
    };
    return [section(en?'Reported value bridge':'申报金额变化怎样构成',[
      en?`Positions with higher reported values add ${money(increase,en)}; positions with lower values subtract ${money(decrease,en)}. The net change is ${money(total-before,en)}. These are filing-value differences, not cash spent or received.`:`申报金额上升的证券合计增加 ${money(increase,en)}，下降的证券合计减少 ${money(decrease,en)}，两者相抵后，本期申报总值净变化 ${money(total-before,en)}。这些金额包含股价和股数的共同影响，并不是本季度实际花费或收回的资金。`,
      en?`${entrants.length} new entries represent ${percent(sum(entrants)/total*100)}% of this filing. The ${exits.length} exits represented ${percent(sum(exits.map(h=>({...h,value:h.prevValue})))/before*100)}% of the previous filing. The ${continuing.length} continuing securities now account for ${percent(sum(continuing)/total*100)}%.`:`本期新进入披露的 ${entrants.length} 项证券，占本期申报金额 ${percent(sum(entrants)/total*100)}%；已退出的 ${exits.length} 项，占上期申报金额 ${percent(exits.reduce((s,h)=>s+h.prevValue,0)/before*100)}%。两期持续披露的 ${continuing.length} 项，占本期 ${percent(sum(continuing)/total*100)}%，可据此区分组合是主要调整原有证券，还是出现较大范围的新旧替换。`
    ]),section(en?`All ${changed.length} share changes`:`全部 ${changed.length} 项股数变化：新建、增持、减持与退出`,changed.map(detail)),section(en?'Largest value changes with unchanged shares':'股数未变、金额变化较大的证券',unchanged.map(detail))].filter(s=>s.items.length);
  }
  function history(d,en){
    if(d.history?.verification?.status==='unverified')return [];
    const excluded=new Set(d.history?.excludedValueQuarters||[]),from=d.meta?.reportingTransition?.comparisonScopeChanged?d.meta.reportingTransition.fromQuarter:null;
    const quarters=[...new Set(d.history?.quarters||[])].filter(q=>quarter(q)!==null&&!excluded.has(q)&&(!from||quarter(q)>=quarter(from))&&valid(d.history?.holdings?.[q])&&sum(d.history.holdings[q])>0).sort((a,b)=>quarter(a)-quarter(b)).slice(-8);
    if(quarters.length<2)return [];
    const current=consolidateHoldings(d.current.holdings).sort((a,b)=>b.value-a.value).slice(0,8);
    return [section(en?'Core securities across available filings':'核心证券在历次可用披露中的轨迹',current.map(h=>{
      let count=0;const points=quarters.map(q=>{
        const rows=consolidateHoldings(d.history.holdings[q]),match=rows.find(p=>sameSecurity(h,p));if(match?.shares>0)count++;
        return `${q}: ${percent((match?.value||0)/sum(rows)*100)}%${match?` (${quantity(match.shares)} ${unit(h,en)})`:''}`;
      });
      return en?`${stock(h,en)} appears in ${count} of these ${quarters.length} available filings. ${points.join('; ')}. These are filing snapshots, not a record of every intervening trade.`:`${stock(h,en)} 在这 ${quarters.length} 份可用披露中出现 ${count} 次。${points.join('；')}。这里追踪的是披露时点的股数和占比，不能据此补出两次申报之间的逐笔交易。`;
    })),section(en?'Concentration through time':'每期组合集中度的变化',quarters.map(q=>{
      const rows=consolidateHoldings(d.history.holdings[q]).sort((a,b)=>b.value-a.value),total=sum(rows),top=rows.slice(0,3);
      return en?`${q}: ${money(total,en)} across ${rows.length} securities; the top three (${top.map(h=>h.ticker+(h.putCall?' '+h.putCall.toUpperCase():'')).join(', ')}) total ${percent(sum(top)/total*100)}%.`:`${q}：申报总值 ${money(total,en)}，共 ${rows.length} 项证券；前三项为 ${top.map(h=>stock(h,en)).join('、')}，合计 ${percent(sum(top)/total*100)}%。`;
    }))];
  }
  function html(sections,en){return `<details class="briefing-depth"><summary>${en?'Detailed numerical analysis':'展开详细数字分析'}</summary>${sections.map(s=>`<section><h4>${escape(s.heading)}</h4><ul>${s.items.map(text=>`<li>${escape(text)}</li>`).join('')}</ul></section>`).join('')}</details>`;}
  window.DisclosureAnalysis={value(candidates,en=false){
    if(!candidates?.length)return '';
    const labels=en?{new:'new entry',added:'added shares',trimmed:'reduced shares',hold:'shares unchanged'}:{new:'新进入披露',added:'股数增加',trimmed:'股数减少',hold:'股数未变'};
    const items=candidates.map(c=>{
      const holders=(c.investors||[]).map(h=>`${h.name||h.id}${(h.reportQuarter||h.quarter)?` (${h.reportQuarter||h.quarter})`:''}: ${labels[h.chg]||(en?'unverified change':'增减未核实')}${Number.isFinite(h.weight)?` · ${percent(h.weight)}%`:''}`).join(en?'; ':'；');
      const price=Number.isFinite(c.price)?'$'+c.price.toFixed(2):'—',cost=Number.isFinite(c.buy)?'$'+c.buy.toFixed(2):'—';
      return en?`${c.cnName||c.name||c.ticker} (${c.ticker}): price ${price}, historical cost reference ${cost}, gap ${c.mos}%. Qualifying holders: ${holders}. Holder weights refer to different portfolios and cannot be added.`:`${c.cnName||c.name||c.ticker} (${c.ticker})：参考股价 ${price}，历史加仓成本参考 ${cost}，价差 ${c.mos}%。达标持有者分别为：${holders}。各人的占比属于各自披露组合，不能相加；价差是相对历史成本的比较，不是相对企业内在价值的折价。`;
    });
    return html([section(en?'Candidate evidence and differing holder directions':'候选依据与各位持有者的不同方向',items)],en);
  },render(kind,d,en=false){
    if(!d?.current||d.meta?.snapshotType||d.current.valueQuality||!valid(d.current.holdings)||sum(d.current.holdings)<=0)return '';
    const sections=kind==='holdings'?holdings(d,en):kind==='changes'?changes(d,en):history(d,en);
    if(!sections.length)return '';
    return html(sections,en);
  }};
})();
