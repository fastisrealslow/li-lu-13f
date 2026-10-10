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
    if (!value || typeof value !== 'object' || Array.isArray(value)) return {};
    let migrated=false;
    for (const e of [...(spinDash.hk.data?.events || []), ...(spinDash.us.data?.events || [])]) {
      for (const id of e.mergedIds || []) {
        const old=value[id]; if (!old || old.mergedInto===e.id) continue;
        const current=value[e.id] || {};
        value[e.id]={...old,...current,watch:!!(old.watch || current.watch),note:[...new Set([current.note,old.note].filter(Boolean))].join('\n\n')};
        value[id]={...old,mergedInto:e.id}; migrated=true;
      }
    }
    if (migrated) {
      try { localStorage.setItem('spinoff-research-v1',JSON.stringify(value)); }
      catch { spinStorageFailed=true; }
    }
    return value;
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
function spinAutoWatchIntroductions(data) {
  const prefs=spinPrefs();let changed=false;
  for (const e of data.events || []) {
    const code=typeof e.type==='object'?e.type?.code || '':e.type || '';
    if (!/^intro(?:_|$)/.test(code)) continue;
    if (prefs[e.id]?.watch && prefs[e.id]?.autoIntro) continue;
    prefs[e.id]={...prefs[e.id],watch:true,autoIntro:true};changed=true;
  }
  if (changed) {
    try { localStorage.setItem('spinoff-research-v1',JSON.stringify(prefs));spinStorageFailed=false; }
    catch { spinStorageFailed=true; }
  }
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
    const code = typeof e.type === 'object' ? e.type?.code || '' : e.type || '';
    const isReit = !!e.type?.is_reit || /reit/i.test(code);
    const isIntro = /^intro(?:_|$)/.test(code);
    return (!q || search.includes(q)) && (state.type === 'all' || (state.type === 'intro' ? isIntro : state.type === 'reit' ? isReit : !isReit));
  });
}
function spinVisible(state, prefs, now=Date.now()) {
  return spinBaseEvents(state).filter(e => {
    if (state.status !== 'all' && e.status !== state.status) return false;
    switch (state.view) {
      case 'confirmed': return !!e.targetName && e.identityState !== 'unconfirmed_event';
      case 'unconfirmed': return !e.targetName || e.identityState === 'unconfirmed_event';
      case 'watch': return !!prefs[e.id]?.watch;
      case 'upcoming': return spinUpcoming(e,now).length > 0;
      case 'completed': return e.status === 'completed' && spinRecent(e.evidence?.date,90,now);
      case 'changes': return spinRecent(spinRecordUpdate(state.data,e).at,7,now);
      case 'unread': return prefs[e.id]?.read !== e.fingerprint;
      default: return true;
    }
  }).sort((a,b)=>state.sort === 'name' ? a.parentTicker.localeCompare(b.parentTicker) : state.sort === 'upcoming' ?
    (spinUpcoming(a,now)[0]?.[1].date || '9999').localeCompare(spinUpcoming(b,now)[0]?.[1].date || '9999') :
    (state.sort==='filing' ? (b.latestDate || '').localeCompare(a.latestDate || '') :
      spinRecordUpdate(state.data,b).at.localeCompare(spinRecordUpdate(state.data,a).at)) ||
      (b.latestDate || '').localeCompare(a.latestDate || '') || a.id.localeCompare(b.id));
}
function spinRecordUpdate(data,e) {
  const changes=(data?.changes || []).filter(c=>spinEventForChange(data,c)?.id===e.id &&
    (c.kind==='new' || (c.fields || []).length));
  const latest=changes.slice().sort((a,b)=>b.at.localeCompare(a.at))[0];
  return {at:[e.recordUpdatedAt,e.changedAt,latest?.at,e.firstSeenAt].filter(Boolean).sort().pop() || '',
    kind:e.updateKind || latest?.updateKind || (latest?'correction':'initial')};
}
function spinUpdateLabel(kind) {
  return ({new_filing:spinLabel('收录新公告','New filing'),backfill:spinLabel('补录历史公告','Historical filing added'),
    correction:spinLabel('档案信息修正','Record corrected'),initial:spinLabel('首次收录','First collected')})[kind] || spinLabel('档案更新','Record updated');
}
function spinSelectView(state, view) {
  Object.assign(state,{view,query:'',status:'all',type:'all',linkedEvent:null});
}
function spinJointRecords(data, event) {
  if (!event.targetName || !['entity','instrument'].includes(event.identityKind)) return [];
  const joint=(event.announcements || []).filter(a=>/聯合|联合|joint/i.test(a.title || ''));
  return (data?.events || []).filter(e=>e.id!==event.id && e.targetName===event.targetName && e.parentTicker!==event.parentTicker &&
    (e.announcements || []).some(a=>joint.some(b=>a.date===b.date && a.title===b.title)));
}
function spinDateLabel(key) { return key === 'listingDate' ? spinLabel('上市日','Listing date') : key === 'recordDate' ? spinLabel('记录日','Record date') : spinLabel('分派日','Distribution date'); }
function spinPct(value) { return typeof value === 'number' && Number.isFinite(value) ? `${value>0?'+':''}${value.toFixed(1)}%` : '—'; }
function spinPrices(e) {
  const pairs = Array.isArray(e.pricePairs) ? e.pricePairs : [];
  const parent = e.parentPrice || {};
  if (!pairs.length && typeof parent.changePct !== 'number') return '';
  return `<section class="sd-section"><h4>${spinLabel('价格参考','Price reference')}</h4><p class="sd-muted">${spinLabel('区间涨跌幅，非母子公司合计收益。','Period price changes, not combined parent/child returns.')}</p>
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
function spinTypeClass(type) {
  const code = typeof type === 'object' ? type?.code || '' : type || '';
  if (type?.is_reit || /^reit/.test(code)) return 'reit';
  if (/^intro/.test(code)) return 'intro';
  if (/_dist$/.test(code)) return 'ipo-dist';
  if (/^ipo_a/.test(code)) return 'ipo-a';
  if (code === 'ipo_hk' || code === 'carveout') return 'ipo-hk';
  if (code === 'ipo_us' || /Nasdaq|NYSE/i.test(type?.exchange_en || '')) return 'ipo-us';
  if (code === 'ipo_th' || type?.exchange_en === 'SET') return 'ipo-th';
  if (['distribution','split_direct','splitoff'].includes(code)) return 'distribution';
  if (code === 'spinoff') return 'spinoff';
  return 'other';
}
function spinUpdatedTime(value) {
  if (!value || !Number.isFinite(Date.parse(value))) return spinLabel('暂无更新时间','Update time unavailable');
  if (value.length===10) return value;
  return new Date(Date.parse(value)+8*3600000).toISOString().slice(0,16).replace('T',' ')+' (UTC+8)';
}
function spinTargetLabel(e) {
  if (e.targetName) return e.targetName;
  if (e.identityState==='unconfirmed_event') return spinLabel('尚未确认关联分拆','Spin-off relationship unconfirmed');
  if (e.identityState==='conflicting_names') return spinLabel('多个名称，待核对关联','Multiple names; relationship unresolved');
  if (e.type?.is_reit && e.typeEvidence) return spinLabel('基础设施 REIT（正式名称待公布 / 核实）','Infrastructure REIT (formal name pending verification)');
  return spinLabel('标的名称待补全','Target name not yet identified');
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
function spinEventForChange(data,c) {
  return (data.events || []).find(e=>e.id===c.eventId || (e.mergedIds || []).includes(c.eventId));
}
function spinChangeGroups(data,now=Date.now()) {
  const groups=new Map();
  for (const c of spinRecentChanges(data,now)) {
    const e=spinEventForChange(data,c), ticker=e?.parentTicker || c.parentTicker || String(c.eventId).split(':')[1] || '';
    const key=ticker || c.eventId;
    if (!groups.has(key)) groups.set(key,{ticker,name:spinIssuerName(e) || c.parentName || '',at:c.at,changes:[],events:[]});
    const group=groups.get(key);group.changes.push({change:c,event:e});
    if (e && !group.events.some(item=>item.id===e.id)) group.events.push(e);
  }
  return Array.from(groups.values());
}
function spinChangesHTML(data, expanded=false) {
  const all=spinChangeGroups(data), changes=expanded?all:all.slice(0,3);
  if (!changes.length) return `<p class="sd-muted">${spinLabel('近 7 天没有记录到档案更新。追踪开始于','No dossier updates recorded in the last 7 days. Tracking began')} ${spinEscape((data.trackingStartedAt || '').slice(0,10))}</p>`;
  return `<p class="sd-change-explanation">${spinLabel('这是下方记录的更新日志：只列系统近 7 天新收录或修改的内容，补录旧公告、纠正名称也计入。它不是“近 7 天新发生的分拆”，也不是另一份项目清单。点击标的可打开下方对应记录。','This is the update log for the records below: additions and corrections in the last 7 days, including backfilled older filings. It does not mean these spin-offs happened in the last 7 days. Select a target to open its matching record.')}</p><ul class="sd-change-groups">${changes.map(group=>{
    const identity=`<strong>${spinEscape(group.name || spinLabel('公司名称待补全','Company name unavailable'))}</strong><span class="sd-change-ticker">${spinEscape(group.ticker)}</span>`;
    return `<li><time>${spinEscape(group.at.slice(0,10))}</time><div class="sd-change-body"><div>${identity} <span class="sd-change-total">${spinLabel(`${group.changes.length} 次更新 · ${group.events.length} 个对应档案`,`${group.changes.length} updates · ${group.events.length} linked dossiers`)}</span></div><div class="sd-change-targets">${group.events.map(e=>`<button class="sd-change-company" data-action="open-event" data-open-event="${spinEscape(e.id)}">${spinEscape(spinTargetLabel(e))} → ${spinLabel('查看下方档案','View dossier below')}</button><small>${spinStatus(e.status)} · ${spinLabel('最近原公告','Latest original filing')} ${spinEscape(e.latestDate || '—')}</small>`).join('')}</div><details class="sd-update-history"><summary>${spinLabel('展开全部更新记录','Show every recorded update')}</summary><ol>${group.changes.map(({change:c,event:e})=>`<li><time>${spinEscape(spinUpdatedTime(c.at))}</time><p>${e?spinEscape(spinTargetLabel(e))+' · ':''}${spinEscape(spinChangeDescription(c,e))}${!e?' · '+spinLabel('仅存历史更新，当前档案未匹配','Historical update only; no current dossier match'):''}</p></li>`).join('')}</ol></details></div></li>`;
  }).join('')}</ul>${all.length>3?`<button class="sd-more" data-action="more-changes">${expanded?spinLabel('收起','Show less'):spinLabel(`查看全部 ${all.length} 家公司`,`View all ${all.length} issuers`)}</button>`:''}`;
}

function spinCard(e, pref={}, joint=[], update={at:e.recordUpdatedAt || e.changedAt || '',kind:e.updateKind || 'initial'}) {
  const dates = Object.entries(e.dates || {});
  const related = e.announcements.filter(a=>a.relevance !== 'unverified');
  const unverified = e.announcements.filter(a=>a.relevance === 'unverified');
  const announcementHTML = list => list.map(a=>`<li><time>${spinEscape(a.date)}</time><div>${spinLink(a.url,a.title)}${!a.direct ? `<small>${spinLabel('公司公告目录，尚未定位原文','Company filing list; original document not yet resolved')}</small>` : ''}</div></li>`).join('');
  const type = spinTypeName(e.type);
  const latest = [...related].sort((a,b)=>(b.date || '').localeCompare(a.date || ''))[0];
  return `<article class="sd-card ${pref.read === e.fingerprint ? 'sd-read' : ''}" data-event="${spinEscape(e.id)}">
    <button class="sd-watch" data-action="watch" aria-label="${spinEscape(spinLabel('自选：','Watch: ')+(spinIssuerName(e) || e.parentTicker))}" title="${spinLabel('加入 / 取消自选','Toggle watchlist')}" aria-pressed="${!!pref.watch}">${pref.watch?'★':'☆'}</button>
    <details class="sd-dossier"><summary>
      <div class="sd-identity"><span class="sd-company" title="${spinEscape(spinIssuerName(e))}">${spinEscape(spinIssuerName(e) || e.parentTicker)}</span><span class="sd-symbol">${spinEscape(e.parentTicker)} <span class="sd-unread">${spinLabel('未读','Unread')}</span></span></div>
      <div class="sd-target" title="${spinEscape(spinTargetLabel(e))}"><b><span class="sd-mobile-label">${spinLabel('分拆 / 分派标的：','Target: ')}</span>${spinEscape(spinTargetLabel(e))}</b><small>${e.identityKind==='business'?spinLabel('业务 / 项目 · ','Business / project · '):''}<span class="sd-type sd-type-${spinTypeClass(e.type)}">${spinEscape(type)}</span>${e.targetTicker?' · '+spinEscape(e.targetTicker):''}</small>${joint.length?`<small class="sd-joint-label">${spinLabel('同一项目 · 与','Same project · jointly disclosed with ')}${joint.map(other=>spinEscape(spinIssuerName(other))).join('、')}${spinLabel('联合披露','')}</small>`:''}</div>
      <div class="sd-row-meta"><span class="sd-status sd-${spinEscape(e.status)}">${spinStatus(e.status)}</span>${pref.watch && pref.autoIntro?`<small class="sd-auto-intro">${spinLabel('介绍上市 · 自动自选','Introduction · auto-watched')}</small>`:''}</div>
      <div class="sd-latest">${latest ? `<div class="sd-latest-title">${spinLink(latest.url,latest.title)}</div>` : ''}<time class="sd-row-date">${spinLabel('公告：','Filing: ')}${spinEscape(latest?.date || e.latestDate || '—')}</time>${update.at?`<small class="sd-record-update">${spinUpdateLabel(update.kind)} · ${spinEscape(spinUpdatedTime(update.at))}</small>`:''}</div>
      <span class="sd-expand" aria-label="${spinLabel('展开档案','Expand dossier')}">⌄</span>
    </summary>
      <div class="sd-detail">
      ${(typeof e.type==='object'?e.type.code:e.type)==='distribution'?`<p class="sd-transaction-note">${spinLabel('这条记录追踪实物分派：关联公司将所持证券派给股东。它不表示该标的重新分拆上市；同一标的历次分派公告合并在本档案。','This record tracks an in-specie distribution of securities to shareholders. It does not mean a new listing of the target; successive distributions are kept in this dossier.')}</p>`:''}
      ${e.evidence?.quote?`<section class="sd-section"><h4>${spinLabel('当前进度依据','Current status evidence')}</h4><p>${spinEscape(e.evidence.quote)}</p><small>${spinEscape(e.evidence.date)} · ${spinLink(e.evidence.url,spinLabel('核对原公告','Original filing'))}</small></section>`:''}
      ${joint.length?`<p class="sd-joint-explanation">${spinLabel('这几家公司联合披露同一个分拆标的，按关联公司保留各自公告记录；不是几个不同的分拆。','These companies jointly disclose the same target. Their filing records are retained by issuer; these are not separate spin-offs.')} ${joint.map(other=>`<button data-action="open-event" data-open-event="${spinEscape(other.id)}">${spinEscape(spinIssuerName(other))} · ${spinEscape(other.parentTicker)} →</button>`).join(' ')}</p>`:''}
      ${related.length || unverified.length ? `<section class="sd-section sd-announcements"><h4>${spinLabel('公告记录','Filings')} <small>${related.length + unverified.length}</small></h4>${related.length ? `<ul class="sd-sources">${announcementHTML(related)}</ul>` : ''}${unverified.length ? `<div class="sd-legacy"><p>${spinLabel('关联待确认','Relevance unconfirmed')} (${unverified.length})</p><ul class="sd-sources">${announcementHTML(unverified)}</ul></div>` : ''}</section>` : ''}
      ${typeof e.parentMarketCap === 'number' ? `<p class="sd-muted">${spinLabel('关联公司市值（快照）','Issuer market cap (snapshot)')} · ${lang==='en'?`$${(e.parentMarketCap/10).toFixed(2)}B`:`${e.parentMarketCap.toFixed(1)} 亿美元`}</p>` : ''}
      ${dates.length ? `<section class="sd-section"><h4>${spinLabel('关键日期','Key dates')}</h4>${dates.map(([k,v])=>`<p><b>${spinDateLabel(k)} · ${spinEscape(v.date)}</b> <span class="sd-muted">${v.kind==='actual'?spinLabel('公告确认已发生','Confirmed in filing'):spinLabel('计划日期，可能调整','Scheduled; subject to change')}</span> ${spinLink(v.url,spinLabel('公告','Filing'))}</p>`).join('')}</section>` : ''}
      ${spinPrices(e)}
      ${e.market === 'hk' ? `<section class="sd-section"><h4>${spinLabel('历史股东披露','Historical ownership disclosures')}</h4><button data-action="ownership">${spinLabel('加载历史记录','Load historical records')}</button><div class="sd-ownership"></div></section>` : ''}

      </div>
    </details></article>`;
}
function spinRenderList(market) {
  const state = spinDash[market], root = document.getElementById(market === 'hk' ? 'spinoffContent' : 'spinoffUSContent');
  const prefs = spinPrefs(), events = spinVisible(state,prefs), base = spinBaseEvents(state);
  root.querySelector('.sd-results').innerHTML = events.length ? `<div class="sd-list-head"><span>${spinLabel('关联公司 / 代码','Associated issuer / ticker')}</span><span>${spinLabel('→ 标的 / 类型','→ Target / type')}</span><span>${spinLabel('当前进度','Current status')}</span><span>${spinLabel('公告 / 档案更新','Filing / record update')}</span><span></span></div>`+events.map(e=>spinCard(e,prefs[e.id],spinJointRecords(state.data,e),spinRecordUpdate(state.data,e))).join('') : `<div class="sd-empty">${spinLabel('当前筛选下没有记录。可清空搜索或重置筛选。','No records match these filters. Clear the search or reset filters.')}</div>`;
  root.querySelector('.sd-count').textContent = spinLabel(`当前显示 ${events.length} 条 · 数据库共 ${state.data.events.length} 条公司记录`,`Showing ${events.length} records · ${state.data.events.length} issuer records in the database`);
  const names={all:spinLabel('全部记录','All records'),confirmed:spinLabel('标的已识别的记录','Records with identified targets'),unconfirmed:spinLabel('待核实公告','Filings to verify'),watch:spinLabel('我的自选','My watchlist'),upcoming:spinLabel('未来 30 天有日期的项目','Projects with dates in the next 30 days'),changes:spinLabel('近 7 天更新过的记录','Records updated in the last 7 days'),unread:spinLabel('未读 / 有更新','Unread / updated'),completed:spinLabel('近 90 天公告称已完成','Completion filings in the last 90 days')};
  root.querySelector('.sd-list-title').textContent=names[state.view] || names.all;
  root.querySelector('.sd-view-help').textContent=state.view==='changes'?spinLabel('这是“全部记录”中近 7 天更新过的同一批档案，顺序和当前状态一致。补录与信息修正会单独标明，原公告日期以每条记录为准。','These are the same records as All, filtered to updates within 7 days, with matching order and current status. Backfills and corrections are labeled separately from original filing dates.'):state.view==='watch'?spinLabel('这里显示你关注的记录：介绍上市自动收录，其他项目点右侧 ☆ 加入。每条可展开查看原公告。','Your followed records: introductions are added automatically; use ☆ for other projects. Open a row to inspect its filings.'):state.view==='unconfirmed'?spinLabel('这些公告的分拆标的或关联还未核实，暂不算作已识别项目。','The target or relationship in these filings is not verified; they are excluded from identified projects.'):spinLabel('按“关联公司 → 分拆标的”阅读；展开一条即可查看该标的的公告、进度和日期。包括历史项目，不代表全部仍在推进；联合披露会标明同一项目。','Read each row as associated issuer → target. Open it for filings, status and dates. Historical projects are included and may no longer be active. Joint disclosures are marked as the same project.');
  const linked=events.find(e=>e.id===state.linkedEvent);
  if (linked) {
    root.querySelector('.sd-results').insertAdjacentHTML('afterbegin',`<p class="sd-linked-notice">${spinLabel('上方变化对应：','Linked from updates: ')}<strong>${spinEscape(spinIssuerName(linked))} · ${spinEscape(spinTargetLabel(linked))}</strong> · ${spinLabel('对应档案已标出；其余为全部档案。','The matching dossier is highlighted; other rows show the full archive.')} <button data-action="reset">${spinLabel('取消定位','Clear highlight')}</button></p>`);
    Array.from(root.querySelectorAll('[data-event]')).find(e=>e.dataset.event===linked.id)?.classList.add('sd-linked');
  }
  root.querySelectorAll('[data-view]').forEach(b=>{ b.setAttribute('aria-pressed',String(state.view===b.dataset.view)); });
  const counts = {confirmed:base.filter(e=>e.targetName && e.identityState !== 'unconfirmed_event').length,unconfirmed:base.filter(e=>!e.targetName || e.identityState === 'unconfirmed_event').length,all:base.length,watch:base.filter(e=>prefs[e.id]?.watch).length,upcoming:base.filter(e=>spinUpcoming(e).length).length};
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
  const viewNames = {all:spinLabel('全部记录','All records'),watch:spinLabel('我的自选','My watchlist'),upcoming:spinLabel('未来 30 天','Next 30 days')};
  root.innerHTML = `<div class="sd-dashboard"><header class="sd-header"><div><p class="sd-eyebrow">${spinLabel('分拆研究工作台','SPIN-OFF RESEARCH')}</p><h2>${market==='hk'?spinLabel('港股分拆','Hong Kong spin-offs'):spinLabel('美股分拆','US spin-offs')}</h2><p class="sd-muted">${spinLabel('先看变化，再核对证据，持续跟踪值得研究的事件。','Track changes, inspect evidence, and follow the events worth researching.')}</p></div><button data-action="refresh">↻ ${spinLabel('刷新数据','Refresh data')}</button></header>
    <p class="sd-updated">${spinLabel('最近自动采集','Last automatic collection')}: ${spinEscape(spinUpdatedTime(data.updatedAt))}</p>
    <p class="sd-error" role="status" ${state.error?'':'hidden'}>${spinLabel('刷新失败，仍显示上次成功加载的数据。请重试。','Refresh failed. Showing the last successfully loaded data. Please retry.')}</p>
    <p class="sd-storage" role="status" hidden>${spinLabel('浏览器存储不可用，自选暂时无法保存。','Browser storage is unavailable; watchlist cannot be saved.')}</p>
    <p class="sd-overview">${spinLabel('下方按公司整理分拆公告。同一个标的的多份公告放在一条记录中；联合披露可能对应多家关联公司，不等于多个分拆。','The list organizes spin-off filings by issuer and target. Multiple filings for one target share a record; joint disclosures can involve several issuers without representing separate spin-offs.')}</p>
    <details class="sd-source-method"><summary>${spinLabel('信息来源与更新方式','Sources and update process')}</summary><p>${market==='hk'?spinLabel('自动搜索港交所披露易的分拆、实物分派、介绍上市等公告标题，再读取公告正文核对标的、日期和进度；并追踪已识别标的的上市公告，以及分派公司的业绩文件。搜索窗口之外的历史公告继续保留，新增公告按原文链接去重、合并到对应档案。','HKEXnews headline searches discover spin-offs, in-specie distributions and introductions. Filing text verifies targets, dates and progress. Known targets and distributing issuers are followed through listing and results filings. Older sources remain archived, and document URLs deduplicate updates.'):spinLabel('自动检索 SEC 公司申报与分拆相关文件，核对原文后合并到对应公司和标的档案。','SEC issuer filings and spin-off documents are collected and checked before merging into issuer/target dossiers.')}</p><p>${spinLabel('每天定时采集两次；上面的采集时间表示系统检查时间，不等于公司刚发布公告。近 7 天与全部使用同一份列表、同一个当前状态。档案新增或修正后移到前面，原公告日期单独显示。','Collection runs twice daily. The collection timestamp is a system check, not the filing publication time. Last 7 days filters the same list and current status as All records. Updated records move to the top; original filing dates are shown separately.')}</p>${data.sourceCollection?.failedKeywords?.length?`<p>${spinLabel('本次部分关键词抓取失败，已保留历史数据：','Some searches failed; historical records were retained: ')}${spinEscape(data.sourceCollection.failedKeywords.join('、'))}</p>`:''}</details>
    <div class="sd-kpis">${Object.entries(viewNames).map(([key,label])=>`<button data-view="${key}" aria-pressed="${state.view===key}"><span>${label}</span><b data-count="${key}">0</b></button>`).join('')}</div>
    <p class="sd-auto-note">${spinLabel('介绍上市每次加载 / 刷新自动加入“我的自选”；点击“我的自选”查看列表，其他项目可点 ☆ 加入。','Introductions are added to My watchlist on every load / refresh. Select My watchlist to view them; use ☆ to add other projects.')}</p>
    <div class="sd-controls"><label class="sd-search">${spinLabel('搜索','Search')}<input type="search" data-filter="query" value="${spinEscape(state.query)}" placeholder="${spinLabel('公司、标的或股票代码','Issuer, target or ticker')}"></label><label>${spinLabel('状态','Status')}<select data-filter="status"><option value="all">${spinLabel('全部状态','All statuses')}</option>${Object.keys(spinStatusText).map(k=>`<option value="${k}">${spinStatus(k)}</option>`).join('')}</select></label><label>${spinLabel('类型','Type')}<select data-filter="type"><option value="all">${spinLabel('全部（含 REIT）','All (including REITs)')}</option><option value="intro">${spinLabel('介绍上市','Listing by introduction')}</option><option value="reit">REIT</option><option value="other">${spinLabel('非 REIT','Non-REIT')}</option></select></label><label>${spinLabel('排序','Sort')}<select data-filter="sort"><option value="latest">${spinLabel('最近更新优先','Recently updated first')}</option><option value="filing">${spinLabel('原公告日期','Original filing date')}</option><option value="upcoming">${spinLabel('临近日期优先','Upcoming date')}</option><option value="name">${spinLabel('股票代码','Ticker')}</option></select></label></div>
    <div class="sd-views">${[['confirmed',spinLabel('已识别项目','Identified projects')],['unconfirmed',spinLabel('待核实公告','Filings to verify')],['unread',spinLabel('未读 / 有更新','Unread / updated')],['changes',spinLabel('近 7 天更新过','Updated in last 7 days')],['completed',spinLabel('近 90 天完成公告','Completion filings · 90 days')]].map(([k,label])=>`<button data-view="${k}" aria-pressed="${state.view===k}">${label}${['confirmed','unconfirmed'].includes(k)?` <span data-count="${k}">0</span>`:''}</button>`).join('')}<button data-action="reset">${spinLabel('重置筛选','Reset filters')}</button></div><header class="sd-list-heading"><h3 class="sd-list-title" tabindex="-1"></h3><span class="sd-count" aria-live="polite"></span></header><p class="sd-view-help" role="status"></p><div class="sd-results"></div>
    <p class="sd-footer">${spinLabel('采集范围内的研究线索，并非全部分拆事件。计划日期可能变化，最终以公司公告为准。','Research leads within collection coverage, not an exhaustive event list. Scheduled dates may change; consult issuer filings.')}</p></div>`;
  for (const key of ['status','type','sort']) root.querySelector(`[data-filter="${key}"]`).value=state[key];
  root.oninput = event=>{
    if (event.target.dataset.filter === 'query') { state.query=event.target.value; spinRenderList(market); }

  };
  root.onchange = event=>{ const key=event.target.dataset.filter; if (key && key!=='query') { state[key]=event.target.value; spinRenderList(market); } };
  root.onclick = event=>{
    const button=event.target.closest('button'); if (!button) return;
    if (button.dataset.view) {
      spinSelectView(state,button.dataset.view);
      for (const key of ['query','status','type']) root.querySelector(`[data-filter="${key}"]`).value=state[key];
      spinRenderList(market);
      const heading=root.querySelector('.sd-list-title');heading.focus({preventScroll:true});heading.scrollIntoView({block:'start',behavior:'smooth'});
    }
    if (button.dataset.action==='more-changes') { state.changesExpanded=!state.changesExpanded; root.querySelector('.sd-change-content').innerHTML=spinChangesHTML(data,state.changesExpanded); }
    if (button.dataset.action==='open-event') {
      const id=button.dataset.openEvent;
      Object.assign(state,{query:'',view:'all',status:'all',type:'all',linkedEvent:id}); spinPaint(market);
      const card=Array.from(root.querySelectorAll('[data-event]')).find(e=>e.dataset.event===id);
      const details=card?.querySelector('.sd-dossier');
      if (details) { details.open=true; details.querySelector('summary').focus({preventScroll:true}); card.scrollIntoView({block:'start',behavior:'smooth'}); }
    }
    if (button.dataset.action==='ownership') spinLoadOwnership(button);
    if (button.dataset.action==='refresh') renderSpinoffDashboard(market,true);
    if (button.dataset.action==='reset') { Object.assign(state,{query:'',view:'all',status:'all',type:'all',sort:'latest',linkedEvent:null}); spinPaint(market); }
    if (button.dataset.action==='watch') {
      const id=button.closest('[data-event]').dataset.event, watch=!spinPrefs()[id]?.watch;
      if (spinSave(id,{watch})) { button.setAttribute('aria-pressed',String(watch)); button.textContent=watch?'★':'☆'; if (!watch) button.closest('[data-event]').querySelector('.sd-auto-intro')?.remove(); if (state.view==='watch') spinRenderList(market); else root.querySelector('[data-count="watch"]').textContent=spinBaseEvents(state).filter(e=>spinPrefs()[e.id]?.watch).length; }
      root.querySelector('.sd-storage').hidden=!spinStorageFailed;
    }
  };
  spinRenderList(market);
}
async function renderSpinoffDashboard(market, refresh=false) {
  const state=spinDash[market], root=document.getElementById(market==='hk'?'spinoffContent':'spinoffUSContent');
  if (!root) return;
  if (state.data && !refresh) { spinAutoWatchIntroductions(state.data);spinPaint(market); return; }
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
    state.data=value; state.error=false; spinAutoWatchIntroductions(value);spinPaint(market);
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
