(function(){
  'use strict';
  const $=id=>document.getElementById(id), PAGE_SIZE=10;
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const safeURL=s=>{try{const u=new URL(s);return u.protocol==='https:'?u.href:'';}catch{return '';}};
  const pair=(p,mode)=>mode==='en'?p.en:p.zh;
  const typeNames={speech:['演讲','Speech'],interview:['访谈','Interview'],qa:['公开问答','Q&A'],essay:['文章与序言','Essay / foreword']};
  let catalog, people, selected, active, mode='zh', page=0, request=0, currentNote;
  const tr=(zh,en)=>mode==='en'?en:zh;
  function title(w){return pair(w.title,mode)||w.title.zh||w.title.en;}
  function workDate(w){return w.date||'';}
  function shownDate(w){return w.dateLabel?.[mode==='en'?'en':'zh']||w.date||tr('日期未确认','Date unconfirmed');}
  function dateType(w){return w.dateKind==='published'?tr('发布','Published'):w.dateKind==='written'?tr('成文','Written'):tr('活动','Event');}
  function type(w){return (typeNames[w.kind]||typeNames.interview)[mode==='en'?1:0];}
  function publisher(w){return mode==='en'?(w.publisherEn||w.publisher):w.publisher;}
  function updateURL(){const u=new URL(location.href);u.searchParams.set('investor',selected);if(active)u.searchParams.set('work',active.id);else u.searchParams.delete('work');history.replaceState(null,'',u);}
  function setPerson(id,preferred){
    selected=people.some(p=>p.id===id)?id:people[0].id;page=0;
    $('archiveInvestor').value=selected;
    $('archiveSearch').value='';$('archiveKind').value='all';$('archiveReady').checked=false;
    renderHeading();renderList();
    const works=catalog.works.filter(w=>w.investor===selected);
    const choice=works.find(w=>w.id===preferred)||works.find(w=>w.noteFile)||works[0];
    if(choice)openWork(choice,false);else{active=null;currentNote=null;request++;$('archiveReader').innerHTML=`<p>${tr('目前尚未核对到公开作品。','No public works have been verified yet.')}</p>`;updateURL();}
  }
  function renderHeading(){
    const p=people.find(p=>p.id===selected),works=catalog.works.filter(w=>w.investor===selected),ready=works.filter(w=>w.noteFile).length;
    $('archiveTitle').textContent=`${mode==='en'?p.nameEn:p.name} · ${tr('演讲与访谈作品集','Speeches & Interviews')}`;
    document.title=$('archiveTitle').textContent;
    document.documentElement.lang=mode==='en'?'en':'zh-CN';
    $('archiveEyebrow').textContent=tr('演讲 · 访谈 · 公开问答','SPEECHES · INTERVIEWS · PUBLIC Q&A');
    updateCatalogToggle();
    $('archiveDescription').textContent=tr('按年代保存公开表达，结合背景、论证与限制阅读。','Public conversations through the years, with context, reasoning and limitations.');
    $('archiveCoverage').textContent=tr(`已核对 ${works.length} 篇作品 · ${ready} 篇站内整理 · 目录更新 ${catalog.updatedAt.slice(0,10)}`,`${works.length} catalogued works · ${ready} study editions · Catalogue updated ${catalog.updatedAt.slice(0,10)}`);
    $('archiveBack').href=`index.html?investor=${encodeURIComponent(selected)}#readings`;
    $('archiveBack').textContent=tr('← 返回投资人资料','← Investor profile');$('catalogLink').textContent=tr('作品目录','Catalogue');
    const labels=[['archiveInvestor','投资人','Investor'],['archiveSearch','搜索作品与主题','Search works and themes']];
    for(const [id,zh,en] of labels)document.querySelector(`label[for=${id}]`).textContent=tr(zh,en);
    $('archiveSearch').placeholder=tr('如：能力圈、资本配置、2015','e.g. competence, capital allocation, 2015');
    Array.from($('archiveInvestor').options).forEach(o=>{const p=people.find(p=>p.id===o.value);o.textContent=mode==='en'?p.nameEn:p.name;});
    const kind=$('archiveKind');kind.options[0].textContent=tr('全部类型','All types');Array.from(kind.options).slice(1).forEach(o=>o.textContent=(typeNames[o.value]||typeNames.interview)[mode==='en'?1:0]);
    kind.parentElement.firstChild.textContent=tr('内容','Type');$('archiveSort').parentElement.firstChild.textContent=tr('排序','Sort');
    $('archiveSort').options[0].textContent=tr('由近到远','Newest first');$('archiveSort').options[1].textContent=tr('由远到近','Oldest first');
    $('archiveReady').parentElement.lastChild.textContent=tr('只看有站内整理的作品','Study editions only');
    $('archiveMethod').innerHTML=mode==='en'?'<summary>Collection and editorial method</summary><p>We catalogue works published by the investor, the fund, original interviewers and event organisers. Reprints are explicitly labelled. Formats of the same event are merged. Event dates and publication dates are distinguished; uncertain dates are not guessed.</p><p>On-site study editions are original third-person summaries with matching Chinese and English paragraphs, not complete transcripts or translations. Embedded videos remain hosted by their publishers. Third-party full texts, captions and translations are not republished without permission.</p><p>Scheduled checks discover new works and preserve earlier records when a source fails. Official texts are preferred; videos are processed using available captions or speech recognition on accessible audio. Unverified names and numbers are omitted. Catalogue-only entries are not presented as processed interviews.</p><p>This growing catalogue does not claim to exhaust the internet. Processing status is shown for each work.</p>':catalog.methodHTML;
  }
  function filtered(){
    const q=$('archiveSearch').value.trim().toLocaleLowerCase(),kind=$('archiveKind').value,ready=$('archiveReady').checked;
    return catalog.works.filter(w=>w.investor===selected&&(kind==='all'||w.kind===kind)&&(!ready||w.noteFile)&&(!q||[w.title.zh,w.title.en,w.date,w.publisher,(w.topics||[]).join(' '),(w.topicsEn||[]).join(' ')].join(' ').toLocaleLowerCase().includes(q))).sort((a,b)=>{const delta=workDate(b).localeCompare(workDate(a));return ($('archiveSort').value==='asc'?-delta:delta)||a.id.localeCompare(b.id);});
  }
  function renderList(){
    const works=filtered(),pages=Math.max(1,Math.ceil(works.length/PAGE_SIZE));page=Math.max(0,Math.min(page,pages-1));
    $('archiveResultCount').textContent=tr(`${works.length} 篇匹配作品`,`${works.length} matching works`);
    $('archiveList').innerHTML=works.slice(page*PAGE_SIZE,(page+1)*PAGE_SIZE).map(w=>`<button type="button" class="archive-item" data-work="${esc(w.id)}" aria-current="${active?.id===w.id}"><small class="archive-item-meta">${esc(shownDate(w))} · ${esc(type(w))}</small><strong>${esc(title(w))}</strong><small>${esc(publisher(w))} · ${w.noteFile?tr('有站内整理','Study edition'):tr('已收录 · 正文待整理','Catalogued · awaiting study edition')}</small></button>`).join('')||`<p class="archive-empty">${tr('没有匹配作品，可以减少筛选条件。','No matches. Try fewer filters.')}</p>`;
    $('archivePagination').innerHTML=pages>1?`<button type="button" data-page="-1" ${page===0?'disabled':''}>${tr('上一页','Previous')}</button><span>${page+1} / ${pages}</span><button type="button" data-page="1" ${page===pages-1?'disabled':''}>${tr('下一页','Next')}</button>`:'';
  }
  function renderPair(p,classes=''){
    if(mode==='bilingual')return `<div class="archive-bilingual-pair"><p lang="zh-CN" class="${classes}">${esc(p.zh)}</p><p lang="en" class="archive-en ${classes}">${esc(p.en)}</p></div>`;
    return `<p lang="${mode==='en'?'en':'zh-CN'}" class="${classes}">${esc(pair(p,mode))}</p>`;
  }
  function renderWork(w,n){
    const sourceStatus=w.transcriptQuality==='publisher_machine_transcript'?tr('发布方机器转录 · 可能存在听写误差','Publisher machine transcript · recognition may be imperfect'):w.textStatus==='official_text'?tr(w.sourceLevel==='reprint'?'已核对原刊文字存档':'已取得官方文字稿',w.sourceLevel==='reprint'?'Original publication archive checked':'Official text obtained'):w.textStatus==='captions'?tr('已取得平台字幕','Platform captions obtained'):w.textStatus==='asr'?tr('已取得机器转录 · 可能存在听写误差','Machine transcription obtained · recognition may be imperfect'):tr('未取得完整文字稿','Full source text not obtained');
    const subtitle=n?tr('本站中文整理及对应英文 · 非逐字全文翻译','Original study edition · not a verbatim transcript or complete translation'):tr('已收录原始作品 · 尚无站内正文','Original work catalogued · study edition not yet available');
    $('archiveReader').innerHTML=`<p class="archive-eyebrow">${esc(type(w))} / ${n?tr('站内整理','STUDY EDITION'):tr('作品目录','CATALOGUE')}</p><h2>${esc(title(w))}</h2><div class="archive-work-meta">${esc(dateType(w))} ${esc(shownDate(w))} · ${esc(publisher(w))}<br>${esc(subtitle)}<br>${esc(sourceStatus)}${w.sourceLevel==='reprint'?tr(' · 转载来源，原始链接见下方',' · Reprinted source; originals listed below'):''}</div>
    <div class="archive-language" role="group" aria-label="${tr('阅读语言','Reading language')}"><button type="button" data-mode="zh" aria-pressed="${mode==='zh'}">中文</button><button type="button" data-mode="en" aria-pressed="${mode==='en'}">English</button><button type="button" data-mode="bilingual" aria-pressed="${mode==='bilingual'}">中英对照</button></div>
    ${n?`<div class="archive-editor-note">${esc(tr('以下内容按原始资料整理为第三人称阅读笔记。中文与英文逐段对应；章节标题和阅读问题由本站编辑，不能当作受访者原话。','The following is an original, third-person study edition based on the source. Paragraphs align across languages. Headings and reading questions are editorial, not the speaker’s own words.'))}${n.basis==='publisher_description'?` ${esc(tr('本篇依据发布方介绍，尚未获得完整转录。','This edition is based on the publisher’s description, not a complete transcript.'))}`:''}</div>${renderPair(n.lead,'archive-lead')}<nav aria-label="${tr('本文目录','Contents')}"><ul class="archive-toc">${n.chapters.map((c,i)=>`<li><a href="#chapter-${i}">${String(i+1).padStart(2,'0')} · ${esc(pair(c.heading,mode))}</a></li>`).join('')}</ul>${n.chapters.map((c,i)=>`<section class="archive-chapter" id="chapter-${i}"><h3>${String(i+1).padStart(2,'0')} / ${esc(pair(c.heading,mode))}</h3>${c.paragraphs.map(p=>renderPair(p)).join('')}</section>`).join('')}${n.questions?.length?`<section class="archive-chapter"><h3>${tr('带着这些问题再读','Questions for a second reading')}</h3>${n.questions.map(p=>renderPair(p)).join('')}</section>`:''}`:`<div class="archive-editor-note">${esc(tr('这篇作品已进入档案。目前没有取得足以可靠整理的正文，因此没有生成或猜测访谈内容。你可以在下面打开原始视频；自动流程取得文字稿或可处理音频后会继续补充。','This work is catalogued, but sufficient source text has not yet been obtained. Interview content has not been invented. Original media can be viewed below where available; processing continues as source text or accessible audio becomes available.'))}</div>`}
    ${renderMedia(w)}<section class="archive-sources"><h3>${tr('原始资料与版本','Sources & editions')}</h3><ul>${w.sources.filter(s=>safeURL(s.url)).map(s=>`<li><a href="${esc(safeURL(s.url))}" target="_blank" rel="noopener noreferrer">${esc(pair(s.label,mode)||s.label)} ↗</a>${s.locator?`<br><span class="archive-muted">${esc(s.locator)}</span>`:''}</li>`).join('')}</ul><p class="archive-muted">${esc(tr('最近核对','Last checked'))} ${esc(w.checkedAt||catalog.updatedAt.slice(0,10))}${n?` · ${esc(tr('整理版本','Study edition'))} ${esc(n.reviewedAt||'')}`:''}</p></section>`;
  }
  function renderMedia(w){
    const video=w.media?.find(m=>m.kind==='youtube'&&/^[A-Za-z0-9_-]{11}$/.test(m.id));
    const audio=w.media?.find(m=>m.kind==='audio'&&safeURL(m.url));
    const provider=w.media?.find(m=>m.kind==='publisher_embed'&&safeURL(m.url)&&['charlierose.com','player.cnbc.com','player.vimeo.com'].includes(new URL(m.url).hostname));
    const pdf=w.sources.find(s=>/\.pdf(?:$|[?#])/i.test(s.url)&&safeURL(s.url)&&s.label?.zh?.includes('备用 CDN'))||w.sources.find(s=>/\.pdf(?:$|[?#])/i.test(s.url)&&safeURL(s.url));
    if(!video&&!audio&&!pdf&&!provider)return '';
    return `<section class="archive-media"><h3>${tr('原始作品 · 站内播放／阅读','Original work · view here')}</h3>${video?`<details><summary>${tr('展开原始视频（发布方播放器）','Open original video (publisher player)')}</summary><div data-video="${esc(video.id)}"></div></details>`:''}${provider?`<details><summary>${tr('展开原始视频（发布方播放器）','Open original video (publisher player)')}</summary><div data-provider="${esc(safeURL(provider.url))}"></div></details>`:''}${audio?`<details><summary>${tr('收听原始音频','Listen to original audio')}</summary><audio controls preload="none" src="${esc(safeURL(audio.url))}"></audio></details>`:''}${pdf?`<details><summary>${tr('展开原始文字稿（原语言 PDF）','Open source text (original-language PDF)')}</summary><div data-pdf="${esc(safeURL(pdf.url))}"></div><p class="archive-muted">${tr('原始文件来自发布方。若设备不支持内嵌 PDF，可使用下方来源链接。','The document is hosted by its publisher. If inline PDF is unsupported, use the source link below.')}</p></details>`:''}</section>`;
  }
  async function openWork(w,scroll=true){
    const own=++request;active=w;currentNote=null;updateURL();renderList();
    $('archiveReader').innerHTML=`<p class="archive-muted archive-loading">${tr('正在载入正文…','Loading study edition…')}</p>`;
    try{
      if(w.noteFile){if(!/^archive\/notes\/[a-z0-9_-]+\.json$/.test(w.noteFile))throw Error('Invalid content path');const r=await fetch(w.noteFile);if(!r.ok)throw Error('Note unavailable');const n=await r.json();if(own!==request)return;currentNote=n;}
      if(own!==request)return;renderWork(w,currentNote);attachMedia();
    }catch(e){if(own!==request)return;renderWork(w,null);attachMedia();$('archiveReader').insertAdjacentHTML('afterbegin',`<p role="alert">${tr('正文暂未载入。请重新选择本篇重试。','Study edition could not be loaded. Select this work again to retry.')}</p>`);}
    if(scroll){if(matchMedia('(max-width:650px)').matches){$('archiveCatalog').classList.add('catalog-folded');updateCatalogToggle();}$('archiveReader').scrollIntoView({block:'start',behavior:'auto'});$('archiveReader').focus({preventScroll:true});}
  }
  function updateCatalogToggle(){const folded=$('archiveCatalog').classList.contains('catalog-folded');$('archiveCatalogToggle').setAttribute('aria-expanded',String(!folded));$('archiveCatalogToggle').textContent=folded?tr('展开作品目录与搜索','Open catalogue & search'):tr('收起作品目录','Close catalogue');}
  function attachMedia(){
    $('archiveReader').querySelectorAll('.archive-media details').forEach(d=>d.addEventListener('toggle',()=>{
      if(!d.open)return;
      const v=d.querySelector('[data-video]'),p=d.querySelector('[data-pdf]'),provider=d.querySelector('[data-provider]');
      if(v&&!v.children.length){const f=document.createElement('iframe');f.src=`https://www.youtube-nocookie.com/embed/${v.dataset.video}`;f.title=tr('原始视频','Original video');f.allow='fullscreen; picture-in-picture';f.referrerPolicy='strict-origin-when-cross-origin';f.allowFullscreen=true;v.append(f);}
      if(p&&!p.children.length){const f=document.createElement('iframe');f.src=p.dataset.pdf;f.title=tr('原始文字稿','Source text');f.style.aspectRatio='3 / 4';p.append(f);}
      if(provider&&!provider.children.length){const f=document.createElement('iframe');f.src=provider.dataset.provider;f.title=tr('原始视频','Original video');f.allowFullscreen=true;provider.append(f);}
    }));
  }
  async function init(){
    try{
      const rs=await Promise.all([fetch('archive/catalog.json'),fetch('investors.json')]);if(rs.some(r=>!r.ok))throw Error('Catalogue unavailable');
      [catalog,people]=await Promise.all(rs.map(r=>r.json()));if(!Array.isArray(people))people=people.investors;
      catalog.methodHTML=$('archiveMethod').innerHTML;
      if(matchMedia('(max-width:650px)').matches)$('archiveCatalog').classList.add('catalog-folded');
      $('archiveInvestor').innerHTML=people.map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
      const q=new URLSearchParams(location.search);setPerson(q.get('investor')||'lilu',q.get('work'));
      $('archiveInvestor').addEventListener('change',e=>setPerson(e.target.value));
      $('archiveCatalogToggle').addEventListener('click',()=>{$('archiveCatalog').classList.toggle('catalog-folded');updateCatalogToggle();});
      $('catalogLink').addEventListener('click',()=>{$('archiveCatalog').classList.remove('catalog-folded');updateCatalogToggle();});
      for(const id of ['archiveSearch','archiveKind','archiveSort','archiveReady'])$(id).addEventListener(id==='archiveSearch'?'input':'change',()=>{page=0;renderList();});
      $('archiveList').addEventListener('click',e=>{const b=e.target.closest('[data-work]');if(b)openWork(catalog.works.find(w=>w.id===b.dataset.work));});
      $('archivePagination').addEventListener('click',e=>{const b=e.target.closest('[data-page]');if(b){page+=Number(b.dataset.page);renderList();$('archiveList').scrollIntoView({block:'start'});}});
      $('archiveReader').addEventListener('click',e=>{const b=e.target.closest('[data-mode]');if(b){mode=b.dataset.mode;renderHeading();renderList();renderWork(active,currentNote);attachMedia();$('archiveReader').querySelector(`[data-mode="${mode}"]`).focus({preventScroll:true});}});
    }catch(e){$('archiveCoverage').textContent='目录暂未载入，请刷新页面重试。 / Catalogue unavailable; please refresh.';$('archiveReader').innerHTML='<p role="alert">无法载入作品集。已有持仓页面仍可从上方返回。</p>';console.error('Archive:',e.message);}
  }
  init();
})();
