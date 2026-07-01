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
  tabHomework: ['📋 价值筛选','📋 Value Picks'],
  tabSpinoff:  ['🔀 分拆研究','🔀 Spin-offs'],
  selLabel: ['切换投资者：','Investor:'],
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
  ftAuto: ['· GitHub Actions 每日自动更新','· Auto-updated daily via GitHub Actions'],
  // Margin of Safety
  mosTitle: ['🟢 抄作业安全边际','Margin of Safety 🟢'],
  mosSubtitle: ['当前股价低于大佬预估建仓成本 20% 以上，可能是逆向关注机会','Current price is 20%+ below estimated cost basis — potential contrarian opportunity'],
  mosGreen: ['🟢 安全边际充足','Green Light'],
  mosWatch: ['⚡ 值得关注','Watch List'],
  mosNoMOS: ['暂无安全边际机会','No margin of safety opportunities right now'],
  mosBadge: ['安全边际','Margin of Safety'],

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
  secCyber: ['网络安全','Cybersecurity'],
  secInsurance: ['保险','Insurance'],
  secEducation: ['教育','Education'],
  secGaming: ['游戏','Gaming'],
  secUtility: ['公用事业','Utilities'],
  secPharma: ['医药','Pharma'],
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
  priceNote: ['💡 参考股价 = Finnhub 每日拉取（非实时） | 最近成本 = 最近一次建仓买入估算 | 历史均价 = 全周期持仓季度中位数','💡 Price = Finnhub daily (not real-time) | Recent Cost = latest buy-in estimate | All-Time Avg = median across all holding quarters'],
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
  footerWeekly: ['· GitHub Actions 每日自动更新',' · Auto-updated daily via GitHub Actions'],
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
  srcAuto: ['📦 GitHub Actions 每日自动更新','📦 Auto-updated daily via GitHub Actions'],
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
    'HCC':'勇士冶金煤','RIG':'越洋钻探','AMR':'Alpha冶金','WARRIOR MET COAL INC':'勇士冶金煤','TRANSOCEAN LTD':'越洋钻探','ALPHA METALLURGICAL RESOUR I':'Alpha冶金资源',
    'CITIGROUP INC':'花旗集团','GENERAL MTRS CO':'通用汽车',
    'FIAT CHRYSLER AUTOMOBILES N':'菲亚特克莱斯勒','NOBLE CORP PLC':'Noble Corp',
    'AERCAP HOLDINGS NV':'AerCap','ALIBABA GROUP HLDG LTD':'阿里巴巴',
    'ARCH RESOURCES INC':'Arch Resources','AUTONATION INC':'AutoNation',
    'BANK AMERICA CORP':'美国银行','BROOKFIELD ASSET MGMT INC':'Brookfield',
    'BROOKFIELD CORP':'Brookfield Corp','CHESAPEAKE ENERGY CORP':'切萨皮克能源',
    'BANK AMER CORP':'美国银行','BANK OF AMERICA CORPORATION':'美国银行',
    'BROOKFIELD ASSET MANAGMT LTD':'Brookfield资管','GRAFTECH INTL LTD':'GrafTech',
    'HORSEHEAD HLDG CORP':'Horsehead','POSCO':'浦项制铁',
    'SERITAGE GROWTH PPTYS':'Seritage','SOUTHWEST AIRLS CO':'西南航空',
    'VALARIS LTD':'Valaris','WL ROSS HLDG CORP':'WL Ross',

    'CONSOL ENERGY INC NEW':'Consol Energy','DANAOS CORPORATION':'Danaos',
    'FERRARI N V':'法拉利','GOLDMAN SACHS GROUP INC':'高盛',
    'GOOGLE INC':'Google','GOOGL':'Google',
    'CHEVRON CORP NEW':'雪佛龙','MICRON TECHNOLOGY INC':'美光科技',
    'HCC':'勇士冶金煤','RIG':'越洋钻探','AMR':'Alpha冶金',
    'WARRIOR MET':'勇士冶金煤','TRANSOCEAN':'越洋钻探',
    'GENERAL MTRS':'通用汽车','CITIGROUP':'花旗集团',
    'FIAT CHRYSLE':'菲亚特克莱斯勒','NOBLE CORP':'Noble',

    'WARRIOR MET':'勇士冶金煤','TRANSOCEAN L':'越洋钻探','ALPHA METALL':'Alpha冶金','HCC':'勇士冶金煤','RIG':'越洋钻探','AMR':'Alpha冶金','WARRIOR MET COAL INC':'勇士冶金煤','TRANSOCEAN LTD':'越洋钻探','ALPHA METALLURGICAL RESOUR I':'Alpha冶金资源',
    // Duan Yongping (H&H International Investment)
    'TESLA INC':'特斯拉','TSLA':'特斯拉',
    'OCCIDENTAL PETE CORP':'西方石油','OXY':'西方石油',
    'CREDO TECHNOLOGY GROUP HOLDI':'Credo科技','CRDO':'Credo科技',
    'TAIWAN SEMICONDUCTOR MANUFAC':'台积电','TSM':'台积电',
    'CIRCLE INTERNET GROUP INC':'Circle','CRCL':'Circle',
    'PALANTIR TECHNOLOGIES INC':'Palantir','PLTR':'Palantir',
    'SYNOPSYS INC':'新思科技','SNPS':'新思科技',
    'CROWDSTRIKE HLDGS INC':'CrowdStrike','CRWD':'CrowdStrike',
    'SNOWFLAKE INC':'Snowflake','SNOW':'Snowflake',
    'TEMPUS AI INC':'Tempus AI','TEM':'Tempus AI',
    'INNODATA INC':'Innodata','INOD':'Innodata',
    'MICROSOFT CORP':'微软','MSFT':'微软',
    'UNITEDHEALTH GROUP INC':'联合健康','UNH':'联合健康',
    // David Tepper (Appaloosa LP)
    'AMAZON COM INC':'亚马逊','AMZN':'亚马逊',
    'UBER TECHNOLOGIES INC':'优步','UBER':'优步',
    'QUALCOMM INC':'高通','QCOM':'高通',
    'ADVANCED MICRO DEVICES INC':'AMD','AMD':'AMD',
    'LYFT INC':'Lyft','LYFT':'Lyft',
    'MICRON TECHNOLOGY INC':'美光科技',
    'TAIWAN SEMICONDUCTOR MANUFAC':'台积电',
    'VISTRA CORP':'Vistra能源',
    'ISHARES INC':'iShares ETF',
    'NRG ENERGY INC':'NRG Energy',
    'SANDISK CORP':'SanDisk闪迪',
    'CORNING INC':'康宁',
    'WHIRLPOOL CORP':'惠而浦',
    'LAM RESEARCH CORP':'泛林半导体',
    'L3HARRIS TECHNOLOGIES INC':'L3Harris',
    'RTX CORPORATION':'RTX',
    'ASML HLDG NV':'ASML',
    'BALL CORP':'Ball Corp',
    'KRANESHARES TRUST':'Kraneshares ETF',
    'ENERGY TRANSFER L P':'Energy Transfer',
    'DEUTSCHE BK AG':'德意志银行',
    // Guy Spier (Aquamarine Capital)
    'BK OF AMERICA CORP':'美国银行',
    'MASTERCARD INCORPORATED':'万事达',
    'FERRARI N V':'法拉利',
    'DAILY JOURNAL CORP':'Daily Journal',
    'SERITAGE GROWTH PPTYS':'Seritage',
    'MOODYS CORP':'穆迪','MCO':'穆迪',
    // Akre Capital
    'VISA INC':'Visa','V':'Visa',
    'KKR & CO L P DEL':'KKR','KKR':'KKR',
    'ROPER TECHNOLOGIES INC':'Roper科技',
    'COSTAR GROUP INC':'CoStar集团',
    'FAIR ISAAC CORP':'FICO',
    'TYLER TECHNOLOGIES INC':'Tyler科技',
    'CONSTELLATION SOFTWARE INC':'Constellation软件',
    'VEEVA SYSTEMS INC':'Veeva',
    'IDEXX LABORATORIES INC':'IDEXX',
    'DANAHER CORPORATION':'丹纳赫',
    // Greenberg (Brave Warrior)
    'TD SYNNEX CORPORATION':'TD SYNNEX',
    'ONEMAIN HLDGS INC':'OneMain金融',
    'ICON PLC':'ICON',
    'ELEVANCE HEALTH INC FORMERLY':'Elevance健康',
    'AUTONATION INC':'AutoNation',
    'SLM CORP':'SLM',
    'GLOBE LIFE INC':'Globe Life',
    'CHARLES SCHWAB CORP':'嘉信理财',
    'AMERICAN EXPRESS CO':'美国运通','AXP':'美国运通',
    'LIBERTY MEDIA CORP DEL':'Liberty媒体',
    // Buffett (Berkshire)
    'COCA COLA CO':'可口可乐','KO':'可口可乐',
    'CHEVRON CORPORATION':'雪佛龙',
    'BANK AMERICA CORP':'美国银行',
    'CHUBB LTD SWITZ':'Chubb',
    'KRAFT HEINZ CO':'卡夫亨氏',
    'OCCIDENTAL PETROLEUM CORP':'西方石油',
    'MOODY S CORP':'穆迪',
    'DAVITA INC':'达维塔',
    'HP INC':'惠普',
    'LIBERTY LATIN AMERICA LTD':'Liberty拉美',
    'VERISIGN INC':'VeriSign',
    'AMAZON COM INC':'亚马逊','AMZN':'亚马逊',
    'SIRIUS XM HLDGS INC':'Sirius XM',
    'CHARTER COMMUNICATIONS INC N':'Charter通信',
    'SNOWFLAKE INC':'Snowflake',
    'VERIZON COMMUNICATIONS INC':'Verizon',
    'DIAGEO PLC':'帝亚吉欧',
    'NU HOLDINGS LTD CO':'Nu Holdings',
    'LIBERTY MEDIA CORP NEW':'Liberty媒体',
    'LOUISIANA PAC CORP':'LP建材',
    'FLOOR DECOR HLDGS INC':'Floor & Decor',
    'PILOT CORP':'Pilot',
    'VISA INC':'Visa',
    // Pabrai
    'SERITAGE GROWTH PPTYS':'Seritage',
    'MICRON TECHNOLOGY INC':'美光科技','MU':'美光科技',
    'INTEL CORP':'英特尔','INTC':'英特尔',
    'WELLS FARGO & CO NEW':'富国银行','WFC':'富国银行',
    'JOHNSON & JOHNSON':'强生',
    'PFIZER INC':'辉瑞',
    'ABBVIE INC':'艾伯维',
    'UNITEDHEALTH GROUP INC':'联合健康','UNH':'联合健康',
    'JPMORGAN CHASE & CO':'摩根大通','JPM':'摩根大通',
    'GOLDMAN SACHS GROUP INC':'高盛','GS':'高盛',
    'CITIGROUP INC':'花旗集团','C':'花旗集团',
    'GENERAL MOTORS CO':'通用汽车','GM':'通用汽车',
    'BANK OF AMERICA CORP':'美国银行','BAC':'美国银行',
    'FREEPORT MCMORAN INC':'自由港矿业','FCX':'自由港矿业',
    'SERVISFIRST BANCSHARES INC':'ServisFirst银行','SFBS':'ServisFirst银行',
    // Webb (HK stocks - using HK names)
    '0700.HK':'腾讯控股','0005.HK':'汇丰控股','0016.HK':'新鸿基地产',
    '0388.HK':'香港交易所','0011.HK':'恒生银行','0941.HK':'中国移动',
    '1299.HK':'友邦保险','2318.HK':'中国平安','0001.HK':'长和',
    '0003.HK':'香港中华煤气','0006.HK':'电能实业','0012.HK':'恒基地产',
    '0013.HK':'和黄','0017.HK':'新世界发展','0019.HK':'太古股份公司',
  },

};
function t(key) { const v = T[key]; return v ? v[lang==='en'?1:0] : key; }
let investor = 'lilu';
const INVESTORS = ['lilu', 'pabrai', 'duan', 'tepper', 'spier', 'webb', 'buffett', 'akre', 'greenberg'];
const INVESTOR_LABELS = { lilu: '李录', pabrai: '帕伯莱', duan: '段永平', tepper: '大卫·泰珀', spier: '盖伊·斯皮尔', webb: '大卫·韦伯', buffett: '巴菲特', akre: '查克·阿克雷', greenberg: '格伦·格林伯格' };
const INVESTOR_LABELS_EN = { lilu: 'Li Lu', pabrai: 'Pabrai', duan: 'Duan', tepper: 'Tepper', spier: 'Spier', webb: 'Webb', buffett: 'Buffett', akre: 'Akre', greenberg: 'Greenberg' };
function renderInvestorBtns() {
  const bar = document.getElementById('investorBtn');
  if (!bar) return;
  const labels = lang === 'en' ? INVESTOR_LABELS_EN : INVESTOR_LABELS;
  bar.innerHTML = INVESTORS.map(id => {
    const active = id === investor;
    return `<button onclick="switchInvestor('${id}')" style="padding:5px 11px;border:1px solid ${active ? 'var(--gold)' : 'rgba(212,168,83,.3)'};border-radius:16px;background:${active ? 'rgba(212,168,83,.15)' : 'transparent'};color:${active ? 'var(--gold)' : 'var(--text-light)'};font-size:.72rem;font-weight:${active ? '700' : '500'};cursor:pointer;white-space:nowrap;transition:all .15s;">${labels[id]}</button>`;
  }).join('');
}
async function switchInvestor(v) {
  if (v && INVESTORS.includes(v)) { investor = v; }
  else { const idx = INVESTORS.indexOf(investor); investor = INVESTORS[(idx + 1) % INVESTORS.length]; }
  renderInvestorBtns();
  try {
    var f, pf;
    if (investor === 'lilu') { f = 'data.json'; pf = 'prices.json'; }
    else if (investor === 'pabrai') { f = 'pabrai_data.json'; pf = 'pabrai_prices.json'; }
    else if (investor === 'duan') { f = 'duan.json'; pf = 'prices_duan.json'; }
    else if (investor === 'tepper') { f = 'tepper.json'; pf = 'prices_tepper.json'; }
    else if (investor === 'spier') { f = 'spier.json'; pf = 'prices_spier.json'; }
    else if (investor === 'webb') { f = 'webb.json'; pf = 'prices_webb.json'; }
    else if (investor === 'buffett') { f = 'buffett.json'; pf = 'prices_buffett.json'; }
    else if (investor === 'akre') { f = 'akre.json'; pf = 'prices_akre.json'; }
    else { f = 'greenberg.json'; pf = 'prices_greenberg.json'; }
    var r = await fetch(f + '?t=' + Date.now());
    if (!r.ok) throw new Error(f + ' HTTP ' + r.status);
    var newData = await r.json();
    if (!newData || !newData.current) throw new Error(f + ' invalid');
    data = newData;
    await loadPrices(pf);
    renderSummary(); renderHoldings(); renderHistoryChart();
    renderInsights();
    renderTimeline();
    updateInvestorContent();
  } catch(e) {
    console.error('switchInvestor error:', e.message, e.stack);
    // Only show toast for actual data load failures (not when data already loaded)
    if (!data || !data.current) {
      const toast = document.createElement('div');
      toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#dc2626;color:#fff;padding:10px 20px;border-radius:8px;font-size:.85rem;z-index:9999;';
      toast.textContent = '数据加载失败，请稍后重试';
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
  }
}
function cn(name, h) {
  if (lang==='zh') {
    if (h && h.cnName) return h.cnName;
    return T.cnName[name] || name;
  }
  return name;
}
function ts(s) {
  const sm = {'科技':'secTech','互联网':'secInternet','电商':'secEcom','金融':'secFinance',
    '综合金融':'secConglomerate','消费':'secConsumer','能源':'secEnergy','娱乐':'secEntertain',
    '金融服务':'secFinSvc','半导体':'secSemi','社交':'secSocial','汽车/新能源':'secAuto',
    '工业/轨交':'secIndustrial','金融/银行':'secBanking','煤炭':'secCoal','油气钻探':'secOilDrill','冶金/煤炭':'secMetCoal','油气':'secEnergy','航空':'secConsumer','汽车':'secAuto','航空租赁':'secFinSvc','航运':'secConsumer','资管':'secFinSvc','汽车零售':'secConsumer','钢铁':'secConsumer','工业':'secIndustrial','房地产':'secConsumer','网络安全':'secCyber','保险':'secInsurance','教育':'secEducation','游戏':'secGaming','公用事业':'secUtility','医药':'secPharma'};
  sm['其他'] = 'secOther';
  return t(sm[s] || 'secOther');
}
function switchLang() {
  lang = lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('lang', lang);
  renderInvestorBtns();
  document.getElementById('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = t(el.dataset.i18n);
    if (el.childElementCount === 0) el.textContent = v;
  });
  renderSummary(); renderHoldings(); renderInsights(); renderHistoryChart();
  updateInvestorContent();
  renderTimeline();
  _homeworkCache = null;
  if (!document.getElementById('tab-homework').classList.contains('d-none')) renderHomework();
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
function currSymbol(ticker) {
  // HK stocks use HKD
  return (ticker && ticker.endsWith('.HK')) ? 'HK$' : '$';
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

async function loadPrices(pf) {
  const file = pf || 'prices.json';
  try {
    const resp = await fetch(file + '?t=' + Date.now());
    prices = await resp.json();
    const el = document.getElementById('priceUpdate');
    if (el) el.textContent =
      prices.updatedAt ? new Date(prices.updatedAt).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'})
      : prices.updated ? new Date(prices.updated).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'}) : '待更新';
  } catch(e) {
    console.log('prices unavailable:', file);
    prices = { quotes: {}, costBasis: {} };
    const el2 = document.getElementById('priceUpdate');
    if (el2) el2.textContent = '暂不可用';
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
    renderSummary(); renderHoldings(); renderInsights(); renderHistoryChart();
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
    let hkUrl = investor === 'pabrai' ? 'pabrai_hk.json' : (investor === 'duan' ? 'duan_hk.json' : (investor === 'tepper' ? 'tepper_hk.json' : (investor === 'spier' ? 'spier_hk.json' : (investor === 'webb' ? 'webb_hk.json' : (investor === 'buffett' ? 'buffett_hk.json' : (investor === 'akre' ? 'akre_hk.json' : (investor === 'greenberg' ? 'greenberg_hk.json' : 'hk_holdings.json')))))));
    const resp = await fetch(hkUrl + '?t=' + Date.now());
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
        <span style="font-size:.88rem;color:var(--text);">${cn(h.name, h)}</span>
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
  `;
}


function renderHoldings() {
  const d = data.current;
  const quotes = prices?.quotes || {};
  const costBasis = prices?.costBasis || {};
  
  // Calculate MOS for each holding
  const mosItems = [];
  
  const rows = d.holdings.map((h,i)=>{
    const pct=(h.value/d.totalValue*100).toFixed(2);
    const q = quotes[h.ticker];
    const cb = costBasis[h.ticker];
    const currentPrice = (q && !q.error) ? q.c : (h.value / h.shares);
    const priceHtml = (q && !q.error) ? `${currSymbol(h.ticker)}${q.c.toFixed(2)}` : '<span style="color:var(--text-lighter)">--</span>';
    
    let mosHtml = '';
    let costHtml = '<span style="color:var(--text-lighter)">--</span>';
    
    if (cb && cb.recent && !cb.recent.error) {
      const rc = cb.recent;
      const at = cb.allTime;
      const pnl = ((currentPrice - rc.buy) / rc.buy * 100).toFixed(1);
      const pnlClass = pnl >= 0 ? 'qoq-up' : 'qoq-down';
      const pnlSign = pnl >= 0 ? '+' : '';
      const isYahoo = rc.source === 'yahoo' || rc.source === 'yfinance';
      const srcBadge = isYahoo ? '<span style="color:#10b981;font-size:.55rem;">K线</span>' : '<span style="color:#f59e0b;font-size:.55rem;">13F估</span>';
      
      // Margin of Safety calculation
      const mos = ((rc.buy - currentPrice) / rc.buy * 100);
      if (mos >= 20) {
        mosItems.push({ ticker: h.ticker, name: h.name, cnName: h.cnName||'', mos: mos.toFixed(1), cost: rc.buy, price: currentPrice });
        mosHtml = `<span title="${t('mosBadge')}: ${mos.toFixed(1)}%" style="display:inline-flex;align-items:center;gap:3px;padding:2px 6px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:4px;font-size:.65rem;color:#059669;font-weight:600;white-space:nowrap;animation:mosPulse 2s ease-in-out infinite;">🟢${mos.toFixed(0)}%</span>`;
      } else if (mos >= 10) {
        mosItems.push({ ticker: h.ticker, name: h.name, cnName: h.cnName||'', mos: mos.toFixed(1), cost: rc.buy, price: currentPrice });
        mosHtml = `<span title="${t('mosWatch')}: ${mos.toFixed(1)}%" style="display:inline-flex;align-items:center;gap:3px;padding:2px 6px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:4px;font-size:.65rem;color:#d97706;font-weight:600;white-space:nowrap;">⚡${mos.toFixed(0)}%</span>`;
      }
      
      const cur$ = currSymbol(h.ticker);
      costHtml = `<div title="近期 ${rc.quarter}: 买入估算 ${cur$}${rc.buy} [${cur$}${rc.low}-${cur$}${rc.high}]\n${isYahoo?'Yahoo历史K线, 偏低价加权':'13F 市值/股数'}`;
      if (at) costHtml += `\n\n全周期 (${at.first}~${at.last}, ${at.quarters}季): 均价 $${at.avg}`;
      costHtml += `" style="cursor:help">`;
      costHtml += `<div style="font-weight:600">${cur$}${rc.buy}</div>`;
      costHtml += `<div style="font-size:.65rem;color:var(--text-lighter);">${t('costRecent')} ${srcBadge} <span class="${pnlClass}" style="font-weight:500;">${pnlSign}${pnl}%</span></div>`;
      if (at) costHtml += `<div style="font-weight:500;color:var(--navy);margin-top:3px;">$${at.avg}</div>`;
      if (at) costHtml += `<div style="font-size:.6rem;color:var(--text-lighter);">${t('costAllTime')} (${at.quarters}季)</div>`;
      costHtml += `</div>`;
    }

    // ── Position change tags ──
    const isEn = lang === 'en';
    const prev = h.prevShares || 0;
    const cur = h.shares || 0;
    let chgTag = '';
    if (prev === 0 && cur > 0) {
      chgTag = `<span title="${isEn?'New position this quarter':'本季新开仓'}" style="display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:4px;font-size:.6rem;color:#3b82f6;font-weight:600;white-space:nowrap;margin-top:3px;">🆕 ${isEn?'New':'新开仓'}</span>`;
    } else if (prev > 0 && cur === 0) {
      chgTag = `<span title="${isEn?'Fully exited this quarter':'本季已清仓'}" style="display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:4px;font-size:.6rem;color:#ef4444;font-weight:600;white-space:nowrap;margin-top:3px;">🚪 ${isEn?'Exited':'已清仓'}</span>`;
    } else if (prev > 0 && cur > prev * 1.05) {
      const addPct = ((cur - prev) / prev * 100).toFixed(0);
      chgTag = `<span title="${isEn?'Added':'加仓'} +${addPct}%" style="display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:4px;font-size:.6rem;color:#10b981;font-weight:600;white-space:nowrap;margin-top:3px;">📈 +${addPct}%</span>`;
    } else if (prev > 0 && cur < prev * 0.95) {
      const cutPct = ((prev - cur) / prev * 100).toFixed(0);
      chgTag = `<span title="${isEn?'Trimmed':'减仓'} -${cutPct}%" style="display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:4px;font-size:.6rem;color:#d97706;font-weight:600;white-space:nowrap;margin-top:3px;">📉 -${cutPct}%</span>`;
    }
    const mosCellHtml = `<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">${mosHtml || '<span style="color:var(--text-lighter);font-size:.7rem;">--</span>'}${chgTag}</div>`;
    
    return `<tr><td class="idx-cell"><span class="idx-num">${i+1}</span></td><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td class="shares-value-cell"><div style="font-weight:600">${fmtNum(h.shares)}</div><div style="font-size:.68rem;color:var(--text-lighter);margin-top:2px;">$${h.value.toLocaleString()}</div></td><td class="price-cell">${priceHtml}</td><td class="cost-cell">${costHtml}</td><td style="width:100px;"><div class="bar-wrap"><div class="bar-fill" style="width:${pct*3.5}%"></div><span style="font-size:.7rem;font-weight:600;color:var(--navy);margin-left:6px;">${pct}%</span></div></td><td style="width:80px;text-align:center;">${mosCellHtml}</td></tr>`;
  }).join('');
  
  // Legend for tags
  const legendHtml = `<div style="margin:10px 0 4px;padding:8px 12px;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.06);border-radius:8px;display:flex;flex-wrap:wrap;gap:10px;align-items:center;">
    <span style="font-size:.65rem;color:var(--text-lighter);margin-right:4px;">${lang==='en'?'Legend:':'图例：'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:4px;color:#3b82f6;font-weight:600;">🆕 ${lang==='en'?'New':'新开仓'}</span> ${lang==='en'?'New position this quarter':'本季新建仓'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:4px;color:#10b981;font-weight:600;">📈 +N%</span> ${lang==='en'?'Added (>5%)':'加仓幅度（>5%）'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:4px;color:#d97706;font-weight:600;">📉 -N%</span> ${lang==='en'?'Trimmed (>5%)':'减仓幅度（>5%）'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(239,68,68,0.12);border:1px solid rgba(239,68,68,0.3);border-radius:4px;color:#ef4444;font-weight:600;">🚪 ${lang==='en'?'Exited':'已清仓'}</span> ${lang==='en'?'Fully exited':'本季完全卖出'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(16,185,129,0.12);border:1px solid rgba(16,185,129,0.3);border-radius:4px;color:#059669;font-weight:600;">🟢 N%</span> ${lang==='en'?'Margin of Safety ≥20%':'安全边际≥20%'}</span>
    <span style="display:inline-flex;align-items:center;gap:3px;font-size:.62rem;"><span style="padding:1px 6px;background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.25);border-radius:4px;color:#d97706;font-weight:600;">⚡ N%</span> ${lang==='en'?'Margin of Safety 10-20%':'安全边际10-20%'}</span>
  </div>`;

  // MOS summary section
  const greenItems = mosItems.filter(m => parseFloat(m.mos) >= 20);
  const watchItems = mosItems.filter(m => parseFloat(m.mos) >= 10 && parseFloat(m.mos) < 20);
  
  let mosSummaryHtml = '';
  if (greenItems.length > 0) {
    const listHtml = greenItems.map(m => 
      `<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:6px;font-size:.8rem;"><span style="font-weight:600;color:#059669;">${m.ticker}</span><span style="color:#4b5563;font-size:.68rem;">${cn(m.name,m)}</span><span style="color:#6b7280;font-size:.7rem;">MOS ${m.mos}%</span><span style="color:#9ca3af;font-size:.65rem;">${currSymbol(m.ticker)}${m.cost} → ${currSymbol(m.ticker)}${m.price}</span></span>`
    ).join('');
    mosSummaryHtml = `<div style="padding:16px;background:linear-gradient(135deg,rgba(16,185,129,0.06),rgba(16,185,129,0.02));border:1px solid rgba(16,185,129,0.2);border-radius:10px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
        <span style="font-size:1.1rem;">🟢</span>
        <span style="font-weight:700;color:#059669;font-size:.95rem;">${t('mosTitle')}</span>
        <span style="padding:2px 8px;background:#059669;color:#fff;border-radius:10px;font-size:.7rem;font-weight:600;">${greenItems.length}</span>
      </div>
      <div style="font-size:.78rem;color:#6b7280;margin-bottom:10px;">${t('mosSubtitle')}</div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">${listHtml}</div>
    </div>`;
  } else if (watchItems.length > 0) {
    const listHtml = watchItems.map(m => 
      `<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);border-radius:6px;font-size:.8rem;"><span style="font-weight:600;color:#d97706;">${m.ticker}</span><span style="color:#4b5563;font-size:.68rem;">${cn(m.name,m)}</span><span style="color:#6b7280;font-size:.7rem;">MOS ${m.mos}%</span></span>`
    ).join('');
    mosSummaryHtml = `<div style="padding:14px;background:rgba(245,158,11,0.04);border:1px solid rgba(245,158,11,0.15);border-radius:10px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
        <span style="font-size:1rem;">⚡</span>
        <span style="font-weight:600;color:#d97706;font-size:.9rem;">${t('mosWatch')}</span>
        <span style="padding:2px 8px;background:#d97706;color:#fff;border-radius:10px;font-size:.7rem;font-weight:600;">${watchItems.length}</span>
      </div>
      <div style="display:flex;flex-wrap:wrap;gap:8px;">${listHtml}</div>
    </div>`;
  }
  
  // Inject MOS summary before the holdings table (only once)
  if (mosSummaryHtml) {
    let existingMos = document.getElementById('mosSummary');
    if (!existingMos) {
      const tabCurrent = document.getElementById('tab-current');
      if (tabCurrent) {
        const mosDiv = document.createElement('div');
        mosDiv.id = 'mosSummary';
        mosDiv.innerHTML = mosSummaryHtml;
        tabCurrent.insertBefore(mosDiv, tabCurrent.querySelector('.table-wrap'));
      }
    } else {
      existingMos.innerHTML = mosSummaryHtml;
    }
  } else {
    const existingMos = document.getElementById('mosSummary');
    if (existingMos) existingMos.remove();
  }
  document.getElementById('holdingsBody').innerHTML = rows;
  const priceFoot = document.getElementById('priceFoot');
  if (priceFoot) {
    // Remove existing legend if any, then append
    const existingLegend = priceFoot.querySelector('.holdings-legend');
    if (existingLegend) existingLegend.remove();
    const legendDiv = document.createElement('div');
    legendDiv.className = 'holdings-legend';
    legendDiv.innerHTML = legendHtml;
    priceFoot.appendChild(legendDiv);
  }
}

