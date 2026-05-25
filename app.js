// ========== i18n ==========
let lang = localStorage.getItem('lang') || 'zh';
const T = {
  // Nav
  navHoldings: ['持仓数据','Holdings'],
  navAbout: ['关于李录','About'],
  navPhilosophy: ['投资理念','Philosophy'],
  navReadings: ['阅读材料','Readings'],
  // Hero
  heroTitle: ['李录 13F 持仓追踪','Li Lu 13F Tracker'],
  heroSub: ['Himalaya Capital · SEC 13F · 价值投资','Himalaya Capital · SEC 13F · Value Investing'],
  // Tabs
  tabCurrent: ['持仓明细','Holdings'],
  tabChanges: ['季度变化','QoQ Changes'],
  tabHistory: ['历史趋势','History'],
  tabTimeline: ['⏳ 时间轴','⏳ Timeline'],
  // Table headers
  thTicker: ['代码','Ticker'],
  thCompany: ['公司','Company'],
  thSector: ['行业','Sector'],
  thShares: ['持股数','Shares'],
  thPrice: ['参考股价 ⓘ','Price ⓘ'],
  thCost: ['估算成本 ⓘ','Est. Cost ⓘ'],
  thValue: ['市值 (USD)','Value (USD)'],
  thWeight: ['权重','Weight'],
  thPct: ['占比','%'],
  thFirst: ['首次建仓','First Buy'],
  thLast: ['最后持有','Last Held'],
  thQCount: ['持有季度','Quarters'],
  thPosition: ['仓位变动','Position'],
  thStatus: ['状态','Status'],
  // Philosophy cards
  philDeep: ['深度研究','Deep Research'],
  philFocus: ['集中持仓','Concentrated'],
  philLong: ['长期视角','Long-Term View'],
  philMargin: ['安全边际','Margin of Safety'],
  philCircle: ['能力圈','Circle of Competence'],
  philFish: ['在对的地方钓鱼','Fish Where Fish Are'],
  // About timeline
  tlBorn: ['出生于唐山，十岁时亲历唐山大地震','Born in Tangshan, survived 1976 earthquake at age 10'],
  tlUniv: ['考入南京大学，先修物理后转经济','Entered Nanjing University, physics to economics'],
  tlUS: ['赴美，入读哥伦比亚大学','Moved to US, Columbia University'],
  tlDegree: ['哥大获 BA / JD / MBA 三学位','BA/JD/MBA triple degree, Columbia'],
  tlFound: ['创立喜马拉雅资本管理公司','Founded Himalaya Capital Management'],
  tlBYD: ['向芒格推荐比亚迪','Recommended BYD to Munger'],
  tlOngoing: ['持续管理喜马拉雅资本，坚守价值投资','Managing Himalaya Capital, value investing'],

  aboutP1: ['李录（Li Lu），1966 年生于唐山，美籍华裔价值投资者，喜马拉雅资本创始人。','Li Lu (b. 1966), Chinese-American value investor, founder of Himalaya Capital.'],
  aboutP2: ['李录（Li Lu），1966 年生于唐山，美籍华裔价值投资者，喜马拉雅资本创始人。','Li Lu (b. 1966), Chinese-American value investor and founder of Himalaya Capital.'],
  aboutP3: ['1997 年创立喜马拉雅资本，专注长期价值投资。','Founded Himalaya Capital in 1997, focused on long-term value investing.'],
  aboutP4: ['除投资外，李录也热心公益，设立了人道主义基金会，关注人权、教育和救灾。','Active in philanthropy: humanitarian foundation focused on human rights, education, and disaster relief.'],
  philDBody: ['全面尽职调查——财务报表、行业动态、竞争地位，确保充分了解企业基本面。','Thorough due diligence on financials, industry dynamics, and competitive positioning.'],
  philFBody1: ['不追求广泛分散，资金集中在少数高确信度投资上。','Concentrated in a few high-conviction investments.'],
  philFBody2: ['只持仓。',' holdings.'],
  philLBody: ['以十年为周期持有，让复利充分发挥。','Held for decades, letting compounding work fully.'],
  philMBody: ['以显著低于内在价值的价格买入，为不可预见的风险提供缓冲。','Buying well below intrinsic value to buffer against unforeseen risks.'],
  philCBody: ['清楚知道自己理解什么、不理解什么。只在真正有优势的领域投资。','Know what you understand. Invest only where you have an edge.'],
  philFishBody: ['芒格钓鱼的故事——投资者不需要理解所有公司。','Mungers fishing story: you need not understand every company.'],

  // Footer
  ftDisclaimer: ['本页面仅展示 SEC 13F 公开披露信息，不构成投资建议。13F 仅披露美股多头持仓。','Displays public SEC 13F disclosures only. Not investment advice.'],
  ftUpdate: ['数据更新：','Updated: '],
  ftAuto: ['· GitHub Actions 每周一自动更新','· Auto-updated weekly via GitHub Actions'],
  // Cost labels
  costRecent: ['最近成本','Recent Cost'],
  costAllTime: ['历史均价','All-Time Avg'],
  // Sector translations
  secTech: ['科技','Tech'],
  secInternet: ['互联网','Internet'],
  secEcom: ['电商','E-commerce'],
  secFinance: ['金融','Finance'],
  secConglomerate: ['综合金融','Conglomerate'],
  secConsumer: ['消费','Consumer'],
  secEnergy: ['能源','Energy'],
  secEntertain: ['娱乐','Entertainment'],
  secFinSvc: ['金融服务','Fin. Services'],
  secSemi: ['半导体','Semiconductor'],
  secSocial: ['社交','Social'],
  secAuto: ['汽车/新能源','Auto/New Energy'],
  secIndustrial: ['工业/轨交','Industrial/Rail'],
  secBanking: ['金融/银行','Banking'],
  secOther: ['其他','Other'],
  // Changes table
  changesPS: ['上季持股','Prev'],
  changesCS: ['本季持股','Cur'],
  changesChg: ['持股变化','Change'],
  changesPV: ['上季市值','Prev Value'],
  changesCV: ['本季市值','Cur Value'],
  changesVChg: ['市值变化','Value Chg'],

  // Summary stat line (used in renderAll)
  statValue: ['组合市值','Portfolio'],
  statCount: ['只持仓','holdings'],
  statTop3: ['TOP3','TOP3'],
  statQuarter: ['报告期','Report'],
  statVs: ['较','vs'],
  // Insights
  insightTitle: ['📌 本季度关键动态','📌 Key Quarter Insights'],
  // Timeline section
  tlTitle: ['持仓时间轴','Holdings Timeline'],
  tlSub: ['每行展示一只股票在投资组合中的持有时间与仓位变化','Duration & position change for each holding'],
  // HK section
  hkTitle: ['🇭🇰 港股持仓','🇭🇰 HK Holdings'],
  hkSub: ['13F 仅披露美股多头持仓。以下港股数据来源于港交所权益披露(di.hkex.com.hk)、公开报道等。','13F only covers US long positions. HK data from HKEX SFC DI system & public records.'],
  // Price note
  priceNote: ['💡 参考股价 = Finnhub 每周拉取（非实时） | 最近成本 = 最近一次建仓买入估算 | 历史均价 = 全周期持仓季度中位数','💡 Price = Finnhub weekly (not real-time) | Recent Cost = latest buy-in estimate | All-Time Avg = median across all holding quarters'],
  // Quote
  quote: ['"宏观是我们必须接受的，微观是我们有所作为的。"','"The macro is what we must accept; the micro is what we can act on."'],
  quoteAttr: ['— 李录，北京大学演讲，2024年12月','— Li Lu, Peking University, Dec 2024'],
  // About
  aboutLabel: ['About Li Lu','About Li Lu'],
  aboutTitle: ['关于李录与喜马拉雅资本','About Li Lu & Himalaya Capital'],
  // Philosophy
  philLabel: ['Philosophy','Philosophy'],
  philTitle: ['投资理念 — 格雷厄姆 → 巴菲特 → 芒格 → 李录','Philosophy — Graham → Buffett → Munger → Li Lu'],
  // Readings
  readLabel: ['Readings','Readings'],
  readTitle: ['学习材料','Learning Resources'],
  // Footer
  footerTitle: ['李录 13F 持仓追踪','Li Lu 13F Tracker'],
  footerTagline: ['— 克隆、学习、跟踪大师持仓变化','— Clone, learn, track master portfolio changes'],
  footerDisclaimer: ['本页面仅展示 SEC 13F 公开披露信息，不构成投资建议。13F 仅披露美股多头持仓。','This page displays public SEC 13F disclosures only. Not investment advice. 13F covers US long positions only.'],
  footerUpdate: ['数据更新：','Updated: '],
  footerWeekly: ['· GitHub Actions 每周一自动更新',' · Auto-updated weekly via GitHub Actions'],
  // Status labels in timeline
  stHolding: ['● 持有中','● Holding'],
  stExited: ['○ 已清仓','○ Exited'],
  stReboughtQ: ['清仓','exited'],
  stReboughtB: ['重新买入（空窗','rebought (gap '],
  stReboughtB2: ['季）','q)'],
  stPositionFull: ['持有','full'],
  stPositionReduced: ['已减持','reduced'],
  stPositionMaxTo: ['最高','max'],
  stPositionCurTo: ['当前','now'],
  // Insights dynamic
  insNew: ['新增 ','New '],
  insNew2: ['个仓位:',' positions:'],
  insExpand: ['显著拓展了持仓广度','broadening portfolio scope'],
  insSell: ['大幅减持约 ',' sold ~'],
  insSell2: ['卖出约 ','sold ~'],
  insSell3: [' 股',' shares'],
  insBuy: ['增持 ','added '],
  insBuy2: ['加仓约 ','bought ~'],
  insBuy3: [' 股',' shares'],
  insUnchanged: ['持股数未变，波动仅来自股价变化','shares unchanged, price movement only'],
  insTop3: ['前三大持仓占总市值约 ','Top 3 positions: ~'],
  insTop3b: ['集中度极高，反映深度价值投资风格','of portfolio, reflecting deep value investing'],
  // Changes table
  chPrevShares: ['上季持股','Prev Shares'],
  chCurShares: ['本季持股','Cur Shares'],
  chChange: ['持股变化','Δ Shares'],
  chPrevValue: ['上季市值','Prev Value'],
  chCurValue: ['本季市值','Cur Value'],
  chValueChg: ['市值变化','Δ Value'],
  // Cost basis labels
  costRecent: ['最近成本','Recent Cost'],
  costAllTime: ['历史均价','All-Time Avg'],
  // Data source
  srcAuto: ['📦 GitHub Actions 每周自动更新','📦 Auto-updated weekly via GitHub Actions'],
  srcLive: ['✅ SEC 实时数据','✅ SEC live data'],
  // Meta
  metaReport: ['报告期','Report Period'],
  metaFiling: ['提交日','Filed'],
  metaPeriod: ['截至','as of'],
  // Company name translations (Chinese display names)
  cnName: {
    'APPLE INC':'苹果','ALPHABET INC':'Alphabet','BK OF AMERICA CORP':'美国银行',
    'BERKSHIRE HATHAWAY INC DEL':'伯克希尔·哈撒韦','CROCS INC':'Crocs',
    'EAST WEST BANCORP INC':'华美银行','BLOCK H & R INC':'H&R Block',
    'MOODYS CORP':'穆迪','MSCI INC':'MSCI','OCCIDENTAL PETE CORP':'西方石油',
    'PDD HOLDINGS INC':'拼多多','S&P GLOBAL INC':'标普全球',
    'TENCENT MUSIC ENTMT GROUP':'腾讯音乐','SABLE OFFSHORE CORP':'Sable Offshore',
    'MICRON TECHNOLOGY INC':'美光科技','FACEBOOK INC':'Facebook',
    'META PLATFORMS INC':'Meta','PINDUODUO INC':'拼多多',
    'ALIBABA GROUP HLDG LTD':'阿里巴巴','Sina Corp':'新浪',
    'Baidu Inc':'百度','Weibo Corp':'微博',
    'BERKSHIRE HATHAWAY INC':'伯克希尔·哈撒韦',
  },

};
function t(key) { const v = T[key]; return v ? v[lang==='en'?1:0] : key; }
function cn(name) { return lang==='zh' ? (T.cnName[name] || name) : name; }
function ts(s) {
  const sm = {'科技':'secTech','互联网':'secInternet','电商':'secEcom','金融':'secFinance',
    '综合金融':'secConglomerate','消费':'secConsumer','能源':'secEnergy','娱乐':'secEntertain',
    '金融服务':'secFinSvc','半导体':'secSemi','社交':'secSocial','汽车/新能源':'secAuto',
    '工业/轨交':'secIndustrial','金融/银行':'secBanking'};
  return t(sm[s] || 'secOther');
}
function switchLang() {
  lang = lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('lang', lang);
  document.getElementById('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = t(el.dataset.i18n);
    if (el.childElementCount === 0) el.textContent = v;
  });
  renderAll();

}

