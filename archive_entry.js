(function(){
  let pending,guidesPending,explanationsPending,generation=0;
  function escape(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));}
  const load=url=>fetch(url,{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Archive unavailable');return r.json();});
  window.SpeechArchive={async updateInvestor(cfg,en){
    const host=document.getElementById('speechArchiveEntry');if(!host)return;
    const own=++generation,key=en?'en':'zh',name=en?cfg.nameEn:cfg.name,url=`archive.html?v=2&investor=${encodeURIComponent(cfg.id)}`;
    host.innerHTML=`<div class="archive-entry"><div><h3>${escape(name)} · ${en?'Works & Detailed Reading Guides':'公开作品与详细导读'}</h3><p>${en?'Read the investor’s approach, the works in their historical context, and source-grounded AI explanations.':'结合人物方法、作品年代和原始来源，理解文章、演讲与访谈；AI 导读与原文明确区分。'}</p><p class="archive-entry-count"></p></div><a href="${url}">${en?'Read the collection →':'阅读作品与导读 →'}</a></div>`;
    try{
      if(!pending)pending=load('archive/catalog.json').catch(e=>{pending=null;throw e;});
      if(!guidesPending)guidesPending=load('archive/guides.json').catch(()=>{guidesPending=null;return {guides:{}};});
      if(!explanationsPending)explanationsPending=load('archive/explanations/index.json?v=3').catch(()=>{explanationsPending=null;return {entries:{}};});
      const [catalog,guides,index]=await Promise.all([pending,guidesPending,explanationsPending]);if(own!==generation)return;
      const items=catalog.works.filter(w=>w.investor===cfg.id),ready=items.filter(w=>{const e=index.entries?.[w.id];return e&&e.reviewStatus==='verified'&&e.sourceBasis!=='description'&&e.catalogDate===w.date&&e.catalogTitle===w.title.en;}).length,g=guides.guides?.[cfg.id];
      if(g){
        const intro=g.sections[0].paragraphs[1][key];
        const more=g.sections.map((s,i)=>`<h4>${escape(s.heading[key])}</h4>${s.paragraphs.filter((p,j)=>i!==0||j!==1).map(p=>`<p>${escape(p[key])}</p>`).join('')}`).join('');
        host.innerHTML=`<div class="archive-entry"><div><h3>${escape(name)} · ${en?'Works & Detailed Reading Guides':'公开作品与详细导读'}</h3><p>${escape(intro)}</p><details class="archive-entry-guide"><summary>${en?'Expand the full collection guide':'展开完整作品导读'}</summary>${more}<p class="archive-ai-label">${escape(g.label[key])}</p></details><p class="archive-entry-count"></p></div><a href="${url}">${en?'Read the collection →':'阅读作品与导读 →'}</a></div>`;
      }
      host.querySelector('.archive-entry-count').textContent=en?`${items.length} catalogued works · ${ready} individual reading guides`:`已建档 ${items.length} 篇 · 已有导读 ${ready} 篇`;
    }catch(e){if(own===generation)host.querySelector('.archive-entry-count').textContent=en?'Open the collection to view available works.':'进入作品集查看已有资料。';}
  }};
})();
