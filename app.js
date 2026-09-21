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
  tabCurrent: ['📊 持仓明细','📊 Holdings'],
  tabChanges: ['📈 季度变化','📈 QoQ Changes'],
  tabHistory: ['📉 历史趋势','📉 History'],
  tabHomework: ['📋 价值筛选','📋 Value Picks'],
  tabSpinoff:  ['🇭🇰 港股分拆','🇭🇰 HK Spin-offs'],
  tabSpinoffUS: ['🇺🇸 美股分拆','🇺🇸 US Spin-offs'],
  tabGame: ['🎴 思维试炼','🎴 Munger Trials'],
  selLabel: ['切换投资者：','Investor:'],
  tabTimeline: ['⏳ 时间轴','⏳ Timeline'],
  // Table headers
  thTicker: ['代码','Ticker'],
  thStock: ['股票','Stock'],
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
  secCoal: ['煤炭','Coal'],
  secOilDrill: ['油气钻探','Oil & Gas Drilling'],
  secMetCoal: ['冶金/煤炭','Metallurgical Coal'],
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
  hkTitle: ['港股权益披露','HK Disclosures'],
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
let investorRequestId = 0;

// ========== 投资者结构化配置（单一权威来源：investors.json） ==========
// 详情页文案（人物简介/时间线/投资理念/推荐阅读）仍在 updateInvestorContent() 里手工维护，
// 因为是创作性内容无法自动生成。但导航/tab切换/港股fallback/数据文件列表/价值筛选候选名单
// 这些结构性逻辑均从下面的 INVESTOR_CFG 派生，新增投资者只需编辑 investors.json。
let INVESTOR_CFG = [];           // investors.json 里的 investors 数组原样（加载后充实）
let INVESTOR_CFG_BY_ID = {};     // id -> 配置对象，方便查找
let INVESTORS = [];              // 按 investors.json 顺序排列的 id 列表
let INVESTOR_LABELS = {};        // id -> 中文名
let INVESTOR_LABELS_EN = {};     // id -> 英文名

async function loadInvestorConfig() {
  try {
    const resp = await fetch('investors.json?t=' + Math.floor(Date.now()/300000));
    const json = await resp.json();
    INVESTOR_CFG = json.investors || [];
  } catch (e) {
    console.error('investors.json 加载失败，将无法正常显示投资者列表:', e);
    INVESTOR_CFG = [];
  }
  INVESTOR_CFG_BY_ID = {};
  INVESTORS = [];
  INVESTOR_LABELS = {};
  INVESTOR_LABELS_EN = {};
  for (const inv of INVESTOR_CFG) {
    INVESTOR_CFG_BY_ID[inv.id] = inv;
    INVESTORS.push(inv.id);
    INVESTOR_LABELS[inv.id] = inv.name;
    INVESTOR_LABELS_EN[inv.id] = inv.nameEn;
  }
}
function renderInvestorBtns() {
  const bar = document.getElementById('investorBtn');
  if (!bar) return;
  const labels = lang === 'en' ? INVESTOR_LABELS_EN : INVESTOR_LABELS;
  bar.innerHTML = INVESTORS.map(id => {
    const active = id === investor;
    return `<button onclick="switchInvestor('${id}')" style="padding:5px 11px;border:1px solid ${active ? 'var(--gold)' : 'rgba(212,168,83,.3)'};border-radius:16px;background:${active ? 'rgba(212,168,83,.15)' : 'transparent'};color:${active ? 'var(--gold)' : 'var(--text-light)'};font-size:.72rem;font-weight:${active ? '700' : '500'};cursor:pointer;white-space:nowrap;transition:all .15s;">${labels[id]}</button>`;
  }).join('');
}
async function switchInvestor(v, {fresh = false, signal} = {}) {
  const requestId = ++investorRequestId;
  const target = v && INVESTORS.includes(v) ? v
    : INVESTORS[(INVESTORS.indexOf(investor) + 1) % INVESTORS.length];
  const src = document.getElementById('dataSource');
  const cfg = INVESTOR_CFG_BY_ID[target];
  if (src) src.textContent = lang === 'en' ? 'Loading published data…' : '正在读取已发布数据…';
  try {
    if (!cfg) throw new Error('Unknown investor: ' + target);
    const stamp = fresh ? Date.now() : Math.floor(Date.now()/300000);
    const r = await fetch(cfg.dataFile + '?t=' + stamp, {signal, cache: fresh ? 'no-store' : 'default'});
    if (!r.ok) throw new Error(cfg.dataFile + ' HTTP ' + r.status);
    const newData = await r.json();
    if (requestId !== investorRequestId) return false;
    if (!newData?.current || !Array.isArray(newData.current.holdings)) throw new Error('Invalid holdings data');
    const pricesOK = await loadPrices(cfg.pricesFile, requestId, {signal, stamp, fresh});
    if (requestId !== investorRequestId) return false;
    // Commit the selection and its dataset together; failed switches keep the old selection.
    investor = target;
    data = newData;
    renderInvestorBtns();
    renderSummary(); renderHoldings(); renderChanges(); renderHistoryChart(); renderTimelineTable();
    renderInsights(); updateInvestorContent();
    const updated = data.meta?.lastUpdated;
    const age = Date.now() - Date.parse(updated);
    const maxAge = (cfg.source13F === false ? 9 * 24 : 48) * 3600000;
    const stale = !Number.isFinite(age) || age > maxAge;
    if (src) src.textContent = (stale || !pricesOK ? '⚠ ' : '✓ ') +
      (lang === 'en' ? 'Published data' : '已发布数据') +
      (updated ? ' · ' + new Date(updated).toLocaleString(lang === 'en' ? 'en-US' : 'zh-CN', {timeZone: 'Asia/Shanghai'}) : '') +
      (stale ? (lang === 'en' ? ' · Check update status' : ' · 数据较旧，请查看更新状态') : '') +
      (!pricesOK ? (lang === 'en' ? ' · Prices unavailable' : ' · 股价暂不可用') : '');
    return true;
  } catch(e) {
    if (requestId !== investorRequestId) return false;
    console.error('switchInvestor error:', e.message);
    if (src) src.textContent = lang === 'en'
      ? '⚠ Loading failed; previous selection retained. Try again.'
      : '⚠ 加载失败，保留原投资人和数据，请重试';
    return false;
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
function applyLanguageLabels() {
  document.getElementById('langBtn').textContent = lang === 'zh' ? 'EN' : '中';
  const refreshBtn = document.getElementById('btnRefresh');
  if (refreshBtn && !refreshBtn.disabled) refreshBtn.textContent = lang === 'en' ? '🔄 Refresh' : '🔄 刷新';
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = t(el.dataset.i18n);
    if (el.childElementCount === 0) el.textContent = v;
  });
}

function switchLang() {
  lang = lang === 'zh' ? 'en' : 'zh';
  localStorage.setItem('lang', lang);
  renderInvestorBtns();
  applyLanguageLabels();
  renderSummary(); renderHoldings(); renderChanges(); renderInsights(); renderHistoryChart();
  updateInvestorContent();
  if (_runStatusData) updateStatusDot(_runStatusData);
  _homeworkCache = null;
  if (!document.getElementById('tab-homework').classList.contains('d-none')) renderHomework();
  if (!document.getElementById('tab-spinoff').classList.contains('d-none')) renderSpinoff();
  if (!document.getElementById('tab-spinoff_us').classList.contains('d-none')) renderSpinoffUS();
  if (!document.getElementById('tab-game').classList.contains('d-none')) { _gameLoaded = false; renderGame(); }
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
  if (prev===0) return `<span class="qoq-new">${lang === 'en' ? 'New' : '新进'}</span>`;
  const p=((cur-prev)/prev*100);
  if (Math.abs(p)<0.05) return '<span class="qoq-flat">-</span>';
  const c=p>0?'qoq-up':'qoq-down', s=p>0?'+':'';
  return `<span class="${c}">${s}${p.toFixed(1)}%</span>`;
}
function fmtShareChg(cur, prev) {
  if (prev===0) return `<span class="qoq-new">${lang === 'en' ? 'New' : '新进'}</span>`;
  const d=cur-prev;
  if (d===0) return `<span class="qoq-flat">${lang === 'en' ? 'Unchanged' : '不变'}</span>`;
  const p=(d/prev*100), c=d>0?'qoq-up':'qoq-down', sign=d>0?'+':'-';
  return `<span class="${c}">${sign}${fmtNum(Math.abs(d))} (${d>0?'+':''}${p.toFixed(1)}%)</span>`;
}

// ========== DATA ==========
let data = null;
let prices = null;  // loaded from prices.json (generated by GitHub Action)
let hkHoldings = null;  // loaded from hk_holdings.json