// ========== FORMAT HELPERS ==========
function fmtVal(v) {
  if (v >= 1e9) return (v/1e9).toFixed(2)+' B';
  if (v >= 1e6) return (v/1e6).toFixed(0)+' M';
  return v.toLocaleString();
}
function fmtNum(n) {
  if (n >= 1e6) return (n/1e6).toFixed(2)+'M';
  if (n >= 1e3) return (n/1e3).toFixed(1)+'K';
  return n.toLocaleString();
}
function fmtPct(cur, prev) {
  if (prev===0) return '<span class="qoq-new">新进</span>';
  const p=((cur-prev)/prev*100);
  if (Math.abs(p)<0.05) return '<span class="qoq-flat">-</span>';
  const c=p>0?'qoq-up':'qoq-down', s=p>0?'+':'';
  return `<span class="${c}">${s}${p.toFixed(1)}%</span>`;
}
function fmtShareChg(cur, prev) {
  if (prev===0) return '<span class="qoq-new">新进</span>';
  const d=cur-prev;
  if (d===0) return '<span class="qoq-flat">不变</span>';
  const p=(d/prev*100), c=d>0?'qoq-up':'qoq-down', s=d>0?'+':'';
  return `<span class="${c}">${s}${fmtNum(Math.abs(d))} (${s}${p.toFixed(1)}%)</span>`;
}