function renderChanges() {
  const d = data.current;
  const pq = d.prevQuarter || '上季';
  const cq = d.quarter || '本季';
  document.getElementById('chPS').textContent = pq + ' 持股';
  document.getElementById('chCS').textContent = cq + ' 持股';
  document.getElementById('chPV').textContent = pq + ' 市值';
  document.getElementById('chCV').textContent = cq + ' 市值';
  document.getElementById('changesBody').innerHTML = d.holdings.map(h=>{
    const sd=h.shares-(h.prevShares||0), vd=h.value-(h.prevValue||0);
    const sc=h.prevShares===0?'qoq-new':(sd>0?'qoq-up':(sd<0?'qoq-down':'qoq-flat'));
    const vc=h.prevValue===0?'qoq-new':(vd>0?'qoq-up':(vd<0?'qoq-down':'qoq-flat'));
    const ss=sd>0?'+':'', vs=vd>0?'+':'';
    return `<tr><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td>${h.prevShares===0?'-':fmtNum(h.prevShares)}</td><td>${fmtNum(h.shares)}</td><td>${fmtShareChg(h.shares,h.prevShares)}</td><td>${h.prevValue===0?'-':'$'+fmtVal(h.prevValue)}</td><td>$${fmtVal(h.value)}</td><td class="${vc}">${h.prevValue===0?'新进':`${vs}$${fmtVal(Math.abs(vd))} (${fmtPct(h.value,h.prevValue)})`}</td></tr>`;
  }).join('');
}

function renderInsights() {
  const d = data.current, ins = [];
  const np = d.holdings.filter(h=>!h.prevShares);
  if (np.length) ins.push(`${t('insNew')} ${np.length} ${t('insNew2')} ${np.map(h=>h.ticker).join('、')}, ${t('insExpand')}。`);
  const bs = d.holdings.filter(h=>h.prevShares&&h.shares<h.prevShares*0.5);
  bs.forEach(h=>{ const p=((h.prevShares-h.shares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name, h)})${t('insSell')} ${p}%, ${t('insSell2')} ${fmtNum(h.prevShares-h.shares)} ${t('insSell3')}。`); });
  const inc = d.holdings.filter(h=>h.prevShares&&h.shares>h.prevShares*1.1);
  inc.forEach(h=>{ const p=((h.shares-h.prevShares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name, h)})${t('insBuy')} ${p}%, ${t('insBuy2')} ${fmtNum(h.shares-h.prevShares)} ${t('insBuy3')}。`); });
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
      if (!tickerInfo[tk]) tickerInfo[tk] = {first: q, last: q, quarters: [], sector: h.sector, name: h.name, cnName: h.cnName||'', maxShares: 0, curShares: 0};
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

  let html = '<table style="width:100%;font-size:.82rem;"><thead><tr><th>'+t('thCompany')+'</th><th>'+t('thFirst')+'</th><th>'+t('thLast')+'</th><th>'+t('thQCount')+'</th><th>'+t('thPosition')+'</th><th>'+t('thStatus')+'</th></tr></thead><tbody>';
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
      <td class="stock-cell"><span class="ticker-line">${fmtTicker(e.ticker)}</span><span class="name-line">${cn(e.name, e)}</span><span class="sector-badge">${ts(e.sector)}</span></td>
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
    let hkUrl = investor === 'pabrai' ? 'pabrai_hk.json' : (investor === 'duan' ? 'duan_hk.json' : (investor === 'tepper' ? 'tepper_hk.json' : (investor === 'spier' ? 'spier_hk.json' : (investor === 'webb' ? 'webb_hk.json' : (investor === 'buffett' ? 'buffett_hk.json' : (investor === 'akre' ? 'akre_hk.json' : (investor === 'greenberg' ? 'greenberg_hk.json' : 'hk_holdings.json')))))));
    const resp = await fetch(hkUrl + '?t=' + Date.now());
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
          <td>${cn(h.name, h)}</td>
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
  ['current','changes','history','homework','spinoff'].forEach(t=>{
    document.getElementById('tab-'+t).classList.toggle('d-none',t!==name);
  });
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{
    b.classList.toggle('active',['current','changes','history','homework','spinoff'][i]===name);
  });
  if (name==='history') { renderHistoryChart(); renderTimeline(); }
  if (name==='homework') { renderHomework(); }
  if (name==='spinoff') { renderSpinoff(); }
}

