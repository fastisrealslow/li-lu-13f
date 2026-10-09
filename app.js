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
  ftDisclaimer: ['本页展示机构 13F 与港股权益披露资料，披露期不等于实时持仓；估算成本不代表真实买入价。不构成投资建议。','Institutional 13F and HK disclosures are dated reports, not live portfolios. Estimated costs are not actual purchase prices. Not investment advice.'],
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
// 人物资料、原始链接与导航均来自核对过的 investors.json。
// 发布版本参数避免新界面读取上一版缓存的配置、持仓和预计算结果。
let INVESTOR_CFG = [];           // investors.json 里的 investors 数组原样（加载后充实）
let INVESTOR_CFG_BY_ID = {};     // id -> 配置对象，方便查找
let INVESTORS = [];              // 按 investors.json 顺序排列的 id 列表
let INVESTOR_LABELS = {};        // id -> 中文名
let INVESTOR_LABELS_EN = {};     // id -> 英文名

async function loadInvestorConfig({fresh = false, signal} = {}) {
  try {
    const resp = await fetch('investors.json?v=65&t=' + (fresh ? Date.now() : Math.floor(Date.now()/300000)), {signal, cache:fresh ? 'no-store' : 'default'});
    if (!resp.ok) throw new Error('investors.json HTTP ' + resp.status);
    const json = await resp.json();
    if (!Array.isArray(json.investors) || !json.investors.length) throw new Error('Invalid investor configuration');
    INVESTOR_CFG = json.investors;
  } catch (e) {
    console.error('investors.json 加载失败，将无法正常显示投资者列表:', e);
    return false;
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
  return true;
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
    const r = await fetch(cfg.dataFile + '?v=65&t=' + stamp, {signal, cache: fresh ? 'no-store' : 'default'});
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
    const archived = !!data.meta?.snapshotType;
    const stale = !archived && (!Number.isFinite(age) || age > maxAge);
    if (src) src.textContent = (stale || !pricesOK ? '⚠ ' : '✓ ') +
      (archived ? (lang === 'en' ? 'Historical archive' : '历史归档披露') : (lang === 'en' ? 'Published data' : '已发布数据')) +
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
  renderTimelineTable();
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
    const resp = await fetch(file + '?v=65&t=' + stamp, {signal, cache: fresh ? 'no-store' : 'default'});
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
    if (!INVESTORS.length && !await loadInvestorConfig({fresh:true, signal:ctrl.signal})) {
      document.getElementById('dataSource').textContent = lang === 'en' ? 'Investor list unavailable; tap Refresh to retry.' : '投资人列表暂不可用，点击刷新可重试。';
      return;
    }
    _homeworkCache = null;
    await switchInvestor(investor, {fresh: true, signal: ctrl.signal});
    if (document.getElementById('tab-homework') && !document.getElementById('tab-homework').classList.contains('d-none') && !ctrl.signal.aborted) await renderHomework();
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
    const resp = await fetch(hkUrl + '?v=65&t=' + Math.floor(Date.now()/300000));
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
      cikHtml + (data.current.valueQuality ? `<span class="data-quality-note">${lang === 'en' ? 'Reported values have an unresolved scale discrepancy; raw SEC amounts retained. Cost estimates are suspended.' : '原表市值存在量级疑点，保留 SEC 原始数值；成本估算暂停。'} <a href="${hkEscape(data.current.valueQuality.source)}" target="_blank" rel="noopener noreferrer">${lang === 'en' ? 'Original filing' : '原始申报'}</a></span>` : '') + (data.meta?.snapshotType ? `<span class="data-quality-note">${lang === 'en' ? 'Historical archived disclosures. Valuation dates could not be verified; totals are HKD, not a complete current portfolio.' : '历史归档披露；估值日期未能核实。合计单位为港元，不代表当前完整组合。'}</span>` : '') + (!comparableQuarter() && !data.meta?.snapshotType ? `<span class="data-quality-note">${comparisonNotice()} <a href="${hkEscape(data.meta.reportingTransition.noticeSource)}" target="_blank" rel="noopener noreferrer">${lang === 'en' ? 'SEC notice' : 'SEC 通知'}</a></span>` : '');
  }
  const tc = d.totalValue - (d.prevTotalValue||0);
  const tp = d.prevTotalValue ? (tc/d.prevTotalValue*100) : 0;
  const cls = tc>=0?'up':'down', sign=tc>=0?'+':'';
  const t3 = d.holdings.slice(0,3);
  document.getElementById('summaryCards').innerHTML = `
      <div class="stat-item">
        <span class="stat-num" style="font-size:1.5rem;">${investor === "webb" ? "HK$" : "US$"}${fmtVal(d.totalValue)}</span>
        <span class="stat-change ${cls}">${comparableQuarter() && !d.valueQuality ? sign+tp.toFixed(1)+"%" : "—"}</span>
        <span class="stat-desc">${d.valueQuality ? (lang === 'en' ? 'Raw reported value; scale unverified' : '原表申报值，量级待核实') : t('statValue')} · ${comparableQuarter() ? t('statVs')+" "+(d.prevQuarter||" ") : comparisonNotice()}</span>
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
        <span class="stat-num">${data.meta?.snapshotType ? (lang === 'en' ? 'Historical' : '历史快照') : d.quarter}</span>
        <span class="stat-desc">${t('statQuarter')} · ${t('metaPeriod')} ${d.periodEnd || '—'}</span>
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
    const cb = data.current.valueQuality || data.meta?.snapshotType || !comparableQuarter() ? null : costBasis[h.ticker];
    const quoteOK = q && !q.error && Number.isFinite(q.c) && q.c > 0;
    const currentPrice = quoteOK && !q.stale ? q.c : null;
    const staleTitle = lang === 'en' ? 'Live quote temporarily unavailable — showing last known price' : '实时报价暂时拉取失败，显示为最后一次成功报价';
    const priceHtml = quoteOK
      ? `${currSymbol(h.ticker)}${q.c.toFixed(2)}${q.stale ? ` <span title="${staleTitle}" style="color:var(--warn,#c9812f);font-size:.7em;">⏱</span>` : ''}`
      : '<span style="color:var(--text-lighter)">--</span>';
    
    let mosHtml = '';
    let costHtml = '<span style="color:var(--text-lighter)">--</span>';
    
    if (cb && cb.recent && !cb.recent.error && Number.isFinite(cb.recent.buy) && cb.recent.buy > 0) {
      const rc = cb.recent;
      const at = cb.allTime;
      const pnl = currentPrice == null ? null : ((currentPrice - rc.buy) / rc.buy * 100).toFixed(1);
      const pnlClass = pnl >= 0 ? 'qoq-up' : 'qoq-down';
      const pnlSign = pnl >= 0 ? '+' : '';
      const isYahoo = rc.source === 'yahoo' || rc.source === 'yfinance';
      const srcBadge = isYahoo ? '<span style="color:#10b981;font-size:.55rem;">K线</span>' : '<span style="color:#f59e0b;font-size:.55rem;">13F估</span>';
      
      // Margin of Safety calculation
      const mos = currentPrice == null ? null : ((rc.buy - currentPrice) / rc.buy * 100);
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
      costHtml += `<div style="font-size:.65rem;color:var(--text-lighter);">${t('costRecent')} ${srcBadge} ${pnl == null ? `<span>${lang === 'en' ? 'Quote unavailable' : '暂无报价'}</span>` : `<span class="${pnlClass}" style="font-weight:500;">${pnlSign}${pnl}%</span>`}</div>`;
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
    if (!comparableQuarter()) { chgTag = ""; } else if (prev === 0 && cur > 0) {
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
    if (!comparableQuarter()) chgTag = "";
    if (h.shareAdjustment && comparableQuarter()) chgTag += `<small style="font-size:.6rem;color:var(--text-lighter);">${lang === 'en' ? 'Split adjusted' : '拆股后可比'}</small>`;
    const mosCellHtml = `<div style="display:flex;flex-direction:column;align-items:center;gap:2px;">${mosHtml || '<span style="color:var(--text-lighter);font-size:.7rem;">--</span>'}${chgTag}</div>`;
    
    return `<tr><td class="idx-cell"><span class="idx-num">${i+1}</span></td><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td class="shares-value-cell"><div style="font-weight:600">${fmtNum(h.shares)}</div><div style="font-size:.68rem;color:var(--text-lighter);margin-top:2px;">${currSymbol(h.ticker)}${h.value.toLocaleString()}</div><div class="mobile-weight-inline" style="display:none;font-size:.65rem;color:var(--navy);font-weight:600;margin-top:3px;"><span style="font-weight:400;color:var(--text-lighter);">${isEn?'Wt':'仓位'}</span> ${pct}%</div></td><td class="price-cell">${priceHtml}</td><td class="cost-cell">${costHtml}</td><td style="width:100px;"><div class="bar-wrap"><div class="bar-fill" style="width:${pct*3.5}%"></div><span style="font-size:.7rem;font-weight:600;color:var(--navy);margin-left:6px;">${pct}%</span></div></td><td style="width:80px;text-align:center;">${mosCellHtml}</td></tr>`;
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
      prevShares: authoritative
        ? (h.shareAdjustment && h.shareAdjustment.reportedShares === p?.shares ? h.prevShares : (p?.shares || 0))
        : (h.prevShares ?? p?.shares ?? 0),
      prevValue: authoritative ? (p?.value || 0) : (h.prevValue ?? p?.value ?? 0)};
  });
  for (const p of remaining) {
    if (p.shares > 0) rows.push({...p, shares: 0, value: 0, prevShares: p.shares, prevValue: p.value, exited: true});
  }
  return rows;
}

function comparableQuarter(snapshot = data) {
  const transition = snapshot?.meta?.reportingTransition;
  return !snapshot?.meta?.snapshotType && !(transition?.comparisonScopeChanged && transition.fromQuarter === snapshot?.current?.quarter);
}
function comparisonNotice(snapshot = data) {
  return snapshot?.meta?.snapshotType
    ? (lang === 'en' ? 'Historical disclosure snapshot; no verified quarterly comparison.' : '历史披露快照；没有可核实的季度比较。')
    : (lang === 'en' ? 'Reporting entity and scope changed this quarter; changes cannot be treated as purchases or sales.' : '本季申报主体与范围变更，持仓差异不能直接视为买卖。');
}
function renderChanges() {
  const d = data.current, en = lang === 'en';
  if (!comparableQuarter()) { document.getElementById('changesBody').innerHTML = `<tr><td colspan="7">${comparisonNotice()}</td></tr>`; return; }
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
    const splitNote = h.shareAdjustment ? `<div style="font-size:.65rem;color:var(--text-lighter);">${en ? 'Split adjusted; reported ' : '拆股后可比；原申报 '}${h.shareAdjustment.reportedShares.toLocaleString('en-US')} · ×${h.shareAdjustment.factor}</div>` : '';
    return `<tr><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker)}${exited}</span><span class="name-line">${cn(h.name, h)}</span><span class="sector-badge">${ts(h.sector)}</span></td><td>${h.prevShares===0?'-':fmtNum(h.prevShares)}${splitNote}</td><td>${fmtNum(h.shares)}</td><td>${fmtShareChg(h.shares,h.prevShares)}</td><td>${h.prevValue===0?'-':symbol+fmtVal(h.prevValue)}</td><td>${symbol}${fmtVal(h.value)}</td><td class="${vc}">${h.prevValue===0?(en?'New':'新进'):`${vs}${symbol}${fmtVal(Math.abs(vd))} (${fmtPct(h.value,h.prevValue)})`}</td></tr>`;
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
    const response=await fetch('ai_supplement.json?v=65&t='+Math.floor(Date.now()/300000),{signal:ctrl.signal});
    if (!response.ok) return;
    const payload=await response.json();
    if (payload.schemaVersion!==2 || !payload.entries || typeof payload.entries!=='object') return;
    _aiSupplement=payload;
    if (data) renderInsights();
    _homeworkCache=null;
  } catch {} finally { clearTimeout(timer); }
}

function aiInvestorFallback(snapshot) {
  if (!comparableQuarter(snapshot)) return comparisonNotice(snapshot);
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
    if (h.shareAdjustment) change+='（拆股调整后）';
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
  const d = data.current, ins = [], changes = comparableQuarter() ? quarterlyHoldings() : [];

  // AI 摘要（如果有）
  const localAI = aiMatchingEntry('investor:'+investor,aiInvestorSource(data));
  // Unverified legacy prose is never used as a fallback.
  const aiSummary = comparableQuarter() ? localAI?.summary || aiInvestorFallback(data) : comparisonNotice();
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
    if (!Number.isFinite(historyQuarterIndex(q)) || history?.excludedValueQuarters?.includes(q)) return;
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
    const txt = generateHistoryInsight(quarters, values) + (data.history?.excludedValueQuarters?.length ? (lang === 'en' ? ' The 2026 Q1/Q2 reported value scale is unverified; those values are excluded from this chart.' : ' 2026 Q1/Q2 原表市值量级待核实，暂不纳入趋势图。') : '');
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
      const factor = (data.meta?.shareActions || []).filter(a =>
        (a.cusip === h.cusip || a.ticker === tk) && q < a.quarter && a.quarter <= latest
      ).reduce((product, a) => product * a.factor, 1);
      const comparableShares = h.shares * factor;
      if (comparableShares > tickerInfo[tk].maxShares) tickerInfo[tk].maxShares = comparableShares;
      if (q === latest) tickerInfo[tk].curShares = comparableShares;
      if (factor !== 1) tickerInfo[tk].splitAdjusted = true;
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
      e.shareInfo = s + shareInfo + (e.splitAdjusted ? `<br><small>${isEn ? 'Split-adjusted shares' : '拆股后可比股数'}</small>` : '');
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
    const resp = await fetch(hkUrl + '?v=65&t=' + Math.floor(Date.now()/300000));
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
          <td><span class="ticker">${hkEscape(h.ticker)}</span></td><td>${hkEscape(cn(h.name, h))}</td>
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
let _homeworkCachedAt = 0;
async function renderHomework() {
  const el = document.getElementById('homeworkContent');
  if (!el) return;
  if (_homeworkCache && Date.now()-_homeworkCachedAt < 300000) { el.innerHTML = _homeworkCache; return; }
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
    const vs = await fetch('value_screen.json?v=65&t=' + Math.floor(Date.now()/300000)).then(r => r.ok ? r.json() : null);
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
    const hwSum = await fetch('homework_summary.json?v=65&t=' + Math.floor(Date.now()/300000)).then(r => r.ok ? r.json() : null).catch(()=>null) || {};
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
  _homeworkCachedAt = Date.now();
}

// ========== Spin-off Tab ==========
async function renderSpinoff() { return renderSpinoffDashboard('hk'); }
async function renderSpinoffUS() { return renderSpinoffDashboard('us'); }

function profileText(value) {
  return Array.isArray(value) ? value[lang === 'en' ? 1 : 0] : (value || '');
}
function updateInvestorContent() {
  const cfg = INVESTOR_CFG_BY_ID[investor];
  if (!cfg?.profile) return;
  const p = cfg.profile, en = lang === 'en', name = en ? cfg.nameEn : cfg.name;
  const text = (zh, english) => en ? english : zh;
  const setText = (selector, value) => { const el = document.querySelector(selector); if (el) el.textContent = value; };
  const setHTML = (selector, value) => { const el = document.querySelector(selector); if (el) el.innerHTML = value; };
  const title = `${name} ${cfg.source13F ? text('13F 持仓追踪', '13F Tracker') : text('港股历史披露', 'Historical HK Disclosures')}`;
  setText('[data-i18n="heroTitle"]', title);
  document.title = title;
  setText('[data-i18n="footerTitle"]', title);
  setText('.hero-title .sub', `${cfg.manager} · ${cfg.source13F ? 'SEC 13F' : text('历史权益披露快照', 'Historical disclosure snapshot')}`);
  setText('.quote-block blockquote', profileText(p.summary));
  setText('.quote-block .attr', text('投资方法摘要 · 非逐字引言 · 原始资料见下方', 'Approach summary · Paraphrased · Sources below'));
  setText('#aboutLabel', 'About');
  setText('#aboutTitle', text(`关于${cfg.name}`, `About ${cfg.nameEn}`));
  setText('#philLabel', 'Philosophy');
  setText('#philTitle', text('投资方法与阅读要点', 'Investment Approach & Reading Notes'));
  setText('#readLabel', 'Sources');
  setText('#readTitle', text('原始资料与延伸阅读', 'Primary Sources & Further Reading'));
  setText('[data-i18n="navAbout"]', text('投资人资料', 'Investor Profile'));
  const sourceURL = cfg.cik ? `https://www.sec.gov/edgar/browse/?CIK=${cfg.cik}&owner=exclude` : 'https://di.hkex.com.hk/di/NSAllFormList.aspx';
  const scope = cfg.source13F
    ? text('本页来自机构的 SEC 13F 申报，只覆盖申报范围内证券，不代表个人财富、基金全部资产或所有投资决策。', 'This page uses the institution’s SEC 13F filings. It covers reportable securities, not personal wealth, every fund asset or every investment decision.')
    : text('本页保留历史港股披露快照；披露有日期和门槛，不能据此判断当前完整持仓。', 'This page retains historical HK disclosure snapshots. Disclosure dates and thresholds limit what can be inferred about a complete current portfolio.');
  setHTML('.ref-text', p.about.map(paragraph => `<p>${hkEscape(profileText(paragraph))}</p>`).join('') + `<p>${scope} <a href="${sourceURL}" target="_blank" rel="noopener noreferrer">${text('核对原始申报', 'Check original filings')}</a>。</p><p style="font-size:.75rem;color:var(--text-lighter);">${text('资料核对日期', 'Profile reviewed')}: ${hkEscape(p.reviewedAt)}</p>`);
  const timeline = [...p.timeline];
  const quarters = historySeries(data?.history).quarters;
  if (quarters.length) timeline.push({date:quarters[0],text:['本页可核实的持仓历史起点', 'First verified holdings quarter on this page']});
  setHTML('.ref-grid .timeline', timeline.map(item => `<div class="tl-item"><div class="tl-year">${hkEscape(item.date)}</div><div class="tl-text">${hkEscape(profileText(item.text))}</div></div>`).join(''));
  const icons = ['🏢','🏰','🤝','⚖️','⏳','🎯'];
  setHTML('.phil-grid', p.principles.map((item,i) => `<div class="phil-card"><div class="icon">${icons[i % icons.length]}</div><h4>${hkEscape(profileText(item.title))}</h4><p>${hkEscape(profileText(item.text))}</p></div>`).join(''));
  setHTML('.articles-grid', p.resources.filter(item => /^https:\/\//.test(item.url)).map(item => `<a class="article-card" href="${hkEscape(item.url)}" target="_blank" rel="noopener noreferrer"><div class="year">${hkEscape(profileText(item.kind))}</div><h4>${hkEscape(profileText(item.title))}</h4><p>${text('打开资料，核对内容与日期。', 'Open the source to verify its content and date.')}</p></a>`).join(''));
  const updated = document.getElementById('updateTime');
  if (updated) updated.textContent = data?.meta?.lastUpdated || '—';
  const sec = document.getElementById('footerSEC');
  if (sec) { sec.hidden = !cfg.cik; if (cfg.cik) sec.href = sourceURL; }
  const official = document.getElementById('footerOfficial');
  if (official) { official.hidden = !cfg.officialWebsite; if (cfg.officialWebsite) { official.href = cfg.officialWebsite; official.textContent = cfg.officialWebsiteLabel || cfg.manager; } }
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
  const steps = Object.entries(run.steps || {}).map(([key,s])=>({...s,status:effectiveStepStatus(key,s)}));
  if (steps.some(s => s.status === 'fail')) return {state: 'fail', label: lang === 'en' ? 'Some updates failed' : '部分更新失败'};
  const ts = Date.parse(run.completedAt || run.run_id);
  if (!Number.isFinite(ts) || now - ts > 36 * 3600000) return {state: 'warn', label: lang === 'en' ? 'Update record is stale' : '更新记录已过期，请检查自动更新'};
  if (steps.some(s => s.status === 'warn')) return {state: 'warn', label: lang === 'en' ? 'Update notices; see details' : '有更新提示，请查看详情'};
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
  if (!await loadInvestorConfig()) {
    const source = document.getElementById('dataSource');
    if (source) source.textContent = lang === 'en' ? 'Investor list could not load. Tap Refresh to retry.' : '投资人列表暂时未能加载，点击刷新重试。';
    return;
  }
  const selected = new URLSearchParams(window.location.search).get('investor');
  await switchInvestor(INVESTORS.includes(selected) ? selected : 'lilu');
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
    'lilu_13f','lilu_prices','vinall_13f','vinall_prices',
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
    vinall_13f:'罗布·维纳尔 13F', vinall_prices:'罗布·维纳尔 股价',
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
    if (s === 'info') return '<span style="color:#2563eb;font-size:.95rem;" title="资料说明">ℹ</span>';
    if (s === 'ok')   return '<span style="color:#15803d;font-size:.95rem;" title="成功">✓</span>';
    if (s === 'warn') return '<span style="color:#d97706;font-size:.85rem;" title="部分功能未更新">!</span>';
    if (s === 'skip') return '<span style="color:#d97706;font-size:.85rem;" title="跳过">↷</span>';
    return '<span style="color:#b91c1c;font-size:.95rem;" title="失败">✗</span>';
  }

  // 统计 ok/fail/skip 数量
  function runSummary(steps) {
    let ok=0, fail=0, skip=0, warn=0, info=0, total=0;
    Object.entries(steps).forEach(([key, raw]) => {
      const s = {...raw,status:effectiveStepStatus(key,raw)};
      total++;
      if (s.status === 'ok') ok++;
      else if (s.status === 'skip') skip++;
      else if (s.status === 'warn') warn++;
      else if (s.status === 'info') info++;
      else fail++;
    });
    return { ok, fail, skip, warn, info, total };
  }

  let html = `
    <div style="margin-bottom:20px;">
      <p style="font-size:.8rem;color:var(--text-lighter);">最近 ${runs.length} 次更新记录。黄色表示需留意的更新提示；红色表示更新失败。历史资料缺失的具体范围会注明。</p>
    </div>`;

  runs.forEach((run, idx) => {
    const steps = run.steps || {};
    const { ok, fail, skip, warn, info, total } = runSummary(steps);
    // Freshness applies to the latest run; older cards describe their state at completion.
    const health = runHealth(run, idx === 0 ? Date.now() : Date.parse(run.completedAt || run.run_id));
    const borderColor = health.state === 'ok' ? '#15803d' : health.state === 'fail' ? '#b91c1c' : '#b45309';
    const bgBadge = `<span class="status-run-badge">${hkEscape(health.label)}</span>`;

    html += `
    <div class="status-run" style="--status-color:${borderColor};--status-bg:${borderColor}15;">
      <div class="status-run-header">
        <span style="font-size:.78rem;color:var(--text-lighter);font-family:monospace;">${fmtTime(run.run_id)}</span>
        ${triggerBadge(run.trigger)}
        ${bgBadge}
        <span class="status-run-count">${ok}✓ ${info}ℹ ${warn}! ${skip}↷ ${fail}✗ / ${total} 步</span>
      </div>
      <div class="status-steps">`;

    [...new Set([...STEP_ORDER, ...Object.keys(steps)])].forEach(stepKey => {
      const s = steps[stepKey];
      if (!s) return;
      const label = STEP_LABELS[stepKey] || s?.label || stepKey;
      const icon = statusIcon(effectiveStepStatus(stepKey,s));
      const msg = s.msg ? `<div class="status-step-message">${hkEscape(statusStepMessage(stepKey, s))}</div>` : '';
      const ts = s.ts ? `<span class="status-step-time">${hkEscape(fmtTime(s.ts).slice(-5))}</span>` : '';
      const status = effectiveStepStatus(stepKey,s);
      const state = ['ok','info','warn','skip','fail'].includes(status) ? status : 'unknown';

      html += `<div class="status-step ${state}" data-step="${hkEscape(stepKey)}">
        ${icon}
        <span class="status-step-label">${hkEscape(label)}</span>
        ${ts}${msg}
      </div>`;
    });

    html += `</div></div>`;
  });

  el.innerHTML = html;
}

