(function(){
  let pending, generation=0;
  function escape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  window.SpeechArchive={async updateInvestor(cfg,en){
    const host=document.getElementById('speechArchiveEntry');if(!host)return;
    const own=++generation;
    const name=en?cfg.nameEn:cfg.name;
    const url=`archive.html?investor=${encodeURIComponent(cfg.id)}`;
    host.innerHTML=`<div class="archive-entry"><div><h3>${escape(name)} · ${en?'Original Texts & Translations':'原文与逐句译稿'}</h3><p>${en?'Complete original texts and sentence-aligned translations only. Summaries have been removed.':'只展示完整原文与逐句译稿，支持中文、英文和逐句对照；此前的摘要已撤下。'}</p><p class="archive-entry-count"></p></div><a href="${url}">${en?'Browse the collection →':'进入作品集 →'}</a></div>`;
    try{
      if(!pending)pending=fetch('archive/catalog.json').then(r=>{if(!r.ok)throw Error('Archive unavailable');return r.json();}).catch(e=>{pending=null;throw e;});
      const catalog=await pending;if(own!==generation)return;
      const items=catalog.works.filter(w=>w.investor===cfg.id),ready=items.filter(w=>w.fullTextStatus==='ready'&&w.fullTextFile).length;
      host.querySelector('.archive-entry-count').textContent=en?`${items.length} entries · ${ready} verified complete texts`:`已建档 ${items.length} 篇 · 完整文字稿 ${ready} 篇`;
    }catch(e){if(own===generation)host.querySelector('.archive-entry-count').textContent=en?'Open the collection to view available works.':'进入作品集查看已有资料。';}
  }};
})();
