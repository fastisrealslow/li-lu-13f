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
    renderAll(); renderHoldings(); renderHistoryChart(); renderTimeline();
    updateInvestorContent();
  renderTimeline();
  } catch(e) { 
    console.warn('switchInvestor error:', e);
    // Show non-blocking toast instead of white screen
    const toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);background:#dc2626;color:#fff;padding:10px 20px;border-radius:8px;font-size:.85rem;z-index:9999;';
    toast.textContent = '数据加载失败，请稍后重试';
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
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
  renderAll();
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
    document.getElementById('priceUpdate').textContent =
      prices.updatedAt ? new Date(prices.updatedAt).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'})
      : prices.updated ? new Date(prices.updated).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'}) : '待更新';
  } catch(e) {
    console.log('prices unavailable:', file);
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
async function renderSpinoff() {
  const el = document.getElementById('spinoffContent');
  if (!el) return;
  if (_spinoffCache) { el.innerHTML = _spinoffCache; return; }
  el.innerHTML = '<p style="padding:16px;color:var(--text-lighter);">加载中…</p>';
  const isEn = lang === 'en';

  try {
    const resp = await fetch('spinoff.json?t=' + Date.now());
    const data = await resp.json();
    const companies = data.companies || [];

    if (!companies.length) {
      el.innerHTML = `<div style="padding:32px;text-align:center;color:var(--text-lighter);">📭 ${isEn?'No data':'暂无数据'}</div>`;
      _spinoffCache = el.innerHTML; return;
    }

    // 日期格式化 YYYYMMDD → YYYY-MM-DD
    const fd = s => s && s.length===8 ? s.slice(0,4)+'-'+s.slice(4,6)+'-'+s.slice(6,8) : (s||'');

    // 分拆进度识别（根据最新公告标题关键词）
    const progressOf = (ann) => {
      if (!ann || !ann.length) return {label:'', color:'#9ca3af', pct:0};
      const t = (ann[0].title||'').toLowerCase();
      if (/上市|ipo|刊發招股|開始買賣|開始交易|listed/.test(t))
        return {label: isEn?'Listed':'已上市',   color:'#059669', pct:100};
      if (/批準|批准|approved|接纳/.test(t))
        return {label: isEn?'Approved':'已批准', color:'#2563eb', pct:75};
      if (/進展|进展|update|最新情況|progress/.test(t))
        return {label: isEn?'In progress':'进行中', color:'#d97706', pct:50};
      if (/終止|终止|撤回|withdraw|cancel/.test(t))
        return {label: isEn?'Cancelled':'已终止', color:'#dc2626', pct:0};
      if (/建議|建议|propose|擬/.test(t))
        return {label: isEn?'Proposed':'初步建议', color:'#7c3aed', pct:25};
      return {label: isEn?'Announced':'已公告', color:'#6b7280', pct:10};
    };

    let html = `
    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap;gap:8px;">
      <div>
        <span style="font-size:.95rem;font-weight:600;color:var(--navy);">
          ${isEn?'Spin-off Tracker':'分拆进展追踪'}
        </span>
        <span style="font-size:.75rem;color:var(--text-lighter);margin-left:10px;">
          ${companies.length} ${isEn?'companies':'家公司'} &nbsp;·&nbsp;
          ${fd(data.dateFrom)} ~ ${fd(data.dateTo)} &nbsp;·&nbsp;
          ${isEn?'Updated':'更新'} ${(data.updatedAt||'').slice(0,10)}
        </span>
      </div>
      <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
        <div style="display:flex;gap:6px;font-size:.68rem;">
          ${[
            ['#059669', isEn?'Listed':'已上市'],
            ['#2563eb', isEn?'Approved':'已批准'],
            ['#d97706', isEn?'In progress':'进行中'],
            ['#7c3aed', isEn?'Proposed':'建议中'],
            ['#dc2626', isEn?'Cancelled':'已终止'],
          ].map(([c,l])=>`<span style="display:flex;align-items:center;gap:3px;">
            <span style="width:8px;height:8px;border-radius:50%;background:${c};display:inline-block;"></span>${l}</span>`).join('')}
        </div>
      </div>
    </div>

    <!-- 表头 -->
    <div style="display:grid;grid-template-columns:110px 100px 1fr 110px 80px 60px;gap:8px;
                padding:6px 14px;background:#0c1e3a;border-radius:8px 8px 0 0;
                font-size:.67rem;font-weight:600;color:rgba(255,255,255,.6);letter-spacing:.5px;text-transform:uppercase;">
      <span>${isEn?'Ticker':'代码'}</span>
      <span>${isEn?'Status':'进度'}</span>
      <span>${isEn?'Latest Announcement':'最新公告'}</span>
      <span>${isEn?'Latest Date':'最新日期'}</span>
      <span style="text-align:center;">${isEn?'Filings':'公告数'}</span>
      <span></span>
    </div>

    <!-- 数据行 -->
    <div id="spinoffList" style="border:1px solid #e5e0d8;border-top:none;border-radius:0 0 8px 8px;overflow:hidden;">`;

    companies.forEach((c, idx) => {
      const ann  = c.announcements || [];
      const prog = progressOf(ann);
      const latest = ann[0] || {};
      const latestTitle = (latest.title||'').slice(0,55) + ((latest.title||'').length>55?'…':'');

      // 进度条（小）
      const progressBar = `
        <div style="display:flex;align-items:center;gap:5px;">
          <div style="width:60px;height:5px;background:#e5e7eb;border-radius:3px;overflow:hidden;flex-shrink:0;">
            <div style="width:${prog.pct}%;height:100%;background:${prog.color};border-radius:3px;transition:width .3s;"></div>
          </div>
          <span style="font-size:.67rem;color:${prog.color};font-weight:600;white-space:nowrap;">${prog.label}</span>
        </div>`;

      // 公告数 dots
      const dotCount = Math.min(ann.length, 12);
      const dots = Array.from({length:dotCount}, (_,i)=>`
        <div style="width:6px;height:6px;border-radius:50%;background:${prog.color};opacity:${1-i*0.06};flex-shrink:0;"></div>`
      ).join('');

      html += `
      <!-- 主行 -->
      <div onclick="spinoffToggle(${idx})" style="
            display:grid;grid-template-columns:110px 100px 1fr 110px 80px 60px;gap:8px;
            padding:10px 14px;cursor:pointer;
            background:${idx%2===0?'#fff':'#faf9f7'};
            border-bottom:1px solid #f0ece4;
            transition:background .12s;align-items:center;"
           onmouseover="this.style.background='#f5f0e8'"
           onmouseout="this.style.background='${idx%2===0?'#fff':'#faf9f7'}'">
        <!-- ticker + name -->
        <div>
          <div style="font-weight:700;font-size:.82rem;color:var(--navy);">${fmtTicker(c.ticker)}</div>
          <div style="font-size:.68rem;color:var(--text-lighter);margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${c.stockName}</div>
        </div>
        <!-- 进度 -->
        <div>${progressBar}</div>
        <!-- 最新标题 -->
        <div style="font-size:.78rem;color:var(--text);line-height:1.4;overflow:hidden;">
          ${latest.docUrl
            ? `<a href="${latest.docUrl}" target="_blank" rel="noopener"
                  onclick="event.stopPropagation()"
                  style="color:var(--navy);text-decoration:none;"
                  title="${(latest.title||'')}">
                  ${latestTitle}
               </a>`
            : latestTitle}
        </div>
        <!-- 最新日期 -->
        <div style="font-size:.75rem;color:var(--text-light);white-space:nowrap;">${c.latestDate}</div>
        <!-- 公告数 dots -->
        <div style="display:flex;flex-wrap:wrap;gap:2px;align-items:center;">
          ${dots}
          ${ann.length>12?`<span style="font-size:.6rem;color:var(--text-lighter);">+${ann.length-12}</span>`:''}
        </div>
        <!-- 展开箭头 -->
        <div style="text-align:center;font-size:.7rem;color:var(--gold);" id="so-arrow-${idx}">▶</div>
      </div>

      <!-- 展开的时间线 -->
      <div id="so-body-${idx}" style="display:none;background:#f8f6f0;border-bottom:1px solid #e5e0d8;">
        <div style="padding:6px 14px 4px;font-size:.7rem;color:var(--text-lighter);">
          ${c.summary||''}
        </div>
        <!-- 时间线 -->
        <div style="padding:0 14px 12px;position:relative;">
          <!-- 竖线 -->
          <div style="position:absolute;left:29px;top:0;bottom:12px;width:2px;background:linear-gradient(180deg,${prog.color}88,${prog.color}22);"></div>
          ${ann.map((a,ai)=>`
          <div style="display:flex;gap:10px;align-items:flex-start;padding:5px 0 5px 0;position:relative;">
            <!-- 时间轴圆点 -->
            <div style="width:10px;height:10px;border-radius:50%;background:${ai===0?prog.color:'#d1d5db'};
                        border:2px solid ${ai===0?prog.color:'#e5e7eb'};
                        flex-shrink:0;margin-top:3px;position:relative;z-index:1;
                        box-shadow:${ai===0?`0 0 0 3px ${prog.color}22`:''};"></div>
            <!-- 内容 -->
            <div style="flex:1;display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
              <span style="font-size:.68rem;color:var(--text-lighter);white-space:nowrap;min-width:82px;font-variant-numeric:tabular-nums;">${a.date}</span>
              <a href="${a.docUrl}" target="_blank" rel="noopener"
                 style="font-size:.78rem;color:var(--navy);text-decoration:none;flex:1;line-height:1.45;"
                 title="${a.title}">${a.title.slice(0,80)}${a.title.length>80?'…':''}</a>
              <a href="${a.docUrl}" target="_blank" rel="noopener" onclick="event.stopPropagation()"
                 style="font-size:.65rem;padding:2px 8px;border:1px solid var(--gold);color:var(--gold);border-radius:4px;white-space:nowrap;text-decoration:none;flex-shrink:0;">PDF↗</a>
            </div>
          </div>`).join('')}
        </div>
      </div>`;
    });

    html += `</div>
    <div style="font-size:.66rem;color:var(--text-lighter);margin-top:12px;padding:6px 12px;background:#f8f6f0;border-radius:6px;line-height:1.7;">
      📋 ${isEn
        ? 'Source: HKEXnews · Keywords: 分拆 / spin-off / demerger · Auto-updated daily · Stocks &lt; HK$0.5 excluded'
        : '数据来源：港交所新闻 · 关键词：分拆 / spin-off / demerger · 每日自动更新 · 现价低于 HK$0.5 已过滤'}
    </div>`;

    el.innerHTML = html;
    _spinoffCache = el.innerHTML;

  } catch(e) {
    el.innerHTML = `<p style="padding:16px;color:var(--text-lighter);">${lang==='en'?'Spin-off data unavailable':'分拆数据加载失败，请刷新'}</p>`;
  }
}

function spinoffToggle(idx) {
  const body  = document.getElementById('so-body-' + idx);
  const arrow = document.getElementById('so-arrow-' + idx);
  if (!body) return;
  const open = body.style.display !== 'none';
  body.style.display = open ? 'none' : 'block';
  if (arrow) arrow.textContent = open ? '▶' : '▼';
}