let _homeworkCache = null;
async function renderHomework() {
  const el = document.getElementById('homeworkContent');
  if (!el) return;
  if (_homeworkCache) { el.innerHTML = _homeworkCache; return; }
  el.innerHTML = '<p style="padding:24px;color:var(--text-lighter);">加载中...</p>';

  // Load all investor data
  const INVESTORS_CFG = [
    {id:'lilu',   df:'data.json',        pf:'prices.json',          name:'李录',     nameEn:'Li Lu'},
    {id:'pabrai', df:'pabrai_data.json', pf:'pabrai_prices.json',   name:'帕伯莱',   nameEn:'Pabrai'},
    {id:'duan',   df:'duan.json',        pf:'prices_duan.json',     name:'段永平',   nameEn:'Duan'},
    {id:'tepper', df:'tepper.json',      pf:'prices_tepper.json',   name:'Tepper',   nameEn:'Tepper'},
    {id:'spier',  df:'spier.json',       pf:'prices_spier.json',    name:'Spier',    nameEn:'Spier'},
    {id:'akre',   df:'akre.json',        pf:'prices_akre.json',     name:'Akre',     nameEn:'Akre'},
    {id:'greenberg',df:'greenberg.json', pf:'prices_greenberg.json',name:'Greenberg',nameEn:'Greenberg'},
    {id:'buffett',df:'buffett.json',     pf:'prices_buffett.json',  name:'巴菲特',   nameEn:'Buffett'},
  ];

  const candidates = [];
  // Pass 1: count ALL holders per ticker (regardless of MOS), for true consensus
  const allHoldersMap = {}; // ticker -> Set of investor ids
  const allDataCache = [];
  for (const cfg of INVESTORS_CFG) {
    try {
      const [dr, pr] = await Promise.all([
        fetch(cfg.df).then(r=>r.json()),
        fetch(cfg.pf).then(r=>r.json()),
      ]);
      allDataCache.push({cfg, dr, pr});
      for (const h of (dr.current.holdings||[])) {
        const tk = h.ticker;
        if (tk.startsWith('?') || tk.endsWith('.HK')) continue;
        if (!allHoldersMap[tk]) allHoldersMap[tk] = new Set();
        allHoldersMap[tk].add(cfg.id);
      }
    } catch(e) { console.warn(cfg.id, e); }
  }

  // Pass 2: build candidates (MOS >= 10% filter applies here)
  for (const {cfg, dr, pr} of allDataCache) {
    try {
      const holdings = dr.current.holdings;
      const totalVal = dr.current.totalValue;
      const quotes = pr.quotes || {};
      const cb = pr.costBasis || {};
      for (const h of holdings) {
        const tk = h.ticker;
        if (tk.startsWith('?') || tk.endsWith('.HK')) continue;
        const q = quotes[tk]; const c = cb[tk];
        if (!q || q.error || !c) continue;
        const rc = c.recent;
        if (!rc || !rc.buy) continue;
        const price = q.c; const buy = rc.buy;
        if (price <= 0 || buy <= 0) continue;
        const mos = (buy - price) / buy * 100;
        if (mos < 10) continue;
        const weight = totalVal > 0 ? h.value / totalVal * 100 : 0;
        const prev = h.prevShares || 0; const cur2 = h.shares || 0;
        let chg = 'hold';
        if (prev === 0 && cur2 > 0) chg = 'new';
        else if (prev > 0 && cur2 > prev * 1.05) chg = 'added';
        else if (prev > 0 && cur2 < prev * 0.95) chg = 'trimmed';
        const invEntry = {name: lang==='en'?cfg.nameEn:cfg.name, id:cfg.id, weight:round1(weight), chg};
        const existing = candidates.find(x => x.ticker === tk);
        if (existing) {
          if (!existing.investors.find(x => x.id === cfg.id)) {
            existing.investors.push(invEntry);
            // Use lowest cost basis across all holders (most conservative)
            if (buy < existing.buy) {
              existing.buy = buy;
              existing.mos = round1(mos);
              existing.atAvg = c.allTime?.avg || existing.atAvg;
            }
          }
        } else {
          candidates.push({
            ticker: tk, name: h.name, cnName: h.cnName||'', sector: h.sector,
            mos: round1(mos), price, buy,
            atAvg: c.allTime?.avg || null,
            investors: [invEntry],
            totalHolders: allHoldersMap[tk]?.size || 1,
          });
        }
      }
    } catch(e) { console.warn(cfg.id, e); }
  }

  // Score: consensus count (weight 40) + MOS (weight 1) + change bonus (new=15, added=8)
  const isEn2 = lang === 'en';
  candidates.forEach(c => {
    let score = c.mos;
    score += (c.totalHolders - 1) * 40; // multi-investor consensus bonus (all holders, not just MOS>=10%)
    const hasNew = c.investors.some(inv => inv.chg === 'new');
    const hasAdded = c.investors.some(inv => inv.chg === 'added');
    const rowChgTag = hasNew
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:4px;font-size:.6rem;color:#3b82f6;font-weight:600;margin-top:3px;">🆕 ${isEn2?'New':'新开仓'}</span>`
      : hasAdded
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:4px;font-size:.6rem;color:#10b981;font-weight:600;margin-top:3px;">📈 ${isEn2?'Added':'加仓'}</span>`
      : '';
    if (hasNew) score += 15;
    else if (hasAdded) score += 8;
    // Penalize if ALL investors are trimming (net exit signal)
    const allTrimming = c.investors.length > 0 && c.investors.every(inv => inv.chg === 'trimmed');
    if (allTrimming) score -= 20;
    c._score = score;
    c._allTrimming = allTrimming;
  });
  candidates.sort((a,b) => b._score - a._score);

  if (candidates.length === 0) {
    el.innerHTML = `<p style="padding:32px;text-align:center;color:var(--text-lighter);">${lang==='en'?'No stocks with MOS ≥ 10%':'暂无安全边际 ≥ 10% 的标的'}</p>`;
    return;
  }

  const cur$ = '$';
  const rows = candidates.map((c,i) => {
    const mosColor = c.mos >= 20 ? '#059669' : '#d97706';
    const mosBg = c.mos >= 20 ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.08)';
    const mosBorder = c.mos >= 20 ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.2)';
    const mosIcon = c.mos >= 20 ? '🟢' : '⚡';
    const _hasNew = c.investors.some(inv => inv.chg === 'new');
    const _hasAdded = c.investors.some(inv => inv.chg === 'added');
    const rowChgTag = _hasNew
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:4px;font-size:.6rem;color:#3b82f6;font-weight:600;margin-top:3px;">🆕 ${isEn2?'New':'新开仓'}</span>`
      : _hasAdded
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:4px;font-size:.6rem;color:#10b981;font-weight:600;margin-top:3px;">📈 ${isEn2?'Added':'加仓'}</span>`
      : c._allTrimming
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(239,68,68,0.1);border:1px solid rgba(239,68,68,0.25);border-radius:4px;font-size:.6rem;color:#ef4444;font-weight:600;margin-top:3px;">⚠️ ${isEn2?'Trimming':'减仓中'}</span>`
      : '';
    const wLabel = inv => inv.weight < 0.1 ? '<0.1%' : inv.weight + '%';
    const chgBadge = inv => {
      if (inv.chg === 'new') return `<span style="font-size:.5rem;padding:0 3px;background:rgba(59,130,246,0.2);border-radius:3px;color:#3b82f6;">🆕</span>`;
      if (inv.chg === 'added') return `<span style="font-size:.5rem;padding:0 3px;background:rgba(16,185,129,0.15);border-radius:3px;color:#10b981;">📈</span>`;
      if (inv.chg === 'trimmed') return `<span style="font-size:.5rem;padding:0 3px;background:rgba(245,158,11,0.15);border-radius:3px;color:#d97706;">📉</span>`;
      return '';
    };
    const mkBadge = (inv, compact) => {
      const w = wLabel(inv);
      const cb = chgBadge(inv);
      const style = compact
        ? `cursor:pointer;display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:#2a3f5f;border:1px solid #d4a853;border-radius:8px;font-size:.55rem;color:#fff;font-weight:600;white-space:nowrap;`
        : `cursor:pointer;display:inline-flex;align-items:center;gap:3px;padding:3px 9px;background:#2a3f5f;border:1px solid #d4a853;border-radius:10px;font-size:.62rem;color:#fff;font-weight:600;white-space:nowrap;`;
      return `<span onclick="switchInvestor('${inv.id}');switchTab('current');" style="${style}" title="${isEn2?'Position':'仓位'}: ${w}">${inv.name}${cb} <span style="color:#d4a853;font-size:.55rem;font-weight:700;">${w}</span></span>`;
    };
    const invBadges = c.investors.map(inv => mkBadge(inv, false)).join(' ');
    const invBadgesCompact = c.investors.map(inv => mkBadge(inv, true)).join(' ');
    const atRow = c.atAvg ? `<div style="font-size:.6rem;color:var(--text-lighter);margin-top:1px;">${isEn2?'Hist.avg':'历史均价'} ${cur$}${c.atAvg}</div>` : '';
    const consensusPrefix = c.totalHolders >= 2
      ? `<span style="font-size:.6rem;color:#d4a853;font-weight:700;margin-right:4px;">👥 ${c.totalHolders}${isEn2?' held':' 人'}</span>`
      : '';
    const invCellHtml = `<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;">${consensusPrefix}${invBadges}</div>`;
    const invMobileHtml = `<div style="display:flex;flex-wrap:wrap;align-items:center;gap:3px;margin-top:4px;">${consensusPrefix}${invBadgesCompact}</div>`;
    return `<tr>
      <td class="idx-cell"><span class="idx-num">${i+1}</span></td>
      <td class="stock-cell">
        <span class="ticker-line">${fmtTicker(c.ticker)}</span>
        <span class="name-line">${cn(c.name, c)}</span>
        <span class="sector-badge">${ts(c.sector)}</span>
        ${rowChgTag}
        <div class="hw-inv-mobile" style="display:none;">${invMobileHtml}</div>
      </td>
      <td><div style="font-weight:600;color:#059669;">${cur$}${c.buy.toFixed(2)}</div><div style="font-size:.65rem;color:var(--text-lighter);">${isEn2?'Est. Cost':'买入估算'}</div>${atRow}</td>
      <td style="text-align:center;">
        <div style="display:inline-flex;flex-direction:column;align-items:center;gap:2px;padding:5px 8px;background:${mosBg};border:1px solid ${mosBorder};border-radius:8px;">
          <span style="font-size:.95rem;font-weight:700;color:${mosColor};">${mosIcon} ${c.mos}%</span>
          <span style="font-size:.55rem;color:var(--text-lighter);">${isEn2?'MOS':'安全边际'}</span>
        </div>
      </td>
      <td>${invCellHtml}</td>
    </tr>`;
  }).join('');

  el.innerHTML = `
    <div style="margin-bottom:16px;padding:12px 16px;background:rgba(212,168,83,0.08);border:1px solid rgba(212,168,83,0.2);border-radius:8px;">
      <p style="font-size:.8rem;color:var(--text-light);line-height:1.6;">
        📋 <strong style="color:var(--gold);">${isEn2?'Value Picks':'抄作业单'}</strong> &mdash;
        ${isEn2?'Stocks with MOS &ge; 10% held by tracked investors. Sorted by consensus + MOS + recent activity (🆕 new / 📈 added). Click an investor badge to view full portfolio.':'所有投资者持仓中安全边际 &ge; 10% 的标的。按多人共识 + 安全边际 + 最近动态（🆕新开仓 / 📈加仓）综合排序。点击投资者名称可跳转完整持仓。'}
      </p>
    </div>
    <div class="table-wrap"><table style="width:100%;">
      <thead><tr>
        <th style="width:4%">#</th>
        <th style="width:16%">${isEn2?'Stock':'股票'}</th>
        <th style="width:13%;white-space:nowrap">${isEn2?'Est. Cost':'估算成本'} <span class="info-wrap"><span class="info-badge" onclick="this.parentElement.querySelector('.info-popover').classList.toggle('show')">ⓘ</span><span class="info-popover">${isEn2?'Multiple holders: shows the lowest cost basis (most conservative). Single holder: that investor\'s estimated cost from historical K-line data (low×70%+avg×30%).':'多人持有时取最低估算成本（最保守）；单人持有时为该投资者历史 K 线估算（低价×70%+均价×30%）。'}</span></span></th>
        <th style="width:13%;text-align:center;white-space:nowrap">${isEn2?'MOS':'安全边际'}</th>
        <th style="width:54%">${isEn2?'Held By':'持有者'}</th>
      </tr></thead>
      <tbody>${rows}</tbody>
    </table></div>
    <p style="margin-top:12px;font-size:.72rem;color:var(--text-lighter);text-align:center;line-height:1.8;">
      ${isEn2
        ? '💡 <strong>Est. Cost</strong>: estimated from historical K-line (low×70%+avg×30%). Multiple holders → lowest cost shown (most conservative). MOS = (Cost−Price)/Cost. Not investment advice.'
        : '💡 <strong>估算成本</strong>：基于历史 K 线（低价×70%+均价×30%）估算买入价。多人持有时取最低成本（最保守）。安全边际 = (成本−现价)÷成本。仅供参考，不构成投资建议。'}
    </p>
  `;
  _homeworkCache = el.innerHTML;
}

// ========== Spin-off Tab ==========
let _spinoffCache = null;

// 进度状态识别（精确版，按优先级排列）
function _soProgress(ann, isEn) {
  if (!ann || !ann.length) return {label:'',color:'#9ca3af',bg:'#f3f4f6',pct:0};
  const t = (ann[0].title||'') + (ann.length>1 ? ann[1].title : '');
  // 1. 终止（最高优先级）
  if (/終止|终止|撤回|撤销|withdraw|cancel/i.test(t))
    return {label:isEn?'✕ Cancelled':'✕ 已终止',  color:'#dc2626',bg:'#fee2e2',pct:0};
  // 2. 真正上市（强信号：开始买卖 / 持续督导 / 行使超额 / 生效日期）
  if (/開始買賣|开始买卖|股份開始|股份开始|持續督導|持续督导|行使超額|行使超额|律師事務所關於.*上市.*核查|实物分派.*保证/i.test(t))
    return {label:isEn?'✅ Listed':'✅ 已上市',    color:'#059669',bg:'#d1fae5',pct:100};
  // 3. 招股书阶段
  if (/刊發招股|招股書|招股章程|招股说明|prospectus/i.test(t))
    return {label:isEn?'📋 IPO Filing':'📋 招股书', color:'#0891b2',bg:'#cffafe',pct:88};
  // 4. 已批准
  if (/批準|批准|approved|聯交所批准|获批/i.test(t))
    return {label:isEn?'✓ Approved':'✓ 已批准',   color:'#2563eb',bg:'#dbeafe',pct:75};
  // 5. 进行中（有进展更新）
  if (/進展|进展|最新情況|最新情况|update|progress/i.test(t))
    return {label:isEn?'⏳ In Progress':'⏳ 进行中', color:'#d97706',bg:'#fef3c7',pct:50};
  // 6. 初步建议
  if (/建議|建议|擬議|拟议|propose|擬|拟/i.test(t))
    return {label:isEn?'💡 Proposed':'💡 建议中',  color:'#7c3aed',bg:'#ede9fe',pct:25};
  // 生效/完成
  if (/生效日期|生效|completion|effective|以實物分派|实物分派/i.test(t))
    return {label:isEn?'✅ Completed':'✅ 已完成', color:'#059669',bg:'#d1fae5',pct:100};
  return   {label:isEn?'📢 Announced':'📢 已公告', color:'#6b7280',bg:'#f3f4f6',pct:15};
}

// 清理标题：去掉常见前缀噪音
function _soCleanTitle(t) {
  return (t||'')
    .replace(/^(内幕消息|內幕消息)\s*[-—–]\s*/i,'')
    .replace(/^(海外監管公告|海外监管公告)\s*[-—–]\s*/i,'')
    .replace(/^(自願性公告|自願公告|自愿公告)\s*[-—–]\s*/i,'')
    .replace(/^(公告及通告)\s*[-—–]\s*/i,'')
    .replace(/\s+/g,' ').trim();
}

