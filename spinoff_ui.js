/* Shared HK/US research dashboard. Only explicit event evidence drives status. */
'use strict';
const spinDash = {
  hk: {data:null, query:'', view:'all', status:'all', type:'all', sort:'latest', request:0},
  us: {data:null, query:'', view:'all', status:'all', type:'all', sort:'latest', request:0},
};
const spinStatusText = {
  needs_review:['待核实','Needs review'], announced:['计划 / 建议','Planned'],
  approved:['公告称获批','Approval announced'], record_set:['已定记录日','Record date set'],
  prospectus:['招股文件','Prospectus'], completed:['公告称已完成','Completion announced'],
  terminated:['公告称终止','Termination announced'],
  paused:['暂不推进','On hold'],
};
const spinEscape = value => String(value ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
const spinLabel = (zh,en) => lang === 'en' ? en : zh;
const spinStatus = key => (spinStatusText[key] || spinStatusText.needs_review)[lang === 'en' ? 1 : 0];
function spinURL(value) {
  try { const u = new URL(value); return u.protocol === 'https:' && !u.username && !u.password ? u.href : ''; }
  catch { return ''; }
}
function spinLink(url, text) {
  const safe = spinURL(url);
  return safe ? `<a href="${spinEscape(safe)}" target="_blank" rel="noopener noreferrer">${spinEscape(text)} ↗</a>` : `<span>${spinEscape(text)}</span>`;
}
let spinStorageFailed = false;
function spinPrefs() {
  try {
    const value = JSON.parse(localStorage.getItem('spinoff-research-v1') || '{}');
    return value && typeof value === 'object' && !Array.isArray(value) ? value : {};
  } catch { spinStorageFailed = true; return {}; }
}
function spinSave(id, patch) {
  try {
    const prefs = spinPrefs();
    prefs[id] = {...prefs[id], ...patch};
    localStorage.setItem('spinoff-research-v1', JSON.stringify(prefs));
    spinStorageFailed = false;
    return true;
  } catch { spinStorageFailed = true; return false; }
}
function spinDate(value) { return /^\d{4}-\d{2}-\d{2}$/.test(value || '') ? Date.parse(value + 'T00:00:00Z') : NaN; }
function spinUpcoming(e, now=Date.now()) {
  const day = Math.floor(now / 86400000) * 86400000;
  if (['completed','terminated','paused'].includes(e.status)) return [];
  return Object.entries(e.dates || {}).filter(([,v]) => spinDate(v.date) >= day && spinDate(v.date) <= day + 30*86400000).sort((a,b)=>a[1].date.localeCompare(b[1].date));
}
function spinRecent(value, days, now=Date.now()) {
  const time = Date.parse(value || ''); return Number.isFinite(time) && time <= now && time >= now-days*86400000;
}
function spinBaseEvents(state) {
  const q = state.query.trim().toLocaleLowerCase();
  return (state.data?.events || []).filter(e => {
    const search = [e.parentTicker,e.parentName,e.targetName,e.targetTicker].join(' ').toLocaleLowerCase();
    const isReit = typeof e.type === 'object' ? e.type.is_reit || /reit/i.test(e.type.code || '') : /reit/i.test(e.type || '');
    return (!q || search.includes(q)) && (state.type === 'all' || (state.type === 'reit' ? isReit : !isReit));
  });
}
function spinVisible(state, prefs, now=Date.now()) {
  const changes = new Set((state.data?.changes || []).filter(c=>spinRecent(c.at,7,now)).map(c=>c.eventId));
  return spinBaseEvents(state).filter(e => {
    if (state.status !== 'all' && e.status !== state.status) return false;
    switch (state.view) {
      case 'watch': return !!prefs[e.id]?.watch;
      case 'review': return e.missing.length > 0 || !e.identityVerified;
      case 'upcoming': return spinUpcoming(e,now).length > 0;
      case 'completed': return e.status === 'completed' && spinRecent(e.evidence?.date,90,now);
      case 'changes': return changes.has(e.id);
      case 'unread': return prefs[e.id]?.read !== e.fingerprint;
      default: return true;
    }
  }).sort((a,b)=>state.sort === 'name' ? a.parentTicker.localeCompare(b.parentTicker) : state.sort === 'upcoming' ?
    (spinUpcoming(a,now)[0]?.[1].date || '9999').localeCompare(spinUpcoming(b,now)[0]?.[1].date || '9999') : b.latestDate.localeCompare(a.latestDate));
}
function spinDateLabel(key) { return key === 'listingDate' ? spinLabel('上市日','Listing date') : key === 'recordDate' ? spinLabel('记录日','Record date') : spinLabel('分派日','Distribution date'); }
function spinPct(value) { return typeof value === 'number' && Number.isFinite(value) ? `${value>0?'+':''}${value.toFixed(1)}%` : '—'; }
function spinPrices(e) {
  const pairs = Array.isArray(e.pricePairs) ? e.pricePairs : [];
  const parent = e.parentPrice || {};
  if (!pairs.length && typeof parent.changePct !== 'number') return '';
  return `<section class="sd-section"><h4>${spinLabel('价格参考','Price reference')}</h4><p class="sd-muted">${spinLabel('价格变动不是母子公司合计收益；历史行情配对尚需核对，不用于判断事件完成或强制卖压。','Price moves are not combined parent/child returns. Legacy price mappings need verification and do not establish completion or forced selling.')}</p>
    ${typeof parent.changePct === 'number' ? `<p>${spinLabel('关联公司参考区间变动','Issuer reference-period move')}: <b>${spinPct(parent.changePct)}</b> · ${spinEscape(parent.firstAnnouncementDate || parent.startDate || '—')} → ${spinEscape(parent.updatedAt || '—')}</p>` : ''}
    ${pairs.map(p=>`<p>${spinEscape(p.spinoffName || p.spinoff || '')} <span class="sd-muted">${spinEscape(p.spinoff || '')}</span> · ${spinPct(p.spinoffChangePct)} · ${spinEscape(p.currency || '')} · ${spinLabel('参考起始日','Reference start')} ${spinEscape(p.spinoffDate || '—')}</p>`).join('')}
  </section>`;
}
function spinIssuerName(e) {
  const name=String(e?.parentName || '').trim(), suffix=`(${e?.parentTicker || ''})`;
  return name.endsWith(suffix) ? name.slice(0,-suffix.length).trim() : name;
}
function spinTypeName(type) {
  if (type && typeof type==='object') return type[lang==='en'?'label_en':'label_zh'] || type.code || '';
  const labels={spinoff:['分拆','Spin-off'],carveout:['分拆上市','Equity carve-out'],splitoff:['换股分拆','Split-off']};
  return labels[type]?.[lang==='en'?1:0] || type || '';
}
function spinUpdatedTime(value) {
  if (!value || !Number.isFinite(Date.parse(value))) return spinLabel('暂无更新时间','Update time unavailable');
  if (value.length===10) return value;
  return new Date(Date.parse(value)+8*3600000).toISOString().slice(0,16).replace('T',' ')+' (UTC+8)';
}
function spinGaps(e) {
  const labels={target:spinLabel('标的名称','target name'),ticker:spinLabel('标的代码','target ticker'),evidence:spinLabel('状态依据','status evidence'),recordDate:spinLabel('记录日','record date'),distributionDate:spinLabel('分派日','distribution date')};
  const items=(e.missing || []).map(k=>labels[k]).filter(Boolean);
  if (!e.identityVerified) items.push(spinLabel('公司对应关系','issuer relationship'));
  return items.length ? spinLabel('待补全 / 核实：','Missing / to verify: ')+items.join('、') : spinLabel('基础资料已收录，仍需核对原文','Core fields available; review original sources');
}
function spinChangeDescription(c,e) {
  const lines=[], fields=c.fields || [], before=c.before, after=c.after;
  if (c.kind==='new') {
    lines.push(spinLabel('新收录分拆线索','New spin-off lead'));
    const target=after?.targetName || e?.targetName;
    if (target) lines.push(spinLabel('分拆标的：','Target: ')+target);
    lines.push(spinLabel('当前记录状态：','Recorded status: ')+spinStatus(c.toStatus));
    return lines.join('；');
  }
  if (fields.includes('status') && c.fromStatus!==c.toStatus)
    lines.push(spinLabel('状态更新：','Status updated: ')+spinStatus(c.fromStatus)+' → '+spinStatus(c.toStatus));
  for (const [key,label] of [['targetName',spinLabel('分拆标的','Target')],['targetTicker',spinLabel('标的代码','Target ticker')]]) {
    if (!fields.includes(key)) continue;
    if (before && after) {
      if (!after[key]) lines.push(label+spinLabel('：原标注已移除，待核实',': previous entry removed; needs verification'));
      else if (!before[key]) lines.push(spinLabel('补充','Added ')+label+': '+after[key]);
      else lines.push(label+': '+before[key]+' → '+after[key]);
    } else {
      // Legacy records did not retain old values; never present today's value as a historical change.
      lines.push(label+spinLabel('信息已调整（未保存修改前内容）',' information updated (previous value not saved)'));
      if (e?.[key]) lines.push(spinLabel('当前记录：','Current record: ')+e[key]);
      else lines.push(spinLabel('当前待核实','Currently unverified'));
    }
  }
  if (fields.includes('dates')) {
    if (before && after) {
      for (const key of new Set([...Object.keys(before.dates || {}),...Object.keys(after.dates || {})])) {
        const from=before.dates?.[key],to=after.dates?.[key];
        if (from===to) continue;
        lines.push(spinDateLabel(key)+': '+(from || spinLabel('未记录','Not recorded'))+' → '+(to || spinLabel('待核实','Needs verification')));
      }
    } else lines.push(spinLabel('关键日期记录已调整，展开档案查看当前日期','Key-date records updated; open the dossier for current dates'));
  }
  return lines.join('；');
}
function spinRecentChanges(data,now=Date.now()) {
  return (data.changes || []).slice().reverse().filter(c=>spinRecent(c.at,7,now) && (c.kind==='new' || (c.fields || []).length>0))
    .sort((a,b)=>b.at.localeCompare(a.at));
}
function spinChangesHTML(data, expanded=false) {
  const all=spinRecentChanges(data), changes=expanded?all:all.slice(0,3);
  if (!changes.length) return `<p class="sd-muted">${spinLabel('暂无记录到的实质变化。追踪开始于','No meaningful changes recorded. Tracking began')} ${spinEscape((data.trackingStartedAt || '').slice(0,10))}${spinLabel('；首次整理不会将全部历史事件标为新增。','; initial imports are not counted as new events.')}</p>`;
  return `<p class="sd-muted">${spinLabel('日期为系统记录更新时间；点击公司名称可查看档案。','Dates show when updates were recorded. Select a company to open its dossier.')}</p><ul>${changes.map(c=>{
    const e=data.events.find(e=>e.id===c.eventId), ticker=c.parentTicker || e?.parentTicker || String(c.eventId).split(':')[1] || '', name=c.parentName || spinIssuerName(e);
    const identity=`<strong>${spinEscape(name || spinLabel('公司名称待补全','Company name unavailable'))}</strong><span class="sd-change-ticker">${spinEscape(ticker)}</span>`;
    return `<li><time>${spinEscape(c.at.slice(0,10))}</time><div class="sd-change-body">${e?`<button class="sd-change-company" data-action="open-event" data-open-event="${spinEscape(e.id)}">${identity}</button>`:`<div>${identity}</div>`}<p>${spinEscape(spinChangeDescription(c,e))}</p></div></li>`;
  }).join('')}</ul>${all.length>3?`<button class="sd-more" data-action="more-changes">${expanded?spinLabel('收起','Show less'):spinLabel(`查看全部 ${all.length} 条变化`,`View all ${all.length} changes`)}</button>`:''}`;
}

function spinCard(e, pref={}) {
  const unknown = spinLabel('待核实','To verify');
  const evidence = e.evidence;
  const dates = Object.entries(e.dates || {});
  const related = e.announcements.filter(a=>a.relevance !== 'unverified');
  const unverified = e.announcements.filter(a=>a.relevance === 'unverified');
  const announcementHTML = list => list.map(a=>`<li><time>${spinEscape(a.date)}</time><div>${spinLink(a.url,a.title)}${!a.direct ? `<small>${spinLabel('公司公告目录，尚未定位原文','Company filing list; original document not yet resolved')}</small>` : ''}</div></li>`).join('');
  const type = spinTypeName(e.type);
  const gapCount=(e.missing || []).length+(e.identityVerified?0:1);
  return `<article class="sd-card ${pref.read === e.fingerprint ? 'sd-read' : ''}" data-event="${spinEscape(e.id)}">
    <button class="sd-watch" data-action="watch" aria-label="${spinEscape(spinLabel('自选：','Watch: ')+(spinIssuerName(e) || e.parentTicker))}" title="${spinLabel('加入 / 取消自选','Toggle watchlist')}" aria-pressed="${!!pref.watch}">${pref.watch?'★':'☆'}</button>
    <details class="sd-dossier"><summary>
      <div class="sd-identity"><span class="sd-company" title="${spinEscape(spinIssuerName(e))}">${spinEscape(spinIssuerName(e) || e.parentTicker)}</span><span class="sd-symbol">${spinEscape(e.parentTicker)} <span class="sd-unread">${spinLabel('未读','Unread')}</span></span></div>
      <div class="sd-target" title="${spinEscape(e.targetName || unknown)}"><b><span class="sd-mobile-label">${spinLabel('分拆标的：','Target: ')}</span>${spinEscape(e.targetName || spinLabel('名称待核实','Name to verify'))}</b><small>${spinEscape(type)}${e.targetTicker?' · '+spinEscape(e.targetTicker):''}</small></div>
      <div class="sd-row-meta"><span class="sd-status sd-${spinEscape(e.status)}">${spinStatus(e.status)}</span><small title="${spinEscape(spinGaps(e))}">${gapCount?spinLabel(`待补全 / 核实 ${gapCount} 项`,`${gapCount} fields to verify`):spinLabel('基础资料已收录','Core fields available')}</small></div>
      <time class="sd-row-date"><span class="sd-mobile-label">${spinLabel('最新公告：','Latest filing: ')}</span>${spinEscape(e.latestDate || '—')}</time>
      <span class="sd-expand" aria-label="${spinLabel('展开档案','Expand dossier')}">⌄</span>
    </summary>
      <div class="sd-detail"><p class="sd-gaps">${spinEscape(spinGaps(e))}</p><div class="sd-facts"><div><span>${spinLabel('申报 / 关联公司','Filing / related issuer')}</span><b>${spinEscape(spinIssuerName(e))}</b><small>${spinEscape(e.parentTicker)}</small></div><div><span>${spinLabel('分拆标的 / 代码','Target / ticker')}</span><b>${spinEscape(e.targetName || unknown)}</b><small>${spinEscape(e.targetTicker || spinLabel('代码待核实','Ticker to verify'))}</small></div><div><span>${spinLabel('实体对应关系','Entity mapping')}</span><b>${e.identityVerified ? spinLabel('原文规则提取，待人工复核','Extracted from filing; review needed') : unknown}</b></div><div><span>${spinLabel('关联公司参考市值','Issuer reference cap')}</span><b>${typeof e.parentMarketCap === 'number' ? (lang==='en'?`$${(e.parentMarketCap/10).toFixed(2)}B`:`${e.parentMarketCap.toFixed(1)} 亿美元`) : '—'}</b><small>${spinLabel('缓存快照，非实时','Cached snapshot, not live')}</small></div></div>
      <section class="sd-section"><h4>${spinLabel('状态依据','Status evidence')}</h4>${evidence ? `<blockquote>${spinEscape(evidence.quote)}</blockquote><p>${spinEscape(evidence.date)} · ${spinLink(evidence.url,spinLabel('查看来源','View source'))} · ${spinLabel('规则提取，需复核全文与标的','Rule extraction; review full context and target')}</p>` : `<p class="sd-muted">${spinLabel('尚无足够的具体公告证据。历史标签与预定日期不作为完成依据。','Insufficient document evidence. Legacy labels and scheduled dates do not establish completion.')}</p>`}</section>
      <section class="sd-section"><h4>${spinLabel('关键日期','Key dates')}</h4>${dates.length ? dates.map(([k,v])=>`<p><b>${spinDateLabel(k)} · ${spinEscape(v.date)}</b> <span class="sd-muted">${v.kind==='actual'?spinLabel('公告确认已发生','Confirmed in filing'):spinLabel('计划日期，可能调整','Scheduled; subject to change')}</span> ${spinLink(v.url,spinLabel('依据','Source'))}</p>`).join('') : `<p class="sd-muted">${spinLabel('记录日、分派日：暂无可靠来源。','Record and distribution dates: no reliable source yet.')}</p>`}</section>
      ${spinPrices(e)}
      ${e.market === 'hk' ? `<section class="sd-section"><h4>${spinLabel('历史股东披露','Historical ownership disclosures')}</h4><button data-action="ownership">${spinLabel('加载历史记录','Load historical records')}</button><div class="sd-ownership"></div></section>` : ''}
      <section class="sd-section"><h4>${spinLabel('研究待办','Research checklist')}</h4><p>${spinLabel('核对母子公司对应关系、分派比例、债务与现金流、管理层持股，以及机构持仓变化。暂无来源的项目不自动打分。','Verify parent/child identity, distribution ratio, debt and cash flow, management ownership, and institutional holdings. Missing evidence is not automatically scored.')}</p></section>
      <section class="sd-section"><h4>${spinLabel('公告记录','Source documents')} <small>${related.length}</small></h4><ul class="sd-sources">${announcementHTML(related)}</ul>${unverified.length ? `<details class="sd-legacy"><summary>${spinLabel('历史导入记录：分拆相关性未核实','Legacy imports: relevance unverified')} (${unverified.length})</summary><ul class="sd-sources">${announcementHTML(unverified)}</ul></details>` : ''}</section>
      <section class="sd-section"><label class="sd-note-label">${spinLabel('研究笔记','Research notes')}<textarea data-action="note" rows="3" maxlength="5000" placeholder="${spinLabel('记录需要核实的问题…','Questions to verify…')}">${spinEscape(pref.note || '')}</textarea></label><small class="sd-note-result" role="status">${spinLabel('笔记与自选仅保存在此浏览器。输入时自动保存。','Notes and watchlist stay in this browser. Notes save as you type.')}</small></section></div>
    </details></article>`;
}
function spinRenderList(market) {
  const state = spinDash[market], root = document.getElementById(market === 'hk' ? 'spinoffContent' : 'spinoffUSContent');
  const prefs = spinPrefs(), events = spinVisible(state,prefs), base = spinBaseEvents(state);
  root.querySelector('.sd-results').innerHTML = events.length ? `<div class="sd-list-head"><span>${spinLabel('公司 / 代码','Company / ticker')}</span><span>${spinLabel('分拆标的 / 类型','Target / type')}</span><span>${spinLabel('进度 / 资料','Status / data')}</span><span>${spinLabel('最新公告','Latest filing')}</span><span></span></div>`+events.map(e=>spinCard(e,prefs[e.id])).join('') : `<div class="sd-empty">${spinLabel('暂无符合条件的事件。可清空搜索或调整筛选。','No matching events. Clear the search or adjust filters.')}</div>`;
  root.querySelector('.sd-count').textContent = spinLabel(`显示 ${events.length} / ${base.length} 个档案`,`Showing ${events.length} / ${base.length} dossiers`);
  root.querySelectorAll('[data-view]').forEach(b=>{ b.setAttribute('aria-pressed',String(state.view===b.dataset.view)); });
  const counts = {all:base.length,watch:base.filter(e=>prefs[e.id]?.watch).length,review:base.filter(e=>e.missing.length || !e.identityVerified).length,upcoming:base.filter(e=>spinUpcoming(e).length).length};
  root.querySelectorAll('[data-count]').forEach(e=>{ e.textContent=counts[e.dataset.count]; });
  root.querySelector('.sd-storage').hidden = !spinStorageFailed;
  root.querySelectorAll('.sd-dossier').forEach(details=>details.addEventListener('toggle',()=>{
    if (!details.open) return;
    const card = details.closest('[data-event]'), e = state.data.events.find(e=>e.id === card.dataset.event);
    if (spinSave(e.id,{read:e.fingerprint})) card.classList.add('sd-read');
    root.querySelector('.sd-storage').hidden = !spinStorageFailed;
  }));
}
function spinPaint(market) {
  const state = spinDash[market], root = document.getElementById(market === 'hk' ? 'spinoffContent' : 'spinoffUSContent');
  const data = state.data;
  const viewNames = {all:spinLabel('全部档案','All dossiers'),watch:spinLabel('我的自选','Watchlist'),review:spinLabel('资料待补全','Incomplete dossiers'),upcoming:spinLabel('未来 30 天','Next 30 days')};
  root.innerHTML = `<div class="sd-dashboard"><header class="sd-header"><div><p class="sd-eyebrow">${spinLabel('分拆研究工作台','SPIN-OFF RESEARCH')}</p><h2>${market==='hk'?spinLabel('港股分拆','Hong Kong spin-offs'):spinLabel('美股分拆','US spin-offs')}</h2><p class="sd-muted">${spinLabel('先看变化，再核对证据，持续跟踪值得研究的事件。','Track changes, inspect evidence, and follow the events worth researching.')}</p></div><button data-action="refresh">↻ ${spinLabel('刷新数据','Refresh data')}</button></header>
    <p class="sd-updated">${spinLabel('来源数据更新','Source data updated')}: ${spinEscape(spinUpdatedTime(data.updatedAt))} · ${spinLabel('不依赖 AI 摘要判断状态','Status does not depend on AI summaries')}</p>
    <p class="sd-error" role="status" ${state.error?'':'hidden'}>${spinLabel('刷新失败，仍显示上次成功加载的数据。请重试。','Refresh failed. Showing the last successfully loaded data. Please retry.')}</p>
    <p class="sd-storage" role="status" hidden>${spinLabel('浏览器存储不可用，自选和笔记暂时无法保存。','Browser storage is unavailable; watchlist and notes cannot be saved.')}</p>
    <div class="sd-kpis">${Object.entries(viewNames).map(([key,label])=>`<button data-view="${key}" aria-pressed="${state.view===key}"><span>${label}</span><b data-count="${key}">0</b>${key==='review'?`<small>${spinLabel('名称、日期或对应关系尚不完整','Missing names, dates or relationship evidence')}</small>`:''}</button>`).join('')}</div>
    <section class="sd-changes"><h3>${spinLabel('近 7 天的实质变化','Meaningful changes · last 7 days')}</h3><div class="sd-change-content">${spinChangesHTML(data,state.changesExpanded)}</div></section>
    <div class="sd-controls"><label class="sd-search">${spinLabel('搜索','Search')}<input type="search" data-filter="query" value="${spinEscape(state.query)}" placeholder="${spinLabel('公司、标的或股票代码','Issuer, target or ticker')}"></label><label>${spinLabel('状态','Status')}<select data-filter="status"><option value="all">${spinLabel('全部状态','All statuses')}</option>${Object.keys(spinStatusText).map(k=>`<option value="${k}">${spinStatus(k)}</option>`).join('')}</select></label><label>${spinLabel('类型','Type')}<select data-filter="type"><option value="all">${spinLabel('全部（含 REIT）','All (including REITs)')}</option><option value="reit">REIT</option><option value="other">${spinLabel('非 REIT','Non-REIT')}</option></select></label><label>${spinLabel('排序','Sort')}<select data-filter="sort"><option value="latest">${spinLabel('最新公告','Latest filing')}</option><option value="upcoming">${spinLabel('临近日期优先','Upcoming date')}</option><option value="name">${spinLabel('股票代码','Ticker')}</option></select></label></div>
    <div class="sd-views">${[['unread',spinLabel('未读 / 有更新','Unread / updated')],['changes',spinLabel('近期变化','Recent changes')],['completed',spinLabel('近 90 天完成公告','Completion filings · 90 days')]].map(([k,label])=>`<button data-view="${k}" aria-pressed="${state.view===k}">${label}</button>`).join('')}<button data-action="reset">${spinLabel('重置筛选','Reset filters')}</button><span class="sd-count" aria-live="polite"></span></div><div class="sd-results"></div>
    <p class="sd-footer">${spinLabel('采集范围内的研究线索，并非全部分拆事件。计划日期可能变化，最终以公司公告为准。','Research leads within collection coverage, not an exhaustive event list. Scheduled dates may change; consult issuer filings.')}</p></div>`;
  for (const key of ['status','type','sort']) root.querySelector(`[data-filter="${key}"]`).value=state[key];
  root.oninput = event=>{
    if (event.target.dataset.filter === 'query') { state.query=event.target.value; spinRenderList(market); }
    if (event.target.dataset.action === 'note') {
      const id=event.target.closest('[data-event]').dataset.event;
      const saved=spinSave(id,{note:event.target.value});
      event.target.parentElement.nextElementSibling.textContent=saved?spinLabel('已保存到此浏览器','Saved in this browser'):spinLabel('保存失败，请保留笔记后重试','Save failed; keep your note and retry');
      root.querySelector('.sd-storage').hidden=!spinStorageFailed;
    }
  };
  root.onchange = event=>{ const key=event.target.dataset.filter; if (key && key!=='query') { state[key]=event.target.value; spinRenderList(market); } };
  root.onclick = event=>{
    const button=event.target.closest('button'); if (!button) return;
    if (button.dataset.view) { state.view=button.dataset.view; spinRenderList(market); }
    if (button.dataset.action==='more-changes') { state.changesExpanded=!state.changesExpanded; root.querySelector('.sd-change-content').innerHTML=spinChangesHTML(data,state.changesExpanded); }
    if (button.dataset.action==='open-event') {
      const id=button.dataset.openEvent;
      Object.assign(state,{query:'',view:'all',status:'all',type:'all'}); spinPaint(market);
      const card=Array.from(root.querySelectorAll('[data-event]')).find(e=>e.dataset.event===id);
      const details=card?.querySelector('.sd-dossier');
      if (details) { details.open=true; details.querySelector('summary').focus({preventScroll:true}); card.scrollIntoView({block:'start',behavior:'smooth'}); }
    }
    if (button.dataset.action==='ownership') spinLoadOwnership(button);
    if (button.dataset.action==='refresh') renderSpinoffDashboard(market,true);
    if (button.dataset.action==='reset') { Object.assign(state,{query:'',view:'all',status:'all',type:'all',sort:'latest'}); spinPaint(market); }
    if (button.dataset.action==='watch') {
      const id=button.closest('[data-event]').dataset.event, watch=!spinPrefs()[id]?.watch;
      if (spinSave(id,{watch})) { button.setAttribute('aria-pressed',String(watch)); button.textContent=watch?'★':'☆'; if (state.view==='watch') spinRenderList(market); else root.querySelector('[data-count="watch"]').textContent=spinBaseEvents(state).filter(e=>spinPrefs()[e.id]?.watch).length; }
      root.querySelector('.sd-storage').hidden=!spinStorageFailed;
    }
  };
  spinRenderList(market);
}
async function renderSpinoffDashboard(market, refresh=false) {
  const state=spinDash[market], root=document.getElementById(market==='hk'?'spinoffContent':'spinoffUSContent');
  if (!root) return;
  if (state.data && !refresh) { spinPaint(market); return; }
  const request=++state.request;
  state.controller?.abort(); const controller=new AbortController(); state.controller=controller;
  const timer=setTimeout(()=>controller.abort(),20000);
  if (!state.data) root.innerHTML=`<div class="sd-empty" role="status">${spinLabel('加载分拆档案…','Loading spin-off dossiers…')}</div>`;
  else { const b=root.querySelector('[data-action="refresh"]'); if(b) { b.disabled=true; b.textContent=spinLabel('刷新中…','Refreshing…'); } }
  try {
    const resp=await fetch(`${market==='hk'?'spinoff':'spinoff_us'}.json?t=${Date.now()}`,{cache:'no-store',signal:controller.signal});
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const value=await resp.json();
    if (value.eventsSchemaVersion!==1 || !Array.isArray(value.events)) throw new Error('Unsupported spin-off schema');
    if (state.request!==request) return;
    state.data=value; state.error=false; spinPaint(market);
  } catch {
    if (state.request!==request) return;
    state.error=true;
    if (state.data) spinPaint(market);
    else { root.innerHTML=`<div class="sd-empty" role="alert">${spinLabel('分拆档案加载失败。','Could not load spin-off dossiers.')} <button>${spinLabel('重试','Retry')}</button></div>`; root.querySelector('button').onclick=()=>renderSpinoffDashboard(market,true); }
  } finally { clearTimeout(timer); }
}

async function spinLoadOwnership(button) {
  const card=button.closest('[data-event]'), code=card.dataset.event.split(':')[1];
  const result=card.querySelector('.sd-ownership');
  button.disabled=true;
  const controller=new AbortController(), timer=setTimeout(()=>controller.abort(),15000);
  try {
    const resp=await fetch(code==='00308'?'guo_haiqing.json':'spinoff_shareholder_history.json',{signal:controller.signal});
    if (!resp.ok) throw new Error('Ownership fetch failed');
    const raw=await resp.json(), value=code==='00308'?raw:raw.companies?.[code];
    if (!value) { result.textContent=spinLabel('暂无该公司的历史记录。','No historical records for this company.'); return; }
    result.innerHTML=`<p><b>${spinEscape(lang==='en' ? value.shareholder_en || value.shareholder : value.shareholder)}</b> · ${spinLabel('记录截至','Records as of')} ${spinEscape(value.last_updated)}</p><p class="sd-muted">${spinLabel('历史呈报快照，不代表当前持股。比例变动不一定属于买卖。','Historical filing snapshots, not current ownership. Percentage changes do not necessarily reflect trades.')}</p><ul class="sd-sources">${(value.records || []).map(r=>`<li><time>${spinEscape(r.date)}</time><div>${spinEscape(r.type)} · ${spinLabel('股数变动','Share change')}: ${r.change == null ? '—' : spinEscape((r.change>0?'+':'')+r.change.toLocaleString())} · ${spinEscape(r.pct ?? '—')}%<small>${spinEscape(r.source)}</small></div></li>`).join('')}</ul>`;
    button.hidden=true;
  } catch { result.textContent=spinLabel('加载失败，请重试。','Could not load records. Please retry.'); }
  finally { clearTimeout(timer); button.disabled=false; }
}