// ========== DATA ==========
let data = null;
let prices = null;  // loaded from prices.json (generated by GitHub Action)
let hkHoldings = null;  // loaded from hk_holdings.json

async function loadPrices() {
  try {
    const resp = await fetch('prices.json?t=' + Date.now());
    prices = await resp.json();
    document.getElementById('priceUpdate').textContent =
      prices.updated ? new Date(prices.updated).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'}) : '待更新';
  } catch(e) {
    console.log('prices.json unavailable');
    prices = { quotes: {}, costBasis: {} };
    document.getElementById('priceUpdate').textContent = '暂不可用';
  }
}

function fmtTicker(tk) {
  // Handle unmapped tickers (prefixed with ? in fetch_13f.py)
  const unmapped = tk && tk.startsWith('?');
  const display = unmapped ? tk.substring(1) : tk;
  const style = unmapped ? 'color:#f59e0b;cursor:help' : '';
  const title = unmapped ? ' title="未映射的股票，需在 TICKER_MAP 中添加"' : '';
  return `<span class="ticker" style="${style}"${title}>${display}</span>`;
}

// ========== LIVE SEC FETCH (direct from browser, for non-China users) ==========
async function tryLiveFetch() {
  const UA = 'Himalaya-13F-Tracker/1.0';
  const CIK = '1709323';
  const subResp = await fetch(`https://data.sec.gov/submissions/CIK${CIK.padStart(10,'0')}.json`,{headers:{'User-Agent':UA}});
  if (!subResp.ok) throw new Error('SEC unreachable');
  const sub = await subResp.json();
  const rec = sub.filings.recent;
  const filings = [];
  for (let i=0; i<rec.form.length && filings.length<2; i++) {
    if (rec.form[i]==='13F-HR') filings.push({
      accession: rec.accessionNumber[i].replace(/-/g,''),
      accessionDashed: rec.accessionNumber[i],
      filingDate: rec.filingDate[i], reportDate: rec.reportDate[i]
    });
  }
  if (filings.length<2) throw new Error('Not enough filings');

  const findInfo = async (acc, accD) => {
    const base = `https://www.sec.gov/Archives/edgar/data/${CIK}/${acc}`;
    const html = await (await fetch(`${base}/${accD}-index.html`,{headers:{'User-Agent':UA}})).text();
    const re = /<a\s+href="([^"]+)"[^>]*>([^<]+\.xml)<\/a>\s*<\/td>\s*<td[^>]*>\s*INFORMATION TABLE/gi;
    let m;
    while ((m=re.exec(html))!==null) { if (!m[1].includes('xslForm13F')) return m[1]; }
    const rd=acc.match(/(\d{2})(\d)(\d)$/);
    if (rd) return `/Archives/edgar/data/${CIK}/${acc}/13fhciq${rd[2]}${rd[3]}.xml`;
    throw new Error('No INFOTABLE');
  };
  const [ci, pi] = await Promise.all([
    findInfo(filings[0].accession, filings[0].accessionDashed),
    findInfo(filings[1].accession, filings[1].accessionDashed)
  ]);

  const tkMap = {
    'ALPHABET INC': (c)=>c?.includes('CL A')?'GOOGL':'GOOG',
    'APPLE INC':'AAPL','BK OF AMERICA CORP':'BAC','BERKSHIRE HATHAWAY INC DEL':'BRK.B',
    'CROCS INC':'CROX','EAST WEST BANCORP INC':'EWBC','BLOCK H & R INC':'HRB',
    'MOODYS CORP':'MCO','MSCI INC':'MSCI','OCCIDENTAL PETE CORP':'OXY',
    'PDD HOLDINGS INC':'PDD','S&P GLOBAL INC':'SPGI','TENCENT MUSIC ENTMT GROUP':'TME'
  };
  const secMap = {GOOGL:'科技',GOOG:'科技',AAPL:'科技',BAC:'金融',EWBC:'金融','BRK.B':'综合金融',CROX:'消费',OXY:'能源',PDD:'电商',TME:'娱乐',SPGI:'金融服务',MCO:'金融服务',HRB:'金融服务',MSCI:'金融服务'};
  const parseXML = async (path) => {
    const xml = await (await fetch(`https://www.sec.gov${path}`,{headers:{'User-Agent':UA}})).text();
    const doc = new DOMParser().parseFromString(xml,'application/xml');
    return [...doc.querySelectorAll('infoTable')].map(r=>{
      const nm=r.querySelector('nameOfIssuer')?.textContent?.trim()||'';
      const cl=r.querySelector('titleOfClass')?.textContent?.trim()||'';
      const tk=typeof tkMap[nm]==='function'?tkMap[nm](cl):(tkMap[nm]||nm);
      return {ticker:tk,name:nm,cls:cl,shares:+r.querySelector('sshPrnamt')?.textContent||0,value:+r.querySelector('value')?.textContent||0,sector:secMap[tk]||'其他'};
    });
  };
  const [curH, prevH] = await Promise.all([parseXML(ci), parseXML(pi)]);
  const pm={}; prevH.forEach(h=>pm[h.ticker]=h);
  curH.forEach(h=>{ const p=pm[h.ticker]; h.prevShares=p?.shares||0; h.prevValue=p?.value||0; });
  curH.sort((a,b)=>b.value-a.value);
  const ql = d => { const dt=new Date(d+'T00:00:00'); return dt.getFullYear()+' Q'+(Math.ceil((dt.getMonth()+1)/3)); };
  return {
    quarter: ql(filings[0].reportDate), filingDate: filings[0].filingDate,
    periodEnd: filings[0].reportDate, prevQuarter: ql(filings[1].reportDate),
    totalValue: curH.reduce((s,h)=>s+h.value,0),
    prevTotalValue: prevH.reduce((s,h)=>s+h.value,0),
    holdings: curH, live: true
  };
}

