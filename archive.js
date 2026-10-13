(function(){
  'use strict';
  const $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  let catalog,people,selected,active,currentText,mode='zh',request=0;
  const tr=(zh,en)=>mode==='en'?en:zh;
  const title=w=>mode==='en'?w.title.en:w.title.zh;
  const ready=w=>w.fullTextStatus==='ready'&&/^archive\/texts\/[a-z0-9_-]+\.json$/.test(w.fullTextFile||'');
  function updateURL(){const u=new URL(location.href);u.searchParams.set('investor',selected);if(active)u.searchParams.set('work',active.id);history.replaceState(null,'',u);}
  function updateControls(){
    $('archiveBack').href=`index.html?investor=${encodeURIComponent(selected)}#readings`;
    $('archiveBack').textContent=tr('← 返回投资人资料','← Investor profile');
    Array.from($('archiveInvestor').options).forEach(o=>{const p=people.find(p=>p.id===o.value);o.textContent=mode==='en'?p.nameEn:p.name;});
    const works=catalog.works.filter(w=>w.investor===selected).sort((a,b)=>(b.date||'').localeCompare(a.date||''));
    $('archiveWork').innerHTML=works.map(w=>`<option value="${esc(w.id)}">${esc((w.dateLabel?.[mode==='en'?'en':'zh']||w.date||'')+' · '+title(w))}</option>`).join('');
    if(active)$('archiveWork').value=active.id;
    $('archiveInvestor').setAttribute('aria-label',tr('投资人','Investor'));
    $('archiveWork').setAttribute('aria-label',tr('选择篇目','Choose a text'));
    document.documentElement.lang=mode==='en'?'en':'zh-CN';
  }
  function validText(t,w){
    if(t.kind!=='verbatim_text'||t.workId!==w.id||t.reviewStatus!=='verified'||!t.rights?.verified||!t.rights?.allowPublication||!t.rights?.allowTranslation||!t.rights?.evidence)throw Error('Text is not verified for publication');
    if(!['zh','en'].includes(t.originalLanguage)||!t.originalText||!Array.isArray(t.segments)||!t.segments.length)throw Error('Incomplete original text');
    const ids=new Set();
    for(const s of t.segments){if(!s.id||ids.has(s.id)||typeof s.zh!=='string'||typeof s.en!=='string'||!s.zh.trim()||!s.en.trim()||s[t.originalLanguage]!==s.original)throw Error('Missing or altered sentence');ids.add(s.id);}
    if(t.segments.map(s=>s.original).join('')!==t.originalText)throw Error('Original text is incomplete');
    if(t.lead||t.chapters||t.questions)throw Error('Study editions are not original texts');
    return t;
  }
  function render(){
    updateControls();
    if(!active){$('archiveReader').innerHTML=`<p>${tr('尚无可展示的完整文字稿。','No complete text is available yet.')}</p>`;return;}
    document.title=title(active);
    const controls=`<div class="archive-language" role="group" aria-label="${tr('阅读语言','Reading language')}"><button type="button" data-mode="zh" aria-pressed="${mode==='zh'}">中文</button><button type="button" data-mode="en" aria-pressed="${mode==='en'}">English</button><button type="button" data-mode="bilingual" aria-pressed="${mode==='bilingual'}">中英对照</button></div>`;
    const body=currentText?currentText.segments.map(s=>mode==='bilingual'?`<div class="archive-text-pair" data-sentence="${esc(s.id)}"><p lang="zh-CN">${esc(s.zh)}</p><p lang="en" class="archive-en">${esc(s.en)}</p></div>`:`<p class="archive-text-line" lang="${mode==='en'?'en':'zh-CN'}" data-sentence="${esc(s.id)}">${esc(s[mode==='en'?'en':'zh'])}</p>`).join(''):`<p class="archive-text-unavailable" role="status">${esc(tr('本篇完整原文与逐句译稿尚未取得可公开展示的授权，当前没有全文。此前的摘要已撤下。','Publication permission for the complete original and sentence-aligned translation has not been verified. No full text is available here; the previous summaries have been removed.'))}</p>`;
    $('archiveReader').innerHTML=`<h1>${esc(title(active))}</h1><p class="archive-work-meta">${esc(active.dateLabel?.[mode==='en'?'en':'zh']||active.date||'')} · ${esc(mode==='en'?(active.publisherEn||active.publisher):active.publisher)}</p>${controls}${currentText?`<div class="archive-text-downloads"><button type="button" data-download="zh">${tr('下载中文稿','Chinese .txt')}</button><button type="button" data-download="en">${tr('下载英文稿','English .txt')}</button><button type="button" data-download="bilingual">${tr('下载对照稿','Bilingual .txt')}</button></div>`:''}<div class="archive-text-body">${body}</div>`;
  }
  async function openWork(w){
    const own=++request;active=w;currentText=null;updateURL();
    $('archiveReader').innerHTML=`<p role="status">${tr('正在载入正文…','Loading text…')}</p>`;
    try{if(ready(w)){const r=await fetch(w.fullTextFile);if(!r.ok)throw Error('Text unavailable');const t=validText(await r.json(),w);const digest=await crypto.subtle.digest('SHA-256',new TextEncoder().encode(t.originalText));const sha=Array.from(new Uint8Array(digest)).map(b=>b.toString(16).padStart(2,'0')).join('');if(sha!==t.sourceDigest)throw Error('Original digest differs');if(own!==request)return;currentText=t;}if(own===request)render();}
    catch(e){if(own!==request)return;currentText=null;render();$('archiveReader').querySelector('.archive-text-unavailable').textContent=tr('完整稿件未通过核对，暂不显示。请稍后重试。','The complete text could not be verified and is not displayed. Please try again later.');}
  }
  function setPerson(id,preferred){
    selected=people.some(p=>p.id===id)?id:people[0].id;$('archiveInvestor').value=selected;
    const works=catalog.works.filter(w=>w.investor===selected).sort((a,b)=>(b.date||'').localeCompare(a.date||''));
    const w=works.find(w=>w.id===preferred)||works.find(ready)||works[0];
    if(w)openWork(w);else{request++;active=null;currentText=null;render();}
  }
  function download(language){
    if(!currentText)return;
    const text=language===currentText.originalLanguage?currentText.originalText:language==='bilingual'?currentText.segments.map(s=>s.zh+'\n'+s.en).join('\n\n'):currentText.segments.map(s=>s[language]).join('');
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain;charset=utf-8'})),a=document.createElement('a');
    a.href=url;a.download=`${active.id}-${language}.txt`;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  async function init(){
    try{
      const rs=await Promise.all([fetch('archive/catalog.json'),fetch('investors.json')]);if(rs.some(r=>!r.ok))throw Error('Archive unavailable');
      [catalog,people]=await Promise.all(rs.map(r=>r.json()));people=Array.isArray(people)?people:people.investors;
      $('archiveInvestor').innerHTML=people.map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
      const q=new URLSearchParams(location.search);setPerson(q.get('investor')||'lilu',q.get('work'));
      $('archiveInvestor').addEventListener('change',e=>setPerson(e.target.value));
      $('archiveWork').addEventListener('change',e=>openWork(catalog.works.find(w=>w.id===e.target.value)));
      $('archiveReader').addEventListener('click',e=>{const b=e.target.closest('[data-mode]');if(b){mode=b.dataset.mode;render();$('archiveReader').querySelector(`[data-mode="${mode}"]`).focus({preventScroll:true});}const d=e.target.closest('[data-download]');if(d)download(d.dataset.download);});
    }catch(e){$('archiveReader').innerHTML='<p role="alert">文字页暂未载入，请刷新重试。 / Please refresh to retry.</p>';console.error('Text reader:',e.message);}
  }
  init();
})();