async function loadPrices(pf, requestId = investorRequestId, {signal, stamp = Math.floor(Date.now()/300000), fresh = false} = {}) {
  const file = pf || 'prices.json';
  try {
    const resp = await fetch(file + '?t=' + stamp, {signal, cache: fresh ? 'no-store' : 'default'});
    if (!resp.ok) throw new Error(file + ' HTTP ' + resp.status);
    const newPrices = await resp.json();
    if (!newPrices || typeof newPrices.quotes !== 'object' || !newPrices.quotes) throw new Error('Invalid prices');
    if (requestId !== investorRequestId) return;
    prices = newPrices;
    const el = document.getElementById('priceUpdate');
    if (el) el.textContent =
      prices.updatedAt ? new Date(prices.updatedAt).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'})
      : prices.updated ? new Date(prices.updated).toLocaleString('zh-CN',{timeZone:'Asia/Shanghai'}) : '待更新';
    return true;
  } catch(e) {
    if (requestId !== investorRequestId) return;
    console.log('prices unavailable:', file);
    prices = { quotes: {}, costBasis: {} };
    const el2 = document.getElementById('priceUpdate');
    if (el2) el2.textContent = '暂不可用';
    return false;
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

// Reload the selected investor's complete, server-processed published snapshot.
// Browser-side SEC parsing bypassed ticker reconciliation and mixed investor data.
async function refreshLive() {
  const btn = document.getElementById('btnRefresh');
  const ctrl = new AbortController();
  const timeout = setTimeout(() => ctrl.abort(), 30000);
  btn.disabled = true;
  btn.textContent = lang === 'en' ? '⏳ Refreshing…' : '⏳ 刷新中…';
  try {
    await switchInvestor(investor, {fresh: true, signal: ctrl.signal});
    if (!ctrl.signal.aborted) await initStatusDot(ctrl.signal);
  } finally {
    clearTimeout(timeout);
    btn.disabled = false;
    btn.textContent = lang === 'en' ? '🔄 Refresh' : '🔄 刷新';
  }
}

// ========== TIMELINE & HK HOLDINGS ==========
async function loadHKHoldings() {
  try {
    const cfg = INVESTOR_CFG_BY_ID[investor];
    const hkUrl = cfg ? cfg.hkFile : null;
    if (!hkUrl) { hkHoldings = { holdings: [], disclaimer: '' }; return; }
    const resp = await fetch(hkUrl + '?t=' + Math.floor(Date.now()/300000));
    hkHoldings = await resp.json();
  } catch(e) {
    console.log('hk_holdings.json unavailable');
    hkHoldings = { holdings: [], disclaimer: '' };
  }
}

function renderTimeline() {
  const container = document.getElementById('timelineCanvas');
  if (!container || !data || !data.history || !data.history.holdings) {
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

// 注：旧的同名同步 renderHKHoldings() 定义（还取决于 hkHoldings 全局变量）已删除，
// 因为 JS 里同名函数会被后面的定义覆盖，该旧定义实际上从未被调用过（死代码）。
// 真正生效的版本在本文件靠后（下方已修复为从 INVESTOR_CFG_BY_ID 动态取 hkUrl）。

// ========== RENDER ==========
// INVESTOR_CIK 不再硬码维护，从 INVESTOR_CFG 动态构建。
// 修复说明：审计过程中发现旧硬码字典里 pabrai=0001474216、akre=0001499406
// 两个 CIK 都是错的（分别指向与本项目无关的 Franchise Portfolio 2, Inc. 和
// KLP 2010 ANP Mirror Trust B，经 SEC EDGAR 官方接口核实），导致前端一直展示错误
// CIK 给用户。investors.json 里的 cik 字段已经过 fetch_13f_all.py 实际抓取验证，
// 以它为准。
function getInvestorCIK(id) {
  const cfg = INVESTOR_CFG_BY_ID[id];
  if (!cfg || !cfg.cik) return null;
  return String(cfg.cik).padStart(10, '0');
}

function renderSummary() {
  const d = data.current;
  // 更新 hero 区报告期 / 提交日 / CIK
  const metaRow = document.getElementById('metaRow');
  if (metaRow) {
    const isEn = lang === 'en';
    const cik = getInvestorCIK(investor);
    const cikHtml = cik
      ? `<span><strong>CIK</strong> ${cik}</span>`
      : '';
    metaRow.innerHTML =
      `<span><strong>${isEn ? 'Period' : '\u62a5\u544a\u671f'}</strong> ${d.periodEnd || '--'}</span>` +
      `<span><strong>${isEn ? 'Filed' : '\u63d0\u4ea4\u65e5'}</strong> ${d.filingDate || '--'}</span>` +
      cikHtml;
  }
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
    const staleTitle = lang === 'en' ? 'Live quote temporarily unavailable — showing last known price' : '实时报价暂时拉取失败，显示为最后一次成功报价';
    const priceHtml = (q && !q.error)
      ? `${currSymbol(h.ticker)}${q.c.toFixed(2)}${q.stale ? ` <span title="${staleTitle}" style="color:var(--warn,#c9812f);font-size:.7em;">⏱</span>` : ''}`
      : '<span style="color:var(--text-lighter)">--</span>';
    
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
      if (at) costHtml += `\n\n全周期 (${at.first}~${at.last}, ${at.buy_quarters ?? at.quarters}季): 均价 $${at.avg}`;
      costHtml += `" style="cursor:help">`;
      costHtml += `<div style="font-weight:600">${cur$}${rc.buy}</div>`;
      costHtml += `<div style="font-size:.65rem;color:var(--text-lighter);">${t('costRecent')} ${srcBadge} <span class="${pnlClass}" style="font-weight:500;">${pnlSign}${pnl}%</span></div>`;
      if (at) {
        costHtml += `<div style="font-weight:500;color:var(--navy);margin-top:3px;">$${at.avg}</div>`;
        // 持仓时间：从首次建仓到当前报告季
        const holdQ = (q) => { const [y,n]=q.split(' Q'); return parseInt(y)*4+parseInt(n); };
        const curQ  = data?.current?.quarter || at.last;
        const nq    = Math.max(holdQ(curQ) - holdQ(at.first) + 1, 1);
        const yrs   = (nq / 4).toFixed(1).replace(/\.0$/,'');
        const _en = lang === 'en';
        const holdLabel = _en ? `${at.buy_quarters ?? at.quarters}q buy · held ${nq}q / ${yrs}y`
                               : `${at.buy_quarters ?? at.quarters}季买入 · 持有 ${nq}季 / ${yrs}年`;
        costHtml += `<div style="font-size:.6rem;color:var(--text-lighter);">${t('costAllTime')} <span style="color:var(--text-light);">(${holdLabel})</span></div>`;
      }
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
    
    return `<tr><td class="idx-cell"><span class="idx-num">${i+1}</span></td><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td class="shares-value-cell"><div style="font-weight:600">${fmtNum(h.shares)}</div><div style="font-size:.68rem;color:var(--text-lighter);margin-top:2px;">$${h.value.toLocaleString()}</div><div class="mobile-weight-inline" style="display:none;font-size:.65rem;color:var(--navy);font-weight:600;margin-top:3px;"><span style="font-weight:400;color:var(--text-lighter);">${isEn?'Wt':'仓位'}</span> ${pct}%</div></td><td class="price-cell">${priceHtml}</td><td class="cost-cell">${costHtml}</td><td style="width:100px;"><div class="bar-wrap"><div class="bar-fill" style="width:${pct*3.5}%"></div><span style="font-size:.7rem;font-weight:600;color:var(--navy);margin-left:6px;">${pct}%</span></div></td><td style="width:80px;text-align:center;">${mosCellHtml}</td></tr>`;
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

function sameSecurity(a, b) {
  if (a.cusip && b.cusip) return a.cusip === b.cusip;
  const ticker = h => (h.ticker || '').toUpperCase().replace(/[./-]/g, '');
  if (ticker(a) && ticker(a) === ticker(b)) return true;
  // Legacy history may lack CUSIP and contain unresolved issuer names.
  return !!a.name && a.name === b.name && (a.cls || '') === (b.cls || '') &&
    ((a.ticker || '').startsWith('?') || (b.ticker || '').startsWith('?'));
}

function quarterlyHoldings(snapshot = data) {
  const current = snapshot.current;
  const authoritative = Array.isArray(current.previousHoldings);
  const previous = authoritative ? current.previousHoldings
    : snapshot.history?.holdings?.[current.prevQuarter] || [];
  const remaining = [...previous];
  const rows = current.holdings.map(h => {
    const index = remaining.findIndex(p => sameSecurity(h, p));
    const p = index < 0 ? null : remaining.splice(index, 1)[0];
    return {...h,
      prevShares: authoritative ? (p?.shares || 0) : (h.prevShares ?? p?.shares ?? 0),
      prevValue: authoritative ? (p?.value || 0) : (h.prevValue ?? p?.value ?? 0)};
  });
  for (const p of remaining) {
    if (p.shares > 0) rows.push({...p, shares: 0, value: 0, prevShares: p.shares, prevValue: p.value, exited: true});
  }
  return rows;
}

function renderChanges() {
  const d = data.current, en = lang === 'en';
  const pq = d.prevQuarter || (en ? 'Previous' : '上季');
  const cq = d.quarter || (en ? 'Current' : '本季');
  document.getElementById('chPS').textContent = pq + (en ? ' Shares' : ' 持股');
  document.getElementById('chCS').textContent = cq + (en ? ' Shares' : ' 持股');
  document.getElementById('chPV').textContent = pq + (en ? ' Value' : ' 市值');
  document.getElementById('chCV').textContent = cq + (en ? ' Value' : ' 市值');
  document.getElementById('changesBody').innerHTML = quarterlyHoldings().map(h => {
    const vd = h.value - h.prevValue;
    const vc = h.prevValue === 0 ? 'qoq-new' : (vd > 0 ? 'qoq-up' : (vd < 0 ? 'qoq-down' : 'qoq-flat'));
    const vs = vd > 0 ? '+' : vd < 0 ? '-' : '';
    const symbol = currSymbol(h.ticker);
    const exited = h.exited ? `<span class="qoq-down"> · ${en ? 'Exited' : '清仓'}</span>` : '';
    return `<tr><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}${exited}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td>${h.prevShares===0?'-':fmtNum(h.prevShares)}</td><td>${fmtNum(h.shares)}</td><td>${fmtShareChg(h.shares,h.prevShares)}</td><td>${h.prevValue===0?'-':symbol+fmtVal(h.prevValue)}</td><td>${symbol}${fmtVal(h.value)}</td><td class="${vc}">${h.prevValue===0?(en?'New':'新进'):`${vs}${symbol}${fmtVal(Math.abs(vd))} (${fmtPct(h.value,h.prevValue)})`}</td></tr>`;
  }).join('');
}

// AI artifacts load independently; holdings and prices never wait for a model.
let _aiSupplement = {entries:{}};
const aiEscape = value => String(value ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
function aiInvestorSource(d) {
  const cur=d?.current || {}, fields=['ticker','cusip','shares','value','prevShares','prevValue','cnName','name'];
  const rows=items=>(items || []).map(h=>fields.map(k=>h[k] ?? null));
  return {quarter:cur.quarter || '',holdings:rows(cur.holdings),previousHoldings:rows(cur.previousHoldings)};
}
function aiValueSource(candidates) {
  return candidates.map(c=>[c.ticker ?? null,c.cnName || c.name || null,(c.investors || []).map(h=>[h.id ?? null,h.weight ?? null,h.chg ?? null,h.name ?? null])]);
}
function aiMatchingEntry(key, source) {
  const e=_aiSupplement.entries?.[key];
  // Object field order is not data: serializers can reorder JSON keys.
  const canonical = value => Array.isArray(value) ? value.map(canonical)
    : value && typeof value==='object'
      ? Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])) : value;
  return e && e.renderVersion===3 && ['model_selection','deterministic'].includes(e.mode) && typeof e.summary==='string' && JSON.stringify(canonical(e.source))===JSON.stringify(canonical(source)) ? e : null;
}
async function refreshAISupplements() {
  const ctrl=new AbortController(), timer=setTimeout(()=>ctrl.abort(),6000);
  try {
    const response=await fetch('ai_supplement.json?t='+Math.floor(Date.now()/300000),{signal:ctrl.signal});
    if (!response.ok) return;
    const payload=await response.json();
    if (payload.schemaVersion!==2 || !payload.entries || typeof payload.entries!=='object') return;
    _aiSupplement=payload;
    if (data) renderInsights();
    _homeworkCache=null;
  } catch {} finally { clearTimeout(timer); }
}

function aiInvestorFallback(snapshot) {
  const cur=snapshot.current, hasPrevious=Array.isArray(cur.previousHoldings) || Array.isArray(snapshot.history?.holdings?.[cur.prevQuarter]);
  const rows=quarterlyHoldings(snapshot).sort((a,b)=>Math.max(b.value||0,b.prevValue||0)-Math.max(a.value||0,a.prevValue||0));
  const ranked=rows.filter(h=>h.shares!==h.prevShares).concat(rows.filter(h=>h.shares===h.prevShares));
  return `${cur.quarter || ''}（按披露股数比较）：`+ranked.slice(0,5).map(h=>{
    const original=cur.holdings.find(x=>sameSecurity(x,h));
    const prev=hasPrevious ? h.prevShares : original?.prevShares;
    let change='上季股数未知，不判断增减';
    if (prev!=null) {
      if (!prev) change=h.shares?'新建仓':'无持仓';
      else if (!h.shares) change='清仓';
      else if(h.shares===prev) change='股数不变';
      else { const pct=Math.abs(h.shares/prev-1)*100; change=(h.shares>prev?'增持':'减持')+(pct<0.05?'（微量变动）':pct.toFixed(1)+'%'); }
    }
    const name=h.cnName || h.name || '';
    return (h.ticker.startsWith('?') ? name || h.ticker.slice(1) : name && name!==h.ticker ? `${name}（${h.ticker}）`:h.ticker)+'：'+change;
  }).join('；')+'。';
}
function aiValueFallback(candidates) {
  const labels={new:'新建仓',added:'增持',trimmed:'减持',hold:'股数不变'};
  const rows=candidates.flatMap(c=>(c.investors || []).map(h=>({c,h})));
  rows.sort((a,b)=>(a.h.chg==='hold')-(b.h.chg==='hold'));
  return rows.length ? '按各投资人最新披露组合：'+rows.slice(0,3).map(({c,h})=>{
    const name=c.cnName || c.name || '', stock=name && name!==c.ticker ? `${name}（${c.ticker}）`:c.ticker;
    const weight=typeof h.weight==='number' && Number.isFinite(h.weight) && h.weight>=0 && h.weight<=100 ? `，占其披露组合市值${h.weight}%`:'';
    return `${h.name || INVESTOR_LABELS[h.id] || h.id}：${stock}${labels[h.chg] || '增减未知'}${weight}`;
  }).join('；')+'。' : '';
}

function renderInsights() {
  const d = data.current, ins = [], changes = quarterlyHoldings();

  // AI 摘要（如果有）
  const localAI = aiMatchingEntry('investor:'+investor,aiInvestorSource(data));
  // Unverified legacy prose is never used as a fallback.
  const aiSummary = localAI?.summary || aiInvestorFallback(data);
  const aiQuarter = localAI?.source?.quarter || d.quarter || '';
  const aiUpdated = localAI?.generatedAt;
  const aiLabel = localAI?.mode==='model_selection' ? '✨ AI' : (lang==='en'?'Quarterly summary':'季度摘要');
  const aiDate = aiUpdated ? ' · ' + new Date(aiUpdated).toLocaleDateString(lang === 'en' ? 'en-US' : 'zh-CN') : '';
  const box = document.querySelector('.insights-box');
  let aiBar = document.getElementById('aiSummaryBar');
  if (aiSummary && box) {
    const html = `<div id="aiSummaryBar" style="
      background:linear-gradient(135deg,rgba(99,102,241,0.08),rgba(139,92,246,0.08));
      border:1px solid rgba(99,102,241,0.2);
      border-radius:8px;padding:10px 14px;margin-bottom:10px;
      font-size:.78rem;line-height:1.6;color:var(--text);
    "><span style="font-size:.65rem;color:#6366f1;font-weight:600;margin-right:6px;">${aiLabel} ${aiEscape(aiQuarter)}${aiDate}</span>${aiEscape(aiSummary)}</div>`;
    if (aiBar) { aiBar.outerHTML = html; } else { box.insertAdjacentHTML('afterbegin', html); }
  } else if (aiBar) {
    aiBar.remove();
  }
  const np = changes.filter(h=>!h.prevShares);
  if (np.length) ins.push(`${t('insNew')} ${np.length} ${t('insNew2')} ${np.map(h=>h.ticker).join('、')}, ${t('insExpand')}。`);
  const bs = changes.filter(h=>h.prevShares&&h.shares<h.prevShares*0.5);
  bs.forEach(h=>{ const p=((h.prevShares-h.shares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name, h)})${t('insSell')} ${p}%, ${t('insSell2')} ${fmtNum(h.prevShares-h.shares)} ${t('insSell3')}。`); });
  const inc = changes.filter(h=>h.prevShares&&h.shares>h.prevShares*1.1);
  inc.forEach(h=>{ const p=((h.shares-h.prevShares)/h.prevShares*100).toFixed(0); ins.push(`${h.ticker}(${cn(h.name, h)})${t('insBuy')} ${p}%, ${t('insBuy2')} ${fmtNum(h.shares-h.prevShares)} ${t('insBuy3')}。`); });
  const unch = changes.filter(h=>h.prevShares&&h.shares===h.prevShares);
  if (unch.length) ins.push(`${unch.map(h=>h.ticker).join('、')} ${t('insUnchanged')}。`);
  const t3p = (d.holdings.slice(0,3).reduce((s,h)=>s+h.value,0)/d.totalValue*100).toFixed(0);
  ins.push(`${t('insTop3')} ${t3p}%, ${t('insTop3b')}。`);
  document.getElementById('insightsList').innerHTML = ins.map(s=>`<li>${s}</li>`).join('');
}

// History values are millions of the investor's reporting currency, not returns/AUM.
function historyQuarterIndex(q) {
  const m = /^(\d{4}) Q([1-4])$/.exec(q);
  return m ? Number(m[1]) * 4 + Number(m[2]) - 1 : NaN;
}
function historySeries(history) {
  if (history?.verification?.status === 'unverified') return {quarters: [], values: []};
  const points = new Map();
  (history?.quarters || []).forEach((q, i) => {
    if (!Number.isFinite(historyQuarterIndex(q))) return;
    const holdings = history.holdings?.[q];
    // Prefer exact filed totals to old rounded summary values.
    const v = Array.isArray(holdings) && holdings.length && holdings.every(h => typeof h.value === 'number' && Number.isFinite(h.value) && h.value >= 0)
      ? holdings.reduce((sum, h) => sum + h.value, 0) / 1e6 : history.values?.[i];
    if (typeof v === 'number' && Number.isFinite(v) && v >= 0) points.set(q, v);
  });
  const entries = [...points].sort((a, b) => historyQuarterIndex(a[0]) - historyQuarterIndex(b[0]));
  return {quarters: entries.map(p => p[0]), values: entries.map(p => p[1])};
}
function historyMoney(v, precision = 2) {
  const currency = investor === 'webb' ? 'HK$' : 'US$';
  const n = v >= 1000 ? v / 1000 : v;
  return currency + n.toLocaleString('en-US', {maximumFractionDigits: precision}) + (v >= 1000 ? 'B' : 'M');
}
function historyRange(values) {
  const low = Math.min(...values), high = Math.max(...values);
  const margin = Math.max((high - low) * .12, high * .02, .01);
  return {minV: Math.max(0, low - margin), maxV: high + margin};
}
function historyChange(quarters, values, i) {
  if (i < 1 || values[i-1] <= 0 || historyQuarterIndex(quarters[i]) - historyQuarterIndex(quarters[i-1]) !== 1) return null;
  return (values[i] - values[i-1]) / values[i-1];
}
function historyX(quarters, i) {
  const first = historyQuarterIndex(quarters[0]);
  const span = historyQuarterIndex(quarters[quarters.length-1]) - first;
  return span ? (historyQuarterIndex(quarters[i]) - first) / span : .5;
}
function historySegments(quarters) {
  const segments = [];
  quarters.forEach((q, i) => {
    if (!i || historyQuarterIndex(q) - historyQuarterIndex(quarters[i-1]) !== 1) segments.push([]);
    segments[segments.length-1].push(i);
  });
  return segments;
}
function generateHistoryInsight(quarters, values) {
  const isEn = lang === 'en';
  if (!values.length) return isEn ? 'No historical data available.' : '暂无历史数据。';
  const first = values[0], last = values[values.length-1];
  const peak = Math.max(...values), peakQ = quarters[values.indexOf(peak)];
  const change = first > 0 ? ((last-first)/first*100) : null;
  const pct = change === null ? '—' : `${change > 0 ? '+' : ''}${change.toFixed(1)}%`;
  let txt = isEn
    ? `Disclosed holdings value: ${quarters[0]} ${historyMoney(first)} → ${quarters[quarters.length-1]} ${historyMoney(last)} (change ${pct}). Peak: ${peakQ}, ${historyMoney(peak)}. `
    : `披露持仓市值：${quarters[0]} ${historyMoney(first)} → ${quarters[quarters.length-1]} ${historyMoney(last)}（变化 ${pct}）。峰值：${peakQ}，${historyMoney(peak)}。`;
  if (historySegments(quarters).length > 1) {
    const known = new Set(quarters.map(historyQuarterIndex)), missing = [];
    for (let i = historyQuarterIndex(quarters[0]); i <= historyQuarterIndex(quarters[quarters.length-1]); i++) {
      if (!known.has(i)) missing.push(`${Math.floor(i/4)} Q${i%4+1}`);
    }
    txt += isEn ? `Missing quarters (not zero holdings): ${missing.join(', ')}. ` : `缺失季度：${missing.join('、')}；断线不代表清仓。`;
    const lookup = data?.history?.coverage?.expandedLookup;
    if (lookup?.status === 'checked') {
      const checked = /^\d{4}-\d{2}-\d{2}/.exec(lookup.checkedAt || '')?.[0] || '—';
      txt += isEn ? `SEC historical indexes were also checked (${checked}); a usable portfolio for the missing quarters is still unavailable. `
        : `已补查 SEC 历史总索引（${checked}），这些季度仍未取得可核实的原始持仓数据。`;
    } else if (lookup?.status === 'partial') {
      txt += isEn ? 'Historical-source verification is incomplete and will retry automatically. '
        : '历史来源补查尚未完成，将自动重试。';
    }
  }
  txt += isEn ? 'Value changes are not investment returns; disclosed holdings do not represent total assets under management.' : '市值变化不等于投资收益，披露持仓也不代表全部管理资产。';
  return txt;
}

// ── 手机端：卡片式时间轴 ──
function renderHistoryMobile(container, quarters, values) {
  const isEn = lang === 'en';
  const fmtM = historyMoney;
  const W = 340, H = 200;
  const pad = {top:20, right:16, bottom:32, left:68};
  const w = W - pad.left - pad.right, h = H - pad.top - pad.bottom;
  const {minV, maxV} = historyRange(values);
  const range = maxV - minV || 1;
  const gX = i => pad.left + historyX(quarters, i)*w;
  const gY = v => pad.top + h - ((v - minV)/range)*h;

  const paths = historySegments(quarters).map(indices => {
    const pts = indices.map(i => `${gX(i).toFixed(1)},${gY(values[i]).toFixed(1)}`).join(' ');
    const fill = `${pts} ${gX(indices[indices.length-1])},${pad.top+h} ${gX(indices[0])},${pad.top+h}`;
    return `<polygon points="${fill}" fill="url(#mspg)"/><polyline points="${pts}" fill="none" stroke="#1e3a5f" stroke-width="2"/>`;
  }).join('');

  // Y轴标签 (3个)
  let yLines = '';
  for (let i = 0; i <= 3; i++) {
    const v = minV + (maxV - minV) * (i/3);
    const y = gY(v);
    const label = historyMoney(v, 1);
    yLines += `<line x1="${pad.left}" y1="${y.toFixed(1)}" x2="${W-pad.right}" y2="${y.toFixed(1)}" stroke="#e5e7eb" stroke-width="0.5"/>`;
    yLines += `<text x="${pad.left-6}" y="${(y+3.5).toFixed(1)}" text-anchor="end" font-size="8.5" fill="#9ca3af">${label}</text>`;
  }

  // X轴标签 (按年)
  let xLabels = '';
  const shownYrs = new Set();
  quarters.forEach((q, i) => {
    const yr = q.split(' ')[0];
    if (shownYrs.has(yr)) return;
    shownYrs.add(yr);
    const x = gX(i);
    xLabels += `<text x="${x.toFixed(1)}" y="${H-6}" text-anchor="middle" font-size="8.5" fill="#9ca3af">${yr}</text>`;
  });

  // 大幅变动标注圆
  let markers = '';
  for (let i = 1; i < values.length; i++) {
    const chg = historyChange(quarters, values, i);
    if (Math.abs(chg) > 0.25) {
      const x = gX(i), y = gY(values[i]);
      const col = chg > 0 ? '#16a34a' : '#dc2626';
      markers += `<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="5" fill="${col}" fill-opacity="0.15" stroke="${col}" stroke-width="1.5"/>`;
      markers += `<text x="${x.toFixed(1)}" y="${(y + (chg>0?-7:12)).toFixed(1)}" text-anchor="middle" font-size="7" fill="${col}" font-weight="bold">${chg>0?'▲':'▼'}</text>`;
    }
  }

  // 最新点标注
  const lastX = gX(values.length-1), lastY = gY(values[values.length-1]);
  const lastLabel = fmtM(values[values.length-1]);
  const labelAnchor = lastX > W*0.7 ? 'end' : 'start';
  const labelX = labelAnchor === 'end' ? lastX - 6 : lastX + 6;

  const svg = `<svg viewBox="0 0 ${W} ${H}" style="width:100%;display:block;" xmlns="http://www.w3.org/2000/svg">
    <defs>
      <linearGradient id="mspg" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0%" stop-color="#1e3a5f" stop-opacity="0.2"/>
        <stop offset="100%" stop-color="#1e3a5f" stop-opacity="0.01"/>
      </linearGradient>
    </defs>
    ${yLines}
    ${xLabels}
    ${paths}
    ${values.map((v,i)=>`<circle cx="${gX(i)}" cy="${gY(v)}" r="2" fill="#1e3a5f"/>`).join('')}
    ${markers}
    <circle cx="${lastX.toFixed(1)}" cy="${lastY.toFixed(1)}" r="3.5" fill="#1e3a5f" stroke="white" stroke-width="1.5"/>
    <text x="${labelX.toFixed(1)}" y="${(lastY-6).toFixed(1)}" text-anchor="${labelAnchor}" font-size="9.5" fill="#1e3a5f" font-weight="bold">${lastLabel}</text>
  </svg>`;

  container.innerHTML = `<div style="background:var(--cream);border:1px solid var(--border-light);border-radius:8px;padding:14px 12px;">${svg}</div>`;
}

function renderHistoryChart() {
  const wrap = document.getElementById('historyChartWrap');
  const canvas = document.getElementById('historyChart');
  if (!canvas) return;
  const {quarters, values} = historySeries(data?.history);
  document.getElementById('hcTooltip')?.remove();
  canvas.onmousemove = canvas.onmouseleave = null;
  const mobile = document.getElementById('historyMobileWrap');
  if (mobile) { mobile.innerHTML = ''; mobile.style.display = 'none'; }
  canvas.parentElement.style.display = '';
  if (!values.length) {
    canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height);
    const insight = document.getElementById('historyInsight');
    if (insight) { insight.textContent = data?.history?.verification?.status === 'unverified' ? (lang === 'en' ? 'Historical quarter snapshots cannot be reconciled to dated disclosures. Chart temporarily unavailable.' : '历史季度快照尚无法与披露日期核对，暂不绘制趋势图。') : generateHistoryInsight([], []); insight.style.display = ''; }
    return;
  }
  const isMobile = window.innerWidth < 640;

  // Render deterministic data summary
  const insightEl = document.getElementById('historyInsight');
  if (insightEl) {
    const txt = generateHistoryInsight(quarters, values);
    const label = lang === 'en' ? '📊 Summary' : '📊 数据摘要';
    insightEl.innerHTML = txt ? `<div style="display:flex;gap:8px;align-items:flex-start;"><span style="font-size:.72rem;color:var(--text-lighter);font-weight:600;flex-shrink:0;margin-top:1px;">${label}</span><span>${txt}</span></div>` : '';
    insightEl.style.display = txt ? '' : 'none';
  }

  // 手机端：卡片式
  if (isMobile) {
    const mobileWrap = document.getElementById('historyMobileWrap');
    if (mobileWrap) {
      canvas.parentElement.style.display = 'none';
      mobileWrap.style.display = '';
      renderHistoryMobile(mobileWrap, quarters, values);
      return;
    }
  } else {
    // 桌面端：恢复 canvas
    const mobileWrap = document.getElementById('historyMobileWrap');
    if (mobileWrap) mobileWrap.style.display = 'none';
    canvas.parentElement.style.display = '';
  }

  // ── 桌面折线图（带 hover tooltip）──
  const ctx = canvas.getContext('2d');
  const W = Math.max(300, canvas.parentElement.clientWidth - 32);
  canvas.width = W; canvas.height = 360;
  const pad = {top:36,right:32,bottom:54,left:88};
  const w=W-pad.left-pad.right, h=360-pad.top-pad.bottom;
  const {minV, maxV} = historyRange(values);
  const range = maxV - minV || 1;
  ctx.clearRect(0,0,W,360);

  // 网格线
  ctx.strokeStyle='#e5e7eb'; ctx.lineWidth=0.5;
  for (let i=0;i<=5;i++) {
    const y=pad.top+(h/5)*i;
    ctx.beginPath(); ctx.moveTo(pad.left,y); ctx.lineTo(W-pad.right,y); ctx.stroke();
    const v=maxV-((maxV-minV)/5)*i;
    const label = historyMoney(v, 1);
    ctx.fillStyle='#9ca3af'; ctx.font='10.5px -apple-system,sans-serif'; ctx.textAlign='right';
    ctx.fillText(label,pad.left-8,y+4);
  }

  // X轴标签 — 按年显示
  const shownYears = new Set();
  quarters.forEach((q,i)=>{
    const yr = q.split(' ')[0];
    if (shownYears.has(yr)) return;
    shownYears.add(yr);
    const x=pad.left+historyX(quarters,i)*w;
    ctx.fillStyle='#9ca3af'; ctx.font='10px -apple-system,sans-serif'; ctx.textAlign='center';
    ctx.fillText(yr,x,pad.top+h+18);
  });

  const gX=i=>pad.left+historyX(quarters,i)*w;
  const gY=v=>pad.top+h-((v-minV)/range)*h;

  const grad=ctx.createLinearGradient(0,pad.top,0,pad.top+h);
  grad.addColorStop(0,'rgba(30,58,95,0.18)'); grad.addColorStop(1,'rgba(30,58,95,0.01)');
  for (const indices of historySegments(quarters)) {
    const first = indices[0], last = indices[indices.length-1];
    ctx.beginPath(); ctx.moveTo(gX(first),gY(values[first]));
    indices.slice(1).forEach(i=>ctx.lineTo(gX(i),gY(values[i])));
    ctx.strokeStyle='#1e3a5f'; ctx.lineWidth=2.5; ctx.lineJoin='round'; ctx.stroke();
    ctx.lineTo(gX(last),pad.top+h); ctx.lineTo(gX(first),pad.top+h); ctx.closePath();
    ctx.fillStyle=grad; ctx.fill();
  }

  // 标注大幅变动点（>25%）
  for (let i=1;i<values.length;i++) {
    const chg = historyChange(quarters, values, i);
    if (Math.abs(chg) > 0.25) {
      const x=gX(i), y=gY(values[i]);
      ctx.beginPath(); ctx.arc(x,y,7,0,Math.PI*2);
      ctx.fillStyle=chg>0?'rgba(22,163,74,0.15)':'rgba(220,38,38,0.12)'; ctx.fill();
      ctx.strokeStyle=chg>0?'#16a34a':'#dc2626'; ctx.lineWidth=1.5; ctx.stroke();
      // 箭头
      ctx.fillStyle=chg>0?'#16a34a':'#dc2626'; ctx.font='bold 9px -apple-system,sans-serif'; ctx.textAlign='center';
      ctx.fillText(chg>0?'▲':'▼',x,y+(chg>0?-10:14));
    }
  }

  // 普通数据点
  values.forEach((v,i)=>{
    const x=gX(i),y=gY(v);
    const chg = historyChange(quarters, values, i);
    if (Math.abs(chg) > 0.25) return; // 大变动点已画
    ctx.beginPath(); ctx.arc(x,y,3.5,0,Math.PI*2); ctx.fillStyle='#1e3a5f'; ctx.fill();
    ctx.strokeStyle='#fff'; ctx.lineWidth=1.5; ctx.stroke();
  });

  // 最新值标注
  const last=values.length-1;
  const lastLabel = historyMoney(values[last]);
  ctx.fillStyle='#1e3a5f'; ctx.font='bold 12px -apple-system,sans-serif'; ctx.textAlign='right';
  ctx.fillText(lastLabel,gX(last)-8,gY(values[last])-8);

  // ── Hover tooltip ──
  const existingTooltip = document.getElementById('hcTooltip');
  if (existingTooltip) existingTooltip.remove();
  const tooltip = document.createElement('div');
  tooltip.id = 'hcTooltip';
  tooltip.style.cssText = 'position:absolute;display:none;background:var(--navy,#1e3a5f);color:#f7f5f0;padding:8px 12px;border-radius:8px;font-size:.75rem;pointer-events:none;z-index:50;line-height:1.7;box-shadow:0 4px 16px rgba(0,0,0,.25);min-width:120px;';
  canvas.parentElement.style.position = 'relative';
  canvas.parentElement.appendChild(tooltip);

  canvas.onmousemove = (e) => {
    const rect = canvas.getBoundingClientRect();
    const mx = (e.clientX - rect.left) * (canvas.width / rect.width);
    const idx = values.reduce((best, _, i) => Math.abs(gX(i)-mx) < Math.abs(gX(best)-mx) ? i : best, 0);
    if (idx < 0 || idx >= quarters.length) { tooltip.style.display='none'; return; }
    const v = values[idx], q = quarters[idx];
    const delta = historyChange(quarters, values, idx);
    const chgStr = delta === null ? '' : `<span style="color:${delta > 0 ? '#4ade80' : delta < 0 ? '#f87171' : '#d1d5db'}">${lang==='zh'?'环比':'QoQ'} ${delta>0?'+':''}${(delta*100).toFixed(1)}%</span>`;
    tooltip.innerHTML = `<div style="font-weight:600;margin-bottom:2px;">${q}</div><div>${historyMoney(v, 3)} ${chgStr}</div>`;
    const cx = gX(idx), cy = gY(v);
    const scaleX = rect.width / canvas.width, scaleY = rect.height / canvas.height;
    tooltip.style.left = Math.max(0, Math.min(cx * scaleX + 12, rect.width - 210)) + 'px';
    tooltip.style.top = (cy * scaleY - 16) + 'px';
    tooltip.style.display = '';
  };
  canvas.onmouseleave = () => { tooltip.style.display='none'; };
}

// ── TIMELINE ──
async function renderTimelineTable() {
  const container = document.getElementById('timelineCanvas');
  if (!data) return;
  if (data.history?.verification?.status === 'unverified') {
    container.innerHTML = `<p style="color:var(--text-lighter);">${lang === 'en' ? 'A holdings timeline requires dated historical snapshots.' : '持仓时间轴需要可核对日期的历史快照，暂不展示。'}</p>`;
    renderHKHoldings();
    return;
  }
  const hdata = data.history?.holdings;
  if (!hdata || Object.keys(hdata).length === 0) {
    container.innerHTML = '<p style="text-align:center;color:var(--text-lighter);padding:40px;">历史持仓数据加载中…</p>';
    return;
  }
  const quarters = Object.keys(hdata).sort();
  const latest = quarters[quarters.length - 1];
  const isHK = investor === 'webb';
  const isEn = lang === 'en';
  const tickerInfo = {};
  for (const q of quarters) {
    for (const h of hdata[q]) {
      if (!(h.shares > 0)) continue;
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

  let html = '<div class="table-wrap tl-table-wrap"><table style="width:100%;font-size:.82rem;table-layout:fixed;"><colgroup><col style="width:38%"><col style="width:18%"><col style="width:18%"><col style="width:26%"></colgroup><thead><tr><th>'+t('thCompany')+'</th><th>'+t('thFirst')+'</th><th>'+t('thLast')+'</th><th>'+t('thStatus')+'</th></tr></thead><tbody>';
  entries.forEach(e => {
    if (e.active && e.curShares > 0 && e.maxShares > 0) {
      const ratio = (e.curShares / e.maxShares * 100).toFixed(0);
      const s = e.curShares === e.maxShares
        ? `<span style="color:#10b981;">${isEn ? 'At peak shares' : '持股处于历史峰值'}</span>`
        : `<span style="color:#f59e0b;">${isEn ? `Shares at ${ratio}% of peak` : `持股为峰值的 ${ratio}%`}</span>`;
      const shareInfo = ratio < 100 ? `<br><span style="font-size:.68rem;color:var(--text-lighter);">最高 ${fmtNum(e.maxShares)} → 当前 ${fmtNum(e.curShares)}</span>` : '';
      e.shareInfo = s + shareInfo;
    } else {
      e.shareInfo = '<span style="color:var(--text-lighter);">—</span>';
    }
    let status;
    if (e.gaps.length > 0) {
      const soldQ = e.gaps[0];
      const boughtQ = e.gaps[e.gaps.length - 1];
      const afterGap = quarters[quarters.indexOf(boughtQ) + 1];
      status = `<span style="color:#f59e0b;font-weight:600;">◐ ${soldQ} ${isEn?'No holding disclosed':'未披露持仓'}</span><br><span style="font-size:.68rem;color:var(--text-lighter);">→ ${afterGap} 重新买入（空窗${e.gaps.length}季）</span>`;
    } else if (e.active) {
      status = '<span style="color:#10b981;font-weight:600;">● 持有中</span>';
    } else {
      // 已清仓 — 尝试显示估算盈亏
      const ep = (prices?.exitPerf || {})[e.ticker];
      let exitTag = '';
      if (ep && ep.entryPrice && ep.exitPrice) {
        const chg = ep.changePct;
        const col  = chg >= 0 ? '#10b981' : '#ef4444';
        const sign = chg >= 0 ? '+' : '';
        const entryLabel = isEn ? 'Entry' : '建仓';
        const exitLabel  = isEn ? 'Exit'  : '清仓';
        exitTag = `<div style="margin-top:4px;font-size:.65rem;color:var(--text-lighter);line-height:1.6;">
          <span style="color:var(--text-lighter);">${entryLabel} ~$${ep.entryPrice}</span>
          <span style="margin:0 3px;">→</span>
          <span style="color:var(--text-lighter);">${exitLabel} ~$${ep.exitPrice}</span>
          <span style="margin-left:4px;font-weight:700;color:${col};">${sign}${chg}%</span>
          <span style="margin-left:3px;font-size:.6rem;color:var(--text-lighter);">(${isEn?'est.':'估算'})</span>
        </div>`;
      }
      status = '<span style="color:var(--text-lighter);">○ ' + (isEn ? 'Exited' : '已清仓') + '</span>' + exitTag;
    }
    html += `<tr>
      <td class="stock-cell"><span class="ticker-line">${fmtTicker(e.ticker)}</span><span class="name-line">${cn(e.name, e)}</span><span class="sector-badge">${ts(e.sector)}</span><span style="display:block;font-size:.65rem;color:var(--text-lighter);margin-top:2px;">${e.qCount} 季</span></td>
      <td style="white-space:nowrap">${e.first}</td>
      <td style="white-space:nowrap">${e.last}</td>
      <td>${status}<div style="margin-top:4px">${e.shareInfo}</div></td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  html += '<div style="font-size:.68rem;color:var(--text-lighter);margin-top:8px;">● 持有中 = 当前仍在组合内 | ○ 已清仓 = 历史持仓 | ◐ 卖出后重新买入 = 有中断</div>';
  if (isHK) html += '<div style="font-size:.68rem;color:var(--text-lighter);margin-top:4px;">⚠️ Webb 港股持仓数据来源于公开权益披露，非 13F 报告</div>';
  container.innerHTML = html;
  renderHKHoldings();
}

function hkEvidenceView(holding) {
  const records = (holding.verified_disclosures || []).filter(r =>
    !r.superseded_by &&
    /^\d{4}-\d{2}-\d{2}$/.test(r.event_date || '') &&
    typeof r.shares === 'number' && Number.isFinite(r.shares) && r.shares >= 0 &&
    typeof r.pct === 'number' && Number.isFinite(r.pct) && r.pct >= 0 && r.pct <= 100 &&
    r.filing_ref && /^https:\/\/di\.hkex\.com\.hk\//.test(r.source_url || '') &&
    (!r.form_url || /^https:\/\/di\.hkex\.com\.hk\//.test(r.form_url))
  ).sort((a,b) => a.event_date.localeCompare(b.event_date) || (a.filing_date || '').localeCompare(b.filing_date || '') || a.filing_ref.localeCompare(b.filing_ref));
  return {records, first: records[0], latest: records[records.length - 1], status: '当前持仓未核实'};
}
function hkEscape(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
async function renderHKHoldings() {
  const container = document.getElementById('hkHoldingsTable');
  if (!container) return;
  const requestedInvestor = investor;
  try {
    const cfg = INVESTOR_CFG_BY_ID[investor];
    const hkUrl = cfg ? cfg.hkFile : null;
    if (!hkUrl) { container.innerHTML = '<p style="color:var(--text-lighter);padding:16px;">暂无港股持仓数据。</p>'; return; }
    const resp = await fetch(hkUrl + '?t=' + Math.floor(Date.now()/300000));
    if (!resp.ok) throw new Error('HK disclosures unavailable');
    const hk = await resp.json();
    if (investor !== requestedInvestor) return;
    const audit = hk.audit;
    const checked = audit?.checkedAt ? `最近自动检查：${hkEscape(audit.checkedAt.replace('T', ' ').replace('Z', ' UTC'))}` : '等待首次自动核验';
    const result = !audit ? '' : audit.status === 'checked' ? '已完成本轮已配置主体检索' : '部分来源未能核实，保留此前证据';
    const empty = audit?.status === 'checked' ? '本轮未检索到匹配主体的公开多头权益披露，不等于没有港股持仓。' : '暂无已核实的港股披露；来源未完成检查时不能判断是否持有。';
    container.innerHTML = `
      <p style="font-size:.75rem;color:var(--text-lighter);">${checked} · ${result}</p>
      <div style="overflow-x:auto;"><table style="width:100%;font-size:.82rem;"><thead><tr>
        <th>代码</th><th>公司</th><th>行业</th><th>披露主体</th><th>已核实记录起点</th><th>最后核实记录</th><th>该次披露持股</th><th>当前状态</th><th>说明与来源</th>
      </tr></thead><tbody>
      ${(hk.holdings || []).map(h=>{
        const evidence = hkEvidenceView(h), r = evidence.latest;
        const quantity = r ? `${r.shares.toLocaleString('en-US')}股 (${r.pct}%，${hkEscape(r.share_class || '原披露类别')})` : '待核实';
        const source = r ? `<br><a href="${hkEscape(r.form_url || r.source_url)}" target="_blank" rel="noopener noreferrer">港交所 ${hkEscape(r.filing_ref)}</a>` : '';
        const history = evidence.records.length ? `<details><summary>已核实历史（${evidence.records.length}条）</summary>${[...evidence.records].reverse().map(record => `<div style="padding:5px 0;border-bottom:1px solid var(--border);">${record.event_date} · ${hkEscape(record.entity)}<br>${record.shares.toLocaleString('en-US')}股 / ${record.pct}% · ${hkEscape(record.share_class || '原披露类别')}<br><a href="${hkEscape(record.form_url || record.source_url)}" target="_blank" rel="noopener noreferrer">${hkEscape(record.filing_ref)}</a></div>`).join('')}</details>` : '';
        const notes = h.evidence_schema === 2 ? h.notes : '历史记录尚未逐项核实；旧状态、峰值及日期不能作为当前持仓依据。';
        return `<tr>
          <td>${hkEscape(fmtTicker(h.ticker))}</td><td>${hkEscape(cn(h.name, h))}</td>
          <td>${hkEscape(h.sector)}</td><td style="font-size:.75rem;">${hkEscape(r?.entity || h.entity)}</td>
          <td>${evidence.first?.event_date || '待核实'}</td><td>${r?.event_date || '待核实'}</td>
          <td style="font-size:.75rem;">${quantity}</td><td><span class="tag">${evidence.status}</span></td>
          <td style="max-width:300px;font-size:.75rem;line-height:1.5;">${hkEscape(notes)}${source}${history}</td>
        </tr>`;
      }).join('')}
      </tbody></table></div>
      ${!(hk.holdings || []).length ? `<p>${empty}</p>` : ''}
      <div style="font-size:.68rem;color:var(--text-lighter);margin-top:8px;padding:6px 12px;background:#f8f6f0;border-radius:6px;">历史披露不代表当前持仓。同一权益可能由个人和受控公司分别申报，不能相加。已核实记录起点不等于建仓时间，最后核实记录不保证是最近一次披露；缺失记录不代表清仓或低于5%。</div>`;
  } catch(e) {
    if (investor === requestedInvestor) container.innerHTML = '<p style="color:var(--text-lighter);">港股数据加载失败</p>';
  }
}

function switchTab(name) {
  document.body?.classList?.toggle('spin-research', ['spinoff','spinoff_us'].includes(name));
  ['current','changes','history','homework','spinoff','spinoff_us','game'].forEach(t=>{
    document.getElementById('tab-'+t).classList.toggle('d-none',t!==name);
  });
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{
    b.classList.toggle('active',['current','changes','history','homework','spinoff','spinoff_us','game'][i]===name);
  });
  if (name==='changes') { renderChanges(); renderInsights(); }
  if (name==='history') { renderHistoryChart(); renderTimelineTable(); }
  if (name==='homework') { renderHomework(); }
  if (name==='spinoff') { renderSpinoff(); }
  if (name==='spinoff_us') { renderSpinoffUS(); }
  if (name==='game') { renderGame(); }
}

const GAME_URL = 'game/v2/index.html';
let _gameLoaded = false;
function renderGame() {
  const el = document.getElementById('gameContent');
  if (!el || _gameLoaded) return;
  const isEn = lang === 'en';
  el.innerHTML = `
    <div style="margin-bottom:14px;">
      <h3 style="font-family:var(--serif);font-size:1.05rem;color:var(--navy);margin:0 0 6px;font-weight:700;">
        ${isEn?'🎴 The Munger Trials: The $2 Trillion Answer':'🎴 格罗茨的试炼：2万亿的答案'}
      </h3>
      <p style="font-size:.8rem;color:var(--text-light);line-height:1.6;margin:0;">
        ${isEn
          ? 'An interactive narrative based on Charlie Munger\'s 1996 speech. Play as an 1884 entrepreneur and derive the mental models behind the Coca-Cola empire through five trials.'
          : '一个改编自查理·芒格 1996 年演讲的互动叙事。扮演 1884 年的创业者，通过五个试炼亲手推导出可口可乐帝国背后的思维模型。'}
      </p>
      <a href="${GAME_URL}" target="_blank" rel="noopener"
         style="display:inline-block;margin-top:8px;font-size:.75rem;color:var(--gold);text-decoration:none;">
        ${isEn?'↗ Open in new tab':'↗ 在新标签页打开'}
      </a>
    </div>
    <div style="position:relative;width:100%;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:#f5f0e6;box-shadow:0 4px 16px rgba(0,0,0,0.08);overscroll-behavior:contain;touch-action:pan-y;">
      <iframe src="${GAME_URL}"
        style="width:100%;height:78vh;min-height:560px;border:0;display:block;"
        allow="autoplay; fullscreen"
        loading="lazy"
        title="Munger Trials Game"></iframe>
    </div>`;
  _gameLoaded = true;
}

let _homeworkCache = null;
async function renderHomework() {
  const el = document.getElementById('homeworkContent');
  if (!el) return;
  if (_homeworkCache) { el.innerHTML = _homeworkCache; return; }
  el.innerHTML = '<p style="padding:24px;color:var(--text-lighter);">加载中...</p>';

  // 预计算架构：全部 MOS/共识人数/打分排序/加减仓标签 计算已搬到后端
  // enrich_metadata.py 的 _build_value_screen()，CI 每次跑完写入 value_screen.json。
  // 前端只需 fetch 这一个静态文件即可拿到已排好序的候选股数组，
  // 不再需要并行拉取 24 个原始持仓+价格文件、也不用在浏览器里重复计算 MOS/打分，
  // 彻底避免前端 JS 与后端 Python 两份独立实现的逻辑漂移风险（此前已发生过两次）。
  let candidates = [];
  let nearMissMap = {};
  const isEn2 = lang === 'en';
  try {
    const vs = await fetch('value_screen.json?t=' + Math.floor(Date.now()/300000)).then(r => r.ok ? r.json() : null);
    if (!vs) throw new Error('value_screen.json fetch failed');
    // investors 数组里的 name/nameEn 已由后端算好，这里按当前语言态选择展示哪个
    candidates = (vs.candidates || []).map(c => ({
      ...c,
      investors: (c.investors || []).map(inv => ({ ...inv, name: isEn2 ? inv.nameEn : inv.name })),
    }));
    nearMissMap = {};
    for (const [tk, list] of Object.entries(vs.nearMissMap || {})) {
      nearMissMap[tk] = list.map(nm => ({ ...nm, investor: isEn2 ? nm.investorEn : nm.investor }));
    }
  } catch (e) {
    console.warn('value_screen.json load failed', e);
    el.innerHTML = `<p style="padding:32px;text-align:center;color:var(--text-lighter);">${isEn2?'Failed to load value screen data':'价值筛选数据加载失败'}</p>`;
    return;
  }

  candidates.forEach(c => {
    const hasNew = c.investors.some(inv => inv.chg === 'new');
    const hasAdded = c.investors.some(inv => inv.chg === 'added');
    const rowChgTag = hasNew
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(59,130,246,0.12);border:1px solid rgba(59,130,246,0.3);border-radius:4px;font-size:.6rem;color:#3b82f6;font-weight:600;margin-top:3px;">🆕 ${isEn2?'New':'新开仓'}</span>`
      : hasAdded
      ? `<span style="display:inline-flex;align-items:center;gap:2px;padding:1px 6px;background:rgba(16,185,129,0.1);border:1px solid rgba(16,185,129,0.25);border-radius:4px;font-size:.6rem;color:#10b981;font-weight:600;margin-top:3px;">📈 ${isEn2?'Added':'加仓'}</span>`
      : '';
    // Penalize if ALL investors are trimming (net exit signal) — 仅用于标签显示，排序已在后端 _build_value_screen() 完成
    const allTrimming = c.investors.length > 0 && c.investors.every(inv => inv.chg === 'trimmed');
    c._allTrimming = allTrimming;
  });
  // 注意：candidates 已由后端 value_screen.json 按打分排序好，前端不再重新 sort

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
    const nmList = nearMissMap[c.ticker] || [];
    const nmTitle = nmList.map(nm => `${nm.investor} ${nm.mos}%`).join(', ');
    const nmBadge = nmList.length
      ? `<span title="${nmTitle}" style="cursor:help;display:inline-flex;align-items:center;gap:2px;padding:2px 6px;background:rgba(148,163,184,0.12);border:1px dashed rgba(148,163,184,0.4);border-radius:8px;font-size:.55rem;color:var(--text-lighter);font-weight:600;white-space:nowrap;">+${nmList.length} ${isEn2?'watching':'观察中'}</span>`
      : '';
    const invCellHtml = `<div style="display:flex;flex-wrap:wrap;align-items:center;gap:4px;">${consensusPrefix}${invBadges}${nmBadge}</div>`;
    const invMobileHtml = `<div style="display:flex;flex-wrap:wrap;align-items:center;gap:3px;margin-top:4px;">${consensusPrefix}${invBadgesCompact}${nmBadge}</div>`;
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

  // 跨投资者 AI 总结（预生成 homework_summary.json：逐股点评 + 整体归纳）
  let hwAiHtml = '';
  try {
    const hwSum = await fetch('homework_summary.json?t=' + Math.floor(Date.now()/300000)).then(r => r.ok ? r.json() : null).catch(()=>null) || {};
    const localOverall = aiMatchingEntry('value',aiValueSource(candidates));
    hwSum.overallSummary=localOverall?.summary || aiValueFallback(candidates);
    if (hwSum && (hwSum.overallSummary || (hwSum.stockNotes && hwSum.stockNotes.length))) {
      const tierColor = t => t === '深度折价' ? '#059669' : (t === '中等折价' ? '#d97706' : '#6b7280');
      const tierColorEn = { '深度折价':'Deep discount', '中等折价':'Moderate discount', '轻度折价':'Shallow discount' };
      const chgLabelEn = { '本季新开仓':'New this quarter', '本季加仓':'Added this quarter', '本季减仓':'Trimmed this quarter', '仓位未变':'Unchanged' };
      const noteRows = (hwSum.stockNotes || []).map(n => {
        const holderHtml = (n.holders || []).map(h => {
          const wLabel = h.weight >= 0.5 ? `${h.weight}%${isEn2?' position':'仓位'}` : (isEn2?'tiny position (<0.5%)':'极小仓位(<0.5%)');
          let holdLabel;
          if (h.reentry && h.hold_quarters) {
            holdLabel = isEn2
              ? `re-entered ${h.reentry_quarter}, held ${h.hold_years}y (exited ${h.exit_quarter})`
              : `本轮${h.reentry_quarter}重建仓后持有${h.hold_years}年(此前${h.exit_quarter}清仓过)`;
          } else if (h.hold_quarters) {
            holdLabel = `${isEn2?'held':'持有'} ${h.hold_years}${isEn2?'y':'年'}`;
          } else {
            holdLabel = isEn2?'new entry':'首次建仓';
          }
          const trendSuffix = h.trend === 'accumulating'
            ? (isEn2 ? ', accumulating 3q' : '，近3季连续加仓')
            : h.trend === 'reducing'
              ? (isEn2 ? ', reducing 3q' : '，近3季连续减仓')
              : '';
          const chgCn = h.chg==='new'?'本季新开仓':h.chg==='added'?'本季加仓':h.chg==='trimmed'?'本季减仓':'仓位未变';
          const chgTxt = isEn2 ? chgLabelEn[chgCn] : chgCn;
          const chgColor = h.chg==='new'?'#3b82f6':h.chg==='added'?'#10b981':h.chg==='trimmed'?'#ef4444':'var(--text-lighter)';
          return `<span>${h.investor}<span style="color:var(--text-lighter);">（${wLabel}，${holdLabel}${trendSuffix}，</span><span style="color:${chgColor};font-weight:600;">${chgTxt}</span><span style="color:var(--text-lighter);">）</span></span>`;
        }).join(isEn2?'; ':'；');
        const tierTxt = isEn2 ? tierColorEn[n.mosTier] : n.mosTier;
        const verdictTxt = isEn2 ? n.verdictEn : n.verdict;
        const verdictHtml = verdictTxt ? `<div style="margin-top:4px;color:var(--text);">${verdictTxt}</div>` : '';
        return `<div style="padding:8px 0;border-bottom:1px solid rgba(148,163,184,0.12);font-size:.76rem;line-height:1.7;">
          <div style="margin-bottom:2px;">
            <strong style="color:var(--text);">${cn(n.name, n)} (${fmtTicker(n.ticker)})</strong>
            <span style="color:var(--text-lighter);"> · ${ts(n.sector)} · </span>
            <span style="color:${tierColor(n.mosTier)};font-weight:600;">${isEn2?'MOS':'安全边际'} ${n.mos}% (${tierTxt})</span>
            <span style="color:var(--text-lighter);"> · ${isEn2?'Cost':'成本'} $${n.buy} ${isEn2?'vs Price':'现价'} $${n.price}</span>
          </div>
          <div style="color:var(--text-light);">${holderHtml}</div>
          ${verdictHtml}
        </div>`;
      }).join('');
      const overallHtml = hwSum.overallSummary ? `<div style="margin-top:10px;padding-top:10px;border-top:1px dashed rgba(99,102,241,0.3);font-size:.8rem;line-height:1.75;color:var(--text);"><strong style="color:#6366f1;">${isEn2?'Overall':'整体归纳'}：</strong>${aiEscape(hwSum.overallSummary)}</div>` : '';
      const droppedOutHtml = (hwSum.droppedOut && hwSum.droppedOut.length) ? `<div style="margin-top:8px;padding-top:8px;border-top:1px dashed rgba(148,163,184,0.25);font-size:.72rem;line-height:1.6;color:var(--text-lighter);"><strong style="color:var(--text-light);">${isEn2?'Dropped from list':'本轮跌出'}：</strong>${hwSum.droppedOut.map(d => `${fmtTicker(d.ticker)}${isEn2?'':`（${d.name}）`}${d.prevMos!=null?` — ${isEn2?'prev MOS':'上轮安全边际'} ${d.prevMos}%`:''}`).join(isEn2?'; ':'；')}</div>` : '';
      hwAiHtml = `<div style="margin-bottom:20px;padding:14px 16px;background:linear-gradient(135deg,rgba(99,102,241,0.05),rgba(139,92,246,0.05));border:1px solid rgba(99,102,241,0.15);border-radius:10px;">
        <div style="font-size:.68rem;color:#6366f1;font-weight:700;margin-bottom:6px;">✨ AI ${isEn2?'Per-Stock Notes':'逐股解读'}</div>
        ${noteRows}
        ${overallHtml}
        ${droppedOutHtml}
        <div style="margin-top:8px;font-size:.62rem;color:var(--text-lighter);">${isEn2?'Generated':'生成于'} ${hwSum.generatedAt ? new Date(hwSum.generatedAt).toLocaleString(isEn2?'en-US':'zh-CN') : ''} · ${isEn2?'For reference only, not investment advice.':'仅供参考，不构成投资建议。'}</div>
      </div>`;
    }
  } catch(e) { /* 静默降级 */ }

  el.innerHTML = `
    <div style="margin-bottom:16px;padding:12px 16px;background:rgba(212,168,83,0.08);border:1px solid rgba(212,168,83,0.2);border-radius:8px;">
      <p style="font-size:.8rem;color:var(--text-light);line-height:1.6;">
        📋 <strong style="color:var(--gold);">${isEn2?'Value Picks':'抄作业单'}</strong> &mdash;
        ${isEn2?'Stocks with MOS &ge; 10% held by tracked investors. Sorted by consensus + MOS + recent activity (🆕 new / 📈 added). Click an investor badge to view full portfolio.':'所有投资者持仓中安全边际 &ge; 10% 的标的。按多人共识 + 安全边际 + 最近动态（🆕新开仓 / 📈加仓）综合排序。点击投资者名称可跳转完整持仓。'}
      </p>
    </div>
    ${hwAiHtml}
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
async function renderSpinoff() { return renderSpinoffDashboard('hk'); }
async function renderSpinoffUS() { return renderSpinoffDashboard('us'); }

function updateInvestorContent() {
  var en = lang === 'en', isP = investor === 'pabrai', isD = investor === 'duan', isT = investor === 'tepper', isW = investor === 'webb', isB = investor === 'buffett', isA = investor === 'akre', isG = investor === 'greenberg', isK = investor === 'klarman', isAck = investor === 'ackman', isAb = investor === 'abrams', isBk = investor === 'berkowitz', isHw = investor === 'hawkins';
  // Hero
  var ht = document.querySelector('[data-i18n="heroTitle"]');
  if (ht) ht.textContent = isB ? (en?'Buffett 13F Tracker':'巴菲特 13F 持仓追踪') : (isW ? (en?'David Webb HK Holdings':'大卫·韦伯 港股持仓') : (isP ? (en?'Pabrai 13F Tracker':'帕伯莱 13F 持仓追踪') : (isD ? (en?'Duan Yongping 13F Tracker':'段永平 13F 持仓追踪') : (isT ? (en?'David Tepper 13F Tracker':'大卫·泰珀 13F 持仓追踪') : (isA ? (en?'Chuck Akre 13F Tracker':'查克·阿克雷 13F 持仓追踪') : (isG ? (en?'Glenn Greenberg 13F Tracker':'格伦·格林伯格 13F 持仓追踪') : (isK ? (en?'Seth Klarman 13F Tracker':'塞斯·克拉曼 13F 持仓追踪') : (isAck ? (en?'Bill Ackman 13F Tracker':'比尔·阿克曼 13F 持仓追踪') : (isAb ? (en?'David Abrams 13F Tracker':'大卫·艾布拉姆斯 13F 持仓追踪') : (isBk ? (en?'Bruce Berkowitz 13F Tracker':'布鲁斯·伯科威茨 13F 持仓追踪') : (isHw ? (en?'Mason Hawkins 13F Tracker':'梅森·霍金斯 13F 持仓追踪') : (en?'Li Lu 13F Tracker':'李录 13F 持仓追踪'))))))))))));
  var hsub = document.querySelector('.hero-title .sub');
  if (hsub) hsub.textContent = isB ? (en ? 'Berkshire Hathaway · SEC 13F · Largest 13F Filer' : '伯克希尔·哈撒韦 · SEC 13F · 最大 13F 申报人') : (isW ? (en ? 'Webb-site.com · HKEX Disclosures · Activist Investor' : 'Webb-site.com · 港股披露 · 维权投资者') : (isP ? (en ? 'Dalal Street, LLC — Tracking Master Moves' : 'Dalal Street, LLC — 学习大师持仓变化') : (isD ? (en ? 'H&H International Investment · Value Investing' : 'H&H International Investment · 价值投资') : (isT ? (en ? 'Appaloosa LP · SEC 13F · Macro & Concentrated Bets' : 'Appaloosa LP · SEC 13F · 宏观与集中持仓') : (isA ? (en ? 'Akre Capital Management · Compounding Machines' : 'Akre Capital Management · 复利机器') : (isG ? (en ? 'Brave Warrior Advisors · Concentrated Value' : 'Brave Warrior Advisors · 集中价值投资') : (isK ? (en ? 'Baupost Group · SEC 13F · Margin of Safety' : 'Baupost Group · SEC 13F · 安全边际') : (isAck ? (en ? 'Pershing Square · SEC 13F · Activist Investing' : 'Pershing Square · SEC 13F · 维权投资') : (isAb ? (en ? 'Abrams Capital · SEC 13F · Ultra-Concentrated Value' : 'Abrams Capital · SEC 13F · 极度集中价值投资') : (isBk ? (en ? 'Fairholme Capital · SEC 13F · Concentrated Real Assets' : 'Fairholme Capital · SEC 13F · 集中实物资产') : (isHw ? (en ? 'Southeastern Asset Management · SEC 13F · Intrinsic Value' : 'Southeastern Asset Management · SEC 13F · 企业内在价值') : (en ? 'Himalaya Capital — Tracking Master Moves' : 'Himalaya Capital Management — 学习大师持仓变化'))))))))))));
  // Quote
  var qb = document.querySelector('.quote-block blockquote');
  if (qb) qb.textContent = isB
    ? (en?'"Be fearful when others are greedy, and greedy when others are fearful."':'"别人贪婪时我恐惧，别人恐惧时我贪婪。"')
    : (isP)
    ? (en?'"Heads I win, tails I don\u2019t lose much."':'"正面我赢，反面我也输不了多少。"')
    : (isD ? (en?'"Buying stocks is buying companies."':'"买股票就是买公司。"') : (isT ? (en?'"The best time to buy is when there\u2019s blood in the streets."':'"最好的买入时机是街头流血时。"') : (isW ? (en?'"Sunlight is the best disinfectant."':'"阳光是最好的消毒剂。"') : (isA ? (en?'"The key to investing is to find a business that\u2019s a compounding machine, and then let it compound."':'"投资的关键是找到一台复利机器，然后让它持续复利。"') : (isG ? (en?'"We look for companies that generate high returns on capital, have strong competitive positions, and are run by good people."':'"我们寻找资本回报率高、竞争优势强、由优秀人才经营的企业。"') : (isK ? (en?'"Investors should recognize that Wall Street forecasters exist to make astrologers look good."':'"投资者应该意识到，华尔街的预测家存在的意义，只是为了让占星师显得靠谱。"') : (isAck ? (en?'"I only want to be in businesses that are simple, predictable, free-cash-flow generative."':'"我只想投资于简单、可预测、能产生自由现金流的企业。"') : (isAb ? (en?'"Concentrate on a small number of ideas you understand deeply, and size positions accordingly."':'"集中于少数你真正深入理解的想法，并据此确定仓位大小。"') : (isBk ? (en?'"Investing is about putting a small amount of money at risk to make a lot of money."':'"投资就是用少量资金承担风险，以赚取巨大回报。"') : (isHw ? (en?'"We seek to buy businesses at a significant discount to their intrinsic value."':'"我们寻求以显著低于内在价值的价格买入企业。"') : (en?'"The macro is what we must accept; the micro is what we can act on."':'"宏观是我们必须接受的，微观是我们有所作为的。"')))))))))));
  var qa = document.querySelector('.quote-block .attr');
  if (qa) qa.textContent = isB
    ? (en?'— Warren Buffett, Berkshire Hathaway Annual Letter':'— 沃伦·巴菲特，伯克希尔·哈撒韦年度信')
    : (isP)
    ? '— Mohnish Pabrai, The Dhandho Investor'
    : (isD ? (en?'— Duan Yongping, Xueqiu (大道无形我有型)':'— 段永平，雪球（大道无形我有型）') : (isT ? (en?'— David Tepper, Appaloosa Management':'— 大卫·泰珀，Appaloosa Management') : (isW ? (en?'— David Webb, Webb-site.com':'— 大卫·韦伯，Webb-site.com') : (isA ? (en?'— Chuck Akre':'— 查克·阿克雷') : (isG ? (en?'— Glenn Greenberg':'— 格伦·格林伯格') : (isK ? (en?'— Seth Klarman, Baupost Group':'— 塞斯·克拉曼，Baupost Group') : (isAck ? (en?'— Bill Ackman, Pershing Square':'— 比尔·阿克曼，Pershing Square') : (isAb ? (en?'— David Abrams, Abrams Capital':'— 大卫·艾布拉姆斯，Abrams Capital') : (isBk ? (en?'— Bruce Berkowitz, Fairholme Capital':'— 布鲁斯·伯科威茨，Fairholme Capital') : (isHw ? (en?'— Mason Hawkins, Southeastern Asset Management':'— 梅森·霍金斯，Southeastern Asset Management') : (en?'— Li Lu, Peking University, Dec 2024':'— 李录，北京大学演讲，2024年12月')))))))))));
  // Labels
  var al = document.getElementById('aboutLabel'); if (al) al.textContent = isB ? 'About Buffett' : (isW ? 'About Webb' : (isP ? (en?'About Pabrai':'关于帕伯莱') : (isD ? (en?'About Duan':'关于段永平') : (isT ? (en?'About Tepper':'关于泰珀') : (isA ? (en?'About Akre':'关于阿克雷') : (isG ? (en?'About Greenberg':'关于格林伯格') : (isK ? (en?'About Klarman':'关于克拉曼') : (isAck ? (en?'About Ackman':'关于阿克曼') : (isAb ? (en?'About Abrams':'关于艾布拉姆斯') : (isBk ? (en?'About Berkowitz':'关于伯科威茨') : (isHw ? (en?'About Hawkins':'关于霍金斯') : (en?'About Li Lu':'关于李录'))))))))))));
  var at = document.getElementById('aboutTitle'); if (at) at.innerHTML = isB
    ? (en?'Warren Buffett \u2014 The Oracle of Omaha':'沃伦·巴菲特 \u2014 奥马哈先知')
    : (isP)
    ? (en?'Mohnish Pabrai — Cloning & Dhandho':'Mohnish Pabrai — 从 Cloning 到 Dhandho')
    : (isD ? (en?"Duan Yongping \u2014 China\u2019s Buffett":'段永平 \u2014 中国巴菲特') : (isT ? (en?'David Tepper \u2014 Macro Bets & Distressed Debt':'大卫·泰珀 \u2014 宏观押注与困境债务') : (isW ? (en?'David Webb \u2014 The Activist Investor':'大卫·韦伯 \u2014 维权投资者') : (isA ? (en?'Chuck Akre \u2014 The Three-Legged Stool':'查克·阿克雷 \u2014 三条腿的凳子') : (isG ? (en?'Glenn Greenberg \u2014 Concentrated Value':'格伦·格林伯格 \u2014 集中价值投资') : (isK ? (en?'Seth Klarman \u2014 The Margin of Safety':'塞斯·克拉曼 \u2014 安全边际') : (isAck ? (en?'Bill Ackman \u2014 The Activist Investor':'比尔·阿克曼 \u2014 维权投资者') : (isAb ? (en?'David Abrams \u2014 The Silent Compounder':'大卫·艾布拉姆斯 \u2014 沉默的复利者') : (isBk ? (en?'Bruce Berkowitz \u2014 Concentrated Real Assets':'布鲁斯·伯科威茨 \u2014 集中实物资产') : (isHw ? (en?'Mason Hawkins \u2014 Intrinsic Value & Business Value':'梅森·霍金斯 \u2014 企业内在价值') : (en?'About Li Lu & Himalaya Capital':'关于李录与喜马拉雅资本')))))))))));
  var pl = document.getElementById('philLabel'); if (pl) pl.textContent = isB ? 'Philosophy' : (isW ? 'Philosophy' : (isP ? 'Dhandho' : (isD ? (en?'Philosophy':'投资理念') : (isT ? (en?'Philosophy':'投资理念') : (isA ? (en?'Philosophy':'投资理念') : (isG ? (en?'Philosophy':'投资理念') : (isK ? (en?'Philosophy':'投资理念') : (isAck ? (en?'Philosophy':'投资理念') : (isAb ? (en?'Philosophy':'投资理念') : (isBk ? (en?'Philosophy':'投资理念') : (isHw ? (en?'Philosophy':'投资理念') : (en?'Philosophy':'投资理念'))))))))))));
  var pt = document.getElementById('philTitle'); if (pt) pt.innerHTML = isB
    ? (en?'Philosophy \u2014 Value Investing Principles':'投资理念 \u2014 价值投资原则')
    : (isP)
    ? (en?'Philosophy \u2014 The Dhandho Way':'投资理念 \u2014 Dhandho 法')
    : (isD ? (en?'Philosophy \u2014 Buy Companies, Not Stocks':'投资理念 \u2014 买股票就是买公司') : (isT ? (en?'Philosophy \u2014 Macro Vision & Concentrated Bets':'投资理念 \u2014 宏观视野与集中押注') : (isW ? (en?'Philosophy \u2014 Activist Principles':'投资理念 \u2014 维权原则') : (isA ? (en?'Philosophy \u2014 Compounding Machines':'投资理念 \u2014 复利机器') : (isG ? (en?'Philosophy \u2014 Concentrated Value':'投资理念 \u2014 集中价值投资') : (isK ? (en?'Philosophy \u2014 Margin of Safety':'投资理念 \u2014 安全边际') : (isAck ? (en?'Philosophy \u2014 Simple, Predictable, Free Cash Flow':'投资理念 \u2014 简单、可预测、自由现金流') : (isAb ? (en?'Philosophy \u2014 Ultra-Concentrated Conviction':'投资理念 \u2014 极度集中的信念') : (isBk ? (en?'Philosophy \u2014 Concentrated Bets on Real Assets':'投资理念 \u2014 重仓实物资产') : (isHw ? (en?'Philosophy \u2014 Intrinsic Value & Deep Discount':'投资理念 \u2014 内在价值与深度折价') : (en?'Philosophy \u2014 Graham \u2192 Buffett \u2192 Munger \u2192 Li Lu':'投资理念 \u2014 格雷厄姆 \u2192 巴菲特 \u2192 芒格 \u2192 李录')))))))))));
  var rl = document.getElementById('readLabel'); if (rl) rl.textContent = isB ? 'Readings' : (isW ? 'Readings' : (isP ? (en?'Resources':'资源') : (isT ? (en?'Readings':'延伸阅读') : (isA ? (en?'Readings':'延伸阅读') : (isG ? (en?'Readings':'延伸阅读') : (isK ? (en?'Readings':'延伸阅读') : (isAck ? (en?'Readings':'延伸阅读') : (isAb ? (en?'Readings':'延伸阅读') : (isBk ? (en?'Readings':'延伸阅读') : (isHw ? (en?'Readings':'延伸阅读') : (en?'Readings':'延伸阅读')))))))))));
  var navAb = document.querySelector('[data-i18n="navAbout"]'); if (navAb) navAb.textContent = isB ? (en?'About Buffett':'关于巴菲特') : (isW ? (en?'About Webb':'关于韦伯') : (isP ? (en?'About Pabrai':'关于帕伯莱') : (isD ? (en?'About Duan':'关于段永平') : (isT ? (en?'About Tepper':'关于泰珀') : (isA ? (en?'About Akre':'关于阿克雷') : (isG ? (en?'About Greenberg':'关于格林伯格') : (isK ? (en?'About Klarman':'关于克拉曼') : (isAck ? (en?'About Ackman':'关于阿克曼') : (isAb ? (en?'About Abrams':'关于艾布拉姆斯') : (isBk ? (en?'About Berkowitz':'关于伯科威茨') : (isHw ? (en?'About Hawkins':'关于霍金斯') : (en?'About':'关于李录'))))))))))));
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
    } else if (isK) {
      rt.innerHTML = en
        ? '<p>Seth Klarman (b. 1957), founder and CEO of <strong>Baupost Group</strong>, one of the most respected value investors of his generation. Started Baupost in 1982 with $27M in seed capital from four families.</p><p>Author of <em>Margin of Safety</em> (1991), a book so sought-after in its out-of-print years that used copies sold for thousands of dollars \u2014 now considered a value-investing bible alongside Graham\'s work.</p><p>Klarman runs an extremely concentrated, low-turnover portfolio and keeps a notoriously low public profile, rarely giving interviews. Baupost is known for holding large cash positions when it can\'t find bargains, and for opportunistic bets in distressed debt and special situations.</p>'
        : '<p>塞斯·克拉曼（Seth Klarman），1957 年生，<strong>Baupost Group</strong> 创始人兼 CEO，是同代最受尊敬的价值投资者之一。1982 年以四个家族提供的 2700 万美元种子资金创立 Baupost。</p><p>著有《安全边际》（Margin of Safety，1991），该书绝版期间二手书曾被炒到数千美元，被视为继格雷厄姆之后的价值投资圣经。</p><p>克拉曼的持仓极度集中、换手率很低，本人极少公开露面或接受采访。Baupost 以在找不到便宜筹码时持有大量现金、并在困境债务和特殊情形中机会性下注而闻名。</p>';
    } else if (isAck) {
      rt.innerHTML = en
        ? '<p>Bill Ackman (b. 1966), founder and CEO of <strong>Pershing Square Capital Management</strong>, a New York-based hedge fund known for highly concentrated, activist positions in public companies.</p><p>Ackman built his reputation on bold, high-conviction bets \u2014 both long and short \u2014 and often pushes for board seats, management changes, or strategic shifts at the companies he invests in.</p><p>Pershing Square typically holds fewer than 12 positions at a time. Ackman is also known for his active presence on social media (X/Twitter), where he shares detailed investment theses and commentary on markets and public policy.</p>'
        : '<p>比尔·阿克曼（Bill Ackman），1966 年生，<strong>Pershing Square Capital Management</strong> 创始人兼 CEO，是一家总部位于纽约、以高度集中的维权式持仓闻名的对冲基金。</p><p>阿克曼以大胆的高确信度押注（做多与做空皆有）建立起自己的声誉，常常推动目标公司改选董事会、更换管理层或调整战略方向。</p><p>Pershing Square 通常同时持有不到 12 个仓位。阿克曼也活跃于社交媒体（X/Twitter），常公开分享详细的投资逻辑及对市场与公共政策的评论。</p>';
    } else if (isAb) {
      rt.innerHTML = en
        ? '<p>David Abrams (b. 1957), founder of <strong>Abrams Capital Management</strong>, is one of the most private and consistently successful value investors in the industry. He began his career as an analyst under Seth Klarman at Baupost Group before founding Abrams Capital in 1999.</p><p>Abrams runs an ultra-concentrated portfolio \u2014 often just 10-15 positions, with single names occasionally approaching 40% of assets \u2014 reflecting extremely high conviction backed by deep research.</p><p>He rarely gives interviews or public statements, and Abrams Capital\'s SEC 13F filings are one of the few public windows into his thinking. His approach closely mirrors the Baupost/Klarman tradition of patient, safety-margin-driven value investing.</p>'
        : '<p>大卫·艾布拉姆斯（David Abrams），1957 年生，<strong>Abrams Capital Management</strong> 创始人，是业内最为低调、同时长期业绩最稳健的价值投资者之一。他早年在 Baupost Group 师从塞斯·克拉曼担任分析师，1999 年创立 Abrams Capital。</p><p>艾布拉姆斯的持仓极度集中\u2014\u2014通常只有 10-15 个仓位，单一仓位有时接近资产的 40%，体现出经过深度研究后的极高确信度。</p><p>他极少接受采访或公开发言，SEC 13F 申报文件几乎是外界了解其思路的唯一窗口。他的投资风格深受 Baupost/克拉曼传统的影响：耐心等待，坚守安全边际。</p>';
    } else if (isBk) {
      rt.innerHTML = en
        ? '<p>Bruce Berkowitz (b. 1958), founder of <strong>Fairholme Capital Management</strong>, made his name running the Fairholme Fund to top-decile returns in the 2000s before a series of concentrated, contrarian bets defined his later career.</p><p>Berkowitz is best known for an extraordinarily concentrated position in <strong>The St. Joe Company (JOE)</strong>, a Florida real estate and land development company \u2014 a bet on the long-term value of undeveloped Florida panhandle land that at times has represented nearly 80% of his portfolio.</p><p>His investment philosophy centers on deep asset-value analysis and a willingness to hold a handful of high-conviction ideas for years, tolerating short-term volatility and skepticism from the market.</p>'
        : '<p>布鲁斯·伯科威茨（Bruce Berkowitz），1958 年生，<strong>Fairholme Capital Management</strong> 创始人，2000 年代凭借 Fairholme Fund 的顶尖业绩崭露头角，此后以一系列集中、逆向的重仓押注定义了自己的投资风格。</p><p>他最广为人知的是对 <strong>圣祖公司（The St. Joe Company, JOE）</strong>\u2014\u2014一家佛罗里达地产与土地开发公司\u2014\u2014的超高比例持仓，押注佛罗里达狹长地带未开发土地的长期价值，该仓位一度占其组合近 80%。</p><p>他的投资理念聚焦于深度资产价值分析，并愿意长年持有少数高确信度的想法，容忍短期波动和市场的质疑。</p>';
    } else if (isHw) {
      rt.innerHTML = en
        ? '<p>Mason Hawkins (b. 1945), co-founder and Chairman of <strong>Southeastern Asset Management</strong>, which he founded in 1975 and which manages the Longleaf Partners family of mutual funds.</p><p>Hawkins is a disciplined <strong>intrinsic value</strong> investor: he and his team estimate a business\'s appraised value as a private buyer would, then buy only at a significant discount (Southeastern targets buying at ~60% of appraised value) with a qualified management team in place.</p><p>Southeastern\'s style is close to deep-value, enterprise-value investing \u2014 look past headline multiples to underlying business and asset value \u2014 an approach with clear echoes of Li Lu\'s own value framework.</p>'
        : '<p>梅森·霍金斯（Mason Hawkins），1945 年生，<strong>Southeastern Asset Management</strong> 联合创始人兼董事长，1975 年创立该公司，旗下管理 Longleaf Partners 系列共同基金。</p><p>霍金斯是严格的<strong>企业内在价值</strong>投资者：他和团队像私人买家一样估算企业的评估价值，只在价格显著低于该价值时买入（Southeastern 的目标是以约 60% 的评估价值买入），同时要求公司具备称职的管理团队。</p><p>Southeastern 的风格接近深度价值与企业价值投资\u2014\u2014穿透报表倍数看底层业务与资产价值\u2014\u2014这一思路与李录本人的价值投资框架有明显的相通之处。</p>';
    } else {
      rt.innerHTML = en
        ? '<p>Li Lu (b. 1966), Chinese-American value investor, founder of Himalaya Capital. Moved to the US in 1989 and earned a BA, JD, and MBA simultaneously at Columbia University \u2014 a rare "triple degree" achievement.</p><p>Founded Himalaya Capital in 1997, focused on long-term value investing. Recommended BYD to Charlie Munger in 2002, leading to Berkshire\'s $230M investment in 2008. Munger once publicly praised him: "Li Lu is a genius, and we\'ve made a lot of money together."</p><p>Active in philanthropy through his humanitarian foundation, focused on human rights, education, and disaster relief.</p>'
        : '<p>李录（Li Lu），1966 年生于唐山，美籍华裔价值投资者，喜马拉雅资本创始人。1989 年赴美，在哥伦比亚大学同时取得经济学学士、法学博士 (JD) 和 MBA 三个学位——哥大罕见的“三学位”成就者。</p><p>1997 年创立喜马拉雅资本，专注长期价值投资。2002 年向查理·芒格推荐比亚迪，后由伯克希尔 2008 年投资 2.3 亿美元。芒格曾公开赞誉：“李录是一个天才，我们一起赚了很多钱。”</p><p>除投资外，李录也热心公益，设立了人道主义基金会，关注人权、教育和救灾。</p>';
    }
  }
  // Timeline
  // 先移除静态时间线元素的 data-i18n 属性，防止 applyI18n 把它覆盖回李录版本
  document.querySelectorAll('.ref-grid .timeline [data-i18n]').forEach(function(el){ el.removeAttribute('data-i18n'); });
  var tl = document.querySelector('.ref-grid .timeline');
  if (tl) {
    function tlItem(year, zh, en_) { return '<div class="tl-item"><div class="tl-year">'+year+'</div><div class="tl-text">'+(en?en_:zh)+'</div></div>'; }
    var now = en ? 'Present' : '至今';
    if (isP) {
      tl.innerHTML = [
        tlItem('1964','出生于印度','Born in India'),
        tlItem('1999','100 万美元起步投资','Started investing with $1M'),
        tlItem('2007','出版 The Dhandho Investor','Published The Dhandho Investor'),
        tlItem('2007','65 万美元拍下巴菲特午餐','Paid $650K for Buffett lunch'),
        tlItem(now,'管理 Pabrai Funds + 博客','Managing Pabrai Funds + blog'),
      ].join('');
    } else if (isD) {
      tl.innerHTML = [
        tlItem('1961','出生于江西南昌','Born in Nanchang, Jiangxi'),
        tlItem('1982','浙江大学无线电工程专业','Radio Engineering, Zhejiang Univ.'),
        tlItem('1989','创立小霸王电子工业公司','Founded Subor Electronics'),
        tlItem('1995','创立步步高电子','Founded BBK Electronics'),
        tlItem('2001','退出一线，移居美国','Retired from ops, moved to US'),
        tlItem('2002','结识巴菲特，开始投资','Met Buffett, began investing'),
        tlItem('2006','62 万美元拍下巴菲特午餐（与黄峥）','$620K Buffett lunch (with Huang Zheng)'),
        tlItem('~2011','开始大量买入苹果','Began heavy buying of Apple'),
        tlItem(now,'管理 H&H International Investment','Managing H&H International Investment'),
      ].join('');
    } else if (isT) {
      tl.innerHTML = [
        tlItem('1957','出生于匹兹堡','Born in Pittsburgh'),
        tlItem('~1980','卡内基梅隆大学，后获 MBA','Carnegie Mellon, then MBA'),
        tlItem('~1982','加入高盛，从事垃圾债券交易','Goldman Sachs, junk bond trading'),
        tlItem('1993','创立 Appaloosa Management','Founded Appaloosa Management'),
        tlItem('2009','金融危机中大胆买入银行股','Bought distressed bank stocks, ~$7B profit'),
        tlItem(now,'管理 Appaloosa LP，宏观押注与集中持仓','Managing Appaloosa LP, macro & concentrated bets'),
      ].join('');
    } else if (isB) {
      tl.innerHTML = [
        tlItem('1930','出生于内布拉斯加州奥马哈','Born in Omaha, Nebraska'),
        tlItem('1951','师从格雷厄姆，哥伦比亚 MBA','Studied under Graham, Columbia MBA'),
        tlItem('1956','创立 Buffett Partnership','Founded Buffett Partnership'),
        tlItem('1965','收购 Berkshire Hathaway','Acquired Berkshire Hathaway'),
        tlItem('1988','开始大量买入可口可乐','Began buying Coca-Cola heavily'),
        tlItem('2016','开始买入苹果，迄今最大持仓','Started buying Apple, now largest position'),
        tlItem(now,'管理伯克希尔·哈撒韦，$263B 组合','Managing Berkshire Hathaway, $263B portfolio'),
      ].join('');
    } else if (isW) {
      tl.innerHTML = [
        tlItem('1965','出生于英国','Born in UK'),
        tlItem('~1990','牛津大学数学系','Mathematics, Oxford University'),
        tlItem('1998','创立 Webb-site.com','Founded Webb-site.com'),
        tlItem('2003','获选港交所独立非执行董事','Elected independent director of HKEX'),
        tlItem('2017','发布"谜网"报告，揭露 50 只不可投资港股','Published "Network of Influence" report'),
        tlItem('2018','确诊前列腺癌','Diagnosed with prostate cancer'),
        tlItem('2026','去世，享年 60 岁','Passed away, aged 60'),
      ].join('');
    } else if (isA) {
      tl.innerHTML = [
        tlItem('1996','创立 Akre Capital Management','Founded Akre Capital Management'),
        tlItem('1997','开始管理 FBR Focus Fund','Began managing FBR Focus Fund'),
        tlItem('2000','互联网泡沫中坚持价值投资','Stayed the course during dot-com bust'),
        tlItem('2009','重组 Akre Capital，推出 Akre Focus Fund','Relaunched as Akre Focus Fund'),
        tlItem('2021','管理资产规模突破 150 亿美元','AUM surpassed $15B'),
        tlItem(now,'集中持有约 20 只高质量复利企业','~20 high-quality compounders'),
      ].join('');
    } else if (isG) {
      tl.innerHTML = [
        tlItem('1984','加入 Chieftain Capital，师从 John Shapiro','Joined Chieftain Capital under John Shapiro'),
        tlItem('1990','成为 Chieftain 合伙人','Became partner at Chieftain'),
        tlItem('2000','互联网泡沫中坚持价值投资','Stayed disciplined through dot-com bubble'),
        tlItem('2009','金融危机中逆势大举买入','Bought aggressively during financial crisis'),
        tlItem('2010','创立 Brave Warrior Advisors','Founded Brave Warrior Advisors'),
        tlItem(now,'管理约 40 亿美元，集中于高质量企业','Managing ~$4B, concentrated in quality compounders'),
      ].join('');
    } else if (isK) {
      tl.innerHTML = [
        tlItem('1957','出生','Born'),
        tlItem('1979','康乃尔大学经济学学士，后获哈佛 MBA','Economics degree from Cornell, later Harvard MBA'),
        tlItem('1982','创立 Baupost Group，初始资金 2700 万美元','Founded Baupost Group with $27M seed capital'),
        tlItem('1991','出版《安全边际》','Published Margin of Safety'),
        tlItem('2008','金融危机中机会性买入困境资产','Opportunistic buying during 2008 financial crisis'),
        tlItem(now,'管理 Baupost Group，持仓集中且换手率极低','Managing Baupost Group, highly concentrated & low turnover'),
      ].join('');
    } else if (isAck) {
      tl.innerHTML = [
        tlItem('1966','出生于纽约','Born in New York'),
        tlItem('1992','哈佛大学 MBA','Harvard MBA'),
        tlItem('2004','创立 Pershing Square Capital Management','Founded Pershing Square Capital Management'),
        tlItem('2012','公开做空 Herbalife，引发市场争议','Public short of Herbalife sparks market debate'),
        tlItem('2020','疫情对冲交易获利约 26 亿美元','COVID hedge trade nets ~$2.6B profit'),
        tlItem(now,'管理 Pershing Square，极度集中的维权式持仓','Managing Pershing Square, ultra-concentrated activist positions'),
      ].join('');
    } else if (isAb) {
      tl.innerHTML = [
        tlItem('1957','出生','Born'),
        tlItem('~1980s','在 Baupost Group 师从塞斯·克拉曼任分析师','Analyst under Seth Klarman at Baupost Group'),
        tlItem('1999','创立 Abrams Capital Management','Founded Abrams Capital Management'),
        tlItem(now,'持仓极度集中，单一仓位有时接近 40%','Ultra-concentrated portfolio, single positions sometimes near 40%'),
      ].join('');
    } else if (isBk) {
      tl.innerHTML = [
        tlItem('1958','出生','Born'),
        tlItem('1997','创立 Fairholme Capital Management','Founded Fairholme Capital Management'),
        tlItem('2000s','Fairholme Fund 业绩位居行业前列','Fairholme Fund posts top-decile returns'),
        tlItem('~2010','开始重仓圣祖公司 (JOE)','Began building concentrated position in The St. Joe Company (JOE)'),
        tlItem(now,'JOE 持仓占组合接近 80%','JOE position nears 80% of portfolio'),
      ].join('');
    } else if (isHw) {
      tl.innerHTML = [
        tlItem('1945','出生','Born'),
        tlItem('1975','创立 Southeastern Asset Management','Co-founded Southeastern Asset Management'),
        tlItem('1987','推出 Longleaf Partners 基金系列','Launched the Longleaf Partners mutual fund family'),
        tlItem(now,'坚持企业内在价值投资，定义性买入价格占评估价值约 60%','Disciplined intrinsic-value investing, targets buying at ~60% of appraised value'),
      ].join('');
    } else {
      tl.innerHTML = [
        tlItem('1966','出生于唐山，十岁时亲历唐山大地震','Born in Tangshan; survived the 1976 earthquake at age 10'),
        tlItem('1985','考入南京大学','Entered Nanjing University'),
        tlItem('1989','赴美，入读哥伦比亚大学','Emigrated to US, enrolled at Columbia'),
        tlItem('1996','哥大 BA/JD/MBA 三学位','Columbia BA/JD/MBA triple degree'),
        tlItem('1997','创立喜马拉雅资本','Founded Himalaya Capital'),
        tlItem('2002','向芒格推荐比亚迪','Introduced BYD to Charlie Munger'),
        tlItem(now,'持续管理喜马拉雅资本','Continues managing Himalaya Capital'),
      ].join('');
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
    } else if (isK) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Never overpay. Always buy at a significant discount to conservatively estimated intrinsic value.</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>Hold Cash When Idle</h4><p>Willing to hold large cash positions rather than force capital into mediocre ideas.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Absolute Return Focus</h4><p>Prioritize capital preservation over relative benchmark performance.</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>Deep Fundamental Research</h4><p>Rigorous, independent analysis before every position.</p></div><div class="phil-card"><div class="icon">\ud83e\udde0</div><h4>Contrarian Discipline</h4><p>Willing to be early and alone; avoid crowd psychology.</p></div><div class="phil-card"><div class="icon">\ud83e\udd10</div><h4>Low Public Profile</h4><p>Rarely gives interviews; lets results speak.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>永不多付：只在价格显著低于保守估计的内在价值时买入。</p></div><div class="phil-card"><div class="icon">\ud83d\udcb0</div><h4>无机会时持现</h4><p>宁愿持有大量现金，也不强行将资金投入平庸的机会。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>绝对收益优先</h4><p>以保全资本为优先，而非追求相对于基准的表现。</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>深入的基本面研究</h4><p>每一仓位背后都是严谨、独立的分析。</p></div><div class="phil-card"><div class="icon">\ud83e\udde0</div><h4>逆向自律</h4><p>愿意提前、孤独地下注，避免集体心理。</p></div><div class="phil-card"><div class="icon">\ud83e\udd10</div><h4>保持低调</h4><p>很少接受采访，让业绩自己说话。</p></div>';
    } else if (isAck) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Simple, Predictable Businesses</h4><p>Free-cash-flow generative companies with durable competitive advantages.</p></div><div class="phil-card"><div class="icon">\ud83d\udce2</div><h4>Activist Engagement</h4><p>Push for board seats, management changes, and strategic shifts.</p></div><div class="phil-card"><div class="icon">\ud83e\udde9</div><h4>Ultra-Concentrated</h4><p>Fewer than 12 positions at a time; each backed by deep conviction.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Asymmetric Hedges</h4><p>Uses options and credit hedges to protect against tail risk.</p></div><div class="phil-card"><div class="icon">\ud83d\udcac</div><h4>Public Thesis-Sharing</h4><p>Openly shares detailed investment cases on social media.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Patient Capital</h4><p>Willing to hold for years for a thesis to play out.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>简单、可预测的企业</h4><p>寻找能产生自由现金流、拥有持久竞争优势的公司。</p></div><div class="phil-card"><div class="icon">\ud83d\udce2</div><h4>维权介入</h4><p>推动改选董事会、更换管理层或调整战略方向。</p></div><div class="phil-card"><div class="icon">\ud83e\udde9</div><h4>极度集中</h4><p>同时持仓通常不超过 12 个，每个仓位背后都是极高确信度。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>非对称对冲</h4><p>使用期权与信用对冲工具防范尾部风险。</p></div><div class="phil-card"><div class="icon">\ud83d\udcac</div><h4>公开分享逻辑</h4><p>乐于在社交媒体上详细分享投资逻辑。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>耐心资本</h4><p>愿意为一个逻辑充分展开而持有年。</p></div>';
    } else if (isAb) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Ultra-Concentration</h4><p>10-15 positions; single names can approach 40% of assets.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Baupost-style discipline: buy well below intrinsic value.</p></div><div class="phil-card"><div class="icon">\ud83e\udd10</div><h4>Extreme Privacy</h4><p>Almost no public statements; 13F filings are the main public signal.</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>Deep, Independent Research</h4><p>Each position backed by exhaustive due diligence.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long Holding Periods</h4><p>Low turnover, patient compounding.</p></div><div class="phil-card"><div class="icon">\ud83d\udcaa</div><h4>High Conviction Sizing</h4><p>Position size scales directly with confidence in the thesis.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>极度集中</h4><p>通常仅 10-15 个仓位，单一仓位有时接近资产的 40%。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>延续 Baupost 风格：买入价显著低于内在价值。</p></div><div class="phil-card"><div class="icon">\ud83e\udd10</div><h4>极度低调</h4><p>几乎不对外发声，13F 申报是外界了解其思路的主要窗口。</p></div><div class="phil-card"><div class="icon">\ud83d\udd0d</div><h4>深入、独立的研究</h4><p>每个仓位背后都有穷尽的尽调支撑。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期持有</h4><p>换手率低，耐心复利。</p></div><div class="phil-card"><div class="icon">\ud83d\udcaa</div><h4>信念决定仓位大小</h4><p>仓位大小与对逻辑的确信程度直接相关。</p></div>';
    } else if (isBk) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83c\udfe0</div><h4>Real Asset Value</h4><p>Deep analysis of underlying land and real-estate asset value.</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>Extreme Concentration</h4><p>Willing to size a single conviction position near 80% of the portfolio.</p></div><div class="phil-card"><div class="icon">\ud83e\udded</div><h4>Contrarian Patience</h4><p>Holds through years of skepticism when the thesis is intact.</p></div><div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>Asset-Based Valuation</h4><p>Values businesses on replacement/asset value, not just earnings multiples.</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>Margin of Safety</h4><p>Buys only when price is well below appraised asset value.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Multi-Decade Horizon</h4><p>Land and real-asset theses play out over decades, not quarters.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83c\udfe0</div><h4>实物资产价值</h4><p>深入分析底层土地与房地产资产价值。</p></div><div class="phil-card"><div class="icon">\ud83c\udfaf</div><h4>极度集中</h4><p>愿意将单一信念仓位押到接近组合的 80%。</p></div><div class="phil-card"><div class="icon">\ud83e\udded</div><h4>逆向耐心</h4><p>只要逻辑未变，即使年年遭质疑仍愿持有。</p></div><div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>资产导向估值</h4><p>以重置成本/资产价值估值，而不仅仅看盈余倍数。</p></div><div class="phil-card"><div class="icon">\ud83d\udee1\ufe0f</div><h4>安全边际</h4><p>仅在价格显著低于评估资产价值时买入。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>数十年视角</h4><p>土地与实物资产的逻辑需要数十年才能充分展现。</p></div>';
    } else if (isHw) {
      pg.innerHTML = en
        ? '<div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>Intrinsic Value Appraisal</h4><p>Estimate business value as a private buyer would.</p></div><div class="phil-card"><div class="icon">\ud83c\udff7\ufe0f</div><h4>Buy at ~60% of Value</h4><p>Target a significant discount to appraised intrinsic value.</p></div><div class="phil-card"><div class="icon">\ud83d\udc65</div><h4>Qualified Management</h4><p>Require capable, aligned management teams before investing.</p></div><div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>Enterprise Value Focus</h4><p>Look past headline multiples to underlying business and asset value.</p></div><div class="phil-card"><div class="icon">\ud83c\udf10</div><h4>Diversified Deep Value</h4><p>Broader portfolio (dozens of names) than most concentrated peers.</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>Long-Term Discipline</h4><p>Patient, multi-year holding periods for value to be realized.</p></div>'
        : '<div class="phil-card"><div class="icon">\ud83d\udcca</div><h4>内在价值评估</h4><p>像私人买家一样估算企业价值。</p></div><div class="phil-card"><div class="icon">\ud83c\udff7\ufe0f</div><h4>以约 60% 估值买入</h4><p>目标是以显著低于评估内在价值的价格买入。</p></div><div class="phil-card"><div class="icon">\ud83d\udc65</div><h4>管理层能力</h4><p>要求能干且与股东利益一致的管理团队。</p></div><div class="phil-card"><div class="icon">\ud83c\udfe2</div><h4>企业价值优先</h4><p>穿透报表倍数看底层业务与资产价值。</p></div><div class="phil-card"><div class="icon">\ud83c\udf10</div><h4>分散式深度价值</h4><p>比大部分集中型同行持有更广泛的组合（数十只股票）。</p></div><div class="phil-card"><div class="icon">\u23f3</div><h4>长期主义</h4><p>耐心持有多年，等待价值充分实现。</p></div>';
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
        ? '<a class="article-card" href="https://xueqiu.com/P/ZH2256330" target="_blank"><div class="year">Xueqiu</div><h4>\u5927\u9053\u65e0\u5f62\u6211\u6709\u578b</h4><p>Duan\u2019s Xueqiu portfolio & investment thoughts.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001759760&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings (H&H)</h4><p>View H&H International Investment SEC submissions.</p></a><a class="article-card" href="https://www.gelonghui.com/search?keyword=%E6%AE%B5%E6%B0%B8%E5%B9%B3" target="_blank"><div class="year">格隆汇</div><h4>\u6bb5\u6c38\u5e73\uff1a\u6295\u8d44\u5c31\u662f\u4e70\u516c\u53f8</h4><p>"Buying stocks is buying companies" \u2014 core philosophy explained.</p></a><a class="article-card" href="https://xueqiu.com/u/5819606876" target="_blank"><div class="year">Xueqiu</div><h4>\u6bb5\u6c38\u5e73\u96ea\u7403\u4e3b\u9875</h4><p>Duan Yongping\'s Xueqiu account \u2014 posts and Q&A.</p></a><a class="article-card" href="https://www.huxiu.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">Huxiu</div><h4>\u864e\u55c5 \u00b7 \u6bb5\u6c38\u5e73</h4><p>News and analysis about Duan Yongping.</p></a><a class="article-card" href="https://36kr.com/search/articles/%E6%AE%B5%E6%B0%B8%E5%B9%B3" target="_blank"><div class="year">36Kr</div><h4>36\u6c2a \u00b7 \u6bb5\u6c38\u5e73</h4><p>Business coverage of Duan Yongping and BBK ecosystem.</p></a>'
        : '<a class="article-card" href="https://xueqiu.com/P/ZH2256330" target="_blank"><div class="year">\u96ea\u7403</div><h4>\u5927\u9053\u65e0\u5f62\u6211\u6709\u578b</h4><p>\u6bb5\u6c38\u5e73\u5728\u96ea\u7403\u7684\u6295\u8d44\u7ec4\u5408\u4e0e\u601d\u8003\u3002</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001759760&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>\u5168\u90e8 13F \u539f\u59cb\u6587\u4ef6</h4><p>\u5728 SEC \u6570\u636e\u5e93\u67e5\u770b H&H International \u5168\u90e8\u63d0\u4ea4\u3002</p></a><a class="article-card" href="https://www.gelonghui.com/search?keyword=%E6%AE%B5%E6%B0%B8%E5%B9%B3" target="_blank"><div class="year">\u683c\u9686\u6c47</div><h4>\u6bb5\u6c38\u5e73\uff1a\u6295\u8d44\u5c31\u662f\u4e70\u516c\u53f8</h4><p>"\u4e70\u80a1\u7968\u5c31\u662f\u4e70\u516c\u53f8"\u2014\u2014\u6838\u5fc3\u6295\u8d44\u7406\u5ff5\u89e3\u8bfb\u3002</p></a><a class="article-card" href="https://xueqiu.com/u/5819606876" target="_blank"><div class="year">\u96ea\u7403\u4e3b\u9875</div><h4>\u6bb5\u6c38\u5e73\u96ea\u7403\u4e3b\u9875</h4><p>\u6bb5\u6c38\u5e73\u96ea\u7403\u8d26\u53f7\uff0c\u539f\u521b\u8d34\u6587\u4e0e\u95ee\u7b54\u3002</p></a><a class="article-card" href="https://www.huxiu.com/search?query=\u6bb5\u6c38\u5e73" target="_blank"><div class="year">\u864e\u55c5</div><h4>\u864e\u55c5 \u00b7 \u6bb5\u6c38\u5e73</h4><p>\u6bb5\u6c38\u5e73\u76f8\u5173\u65b0\u95fb\u4e0e\u5206\u6790\u3002</p></a><a class="article-card" href="https://36kr.com/search/articles/%E6%AE%B5%E6%B0%B8%E5%B9%B3" target="_blank"><div class="year">36\u6c2a</div><h4>36\u6c2a \u00b7 \u6bb5\u6c38\u5e73</h4><p>\u6bb5\u6c38\u5e73\u53ca\u6b65\u6b65\u9ad8\u7cfb\u5546\u4e1a\u62a5\u9053\u3002</p></a>';
    } else if (isT) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001656456&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings (Appaloosa)</h4><p>View Appaloosa LP SEC submissions.</p></a><a class="article-card" href="https://www.forbes.com/profile/david-tepper/" target="_blank"><div class="year">Forbes</div><h4>Forbes Profile</h4><p>David Tepper billionaire profile and net worth.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Tepper" target="_blank"><div class="year">Wikipedia</div><h4>David Tepper</h4><p>Biography, career, and investing philosophy.</p></a><a class="article-card" href="https://www.bloomberg.com/news/articles/2023-05-25/david-tepper-appaloosa-says-he-s-fully-invested-in-stocks" target="_blank"><div class="year">Bloomberg</div><h4>Tepper: "I\u2019m Fully Invested"</h4><p>Interview on market outlook and portfolio strategy.</p></a><a class="article-card" href="https://www.cnbc.com/david-tepper/" target="_blank"><div class="year">CNBC</div><h4>CNBC Coverage</h4><p>Latest news and interviews about David Tepper.</p></a><a class="article-card" href="https://www.businessinsider.com/search?q=david+tepper" target="_blank"><div class="year">Business Insider</div><h4>Tepper Archive</h4><p>Collection of articles and analysis.</p></a>'
        : '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001656456&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Appaloosa LP 全部提交。</p></a><a class="article-card" href="https://www.forbes.com/profile/david-tepper/" target="_blank"><div class="year">Forbes</div><h4>Forbes 富豪档案</h4><p>大卫·泰珀个人简介与净资产。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Tepper" target="_blank"><div class="year">Wikipedia</div><h4>大卫·泰珀</h4><p>生平、职业历程与投资哲学。</p></a><a class="article-card" href="https://www.bloomberg.com/news/articles/2023-05-25/david-tepper-appaloosa-says-he-s-fully-invested-in-stocks" target="_blank"><div class="year">Bloomberg</div><h4>泰珀："我全仓了"</h4><p>市场前景与组合策略访谈。</p></a><a class="article-card" href="https://www.cnbc.com/david-tepper/" target="_blank"><div class="year">CNBC</div><h4>CNBC 报道</h4><p>大卫·泰珀最新新闻与访谈。</p></a><a class="article-card" href="https://www.businessinsider.com/search?q=david+tepper" target="_blank"><div class="year">Business Insider</div><h4>泰珀文章集</h4><p>相关文章与分析合集。</p></a>';
    } else if (isB) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.berkshirehathaway.com/letters/letters.html" target="_blank"><div class="year">Letters</div><h4>Shareholder Letters</h4><p>All Berkshire Hathaway annual letters by Buffett.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Berkshire Hathaway SEC submissions.</p></a><a class="article-card" href="https://www.berkshirehathaway.com/" target="_blank"><div class="year">Official</div><h4>berkshirehathaway.com</h4><p>Official BRK website, letters, and more.</p></a><a class="article-card" href="https://www.amazon.com/Snowball-Warren-Buffett-Business/dp/0553384846" target="_blank"><div class="year">Book</div><h4>The Snowball</h4><p>Alice Schroeder\'s authorized biography of Buffett.</p></a><a class="article-card" href="https://www.cnbc.com/warren-buffett/" target="_blank"><div class="year">CNBC</div><h4>CNBC Buffett Archive</h4><p>News, interviews, and market commentary.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=berkshire+hathaway+annual+meeting" target="_blank"><div class="year">YouTube</div><h4>Annual Meeting Videos</h4><p>Woodstock for Capitalists — full meeting recordings.</p></a>'
        : '<a class="article-card" href="https://www.berkshirehathaway.com/letters/letters.html" target="_blank"><div class="year">股东信</div><h4>年度股东信全集</h4><p>巴菲特亲笔撰写的所有伯克希尔年度信。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001067983&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看伯克希尔全部提交。</p></a><a class="article-card" href="https://www.berkshirehathaway.com/" target="_blank"><div class="year">官网</div><h4>berkshirehathaway.com</h4><p>伯克希尔官网，股东信与公司信息。</p></a><a class="article-card" href="https://www.amazon.com/Snowball-Warren-Buffett-Business/dp/0553384846" target="_blank"><div class="year">书籍</div><h4>滚雪球</h4><p>艾丽斯·施罗德授权的巴菲特传记。</p></a><a class="article-card" href="https://www.cnbc.com/warren-buffett/" target="_blank"><div class="year">CNBC</div><h4>CNBC 巴菲特档案</h4><p>新闻、访谈与市场评论。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=berkshire+hathaway+annual+meeting" target="_blank"><div class="year">YouTube</div><h4>年度股东大会视频</h4><p>资本家的伍德斯托克——完整会议录像。</p></a>';
    } else if (isW) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://webb-site.com/" target="_blank"><div class="year">Official</div><h4>webb-site.com</h4><p>Webb\'s independent HK corporate governance platform.</p></a><a class="article-card" href="https://webb-site.com/database/" target="_blank"><div class="year">Database</div><h4>Webb-site Database</h4><p>Searchable database of HK-listed companies and directors.</p></a><a class="article-card" href="https://webb-site.com/articles/" target="_blank"><div class="year">Articles</div><h4>Enigma Network & Articles</h4><p>Webb\'s investigations and governance articles.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Webb_(activist)" target="_blank"><div class="year">Wikipedia</div><h4>David Webb</h4><p>Biography and career summary.</p></a><a class="article-card" href="https://www.reuters.com/" target="_blank"><div class="year">Reuters</div><h4>Reuters Coverage</h4><p>News about Webb\'s activism and passing.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=david+webb+hkex" target="_blank"><div class="year">YouTube</div><h4>Interviews & Talks</h4><p>Webb\'s public appearances and interviews.</p></a>'
        : '<a class="article-card" href="https://webb-site.com/" target="_blank"><div class="year">官网</div><h4>webb-site.com</h4><p>韦伯的独立港股企业管治平台。</p></a><a class="article-card" href="https://webb-site.com/database/" target="_blank"><div class="year">数据库</div><h4>Webb-site 数据库</h4><p>可搜索的港股公司和董事数据库。</p></a><a class="article-card" href="https://webb-site.com/articles/" target="_blank"><div class="year">文章</div><h4>谜网与文章合集</h4><p>韦伯的调查报道与管治分析文章。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Webb_(activist)" target="_blank"><div class="year">维基百科</div><h4>David Webb</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://www.reuters.com/" target="_blank"><div class="year">路透社</div><h4>路透社报道</h4><p>关于韦伯维权活动与逝世的新闻。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=david+webb+hkex" target="_blank"><div class="year">YouTube</div><h4>访谈与演讲</h4><p>韦伯的公开露面与访谈录像。</p></a>';
    } else if (isA) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.akrecapital.com/" target="_blank"><div class="year">Official</div><h4>akrecapital.com</h4><p>Official Akre Capital Management website.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001499406&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Akre Capital SEC submissions.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=chuck+akre+interview" target="_blank"><div class="year">YouTube</div><h4>Akre Interviews</h4><p>Chuck Akre on compounding machines and the three-legged stool.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Chuck_Akre" target="_blank"><div class="year">Wikipedia</div><h4>Chuck Akre</h4><p>Biography and career.</p></a><a class="article-card" href="https://www.validea.com/" target="_blank"><div class="year">Validea</div><h4>Three-Legged Stool</h4><p>Validea\'s analysis of the Akre framework.</p></a><a class="article-card" href="https://www.gurufocus.com/investor/chuck-akre" target="_blank"><div class="year">GuruFocus</div><h4>Akre Portfolio</h4><p>Current holdings and performance tracking.</p></a>'
        : '<a class="article-card" href="https://www.akrecapital.com/" target="_blank"><div class="year">官网</div><h4>akrecapital.com</h4><p>Akre Capital Management 官方网站。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001499406&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Akre Capital 全部提交。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=chuck+akre+interview" target="_blank"><div class="year">YouTube</div><h4>阿克雷访谈</h4><p>查克·阿克雷谈复利机器与三条腿的凳子。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Chuck_Akre" target="_blank"><div class="year">维基百科</div><h4>Chuck Akre</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://www.validea.com/" target="_blank"><div class="year">Validea</div><h4>三条腿的凳子</h4><p>Validea 对阿克雷投资框架的分析。</p></a><a class="article-card" href="https://www.gurufocus.com/investor/chuck-akre" target="_blank"><div class="year">GuruFocus</div><h4>阿克雷持仓</h4><p>当前持仓与表现追踪。</p></a>';
    } else if (isG) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.linkedin.com/company/brave-warrior-advisors" target="_blank"><div class="year">LinkedIn</div><h4>Brave Warrior Advisors</h4><p>Official LinkedIn page.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001495196&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Brave Warrior Advisors SEC submissions.</p></a><a class="article-card" href="https://www.gurufocus.com/investor/glenn-greenberg" target="_blank"><div class="year">GuruFocus</div><h4>Greenberg Profile</h4><p>Holdings history and performance analysis.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=glenn+greenberg+investor" target="_blank"><div class="year">YouTube</div><h4>Greenberg Interviews</h4><p>Glenn Greenberg on concentrated value investing.</p></a><a class="article-card" href="https://www.dataroma.com/m/home.php?g=gg" target="_blank"><div class="year">Dataroma</div><h4>Portfolio Tracker</h4><p>Brave Warrior 13F portfolio tracking.</p></a><a class="article-card" href="https://www.gurufocus.com/portfolio/brave-warrior-advisors" target="_blank"><div class="year">GuruFocus</div><h4>Current Portfolio</h4><p>Latest Brave Warrior holdings and allocation.</p></a>'
        : '<a class="article-card" href="https://www.linkedin.com/company/brave-warrior-advisors" target="_blank"><div class="year">LinkedIn</div><h4>Brave Warrior Advisors</h4><p>官方 LinkedIn 页面。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001495196&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Brave Warrior 全部提交。</p></a><a class="article-card" href="https://www.gurufocus.com/investor/glenn-greenberg" target="_blank"><div class="year">GuruFocus</div><h4>格林伯格档案</h4><p>持仓历史与表现分析。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=glenn+greenberg+investor" target="_blank"><div class="year">YouTube</div><h4>格林伯格访谈</h4><p>格伦·格林伯格谈集中价值投资。</p></a><a class="article-card" href="https://www.dataroma.com/m/home.php?g=gg" target="_blank"><div class="year">Dataroma</div><h4>组合追踪</h4><p>Brave Warrior 13F 组合追踪。</p></a><a class="article-card" href="https://www.gurufocus.com/portfolio/brave-warrior-advisors" target="_blank"><div class="year">GuruFocus</div><h4>当前持仓</h4><p>最新 Brave Warrior 持仓与配置。</p></a>';
    } else if (isK) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001061768&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Baupost Group SEC submissions.</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=BG" target="_blank"><div class="year">Dataroma</div><h4>Baupost Portfolio</h4><p>Holdings history and performance tracking.</p></a><a class="article-card" href="https://www.gurufocus.com/institution/Baupost+Group%2C+LLC" target="_blank"><div class="year">GuruFocus</div><h4>Baupost Profile</h4><p>Current holdings and portfolio analysis.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Seth_Klarman" target="_blank"><div class="year">Wikipedia</div><h4>Seth Klarman</h4><p>Biography, career, and investing philosophy.</p></a><a class="article-card" href="https://www.amazon.com/Margin-Safety-Value-Investment-Strategies/dp/0887305105" target="_blank"><div class="year">1991</div><h4>Margin of Safety</h4><p>Klarman\'s famous out-of-print value investing classic.</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=seth+klarman+interview" target="_blank"><div class="year">YouTube</div><h4>Rare Interviews</h4><p>Klarman\'s rare public talks and lectures.</p></a>'
        : '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001061768&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Baupost Group 全部提交。</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=BG" target="_blank"><div class="year">Dataroma</div><h4>Baupost 组合追踪</h4><p>持仓历史与表现追踪。</p></a><a class="article-card" href="https://www.gurufocus.com/institution/Baupost+Group%2C+LLC" target="_blank"><div class="year">GuruFocus</div><h4>Baupost 档案</h4><p>当前持仓与组合分析。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Seth_Klarman" target="_blank"><div class="year">维基百科</div><h4>塞斯·克拉曼</h4><p>生平、职业历程与投资哲学。</p></a><a class="article-card" href="https://www.amazon.com/Margin-Safety-Value-Investment-Strategies/dp/0887305105" target="_blank"><div class="year">1991</div><h4>安全边际</h4><p>克拉曼的经典绝版价值投资著作。</p></a><a class="article-card" href="https://www.youtube.com/results?search_query=seth+klarman+interview" target="_blank"><div class="year">YouTube</div><h4>罕见访谈</h4><p>克拉曼罕有的公开演讲与访谈。</p></a>';
    } else if (isAck) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://pershingsquareholdings.com/" target="_blank"><div class="year">Official</div><h4>Pershing Square Holdings</h4><p>Official investor relations site.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001336528&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Pershing Square Capital SEC submissions.</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=PSC" target="_blank"><div class="year">Dataroma</div><h4>Pershing Square Portfolio</h4><p>Holdings history and performance tracking.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Bill_Ackman" target="_blank"><div class="year">Wikipedia</div><h4>Bill Ackman</h4><p>Biography and career summary.</p></a><a class="article-card" href="https://x.com/BillAckman" target="_blank"><div class="year">X</div><h4>@BillAckman</h4><p>Ackman\'s public thesis-sharing and commentary.</p></a><a class="article-card" href="https://www.cnbc.com/bill-ackman/" target="_blank"><div class="year">CNBC</div><h4>CNBC Coverage</h4><p>Latest news and interviews about Bill Ackman.</p></a>'
        : '<a class="article-card" href="https://pershingsquareholdings.com/" target="_blank"><div class="year">官网</div><h4>Pershing Square Holdings</h4><p>官方投资者关系网站。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001336528&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Pershing Square 全部提交。</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=PSC" target="_blank"><div class="year">Dataroma</div><h4>Pershing Square 组合追踪</h4><p>持仓历史与表现追踪。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Bill_Ackman" target="_blank"><div class="year">维基百科</div><h4>比尔·阿克曼</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://x.com/BillAckman" target="_blank"><div class="year">X</div><h4>@BillAckman</h4><p>阿克曼公开分享投资逻辑与市场评论。</p></a><a class="article-card" href="https://www.cnbc.com/bill-ackman/" target="_blank"><div class="year">CNBC</div><h4>CNBC 报道</h4><p>比尔·阿克曼最新新闻与访谈。</p></a>';
    } else if (isAb) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001358706&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Abrams Capital Management SEC submissions.</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=AC" target="_blank"><div class="year">Dataroma</div><h4>Abrams Capital Portfolio</h4><p>Holdings history and performance tracking.</p></a><a class="article-card" href="https://www.gurufocus.com/institution/Abrams+Capital+Management%2C+LLC" target="_blank"><div class="year">GuruFocus</div><h4>Abrams Capital Profile</h4><p>Current holdings and portfolio analysis.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Abrams_(investor)" target="_blank"><div class="year">Wikipedia</div><h4>David Abrams</h4><p>Biography and career summary.</p></a>'
        : '<a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001358706&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Abrams Capital Management 全部提交。</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=AC" target="_blank"><div class="year">Dataroma</div><h4>Abrams Capital 组合追踪</h4><p>持仓历史与表现追踪。</p></a><a class="article-card" href="https://www.gurufocus.com/institution/Abrams+Capital+Management%2C+LLC" target="_blank"><div class="year">GuruFocus</div><h4>Abrams Capital 档案</h4><p>当前持仓与组合分析。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/David_Abrams_(investor)" target="_blank"><div class="year">维基百科</div><h4>大卫·艾布拉姆斯</h4><p>生平与职业概述。</p></a>';
    } else if (isBk) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://fairholmefunds.com/" target="_blank"><div class="year">Official</div><h4>fairholmefunds.com</h4><p>Official Fairholme Funds website.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001056831&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Fairholme Capital SEC submissions.</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=FC" target="_blank"><div class="year">Dataroma</div><h4>Fairholme Portfolio</h4><p>Holdings history and performance tracking.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Bruce_Berkowitz" target="_blank"><div class="year">Wikipedia</div><h4>Bruce Berkowitz</h4><p>Biography and career summary.</p></a><a class="article-card" href="https://www.cnbc.com/bruce-berkowitz/" target="_blank"><div class="year">CNBC</div><h4>CNBC Coverage</h4><p>News and interviews about Bruce Berkowitz.</p></a>'
        : '<a class="article-card" href="https://fairholmefunds.com/" target="_blank"><div class="year">官网</div><h4>fairholmefunds.com</h4><p>Fairholme Funds 官方网站。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001056831&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Fairholme Capital 全部提交。</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=FC" target="_blank"><div class="year">Dataroma</div><h4>Fairholme 组合追踪</h4><p>持仓历史与表现追踪。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Bruce_Berkowitz" target="_blank"><div class="year">维基百科</div><h4>布鲁斯·伯科威茨</h4><p>生平与职业概述。</p></a><a class="article-card" href="https://www.cnbc.com/bruce-berkowitz/" target="_blank"><div class="year">CNBC</div><h4>CNBC 报道</h4><p>布鲁斯·伯科威茨相关新闻与访谈。</p></a>';
    } else if (isHw) {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://www.southeasternasset.com/" target="_blank"><div class="year">Official</div><h4>southeasternasset.com</h4><p>Official Southeastern Asset Management website.</p></a><a class="article-card" href="https://www.longleafpartners.com/" target="_blank"><div class="year">Funds</div><h4>Longleaf Partners Funds</h4><p>Southeastern\'s mutual fund family managed by Hawkins\' team.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807985&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>All 13F Filings</h4><p>View Southeastern Asset Management SEC submissions.</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=SAM" target="_blank"><div class="year">Dataroma</div><h4>Southeastern Portfolio</h4><p>Holdings history and performance tracking.</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Mason_Hawkins" target="_blank"><div class="year">Wikipedia</div><h4>Mason Hawkins</h4><p>Biography and career summary.</p></a>'
        : '<a class="article-card" href="https://www.southeasternasset.com/" target="_blank"><div class="year">官网</div><h4>southeasternasset.com</h4><p>Southeastern Asset Management 官方网站。</p></a><a class="article-card" href="https://www.longleafpartners.com/" target="_blank"><div class="year">基金</div><h4>Longleaf Partners 基金</h4><p>霍金斯团队管理的共同基金系列。</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000807985&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>全部 13F 原始文件</h4><p>在 SEC 数据库查看 Southeastern Asset Management 全部提交。</p></a><a class="article-card" href="https://www.dataroma.com/m/holdings.php?m=SAM" target="_blank"><div class="year">Dataroma</div><h4>Southeastern 组合追踪</h4><p>持仓历史与表现追踪。</p></a><a class="article-card" href="https://en.wikipedia.org/wiki/Mason_Hawkins" target="_blank"><div class="year">维基百科</div><h4>梅森·霍金斯</h4><p>生平与职业概述。</p></a>';
    } else {
      rg.innerHTML = en
        ? '<a class="article-card" href="https://cdn.prod.website-files.com/5ef3c7300432b40ed865991a/67a4f75703627bd3a927077e_Global%20Value%20Investing%20in%20Our%20Era%20(2024-12-07).pdf" target="_blank"><div class="year">2024 PDF</div><h4>Global Value Investing in Our Era</h4><p>Peking University lecture on six core principles.</p></a><a class="article-card" href="https://acquirersmultiple.com/2025/04/li-lu-how-to-invest-during-turbulent-times/" target="_blank"><div class="year">2025</div><h4>How to Invest in Turbulent Times</h4><p>Macro vs micro, essence of wealth.</p></a><a class="article-card" href="https://roiss.substack.com/p/transcript-of-li-lu-and-bruce-greenwald" target="_blank"><div class="year">2021</div><h4>On Value Investing in China</h4><p>Conversation with Prof. Bruce Greenwald.</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001709323&type=13F" target="_blank"><div class="year">SEC</div><h4>All 13F Filings</h4><p>View original SEC submissions.</p></a><a class="article-card" href="https://www.himcap.com/" target="_blank"><div class="year">Official</div><h4>Himalaya Capital</h4><p>Official website of the firm.</p></a><a class="article-card" href="https://monkeyenroute.medium.com/book-review-civilization-modernization-value-investing-china-by-li-lu-22398102583c" target="_blank"><div class="year">Book</div><h4>Civilization & Investment</h4><p>Book review: Civilization, Modernization and China.</p></a>'
        : '<a class="article-card" href="https://cdn.prod.website-files.com/5ef3c7300432b40ed865991a/67a4f75703627bd3a927077e_Global%20Value%20Investing%20in%20Our%20Era%20(2024-12-07).pdf" target="_blank"><div class="year">2024 \u00b7 PDF</div><h4>\u6211\u4eec\u65f6\u4ee3\u7684\u5168\u7403\u4ef7\u503c\u6295\u8d44</h4><p>\u5317\u5927\u4e3b\u9898\u6f14\u8bb2\uff0c\u4ef7\u503c\u6295\u8d44\u516d\u5927\u6838\u5fc3\u539f\u5219\u3002</p></a><a class="article-card" href="https://acquirersmultiple.com/2025/04/li-lu-how-to-invest-during-turbulent-times/" target="_blank"><div class="year">2025 \u00b7 04</div><h4>\u52a8\u8361\u65f6\u671f\u5982\u4f55\u6295\u8d44</h4><p>\u5b8f\u89c2\u4e0e\u5fae\u89c2\u7684\u5e73\u8861\u3001\u8d22\u5bcc\u7684\u672c\u8d28\u3002</p></a><a class="article-card" href="https://roiss.substack.com/p/transcript-of-li-lu-and-bruce-greenwald" target="_blank"><div class="year">2021 \u00b7 04</div><h4>\u5bf9\u8bdd\u683c\u6797\u6c83\u5c14\u5fb7</h4><p>\u4e0e\u54e5\u5927\u4ef7\u503c\u6295\u8d44\u6743\u5a01\u7684\u5bf9\u8bdd\u5b9e\u5f55\u3002</p></a><a class="article-card" href="https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001709323&type=13F" target="_blank"><div class="year">SEC EDGAR</div><h4>\u5168\u90e8 13F \u539f\u59cb\u6587\u4ef6</h4><p>\u5728 SEC \u6570\u636e\u5e93\u67e5\u770b\u6240\u6709 13F\u3002</p></a><a class="article-card" href="https://www.himcap.com/" target="_blank"><div class="year">\u5b98\u7f51</div><h4>Himalaya Capital</h4><p>\u4e86\u89e3\u66f4\u591a\u6295\u8d44\u7406\u5ff5\u3002</p></a><a class="article-card" href="https://monkeyenroute.medium.com/book-review-civilization-modernization-value-investing-china-by-li-lu-22398102583c" target="_blank"><div class="year">\u4e66\u8bc4</div><h4>\u6587\u660e\u3001\u73b0\u4ee3\u5316\u4e0e\u6295\u8d44</h4><p>\u300a\u6587\u660e\u3001\u73b0\u4ee3\u5316\u4e0e\u4e2d\u56fd\u300b\u4e66\u8bc4\u3002</p></a>';
    }
  }
}

// ========== AUTO-INIT ==========
function renderAll() { try { renderSummary(); renderHoldings(); renderChanges(); renderInsights(); renderHistoryChart(); } catch(e) {} }

// 页面加载后静默拉取状态灯颜色（不弹抽屉）
async function initStatusDot(signal) {
  try {
    const r = await fetch('run_status.json?_=' + Date.now(), {cache: 'no-store', signal});
    if (!r.ok) throw new Error('Status unavailable');
    const statusData = await r.json();
    _runStatusData = statusData;
    updateStatusDot(statusData);
    if (data) renderInsights();
  } catch(e) { updateStatusDot(null); }
}

function runHealth(run, now = Date.now()) {
  if (!run) return {state: 'warn', label: lang === 'en' ? 'Update status unavailable' : '更新状态暂不可用'};
  const steps = Object.values(run.steps || {});
  if (steps.some(s => s.status === 'fail')) return {state: 'fail', label: lang === 'en' ? 'Some updates failed' : '部分更新失败'};
  const ts = Date.parse(run.completedAt || run.run_id);
  if (!Number.isFinite(ts) || now - ts > 36 * 3600000) return {state: 'warn', label: lang === 'en' ? 'Update record is stale' : '更新记录已过期，请检查自动更新'};
  if (steps.some(s => s.status === 'warn')) return {state: 'warn', label: lang === 'en' ? 'Partial update; see details' : '部分功能未完整更新，请查看详情'};
  if (run.schemaVersion !== 2) return {state: 'warn', label: lang === 'en' ? 'Older record; AI status unknown' : '旧版记录，未包含 AI 可用状态'};
  if (!run.completedAt || !steps.length) return {state: 'warn', label: lang === 'en' ? 'Update not completed' : '更新尚未完成'};
  return {state: 'ok', label: lang === 'en' ? 'Update completed' : '更新完成'};
}

function updateStatusDot(statusData) {
  const dot = document.getElementById('statusDot');
  if (!dot) return;
  const health = runHealth(statusData?.runs?.[0]);
  dot.classList.remove('ok', 'fail', 'warn');
  dot.classList.add(health.state);
  dot.title = health.label;
  dot.setAttribute('aria-label', health.label);
}

async function initApp() {
  applyLanguageLabels();
  // 先加载 investors.json（单一权威来源），再切换投资者，避免导航按钮/数据加载
  // 发生在 INVESTOR_CFG 为空时的竞态。
  await loadInvestorConfig();
  await switchInvestor('lilu');
  refreshAISupplements();
  initStatusDot();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}

// ========== STATUS DRAWER ==========
let _runStatusData = null;

function openStatusDrawer() {
  document.getElementById('statusOverlay').classList.add('open');
  document.getElementById('statusDrawer').classList.add('open');
  renderStatusDrawer();
}

function closeStatusDrawer() {
  document.getElementById('statusOverlay').classList.remove('open');
  document.getElementById('statusDrawer').classList.remove('open');
}

// ESC 关闭
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeStatusDrawer(); });

async function renderStatusDrawer() {
  const el = document.getElementById('statusDrawerBody');
  if (!el) return;
  el.innerHTML = '<p style="padding:16px 0;color:var(--text-lighter);font-size:.85rem;">加载中...</p>';

  let data;
  try {
    const r = await fetch('run_status.json?_=' + Date.now(), {cache: 'no-store'});
    if (!r.ok) throw new Error('not found');
    data = await r.json();
    _runStatusData = data;
  } catch(e) {
    el.innerHTML = `<div style="padding:16px 0;text-align:center;color:var(--text-lighter);">
      <p style="font-size:.9rem;margin-bottom:6px;">暂无更新记录</p>
      <p style="font-size:.78rem;">workflow 执行后会自动生成。</p>
    </div>`;
    return;
  }

  // 更新状态灯
  updateStatusDot(data);

  const runs = (data.runs || []).slice(0, 10); // 最多显示 10 次

  if (!runs.length) {
    el.innerHTML = '<p style="padding:24px;color:var(--text-lighter);">暂无运行记录。</p>';
    return;
  }

  const STEP_ORDER = [
    'lilu_13f','lilu_prices',
    'pabrai_13f','pabrai_prices',
    'duan_13f','duan_prices',
    'tepper_13f','tepper_prices',
    'buffett_13f','buffett_prices',
    'akre_greenberg_13f','akre_prices','greenberg_prices',
    'batch2_13f','klarman_prices','ackman_prices','abrams_prices','berkowitz_prices','hawkins_prices',
    'webb_prices','webb_holdings',
    'resolve_cusip','metadata','hk_disclosures','spinoff_hk','spinoff_us','spinoff_prices','greenblatt_notes',
  ];

  const STEP_LABELS = {
    lilu_13f:'李录 13F', lilu_prices:'李录 股价',
    pabrai_13f:'Pabrai 13F', pabrai_prices:'Pabrai 股价',
    duan_13f:'段永平 13F', duan_prices:'段永平 股价',
    tepper_13f:'Tepper 13F', tepper_prices:'Tepper 股价',
    buffett_13f:'巴菲特 13F', buffett_prices:'巴菲特 股价',
    akre_greenberg_13f:'Akre/Greenberg 13F',
    akre_prices:'Akre 股价', greenberg_prices:'Greenberg 股价',
    batch2_13f:'克拉曼/阿克曼/艾布拉姆斯/伯科威茨/霍金斯 13F',
    klarman_prices:'克拉曼 股价', ackman_prices:'阿克曼 股价',
    abrams_prices:'艾布拉姆斯 股价', berkowitz_prices:'伯科威茨 股价', hawkins_prices:'霍金斯 股价',
    webb_prices:'Webb 股价', webb_holdings:'Webb 港股持仓',
    resolve_cusip:'股票代码解析', spinoff_prices:'分拆股价刷新', greenblatt_notes:'格林布拉特点评',
    metadata:'元数据富化', hk_disclosures:'港股披露监控',
    spinoff_hk:'港股分拆', spinoff_us:'美股分拆',
  };

  function fmtTime(ts) {
    if (!ts) return '—';
    try {
      const d = new Date(ts);
      return d.toLocaleString('zh-CN', { timeZone: 'Asia/Shanghai', month:'2-digit', day:'2-digit', hour:'2-digit', minute:'2-digit' });
    } catch(e) { return ts.slice(0,16); }
  }

  function triggerBadge(trigger) {
    const label = trigger === 'workflow_dispatch' ? '手动触发' : trigger === 'push' ? '代码更新' : '定时任务';
    const color = trigger === 'workflow_dispatch' ? '#1d4ed8' : '#6b7280';
    return `<span style="font-size:.65rem;padding:2px 8px;border-radius:12px;background:${color}1a;color:${color};font-weight:600;border:1px solid ${color}33;">${label}</span>`;
  }

  function statusIcon(s) {
    if (!s) return '<span style="color:#9ca3af;font-size:.95rem;">—</span>';
    if (s === 'ok')   return '<span style="color:#15803d;font-size:.95rem;" title="成功">✓</span>';
    if (s === 'warn') return '<span style="color:#d97706;font-size:.85rem;" title="部分功能未更新">!</span>';
    if (s === 'skip') return '<span style="color:#d97706;font-size:.85rem;" title="跳过">↷</span>';
    return '<span style="color:#b91c1c;font-size:.95rem;" title="失败">✗</span>';
  }

  // 统计 ok/fail/skip 数量
  function runSummary(steps) {
    let ok=0, fail=0, skip=0, warn=0, total=0;
    Object.values(steps).forEach(s => {
      total++;
      if (s.status === 'ok') ok++;
      else if (s.status === 'skip') skip++;
      else if (s.status === 'warn') warn++;
      else fail++;
    });
    return { ok, fail, skip, warn, total };
  }

  let html = `
    <div style="margin-bottom:20px;">
      <h3 style="font-family:var(--serif);font-size:1.1rem;color:var(--navy);font-weight:600;margin-bottom:4px;">
        🔍 自动更新状态
      </h3>
      <p style="font-size:.8rem;color:var(--text-lighter);">显示最近 ${runs.length} 次 workflow 执行结果，每步骤标记成功 / 部分更新 / 失败 / 跳过。绿色表示更新完成，黄色表示降级、未完成或记录过期。</p>
    </div>`;

  runs.forEach((run, idx) => {
    const steps = run.steps || {};
    const { ok, fail, skip, warn, total } = runSummary(steps);
    // Freshness applies to the latest run; older cards describe their state at completion.
    const health = runHealth(run, idx === 0 ? Date.now() : Date.parse(run.completedAt || run.run_id));
    const borderColor = health.state === 'ok' ? '#15803d' : health.state === 'fail' ? '#b91c1c' : '#b45309';
    const bgBadge = `<span style="font-size:.7rem;padding:2px 10px;border-radius:12px;background:${borderColor}15;color:${borderColor};font-weight:600;">${health.label}</span>`;

    html += `
    <div style="border:1px solid var(--border-light);border-left:3px solid ${borderColor};border-radius:8px;padding:16px 20px;margin-bottom:16px;">
      <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:14px;">
        <span style="font-size:.78rem;color:var(--text-lighter);font-family:monospace;">${fmtTime(run.run_id)}</span>
        ${triggerBadge(run.trigger)}
        ${bgBadge}
        <span style="font-size:.72rem;color:var(--text-lighter);margin-left:auto;">${ok}✓ ${warn}! ${skip}↷ ${fail}✗ / ${total} 步</span>
      </div>
      <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(190px,1fr));gap:6px;">`;

    [...new Set([...STEP_ORDER, ...Object.keys(steps)])].forEach(stepKey => {
      const s = steps[stepKey];
      const label = STEP_LABELS[stepKey] || s?.label || stepKey;
      const icon = statusIcon(s ? s.status : null);
      const msg = s && s.msg ? `<span style="font-size:.65rem;color:#b91c1c;margin-left:4px;">${s.msg}</span>` : '';
      const ts = s && s.ts ? `<span style="font-size:.62rem;color:#9ca3af;margin-left:auto;">${fmtTime(s.ts).slice(-5)}</span>` : '';
      const bg = !s ? '#f9fafb' : s.status === 'ok' ? '#f0fdf4' : ['skip', 'warn'].includes(s.status) ? '#fffbeb' : '#fef2f2';
      const border = !s ? 'var(--border-light)' : s.status === 'ok' ? '#bbf7d0' : ['skip', 'warn'].includes(s.status) ? '#fde68a' : '#fecaca';

      html += `<div style="display:flex;align-items:center;gap:6px;padding:6px 10px;border-radius:6px;background:${bg};border:1px solid ${border};font-size:.78rem;">
        ${icon}
        <span style="color:var(--text);flex:1;min-width:0;">${label}</span>
        ${msg}${ts}
      </div>`;
    });

    html += `</div></div>`;
  });

  el.innerHTML = html;
}