// 派生分拆子公司名称（从标题提取）
function _soExtractSpinSub(company) {
  const ann = company.announcements || [];
  for (const a of ann) {
    const t = a.title || '';
    // 「建議分拆 XXX 並於...」
    const m1 = t.match(/分拆\s*([^\s，,。\u3002（(（\[\]【】]{3,25})\s*(?:並於|并于|at|to|upon)/i);
    if (m1) return m1[1].trim();
    // 「建議分拆所屬子公司 XXX」
    const m2 = t.match(/子公司\s*([^\s，,。（(]{4,25})\s*(?:至|在|于|to)/i);
    if (m2) return m2[1].trim();
  }
  return '';
}

async function renderSpinoff() {
  const el = document.getElementById('spinoffContent');
  if (!el) return;
  if (_spinoffCache) { el.innerHTML = _spinoffCache; return; }
  el.innerHTML = '<div style="padding:40px;text-align:center;color:var(--text-lighter);font-size:.9rem;">⏳ 加载分拆数据…</div>';
  const isEn = lang === 'en';

  try {
    const resp = await fetch('spinoff.json?t=' + Date.now());
    if (!resp.ok) throw new Error(resp.status);
    const data = await resp.json();
    const companies = (data.companies || []);

    if (!companies.length) {
      el.innerHTML = `<div style="padding:40px;text-align:center;color:var(--text-lighter);">
        <div style="font-size:2rem;margin-bottom:12px;">📭</div>
        <div>${isEn?'No spin-off announcements in the past 12 months.':'近12个月内暂无分拆公告数据。'}</div>
      </div>`;
      _spinoffCache = el.innerHTML; return;
    }

    const fd = s => s && s.length===8 ? s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8) : (s||'');

    // 统计各状态数量
    const statCount = {listed:0,approved:0,progress:0,proposed:0,cancelled:0,other:0};
    companies.forEach(c => {
      const p = _soProgress(c.announcements, true);
      if (p.pct===100) statCount.listed++;
      else if (p.pct===0 && p.color==='#dc2626') statCount.cancelled++;
      else if (p.pct>=75) statCount.approved++;
      else if (p.pct>=40) statCount.progress++;
      else if (p.pct>=15) statCount.proposed++;
      else statCount.other++;
    });

    // ── 顶部 KPI 栏 ──────────────────────────────────────────────
    let html = `
    <div style="margin-bottom:20px;">
      <!-- 标题行 -->
      <div style="display:flex;align-items:baseline;gap:12px;margin-bottom:14px;flex-wrap:wrap;">
        <h3 style="font-family:var(--serif);font-size:1.05rem;color:var(--navy);margin:0;font-weight:700;">
          ${isEn?'HK Spin-off Tracker':'港股分拆进展追踪'}
        </h3>
        <span style="font-size:.72rem;color:var(--text-lighter);">
          ${fd(data.dateFrom)} ~ ${fd(data.dateTo)} &nbsp;·&nbsp; ${isEn?'Updated':'更新'} ${(data.updatedAt||'').slice(0,10)}
        </span>
      </div>

      <!-- KPI 卡片 -->
      <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:18px;">
        ${[
          ['#059669','#d1fae5', isEn?'Listed':'已上市',    statCount.listed],
          ['#2563eb','#dbeafe', isEn?'Approved':'已批准',  statCount.approved],
          ['#d97706','#fef3c7', isEn?'In Progress':'进行中',statCount.progress],
          ['#7c3aed','#ede9fe', isEn?'Proposed':'建议中',  statCount.proposed],
          ['#dc2626','#fee2e2', isEn?'Cancelled':'已终止',  statCount.cancelled],
        ].map(([color,bg,label,count])=>`
          <div style="background:${bg};border:1px solid ${color}30;border-radius:8px;padding:8px 10px;text-align:center;">
            <div style="font-size:1.4rem;font-weight:700;color:${color};font-family:var(--serif);">${count}</div>
            <div style="font-size:.65rem;color:${color};font-weight:600;margin-top:2px;">${label}</div>
          </div>`).join('')}
      </div>

      <!-- 搜索过滤 -->
    <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;flex-wrap:wrap;">
      <input id="soSearch" type="text" placeholder="${isEn?'Search company / target…':'搜索公司/分拆标的…'}"
             oninput="soFilter(this.value)"
             style="flex:1;min-width:180px;max-width:320px;padding:6px 12px;font-size:.78rem;
                    border:1px solid var(--border);border-radius:6px;color:var(--text);
                    background:#fff;outline:none;transition:border-color .15s;"
             onfocus="this.style.borderColor='var(--gold)'"
             onblur="this.style.borderColor='var(--border)'" />
      <div style="display:flex;gap:6px;flex-wrap:wrap;align-items:center;">
        ${['all','progress','proposed','approved','listed','cancelled'].map(s=>`
          <button onclick="soFilterStatus('${s}')"
                  id="soBtn-${s}"
                  style="font-size:.65rem;padding:2px 9px;border-radius:12px;cursor:pointer;
                         border:1px solid ${s==='all'?'var(--navy)':'var(--border)'};
                         background:${s==='all'?'var(--navy)':'#fff'};
                         color:${s==='all'?'#fff':'var(--text-light)'};
                         transition:all .15s;">
            ${{all:isEn?'All':'全部',progress:isEn?'In Progress':'进行中',proposed:isEn?'Proposed':'建议中',approved:isEn?'Approved':'批准',listed:isEn?'Listed':'上市',cancelled:isEn?'Cancelled':'终止'}[s]}
          </button>`).join('')}
        <span style="width:1px;height:16px;background:var(--border);margin:0 4px;"></span>
        <button id="soBtn-reit" onclick="soToggleReit()"
                style="font-size:.65rem;padding:2px 9px;border-radius:12px;cursor:pointer;
                       border:1px solid var(--border);background:#fff;
                       color:var(--text-light);transition:all .15s;">
          ${isEn?'+ REIT':'＋ REIT'}
        </button>
      </div>
    </div>

    <!-- 表头 -->
      <div style="display:grid;grid-template-columns:120px 118px 88px 1fr 88px 44px;
                  gap:0;padding:8px 14px;
                  background:var(--navy);border-radius:8px 8px 0 0;
                  font-size:.67rem;font-weight:600;color:rgba(255,255,255,.55);
                  letter-spacing:.6px;text-transform:uppercase;align-items:center;">
        <span>${isEn?'COMPANY':'公司'}</span>
        <span>${isEn?'STATUS':'进度'}</span>
        <span>${isEn?'TYPE':'类型'}</span>
        <span>${isEn?'LATEST ANNOUNCEMENT':'最新公告'}</span>
        <span style="text-align:right;">${isEn?'DATE':'日期'}</span>
        <span style="text-align:center;">${isEn?'N':'条'}</span>
      </div>
    </div>

    <!-- 数据列表 -->
    <div id="soList" style="border:1px solid var(--border);border-radius:0 0 10px 10px;overflow:hidden;margin-top:-20px;">`;

    companies.forEach((c, idx) => {
      const ann  = c.announcements || [];
      const prog = _soProgress(ann, isEn);
      const latest = ann[0] || {};
      const sub  = c.spinTarget || _soExtractSpinSub(c);
      const cleanLatest = _soCleanTitle(latest.title||'');
      const isEven = idx % 2 === 0;

      // 进度进度条
      const bar = `
        <div style="display:flex;align-items:center;gap:5px;flex-wrap:nowrap;">
          <div style="width:48px;height:4px;background:#e5e7eb;border-radius:2px;overflow:hidden;flex-shrink:0;">
            <div style="width:${prog.pct}%;height:100%;background:${prog.color};border-radius:2px;"></div>
          </div>
          <span style="font-size:.68rem;color:${prog.color};font-weight:600;white-space:nowrap;
                       background:${prog.bg};padding:1px 6px;border-radius:10px;">
            ${prog.label}
          </span>
        </div>`;

      html += `
      <!-- row ${idx} -->
      <div>
        <div onclick="soToggle(${idx})" style="
              display:grid;grid-template-columns:120px 118px 88px 1fr 88px 44px;
              gap:0;padding:10px 14px;
              background:${isEven?'#fff':'#faf9f7'};
              border-bottom:1px solid var(--border-light);
              cursor:pointer;align-items:center;
              transition:background .1s;"
             onmouseover="this.style.background='#f5f0e6'"
             onmouseout="this.style.background='${isEven?'#fff':'#faf9f7'}'">
          <!-- 公司 -->
          <div>
            <div style="font-weight:700;font-size:.84rem;color:var(--navy);letter-spacing:.3px;line-height:1.2;">${fmtTicker(c.ticker)}</div>
            <div style="font-size:.7rem;color:var(--text-light);margin-top:2px;
                        white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:118px;"
                 title="${c.stockName}">${c.stockName}</div>
            ${sub?`<div style="font-size:.65rem;color:var(--gold);margin-top:3px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:120px;font-weight:500;" title="${sub}">↗ ${sub}</div>`:''}
          </div>
          <!-- 进度 -->
          <div>${bar}</div>
          <!-- 类型 -->
          <div style="padding:0 4px;">${_soTypeBadge(c.spinType, isEn)}</div>
          <!-- 最新公告 -->
          <div style="padding:0 10px;overflow:hidden;">
            ${latest.docUrl
              ? `<a href="${latest.docUrl}" target="_blank" rel="noopener"
                    onclick="event.stopPropagation()"
                    style="font-size:.78rem;color:var(--navy);text-decoration:none;
                           display:block;line-height:1.4;
                           white-space:nowrap;overflow:hidden;text-overflow:ellipsis;"
                    title="${cleanLatest}">${cleanLatest.slice(0,62)}${cleanLatest.length>62?'…':''}</a>`
              : `<span style="font-size:.78rem;color:var(--text);">${cleanLatest.slice(0,62)}</span>`}
            ${ann.length>1?`<div style="font-size:.62rem;color:var(--text-lighter);margin-top:2px;">
              共 ${ann.length} 条公告 · 首次 ${c.firstDate}
            </div>`:''}
          </div>
          <!-- 日期 -->
          <div style="font-size:.72rem;color:var(--text-light);text-align:right;white-space:nowrap;">${c.latestDate}</div>
          <!-- 展开箭头 -->
          <div id="so-arr-${idx}" style="text-align:center;font-size:.72rem;color:var(--gold);
               transition:transform .2s;">▶</div>
        </div>

        <!-- 时间线展开区 -->
        <div id="so-body-${idx}" style="display:none;background:#f8f6f0;border-bottom:1px solid var(--border);">
          ${sub?`<div style="padding:8px 14px 4px;font-size:.72rem;color:var(--text-light);">
            <span style="color:var(--gold);font-weight:600;">分拆标的：</span>${sub}
            &nbsp;&nbsp;
            <span style="color:var(--text-lighter);">${c.summary||''}</span>
          </div>`:`<div style="padding:6px 14px 2px;font-size:.7rem;color:var(--text-lighter);">${c.summary||''}</div>`}

          <!-- 进度条（完整版） -->
          <div style="margin:6px 14px 0;background:#e5e7eb;border-radius:4px;height:6px;overflow:hidden;">
            <div style="width:${prog.pct}%;height:100%;background:linear-gradient(90deg,${prog.color}99,${prog.color});border-radius:4px;transition:width .5s;"></div>
          </div>

          <!-- 时间线 -->
          <div style="padding:10px 14px 14px;position:relative;">
            <div style="position:absolute;left:21px;top:10px;bottom:14px;width:2px;
                        background:linear-gradient(180deg,${prog.color}80 0%,${prog.color}15 100%);"></div>
            ${ann.map((a,ai)=>{
              const ct = _soCleanTitle(a.title);
              const isLatest = ai===0;
              return `
              <div style="display:grid;grid-template-columns:14px 88px 1fr auto;
                           gap:8px;align-items:flex-start;padding:5px 0;position:relative;z-index:1;">
                <!-- 圆点 -->
                <div style="width:10px;height:10px;border-radius:50%;margin-top:3px;flex-shrink:0;
                             background:${isLatest?prog.color:'#d1d5db'};
                             border:2px solid ${isLatest?prog.color:'#e5e7eb'};
                             ${isLatest?'box-shadow:0 0 0 3px '+prog.color+'28;':''}"></div>
                <!-- 日期 -->
                <span style="font-size:.68rem;color:${isLatest?prog.color:'var(--text-lighter)'};
                              font-variant-numeric:tabular-nums;white-space:nowrap;
                              font-weight:${isLatest?'600':'400'};padding-top:2px;">${a.date}</span>
                <!-- 标题 -->
                <a href="${a.docUrl}" target="_blank" rel="noopener"
                   onclick="event.stopPropagation()"
                   style="font-size:.78rem;line-height:1.45;text-decoration:none;
                          color:${isLatest?'var(--navy)':'var(--text-light)'};
                          font-weight:${isLatest?'500':'400'};"
                   title="${ct}">${ct.slice(0,85)}${ct.length>85?'…':''}</a>
                <!-- PDF按钮 -->
                <a href="${a.docUrl}" target="_blank" rel="noopener" onclick="event.stopPropagation()"
                   style="font-size:.63rem;padding:2px 7px;flex-shrink:0;
                          border:1px solid ${isLatest?'var(--gold)':'#d1d5db'};
                          color:${isLatest?'var(--gold)':'var(--text-lighter)'};
                          border-radius:4px;text-decoration:none;white-space:nowrap;
                          transition:all .15s;"
                   onmouseover="this.style.borderColor='var(--gold)';this.style.color='var(--gold)'"
                   onmouseout="this.style.borderColor='${isLatest?'var(--gold)':'#d1d5db'}';this.style.color='${isLatest?'var(--gold)':'var(--text-lighter)'}'">
                   PDF ↗</a>
              </div>`;
            }).join('')}
          </div>
        </div>
      </div>`;
    });

    html += `</div>
    <div style="font-size:.65rem;color:var(--text-lighter);margin-top:12px;padding:6px 12px;
                background:#f8f6f0;border-radius:6px;line-height:1.7;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px;">
      <span>📋 ${isEn
        ? 'Source: HKEXnews · Keywords: 分拆 / spin-off / demerger · Stocks &lt; HK$0.5 excluded'
        : '数据来源：港交所新闻 · 关键词：分拆/spin-off/demerger · 现价低于HK$0.5已过滤'}</span>
      <span>${isEn?'Auto-updated daily via GitHub Actions':'每日通过 GitHub Actions 自动更新'}</span>
    </div>`;

    el.innerHTML = html;
    _spinoffCache = el.innerHTML;
    // 默认隐藏 REIT，渲染完成后立即过滤一次
    setTimeout(() => _soApplyFilters(), 0);

  } catch(e) {
    console.error('spinoff error:', e);
    el.innerHTML = `<div style="padding:24px;text-align:center;color:var(--text-lighter);">
      ${lang==='en'?'Spin-off data unavailable. Try refreshing.':'分拆数据加载失败，请刷新页面。'}
    </div>`;
  }
}

function _soTypeBadge(st, isEn) {
  if (!st) return '';
  const code  = st.code  || 'unknown';
  const label = isEn ? (st.label_en || 'Spinoff') : (st.label_zh || '\u5206\u62c6');
  const palettes = {
    ipo_hk:       { bg:'#e0f2fe', color:'#0369a1', border:'#bae6fd' },
    ipo_a_sh:     { bg:'#fef9c3', color:'#854d0e', border:'#fde68a' },
    ipo_a_sz:     { bg:'#fef9c3', color:'#854d0e', border:'#fde68a' },
    ipo_a:        { bg:'#fef9c3', color:'#854d0e', border:'#fde68a' },
    ipo_other:    { bg:'#f3f4f6', color:'#6b7280', border:'#e5e7eb' },
    reit_sz:      { bg:'#f0fdf4', color:'#166534', border:'#bbf7d0' },
    reit_sh:      { bg:'#f0fdf4', color:'#166534', border:'#bbf7d0' },
    reit:         { bg:'#f0fdf4', color:'#166534', border:'#bbf7d0' },
    split_direct: { bg:'#fdf2f8', color:'#9d174d', border:'#fbcfe8' },
    unknown:      { bg:'#f9fafb', color:'#9ca3af', border:'#e5e7eb' },
  };
  const p = palettes[code] || palettes.unknown;
  return '<span style="display:inline-block;font-size:.62rem;padding:2px 7px;' +
    'border-radius:10px;font-weight:600;white-space:nowrap;line-height:1.5;' +
    'background:' + p.bg + ';color:' + p.color + ';border:1px solid ' + p.border + ';">' +
    label + '</span>';
}

let _soShowReit = false;   // 默认隐藏 REIT
function soToggleReit() {
  _soShowReit = !_soShowReit;
  const btn = document.getElementById('soBtn-reit');
  if (btn) {
    btn.style.background   = _soShowReit ? 'var(--navy)' : '#fff';
    btn.style.color        = _soShowReit ? '#fff' : 'var(--text-light)';
    btn.style.borderColor  = _soShowReit ? 'var(--navy)' : 'var(--border)';
    btn.textContent        = _soShowReit ? (lang==='en'?'− REIT':'－ REIT') : (lang==='en'?'+ REIT':'＋ REIT');
  }
  _soApplyFilters();
}

function _soIsReit(row) {
  // 通过行内类型 badge 文本判断是否为 REIT
  const badge = row.querySelector('span[style*="#f0fdf4"]');
  return !!badge;
}

function _soApplyFilters() {
  const rows = document.querySelectorAll('#soList > div');
  const kw = (document.getElementById('soSearch')?.value || '').toLowerCase().trim();
  rows.forEach(row => {
    // 关键词过滤
    const textMatch = !kw || row.textContent.toLowerCase().includes(kw);
    // REIT 过滤
    const reitMatch = _soShowReit || !_soIsReit(row);
    // 状态过滤
    let statusMatch = true;
    if (_soStatusFilter !== 'all') {
      const badgeSpan = row.querySelector('span[style*="border-radius:10px"]');
      const text = (badgeSpan ? badgeSpan.textContent : row.textContent).toLowerCase();
      const matchKw = {
        progress:  ['进行中','in progress','生效'],
        proposed:  ['建议中','proposed'],
        approved:  ['批准','approved'],
        listed:    ['上市','listed','完成','招股书','ipo'],
        cancelled: ['终止','cancelled'],
      }[_soStatusFilter] || [];
      statusMatch = matchKw.some(m => text.includes(m));
    }
    row.style.display = (textMatch && reitMatch && statusMatch) ? '' : 'none';
  });
}

function soFilter(q) {
  _soApplyFilters();
}

let _soStatusFilter = 'all';
function soFilterStatus(status) {
  _soStatusFilter = status;
  ['all','progress','proposed','approved','listed','cancelled'].forEach(s => {
    const btn = document.getElementById('soBtn-' + s);
    if (!btn) return;
    const active = s === status;
    btn.style.background   = active ? 'var(--navy)' : '#fff';
    btn.style.color        = active ? '#fff' : 'var(--text-light)';
    btn.style.borderColor  = active ? 'var(--navy)' : 'var(--border)';
  });
  _soApplyFilters();
}

function soToggle(idx) {
  const body  = document.getElementById('so-body-' + idx);
  const arrow = document.getElementById('so-arr-'  + idx);
  if (!body) return;
  const open = body.style.display !== 'none';
  // 带过渡的展开/收起
  if (!open) {
    body.style.display   = 'block';
    body.style.opacity   = '0';
    body.style.transform = 'translateY(-4px)';
    setTimeout(() => {
      body.style.transition = 'opacity .18s ease, transform .18s ease';
      body.style.opacity    = '1';
      body.style.transform  = 'translateY(0)';
    }, 10);
  } else {
    body.style.transition = 'opacity .15s ease';
    body.style.opacity    = '0';
    setTimeout(() => { body.style.display = 'none'; body.style.transition = ''; }, 150);
  }
  if (arrow) {
    arrow.textContent = open ? '▶' : '▼';
    arrow.style.color = open ? 'var(--gold)' : 'var(--navy)';
  }
}

// 兼容旧调用
function spinoffToggle(idx) { soToggle(idx); }



function updateInvestorContent() {
  var en = lang === 'en', isP = investor === 'pabrai', isD = investor === 'duan', isT = investor === 'tepper', isS = investor === 'spier', isW = investor === 'webb', isB = investor === 'buffett', isA = investor === 'akre', isG = investor === 'greenberg';
  // Hero
  var ht = document.querySelector('[data-i18n="heroTitle"]');
  if (ht) ht.textContent = isB ? (en?'Buffett 13F Tracker':'巴菲特 13F 持仓追踪') : (isW ? (en?'David Webb HK Holdings':'大卫·韦伯 港股持仓') : (isP ? (en?'Pabrai 13F Tracker':'帕伯莱 13F 持仓追踪') : (isD ? (en?'Duan Yongping 13F Tracker':'段永平 13F 持仓追踪') : (isT ? (en?'David Tepper 13F Tracker':'大卫·泰珀 13F 持仓追踪') : (isS ? (en?'Guy Spier 13F Tracker':'盖伊·斯皮尔 13F 持仓追踪') : (isA ? (en?'Chuck Akre 13F Tracker':'查克·阿克雷 13F 持仓追踪') : (isG ? (en?'Glenn Greenberg 13F Tracker':'格伦·格林伯格 13F 持仓追踪') : (en?'Li Lu 13F Tracker':'李录 13F 持仓追踪'))))))));
  var hsub = document.querySelector('.hero-title .sub');
  if (hsub) hsub.textContent = isB ? (en ? 'Berkshire Hathaway · SEC 13F · Largest 13F Filer' : '伯克希尔·哈撒韦 · SEC 13F · 最大 13F 申报人') : (isW ? (en ? 'Webb-site.com · HKEX Disclosures · Activist Investor' : 'Webb-site.com · 港股披露 · 维权投资者') : (isP ? (en ? 'Dalal Street, LLC — Tracking Master Moves' : 'Dalal Street, LLC — 学习大师持仓变化') : (isD ? (en ? 'H&H International Investment · Value Investing' : 'H&H International Investment · 价值投资') : (isT ? (en ? 'Appaloosa LP · SEC 13F · Macro & Concentrated Bets' : 'Appaloosa LP · SEC 13F · 宏观与集中持仓') : (isS ? (en ? 'Aquamarine Capital · Deep Value Investing' : 'Aquamarine Capital · 深度价值投资') : (isA ? (en ? 'Akre Capital Management · Compounding Machines' : 'Akre Capital Management · 复利机器') : (isG ? (en ? 'Brave Warrior Advisors · Concentrated Value' : 'Brave Warrior Advisors · 集中价值投资') : (en ? 'Himalaya Capital — Tracking Master Moves' : 'Himalaya Capital Management — 学习大师持仓变化'))))))));
  // Quote
  var qb = document.querySelector('.quote-block blockquote');
  if (qb) qb.textContent = isB
    ? (en?'"Be fearful when others are greedy, and greedy when others are fearful."':'"别人贪婪时我恐惧，别人恐惧时我贪婪。"')
    : (isP
    ? (en?'"Heads I win, tails I don\u2019t lose much."':'"正面我赢，反面我也输不了多少。"')
    : (isD ? (en?'"Buying stocks is buying companies."':'"买股票就是买公司。"') : (isT ? (en?'"The best time to buy is when there\u2019s blood in the streets."':'"最好的买入时机是街头流血时。"') : (isS ? (en?'"Investing is simple, but not easy. Most people are their own worst enemy."':'"投资简单但不容易。大多数人是自己最大的敌人。"') : (isW ? (en?'"Sunlight is the best disinfectant."':'"阳光是最好的消毒剂。"') : (isA ? (en?'"The key to investing is to find a business that\u2019s a compounding machine, and then let it compound."':'"投资的关键是找到一台复利机器，然后让它持续复利。"') : (isG ? (en?'"We look for companies that generate high returns on capital, have strong competitive positions, and are run by good people."':'"我们寻找资本回报率高、竞争优势强、由优秀人才经营的企业。"') : (en?'"The macro is what we must accept; the micro is what we can act on."':'"宏观是我们必须接受的，微观是我们有所作为的。"'))))))));
  var qa = document.querySelector('.quote-block .attr');
  if (qa) qa.textContent = isB
    ? (en?'— Warren Buffett, Berkshire Hathaway Annual Letter':'— 沃伦·巴菲特，伯克希尔·哈撒韦年度信')
    : (isP
    ? '— Mohnish Pabrai, The Dhandho Investor'
    : (isD ? (en?'— Duan Yongping, Xueqiu (大道无形我有型)':'— 段永平，雪球（大道无形我有型）') : (isT ? (en?'— David Tepper, Appaloosa Management':'— 大卫·泰珀，Appaloosa Management') : (isS ? (en?'— Guy Spier, The Education of a Value Investor':'— 盖伊·斯皮尔，《价值投资者的修炼》') : (isW ? (en?'— David Webb, Webb-site.com':'— 大卫·韦伯，Webb-site.com') : (isA ? (en?'— Chuck Akre':'— 查克·阿克雷') : (isG ? (en?'— Glenn Greenberg':'— 格伦·格林伯格') : (en?'— Li Lu, Peking University, Dec 2024':'— 李录，北京大学演讲，2024年12月'))))))));
  // Labels
  var al = document.getElementById('aboutLabel'); if (al) al.textContent = isB ? 'About Buffett' : (isW ? 'About Webb' : (isP ? (en?'About Pabrai':'关于帕伯莱') : (isD ? (en?'About Duan':'关于段永平') : (isT ? (en?'About Tepper':'关于泰珀') : (isS ? (en?'About Spier':'关于斯皮尔') : (isA ? (en?'About Akre':'关于阿克雷') : (isG ? (en?'About Greenberg':'关于格林伯格') : (en?'About Li Lu':'关于李录'))))))));
  var at = document.getElementById('aboutTitle'); if (at) at.innerHTML = isB
    ? (en?'Warren Buffett \u2014 The Oracle of Omaha':'沃伦·巴菲特 \u2014 奥马哈先知')
    : (isP
    ? (en?'Mohnish Pabrai — Cloning & Dhandho':'Mohnish Pabrai — 从 Cloning 到 Dhandho')
    : (isD ? (en?"Duan Yongping \u2014 China\u2019s Buffett":'段永平 \u2014 中国巴菲特') : (isT ? (en?'David Tepper \u2014 Macro Bets & Distressed Debt':'大卫·泰珀 \u2014 宏观押注与困境债务') : (isS ? (en?'Guy Spier \u2014 The Education of a Value Investor':'盖伊·斯皮尔 \u2014 价值投资者的修炼') : (isW ? (en?'David Webb \u2014 The Activist Investor':'大卫·韦伯 \u2014 维权投资者') : (isA ? (en?'Chuck Akre \u2014 The Three-Legged Stool':'查克·阿克雷 \u2014 三条腿的凳子') : (isG ? (en?'Glenn Greenberg \u2014 Concentrated Value':'格伦·格林伯格 \u2014 集中价值投资') : (en?'About Li Lu & Himalaya Capital':'关于李录与喜马拉雅资本'))))))));
  var pl = document.getElementById('philLabel'); if (pl) pl.textContent = isB ? 'Philosophy' : (isW ? 'Philosophy' : (isP ? 'Dhandho' : (isD ? (en?'Philosophy':'投资理念') : (isT ? (en?'Philosophy':'投资理念') : (isS ? (en?'Philosophy':'投资理念') : (isA ? (en?'Philosophy':'投资理念') : (isG ? (en?'Philosophy':'投资理念') : (en?'Philosophy':'投资理念'))))))));
  var pt = document.getElementById('philTitle'); if (pt) pt.innerHTML = isB
    ? (en?'Philosophy \u2014 Value Investing Principles':'投资理念 \u2014 价值投资原则')
    : (isP
    ? (en?'Philosophy \u2014 The Dhandho Way':'投资理念 \u2014 Dhandho 法')
    : (isD ? (en?'Philosophy \u2014 Buy Companies, Not Stocks':'投资理念 \u2014 买股票就是买公司') : (isT ? (en?'Philosophy \u2014 Macro Vision & Concentrated Bets':'投资理念 \u2014 宏观视野与集中押注') : (isS ? (en?'Philosophy \u2014 Deep Value, Buffett Style':'投资理念 \u2014 深度价值，巴菲特风格') : (isW ? (en?'Philosophy \u2014 Activist Principles':'投资理念 \u2014 维权原则') : (isA ? (en?'Philosophy \u2014 Compounding Machines':'投资理念 \u2014 复利机器') : (isG ? (en?'Philosophy \u2014 Concentrated Value':'投资理念 \u2014 集中价值投资') : (en?'Philosophy \u2014 Graham \u2192 Buffett \u2192 Munger \u2192 Li Lu':'投资理念 \u2014 格雷厄姆 \u2192 巴菲特 \u2192 芒格 \u2192 李录'))))))));
  var rl = document.getElementById('readLabel'); if (rl) rl.textContent = isB ? 'Readings' : (isW ? 'Readings' : (isP ? (en?'Resources':'资源') : (isT ? (en?'Readings':'延伸阅读') : (isS ? (en?'Readings':'延伸阅读') : (isA ? (en?'Readings':'延伸阅读') : (isG ? (en?'Readings':'延伸阅读') : (en?'Readings':'延伸阅读')))))));
  var navAb = document.querySelector('[data-i18n="navAbout"]'); if (navAb) navAb.textContent = isB ? (en?'About Buffett':'关于巴菲特') : (isW ? (en?'About Webb':'关于韦伯') : (isP ? (en?'About Pabrai':'关于帕伯莱') : (isD ? (en?'About Duan':'关于段永平') : (isT ? (en?'About Tepper':'关于泰珀') : (isS ? (en?'About Spier':'关于斯皮尔') : (isA ? (en?'About Akre':'关于阿克雷') : (isG ? (en?'About Greenberg':'关于格林伯格') : (en?'About':'关于李录'))))))));
  // About text
  var rt = document.querySelector('.ref-text');
  if (rt) {
    if (isP) {
      rt.innerHTML = en
        ? '<p>Mohnish Pabrai (b. 1964), Indian-American value investor, founder of Pabrai Investment Funds. Started with $1M in 1999 after selling his IT company.</p><p>Created the <strong>Dhandho</strong> framework \u2014 Heads I win, tails I don\u2019t lose much \u2014 focused on distressed turnarounds. Won Buffett charity lunch for $650K in 2007.</p><p>Author of <em>The Dhandho Investor</em>, runs blog <a href=https://www.chaiwithpabrai.com target=_blank>Chai with Pabrai</a>.</p>'
        : '<p>Mohnish Pabrai\uff0c1964 年生于印度\uff0cPabrai Investment Funds 创始人。1999 年以 100 万美元起步投身价值投资。</p><p>提出 <strong>Dhandho</strong> 投资框架\u2014\u2014正面我赢\uff0c反面我也输不了多少\uff0c专注于困境反转和深度价值。2007 年以 65 万美元拍下巴菲特慈善午餐。</p><p>著有 <em>The Dhandho Investor</em>\uff0c运营博客 <a href=https://www.chaiwithpabrai.com target=_blank>Chai with Pabrai</a>\u3002</p>';
    } else if (isD) {
      rt.innerHTML = en
        ? '<p>Duan Yongping (b. 1961, Nanchang), Chinese entrepreneur and value investor. Founded Subor (\u5c0f\u9738\u738b, 1989) and BBK Electronics (\u6b65\u6b65\u9ad8, 1995), which spawned OPPO, vivo, OnePlus, and realme.</p><p>Known as <strong>"China\u2019s Buffett"</strong> (\u4e2d\u56fd\u5df4\u7279\u83f2). Heavy AAPL holder since ~2011. Philosophy: "Buying stocks is buying companies" (\u4e70\u80a1\u7968\u5c31\u662f\u4e70\u516c\u53f8). "Don\u2019t short, don\u2019t use margin, don\u2019t invest in what you don\u2019t understand" (\u4e0d\u505a\u7a7a\uff0c\u4e0d\u501f\u94b1\uff0c\u4e0d\u61c2\u4e0d\u505a).</p><p>Active on Xueqiu (\u96ea\u7403) as "\u5927\u9053\u65e0\u5f62\u6211\u6709\u578b". Retired early, focused on investing and philanthropy.</p>'
        : '<p>\u6bb5\u6c38\u5e73\uff0c1961 年生于江西南昌\uff0c企业家、价值投资者。1989 年创立小霸王\uff0c1995 年创立步步高\uff0c后衍生出 OPPO、vivo、一加、realme 等品牌。</p><p>被称为<strong>"中国巴菲特"</strong>。自 2011 年起重仓苹果。投资理念\uff1a"买股票就是买公司"、"不做空\uff0c不借钱\uff0c不懂不做"。</p><p>活跃于雪球平台\uff0c网名"大道无形我有型"\uff0c分享投资思考。早年退出一线\uff0c专注于投资和公益。</p>';
    } else if (isB) {
      rt.innerHTML = en
        ? '<p>Warren Buffett (b. 1930), Chairman and CEO of <strong>Berkshire Hathaway</strong>, widely regarded as the greatest investor of all time. Learned value investing from Benjamin Graham at Columbia Business School.</p><p>Built Berkshire Hathaway from a failing textile mill into a $1+ trillion conglomerate over six decades. Known for his long-term, concentrated approach: buying wonderful businesses at fair prices and holding them forever.</p><p>His annual shareholder letters are considered the bible of value investing. Philanthropically, he has pledged 99% of his wealth to the Gates Foundation and other charities through the Giving Pledge.</p>'
        : '<p>沃伦·巴菲特（Warren Buffett），1930 年出生，<strong>伯克希尔·哈撒韦</strong>董事长兼 CEO，被公认为史上最伟大的投资者。在哥伦比亚商学院师从本杰明·格雷厄姆学习价值投资。</p><p>用六十年时间将伯克希尔从一家衰落的纺织厂打造成万亿美元企业集团。以长期、集中投资而闻名：以合理价格买入优秀企业并永久持有。</p><p>他的年度股东信被誉为价值投资的圣经。慈善方面，通过“捐赠誓言”承诺将 99% 的财富捐给盖茨基金会等慈善机构。</p>';
    } else if (isW) {
      rt.innerHTML = en
        ? '<p>David Webb (1965\u20132026), British-born corporate governance activist and value investor based in Hong Kong. Founder of <strong>Webb-site.com</strong>, the most influential independent source of HK corporate governance intelligence.</p><p>A fierce advocate for minority shareholder rights, Webb exposed corporate governance failures at dozens of Hong Kong-listed companies. His "Enigma Network" research in 2017 triggered a regulatory investigation into a web of interconnected HK-listed firms.</p><p>Webb lived modestly, invested in undervalued small-cap HK stocks, and shared his research openly. Diagnosed with prostate cancer in 2018, he continued publishing until his death in 2026. His motto: <em>"Sunlight is the best disinfectant."</em></p>'
        : '<p>大卫·韦伯（David Webb，1965\u20132026），英国出生的企业管治维权者与价值投资者，长期驻香港。<strong>Webb-site.com</strong> 创始人，香港最具影响力的独立企业管治信息来源。</p><p>以坚定维护小股东权益著称，揭露数十家港股公司的管治问题。2017 年发布的“谜网”（Enigma Network）研究报告引发监管层对一批相互关联港股公司的调查。</p><p>韦伯生活简朴，专投被低估的港股小型股，并公开分享研究。2018 年确诊前列腺癌，仍坚持发布分析直至 2026 年去世。他的信条：<em>“阳光是最好的消毒剂。”</em></p>';
    } else if (isA) {
      rt.innerHTML = en
        ? '<p>Chuck Akre, founder of Akre Capital Management, is known for his <strong>three-legged stool</strong> investment framework: an extraordinary business (high ROE, low capital reinvestment needs), excellent management (honest, capable, skilled capital allocators), and abundant reinvestment opportunities.</p><p>Akre managed the FBR Focus Fund for 13 years with annualized returns exceeding 20%, beating 99% of peers. He founded Akre Capital Management in 2009, concentrating on a handful of "compounding machine" companies held for the long term with minimal turnover.</p><p>His portfolio typically holds ~20 high-quality companies. His philosophy: find a business that can reinvest its profits at high rates of return, then hold on and let compounding do its work.</p>'
        : '<p>查克·阿克雷（Chuck Akre），Akre Capital Management 创始人，以<strong>“三条腿的凳子”</strong>投资框架闻名：卓越的商业模式（高ROE、无需大量资本再投资）、优秀的管理层（诚实能干、善于资本配置）、以及持续的再投资机会。</p><p>阿克雷管理 FBR Focus Fund 长达 13 年，年化回报率超过 20%，击败了 99% 的同类基金。2009 年创立 Akre Capital Management，坚持集中投资于少数“复利机器”型公司，长期持有，极少交易。</p><p>他的投资组合通常持有约 20 只高质量公司。他信奉：找到能以高回报率持续再投资的企业，然后让复利发挥作用。</p>';
    } else if (isG) {
      rt.innerHTML = en
        ? '<p>Glenn Greenberg, founder of Brave Warrior Advisors, is one of the most respected <strong>concentrated value investors</strong>. He began his career at Chieftain Capital Management, studying under value investing masters, and founded Brave Warrior in 2010.</p><p>Greenberg is known for extremely concentrated portfolios \u2014 typically just 8-12 stocks, each deeply researched. He focuses on businesses with high returns on capital, strong competitive moats, and excellent management, willing to buy aggressively during market panics.</p><p>His investment style is deeply influenced by Buffett and Munger, emphasizing "buy wonderful businesses and hold them for the long term." As of 2026, Brave Warrior manages approximately $4 billion, concentrated in financial services and quality compounders.</p>'
        : '<p>格伦·格林伯格（Glenn Greenberg），Brave Warrior Advisors 创始人，是价值投资领域最受尊敬的<strong>集中投资者</strong>之一。他在 Chieftain Capital Management 开始了投资生涯，师从价值投资大师，2010 年创立 Brave Warrior。</p><p>格林伯格以极度集中的投资组合闻名\u2014\u2014通常仅持有 8-12 只股票，每只都经过深入研究。他专注于具有高资本回报率、强竞争优势和优秀管理层的企业，愿意在市场恐慌时大举买入。</p><p>他的投资风格深受巴菲特和芒格影响，强调“买入优秀企业并长期持有”。截至 2026 年，Brave Warrior 管理约 40 亿美元，持仓集中于金融服务和高质量复利企业。</p>';
    } else if (isT) {
      rt.innerHTML = en
        ? '<p>David Tepper (b. 1957, Pittsburgh), founder of <strong>Appaloosa Management</strong>. Started at Goldman Sachs trading junk bonds, then founded Appaloosa in 1993.</p><p>Known for his bold macro bets during crises. In 2009, he made ~$7B profit buying distressed bank stocks during the financial crisis — one of the greatest trades in hedge fund history.</p><p>His philosophy: top-down macro analysis, concentrated bets when conviction is high, and aggressive repositioning when the picture changes. Not a buy-and-hold investor — willing to exit quickly.</p>'
        : '<p>大卫·泰珀（David Tepper），1957 年生于匹兹堡，<strong>Appaloosa Management</strong> 创始人。早年在高盛从事垃圾债券交易，1993 年创立 Appaloosa。</p><p>以危机中大胆押注著称。2009 年金融危机中大举买入银行股，获利约 70 亿美元，是对冲基金史上最成功的交易之一。</p><p>他的理念：自上而下的宏观分析，高确信度时集中下注，形势变化时迅速调仓。不是买入持有型投资者，敢于快速止盈止损。</p>';
    } else if (isS) {
      rt.innerHTML = en
        ? '<p>Guy Spier (b. 1966), Swiss-based value investor, founder of <strong>Aquamarine Capital</strong>. Graduated from Oxford and Harvard Business School.</p><p>Author of <em>The Education of a Value Investor</em> (2014), chronicling his transformation from a Gordon Gekko-style banker to a Buffett disciple. In 2007, he and Mohnish Pabrai paid $650,100 for a charity lunch with Warren Buffett.</p><p>His philosophy emphasizes the importance of environment, psychology, and self-awareness in investing. He moved from New York to Zurich partly to escape Wall Street\'s short-term thinking culture.</p>'
        : '<p>盖伊·斯皮尔（Guy Spier），1966 年生，旅居瑞士的价值投资者，<strong>Aquamarine Capital</strong> 创始人。牛津大学和哈佛商学院毕业。</p><p>著有《价值投资者的修炼》（2014），记录了他从戈登·盖柯式银行家转变为巴菲特信徒的历程。2007 年与帕伯莱合出 65.01 万美元，竞拍巴菲特慈善午餐。</p><p>他的理念强调投资环境、心理和自我认知的重要性。他从纽约移居苏黎世，部分原因是为了远离华尔街的短视文化。</p>';
    } else {
      rt.innerHTML = en
        ? '<p>Li Lu (b. 1966), Chinese-American value investor, founder of Himalaya Capital. Earned BA, JD, and MBA at Columbia University.</p><p>Founded Himalaya Capital in 1997. Recommended BYD to Charlie Munger in 2002, leading to Berkshire\'s $230M investment.</p><p>Active in philanthropy through his humanitarian foundation.</p>'
        : '<p>李录（Li Lu），1966 年生于唐山，美籍华裔价值投资者，喜马拉雅资本创始人。哥伦比亚大学 BA/JD/MBA 三学位。</p><p>1997 年创立喜马拉雅资本。2002 年向查理·芒格推荐比亚迪，伯克希尔 2008 年投资 2.3 亿美元。</p><p>热心公益，设立了人道主义基金会。</p>';
    }
  }
  // Timeline
  var tl = document.querySelector('.ref-grid .timeline');
  if (tl) {
    if (isP) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1964</div><div class="tl-text">出生于印度</div></div><div class="tl-item"><div class="tl-year">1999</div><div class="tl-text">100 万美元起步投资</div></div><div class="tl-item"><div class="tl-year">2007</div><div class="tl-text">出版 The Dhandho Investor</div></div><div class="tl-item"><div class="tl-year">2007</div><div class="tl-text">65 万美元拍下巴菲特午餐</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">管理 Pabrai Funds + 博客</div></div>';
    } else if (isD) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1961</div><div class="tl-text">出生于江西南昌</div></div><div class="tl-item"><div class="tl-year">1982</div><div class="tl-text">浙江大学无线电工程专业</div></div><div class="tl-item"><div class="tl-year">1989</div><div class="tl-text">创立小霸王电子工业公司</div></div><div class="tl-item"><div class="tl-year">1995</div><div class="tl-text">创立步步高电子</div></div><div class="tl-item"><div class="tl-year">2001</div><div class="tl-text">退出一线，移居美国</div></div><div class="tl-item"><div class="tl-year">2002</div><div class="tl-text">结识巴菲特，开始投资</div></div><div class="tl-item"><div class="tl-year">2006</div><div class="tl-text">62 万美元拍下巴菲特午餐（与黄峥）</div></div><div class="tl-item"><div class="tl-year">~2011</div><div class="tl-text">开始大量买入苹果</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">管理 H&H International Investment</div></div>';
    } else if (isT) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1957</div><div class="tl-text">出生于匹兹堡</div></div><div class="tl-item"><div class="tl-year">~1980</div><div class="tl-text">卡内基梅隆大学，后获 MBA</div></div><div class="tl-item"><div class="tl-year">~1982</div><div class="tl-text">加入高盛，从事垃圾债券交易</div></div><div class="tl-item"><div class="tl-year">1993</div><div class="tl-text">创立 Appaloosa Management</div></div><div class="tl-item"><div class="tl-year">2009</div><div class="tl-text">金融危机中大胆买入银行股</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">管理 Appaloosa LP，宏观押注与集中持仓</div></div>';
    } else if (isS) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1966</div><div class="tl-text">出生于南非</div></div><div class="tl-item"><div class="tl-year">~1988</div><div class="tl-text">牛津大学 PPE 学位</div></div><div class="tl-item"><div class="tl-year">~1990</div><div class="tl-text">哈佛商学院 MBA</div></div><div class="tl-item"><div class="tl-year">1997</div><div class="tl-text">创立 Aquamarine Capital</div></div><div class="tl-item"><div class="tl-year">2007</div><div class="tl-text">65 万美元拍下巴菲特午餐（与帕伯莱）</div></div><div class="tl-item"><div class="tl-year">2014</div><div class="tl-text">出版 The Education of a Value Investor</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">常驻苏黎世，管理 Aquamarine Capital</div></div>';
    } else if (isB) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1930</div><div class="tl-text">出生于内布拉斯加州奥马哈</div></div><div class="tl-item"><div class="tl-year">1951</div><div class="tl-text">师从格雷厄姆，哥伦比亚 MBA</div></div><div class="tl-item"><div class="tl-year">1956</div><div class="tl-text">创立 Buffett Partnership</div></div><div class="tl-item"><div class="tl-year">1965</div><div class="tl-text">收购 Berkshire Hathaway</div></div><div class="tl-item"><div class="tl-year">1988</div><div class="tl-text">开始大量买入可口可乐</div></div><div class="tl-item"><div class="tl-year">2016</div><div class="tl-text">开始买入苹果，迄今最大持仓</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">管理伯克希尔·哈撒韦，$263B 组合</div></div>';
    } else if (isW) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1965</div><div class="tl-text">出生于英国</div></div><div class="tl-item"><div class="tl-year">~1990</div><div class="tl-text">牛津大学数学系</div></div><div class="tl-item"><div class="tl-year">1998</div><div class="tl-text">创立 Webb-site.com</div></div><div class="tl-item"><div class="tl-year">2003</div><div class="tl-text">获选港交所独立非执行董事</div></div><div class="tl-item"><div class="tl-year">2017</div><div class="tl-text">发布"谜网"报告，揭露 50 只不可投资港股</div></div><div class="tl-item"><div class="tl-year">2018</div><div class="tl-text">确诊前列腺癌</div></div><div class="tl-item"><div class="tl-year">2026</div><div class="tl-text">去世，享年 60 岁</div></div>';
    } else if (isA) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1996</div><div class="tl-text">创立 Akre Capital Management</div></div><div class="tl-item"><div class="tl-year">1997</div><div class="tl-text">开始管理 FBR Focus Fund</div></div><div class="tl-item"><div class="tl-year">2000</div><div class="tl-text">互联网泡沫中坚持价值投资</div></div><div class="tl-item"><div class="tl-year">2009</div><div class="tl-text">重组 Akre Capital，推出 Akre Focus Fund</div></div><div class="tl-item"><div class="tl-year">2021</div><div class="tl-text">管理资产规模突破 150 亿美元</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">集中持有约 20 只高质量复利企业</div></div>';
    } else if (isG) {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1984</div><div class="tl-text">加入 Chieftain Capital，师从 John Shapiro</div></div><div class="tl-item"><div class="tl-year">1990</div><div class="tl-text">成为 Chieftain 合伙人</div></div><div class="tl-item"><div class="tl-year">2000</div><div class="tl-text">互联网泡沫中坚持价值投资</div></div><div class="tl-item"><div class="tl-year">2009</div><div class="tl-text">金融危机中逆势大举买入</div></div><div class="tl-item"><div class="tl-year">2010</div><div class="tl-text">创立 Brave Warrior Advisors</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">管理约 40 亿美元，集中于高质量企业</div></div>';
    } else {
      tl.innerHTML = '<div class="tl-item"><div class="tl-year">1966</div><div class="tl-text">出生于唐山，十岁时亲历唐山大地震</div></div><div class="tl-item"><div class="tl-year">1985</div><div class="tl-text">考入南京大学</div></div><div class="tl-item"><div class="tl-year">1989</div><div class="tl-text">赴美，入读哥伦比亚大学</div></div><div class="tl-item"><div class="tl-year">1996</div><div class="tl-text">哥大 BA/JD/MBA 三学位</div></div><div class="tl-item"><div class="tl-year">1997</div><div class="tl-text">创立喜马拉雅资本</div></div><div class="tl-item"><div class="tl-year">2002</div><div class="tl-text">向芒格推荐比亚迪</div></div><div class="tl-item"><div class="tl-year">至今</div><div class="tl-text">持续管理喜马拉雅资本</div></div>';
    }
  }
  // Philosophy
  var pg = document.querySelector('.phil-grid');
  if (pg) {
    if (isP) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfb2</div><h4>Heads I Win, Tails I Don\u2019t Lose Much</h4><p>Core Dhandho principle \u2014 asymmetric bets with limited downside.</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>Buy $1 for 50 Cents</h4><p>Purchase well below intrinsic value. Distressed turnarounds are the favorite hunting ground.</p></div><div class="phil-card"><div class="icon">\ud83d\udccb</div><h4>Checklist Investing</h4><p>Rigorous pre-investment checklists to avoid cognitive biases.</p></div><div class="phil-card"><div class="icon">\ud83d\udc11</div><h4>Clone the Best</h4><p>Copy the best ideas of top investors. Cloning is a wonderful strategy.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Ultra-Concentrated</h4><p>3-5 stocks. Diversification is protection against ignorance.</p></div><div class="phil-card"><div class="icon">\u2615</div><h4>Patience</h4><p>Do nothing most of the time. Only swing in your sweet spot.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfb2</div><h4>正面我赢，反面我也输不了多少</h4><p>Dhandho 核心\u2014\u2014寻找高度不对称的赌注。</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>50 美分买 1 美元</h4><p>买入显著低于内在价值的股票。困境反转是最爱的狩猎场。</p></div><div class="phil-card"><div class="icon">\ud83d\udccb</div><h4>清单投资法</h4><p>受 Atul Gawande 启发，严格的买入前检查清单。</p></div><div class="phil-card"><div class="icon">\ud83d\udc11</div><h4>克隆大师</h4><p>不羞于复制顶级投资者的最佳想法。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>极度集中</h4><p>通常 3-5 只股票，偶尔只持有一只。</p></div><div class="phil-card"><div class="icon">\u2615</div><h4>耐心等待</h4><p>大部分时间什么都不做，只在最佳击球区挥棒。</p></div>';
    } else if (isD) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>Buy Companies, Not Stocks</h4><p>"Buying stocks is buying companies" \u2014 evaluate businesses as if buying the whole company.</p></div><div class="phil-card"><div class="icon">\ud83d\udeab</div><h4>Three Don\u2019ts</h4><p>Don\u2019t short, don\u2019t use margin, don\u2019t invest in what you don\u2019t understand (\u4e0d\u505a\u7a7a\uff0c\u4e0d\u501f\u94b1\uff0c\u4e0d\u61c2\u4e0d\u505a).</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long-Term Concentration</h4><p>Heavy AAPL position since 2011. Concentrated bets on deeply understood businesses.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Circle of Competence</h4><p>Only invest in businesses you truly understand. Consumer tech and internet are sweet spots.</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>Business First</h4><p>Focus on business model, competitive moat, and management quality before price.</p></div><div class="phil-card"><div class="icon">\ud83d\udca1</div><h4>Learn from the Best</h4><p>Follow Buffett\u2019s and Munger\u2019s principles. Met Buffett at the 2006 charity lunch.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>买股票就是买公司</h4><p>把股票当作整家公司来评估，看生意本质而非报价波动。</p></div><div class="phil-card"><div class="icon">\ud83d\udeab</div><h4>三不原则</h4><p>不做空，不借钱，不懂不做\u2014\u2014坚守能力圈，拒绝诱惑。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期集中</h4><p>2011 年起重仓苹果，对理解深刻的企业下重注。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>能力圈</h4><p>只投真正理解的生意。消费电子和互联网是舒适区。</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>生意本质优先</h4><p>先看商业模式、护城河、管理层，再看价格。</p></div><div class="phil-card"><div class="icon">\ud83d\udca1</div><h4>师从巴菲特</h4><p>追随巴菲特和芒格的理念，2006 年亲历巴菲特慈善午餐。</p></div>';
    } else if (isT) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udf0d</div><h4>Macro Vision</h4><p>Top-down macro analysis guides portfolio positioning. Interest rates, economic cycles, and policy shifts drive decisions.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Concentrated Bets</h4><p>High conviction positions in a focused portfolio. When the thesis is strong, bet big.</p></div><div class="phil-card"><div class="icon">\ud83d\udd25</div><h4>Blood in the Streets</h4><p>The best opportunities come during crises. Distressed assets and panic selling are the hunting grounds.</p></div><div class="phil-card"><div class="icon">\u26a1</div><h4>Aggressive Trading</h4><p>Willing to reposition quickly when the macro picture changes. Not a buy-and-hold purist.</p></div><div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>Deep Due Diligence</h4><p>Intensive research on every position. Understand the business, the numbers, and the risks.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Risk Management</h4><p>Know when to cut losses. Position sizing and stop-losses protect the downside.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udf0d</div><h4>宏观视野</h4><p>自上而下的宏观分析指导仓位。利率、经济周期和政策转向是核心驱动。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>集中押注</h4><p>高确信度的集中持仓。当逻辑足够强，就下大注。</p></div><div class="phil-card"><div class="icon">\ud83d\udd25</div><h4>街头流血时买入</h4><p>最佳机会来自危机。困境资产和恐慌性抛售是狩猎场。</p></div><div class="phil-card"><div class="icon">\u26a1</div><h4>积极交易</h4><p>宏观形势变化时迅速调整仓位。不是纯粹的买入持有型投资者。</p></div><div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>深度尽调</h4><p>对每个仓位进行深入研究。了解生意、数据和风险。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>风险管理</h4><p>知道何时止损。仓位大小和止损线保护下行风险。</p></div>';
    } else if (isS) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83d\udcda</div><h4>Read the Masters</h4><p>Study Buffett, Munger, Graham deeply. Internalize their principles before developing your own style.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Concentrated Value</h4><p>5-10 positions maximum. Only invest when you have genuine edge and conviction.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long-Term Patience</h4><p>Hold great businesses for years. Let compounding work without interference.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Only buy at a significant discount to intrinsic value. Price is what you pay, value is what you get.</p></div><div class="phil-card"><div class="icon">\ud83d\udd2d</div><h4>Know Yourself</h4><p>Understand your own psychology and biases. Self-awareness is the hardest part of investing.</p></div><div class="phil-card"><div class="icon">\ud83d\udca1</div><h4>Learn by Doing</h4><p>Reading about investing is not enough. Real understanding comes from experience and mistakes.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83d\udcda</div><h4>阅读大师</h4><p>深入学习巴菲特、芒格、格雷厄姆。在形成自己的风格前先内化他们的原则。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>集中价值</h4><p>最多 5-10 个仓位。只在有真正优势和确信度时投资。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期耐心</h4><p>持有优秀企业多年。让复利发挥作用，不加干扰。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>只在显著低于内在价值时买入。价格是你付出的，价值是你得到的。</p></div><div class="phil-card"><div class="icon">\ud83d\udd2d</div><h4>认识自己</h4><p>了解自己的心理和偏见。自我认知是投资中最难的部分。</p></div><div class="phil-card"><div class="icon">\ud83d\udca1</div><h4>在实践中学习</h4><p>仅靠阅读是不够的。真正的理解来自经验和犯错。</p></div>';
    } else if (isB) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>Buy Wonderful Businesses</h4><p>Buy companies with durable competitive advantages at fair prices.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Never overpay. The difference between price and intrinsic value is your protection.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long-Term Horizon</h4><p>Our favorite holding period is forever. Let winners compound.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Circle of Competence</h4><p>Stay within what you understand.</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>Owner\'s Mindset</h4><p>Think like a business owner, not a stock trader.</p></div><div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>Read Everything</h4><p>Read 500 pages a day. Knowledge builds like compound interest.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>买入优秀企业</h4><p>以合理价格买入具有持久竞争优势的企业。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>永远不要多付。价格与内在价值的差距是你的保护。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期持有</h4><p>我们最喜欢的持有期限是永远。让赢家持续复利。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>能力圈</h4><p>留在你理解的范围内。</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>企业主思维</h4><p>像企业主一样思考，而非股票交易员。</p></div><div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>大量阅读</h4><p>每天读 500 页。知识像复利一样积累。</p></div>';
    } else if (isW) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>Forensic Research</h4><p>Deep-dive into financial statements. Uncover issues management won\'t show you.</p></div><div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>Read Every Word</h4><p>Read filings line by line. Cross-reference related-party transactions.</p></div><div class="phil-card"><div class="icon">\u2600\ufe0f</div><h4>Sunlight as Disinfectant</h4><p>Transparency is the ultimate remedy for corporate misgovernance.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Minority Shareholder Rights</h4><p>Fight for the small investor.</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>Small-Cap Value</h4><p>Undervalued, overlooked HK small-caps are the hunting ground.</p></div><div class="phil-card"><div class="icon">\ud83d\udce1</div><h4>Open Research</h4><p>Share findings publicly. Knowledge is most powerful when it\'s free.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>法证式研究</h4><p>深入财务报表，发掘管理层不愿让你看到的问题。</p></div><div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>逐字细读</h4><p>逐行阅读申报文件，交叉比对关联交易。</p></div><div class="phil-card"><div class="icon">\u2600\ufe0f</div><h4>阳光是最好的消毒剂</h4><p>透明度是公司治理不善的终极解药。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>捍卫小股东</h4><p>为小投资者争取权益。</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>小盘价值投资</h4><p>被低估、被忽视的港股小型股是狩猎场。</p></div><div class="phil-card"><div class="icon">\ud83d\udce1</div><h4>公开研究</h4><p>公开分享研究成果。知识自由流通时最有力量。</p></div>';
    } else if (isA) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83e\ude91</div><h4>Three-Legged Stool</h4><p>Extraordinary business + excellent management + reinvestment.</p></div><div class="phil-card"><div class="icon">\u2699\ufe0f</div><h4>Compounding Machines</h4><p>Find businesses that reinvest at high rates of return.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Concentration</h4><p>~20 stocks only. Deep research over diversification.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long Holding Periods</h4><p>Minimal turnover. Let compounding do the work.</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>High ROE Focus</h4><p>Prefers ROE >20% with low capex needs.</p></div><div class="phil-card"><div class="icon">\ud83d\udcbc</div><h4>Management First</h4><p>Honest, capable, skilled capital allocators.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83e\ude91</div><h4>三条腿的凳子</h4><p>卓越商业模式 + 优秀管理层 + 再投资机会。</p></div><div class="phil-card"><div class="icon">\u2699\ufe0f</div><h4>复利机器</h4><p>寻找能持续以高回报率再投资利润的企业。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>集中投资</h4><p>仅持有约 20 只股票，深度研究而非广泛分散。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期持有</h4><p>年换手率极低，让复利充分发挥作用。</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>高 ROE</h4><p>偏好 ROE 持续高于 20% 且无需大量资本支出。</p></div><div class="phil-card"><div class="icon">\ud83d\udcbc</div><h4>管理层至上</h4><p>诚实、能干、善于资本配置的管理层。</p></div>';
    } else if (isG) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Extreme Concentration</h4><p>Only 8-12 stocks. Deep research on each.</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>High ROIC</h4><p>Prefers ROIC >15% and strong cash flow.</p></div><div class="phil-card"><div class="icon">\ud83c\udff0</div><h4>Strong Moats</h4><p>Durable competitive advantages and pricing power.</p></div><div class="phil-card"><div class="icon">\ud83d\udc54</div><h4>Excellent Management</h4><p>Honest, capable, shareholder-aligned.</p></div><div class="phil-card"><div class="icon">\u26a1</div><h4>Contrarian Buying</h4><p>Buy aggressively during panics.</p></div><div class="phil-card"><div class="icon">\ud83d\udcc5</div><h4>Long-Term Hold</h4><p>Minimal turnover. Let quality businesses compound.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>极度集中</h4><p>仅持有 8-12 只股票。</p></div><div class="phil-card"><div class="icon">\ud83d\udcc8</div><h4>高 ROIC</h4><p>偏好 ROIC 持续高于 15%的企业。</p></div><div class="phil-card"><div class="icon">\ud83c\udff0</div><h4>强护城河</h4><p>寻找具有持久竞争优势和定价权的企业。</p></div><div class="phil-card"><div class="icon">\ud83d\udc54</div><h4>优秀管理层</h4><p>管理层必须诚实、能干、以股东利益为重。</p></div><div class="phil-card"><div class="icon">\u26a1</div><h4>逆向买入</h4><p>在市场恐慌时敢于大举买入。</p></div><div class="phil-card"><div class="icon">\ud83d\udcc5</div><h4>长期持有</h4><p>年换手率极低，让优质企业持续创造价值。</p></div>';
    } else {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>Deep Research</h4><p>Thorough due diligence on financials, industry dynamics, and competitive positioning.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Concentrated Portfolio</h4><p>Capital in a few high-conviction investments.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long-Term View</h4><p>Holding for decades, letting compounding work.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Buying well below intrinsic value.</p></div><div class="phil-card"><div class="icon">\ud83d\udd2d</div><h4>Circle of Competence</h4><p>Invest only where you have a genuine edge.</p></div><div class="phil-card"><div class="icon">\ud83c\udfa3</div><h4>Fish Where the Fish Are</h4><p>Focus where you can catch fish.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83d\udcd6</div><h4>深度研究</h4><p>财务报表、行业动态、竞争地位。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>集中持仓</h4><p>资金集中在少数高确信度投资上。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期视角</h4><p>以十年为周期持有，让复利充分发挥。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>以显著低于内在价值的价格买入。</p></div><div class="phil-card"><div class="icon">\ud83d\udd2d</div><h4>能力圈</h4><p>清楚知道自己理解什么、不理解什么。</p></div><div class="phil-card"><div class="icon">\ud83c\udfa3</div><h4>在对的地方钓鱼</h4><p>找到自己能钓到鱼的水域。</p></div>';
    }
  }
  // Readings
  var rg = document.querySelector('.articles-grid');
  if (rg) {
    if (isP) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.chaiwithpabrai.com" target="_blank"><div class="year">Blog</div><h4>Chai with Pabrai</h4><p>Investment thoughts & portfolio updates.</p></a><a class="article-card" href="https://www.amazon.com/Dhandho-Investor-Low-Risk-Method-Returns/dp/047004389X" target="_blank"><div class="year">2007</div><h4>The Dhandho Investor</h4><p>Low-risk, high-return framework.</p></a><a class="article-card" href="https://www.youtube.com/@mohnishpabrai" target="_blank"><div class="year">YouTube</div><h4>Video Channel</h4><p>Speeches, interviews, annual meetings.</p></a><a class="article-card" href="https://www.dakshana.org/" target="_blank"><div class="year">Charity</div><h4>Dakshana Foundation</h4><p>Helping underprivileged students in India.</p></a><a class="article-card" href="https://www.forbes.com/sites/investor-hub/2024/11/01/the-unconventional-fund-from-an-investing-legend-poised-to-outperform/" target="_blank"><div class="year">2024 Forbes</div><h4>Forbes Profile</h4><p>An unconventional fund legend.</p></a><a class="article-card" href="https://open.spotify.com/show/7LX2ps7irNRtxj8I12jFSq" target="_blank"><div class="year">Podcast</div><h4>Chai with Pabrai</h4><p>Full podcast on Spotify.</p></a>'
        : '<a class="article-card" href="https://www.chaiwithpabrai.com" target="_blank"><div class="year">Blog</div><h4>Chai with Pabrai</h4><p>Pabrai 个人博客，投资思考与组合更新。</p></a><a class="article-card" href="https://www.amazon.com/Dhandho-Investor-Low-Risk-Method-Returns/dp/047004389X" target="_blank"><div class="year">2007</div><h4>The Dhandho Investor</h4><p>Pabrai 经典著作。</p></a><a class="article-card" href="https://www.youtube.com/@mohnishpabrai" target="_blank"><div class="year">YouTube</div><h4>视频频道</h4><p>演讲、访谈合集。</p></a><a class="article-card" href="https://www.dakshana.org/" target="_blank"><div class="year">慈善</div><h4>Dakshana Foundation</h4><p>Pabrai 公益组织。</p></a><a class="article-card" href="https://www.forbes.com/sites/investor-hub/2024/11/01/the-unconventional-fund-from-an-investing-legend-poised-to-outperform/" target="_blank"><div class="year">2024 Forbes</div><h4>Forbes 深度报道</h4><p>非传统基金传奇。</p></a><a class="article-card" href="https://open.spotify.com/show/7LX2ps7irNRtxj8I12jFSq" target="_blank"><div class="year">Podcast</div><h4>Chai with Pabrai 播客</h4><p>Spotify 全集。</p></a>';
    } else if (isD) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://xueqiu.com/P/ZH2256330" target="_blank"><div class="year">Xueqiu</div><h4>\u5927\u9053\u65e0\u5f62\u6211\u6709\u578b</h4><p>Duan\u2019s Xueqiu portfolio & investment thoughts.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001759760&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings (H&H)</h4><p>View H&H International Investment SEC submissions.</p></a><a class="article-card" href="https://www.gelonghui.com/p/2363835" target="_blank"><div class="year">Article</div><h4>\u6bb5\u6c38\u5e73\uff1a\u6295\u8d44\u5c31\u662f\u4e70\u516c\u53f8</h4><p>"Buying stocks is buying companies" \u2014 core philosophy explained.</p></a><a class="article-card" href="https://www.chinaventure.com.cn/" target="_blank"><div class="year">Interview</div><h4>\u6bb5\u6c38\u5e73\u6295\u8d44\u8bbf\u8c08</h4><p>Interviews on value investing philosophy.</p></a><a class="article-card" href="https://www.huxiu.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">Huxiu</div><h4>\u864e\u55c5 \u00b7 \u6bb5\u6c38\u5e73</h4><p>News and analysis about Duan Yongping.</p></a><a class="article-card" href="https://www.36kr.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">36Kr</div><h4>36\u6c10 \u00b7 \u6bb5\u6c38\u5e73</h4><p>Business coverage of Duan Yongping and BBK ecosystem.</p></a>'
        : '<a class="article-card" href="https://xueqiu.com/P/ZH2256330" target="_blank"><div class="year">\u96ea\u7403</div><h4>\u5927\u9053\u65e0\u5f62\u6211\u6709\u578b</h4><p>\u6bb5\u6c38\u5e73\u5728\u96ea\u7403\u7684\u6295\u8d44\u7ec4\u5408\u4e0e\u601d\u8003\u3002</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001759760&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>\u5168\u90e8 13F \u539f\u59cb\u6587\u4ef6</h4><p>\u5728 SEC \u6570\u636e\u5e93\u67e5\u770b H&H International \u5168\u90e8\u63d0\u4ea4\u3002</p></a><a class="article-card" href="https://www.gelonghui.com/p/2363835" target="_blank"><div class="year">\u6587\u7ae0</div><h4>\u6bb5\u6c38\u5e73\uff1a\u6295\u8d44\u5c31\u662f\u4e70\u516c\u53f8</h4><p>"\u4e70\u80a1\u7968\u5c31\u662f\u4e70\u516c\u53f8"\u2014\u2014\u6838\u5fc3\u6295\u8d44\u7406\u5ff5\u89e3\u8bfb\u3002</p></a><a class="article-card" href="https://www.chinaventure.com.cn/" target="_blank"><div class="year">\u8bbf\u8c08</div><h4>\u6bb5\u6c38\u5e73\u6295\u8d44\u8bbf\u8c08</h4><p>\u6bb5\u6c38\u5e73\u4ef7\u503c\u6295\u8d44\u7406\u5ff5\u76f8\u5173\u8bbf\u8c08\u3002</p></a><a class="article-card" href="https://www.huxiu.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">\u864e\u55c5</div><h4>\u864e\u55c5 \u00b7 \u6bb5\u6c38\u5e73</h4><p>\u6bb5\u6c38\u5e73\u76f8\u5173\u65b0\u95fb\u4e0e\u5206\u6790\u3002</p></a><a class="article-card" href="https://www.36kr.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">36\u6c10</div><h4>36\u6c10 \u00b7 \u6bb5\u6c38\u5e73</h4><p>\u6bb5\u6c38\u5e73\u53ca\u6b65\u6b65\u9ad8\u7cfb\u5546\u4e1a\u62a5\u9053\u3002</p></a>';
    } else if (isT) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001656456&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings (Appaloosa)</h4><p>View Appaloosa LP SEC submissions.</p></a><a class="article-card" href="https://www.forbes.com/profile/david-tepper/" target="_blank"><div class="year">Forbes</div><h4>Forbes Profile</h4><p>David Tepper billionaire profile and net worth.</p></a><a class="article-card" href="https://www.institutionalinvestor.com/article/2b955b08k01252" target="_blank"><div class="year">Institutional Investor</div><h4>Tepper\u2019s Greatest Trades</h4><p>Analysis of his most successful macro bets.</p></a><a class="article-card" href="https://www.bloomberg.com/news/articles/2023-05-25/david-tepper-appaloosa-says-he-s-fully-invested-in-stocks" target="_blank"><div class="year">Bloomberg</div><h4>Tepper: "I\u2019m Fully Invested"</h4><p>Interview on market outlook and portfolio strategy.</p></a><a class="article-card" href="https://www.cnbc.com/" target="_blank"><div class="year">CNBC</div><h4>CNBC Coverage</h4><p>Latest news and interviews about David Tepper.</p></a><a class="article-card" href="https://www.businessinsider.com/personal-finance/david-tepper" target="_blank"><div class="year">Business Insider</div><h4>Tepper Archive</h4><p>Collection of articles and analysis.</p></a>'
        : '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001656456&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Appaloosa LP 全部提交。</p></a><a class="article-card" href="https://www.forbes.com/profile/david-tepper/" target="_blank"><div class="year">Forbes</div><h4>Forbes 富豪档案</h4><p>大卫·泰珀个人简介与净资产。</p></a><a class="article-card" href="https://www.institutionalinvestor.com/article/2b955b08k01252" target="_blank"><div class="year">Institutional Investor</div><h4>泰珀的经典交易</h4><p>分析他最成功的宏观押注。</p></a><a class="article-card" href="https://www.bloomberg.com/news/articles/2023-05-25/david-tepper-appaloosa-says-he-s-fully-invested-in-stocks" target="_blank"><div class="year">Bloomberg</div><h4>泰珀："我全仓了"</h4><p>市场前景与组合策略访谈。</p></a><a class="article-card" href="https://www.cnbc.com/" target="_blank"><div class="year">CNBC</div><h4>CNBC 报道</h4><p>大卫·泰珀最新新闻与访谈。</p></a><a class="article-card" href="https://www.businessinsider.com/personal-finance/david-tepper" target="_blank"><div class="year">Business Insider</div><h4>泰珀文章集</h4><p>相关文章与分析合集。</p></a>';
    } else if (isS) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.amazon.com/Education-Value-Investor-Transformative/dp/1137278943" target="_blank"><div class="year">2014 Book</div><h4>The Education of a Value Investor</h4><p>Spier\u2019s memoir and investment philosophy.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001404599&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings (Aquamarine)</h4><p>View Aquamarine Capital SEC submissions.</p></a><a class="article-card" href="https://aquamarinefund.com/" target="_blank"><div class="year">Official</div><h4>Aquamarine Fund</h4><p>Official fund website.</p></a><a class="article-card" href="https://www.chaiwithpabrai.com/" target="_blank"><div class="year">Chai with Pabrai</div><h4>Buffett Lunch Story</h4><p>The story of the charity lunch with Buffett and Pabrai.</p></a><a class="article-card" href="https://www.youtube.com/watch?v=8Jd6wMzG0cI" target="_blank"><div class="year">YouTube</div><h4>Spier Interviews</h4><p>Value investing discussions and insights.</p></a><a class="article-card" href="https://www.morningstar.com/" target="_blank"><div class="year">Morningstar</div><h4>Aquamarine Fund Analysis</h4><p>Fund performance and holdings analysis.</p></a>'
        : '<a class="article-card" href="https://www.amazon.com/Education-Value-Investor-Transformative/dp/1137278943" target="_blank"><div class="year">2014 书籍</div><h4>价值投资者的修炼</h4><p>斯皮尔的回忆录与投资理念。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001404599&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Aquamarine Capital 全部提交。</p></a><a class="article-card" href="https://aquamarinefund.com/" target="_blank"><div class="year">官网</div><h4>Aquamarine Fund</h4><p>基金官方网站。</p></a><a class="article-card" href="https://www.chaiwithpabrai.com/" target="_blank"><div class="year">Chai with Pabrai</div><h4>巴菲特午餐故事</h4><p>与帕伯莱合拍巴菲特午餐的故事。</p></a><a class="article-card" href="https://www.youtube.com/watch?v=8Jd6wMzG0cI" target="_blank"><div class="year">YouTube</div><h4>斯皮尔访谈</h4><p>价值投资讨论与见解。</p></a><a class="article-card" href="https://www.morningstar.com/" target="_blank"><div class="year">Morningstar</div><h4>Aquamarine 基金分析</h4><p>基金表现与持仓分析。</p></a>';
    } else if (isB) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.berkshirehathaway.com/letters/letters.html" target="_blank"><div class="year">Letters</div><h4>Shareholder Letters</h4><p>All Berkshire Hathaway annual letters by Buffett.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Berkshire Hathaway SEC submissions.</p></a><a class="article-card" href="https://www.berkshirehathaway.com/" target="_blank"><div class="year">Official</div><h4>berkshirehathaway.com</h4><p>Official BRK website, letters, and more.</p></a><a class="article-card" href="https://www.amazon.com/Snowball-Warren-Buffett-Business/dp/0553384846" target="_blank"><div class="year">Book</div><h4>The Snowball</h4><p>Alice Schroeder\'s authorized biography of Buffett.</p></a><a class="article-card" href="https://www.cnbc.com/warren-buffett/" target="_blank"><div class="year">CNBC</div><h4>CNBC Buffett Archive</h4><p>News, interviews, and market commentary.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=berkshire+hathaway+annual+meeting" target="_blank"><div class="year">YouTube</div><h4>Annual Meeting Videos</h4><p>Woodstock for Capitalists — full meeting recordings.</p></a>'
        : '<a class="article-card" href="https://www.berkshirehathaway.com/letters/letters.html" target="_blank"><div class="year">股东信</div><h4>年度股东信全集</h4><p>巴菲特亲笔撰写的所有伯克希尔年度信。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看伯克希尔全部提交。</p></a><a class="article-card" href="https://www.berkshirehathaway.com/" target="_blank"><div class="year">官网</div><h4>berkshirehathaway.com</h4><p>伯克希尔官网，股东信与公司信息。</p></a><a class="article-card" href="https://www.amazon.com/Snowball-Warren-Buffett-Business/dp/0553384846" target="_blank"><div class="year">书籍</div><h4>滚雪球</h4><p>艾丽斯·施罗德授权的巴菲特传记。</p></a><a class="article-card" href="https://www.cnbc.com/warren-buffett/" target="_blank"><div class="year">CNBC</div><h4>CNBC 巴菲特档案</h4><p>新闻、访谈与市场评论。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=berkshire+hathaway+annual+meeting" target="_blank"><div class="year">YouTube</div><h4>年度股东大会视频</h4><p>资本家的伍德斯托克——完整会议录像。</p></a>';
    } else if (isW) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://webb-site.com/" target="_blank"><div class="year">Official</div><h4>webb-site.com</h4><p>Webb\'s independent HK corporate governance platform.</p></a><a class="article-card" href="https://webb-site.com/database/" target="_blank"><div class="year">Database</div><h4>Webb-site Database</h4><p>Searchable database of HK-listed companies and directors.</p></a><a class="article-card" href="https://webb-site.com/articles/" target="_blank"><div class="year">Articles</div><h4>Enigma Network & Articles</h4><p>Webb\'s investigations and governance articles.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Webb_(investor)" target="_blank"><div class="year">Wikipedia</div><h4>David Webb</h4><p>Biography and career summary.</p></a><a class="article-card" href="https://www.reuters.com/" target="_blank"><div class="year">Reuters</div><h4>Reuters Coverage</h4><p>News about Webb\'s activism and passing.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=david+webb+hkex" target="_blank"><div class="year">YouTube</div><h4>Interviews & Talks</h4><p>Webb\'s public appearances and interviews.</p></a>'
        : '<a class="article-card" href="https://webb-site.com/" target="_blank"><div class="year">官网</div><h4>webb-site.com</h4><p>韦伯的独立港股企业管治平台。</p></a><a class="article-card" href="https://webb-site.com/database/" target="_blank"><div class="year">数据库</div><h4>Webb-site 数据库</h4><p>可搜索的港股公司和董事数据库。</p></a><a class="article-card" href="https://webb-site.com/articles/" target="_blank"><div class="year">文章</div><h4>谜网与文章合集</h4><p>韦伯的调查报道与管治分析文章。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Webb_(investor)" target="_blank"><div class="year">维基百科</div><h4>David Webb</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://www.reuters.com/" target="_blank"><div class="year">路透社</div><h4>路透社报道</h4><p>关于韦伯维权活动与逝世的新闻。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=david+webb+hkex" target="_blank"><div class="year">YouTube</div><h4>访谈与演讲</h4><p>韦伯的公开露面与访谈录像。</p></a>';
    } else if (isA) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.akrecapital.com/" target="_blank"><div class="year">Official</div><h4>akrecapital.com</h4><p>Official Akre Capital Management website.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001499406&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Akre Capital SEC submissions.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=chuck+akre+interview" target="_blank"><div class="year">YouTube</div><h4>Akre Interviews</h4><p>Chuck Akre on compounding machines and the three-legged stool.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Chuck_Akre" target="_blank"><div class="year">Wikipedia</div><h4>Chuck Akre</h4><p>Biography and career.</p></a><a class="article-card" href="https://www.validea.com/" target="_blank"><div class="year">Validea</div><h4>Three-Legged Stool</h4><p>Validea\'s analysis of the Akre framework.</p></a><a class="article-card" href="https://www.gurufocus.com/investor/chuck-akre" target="_blank"><div class="year">GuruFocus</div><h4>Akre Portfolio</h4><p>Current holdings and performance tracking.</p></a>'
        : '<a class="article-card" href="https://www.akrecapital.com/" target="_blank"><div class="year">官网</div><h4>akrecapital.com</h4><p>Akre Capital Management 官方网站。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001499406&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Akre Capital 全部提交。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=chuck+akre+interview" target="_blank"><div class="year">YouTube</div><h4>阿克雷访谈</h4><p>查克·阿克雷谈复利机器与三条腿的凳子。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Chuck_Akre" target="_blank"><div class="year">维基百科</div><h4>Chuck Akre</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://www.validea.com/" target="_blank"><div class="year">Validea</div><h4>三条腿的凳子</h4><p>Validea 对阿克雷投资框架的分析。</p></a><a class="article-card" href="https://www.gurufocus.com/investor/chuck-akre" target="_blank"><div class="year">GuruFocus</div><h4>阿克雷持仓</h4><p>当前持仓与表现追踪。</p></a>';
    } else if (isG) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.bravewarrior.com/" target="_blank"><div class="year">Official</div><h4>bravewarrior.com</h4><p>Official Brave Warrior Advisors website.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001495196&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Brave Warrior Advisors SEC submissions.</p></a><a class="article-card" href="https://www.gurufocus.com/investor/glenn-greenberg" target="_blank"><div class="year">GuruFocus</div><h4>Greenberg Profile</h4><p>Holdings history and performance analysis.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=glenn+greenberg+investor" target="_blank"><div class="year">YouTube</div><h4>Greenberg Interviews</h4><p>Glenn Greenberg on concentrated value investing.</p></a><a class="article-card" href="https://www.dataroma.com/m/home.php?g=gg" target="_blank"><div class="year">Dataroma</div><h4>Portfolio Tracker</h4><p>Brave Warrior 13F portfolio tracking.</p></a><a class="article-card" href="https://www.gurufocus.com/portfolio/brave-warrior-advisors" target="_blank"><div class="year">GuruFocus</div><h4>Current Portfolio</h4><p>Latest Brave Warrior holdings and allocation.</p></a>'
        : '<a class="article-card" href="https://www.bravewarrior.com/" target="_blank"><div class="year">官网</div><h4>bravewarrior.com</h4><p>Brave Warrior Advisors 官方网站。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001495196&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Brave Warrior 全部提交。</p></a><a class="article-card" href="https://www.gurufocus.com/investor/glenn-greenberg" target="_blank"><div class="year">GuruFocus</div><h4>格林伯格档案</h4><p>持仓历史与表现分析。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=glenn+greenberg+investor" target="_blank"><div class="year">YouTube</div><h4>格林伯格访谈</h4><p>格伦·格林伯格谈集中价值投资。</p></a><a class="article-card" href="https://www.dataroma.com/m/home.php?g=gg" target="_blank"><div class="year">Dataroma</div><h4>组合追踪</h4><p>Brave Warrior 13F 组合追踪。</p></a><a class="article-card" href="https://www.gurufocus.com/portfolio/brave-warrior-advisors" target="_blank"><div class="year">GuruFocus</div><h4>当前持仓</h4><p>最新 Brave Warrior 持仓与配置。</p></a>';
    } else {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://cdn.prod.website-files.com/5ef3c7300432b40ed865991a/67a4f75703627bd3a927077e_Global%20Value%20Investing%20in%20Our%20Era%20(2024-12-07).pdf" target="_blank"><div class="year">2024 PDF</div><h4>Global Value Investing in Our Era</h4><p>Peking University lecture on six core principles.</p></a><a class="article-card" href="https://acquirersmultiple.com/2025/04/li-lu-how-to-invest-during-turbulent-times/" target="_blank"><div class="year">2025</div><h4>How to Invest in Turbulent Times</h4><p>Macro vs micro, essence of wealth.</p></a><a class="article-card" href="https://roiss.substack.com/p/transcript-of-li-lu-and-bruce-greenwald" target="_blank"><div class="year">2021</div><h4>On Value Investing in China</h4><p>Conversation with Prof. Bruce Greenwald.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001709323&type=13F" target="_blank"><div class="year">SEC</div><h4>All 13F Filings</h4><p>View original SEC submissions.</p></a><a class="article-card" href="https://www.himcap.com/" target="_blank"><div class="year">Official</div><h4>Himalaya Capital</h4><p>Official website of the firm.</p></a><a class="article-card" href="https://monkeyenroute.medium.com/book-review-civilization-modernization-value-investing-china-by-li-lu-22398102583c" target="_blank"><div class="year">Book</div><h4>Civilization & Investment</h4><p>Book review: Civilization, Modernization and China.</p></a>'
        : '<a class="article-card" href="https://cdn.prod.website-files.com/5ef3c7300432b40ed865991a/67a4f75703627bd3a927077e_Global%20Value%20Investing%20in%20Our%20Era%20(2024-12-07).pdf" target="_blank"><div class="year">2024 \u00b7 PDF</div><h4>\u6211\u4eec\u65f6\u4ee3\u7684\u5168\u7403\u4ef7\u503c\u6295\u8d44</h4><p>\u5317\u5927\u4e3b\u9898\u6f14\u8bb2\uff0c\u4ef7\u503c\u6295\u8d44\u516d\u5927\u6838\u5fc3\u539f\u5219\u3002</p></a><a class="article-card" href="https://acquirersmultiple.com/2025/04/li-lu-how-to-invest-during-turbulent-times/" target="_blank"><div class="year">2025 \u00b7 04</div><h4>\u52a8\u8361\u65f6\u671f\u5982\u4f55\u6295\u8d44</h4><p>\u5b8f\u89c2\u4e0e\u5fae\u89c2\u7684\u5e73\u8861\u3001\u8d22\u5bcc\u7684\u672c\u8d28\u3002</p></a><a class="article-card" href="https://roiss.substack.com/p/transcript-of-li-lu-and-bruce-greenwald" target="_blank"><div class="year">2021 \u00b7 04</div><h4>\u5bf9\u8bdd\u683c\u6797\u6c83\u5c14\u5fb7</h4><p>\u4e0e\u54e5\u5927\u4ef7\u503c\u6295\u8d44\u6743\u5a01\u7684\u5bf9\u8bdd\u5b9e\u5f55\u3002</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001709323&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>\u5168\u90e8 13F \u539f\u59cb\u6587\u4ef6</h4><p>\u5728 SEC \u6570\u636e\u5e93\u67e5\u770b\u6240\u6709 13F\u3002</p></a><a class="article-card" href="https://www.himcap.com/" target="_blank"><div class="year">\u5b98\u7f51</div><h4>Himalaya Capital</h4><p>\u4e86\u89e3\u66f4\u591a\u6295\u8d44\u7406\u5ff5\u3002</p></a><a class="article-card" href="https://monkeyenroute.medium.com/book-review-civilization-modernization-value-investing-china-by-li-lu-22398102583c" target="_blank"><div class="year">\u4e66\u8bc4</div><h4>\u6587\u660e\u3001\u73b0\u4ee3\u5316\u4e0e\u6295\u8d44</h4><p>\u300a\u6587\u660e\u3001\u73b0\u4ee3\u5316\u4e0e\u4e2d\u56fd\u300b\u4e66\u8bc4\u3002</p></a>';
    }
  }
}

// ========== AUTO-INIT ==========
// Safety shim: old cached pages may still call renderAll()
function renderAll() { try { renderSummary(); renderHoldings(); renderInsights(); renderHistoryChart(); } catch(e) {} }
// 页面加载完成后自动初始化
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => switchInvestor('lilu'));
} else {
  switchInvestor('lilu');
}