async function refreshLive() {
  const btn = document.getElementById('btnRefresh');
  const src = document.getElementById('dataSource');
  btn.disabled = true; btn.textContent = '⏳ 拉取中...';
  src.textContent = '正在连接 SEC EDGAR...';
  try {
    const ctrl = new AbortController();
    setTimeout(()=>ctrl.abort(), 30000);
    const live = await tryLiveFetch();
    data.current = live; data._live = true;
    renderAll();
    src.textContent = '✅ SEC 实时数据';
  } catch(e) {
    src.textContent = '⚠ SEC 不可达,显示缓存数据';
    console.log('Live fetch failed:', e.message);
  } finally {
    btn.disabled = false; btn.textContent = '🔄 刷新';
  }
}

// ========== TIMELINE & HK HOLDINGS ==========
async function loadHKHoldings() {
  try {
    const resp = await fetch('hk_holdings.json?t=' + Date.now());
    hkHoldings = await resp.json();
  } catch(e) {
    console.log('hk_holdings.json unavailable');
    hkHoldings = { holdings: [], disclaimer: '' };
  }
}

function renderTimeline() {
  const container = document.getElementById('timelineCanvas');
  if (!container || !data.history || !data.history.holdings) {
    if (container) container.innerHTML = '<p style="color:var(--text-lighter);padding:24px;text-align:center;">历史持仓数据尚未加载。请先运行 fetch_13f.py --full。</p>';
    return;
  }
  const holdings = data.history.holdings;
  const quarters = data.history.quarters;

  // Collect all unique tickers and their first/last quarter
  const tickerInfo = {};
  quarters.forEach(q => {
    const hs = holdings[q] || [];
    hs.forEach(h => {
      if (!tickerInfo[h.ticker]) {
        tickerInfo[h.ticker] = {
          ticker: h.ticker,
          name: h.name,
          sector: h.sector,
          firstQ: q,
          lastQ: q,
          firstIdx: quarters.indexOf(q),
          lastIdx: quarters.indexOf(q),
        };
      } else {
        tickerInfo[h.ticker].lastQ = q;
        tickerInfo[h.ticker].lastIdx = quarters.indexOf(q);
      }
    });
  });

  // Sort by first appearance
  const stocks = Object.values(tickerInfo).sort((a,b) => a.firstIdx - b.firstIdx);

  // Sector colors (navy/gold/cream palette)
  const sectorColors = {
    '科技': '#1e3a5f',
    '金融': '#c8a86e',
    '金融服务': '#8b6914',
    '综合金融': '#6b8e5a',
    '消费': '#b45309',
    '能源': '#92400e',
    '电商': '#7c3aed',
    '娱乐': '#db2777',
  };

  const W = container.parentElement.clientWidth - 32;
  const barH = 26;
  const gap = 6;
  const padL = 100, padR = 30, padT = 10, padB = 40;
  const H = padT + stocks.length * (barH + gap) + padB;

  let html = `<div style="overflow-x:auto;"><div style="min-width:${W}px;position:relative;">`;

  // Quarter labels on top
  html += '<div style="position:relative;height:' + padT + padB + 'px;margin-left:' + padL + 'px;">';
  const plotW = W - padL - padR;
  quarters.forEach((q, i) => {
    const x = (i / Math.max(quarters.length - 1, 1)) * plotW;
    const show = i % 2 === 0 || quarters.length <= 10;
    if (show) {
      html += `<span style="position:absolute;left:${x}px;top:0;font-size:10px;color:var(--text-lighter);transform:translateX(-50%);">${q}</span>`;
    }
  });
  html += '</div>';

  // Bars
  stocks.forEach((s, idx) => {
    const y = padT + idx * (barH + gap);
    const x1 = (s.firstIdx / Math.max(quarters.length - 1, 1)) * plotW;
    const x2 = (s.lastIdx / Math.max(quarters.length - 1, 1)) * plotW;
    const bw = Math.max(x2 - x1, 4);
    const color = sectorColors[s.sector] || '#6b7280';
    const dur = s.lastIdx - s.firstIdx + 1;
    html += `<div style="position:relative;height:${barH + gap}px;">`;
    html += `<span style="position:absolute;left:0;top:0;width:${padL - 8}px;font-size:12px;font-weight:600;color:var(--navy);text-align:right;line-height:${barH}px;">${s.ticker}</span>`;
    html += `<div style="position:absolute;left:${padL + x1}px;top:4px;width:${bw}px;height:${barH}px;background:${color};border-radius:4px;opacity:0.85;" title="${s.ticker} (${s.sector})\n${s.firstQ} → ${s.lastQ}\n持有 ${dur} 个季度"></div>`;
    html += `</div>`;
  });

  html += '</div></div>';

  // Legend
  html += '<div style="margin-top:16px;display:flex;flex-wrap:wrap;gap:12px;">';
  Object.entries(sectorColors).forEach(([sector, color]) => {
    const has = stocks.some(s => s.sector === sector);
    if (has) html += `<span style="display:inline-flex;align-items:center;gap:4px;font-size:11px;color:var(--text-light);"><span style="display:inline-block;width:12px;height:12px;border-radius:3px;background:${color};"></span>${sector}</span>`;
  });
  html += '</div>';

  container.innerHTML = html;
}

