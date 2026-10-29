(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let catalog,people,guides,explanationIndex,selected,active,currentText,currentExplanation,mode='zh',view='explanation',request=0;
  const tr=(zh,en)=>mode==='en'?en:zh;
  const title=w=>mode==='en'?w.title.en:w.title.zh;
  const explained=w=>{const e=explanationIndex.entries?.[w.id];return e&&e.reviewStatus==='verified'&&e.sourceBasis!=='description'&&e.catalogDate===w.date&&e.catalogTitle===w.title.en;};
  const ready=w=>w.fullTextStatus==='ready'&&/^archive\/texts\/[a-z0-9_-]+\.json$/.test(w.fullTextFile||'');
  function externalURL(value){
    try{const u=new URL(value);return ['https:','http:'].includes(u.protocol) && !u.username && !u.password && !/[\u0000-\u0020]/.test(value)?u.href:null;}catch(_){return null;}
  }
  function updateURL(){const u=new URL(location.href);u.searchParams.set('investor',selected);if(active)u.searchParams.set('work',active.id);else u.searchParams.delete('work');history.replaceState(null,'',u);}
  function updateControls(){
    window.InvestorBookplates?.select(selected,mode==='en');
    $('archiveBack').href=`index.html?investor=${encodeURIComponent(selected)}#readings`;
    $('archiveBack').textContent=tr('← 返回投资人资料','← Investor profile');
    Array.from($('archiveInvestor').options).forEach(o=>{const p=people.find(p=>p.id===o.value);o.textContent=mode==='en'?p.nameEn:p.name;});
    const works=catalog.works.filter(w=>w.investor===selected).sort((a,b)=>(b.date||'').localeCompare(a.date||''));
    $('archiveWork').innerHTML=`<option value="">${tr('投资人作品整体导读','Collection reading guide')}</option>`+works.map(w=>`<option value="${esc(w.id)}">${esc((w.dateLabel?.[mode==='en'?'en':'zh']||w.date||'')+' · '+title(w))}${ready(w)?tr(' · 全文',' · Full text'):explained(w)?tr(' · 导读',' · Guide'):''}</option>`).join('');
    $('archiveWork').value=active?.id || '';
    $('archiveInvestor').setAttribute('aria-label',tr('投资人','Investor'));
    $('archiveWork').setAttribute('aria-label',tr('选择篇目','Choose a text'));
    document.documentElement.lang=mode==='en'?'en':'zh-CN';
  }
  function validText(t,w){
    if(t.kind!=='verbatim_text'||t.workId!==w.id||t.reviewStatus!=='verified'||!t.rights?.verified||!t.rights?.allowPublication||!t.rights?.allowTranslation||!t.rights?.evidence)throw Error('Text is not verified for publication');
    if(!['zh','en'].includes(t.originalLanguage)||!t.originalText||!Array.isArray(t.segments)||!t.segments.length)throw Error('Incomplete original text');
    const languages=t.languages||['zh','en'];
    if(!Array.isArray(languages)||!languages.includes(t.originalLanguage)||languages.some(k=>!['zh','en'].includes(k)))throw Error('Invalid languages');
    const ids=new Set();
    for(const s of t.segments){if(!s.id||ids.has(s.id)||languages.some(k=>typeof s[k]!=='string'||!s[k].trim())||s[t.originalLanguage]!==s.original)throw Error('Missing or altered sentence');ids.add(s.id);}
    if(t.segments.map(s=>s.original).join('')!==t.originalText)throw Error('Original text is incomplete');
    if(t.lead||t.chapters||t.questions)throw Error('Study editions are not original texts');
    return t;
  }
  function render(){
    updateControls();
    const languages=currentText?.languages||['zh','en'];
    if(currentText&&(!languages.includes(mode)&&mode!=='bilingual'||mode==='bilingual'&&languages.length<2))mode=currentText.originalLanguage;
    const controls=`<div class="archive-language" role="group" aria-label="${tr('阅读语言','Reading language')}"><button type="button" data-mode="zh" aria-pressed="${mode==='zh'}">中文</button>${languages.includes('en')?`<button type="button" data-mode="en" aria-pressed="${mode==='en'}">English</button>`:''}${languages.length>1?`<button type="button" data-mode="bilingual" aria-pressed="${mode==='bilingual'}">中英对照</button>`:''}</div>`;
    if(!active){
      const g=guides.guides?.[selected];
      if(!g){$('archiveReader').innerHTML=`<p>${tr('导读暂未载入，请刷新重试。','Please refresh to load the guide.')}</p>`;return;}
      document.title=tr(g.title.zh,g.title.en);
      $('archiveReader').innerHTML=`<h1>${esc(tr(g.title.zh,g.title.en))}</h1>${controls}<p class="archive-ai-label">${esc(tr(g.label.zh,g.label.en))}</p>${renderPair(g.lead)}${renderSections(g.sections)}<details class="archive-guide-sequence" ${g.works.length<=5?'open':''}><summary>${tr('全部作品目录','Complete catalogue')} · ${g.works.length}</summary>${g.works.map(w=>`<p><a href="?investor=${encodeURIComponent(selected)}&work=${encodeURIComponent(w.id)}">${esc(w.date || '')} · ${esc(tr(w.title.zh,w.title.en))}</a><small>${esc(w.publisher)}</small></p>`).join('')}</details>`;
      return;
    }
    document.title=title(active);
    const views=`<div class="archive-reading-view" role="group"><button type="button" data-view="explanation" aria-pressed="${view==='explanation'}">${tr('AI 辅助导读','AI reading guide')}</button><button type="button" data-view="original" aria-pressed="${view==='original'}">${currentText?.originalLanguage==='zh'?(currentText.languages?.length===1?tr('中文原文','Chinese original'):tr('原文与译文','Original and translation')):tr('原文与中文译文','Original and Chinese translation')}</button></div>`;
    if(view==='explanation'){
      const note=currentExplanation;
      const written=note?.materialURL&&active.sources.find(s=>s.url===note.materialURL && externalURL(s.url));
      const writtenLink=written?` · <a href="${esc(externalURL(written.url))}" target="_blank" rel="noopener noreferrer">${esc(tr(written.label.zh,written.label.en))} ↗</a>`:'';
      const content=note?`<p class="archive-ai-label">${esc(tr(note.label.zh,note.label.en))} ${note.sourceBasis==='description'?tr(' · 节目说明',' · Programme notes'):''}</p>${renderPair(note.sourceSummary)}${renderSections(note.sections)}<p class="archive-work-meta">${tr('依据材料','Source')}：<a href="${esc(externalURL(note.sourceURL))}" target="_blank" rel="noopener noreferrer">${esc(active.publisher)} ↗</a>${writtenLink} · ${tr('生成日期','Generated')} ${esc(note.generatedAt.slice(0,10))}</p>`:`<p class="archive-text-unavailable">${tr('来源已收录，作品导读待完成。','The source is catalogued; its reading guide is pending.')}</p>`;
      $('archiveReader').innerHTML=`<h1>${esc(title(active))}</h1><p class="archive-work-meta">${esc(active.date || '')} · ${esc(active.publisher)}</p>${views}${controls}${content}`;return;
    }
    const provenance=currentText?renderProvenance(currentText):'';
    const body=currentText?currentText.segments.map(s=>mode==='bilingual'?`<div class="archive-text-pair" id="${esc(s.id)}" data-sentence="${esc(s.id)}">${segmentAnchor(s)}<div lang="zh-CN">${renderContent(s,'zh')}</div><div lang="en" class="archive-en">${renderContent(s,'en')}</div></div>`:`<div class="archive-text-line" lang="${mode==='en'?'en':'zh-CN'}" id="${esc(s.id)}" data-sentence="${esc(s.id)}">${segmentAnchor(s)}${renderContent(s,mode==='en'?'en':'zh')}</div>`).join(''):`<p class="archive-text-unavailable" role="status">${esc(tr('尚未收录可展示的完整原文与逐句译稿。AI 详细介绍单独标注，不作为原文。','No complete original and sentence-aligned translation is available. The AI introduction is labelled separately.'))}</p>`;
    $('archiveReader').innerHTML=`<h1>${esc(title(active))}</h1><p class="archive-work-meta">${esc(active.dateLabel?.[mode==='en'?'en':'zh']||active.date||'')} · ${esc(mode==='en'?(active.publisherEn||active.publisher):active.publisher)}</p>${views}${controls}${provenance}${currentText?.chapterIndex?`<details class="archive-chapters"><summary>${tr('章节目录','Chapters')} · ${currentText.chapterIndex.length}</summary>${currentText.chapterIndex.map(c=>`<p><a href="#${esc(c.anchor)}">${esc(mode==='en'?c.title_original:c.title_zh)}</a></p>`).join('')}</details>`:''}${currentText?`<div class="archive-text-downloads"><button type="button" data-download="zh">${tr('下载中文稿','Chinese .txt')}</button>${languages.includes('en')?`<button type="button" data-download="en">${tr('下载英文稿','English .txt')}</button>`:''}${languages.length>1?`<button type="button" data-download="bilingual">${tr('下载对照稿','Bilingual .txt')}</button>`:''}</div>`:''}<div class="archive-text-body">${body}</div>`;
  }
  function renderContent(s,language){
    const blocks=s[language+'Blocks'];
    if(!blocks)return esc(s[language]);
    return blocks.map(b=>{
      if(b.type==='table')return `<div class="archive-table-scroll"><table><thead><tr>${b.headers.map(h=>`<th scope="col">${esc(h)}</th>`).join('')}</tr></thead><tbody>${b.rows.map(row=>`<tr>${row.map(cell=>`<td>${esc(cell)}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;
      if(b.type==='list'){const tag=b.ordered?'ol':'ul';return `<${tag}>${b.items.map(item=>`<li>${esc(item)}</li>`).join('')}</${tag}>`;}
      return b.type==='heading'?`<h2>${esc(b.text)}</h2>`:`<p>${esc(b.text)}</p>`;
    }).join('');
  }
  function segmentAnchor(s){return s.page||s.anchor||s.timestamp?`<small class="archive-segment-anchor">${esc(s.page?tr('原件第 ','Source page ')+s.page+tr(' 页',''):s.timestamp||s.anchor)}</small>`:'';}
  function renderProvenance(t){
    const source=externalURL(t.sourceURL)||active.sources.map(s=>externalURL(s.url)).find(Boolean);
    const label=t.originalLanguage==='en'?tr('英文原文 · 中文为非官方译文','English original · Unofficial Chinese translation'):tr('中文原文','Chinese original');
    return `<aside class="archive-text-provenance"><p>${esc(label)}${source?` · <a href="${esc(source)}" target="_blank" rel="noopener noreferrer">${tr('原始出处 ↗','Original source ↗')}</a>`:''}</p><p>${esc(t.rights.evidence)}</p>${t.disclaimer?`<p>${esc(t.disclaimer)}</p>`:''}</aside>`;
  }
  function renderPair(p){return mode==='bilingual'?`<div class="archive-text-pair"><p lang="zh-CN">${esc(p.zh)}</p><p lang="en" class="archive-en">${esc(p.en)}</p></div>`:`<p class="archive-text-line">${esc(p[mode==='en'?'en':'zh'])}</p>`;}
  function renderSections(sections){return sections.map(s=>`<section class="archive-explanation-section"><h2>${esc(tr(s.heading.zh,s.heading.en))}</h2>${s.paragraphs.map(renderPair).join('')}</section>`).join('');}
  function validExplanation(note,w,entry){
    if(note.inputHash!==entry.inputHash || (entry.sourceDigest && note.sourceDigest!==entry.sourceDigest))throw Error('Introduction differs from approved index');
    if((note.version>=4&&note.sourceBasis==='description')||(note.version>=3&&note.reviewVersion!==1)||note.kind!=='ai_explanation'||note.workId!==w.id||note.catalogDate!==w.date||note.catalogTitle!==w.title.en||!note.label?.zh||!note.label?.en||(!externalURL(note.sourceURL)||!w.sources.some(s=>s.url===note.sourceURL))||!/^[a-f0-9]{64}$/.test(note.sourceDigest||'')||!note.sourceSummary?.zh||!note.sourceSummary?.en||!Array.isArray(note.sections)||note.sections.length<(note.version>=4?2:6))throw Error('Invalid AI introduction');
    const ids=new Set((note.evidence||[]).map(e=>e.id));
    if(note.sections.some(s=>!s.heading?.zh||!s.heading?.en||!s.paragraphs?.length||s.paragraphs.some(p=>!p.zh||!p.en)||!s.evidenceIds?.length||s.evidenceIds.some(id=>!ids.has(id))))throw Error('Missing source evidence');
    const length=(note.sections.flatMap(s=>s.paragraphs).map(p=>p.zh).join('').match(/[\u4e00-\u9fff]/g)||[]).length;if(note.version<4&&(length<note.minimumChineseCharacters||note.minimumChineseCharacters<1300))throw Error('AI introduction is too short');return note;
  }
  async function openWork(w){
    const own=++request;active=w;currentText=null;currentExplanation=null;updateURL();
    if(!w){render();return;}
    $('archiveReader').innerHTML=`<p role="status">${tr('正在载入正文…','Loading text…')}</p>`;
    let failedExplanation=false,failedText=false;
    const entry=explanationIndex.entries?.[w.id];
    if(explained(w) && entry && /^archive\/explanations\/[a-z0-9_-]+\.json$/.test(entry.file)){
      try{const r=await fetch(entry.file+'?v='+encodeURIComponent(entry.inputHash+'|'+entry.generatedAt),{cache:'no-store'});if(!r.ok)throw Error('Introduction unavailable');const n=validExplanation(await r.json(),w,entry);if(own!==request)return;currentExplanation=n;}
      catch(e){failedExplanation=true;}
    }
    if(ready(w)){
      try{const r=await fetch(w.fullTextFile);if(!r.ok)throw Error('Text unavailable');const t=validText(await r.json(),w);const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t.originalText));const sha=Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');if(sha!==t.sourceDigest)throw Error('Original digest differs');if(own!==request)return;currentText=t;}
      catch(e){failedText=true;}
    }
    if(own!==request)return;render();
    if((view==='explanation' && failedExplanation)||(view==='original' && failedText)){const notice=$('archiveReader').querySelector('.archive-text-unavailable');if(notice)notice.textContent=tr('资料未通过核对，暂不显示。请稍后重试。','The material could not be verified and is not displayed. Please try again later.');}

  }
  function setPerson(id,preferred){
    selected=people.some(p=>p.id===id)?id:people[0].id;$('archiveInvestor').value=selected;
    const works=catalog.works.filter(w=>w.investor===selected).sort((a,b)=>(b.date||'').localeCompare(a.date||''));
    const w=works.find(w=>w.id===preferred)||(preferred?null:works.find(ready));view=ready(w||{})?'original':'explanation';openWork(w||null);
  }
  function download(language){
    if(!currentText)return;
    const text=language===currentText.originalLanguage?currentText.originalText:language==='bilingual'?currentText.segments.map(s=>s.zh+'\n'+s.en).join('\n\n'):currentText.segments.map(s=>s[language]).join('');
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'})),a=document.createElement('a');
    a.href=url;a.download=`${active.id}-${language}.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  async function init(){
    try{
      const rs=await Promise.all([fetch('archive/catalog.json',{cache:'no-store'}),fetch('investors.json',{cache:'no-store'}),fetch('archive/guides.json',{cache:'no-store'}),fetch('archive/explanations/index.json?v=3',{cache:'no-store'})]);if(rs.some(r=>!r.ok))throw Error('Archive unavailable');
      [catalog,people,guides,explanationIndex]=await Promise.all(rs.map(r=>r.json()));people=Array.isArray(people)?people:people.investors;
      $('archiveInvestor').innerHTML=people.map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
      const q=new URLSearchParams(location.search);setPerson(q.get('investor')||'lilu',q.get('work'));
      $('archiveInvestor').addEventListener('change',e=>setPerson(e.target.value));
      $('archiveWork').addEventListener('change',e=>{const w=catalog.works.find(w=>w.id===e.target.value)||null;view=ready(w||{})?'original':'explanation';openWork(w);});
      $('archiveReader').addEventListener('click',e=>{const b=e.target.closest('[data-mode]');if(b){mode=b.dataset.mode;render();$('archiveReader').querySelector(`[data-mode="${mode}"]`).focus({preventScroll:true});}const v=e.target.closest('[data-view]');if(v){view=v.dataset.view;render();}const d=e.target.closest('[data-download]');if(d)download(d.dataset.download);});
    }catch(e){$('archiveReader').innerHTML='<p role="alert">文字页暂未载入，请刷新重试。 / Please refresh to retry.</p>';console.error('Text reader:',e.message);}
  }
  init();
})();
