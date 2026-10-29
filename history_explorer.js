/* Complete filing history: immutable model, bounded tables, deterministic facts. */
(function(root){
'use strict';
const EVENT={id:'google-alphabet-class-c-2015',from:'38259P706',to:'02079K107',quarter:'2015 Q4',date:'2015-10-02',ratio:1,
  sources:['https://www.nasdaqtrader.com/TraderNews.aspx?id=dtn2015-21','https://www.sec.gov/Archives/edgar/data/1288776/000119312515336550/d56649d8k.htm']};
const idx=q=>{const m=/^(\d{4}) Q([1-4])$/.exec(q||'');return m?+m[1]*4+(+m[2]-1):null;};
const quarter=n=>Math.floor(n/4)+' Q'+(n%4+1);
const instrument=h=>[(h.putCall||'').toUpperCase(),(h.shareType||'SH').toUpperCase()].join('|');
const finite=n=>typeof n==='number'&&Number.isFinite(n)&&n>=0;
const escape=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const validURL=s=>/^https:\/\/(?:www\.)?(?:sec\.gov|nasdaqtrader\.com)\//.test(s||'');
function securityKey(h,q){
  // Economic continuity is explicitly dated and class-specific. Legal CUSIPs remain on each row.
  const date=idx(q),boundary=idx(EVENT.quarter);
  if(!h.putCall && (h.shareType||'SH').toUpperCase()==='SH' && /\bCL(?:ASS)?\s+C\b/i.test(h.cls||'') && ((h.cusip===EVENT.from && date<boundary)||(h.cusip===EVENT.to && date>=boundary)))return 'economic:'+EVENT.id;
  return JSON.stringify([h.cusip||[h.ticker,h.cls||''],instrument(h)]);
}
function model(snapshot,options={}){
  const history=snapshot.history||{},raw=history.holdings||{},keys=Object.keys(raw).filter(q=>idx(q)!==null).sort((a,b)=>idx(a)-idx(b));
  const disabled=history.verification?.status==='unverified'||snapshot.meta?.snapshotType||snapshot.meta?.portfolioMode==='public_projects';
  const quarters=keys.length?Array.from({length:idx(keys.at(-1))-idx(keys[0])+1},(_,i)=>quarter(idx(keys[0])+i)):[];
  const excluded=new Set(history.excludedValueQuarters||[]),securities=new Map(),reports=new Map();
  for(const q of keys){
    const positions=new Map();
    for(const row of raw[q]){
      const key=securityKey(row,q);let h=positions.get(key);
      if(!h){h={...row,key,sourceRows:[]};positions.set(key,h);}else{h.shares+=row.shares;h.value+=row.value;}
      h.sourceRows.push(row);
    }
    const rows=[...positions.values()],valueKnown=!excluded.has(q)&&rows.every(h=>finite(h.value)),total=valueKnown?rows.reduce((n,h)=>n+h.value,0):null;
    const ranked=valueKnown?[...rows].sort((a,b)=>b.value-a.value):[];
    ranked.forEach((h,i)=>{h.rank=i+1;h.weight=total>0?h.value/total*100:null;});
    reports.set(q,{quarter:q,positions,rows,valueKnown,total,top3:valueKnown&&total>0?ranked.slice(0,3).reduce((n,h)=>n+h.value,0)/total*100:null,top5:valueKnown&&total>0?ranked.slice(0,5).reduce((n,h)=>n+h.value,0)/total*100:null});
    for(const h of rows)if(h.shares>0){
      let security=securities.get(h.key);
      if(!security){security={key:h.key,first:q,last:q,row:h,quarters:[],legalIds:new Set(),peakShares:0};securities.set(h.key,security);}
      security.last=q;security.row=h;security.quarters.push(q);security.legalIds.add(h.cusip||'');security.peakShares=Math.max(security.peakShares,h.shares);
    }
  }
  const currentQuarter=keys.at(-1),boundary=snapshot.meta?.reportingTransition;
  function scopeChanged(h,q){return boundary?.comparisonScopeChanged&&boundary.fromQuarter===q&&!(options.sameManager?.(h));}
  function point(key,q){
    const report=reports.get(q);if(!report)return {quarter:q,status:'unknown',shares:null,value:null,weight:null,row:null};
    const h=report.positions.get(key),present=!!h&&h.shares>0;
    return {quarter:q,status:present?'disclosed':'absent',shares:h?.shares||0,value:report.valueKnown?(h?.value||0):null,weight:report.valueKnown&&report.total>0?(h?.value||0)/report.total*100:null,row:h||null,rank:h?.rank||null};
  }
  function change(key,q){
    const p=point(key,q),prevQ=quarter(idx(q)-1),prev=point(key,prevQ),security=securities.get(key),h=p.row||prev.row;
    const out={...p,previousQuarter:prevQ,previousShares:prev.shares,delta:null,weightDelta:null,kind:'unknown',corporateAction:false};
    if(p.status==='unknown'||prev.status==='unknown'||scopeChanged(h,q))return out;
    const linked=h&&key==='economic:'+EVENT.id&&q===EVENT.quarter;
    const actions=h?(options.actions?.(h)||[]):[];
    const action=linked || actions.some(a=>a.quarter===q) || !!p.row?.shareAdjustment;
    out.corporateAction=action;out.delta=p.shares-prev.shares;
    out.weightDelta=p.weight!==null&&prev.weight!==null?p.weight-prev.weight:null;
    if(action){out.kind='action';out.delta=null;return out;}
    if(prev.shares===0&&p.shares>0){
      const before=security?.quarters.filter(t=>idx(t)<idx(prevQ))||[];
      out.kind=before.length?'reappeared':'new';
    }else if(prev.shares>0&&p.shares===0)out.kind='absent';
    else if(p.shares>prev.shares)out.kind='increased';
    else if(p.shares<prev.shares)out.kind='decreased';
    else out.kind='unchanged';
    return out;
  }
  function series(key,from=quarters[0],to=quarters.at(-1)){
    return quarters.filter(q=>idx(q)>=idx(from)&&idx(q)<=idx(to)).map(q=>change(key,q));
  }
  function portfolio(q){
    const report=reports.get(q);if(!report)return {quarter:q,rows:[],known:false,previousQuarter:null};
    const previous=reports.get(quarter(idx(q)-1)),all=new Map(report.positions);
    if(previous)for(const [k,h]of previous.positions)if(!all.has(k))all.set(k,{...h,shares:0,value:0,weight:report.valueKnown?0:null,rank:null,sourceRows:[]});
    const rows=[...all].map(([key,h])=>({...h,...change(key,q),row:h,key,absent:h.shares===0}));
    return {...report,known:true,previousQuarter:previous?.quarter||null,rows};
  }
  function listed({query='',status='all',sort='value',direction='desc',page=0,size=50,q=currentQuarter}={}){
    const report=portfolio(q),needle=query.trim().toLowerCase(),maxSize=Math.min(100,Math.max(1,size));
    let rows=report.rows.filter(h=>(status==='all'||h.kind===status||(status==='held'&&h.shares>0))&&(!needle||[h.ticker,h.name,h.cnName,h.cls,h.cusip].join(' ').toLowerCase().includes(needle)));
    const sign=direction==='asc'?1:-1;
    rows.sort((a,b)=>{const x=sort==='ticker'?String(a.ticker).localeCompare(String(b.ticker)):(a[sort]??-Infinity)-(b[sort]??-Infinity);return (Number.isNaN(x)?0:x)*sign||String(a.key).localeCompare(String(b.key));});
    const total=rows.length,pages=Math.max(1,Math.ceil(total/maxSize)),safePage=Math.min(Math.max(0,page),pages-1);
    return {rows:rows.slice(safePage*maxSize,(safePage+1)*maxSize),total,page:safePage,pages,size:maxSize};
  }
  return {snapshot,history,disabled,quarters,keys,reports,securities,currentQuarter,point,change,series,portfolio,listed,event:EVENT};
}
const labels={unknown:['不可比 / 缺报','Unknown / no comparison'],new:['新出现','New disclosure'],reappeared:['重新出现','Reappeared'],absent:['未再披露','No longer disclosed'],increased:['股数增加','Shares increased'],decreased:['股数减少','Shares decreased'],unchanged:['股数不变','Shares unchanged'],action:['公司行动期，非净买卖','Corporate action; not net trades']};
let active=null;
function mount(container,snapshot,options={}){
  if(!container)return;
  const signature=options.investor+'|'+options.lang;
  if(active?.snapshot===snapshot&&active.signature===signature){active.render();return active;}
  const previous=active?.signature===signature?active.state:null;
  const m=model(snapshot,options),en=options.lang==='en',t=(zh,eng)=>en?eng:zh;
  const name=h=>[h.ticker?.replace(/^\?/,''),en?h.name:(h.cnName||h.name),h.cls,h.putCall].filter(Boolean).join(' · ');
  const number=n=>n===null||n===undefined?'—':Number(n).toLocaleString(en?'en-US':'zh-CN',{maximumFractionDigits:2});
  const percent=n=>n===null||n===undefined?'—':(n>0&&n<.1?'<0.1':Number(n.toFixed(2)))+'%';
  const money=n=>n===null||n===undefined?t('待核验','Unverified'):(options.currency||'US$')+number(n);
  const keyList=[...m.securities.values()].sort((a,b)=>(b.last===m.currentQuarter)-(a.last===m.currentQuarter)||b.last.localeCompare(a.last)||b.peakShares-a.peakShares);
  const state={mode:'security',key:keyList[0]?.key||'',q:m.currentQuarter,from:m.quarters[0],to:m.quarters.at(-1),metric:'shares',query:'',search:'',status:'all',sort:'value',direction:'desc',page:0,detailPage:0,concentrationPage:0,...previous};
  if(!m.securities.has(state.key))state.key=keyList[0]?.key||'';
  if(!m.reports.has(state.q))state.q=m.currentQuarter;
  const button=(text,field,value,extra='')=>`<button type="button" data-hx="${field}" data-value="${escape(value)}" ${extra}>${text}</button>`;
  const select=(field,title,choices,value)=>`<label>${title}<select id="hx-${field}" data-hx="${field}" aria-label="${escape(title)}">${choices.map(([v,label])=>`<option value="${escape(v)}" ${v===value?'selected':''}>${escape(label)}</option>`).join('')}</select></label>`;
  const paging=(page,pages,field)=>`<div class="hx-pages">${button(t('上一页','Previous'),field,page-1,page<=0?'disabled':'')}<span>${page+1} / ${pages}</span>${button(t('下一页','Next'),field,page+1,page>=pages-1?'disabled':'')}</div>`;
  const tag=kind=>`<span class="hx-change hx-${kind}">${escape(labels[kind]?.[en?1:0]||kind)}</span>`;
  function chart(points,field,title,other=null){
    const width=900,height=240,left=65,right=15,top=20,bottom=35,values=points.flatMap(p=>[p[field],...(other?[p[other]]:[])]).filter(finite),max=Math.max(...values,1)*1.06;
    const x=i=>left+i/Math.max(1,points.length-1)*(width-left-right),y=v=>height-bottom-v/max*(height-top-bottom);
    const lines=(metric,color)=>{let parts=[],current=[];points.forEach((p,i)=>{const value=p[metric];if(!finite(value)){if(current.length)parts.push(current);current=[];}else current.push([x(i),y(value),p]);});if(current.length)parts.push(current);
      return parts.map(part=>`<polyline fill="none" stroke="${color}" stroke-width="2" points="${part.map(([a,b])=>a.toFixed(2)+','+b.toFixed(2)).join(' ')}"/>`+part.map(([a,b,p])=>`<circle cx="${a}" cy="${b}" r="3" fill="${color}"><title>${escape(p.quarter+' '+(metric==='shares'?number(p[metric]):metric==='value'?money(p[metric]):percent(p[metric])))}</title></circle>`).join('')).join('');};
    return `<figure class="hx-chart"><figcaption>${escape(title)}</figcaption><svg viewBox="0 0 ${width} ${height}" role="img" aria-label="${escape(title)}"><title>${escape(title)}</title><line x1="${left}" y1="${height-bottom}" x2="${width-right}" y2="${height-bottom}" stroke="currentColor" opacity=".2"/><text x="5" y="28">${escape(field==='value'?(options.currency||'US$')+(max/1e6).toFixed(1)+'M':field==='shares'?number(max):max.toFixed(1)+'%')}</text><text x="20" y="${height-bottom}">0</text>${lines(field,'#254c62')}${other?lines(other,'#b78b4a'):''}<text x="${left}" y="${height-8}">${escape(points[0]?.quarter||'')}</text><text text-anchor="end" x="${width-right}" y="${height-8}">${escape(points.at(-1)?.quarter||'')}</text></svg><small>${t('断线＝缺报或该指标待核验；0＝该季有申报但未披露此证券。数表保留精确值。','Breaks = missing reports or unverified metric; zero = filed report without this security. Exact values are in the table.')}</small></figure>`;
  }
  function evidence(h,q){
    const source=m.history.filing_sources?.[q],url=source?.url;
    const rows=h?.sourceRows||[];
    let html=`<details class="hx-evidence"><summary>${t('原始申报、股份与管理权限','Filing, legal class and manager authority')}</summary>`;
    if(validURL(url))html+=`<a href="${escape(url)}" target="_blank" rel="noopener">${t('该季 SEC 原始申报','Original SEC filing')} ↗</a>`;
    for(const row of rows){
      html+=`<p>${escape(row.cusip||t('CUSIP 未采集','CUSIP unavailable'))} · ${escape(row.cls||'—')} · ${escape(instrument(row))}</p>`;
      if(row.reportedIdentity)html+=`<p>${t('保留原始身份','Reported identity')}: ${escape(JSON.stringify(row.reportedIdentity))}</p>`;
      if(row.identityEvidence){const link=row.identityEvidence.source?.url;html+=`<p>${escape(row.identityEvidence.method)} ${validURL(link)?`<a href="${escape(link)}" target="_blank" rel="noopener">${t('身份依据','Identity evidence')} ↗</a>`:''}</p>`;}
      const allocations=row.managerAllocations||[{investmentDiscretion:row.investmentDiscretion,votingAuthority:row.votingAuthority}];
      html+=allocations.map(a=>`<p>${t('申报管理人编号','Filed manager IDs')}: ${escape(a.managerIds?.join(', ')||t('未提供','Not supplied'))} · ${t('投资决定权限','Investment discretion')}: ${escape(a.investmentDiscretion||t('未采集','Not collected'))} · ${t('投票权','Voting authority')}: ${a.votingAuthority?escape(JSON.stringify(a.votingAuthority)):t('未采集','Not collected')}</p>`).join('');
    }
    if(!rows.length)html+=`<p>${t('该季未披露此证券；没有证券行可展示。','No security row was disclosed in this quarter.')}</p>`;
    return html+`<p>${t('机构申报不证明某个人亲自下单。未采集字段保持未知。','An institutional filing does not establish personal trading instructions. Uncollected fields remain unknown.')}</p></details>`;
  }
  function renderSecurity(){
    const security=m.securities.get(state.key);if(!security)return `<p>${t('没有匹配证券','No matching security')}</p>`;
    const selected=keyList.filter(s=>!state.search||(name(s.row)+' '+[...s.legalIds].join(' ')).toLowerCase().includes(state.search.toLowerCase())).slice(0,20);
    if(!selected.some(s=>s.key===state.key))selected.unshift(security);
    const points=m.series(state.key,state.from,state.to),last=m.point(state.key,m.currentQuarter),changes=points.filter(p=>p.kind==='increased'||p.kind==='decreased'),current=last.shares>0;
    const rows=points.slice(state.detailPage*24,(state.detailPage+1)*24),pages=Math.max(1,Math.ceil(points.length/24));
    const drift=points.filter(p=>p.kind==='unchanged'&&p.shares>0&&p.weightDelta!==null&&Math.abs(p.weightDelta)>.01);
    let run=[];
    for(let i=points.length-1;i>=0;i--){const p=points[i];if(!p.row||p.corporateAction||(run.length&&(p.shares!==run[0].shares||idx(run[0].quarter)-idx(p.quarter)!==1)))break;run.unshift(p);}
    const driftRun=run.length>=2&&run[0].weight!==null&&run.at(-1).weight!==null?`<p class="hx-note">${t('连续','Consecutive')} ${run.length} ${t('季股数均为','quarters with shares at')} ${number(run[0].shares)} (${run[0].quarter}–${run.at(-1).quarter}) · ${t('权重','weight')} ${percent(run[0].weight)} → ${percent(run.at(-1).weight)}。${t('权重变化不代表主动买卖。','Weight changes do not establish active trading.')}</p>`:'';
    const event=state.key==='economic:'+EVENT.id?`<aside class="hx-event">${t('2015-10-02：Google C 类股按 1:1 转换为 Alphabet C 类股。关联经济持仓，保留旧/新法定 CUSIP；不标为卖出再买入。','2015-10-02: Google class C converted 1:1 into Alphabet class C. Economic continuity is linked; both legal CUSIPs remain, without a fabricated exit/reentry.')} ${EVENT.sources.map((url,i)=>`<a href="${url}" target="_blank" rel="noopener">${i===0?'Nasdaq':'SEC'} ↗</a>`).join(' · ')}</aside>`:'';
    return `<div class="hx-controls"><label>${t('搜索全部历史证券（含已退出）','Search all historic securities, including exited')}<input id="hx-search" data-hx="search" type="search" value="${escape(state.search)}" placeholder="${t('代码、公司、CUSIP、股份类别','Ticker, company, CUSIP, class')}"/></label>${select('key',t('匹配证券（最多显示20个匹配项）','Matching securities (up to 20)'),selected.map(s=>[s.key,name(s.row)]),state.key)}${select('from',t('起始季度','From'),m.quarters.map(q=>[q,q]),state.from)}${select('to',t('结束季度','Through'),m.quarters.map(q=>[q,q]),state.to)}${select('metric',t('图表指标','Chart metric'),[['shares',t('申报股数／本金','Reported shares / principal')],['weight',t('申报组合权重','Reported portfolio weight')],['value',t('申报市值','Reported value')]],state.metric)}</div>
    <div class="hx-facts"><strong>${escape(name(security.row))}</strong><span>${current?t('当前披露持有','Currently disclosed'):t('最新申报未再披露','Not disclosed in latest filing')}</span><span>${t('首次披露','First disclosed')} ${security.first} · ${t('最后披露','Last disclosed')} ${security.last}</span><span>${t('已知季度股数变化','Known quarter share changes')}: ${changes.length} · ${t('股数未变而权重变化','Unchanged shares with weight drift')}: ${drift.length}</span></div>${driftRun}${event}${chart(points,state.metric,t('单证券逐季趋势','Quarterly security history'))}
    <p class="hx-note">${t('股数变化为申报快照差异，不能等同净买卖。权重变化也受价格和组合分母影响；申报市值变化不是收益率。股份拆分／重组季度单独标注。','Share changes are differences between filing snapshots, not net transactions. Weight also reflects prices and the portfolio denominator; reported-value changes are not returns. Split / reorganization quarters are marked separately.')}</p>
    <div class="hx-table"><table><thead><tr>${[t('季度','Quarter'),t('披露','Disclosure'),t('股数／本金','Shares / principal'),t('股数变化','Share change'),t('市值','Value'),t('权重','Weight'),t('权重变化','Weight change'),t('当季排名','Quarter rank'),t('状态／证据','Status / evidence')].map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${rows.map(p=>`<tr><td>${p.quarter}</td><td>${t(p.status==='unknown'?'缺报／未知':p.status==='absent'?'有申报，未披露':'已披露',p.status)}</td><td>${number(p.shares)}</td><td>${number(p.delta)}</td><td>${money(p.value)}</td><td>${percent(p.weight)}</td><td>${p.weightDelta===null?'—':number(p.weightDelta)+' pp'}</td><td>${p.rank||'—'}</td><td>${tag(p.kind)}${evidence(p.row,p.quarter)}</td></tr>`).join('')}</tbody></table></div>${paging(state.detailPage,pages,'detailPage')}`;
  }
  function renderPortfolio(){
    const report=m.portfolio(state.q),listing=m.listed({...state,query:state.query,q:state.q,size:50}),previous=report.previousQuarter;
    const groups={};for(const h of report.rows)groups[h.kind]=(groups[h.kind]||0)+1;
    const lastKnown=m.keys.filter(q=>idx(q)<idx(state.q)).at(-1);
    return `<div class="hx-controls">${select('q',t('历史季度（完整申报）','Quarter (complete filing)'),m.quarters.map(q=>[q,q+(m.reports.has(q)?'':t(' · 缺报',' · missing'))]),state.q)}<label>${t('搜索该季组合','Search quarter')}<input id="hx-query" type="search" data-hx="query" value="${escape(state.query)}"/></label>${select('status',t('筛选','Filter'),[['all',t('全部（含上季未再披露）','All, including disappeared')],['held',t('本季披露持有','Held this quarter')],...Object.entries(labels).map(([k,v])=>[k,v[en?1:0]])],state.status)}${select('sort',t('排序','Sort'),[['value',t('市值','Value')],['shares',t('股数','Shares')],['weight',t('权重','Weight')],['delta',t('股数变化','Share change')],['ticker',t('代码','Ticker')],['rank',t('重仓排名','Rank')]],state.sort)}${select('direction',t('方向','Direction'),[['desc',t('降序','Descending')],['asc',t('升序','Ascending')]],state.direction)}</div>
    <div class="hx-facts"><strong>${state.q} · ${report.known?report.positions.size:'—'} ${t('项已披露证券','disclosed securities')}</strong><span>${t('申报总值','Filed total')}: ${money(report.total)}</span><span>Top3 ${percent(report.top3)} · Top5 ${percent(report.top5)}</span></div>
    <p>${!report.known?t('本季缺报，不能当作零持仓。','This report is missing, not a zero portfolio.'):!report.valueKnown?t('本季持仓仍存在，市值尺度待核验；股数可看，金额、权重、排名不作已验证数据。','Holdings exist; value scale is unverified. Shares remain visible; value, weights and ranks are unavailable.'):''} ${previous?t('与相邻季度比较：','Adjacent quarter comparison: ')+previous:lastKnown?t('前一已知季为 ','Previous known report: ')+lastKnown+t('，中间缺报，不据此判断本季增减。','; intervening reports are missing, so no quarterly share-change claim is made.'):t('缺少相邻上季，变化未知。','No adjacent prior report; changes unknown.')}</p>
    <p class="hx-note">${Object.entries(groups).filter(([k])=>k!=='unchanged').map(([k,n])=>escape(labels[k]?.[en?1:0])+': '+n).join(' · ')} · ${t('完整组合，不受当前持仓Top50限制；每页最多50行。','Complete filing, independent of today’s Top 50; at most 50 rows per page.')}</p>
    <div class="hx-table"><table><thead><tr>${[t('排名／证券','Rank / security'),t('股数／本金','Shares / principal'),t('申报市值','Filed value'),t('组合权重','Weight'),t('股数变化','Share change'),t('状态','Status'),t('证据','Evidence')].map(x=>`<th>${x}</th>`).join('')}</tr></thead><tbody>${listing.rows.map(h=>`<tr><td>${h.rank||'—'} ${button(escape(name(h.row)),'open',h.key)}</td><td>${number(h.shares)}</td><td>${money(h.value)}</td><td>${percent(h.weight)}</td><td>${number(h.delta)}</td><td>${tag(h.kind)}</td><td>${evidence(h.row,state.q)}</td></tr>`).join('')}</tbody></table></div><p>${listing.total} ${t('项匹配','matches')}</p>${paging(listing.page,listing.pages,'page')}`;
  }
  function renderConcentration(){
    const points=m.quarters.map(q=>{const r=m.reports.get(q);return {quarter:q,top3:r?.top3??null,top5:r?.top5??null};}),pages=Math.max(1,Math.ceil(points.length/24)),slice=points.slice(state.concentrationPage*24,(state.concentrationPage+1)*24);
    return chart(points,'top3',t('Top3（蓝）／Top5（金）集中度，完整申报口径','Top 3 (blue) / Top 5 (gold), complete filings'),'top5')+`<p>${t('按证券类别分别排序，期权名义申报值可能影响分母；集中度不是收益率。经理申报范围改变时不把跳变当作投资行为。','Ranks keep security classes distinct; option reported notional values may affect the denominator. Concentration is not return. Manager scope changes are not trading signals.')}</p><div class="hx-table"><table><thead><tr><th>${t('季度','Quarter')}</th><th>Top3</th><th>Top5</th><th>${t('集中度变化','Change (pp)')}</th><th>${t('当季前三名','Top 3 securities')}</th></tr></thead><tbody>${slice.map(p=>{const r=m.reports.get(p.quarter),prev=m.reports.get(quarter(idx(p.quarter)-1)),scope=boundaryChange(p.quarter);const delta=p.top3!==null&&prev?.top3!==null&&prev?.top3!==undefined&&!scope?p.top3-prev.top3:null;return `<tr><td>${button(p.quarter,'quarter',p.quarter)}</td><td>${percent(p.top3)}</td><td>${percent(p.top5)}</td><td>${delta===null?'—':number(delta)+' pp'}</td><td>${r?.valueKnown?[...r.rows].sort((a,b)=>b.value-a.value).slice(0,3).map(h=>escape(h.ticker)+' '+percent(h.weight)).join(' · '):t('未知／待核验','Unknown / unverified')}${scope?' · '+t('申报范围变化','Scope changed'):''}</td></tr>`;}).join('')}</tbody></table></div>${paging(state.concentrationPage,pages,'concentrationPage')}`;
  }
  function boundaryChange(q){return snapshot.meta?.reportingTransition?.comparisonScopeChanged&&snapshot.meta.reportingTransition.fromQuarter===q;}
  function render(){
    const focus=container.ownerDocument?.activeElement,id=focus?.id,selection=focus?.selectionStart;
    if(m.disabled||!m.keys.length){container.innerHTML=`<p>${t('缺少可核验来源的历史快照，不绘制证券或组合趋势。','No source-verified historical snapshots; security and portfolio charts are unavailable.')}</p>`;return;}
    container.innerHTML=`<section class="hx-explorer"><h3>${t('历史研究台','History explorer')}</h3><p>${m.keys.length} ${t('个已申报季度','filed quarters')} · ${m.securities.size} ${t('个历史证券身份（含有据可查的经济延续）','historic security identities, including evidenced economic continuity')} · ${t('数据完整按需载入，表格分页','Complete history loaded on demand; paginated tables')}</p><nav class="hx-modes" aria-label="${t('历史研究视图','History views')}">${[['security',t('单股逐季','Security')],['portfolio',t('任意季度完整组合','Full quarterly portfolio')],['concentration',t('重仓与集中度','Concentration')]].map(([k,n])=>button(n,'mode',k,`aria-pressed="${state.mode===k}"`)).join('')}</nav>${state.mode==='portfolio'?renderPortfolio():state.mode==='concentration'?renderConcentration():renderSecurity()}</section>`;
    if(id){const field=container.querySelector('#'+id);if(field){field.focus({preventScroll:true});if(typeof selection==='number'&&field.setSelectionRange&&field.type==='search')field.setSelectionRange(selection,selection);}}
  }
  function update(field,value){
    if(field==='open'){state.key=value;state.mode='security';state.detailPage=0;}else if(field==='quarter'){state.q=value;state.mode='portfolio';state.page=0;}else{
      state[field]=['page','detailPage','concentrationPage'].includes(field)?Math.max(0,+value):value;
      if(field==='search'){
        const matches=keyList.filter(s=>(name(s.row)+' '+[...s.legalIds].join(' ')).toLowerCase().includes(value.toLowerCase()));
        if(matches.length&&!matches.some(s=>s.key===state.key))state.key=matches[0].key;
      }
      if(['q','query','status','sort','direction'].includes(field))state.page=0;
      if(['key','from','to','search'].includes(field))state.detailPage=0;
      if(idx(state.from)>idx(state.to)){if(field==='from')state.to=state.from;else state.from=state.to;}
    }
    render();
  }
  container.onclick=e=>{const button=e.target.closest?.('button[data-hx]');if(button&&!button.disabled)update(button.dataset.hx,button.dataset.value);};
  container.onchange=e=>{if(e.target.dataset.hx)update(e.target.dataset.hx,e.target.value);};
  container.oninput=e=>{if(['search','query'].includes(e.target.dataset.hx))update(e.target.dataset.hx,e.target.value);};
  active={snapshot,signature,state,model:m,render,update,container};render();return active;
}
const api={model,securityKey,event:EVENT,mount,select:key=>{if(active){active.update('open',key);active.container.scrollIntoView?.({behavior:'smooth',block:'start'});}},get active(){return active;},idx,quarter};
root.HistoryExplorer=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