function renderHKHoldings() {
  const container = document.getElementById('hkHoldingsTable');
  if (!container || !hkHoldings) return;

  if (!hkHoldings.holdings.length) {
    container.innerHTML = '<p style="color:var(--text-lighter);padding:16px;">暂无港股持仓数据。</p>';
    return;
  }

  let html = '';
  hkHoldings.holdings.forEach((h, i) => {
    const qualityTag = h.data_quality === 'rumored' ? '<span class="tag" style="background:#fef3c7;color:#92400e;">传闻</span>' :
                       h.data_quality === 'estimated' ? '<span class="tag" style="background:#dbeafe;color:#1e40af;">估算</span>' :
                       '<span class="tag">已确认</span>';
    const statusTag = h.current_status === 'reduced' ? '<span style="color:var(--down);font-size:.72rem;">减持中</span>' :
                      h.current_status === 'active' ? '<span style="color:var(--up);font-size:.72rem;">活跃</span>' :
                      '<span style="color:var(--text-lighter);font-size:.72rem;">未知</span>';
    const peakStr = h.peak_shares_approx ? fmtNum(h.peak_shares_approx) + ' 股' : '未知';

    html += `<div style="padding:16px;border:1px solid var(--border-light);border-radius:8px;margin-bottom:12px;background:var(--bg);">
      <div style="display:flex;align-items:center;gap:12px;margin-bottom:8px;">
        <span style="font-weight:700;color:var(--navy);font-size:1rem;">${h.ticker}</span>
        <span style="font-size:.88rem;color:var(--text);">${cn(h.name)}</span>
        <span class="tag">${h.sector}</span>
        ${qualityTag}
        ${statusTag}
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(140px,1fr));gap:8px;font-size:.82rem;color:var(--text-light);margin-bottom:8px;">
        <div><strong style="color:var(--navy);">首次建仓:</strong> ${h.first_acquired}</div>
        <div><strong style="color:var(--navy);">峰值持仓:</strong> ${peakStr}</div>
        <div><strong style="color:var(--navy);">峰值年份:</strong> ${h.peak_year || '未知'}</div>
      </div>
      <div style="font-size:.8rem;color:var(--text-lighter);line-height:1.6;">${h.notes}</div>
    </div>`;
  });

  if (hkHoldings.disclaimer) {
    html += `<div style="margin-top:12px;padding:12px 16px;background:var(--cream);border-radius:6px;font-size:.74rem;color:var(--text-lighter);line-height:1.6;">⚠️ ${hkHoldings.disclaimer}</div>`;
  }

  container.innerHTML = html;
}

// ========== RENDER ==========
function renderSummary() {
  const d = data.current;
  const tc = d.totalValue - (d.prevTotalValue||0);
  const tp = d.prevTotalValue ? (tc/d.prevTotalValue*100) : 0;
  const cls = tc>=0?'up':'down', sign=tc>=0?'+':'';
  const t3 = d.holdings.slice(0,3);
  document.getElementById('summaryCards').innerHTML = `
    <div class="stat-line">
      <div class="stat-item">
        <span class="stat-num" style="font-size:1.5rem;">$${fmtVal(d.totalValue)}</span>
        <span class="stat-change ${cls}">${sign}${tp.toFixed(1)}%</span>
        <span class="stat-desc">${t('statValue')} · ${t('statVs')} ${d.prevQuarter||''}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">${d.holdings.length}</span>
        <span class="stat-desc">${t('statCount')}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">${(t3.reduce((s,h)=>s+h.value,0)/d.totalValue*100).toFixed(1)}%</span>
        <span class="stat-desc">${t('statTop3')} ${t3.map(h=>h.ticker).join('·')}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <span class="stat-num">${d.quarter}</span>
        <span class="stat-desc">${t('statQuarter')} · ${t('metaPeriod')} ${d.periodEnd}</span>
      </div>
    </div>
  `;
}


