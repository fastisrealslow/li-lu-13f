/* Source-aware presentation for venture portfolios with no quarterly position report. */
(function(win,doc){
  'use strict';
  const escape=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const link=(url,label)=>{try{const u=new URL(url);if(u.protocol!=='https:'||u.username||u.password)return escape(label);return `<a href="${escape(u.href)}" target="_blank" rel="noopener noreferrer">${escape(label)}</a>`;}catch{return escape(label);}};
  const set=(id,html)=>{const el=doc.getElementById(id);if(el)el.innerHTML=html;};
  function block(id,parent){let el=doc.getElementById(id);if(!el){el=doc.createElement('section');el.id=id;el.className='public-portfolio';doc.getElementById(parent).prepend(el);}return el;}
  function render(section,{data,lang,config}){
    const enabled=data?.meta?.portfolioMode==='public_projects', en=lang==='en';
    const text=(zh,english)=>en?english:zh;
    const selectors={'holdings':'#tab-current > .table-wrap','changes':'#tab-changes > .table-wrap','history':'#historyChart'};
    const blocks={holdings:['publicProjects','tab-current'],changes:['publicDisclosures','tab-changes'],history:['publicHistory','tab-history']};
    if(selectors[section]){const el=doc.querySelector(selectors[section]);if(el)(section==='history'?el.parentElement:el).style.display=enabled?'none':'';}
    if(blocks[section]){const [id,parent]=blocks[section];let el=doc.getElementById(id);if(enabled)el=block(id,parent);if(el)el.hidden=!enabled;}
    if(!enabled)return false;
    const projects=data.publicProjects||[], filings=data.publicFilings||[], snapshots=data.projectSnapshots||[], latest=filings[0], oldest=filings.at(-1);
    const panel=(heading,lead,detail='')=>`<div class="scope-heading"><h3>${escape(heading)}</h3></div><p>${escape(lead)}</p>${detail?`<p>${escape(detail)}</p>`:''}`;
    if(section==='summary'){
      set('metaRow',`${escape(text('资料核对','Sources checked'))} <strong>${escape(data.meta.lastUpdated?.slice(0,10))}</strong> · ${link(data.meta.projectSource,text('Lux 官方人物页','Official Lux profile'))} · ${link('https://www.sec.gov/edgar/browse/?CIK='+config.cik+'&owner=exclude','SEC EDGAR')}`);
      const stats=[[projects.length,text('官方投资关联','Official project associations'),text('人物页明确提及','Named in the official profile')],[filings.length,text('权益披露文件','Ownership filings'),text('13D / 13G，含修订','13D / 13G, including amendments')],[latest?.filingDate||'—',text('最近权益申报','Latest ownership filing'),latest?.issuer||''],[snapshots.at(-1)?.observedAt.slice(0,10)||'—',text('项目目录核对','Project snapshot observed'),text('不是买卖发生日期','Not a transaction date')]];
      set('summaryCards',stats.map(([n,label,detail])=>`<div class="stat-item"><div class="stat-primary"><span class="stat-num public-stat">${escape(n)}</span></div><span class="stat-desc">${escape(label)}<small>${escape(detail)}</small></span></div>`).join(''));
    }else if(section==='holdings'){
      doc.getElementById('mosSummary')?.remove();
      set('publicProjects',`<p class="public-context">${escape(text('以下是官方人物页明确提及的投资项目。官网未公开逐项的当前持股数量、市值或退出状态。','These projects are explicitly associated with the investor in the official biography. Current ownership, valuation and exit status are not individually disclosed.'))}</p><div class="table-wrap"><table class="public-table"><thead><tr><th>#</th><th>${text('企业 / 项目','Company / project')}</th><th>${text('公开关联','Public association')}</th><th>${text('来源','Source')}</th></tr></thead><tbody>${projects.map((p,i)=>`<tr><td>${i+1}</td><td><strong>${link(p.url,p.name)}</strong></td><td>${text('Lux 投资项目','Lux investment association')}</td><td>${link(p.sourceUrl,text('官方人物页','Official profile'))}</td></tr>`).join('')}</tbody></table></div>`);
    }else if(section==='changes'){
      set('publicDisclosures',`<p class="public-context">${escape(text('按实际提交日期排列。13D / 13G 是特定公司的权益披露，不是季度买卖清单；修订文件与原始文件各保留一行。','Ordered by actual filing date. Forms 13D / 13G disclose beneficial ownership in specific issuers rather than quarterly trades. Originals and amendments are retained separately.'))}</p><div class="table-wrap"><table class="public-table"><thead><tr><th>${text('申报日期','Filed')}</th><th>${text('申报对象','Issuer')}</th><th>${text('文件类型','Form')}</th><th>${text('原始文件','Original document')}</th></tr></thead><tbody>${filings.map(f=>`<tr><td>${escape(f.filingDate)}</td><td><strong>${escape(f.issuer)}</strong></td><td>${escape(f.form)}</td><td>${link(f.url,'SEC ↗')}</td></tr>`).join('')}</tbody></table></div>`);
    }else if(section==='history'){
      const mobile=doc.getElementById('historyMobileWrap');if(mobile){mobile.innerHTML='';mobile.style.display='none';}
      set('publicHistory',`<h3>${text('有日期的公开记录','Dated public records')}</h3><ol class="public-history">${filings.map(f=>`<li><time>${escape(f.filingDate)}</time><span>${escape(f.issuer)} · ${link(f.url,f.form)}</span></li>`).join('')}</ol>`);
    }else if(section==='timeline'){
      set('timelineCanvas',`<div class="public-observations"><h4>${text('官方项目目录的观测记录','Official project observations')}</h4>${snapshots.map(s=>`<p><time>${escape(s.observedAt.slice(0,10))}</time> · ${s.projects.length} ${text('个官方关联项目','official project associations')}</p>`).join('')}</div>`);
    }else if(section==='insights'){
      set('holdingsInsight',panel(text('投资项目解读','Project associations'),text(`官方人物页明确提及 ${projects.length} 家企业，覆盖人工智能、计算、机器人、国防、能源与生命科学。这里反映的是研究与投资关联，不能按持股金额排出“第一重仓”。`,`The official biography names ${projects.length} companies spanning AI, computing, robotics, defense, energy and life sciences. These associations describe a research and investment footprint, without amounts from which to rank positions.`),text('其中既有从零共同创办的企业，也有参与投资的项目。逐项研究更适合追问技术突破、工程约束、团队与商业化路径；页面不把未披露的数量或估值填成零。','The footprint includes company formation as well as investment. Research can focus on technical breakthroughs, engineering constraints, teams and commercialization; undisclosed quantities and values are not represented as zero.')));
      set('changesAISummary',panel(text('公开披露解读','Ownership disclosure review'),latest?text(`已核对 ${filings.length} 份权益文件，最新一份提交于 ${latest.filingDate}，对象为 ${latest.issuer}。页面每日复查 SEC；没有新文件时，原始申报日期保持不变。`,`There are ${filings.length} checked ownership filings. The latest was filed on ${latest.filingDate} for ${latest.issuer}. Daily SEC checks preserve the original dates when no newer document exists.`):text('该主体暂无可确认的权益申报。','No verified ownership filings are available for this entity.'),text('13D / 13G 的修订可能反映持股比例、股数或申报关系变化，必须阅读对应文件后才可判断；项目目录新增也不等于刚刚买入。','An ownership amendment may concern shares, percentages or reporting relationships and needs to be read as filed. A newly observed directory entry is not evidence of a recent purchase.')));
      set('insightsList','');
      set('historyInsight',panel(text('披露历史解读','Disclosure history'),oldest?text(`当前可核对的权益文件日期从 ${oldest.filingDate} 至 ${latest.filingDate}；项目目录从首次观测日起另外留存。两条时间线分别记录“提交过什么”和“当时官网列了什么”。`,`The checked ownership filings run from ${oldest.filingDate} to ${latest.filingDate}. Directory observations are retained separately from their first observation date, distinguishing what was filed from what the website listed.`):text('项目目录从首次核对日期开始保存。','Directory history begins on the first checked observation date.'),text('Lux 没有可用的季度 13F 持仓序列，因此这里按真实事件呈现历史，不绘制虚构的组合市值或收益曲线。','Lux has no available quarterly 13F position series, so history is presented as dated events rather than an invented portfolio value or return curve.')));
    }
    return true;
  }
  win.PublicPortfolio={render};
})(window,document);
