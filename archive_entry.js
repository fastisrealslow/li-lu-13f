(function(){
  let pending, generation=0;
  function escape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  window.SpeechArchive={async updateInvestor(cfg,en){
    const host=document.getElementById('speechArchiveEntry');if(!host)return;
    const own=++generation;
    const name=en?cfg.nameEn:cfg.name;
    const url=`archive.html?investor=${encodeURIComponent(cfg.id)}`;
    host.innerHTML=`<div class="archive-entry"><div><h3>${escape(name)} · ${en?'Speeches & Interviews':'演讲与访谈作品集'}</h3><p>${en?'Read sourced study editions on this website. Chinese, English and paragraph-aligned bilingual reading.':'按年代整理公开演讲、访谈与问答，在本站阅读中文整理，并可一键切换英文或逐段中英对照。'}</p><p class="archive-entry-count"></p></div><a href="${url}">${en?'Browse the collection →':'进入作品集 →'}</a></div>`;
    try{
      if(!pending)pending=fetch('archive/catalog.json').then(r=>{if(!r.ok)throw Error('Archive unavailable');return r.json();}).catch(e=>{pending=null;throw e;});
      const catalog=await pending;if(own!==generation)return;
      const items=catalog.works.filter(w=>w.investor===cfg.id),ready=items.filter(w=>w.noteFile).length;
      host.querySelector('.archive-entry-count').textContent=en?`${items.length} catalogued works · ${ready} study editions · Updated ${catalog.updatedAt.slice(0,10)}`:`已收录 ${items.length} 篇 · ${ready} 篇站内整理 · 更新于 ${catalog.updatedAt.slice(0,10)}`;
    }catch(e){if(own===generation)host.querySelector('.archive-entry-count').textContent=en?'Open the collection to view available works.':'进入作品集查看已有资料。';}
  }};
})();