function renderHoldings() {
  const d = data.current;
  const quotes = prices?.quotes || {};
  const costBasis = prices?.costBasis || {};
  // countBadge removed
  document.getElementById('holdingsBody').innerHTML = d.holdings.map((h,i)=>{
    const pct=(h.value/d.totalValue*100).toFixed(2);
    const q = quotes[h.ticker];
    const cb = costBasis[h.ticker];
    const priceHtml = (q && !q.error) ? `$${q.c.toFixed(2)}` : '<span style="color:var(--text-lighter)">--</span>';
    let costHtml = '<span style="color:var(--text-lighter)">--</span>';
    if (cb && cb.recent && !cb.recent.error) {
      const rc = cb.recent;
      const at = cb.allTime;
      const currentPrice = (q && !q.error) ? q.c : (h.value / h.shares);
      const pnl = ((currentPrice - rc.buy) / rc.buy * 100).toFixed(1);
      const pnlClass = pnl >= 0 ? 'qoq-up' : 'qoq-down';
      const pnlSign = pnl >= 0 ? '+' : '';
      const isYahoo = rc.source === 'yahoo';
      const srcBadge = isYahoo ? '<span style="color:#10b981;font-size:.55rem;">K线</span>' : '<span style="color:#f59e0b;font-size:.55rem;">13F估</span>';
      costHtml = `<div title="近期 ${rc.quarter}: 买入估算 $${rc.buy} [$${rc.low}-$${rc.high}]\n${isYahoo?'Yahoo历史K线, 偏低价加权':'13F 市值/股数'}`;
      if (at) costHtml += `\n\n全周期 (${at.first}~${at.last}, ${at.quarters}季): 均价 $${at.avg}`;
      costHtml += `" style="cursor:help">`;
      costHtml += `<div style="font-weight:600">$${rc.buy}</div>`;
      costHtml += `<div style="font-size:.65rem;color:var(--text-lighter);">${t('costRecent')} ${srcBadge} <span class="${pnlClass}" style="font-weight:500;">${pnlSign}${pnl}%</span></div>`;
      if (at) costHtml += `<div style="font-weight:500;color:var(--navy);margin-top:3px;">$${at.avg}</div>`;
      if (at) costHtml += `<div style="font-size:.6rem;color:var(--text-lighter);">${t('costAllTime')} (${at.quarters}季)</div>`;
      costHtml += `</div>`;
    }
    return `<tr><td>${i+1}</td><td>${fmtTicker(h.ticker)}</td><td>${cn(h.name)}</td><td><span class="tag">${ts(h.sector)}</span></td><td>${fmtNum(h.shares)}</td><td class="price-cell">${priceHtml}</td><td class="cost-cell">${costHtml}</td><td>$${h.value.toLocaleString()}</td><td style="width:100px;"><div class="bar-wrap"><div class="bar-fill" style="width:${pct*3.5}%"></div><span style="font-size:.7rem;font-weight:600;color:var(--navy);margin-left:6px;">${pct}%</span></div></td></tr>`;
  }).join('');
}

function renderChanges() {
  const d = data.current;
  document.getElementById('changesBody').innerHTML = d.holdings.map(h=>{
    const sd=h.shares-(h.prevShares||0), vd=h.value-(h.prevValue||0);
    const sc=h.prevShares===0?'qoq-new':(sd>0?'qoq-up':(sd<0?'qoq-down':'qoq-flat'));
    const vc=h.prevValue===0?'qoq-new':(vd>0?'qoq-up':(vd<0?'qoq-down':'qoq-flat'));
    const ss=sd>0?'+':'', vs=vd>0?'+':'';
    return `<tr><td>${fmtTicker(h.ticker)}</td><td>${cn(h.name)}</td><td>${h.prevShares===0?'-':fmtNum(h.prevShares)}</td><td>${fmtNum(h.shares)}</td><td>${fmtShareChg(h.shares,h.prevShares)}</td><td>${h.prevValue===0?'-':'$'+fmtVal(h.prevValue)}</td><td>$${fmtVal(h.value)}</td><td class="${vc}">${h.prevValue===0?'新进':`${vs}$${fmtVal(Math.abs(vd))} (${fmtPct(h.value,h.prevValue)})`}</td></tr>`;
  }).join('');
}

function renderInsights() {
  const d = data.current, ins = [];
  const np = d.holdings.filter(h=>!h.prevShares);
  if (np.length) ins.push(`${t('insNew')} ${np.length} ${t('insNew2')} ${np.map(h=>h.ticker).join('、')}, ${t('insExpand')}。`);
  const bs = d.holdings.filter(h=>h.prevShares&&h.shares<h.prevShares*0.5);
  bs.forEach(h=>{ const p=((h.prevShares-h.shares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name)})${t('insSell')} ${p}%, ${t('insSell2')} ${fmtNum(h.prevShares-h.shares)} ${t('insSell3')}。`); });
  const inc = d.holdings.filter(h=>h.prevShares&&h.shares>h.prevShares*1.1);
  inc.forEach(h=>{ const p=((h.shares-h.prevShares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name)})${t('insBuy')} ${p}%, ${t('insBuy2')} ${fmtNum(h.shares-h.prevShares)} ${t('insBuy3')}。`); });
  const unch = d.holdings.filter(h=>h.prevShares&&h.shares===h.prevShares);
  if (unch.length) ins.push(`${unch.map(h=>h.ticker).join('、')} ${t('insUnchanged')}。`);
  const t3p = (d.holdings.slice(0,3).reduce((s,h)=>s+h.value,0)/d.totalValue*100).toFixed(0);
  ins.push(`${t('insTop3')} ${t3p}%, ${t('insTop3b')}。`);
  document.getElementById('insightsList').innerHTML = ins.map(s=>`<li>${s}</li>`).join('');
}