function effectiveStepStatus(key, step) {
  // Reclassify only an explicitly completed search, never an interrupted fetch.
  return key === 'lilu_13f' && step?.status === 'warn' && /^lilu 历史缺 \d+ 季：已补查SEC历史索引，仍无可用原始持仓报告；不作零持仓$/.test(step.msg || '') ? 'info' : step?.status;
}
function statusStepMessage(stepKey, step) {
  const msg = String(step?.msg || '');
  const missing = stepKey === 'lilu_13f' && ['warn','info'].includes(step.status) && msg.match(/历史缺\s*(\d+)\s*季/);
  const scope = msg.match(/季（([^）]+)）/);
  const quarters = scope ? ` (${scope[1]})` : '';
  if (missing && (step.status === 'info' || effectiveStepStatus(stepKey,step) === 'info' || /已补查/.test(msg))) return lang === 'en'
    ? `${missing[1]} early historical quarters${quarters} lack verifiable SEC holdings reports, even after checking historical indexes. This notice concerns historical coverage, not a failure to load the latest holdings; gaps remain in the history chart.`
    : `早期历史资料缺 ${missing[1]} 个季度${quarters}：补查 SEC 历史索引后，仍未找到可核实的原始持仓报告。这项提示针对历史覆盖，不表示最新持仓加载失败；历史图保留断点。`;
  if (missing) return lang === 'en' ? `${missing[1]} historical quarters have no verified holdings report. See historical coverage; this is separate from the latest holdings update.` : `历史持仓缺 ${missing[1]} 个季度，请查看历史覆盖说明；此提示不表示最新持仓加载失败。`;
  return msg;
}