function renderHistoryChart() {
  const canvas = document.getElementById('historyChart');
  if (!canvas || !data.history) return;
  const ctx = canvas.getContext('2d');
  const W = canvas.parentElement.clientWidth - 32;
  canvas.width = W; canvas.height = 380;
  const {quarters, values} = data.history;
  const pad = {top:30,right:40,bottom:50,left:65};
  const w=W-pad.left-pad.right, h=380-pad.top-pad.bottom;
  const maxV=Math.ceil(Math.max(...values)/500)*500;
  const minV=Math.floor(Math.min(...values)/500)*500-500;
  ctx.clearRect(0,0,W,380);
  ctx.strokeStyle='#e5e7eb'; ctx.lineWidth=0.5;
  for (let i=0;i<=5;i++) {
    const y=pad.top+(h/5)*i;
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(W-pad.right,y); ctx.stroke();
    const v=maxV-((maxV-minV)/5)*i;
    ctx.fillStyle='#6b7280'; ctx.font='11px -apple-system,sans-serif'; ctx.textAlign='right';
    ctx.fillText('$'+v+'M',pad.left-8,y+4);
  }
  const xStep=w/(quarters.length-1);
  quarters.forEach((q,i)=>{
    if (i%2!==0) return;
    const x=pad.left+xStep*i;
    ctx.fillStyle='#6b7280'; ctx.font='10px -apple-system,sans-serif'; ctx.textAlign='center';
    ctx.save(); ctx.translate(x,pad.top+h+12); ctx.rotate(-0.4); ctx.fillText(q,0,0); ctx.restore();
  });
  const gX=i=>pad.left+xStep*i, gY=v=>pad.top+h-((v-minV)/(maxV-minV))*h;
  ctx.beginPath(); ctx.moveTo(gX(0),gY(values[0]));
  for (let i=1;i<values.length;i++) ctx.lineTo(gX(i),gY(values[i]));
  ctx.strokeStyle='#1e3a5f'; ctx.lineWidth=2.5; ctx.stroke();
  ctx.lineTo(gX(values.length-1),pad.top+h); ctx.lineTo(gX(0),pad.top+h); ctx.closePath();
  const grad=ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  grad.addColorStop(0,'rgba(30,58,95,0.25)'); grad.addColorStop(1,'rgba(30,58,95,0.02)');
  ctx.fillStyle=grad; ctx.fill();
  values.forEach((v,i)=>{
    const x=gX(i),y=gY(v);
    ctx.beginPath(); ctx.arc(x,y,3.5,0,Math.PI*2); ctx.fillStyle='#1e3a5f'; ctx.fill();
    ctx.strokeStyle='#fff'; ctx.lineWidth=1.5; ctx.stroke();
  });
  const last=values.length-1;
  ctx.fillStyle='#1e3a5f'; ctx.font='bold 13px -apple-system,sans-serif'; ctx.textAlign='left';
  ctx.fillText('$'+values[last]+'M',gX(last)+8,gY(values[last])-8);
}

// ── TIMELINE ──
async function renderTimeline() {
  const container = document.getElementById('timelineCanvas');
  const hdata = data.history?.holdings;
  if (!hdata || Object.keys(hdata).length === 0) {
    container.innerHTML = '<p style="text-align:center;color:var(--text-lighter);padding:40px;">历史持仓数据加载中…</p>';
    return;
  }
  const quarters = Object.keys(hdata).sort();
  const latest = quarters[quarters.length - 1];
  const tickerInfo = {};
  for (const q of quarters) {
    for (const h of hdata[q]) {
      const tk = h.ticker;
      if (!tickerInfo[tk]) tickerInfo[tk] = {first: q, last: q, quarters: [], sector: h.sector, name: h.name, maxShares: 0, curShares: 0};
      else tickerInfo[tk].last = q;
      tickerInfo[tk].quarters.push(q);
      if (h.shares > tickerInfo[tk].maxShares) tickerInfo[tk].maxShares = h.shares;
      if (q === latest) tickerInfo[tk].curShares = h.shares;
    }
  }
  const entries = Object.entries(tickerInfo)
    .map(([tk, info]) => {
      // Detect gaps (sell-then-rebuy)
      const allQs = new Set(info.quarters);
      let gaps = [];
      for (let i = quarters.indexOf(info.first); i <= quarters.indexOf(info.last); i++) {
        if (!allQs.has(quarters[i])) gaps.push(quarters[i]);
      }
      return {ticker: tk, ...info, gaps, active: info.last === latest, qCount: info.quarters.length};
    })
    .sort((a, b) => a.first.localeCompare(b.first));

  let html = '<table style="width:100%;font-size:.82rem;"><thead><tr><th>'+t('thTicker')+'</th><th>'+t('thCompany')+'</th><th>'+t('thSector')+'</th><th>'+t('thFirst')+'</th><th>'+t('thLast')+'</th><th>'+t('thQCount')+'</th><th>'+t('thPosition')+'</th><th>'+t('thStatus')+'</th></tr></thead><tbody>';
  entries.forEach(e => {
    if (e.active && e.curShares > 0 && e.maxShares > 0) {
      const ratio = (e.curShares / e.maxShares * 100).toFixed(0);
      const s = e.curShares === e.maxShares
        ? `<span style="color:#10b981;">${ratio}% 持有</span>`
        : `<span style="color:#f59e0b;">${ratio}% 已减持</span>`;
      const shareInfo = ratio < 100 ? `<br><span style="font-size:.68rem;color:var(--text-lighter);">最高 ${fmtNum(e.maxShares)} → 当前 ${fmtNum(e.curShares)}</span>` : '';
      e.shareInfo = s + shareInfo;
    } else {
      e.shareInfo = '<span style="color:var(--text-lighter);">—</span>';
    }
    let status;
    if (e.gaps.length > 0) {
      const soldQ = e.gaps[0];
      const boughtQ = e.gaps[e.gaps.length - 1];
      const beforeGap = quarters[quarters.indexOf(soldQ) - 1];
      const afterGap = quarters[quarters.indexOf(boughtQ) + 1];
      status = `<span style="color:#f59e0b;font-weight:600;">◐ ${beforeGap} 清仓</span><br><span style="font-size:.68rem;color:var(--text-lighter);">→ ${afterGap} 重新买入（空窗${e.gaps.length}季）</span>`;
    } else if (e.active) {
      status = '<span style="color:#10b981;font-weight:600;">● 持有中</span>';
    } else {
      status = '<span style="color:var(--text-lighter);">○ 已清仓</span>';
    }
    html += `<tr>
      <td>${fmtTicker(e.ticker)}</td>
      <td>${cn(e.name)}</td>
      <td><span class="tag">${ts(e.sector)}</span></td>
      <td>${e.first}</td>
      <td>${e.last}</td>
      <td>${e.qCount}</td>
      <td>${e.shareInfo}</td>
      <td>${status}</td>
    </tr>`;
  });
  html += '</tbody></table>';
  html += '<div style="font-size:.68rem;color:var(--text-lighter);margin-top:8px;">● 持有中 = 当前仍在组合内 | ○ 已清仓 = 历史持仓 | ◐ 卖出后重新买入 = 有中断</div>';
  container.innerHTML = html;
  renderHKHoldings();
}

async function renderHKHoldings() {
  const container = document.getElementById('hkHoldingsTable');
  if (!container) return;
  try {
    const resp = await fetch('hk_holdings.json?t=' + Date.now());
    const hk = await resp.json();
    const statusLabels = {below_5pct:'<5% 未披露', active:'>5% 持仓中', reduced:'已减持'};
    const statusColors = {below_5pct:'#f3f4f6;color:#6b7280', active:'#d1fae5;color:#065f46', reduced:'#fef3c7;color:#92400e'};
    container.innerHTML = `
      <div style="overflow-x:auto;"><table style="width:100%;font-size:.82rem;"><thead><tr>
        <th>代码</th><th>公司</th><th>行业</th><th>披露主体</th><th>首次披露</th><th>最后披露</th><th>已知峰值</th><th>当前状态</th>
        <th>说明</th>
      </tr></thead><tbody>
      ${hk.holdings.map(h=>{
        const peak = h.peak_known ? `${(h.peak_shares/1e6).toFixed(1)}M股 (${h.peak_pct})<br><span style="font-size:.65rem;color:var(--text-lighter)">${h.buy_price_note||''}</span>` : '未公开';
        const st = statusLabels[h.current_status]||h.current_status;
        const sc = statusColors[h.current_status]||'#f3f4f6;color:#6b7280';
        return `
        <tr>
          <td>${fmtTicker(h.ticker)}</td>
          <td>${cn(h.name)}</td>
          <td><span class="tag">${h.sector}</span></td>
          <td style="font-size:.75rem;">${h.entity}</td>
          <td>${h.first_disclosure}</td>
          <td>${h.last_disclosure}</td>
          <td style="font-size:.75rem;">${peak}</td>
          <td><span class="tag" style="background:${sc}">${st}</span></td>
          <td style="max-width:300px;font-size:.75rem;line-height:1.5;">${h.notes}</td>
        </tr>`;
      }).join('')}
      </tbody></table></div>
      <div style="font-size:.68rem;color:var(--text-lighter);margin-top:8px;padding:6px 12px;background:#f8f6f0;border-radius:6px;">📋 数据源：<code>${hk.source}</code> | ${hk.disclaimer}</div>
    `;
  } catch(e) {
    container.innerHTML = '<p style="color:var(--text-lighter);">港股数据加载失败</p>';
  }
}

function switchTab(name) {
  ['current','changes','history'].forEach(t=>{
    document.getElementById('tab-'+t).classList.toggle('d-none',t!==name);
  });
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{
    b.classList.toggle('active',['current','changes','history'][i]===name);
  });
  if (name==='history') { renderHistoryChart(); renderTimeline(); }
}

function renderAll() {
  const d = data.current;
  const pq = d.prevQuarter||'上季', cq = d.quarter||'本季';
  ['chPS','chPV'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=pq;});
  ['chCS','chCV'].forEach(id=>{const el=document.getElementById(id);if(el)el.textContent=cq;});
  document.getElementById('metaRow').innerHTML = `
    <span>📅 ${t('metaReport')}: ${d.quarter} (${t('metaPeriod')} ${d.periodEnd})</span>
    <span>📬 ${t('metaFiling')}: ${d.filingDate}</span>
    <span>📍 Seattle, WA</span>
  `;
  document.getElementById('dataSource').textContent = data._live ? t('srcLive') : t('srcAuto');
  document.getElementById('updateTime').innerHTML = `13F: ${new Date(data.meta?.lastUpdated || Date.now()).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'})} | 股价: <span id="priceUpdate">加载中...</span>`;
  // update dynamic content
  const pcEl = document.getElementById('philoCount');
  if (pcEl) pcEl.textContent = d.holdings.length;
  // Update philosophy card text (has child span, can't use data-i18n)
  const philP = document.querySelector('[data-i18n="philFBody1"]');
  if (philP && lang === 'en') philP.innerHTML = `Concentrated in a few high-conviction investments. Currently only <span id="philoCount">${d.holdings.length}</span> holdings.`;
  renderSummary(); renderHoldings(); renderChanges(); renderInsights();

  renderHKHoldings();
  // Update price note
  const pf = document.getElementById('priceFoot');
  if (pf) pf.innerHTML = lang === 'zh'
    ? '💡 <strong>参考股价</strong> = Finnhub 每周拉取（非实时） | <strong>最近成本</strong> = 最近建仓买入估算 | <strong>历史均价</strong> = 全周期持仓季度中位数 | 无法获取时以 <code>13F 市值/股数</code> 代替'
    : '💡 <strong>Price</strong> = Finnhub weekly (not real-time) | <strong>Recent Cost</strong> = latest buy-in estimate | <strong>All-Time Avg</strong> = median across quarters | <code>13F value/share</code> as fallback';
}


// ========== INIT ==========
async function init() {
  try {
    const resp = await fetch('data.json?t=' + Date.now());
    data = await resp.json();
  } catch(e) {
    document.body.innerHTML = '<div style="text-align:center;padding:100px;"><h2 style="color:#dc2626;">⚠ Data load failed</h2><p style="color:#6b7280;margin-top:12px;">data.json not found.</p></div>';
    return;
  }
  document.addEventListener('click', e => {
    if (!e.target.closest('.info-wrap'))
      document.querySelectorAll('.info-popover.show').forEach(p => p.classList.remove('show'));
  });
  renderAll();
  await loadPrices();
  await loadHKHoldings();
  renderHoldings();
  renderHKHoldings();
  document.getElementById('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    if (el.childElementCount === 0) el.textContent = t(el.dataset.i18n);
  });
}

init();
