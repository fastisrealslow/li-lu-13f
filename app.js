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
  tabHomework: ['价值筛选','Value Picks'],
  tabSpinoff:  ['港股分拆','HK Spin-offs'],
  tabSpinoffUS: ['美股分拆','US Spin-offs'],
  tabGame: ['思维试炼','Munger Trials'],
  tabPersonal: ['我的持仓','My Holdings'],
  selLabel: ['研究对象','Investor'],
  tabTimeline: ['⏳ 时间轴','⏳ Timeline'],
  // Table headers
  thTicker: ['代码','Ticker'],
  thStock: ['证券','Security'],
  thCompany: ['公司','Company'],
  thSector: ['行业','Sector'],
  thShares: ['持股数','Shares'],
  thHoldingAmount: ['股数 / 申报金额','Shares / reported value'],
  thPrice: ['参考单价','Reference price'],
  thCost: ['历史参考成本','Historical cost estimates'],
  thGap: ['现价与参考价对比','Price vs. reference'],
  gapSub: ['（参考类型见每行说明）','(reference type shown in each row)'],
  priceHelp: ['每日更新参考行情，日期见每行；期权行显示标的股票价格，不是期权价格或行权价。','Daily reference quotes are dated in each row. Option rows show the underlying stock price, not the option premium or strike.'],
  costHelp: ['加仓参考价对应最近披露股数增加季度；历次均价按估计新增股数加权。季末参考价单独标明，不视为买入成本。计算方法见表格下方。','Buying references use the last reported share-increase quarter. Position averages weight estimated additions. Quarter-end proxies are labeled separately and are not acquisition costs. Methods are below the table.'],
  thValue: ['市值 (USD)','Value (USD)'],
  thWeight: ['申报占比','Reported %'],
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
  mosTitle: ['现价比最近加仓参考价低至少 20%','Price at least 20% below latest buying reference'],
  mosSubtitle: ['仅比较今日参考股价与加仓季度的历史价格，不表示股票被低估。','Compares the daily quote with the historical buying reference; it does not imply undervaluation.'],
  mosGreen: ['低于参考价至少 20%','At least 20% below reference'],
  mosWatch: ['现价比最近加仓参考价低 10%–20%','Price 10%–20% below latest buying reference'],
  mosNoMOS: ['暂无低于加仓参考价至少 10% 的标的','No stocks at least 10% below their buying reference'],
  mosBadge: ['低于参考价','Below reference'],

  // Cost labels
  costRecent: ['最近加仓参考价','Latest buying reference'],
  costAllTime: ['历次加仓均价（估算）','Average across purchases (estimated)'],
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
  statValue: ['13F 申报总值','Reported 13F value'],
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
  hkSub: ['港股披露与 13F 分开列示，逐项标注日期、主体与原始文件。','Dated HK disclosures are shown separately from 13F, with entities and original sources.'],
  // Price note
  priceNote: ['加仓参考价取最近披露股数增加的季度：历史低价×70%＋均价×30%；缺少行情时使用该季申报市值÷股数，并标明来源。历次加仓均价按各次估计新增股数加权，减仓保留原均价，清仓后重新累计；拆股按比例校正。低于参考价的比例＝（参考价－现价）÷参考价；高于参考价时显示相应高出幅度。季度披露无法还原每笔交易；这些是历史成本参考，不是投资者实际成本或企业合理估值。','Latest buying references use the last quarter with a reported share increase: historical low × 70% + average × 30%, or a labeled quarter-end value-per-share proxy when prices are unavailable. The position average weights estimated share additions, retains the average on reductions, restarts after exits, and adjusts for splits. Below-reference percentage = (reference − price) / reference; prices above reference show the corresponding excess. Quarterly filings cannot reconstruct every trade. These historical references are neither actual costs nor fair value.'],
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
  costRecent: ['最近加仓参考价','Latest buying reference'],
  costAllTime: ['历次加仓均价（估算）','Average across purchases (estimated)'],
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
    const resp = await fetch('investors.json?v=77&t=' + (fresh ? Date.now() : Math.floor(Date.now()/300000)), {signal, cache:fresh ? 'no-store' : 'default'});
    if (!resp.ok) throw new Error('investors.json HTTP ' + resp.status);
    const json = await resp.json();
    if (!Array.isArray(json.investors) || !json.investors.length) throw new Error('Invalid investor configuration');
    const ids=new Set();
    for(const inv of json.investors){
      if(!/^[a-z][a-z0-9_]{0,30}$/.test(inv.id || '') || ids.has(inv.id) || !/^[a-z0-9_]+\.json$/.test(inv.dataFile || '') || !/^[a-z0-9_]+\.json$/.test(inv.pricesFile || '') || (inv.hkFile && !/^[a-z0-9_]+\.json$/.test(inv.hkFile)))throw new Error('Invalid investor identity or data path');
      ids.add(inv.id);
    }
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
  bar.innerHTML = INVESTORS.map(id => `<button type="button" class="investor-button" aria-pressed="${id===investor}" onclick="switchInvestor('${id}')">${hkEscape(labels[id])}</button>`).join('');
  const select = document.getElementById('investorSelect');
  if (select) {
    select.innerHTML = INVESTORS.map(id => `<option value="${id}">${hkEscape(labels[id])}</option>`).join('');
    select.value = investor;
  }
}
let _investorController=null,_pendingInvestor=null,_switchPromise=null;
let _activeInvestorTab='current',_renderedInvestorViews={},_historyRequest=null;
const _historyRecoveryAssets=new Set();
function investorLoadState(target,error=false) {
  _pendingInvestor=target;
  const node=document.getElementById('investorLoadState');
  if(node){node.textContent=target?(error?(lang==='en'?'Unable to load ':'暂未载入 '):(lang==='en'?'Loading ':'正在载入 '))+(lang==='en'?INVESTOR_LABELS_EN[target]:INVESTOR_LABELS[target])+(error?(lang==='en'?'; please select again.':'，请重新选择重试。'):''):'';node.hidden=!target;node.classList?.toggle('load-error',error);}
  if(typeof document.body?.classList?.toggle==='function')document.body.classList.toggle('investor-loading',!!target&&!error);
  for(const id of ['summaryCards','tab-current','tab-changes','tab-history'])document.getElementById(id)?.setAttribute?.('aria-busy',String(!!target&&!error));
  const select=document.getElementById('investorSelect');if(select)select.value=target&&!error?target:investor;
}
async function investorJSON(file,{signal,stamp,fresh}) {
  const response=await fetch(file+'?v=98&t='+stamp,{signal,cache:fresh?'no-store':'default'});
  if(!response.ok)throw Error(file+' HTTP '+response.status);
  return response.json();
}
function switchInvestor(v,options={}) {
  const target=v&&INVESTORS.includes(v)?v:INVESTORS[(INVESTORS.indexOf(investor)+1)%INVESTORS.length];
  if(_pendingInvestor===target&&_switchPromise&&!options.fresh)return _switchPromise;
  _switchPromise=performInvestorSwitch(target,options);return _switchPromise;
}
async function performInvestorSwitch(target,{fresh=false,signal}={}) {
  const requestId=++investorRequestId,cfg=INVESTOR_CFG_BY_ID[target];
  _investorController?.abort();_historyRequest?.controller.abort();
  const ctrl=new AbortController();_investorController=ctrl;
  const abort=()=>ctrl.abort();signal?.addEventListener?.('abort',abort,{once:true});if(signal?.aborted)ctrl.abort();
  const timer=setTimeout(abort,25000),src=document.getElementById('dataSource');
  let committed=false;
  investorLoadState(target);
  if(src)src.textContent=(lang==='en'?'Loading ':'正在载入 ')+(lang==='en'?cfg?.nameEn:cfg?.name)+'…';
  try {
    if(!cfg)throw Error('Unknown investor');
    const stamp=fresh?Date.now():Math.floor(Date.now()/300000),settings={signal:ctrl.signal,stamp,fresh};
    const bundle=globalThis.InvestorSnapshots?await globalThis.InvestorSnapshots.load(target,settings):null;
    let newData,newPrices,newHKDisclosures,pricesOK;
    if(bundle){
      newData={...bundle.data};newPrices={...bundle.prices};newHKDisclosures=bundle.hk;pricesOK=true;
    }else{
      newData=await investorJSON(cfg.dataFile,settings);
      const results=await Promise.allSettled([investorJSON(cfg.pricesFile,settings),loadHKDisclosures(cfg,settings)]);
      newPrices=results[0].status==='fulfilled'?results[0].value:{quotes:{},costBasis:{}};
      newHKDisclosures=results[1].status==='fulfilled'?results[1].value:null;
      pricesOK=results[0].status==='fulfilled'&&!!newPrices?.quotes;
    }
    if(requestId!==investorRequestId||ctrl.signal.aborted)return false;
    if(!newData?.current||!Array.isArray(newData.current.holdings)||!Number.isFinite(newData.current.totalValue)||newData.current.totalValue<0||newData.current.holdings.some(h=>!h||typeof h.ticker!=='string'||!Number.isFinite(h.shares)||h.shares<0||!Number.isFinite(h.value)||h.value<0||['prevShares','prevValue'].some(k=>h[k]!=null&&(!Number.isFinite(h[k])||h[k]<0))))throw Error('Invalid numeric holdings fields');
    if(!newPrices||typeof newPrices.quotes!=='object'||!newPrices.quotes)throw Error('Invalid prices');
    // Commit every part together: no old investor can acquire a later request's quotes.
    investor=target;data=newData;prices=newPrices;hkDisclosures=newHKDisclosures;
    committed=true;
    if(bundle){data.browserProjection={...data.browserProjection,historyAsset:bundle.history,historyLoaded:false};_aiSupplement=bundle.insights;}
    recentHKRows=latestReportedHKHoldings(newHKDisclosures,cfg,newData.current.quarter);
    _renderedInvestorViews={};
    renderInvestorBtns();updateInvestorContent();renderSummary();
    const updated=data.meta?.lastUpdated,age=Date.now()-Date.parse(updated),archived=!!data.meta?.snapshotType;
    const stale=!archived&&(!Number.isFinite(age)||age>(cfg.source13F===false?9*24:48)*3600000);
    if(src)src.textContent=(stale||!pricesOK?'⚠ ':'✓ ')+(archived?(data.meta?.snapshotType==='verified_disclosure_snapshot'?(lang==='en'?'Verified public disclosures':'已核实公开披露'):(lang==='en'?'Historical archive':'历史归档披露')):(lang==='en'?'Published data':'已发布数据'))+(updated?' · '+new Date(updated).toLocaleString(lang==='en'?'en-US':'zh-CN',{timeZone:'Asia/Shanghai'}):'')+(stale?(lang==='en'?' · Check update status':' · 数据较旧，请查看更新状态'):'')+(!pricesOK?(lang==='en'?' · Prices unavailable':' · 股价暂不可用'):'');
    const priceDate=document.getElementById('priceUpdate');if(priceDate)priceDate.textContent=prices.updatedAt||prices.updated||'';
    investorLoadState(null);
    renderActiveInvestorView();
    return true;
  }catch(error){
    if(requestId!==investorRequestId)return false;
    renderInvestorBtns();investorLoadState(target,true);
    if(committed){
      const message=lang==='en'?'Data loaded; this view could not display. Please refresh.':'数据已载入，当前视图未能显示，请刷新重试。';
      if(src)src.textContent=message;const notice=document.getElementById('investorLoadState');if(notice)notice.textContent=message;
    }else if(src)src.textContent=lang==='en'?'Loading failed; previous selection retained. Try again.':'加载失败，保留原投资人和数据，请重试';
    console.error('switchInvestor error:',error.message);return false;
  }finally{clearTimeout(timer);signal?.removeEventListener?.('abort',abort);if(requestId===investorRequestId){_pendingInvestor=null;_switchPromise=null;}}
}
function renderActiveInvestorView(force=false) {
  if(!data)return;
  const tab=_activeInvestorTab,key=investorRequestId+'|'+lang+'|'+(data.browserProjection?.historyLoaded?'full':'overview');
  if(!force&&_renderedInvestorViews[tab]===key)return;
  if(tab==='current'){renderHoldings();renderScopedInsight('holdings');renderHKDisclosures();}
  else if(tab==='changes'){renderChanges();renderInsights('changes');}
  else if(tab==='history'){renderHistoryChart();renderScopedInsight('history');if(data.browserProjection&&!data.browserProjection.historyLoaded)ensureInvestorHistory();else renderTimelineTable();}
  _renderedInvestorViews[tab]=key;
}
let _mobileInvestorLayout=globalThis.window?.innerWidth<640;
function syncInvestorLayout(){
  syncOptionDetailColumns();
  const mobile=globalThis.window?.innerWidth<640;
  if(mobile!==_mobileInvestorLayout){_mobileInvestorLayout=mobile;if(data)renderActiveInvestorView(true);}
}
async function ensureInvestorHistory() {
  if(!data?.browserProjection||data.browserProjection.historyLoaded||!globalThis.InvestorSnapshots)return;
  const target=investor,snapshot=data,requestId=investorRequestId;
  if(_historyRequest?.snapshot===snapshot)return _historyRequest.promise;
  const controller=new AbortController(),container=document.getElementById('timelineCanvas');
  if(container)container.innerHTML=`<p class="portfolio-history-loading" role="status">${lang==='en'?'Loading full history for ':'正在载入完整历史：'}${hkEscape(lang==='en'?INVESTOR_LABELS_EN[target]:INVESTOR_LABELS[target])}…</p>`;
  const timer=setTimeout(()=>controller.abort(),30000);
  const promise=(async()=>{try{
    const value=await globalThis.InvestorSnapshots.history(snapshot.browserProjection.historyAsset,{signal:controller.signal});
    if(requestId!==investorRequestId||data!==snapshot)return;
    data.history={...value.history,costReferenceProofs:snapshot.history.costReferenceProofs};prices.exitPerf=value.exitPerf;data.browserProjection.historyLoaded=true;
    delete _renderedInvestorViews.history;if(_activeInvestorTab==='history')renderActiveInvestorView();
  }catch(error){if(requestId!==investorRequestId||data!==snapshot||controller.signal.aborted&&_activeInvestorTab!=='history')return;
    const file=snapshot.browserProjection.historyAsset.file;
    if(error.status===404&&!_historyRecoveryAssets.has(file)){_historyRecoveryAssets.add(file);if(_historyRecoveryAssets.size>10)_historyRecoveryAssets.delete(_historyRecoveryAssets.values().next().value);await switchInvestor(target,{fresh:true});return;}
    if(container)container.innerHTML=`<p class="portfolio-history-loading">${lang==='en'?'History could not load.':'历史暂未载入。'} <button type="button" onclick="switchInvestor('${target}',{fresh:true})">${lang==='en'?'Reload':'重新载入'}</button></p>`;
  }finally{clearTimeout(timer);if(_historyRequest?.snapshot===snapshot)_historyRequest=null;}})();
  _historyRequest={snapshot,controller,promise};return promise;
}

function cn(name, h) {
  if (lang==='zh') {
    if (h && h.cnName) return h.cnName;
    return Object.prototype.hasOwnProperty.call(T.cnName,name) ? T.cnName[name] : name;
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
  if (refreshBtn && !refreshBtn.disabled) refreshBtn.textContent = lang === 'en' ? 'Refresh' : '刷新';
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
  if (data) {
    renderSummary(); updateInvestorContent(); renderActiveInvestorView(true);
  }
  if (_runStatusData) updateStatusDot(_runStatusData);
  if (!document.getElementById('tab-personal')?.classList.contains('d-none') && typeof renderPersonalPortfolio === 'function') renderPersonalPortfolio();
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
function changePercent(cur,prev) { const pct=Math.abs(cur/prev-1)*100;return pct>0 && pct<.05?'<0.05':pct.toFixed(1); }
function positionChangeBadge(cur, prev) {
  const en=lang==='en';
  if(!Number.isFinite(cur) || !Number.isFinite(prev) || cur<0 || prev<0) return '';
  const kind=prev===0 && cur>0?'new':prev>0 && cur===0?'exited':cur>prev?'added':cur<prev?'trimmed':'hold';
  const labels=en?{new:'New',exited:'Exited',added:'Added',trimmed:'Reduced',hold:'Shares unchanged'}:{new:'新建仓',exited:'清仓',added:'加仓',trimmed:'减仓',hold:'股数不变'};
  const icons={new:'＋',exited:'×',added:'▲',trimmed:'▼',hold:'＝'};
  const percentage=['added','trimmed'].includes(kind)?` ${cur>prev?'+':'−'}${changePercent(cur,prev)}%`:'';
  return `<span class="position-change ${kind}"><span aria-hidden="true">${icons[kind]}</span> ${labels[kind]}${percentage}</span>`;
}
function fmtShareChg(cur, prev) {
  if (!Number.isFinite(cur) || !Number.isFinite(prev) || cur<0 || prev<0) return `<span class="qoq-flat">${lang==='en'?'Unverified':'待比较'}</span>`;
  if (prev===0 && cur>0) return `<span class="qoq-new"><span aria-hidden="true">＋</span> ${lang === 'en' ? 'New' : '新进'}</span>`;
  if (prev>0 && cur===0) return `<span class="qoq-down"><span aria-hidden="true">×</span> ${lang==='en'?'Exited':'清仓'} -${prev.toLocaleString('en-US')} (-100.0%)</span>`;
  const d=cur-prev;
  if (d===0) return `<span class="qoq-flat"><span aria-hidden="true">＝</span> ${lang === 'en' ? 'Unchanged' : '不变'}</span>`;
  const p=(d/prev*100), c=d>0?'qoq-up':'qoq-down', sign=d>0?'+':'-';
  return `<span class="${c}"><span aria-hidden="true">${d>0?'▲':'▼'}</span> ${lang==='en'?(d>0?'Added':'Reduced'):(d>0?'加仓':'减仓')} ${sign}${Math.abs(d).toLocaleString('en-US')} (${sign}${changePercent(cur,prev)}%)</span>`;
}

// ========== DATA ==========
let data = null;
let prices = null;  // loaded from prices.json (generated by GitHub Action)

async function loadPrices(pf, requestId = investorRequestId, {signal, stamp = Math.floor(Date.now()/300000), fresh = false} = {}) {
  const file = pf || 'prices.json';
  try {
    const resp = await fetch(file + '?v=73&t=' + stamp, {signal, cache: fresh ? 'no-store' : 'default'});
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

function fmtTicker(tk, holding = null) {
  if(holding?.shareType && holding.shareType!=='SH') return `<span class="ticker" title="CUSIP">${hkEscape(holding.cusip || tk)}</span>`;
  // Handle unmapped tickers (prefixed with ? in fetch_13f.py)
  const unmapped = tk && tk.startsWith('?');
  const display = unmapped ? tk.substring(1) : tk;
  const style = unmapped ? 'color:#f59e0b;cursor:help' : '';
  const title = unmapped ? ` title="${lang==='en'?'Listing code not yet matched; original filing name retained':'证券代码尚未匹配，保留原始申报名称'}"` : '';
  return `<span class="ticker" style="${style}"${title}>${hkEscape(display)}</span>`;
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
    if (document.body?.classList?.contains?.('personal-research') && typeof renderPersonalPortfolio === 'function') {
      await renderPersonalPortfolio(true);
      return;
    }
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
    btn.textContent = lang === 'en' ? 'Refresh' : '刷新';
  }
}

// ========== TIMELINE & HK HOLDINGS ==========

function renderTimeline() {
  const container = document.getElementById('timelineCanvas');
  if (!container || !data || !data.history || !data.history.holdings) {
    if (container) container.innerHTML = `<p style="color:var(--text-lighter);padding:24px;text-align:center;">${lang==='en'?'Historical holdings are not available in this snapshot.':'当前数据中没有可展示的历史持仓。'}</p>`;
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
      html += `<span style="position:absolute;left:${x}px;top:0;font-size:10px;color:var(--text-lighter);transform:translateX(-50%);">${hkEscape(q)}</span>`;
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
    html += `<span style="position:absolute;left:0;top:0;width:${padL - 8}px;font-size:12px;font-weight:600;color:var(--navy);text-align:right;line-height:${barH}px;">${hkEscape(s.ticker)}</span>`;
    html += `<div style="position:absolute;left:${padL + x1}px;top:4px;width:${bw}px;height:${barH}px;background:${color};border-radius:4px;opacity:0.85;" title="${hkEscape(s.ticker)} (${hkEscape(s.sector)})\n${hkEscape(s.firstQ)} → ${hkEscape(s.lastQ)}\n持有 ${dur} 个季度"></div>`;
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
  if (globalThis.window?.PublicPortfolio?.render('summary',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
  const d = data.current;
  // 更新 hero 区报告期 / 提交日 / CIK
  const metaRow = document.getElementById('metaRow');
  if (metaRow) {
    const isEn = lang === 'en';
    const cik = getInvestorCIK(investor);
    const cikHtml = cik
      ? `<span><strong>CIK</strong> ${hkEscape(cik)}</span>`
      : '';
    metaRow.innerHTML =
      `<span><strong>${isEn ? 'Period' : '\u62a5\u544a\u671f'}</strong> ${hkEscape(d.periodEnd || '--')}</span>` +
      `<span><strong>${isEn ? 'Filed' : '\u63d0\u4ea4\u65e5'}</strong> ${hkEscape(d.filingDate || '--')}</span>` +
      cikHtml + (data.current.holdings.some(h=>h.putCall) ? `<span class="data-quality-note">${lang==='en'?'Option rows show underlying notional values.':'期权按标的名义金额展示。'} <a href="https://www.sec.gov/files/form13f.pdf" target="_blank" rel="noopener noreferrer">SEC 13F</a></span>` : '') + (data.current.valueQuality ? `<span class="data-quality-note">${lang === 'en' ? 'Reported values have an unresolved scale discrepancy; raw SEC amounts retained. Cost estimates are suspended.' : '原表市值存在量级疑点，保留 SEC 原始数值；成本估算暂停。'} <a href="${hkEscape(data.current.valueQuality.source)}" target="_blank" rel="noopener noreferrer">${lang === 'en' ? 'Original filing' : '原始申报'}</a></span>` : '') + (data.meta?.snapshotType ? `<span class="data-quality-note">${data.meta.snapshotType==='verified_disclosure_snapshot'?(lang==='en'?'Latest verified HKEX forms, dated individually; interests remain at least 5%. Values use latest HKD quotes.':'采用各股最近一份已核实港交所原表，展示披露权益仍达 5% 的证券；估值使用最新港元股价。'):(lang === 'en' ? 'Historical archived disclosures. Valuation dates could not be verified; totals are HKD, not a complete current portfolio.' : '历史归档披露；估值日期未能核实。合计单位为港元，不代表当前完整组合。')}</span>` : '') + (!comparableQuarter() && !data.meta?.snapshotType ? `<span class="data-quality-note">${comparisonNotice()} <a href="${hkEscape(data.meta?.reportingTransition?.noticeSource || INVESTOR_CFG_BY_ID[investor]?.resources?.[0]?.url || 'https://www.sec.gov/edgar/search/')}" target="_blank" rel="noopener noreferrer">${lang === 'en' ? 'SEC notice' : 'SEC 通知'}</a></span>` : '');
  }
  const tc = d.totalValue - (d.prevTotalValue||0);
  if (metaRow && INVESTOR_CFG_BY_ID[investor]?.holdingsUpdateMode==='archived') {
    metaRow.innerHTML+=`<span class="data-quality-note">${lang==='en'?'Archive mode: historical shares are retained; quotes refresh independently.':'历史档案模式：持仓股数保留原样，股价独立定期更新。'}</span>`;
  }
  if(metaRow && data.meta?.browserScope){const s=data.meta.browserScope;metaRow.innerHTML+=`<span class="data-quality-note">${lang==='en'?`Showing the largest ${s.limit} current positions (${s.reportedHoldings} reported). Changes and security histories use these positions; the value chart shows the full filing.`:`展示当前前 ${s.limit} 大持仓（完整申报 ${s.reportedHoldings} 项）；季度变化和个股历史按此范围展示，市值曲线保留全组合。`}</span>`;}
  const tp = d.prevTotalValue ? (tc/d.prevTotalValue*100) : 0;
  const cls = tc>=0?'up':'down', sign=tc>=0?'+':'';
  const t3 = d.holdings.slice(0,3);
  document.getElementById('summaryCards').innerHTML = `
      <div class="stat-item"><div class="stat-primary">
        <span class="stat-num" style="font-size:1.5rem;">${d.valueQuality?(lang==='en'?'Value unverified':'金额待核实'):(investor === "webb" ? "HK$" : "US$")+fmtVal(d.totalValue)}</span>
        <span class="stat-change ${cls}">${comparisonState()==='comparable' && !d.valueQuality ? sign+tp.toFixed(1)+"%" : "—"}</span>
        </div><span class="stat-desc">${d.valueQuality ? (lang === 'en' ? 'Reported value units unverified' : '申报金额单位待核实') : data.meta?.snapshotType?(data.meta.snapshotType==='verified_disclosure_snapshot'?(lang==='en'?'Disclosed shares × latest quotes':'披露股数×最新股价'):(lang==='en'?'Archived valuation total':'历史估值合计')):t('statValue')} · ${comparisonState()==='scope_partial'?(lang==='en'?'Expanded parent filing':'母公司合并申报'):comparableQuarter() ? t('statVs')+" "+(d.prevQuarter||" ") : comparisonNotice()}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <div class="stat-primary"><span class="stat-num">${data.meta?.browserScope?.reportedHoldings || d.holdings.length}</span></div>
        <span class="stat-desc">${recentHKRows.length ? (lang==='en'?'13F holdings':'只 13F 持仓') : t('statCount')}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <div class="stat-primary"><span class="stat-num">${d.valueQuality?'—':(t3.reduce((s,h)=>s+h.value,0)/d.totalValue*100).toFixed(1)+'%'}</span></div>
        <span class="stat-desc">${t('statTop3')} ${t3.map(h=>hkEscape(h.ticker)).join('·')}</span>
      </div>
      <div class="stat-sep"></div>
      <div class="stat-item">
        <div class="stat-primary"><span class="stat-num">${data.meta?.snapshotType ? (data.meta.snapshotType==='verified_disclosure_snapshot'?(lang==='en'?'Disclosed':'公开披露'):(lang === 'en' ? 'Historical' : '历史快照')) : hkEscape(d.quarter)}</span></div>
        <span class="stat-desc">${t('statQuarter')} · ${t('metaPeriod')} ${hkEscape(d.periodEnd || '—')}</span>
      </div>
  `;
}


function sameManagerCostHistory(h, snapshot) {
  const transition=snapshot.meta?.reportingTransition,quarter=transition?.fromQuarter;
  const match=/^(\d{4}) Q([1-4])$/.exec(quarter || '');
  if(!match || !transition.fromCIK)return false;
  const year=Number(match[1]),number=Number(match[2]),previous=`${number>1?year:year-1} Q${number>1?number-1:4}`;
  const history=snapshot.history || {},scope=history.reportingScopes?.[quarter] || snapshot.current?.reportingScope;
  const normalize=cik=>String(cik || '').replace(/^0+/,'');
  if(scope?.quarter!==quarter || normalize(history.filing_sources?.[previous]?.cik)!==normalize(transition.fromCIK))return false;
  const ids=new Set(Object.entries(scope.managers || {}).filter(([,manager])=>normalize(manager.cik)===normalize(transition.fromCIK)).map(([id])=>id));
  const rows=history.holdings?.[quarter] || (snapshot.current?.quarter===quarter?snapshot.current.holdings:[]) || [];
  const row=rows.find(r=>r.cusip===h.cusip&&(r.putCall || '')===(h.putCall || '')&&(r.shareType || 'SH')===(h.shareType || 'SH'));
  return !!(h.cusip && ids.size && row?.managerAllocations?.length && row.managerAllocations.every(a=>a.managerIds.some(id=>ids.has(id))) && ['shares','value'].every(k=>row.managerAllocations.reduce((sum,a)=>sum+a[k],0)===row[k]));
}
const _costProofSets=new WeakMap(),_instrumentTickerSets=new WeakMap(),_shareActionIndexes=new WeakMap();
function verifiedCostReference(h,quarter,snapshot) {
  const proofs=snapshot.history?.costReferenceProofs;
  if(!proofs)return (snapshot.history?.holdings?.[quarter]||[]).some(row=>row.ticker===h.ticker&&row.cusip===h.cusip&&row.shareType==='SH'&&row.putCall===''&&row.shares>0);
  let index=_costProofSets.get(proofs);if(!index){index=new Map(Object.entries(proofs).map(([q,ids])=>[q,new Set(ids.map(id=>JSON.stringify(id)))]));_costProofSets.set(proofs,index);}
  return !!index.get(quarter)?.has(JSON.stringify([h.ticker,h.cusip??null]));
}
function instrumentHistoryIncludes(meta,ticker) {
  const rows=meta.instrumentHistoryTickers;if(!rows)return false;
  let entry=_instrumentTickerSets.get(rows);if(!entry||entry.length!==rows.length){entry={length:rows.length,set:new Set(rows)};_instrumentTickerSets.set(rows,entry);}
  return entry.set.has(ticker);
}
function shareActionsFor(h,snapshot) {
  const rows=snapshot.meta?.shareActions;if(!rows?.length)return [];
  let entry=_shareActionIndexes.get(rows);
  if(!entry||entry.length!==rows.length){entry={length:rows.length,cusips:new Map(),tickers:new Map(),unbound:new Map()};for(const a of rows){const add=(m,key)=>{if(!m.has(key))m.set(key,[]);m.get(key).push(a);};add(entry.tickers,a.ticker);if(a.cusip)add(entry.cusips,a.cusip);else add(entry.unbound,a.ticker);}_shareActionIndexes.set(rows,entry);}
  return h.cusip?[...(entry.cusips.get(h.cusip)||[]),...(entry.unbound.get(h.ticker)||[])]:entry.tickers.get(h.ticker)||[];
}
function holdingCostState(h, snapshot = data, priceSnapshot = prices) {
  const meta = snapshot?.meta || {}, current = snapshot?.current || {};
  const unavailable = reason => ({basis: null, reason});
  if (h.putCall) return unavailable('option');
  if (h.shareType && h.shareType !== 'SH') return unavailable('principal');
  if (meta.snapshotType) return unavailable('archive');
  if (current.valueQuality) return unavailable('units');
  if (h.ticker?.startsWith('?')) return unavailable('unmapped');
  const filedReference = () => {
    const exact = current.holdings?.some(row => row.cusip === h.cusip && row.ticker === h.ticker && row.shares === h.shares && row.value === h.value);
    if (!exact || !Number.isFinite(h.value) || !Number.isFinite(h.shares) || h.value<=0 || h.shares<=0) return null;
    return {basis:{recent:{buy:h.value/h.shares,quarter:current.quarter,source:'13f-estimate',kind:'quarter_reference'},allTime:null},reason:null};
  };
  const cb = priceSnapshot?.costBasis?.[h.ticker];
  if (!cb?.recent || cb.recent.error || !Number.isFinite(cb.recent.buy) || cb.recent.buy <= 0) return filedReference() || unavailable('missing');
  const recentQuarter = historyQuarterIndex(cb.recent.quarter), currentQuarter = historyQuarterIndex(current.quarter);
  const transition=meta.reportingTransition;
  if(transition?.comparisonScopeChanged && recentQuarter<historyQuarterIndex(transition.fromQuarter) && !sameManagerCostHistory(h,snapshot)) return filedReference() || unavailable('scope');
  if (!Number.isFinite(recentQuarter) || recentQuarter > currentQuarter) return filedReference() || unavailable('stale_cost');
  const verified = quarter => !(snapshot?.history?.excludedValueQuarters || []).includes(quarter) && verifiedCostReference(h,quarter,snapshot);
  if ((snapshot?.history?.excludedValueQuarters || []).includes(cb.recent.quarter) && !['yahoo','yfinance'].includes(cb.recent.source)) return unavailable('units');
  let allTime = cb.allTime;
  const pendingUnits=cb.averageUnavailable==='units' || allTime && (snapshot?.history?.excludedValueQuarters || []).some(q=>historyQuarterIndex(q)>=historyQuarterIndex(allTime.first) && historyQuarterIndex(q)<=historyQuarterIndex(allTime.last));
  if (pendingUnits) allTime=null;
  if (allTime?.first && recentQuarter < historyQuarterIndex(allTime.first)) return filedReference() || unavailable('stale_cost');
  if (instrumentHistoryIncludes(meta,h.ticker)) {
    const boundary = historyQuarterIndex(meta.instrumentHistoryFrom);
    if (!Number.isFinite(boundary) || recentQuarter < boundary || !verified(cb.recent.quarter)) return filedReference() || unavailable('classes');
    if (allTime && (historyQuarterIndex(allTime.first) < boundary || !verified(allTime.first))) allTime = null;
  }
  // An old average must not survive a newly verified split correction.
  const actions = shareActionsFor(h,snapshot).filter(a =>
    historyQuarterIndex(allTime?.first) < historyQuarterIndex(a.quarter) && historyQuarterIndex(a.quarter) <= currentQuarter);
  const pendingSplit = allTime && actions.length && cb.splitAdjustedThrough !== current.quarter;
  if (pendingSplit || !Number.isFinite(allTime?.avg) || allTime.avg <= 0) allTime = null;
  return {basis: {...cb, allTime}, reason: null, averagePending: !!pendingSplit || !!pendingUnits || cb.averageUnavailable==='corporate_action', averageReason: cb.averageUnavailable==='corporate_action'?'corporate_action':pendingUnits?'units':'split'};
}
function costUnavailableText(reason, en = lang === 'en') {
  const messages = {
    option: ['期权不适用', 'Not for options'], principal: ['本金不适用', 'Not for principal'],
    archive: ['历史快照不估算', 'Archive only'], units: ['申报单位待核实', 'Filed units unverified'],
    scope: ['申报范围待比较', 'Reporting scope changed'], classes: ['股类历史待核实', 'Share-class history unverified'],
    stale_cost: ['估价季度待更新', 'Estimate quarter unverified'], unmapped: ['证券代码待映射', 'Ticker mapping pending'], missing: ['暂无历史估价', 'History estimate unavailable']
  };
  return (messages[reason] || messages.missing)[en ? 1 : 0];
}
function costGap(price, cost) {
  return Number.isFinite(price) && price > 0 && Number.isFinite(cost) && cost > 0 ? (cost - price) / cost * 100 : null;
}
function costGapTone(gap) { return gap >= 20 ? 'deep' : gap >= 10 ? 'watch' : gap > 0 ? 'positive' : gap < 0 ? 'negative' : 'neutral'; }
function optionNotionalReference(h, snapshot=data) {
  if(!h?.putCall || (h.shareType || 'SH')!=='SH' || snapshot?.current?.valueQuality || !Number.isFinite(h.value) || !Number.isFinite(h.shares) || h.value<=0 || h.shares<=0)return null;
  return {price:h.value/h.shares,quarter:snapshot.current.quarter};
}
const _quoteDateFormatters=new Map();
function quoteDateText(q, ticker) {
  if (!Number.isFinite(q?.t) || q.t <= 0 || q.t*1000 > Date.now()+300000) return '';
  const timeZone=ticker?.endsWith('.HK')?'Asia/Hong_Kong':'America/New_York';
  if(!_quoteDateFormatters.has(timeZone))_quoteDateFormatters.set(timeZone,new Intl.DateTimeFormat('en-CA',{timeZone}));
  return _quoteDateFormatters.get(timeZone).format(new Date(q.t*1000));
}
function reportingScopeHTML(snapshot = data) {
  const current=snapshot?.current,scope=current?.reportingScope,en=lang==='en';
  if(!scope || scope.quarter!==current.quarter) return '';
  const managers=scope.managers || {};
  const continuing=current.holdings.filter(h=>sameManagerCostHistory(h,snapshot));
  const added=current.holdings.filter(h=>!sameManagerCostHistory(h,snapshot)).map(h=>h.ticker);
  const continuity=continuing.length && snapshot.meta?.reportingTransition?.fromQuarter===current.quarter
    ? `<p>${en?`${continuing.length} securities retain verified predecessor-manager history. ${hkEscape(added.join(', '))} entered the reporting scope this quarter; its reference starts here.`:`${continuing.length} 项证券已按原管理人编号衔接持仓历史；${hkEscape(added.join('、'))} 为本季新增申报范围，从本季建立价格参考。`}</p>` : '';
  const lines=current.holdings.flatMap(h=>(h.managerAllocations || []).map(a=>`<tr><td>${hkEscape(h.ticker)}</td><td>${a.shares.toLocaleString('en-US')}</td><td>$${a.value.toLocaleString('en-US')}</td><td>${a.managerIds.map(id=>'#'+hkEscape(id)).join(', ')}</td></tr>`)).join('');
  return `<details class="position-note"><summary>${en?'Consolidated filing: security and manager breakdown':'合并申报：每只证券的主体与数量'}</summary>${continuity}<p>${en?'Each row below is one original filing entry. Multiple manager numbers on the same row describe joint discretion over that row; its shares are counted once.':'下表逐行对应 SEC 原表；同一行出现多个主体编号，表示共同申报同一笔证券，股数只计一次。'}</p>${Object.entries(managers).map(([id,m])=>`<p>#${hkEscape(id)} · ${hkEscape(m.name)}</p>`).join('')}<div style="overflow-x:auto"><table><thead><tr><th>${en?'Security':'证券'}</th><th>${en?'Shares':'股数'}</th><th>${en?'Filed value':'申报市值'}</th><th>${en?'Manager IDs':'主体编号'}</th></tr></thead><tbody>${lines}</tbody></table></div><a href="${hkEscape(scope.source)}" target="_blank" rel="noopener noreferrer">${en?'SEC manager list':'SEC 主体编号原表'}</a></details>`;
}
function costGapHTML(gap, reason, en = lang === 'en', scopeInitial = false) {
  if (gap === null) return `<span class="estimate-unavailable">${hkEscape(reason || (en ? 'Quote unavailable' : '报价待更新'))}</span>`;
  const tone = costGapTone(gap);
  const ref = scopeInitial==='adjusted_quarter_reference' ? (en?'corporate-action adjusted reference':'公司行动调整参考') : scopeInitial==='quarter_reference' ? (en?'filed quarter-end price':'本季季末价') : scopeInitial ? (en?'scope-entry reference':'新范围首季参考价') : (en?'buying reference':'加仓参考价');
  const label = gap > 0 ? (en ? 'Price below '+ref : '现价低于'+ref) : gap < 0 ? (en ? 'Price above '+ref : '现价高于'+ref) : (en ? 'Price equals '+ref : '现价等于'+ref);
  return `<span class="cost-gap ${tone}"><small>${label}</small><strong>${Math.abs(gap).toFixed(1)}%</strong></span>`;
}
function holdingsLegendHTML(rows,gaps) {
  const en=lang==='en',entries=[];
  if(comparableQuarter()) {
    const shown=new Set(rows.filter(h=>(comparisonState()!=='scope_partial'||sameManagerCostHistory(h,data)) && Number.isFinite(h.prevShares) && h.prevShares>=0 && Number.isFinite(h.shares) && h.shares>=0).map(changeCategory));
    for(const [kind,cur,prev,zh,english] of [
      ['new',1,0,'本期首次出现','First appearance this quarter'],
      ['added',110,100,'较上季股数增加','More shares than the prior quarter'],
      ['trimmed',90,100,'较上季股数减少','Fewer shares than the prior quarter'],
      ['exited',0,100,'本期不再披露','Absent from this filing'],
      ['hold',100,100,'较上季股数相同','Same share count as the prior quarter']]) {
      if(shown.has(kind))entries.push(`<span class="legend-item">${positionChangeBadge(cur,prev)}<span>${en?english:zh}</span></span>`);
    }
  }
  const shownTones=new Set(gaps.map(costGapTone));
  for(const [tone,zh,english] of [
    ['deep','低于参考价至少 20%','At least 20% below reference'],
    ['watch','低于参考价 10% 至不足 20%','10% to under 20% below reference'],
    ['positive','低于参考价不足 10%','Under 10% below reference'],
    ['negative','高于参考价','Above reference'],
    ['neutral','等于参考价','Equal to reference']]) {
    if(shownTones.has(tone))entries.push(`<span class="legend-item"><span class="legend-swatch ${tone}" aria-hidden="true"></span><span>${en?english:zh}</span></span>`);
  }
  return entries.length?`<details class="holdings-key"><summary>${en?'Table legend':'表内标记说明'}</summary><div class="holdings-key-items">${entries.join('')}</div></details>`:'';
}
function optionPositionHTML(h,cur) {
  const type=(h.putCall || '').toUpperCase(),en=lang==='en';
  if(!['PUT','CALL'].includes(type))return '';
  const put=type==='PUT',total=cur.totalValue;
  const weight=!cur.valueQuality && Number.isFinite(total) && total>0 && Number.isFinite(h.value) && h.value>=0?h.value/total*100:null;
  const formula=weight===null?(en?'Reported values unverified':'申报金额待核实'):`${currSymbol(h.ticker)}${h.value.toLocaleString('en-US')} ÷ ${currSymbol(h.ticker)}${total.toLocaleString('en-US')} = ${weight.toFixed(2)}%`;
  const filing=typeof cur.sourceFiling==='string' && /^https:\/\/www\.sec\.gov\/Archives\//.test(cur.sourceFiling)?`<a href="${hkEscape(cur.sourceFiling)}" target="_blank" rel="noopener noreferrer">${en?'Original filing':'原始申报'} ↗</a> · `:'';
  return `<div class="option-position-content"><p><strong>${en?`Long ${type}: right to ${put?'sell':'buy'} the underlying at the strike.`:`${put?'买入／持有看跌期权':'买入／持有看涨期权'}：按行权价${put?'卖出':'买入'}标的的权利。`}</strong></p><p>${hkEscape(cn(h.name,h))} · ${hkEscape(h.ticker)} · ${h.shares.toLocaleString('en-US')} ${en?'shares covered, not contracts':'股，不是合约张数'}<br>${en?'Underlying notional / filed total':'标的名义金额 ÷ 申报总值'}：<strong>${formula}</strong></p><p class="option-field-note">${en?'Notional weight, not stock exposure. Strike, expiry and premium are not disclosed.':'名义占比不等于正股敞口。未披露行权价、到期日和权利金。'} ${filing}</p></div>`;
}
function toggleOptionPosition(button) {
  const row=document.getElementById(button.getAttribute('aria-controls'));
  if(!row)return;
  row.hidden=!row.hidden;
  button.setAttribute('aria-expanded',String(!row.hidden));
  button.textContent=lang==='en'?(row.hidden?'Option details':'Hide option details'):(row.hidden?'期权明细':'收起期权明细');
  syncOptionDetailColumns();
}
function syncOptionDetailColumns() {
  if(typeof getComputedStyle!=='function')return;
  const columns=[...document.querySelectorAll('#tab-current > .table-wrap thead th')].filter(th=>getComputedStyle(th).display!=='none').length;
  if(columns)document.querySelectorAll('#holdingsBody .option-details-row > td').forEach(td=>{td.colSpan=columns;});
}
const _portfolioViews={};
function portfolioVisibleIndexes(kind,rows) {
  let state=_portfolioViews[kind];if(!state||state.investor!==investor)state=_portfolioViews[kind]={investor,query:'',page:0};
  const pageSize=rows.length>200&&globalThis.window?.innerWidth<640?50:200;
  if(state.pageSize&&state.pageSize!==pageSize)state.page=Math.floor(state.page*state.pageSize/pageSize);
  state.pageSize=pageSize;
  const term=state.query.trim().toLowerCase();let matches=rows.map((h,i)=>({h,i})).filter(({h})=>!term||[h.ticker,h.name,h.cnName,h.cusip].join(' ').toLowerCase().includes(term));
  const pages=Math.max(1,Math.ceil(matches.length/pageSize));state.page=Math.max(0,Math.min(pages-1,state.page));
  const target=document.getElementById(kind==='current'?'holdingsControls':'changesControls');
  if(target){
    target.innerHTML=rows.length<=200&&!state.query?'':`<div class="portfolio-controls"><label>${lang==='en'?'Find a security':'查找证券'}<input id="portfolio-search-${kind}" type="search" value="${hkEscape(state.query)}" placeholder="${lang==='en'?'Company, ticker or CUSIP':'公司、代码或 CUSIP'}" oninput="setPortfolioView('${kind}','query',this.value)"></label><span>${lang==='en'?'Showing':'显示'} ${matches.length?state.page*pageSize+1:0}–${Math.min((state.page+1)*pageSize,matches.length)} / ${matches.length}</span><button type="button" onclick="setPortfolioView('${kind}','page',${state.page-1})"${state.page===0?' disabled':''}>${lang==='en'?'Previous':'上一页'}</button><button type="button" onclick="setPortfolioView('${kind}','page',${state.page+1})"${state.page>=pages-1?' disabled':''}>${lang==='en'?'Next':'下一页'}</button></div>`;
  }
  return new Set(matches.slice(state.page*pageSize,(state.page+1)*pageSize).map(x=>x.i));
}
function setPortfolioView(kind,key,value) {
  if(!['current','changes'].includes(kind))return;
  const prior=document.getElementById('portfolio-search-'+kind),start=prior?.selectionStart,end=prior?.selectionEnd,direction=prior?.selectionDirection;
  const state=_portfolioViews[kind]||{investor,query:'',page:0};
  if(key==='query'){state.query=String(value);state.page=0;}else if(key==='page'&&Number.isInteger(value))state.page=value;
  _portfolioViews[kind]=state;kind==='current'?renderHoldings():renderChanges();
  if(key==='query'){const input=document.getElementById('portfolio-search-'+kind);input?.focus?.();if(Number.isInteger(start)&&Number.isInteger(end))input?.setSelectionRange?.(start,end,direction||'none');}
}

function renderHoldings() {
  if (globalThis.window?.PublicPortfolio?.render('holdings',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
  const d = data.current;
  const quotes = prices?.quotes || {};
  
  // Calculate MOS for each holding
  const mosItems = [];
  const shownGaps = [];
  
  const visibleRows=portfolioVisibleIndexes('current',d.holdings);
  const rows = d.holdings.map((h,i)=>{
    const q = h.shareType && h.shareType!=='SH' ? null : quotes[h.ticker];
    const costState = holdingCostState(h);
    const cb = costState.basis;
    const quoteOK = q && !q.error && Number.isFinite(q.c) && q.c > 0;
    const currentPrice = quoteOK && !q.stale ? q.c : null;
    const reason = cb ? null : costState.reason==='archive' && data.meta?.snapshotType==='verified_disclosure_snapshot'?(lang==='en'?'Transaction cost undisclosed':'未披露成交成本'):costUnavailableText(costState.reason);
    const mos = cb ? costGap(currentPrice, cb.recent.buy) : null;
    if(mos!==null) shownGaps.push(mos);
    if(!visibleRows.has(i))return '';
    const pct=d.valueQuality?0:(h.value/d.totalValue*100).toFixed(2);
    const weightText=d.valueQuality?'—':pct+'%';
    const amountText=d.valueQuality?(lang==='en'?'Value unverified':'金额待核实'):currSymbol(h.ticker)+h.value.toLocaleString();
    const quoteDate = quoteDateText(q,h.ticker);
    const lifecycle=q?.status==='ceased_trading' ? q.event : null;
    const filedReference=q?.status==='filing_reference' && q.cusip===h.cusip && Number.isFinite(q.filedUnitValue) && q.filedUnitValue>=0 ? q : null;
    const priceHtml = filedReference ? `<span class="current-price">${currSymbol(h.ticker)}${filedReference.filedUnitValue.toFixed(2)}</span><small class="quote-date">${hkEscape(filedReference.asOf)}</small><small class="option-field-note">${lang==='en'?'Filed warrant unit value · not a current quote':'权证申报单价 · 非现价'}</small>` : lifecycle ? `<span class="estimate-unavailable">${lang==='en'?'No longer trading':'已停止交易'}</span><small class="quote-date">${hkEscape(lifecycle.effectiveDate)}</small><small class="option-field-note"><a href="${hkEscape(lifecycle.sourceURL)}" target="_blank" rel="noopener noreferrer">${lang==='en'?'Issuer confirmation':'公司公告'}</a></small>` : quoteOK
      ? `<span class="current-price">${currSymbol(h.ticker)}${q.c.toFixed(2)}</span>${quoteDate?`<small class="quote-date">${quoteDate}</small>`:''}${h.putCall?`<small class="option-field-note">${lang==='en'?'Underlying stock price':'标的股价'}</small>`:''}${q.successorRatio===1&&/^https:\/\/www\.sec\.gov\/Archives\//.test(q.successorSource||'')?`<small class="quote-date"><a href="${hkEscape(q.successorSource)}" target="_blank" rel="noopener noreferrer">${lang==='en'?'1:1 successor quote':'1:1 换股后报价'}</a></small>`:''}${q.stale ? `<small class="quote-stale">${lang==='en'?'Last saved quote':'上次成功报价'}</small>` : ''}`
      : `<span class="estimate-unavailable">${h.shareType && h.shareType!=='SH' ? (lang==='en'?'Principal security · no stock quote':'本金类证券 · 不适用股价') : (lang === 'en' ? 'Quote unavailable' : '暂无报价')}</span>`;
    const mosHtml = h.putCall ? '<span class="estimate-unavailable">—</span>' : costGapHTML(mos, reason, lang==='en', cb?.recent?.kind);
    let costHtml = h.putCall ? '<span class="estimate-unavailable">—</span>' : `<span class="estimate-unavailable">${hkEscape(reason)}</span>`;
    const optionReference=optionNotionalReference(h);
    if(optionReference)costHtml=`<div class="cost-estimate" title="${lang==='en'?'Reported underlying value ÷ underlying shares; not the option premium or purchase cost':'申报标的名义金额÷标的股数；不是期权权利金或买入成本'}"><strong>${currSymbol(h.ticker)}${optionReference.price.toFixed(2)}</strong><small>${lang==='en'?'Filed notional unit price':'申报名义单价'}</small><small>${hkEscape(optionReference.quarter)}</small><small>${lang==='en'?'Option cost undisclosed':'期权成本未披露'}</small></div>`;
    let compactCost = costHtml;
    if (cb) {
      const rc = cb.recent, at = cb.allTime, symbol = currSymbol(h.ticker);
      const costPeriodLabel = ['quarter_reference','adjusted_quarter_reference'].includes(rc.kind) ? (lang==='en'?'Reference quarter: ':'申报参考季度：') : rc.kind === 'scope_initial' ? (lang==='en'?'First quarter in expanded scope: ':'新申报范围首季：') : (lang==='en'?'Last reported addition: ':'最近加仓季度：');
      const isYahoo = rc.source === 'yahoo' || rc.source === 'yfinance';
      const method = rc.kind==='adjusted_quarter_reference' && rc.basisAdjustment!==1 ? (lang==='en'?`Filed value ÷ shares ÷ corporate-action price factor ${rc.basisAdjustment}`:`申报市值÷股数÷公司行动价格调整因子 ${rc.basisAdjustment}`) : isYahoo ? (lang === 'en' ? 'Quarter low × 70% + average × 30%' : '该季低价×70%＋均价×30%')
        : (lang === 'en' ? 'Filed quarter-end value per share; a price proxy, not purchase cost' : '季末申报市值÷股数，仅作价格代理，不是买入成本');
      costHtml = `<div class="cost-estimate" title="${hkEscape(method)}"><strong>${symbol}${rc.buy.toFixed(2)}</strong>
        <small>${rc.kind==='adjusted_quarter_reference'?(lang==='en'?'Corporate-action adjusted reference':'公司行动后季末参考'):rc.kind==='quarter_reference'?(lang==='en'?'Filed quarter-end price':'本季季末价格参考'):rc.kind==='scope_initial'?(lang==='en'?'Scope-entry price reference':'新范围首季价格参考'):t('costRecent')}</small><small>${costPeriodLabel}${hkEscape(rc.quarter)}</small><small class="estimate-method">${isYahoo ? (lang === 'en' ? 'Historical prices' : '历史行情估算') : (lang === 'en' ? '13F price proxy' : '13F 季末价代理')}</small>`;
      if (at) costHtml += `<div class="average-cost">${symbol}${at.avg.toFixed(2)}<small>${t('costAllTime')}</small><small>${costSpanText(at)}</small></div>`;
      else if (costState.averagePending) costHtml += `<small>${costState.averageReason==='corporate_action'?(lang==='en'?'Historical averages do not span this corporate action':'公司行动前后不混算历史均价'):costState.averageReason==='units'?(lang==='en'?'Average awaits historical value verification':'历史金额待核实，暂不显示长期均价'):(lang==='en'?'Average awaiting split correction':'长期均价待拆股校正')}</small>`;
      costHtml += '</div>';
      compactCost = `<span class="mobile-estimate-label">${rc.kind==='adjusted_quarter_reference'?(lang==='en'?'Corporate-action adjusted reference':'公司行动后季末参考'):rc.kind==='quarter_reference'?(lang==='en'?'Quarter-end':'季末参考'):rc.kind==='scope_initial'?(lang==='en'?'Scope ref.':'首季参考'):(lang === 'en' ? 'Buy ref.' : '加仓参考')} <strong>${symbol}${rc.buy.toFixed(2)}</strong></span><small>${costPeriodLabel}${hkEscape(rc.quarter)}</small>`;
      if (costState.averagePending) compactCost += `<small>${costState.averageReason==='corporate_action'?(lang==='en'?'Historical averages do not span this corporate action':'公司行动前后不混算历史均价'):costState.averageReason==='units'?(lang==='en'?'Average awaits historical value verification':'历史金额待核实，长期均价暂缺'):(lang==='en'?'Average awaits split correction':'长期均价待拆股校正')}</small>`;
      if (at) compactCost += `<small class="mobile-average-cost">${lang==='en'?'Avg. (est.)':'历次均价（估）'} ${symbol}${at.avg.toFixed(2)}</small><small>${costSpanText(at)}</small>`;
      if (!rc.kind && mos !== null && mos >= 10) mosItems.push({ticker:h.ticker,name:h.name,cnName:h.cnName||'',mos:mos.toFixed(1),cost:rc.buy,price:currentPrice});
    }
    const mobileCostHtml = h.putCall ? (optionReference?`<div class="mobile-cost-detail">${compactCost}</div>`:'') : `<div class="mobile-cost-detail">${compactCost}${cb?mosHtml:''}</div>`;

    // ── Position change tags ──
    const isEn = lang === 'en';
    const prev = h.prevShares;
    const cur = h.shares || 0;
    const comparable=comparableQuarter() && (comparisonState()!=='scope_partial' || sameManagerCostHistory(h,data));
    let chgTag = comparable ? positionChangeBadge(cur, prev) : '';
    if (h.shareAdjustment && comparable) chgTag += `<small class="split-change-note">${lang === 'en' ? 'Split adjusted' : '拆股后可比'}</small>`;
    const mosCellHtml = mosHtml;
    
    if(!visibleRows.has(i))return '';
    const quantityLabel=h.putCall?(isEn?'Underlying shares':'标的股数'):h.shareType==='PRN'?(isEn?'Principal':'本金'):/\bWARRANT\b/i.test(h.cls||'')?(isEn?'Warrants':'权证份数'):'';
    return `<tr><td class="idx-cell"><span class="idx-num">${i+1}</span></td><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker,h)}</span>${instrumentTag(h)}<span class="name-line">${hkEscape(cn(h.name, h))}</span>${data.meta?.snapshotType==='verified_disclosure_snapshot'&&h.eventDate?`<small class="quote-date">${isEn?'Disclosed':'权益日期'} ${hkEscape(h.eventDate)}</small>`:''}${h.putCall?'':`<span class="sector-badge">${ts(h.sector)}</span>`}<span class="holding-change">${chgTag}</span>${h.putCall?`<button class="option-toggle" type="button" aria-expanded="false" aria-controls="option-position-${i}" onclick="toggleOptionPosition(this)">${isEn?'Option details':'期权明细'}</button>`:''}</td><td class="shares-value-cell"><div style="font-weight:600">${h.shares.toLocaleString('en-US')}</div>${quantityLabel?`<small class="option-field-note">${quantityLabel}</small>`:''}<div style="font-size:.68rem;color:var(--text-lighter);margin-top:2px;">${amountText}</div>${h.putCall?`<small class="option-field-note">${isEn?'Underlying notional value':'标的名义金额'}</small>`:''}<div class="mobile-weight-inline" style="display:none;font-size:.65rem;color:var(--navy);font-weight:600;margin-top:3px;"><span style="font-weight:400;color:var(--text-lighter);">${h.putCall?(isEn?'Notional':'名义占比'):(isEn?'Reported':'申报占比')}</span> ${weightText}</div></td><td class="price-cell">${priceHtml}${mobileCostHtml}</td><td class="cost-cell">${costHtml}</td><td style="width:100px;"><div class="weight-cell"><span class="weight-percent">${weightText}</span>${h.putCall?`<small class="option-field-note">${isEn?'Notional weight':'标的名义占比'}</small>`:''}<div class="bar-wrap"><div class="bar-fill" style="width:${Math.max(0,Math.min(100,Number(pct)||0))}%"></div></div></div></td><td style="width:80px;text-align:center;">${mosCellHtml}</td></tr>${h.putCall?`<tr class="option-details-row" id="option-position-${i}" hidden><td colspan="7">${optionPositionHTML(h,d)}</td></tr>`:''}`;
  }).join('');
  
  // Legend for tags
  const legendHtml = holdingsLegendHTML(d.holdings,shownGaps)+reportingScopeHTML();

  // MOS summary section
  const greenItems = mosItems.filter(m => parseFloat(m.mos) >= 20);
  const watchItems = mosItems.filter(m => parseFloat(m.mos) >= 10 && parseFloat(m.mos) < 20);
  
  let mosSummaryHtml = '';
  if (greenItems.length > 0 && d.holdings.length <= 200) {
    const listHtml = greenItems.map(m => 
      `<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:6px;font-size:.8rem;"><span style="font-weight:600;color:#059669;">${hkEscape(m.ticker)}</span><span style="color:#4b5563;font-size:.68rem;">${hkEscape(cn(m.name,m))}</span><span style="color:#6b7280;font-size:.7rem;">${lang==='en'?'Price lower by':'现价低'} ${m.mos}%</span><span style="color:#9ca3af;font-size:.65rem;">${currSymbol(m.ticker)}${m.cost} → ${currSymbol(m.ticker)}${m.price}</span></span>`
    ).join('');
    mosSummaryHtml = `<div class="position-note">
      <div class="position-note-heading">
        <span>${t('mosTitle')}</span><b>${greenItems.length}</b>
      </div>
      <div class="position-note-description">${t('mosSubtitle')}</div>
      <div class="position-note-items">${listHtml}</div>
    </div>`;
  } else if (watchItems.length > 0) {
    const listHtml = watchItems.map(m => 
      `<span style="display:inline-flex;align-items:center;gap:4px;padding:4px 10px;background:rgba(245,158,11,0.06);border:1px solid rgba(245,158,11,0.15);border-radius:6px;font-size:.8rem;"><span style="font-weight:600;color:#d97706;">${hkEscape(m.ticker)}</span><span style="color:#4b5563;font-size:.68rem;">${hkEscape(cn(m.name,m))}</span><span style="color:#6b7280;font-size:.7rem;">${lang==='en'?'Price lower by':'现价低'} ${m.mos}%</span></span>`
    ).join('');
    mosSummaryHtml = `<div class="position-note watch">
      <div class="position-note-heading"><span>${t('mosWatch')}</span><b>${watchItems.length}</b>
      </div>
      <div class="position-note-items">${listHtml}</div>
    </div>`;
  }
  
  // Broad institutional portfolios use the searchable table and value screen.
  if(d.holdings.length>200)mosSummaryHtml='';
  // Inject MOS summary before the holdings table (only once)
  if (mosSummaryHtml) {
    let existingMos = document.getElementById('mosSummary');
    if (!existingMos) {
      const tabCurrent = document.getElementById('tab-current');
      if (tabCurrent) {
        const mosDiv = document.createElement('div');
        mosDiv.id = 'mosSummary';
        mosDiv.innerHTML = mosSummaryHtml;
        tabCurrent.insertBefore(mosDiv, tabCurrent.querySelector(':scope > .table-wrap'));
      }
    } else {
      existingMos.innerHTML = mosSummaryHtml;
    }
  } else {
    const existingMos = document.getElementById('mosSummary');
    if (existingMos) existingMos.remove();
  }
  const hkRows = recentHKRows.map((h,i) => {
    const quote=hkQuoteState(h.ticker,h.shareClass),derivatives=Array.isArray(h.derivatives)?h.derivatives.reduce((n,d)=>n+d.shares,0):null;
    return `<tr class="reported-hk-row">
      <td class="idx-cell"><span class="idx-num">${data.current.holdings.length+i+1}</span></td>
      <td class="stock-cell"><span class="ticker-line">${hkEscape(h.ticker)}</span><span class="name-line">${hkEscape(hkStockName(h))}</span><small><a href="${hkEscape(h.sourceURL)}" target="_blank" rel="noopener noreferrer">${lang==='en'?'HK · Reported':'港股 · 权益披露'} ${h.asOf} ↗</a></small></td>
      <td><strong>${h.shares.toLocaleString('en-US')}</strong><small class="hk-inline-note">${lang==='en'?'Long-interest share equivalents':'多头权益对应股数'}</small>${derivatives>0?`<small class="hk-inline-note">${lang==='en'?'Includes derivative equivalents':'其中衍生品权益'} ${derivatives.toLocaleString('en-US')}</small>`:''}<small class="hk-inline-note">${lang==='en'?'Of issued class':'占该类已发行股份'} ${h.pct.toFixed(2)}%</small></td>
      <td class="price-cell">${quote.usable?hkQuoteHTML(quote):'—'}</td><td>—</td><td>—</td><td>—</td>
    </tr>`;
  }).join('');
  document.getElementById('holdingsBody').innerHTML = rows + hkRows;
  syncOptionDetailColumns();
  const priceFoot = document.getElementById('priceFoot');
  if (priceFoot) {
    // Remove existing legend if any, then append
    const existingLegend = priceFoot.querySelector('.holdings-legend');
    if (existingLegend) existingLegend.remove();
    const legendDiv = document.createElement('div');
    legendDiv.className = 'holdings-legend';
    legendDiv.innerHTML = legendHtml + `<details class="cost-method-note"><summary>${lang==='en'?'Cost estimation method':'价格估算方法'}</summary><p>${t('priceNote')}</p></details>` + (recentHKRows.length ? `<p>${lang==='en'?'HK rows show dated long interests, which may include derivatives, not a complete live portfolio. Ownership uses the issuer share class, not portfolio allocation; USD 13F totals exclude HK rows.':'港股补充行是带日期的多头权益，可能含衍生品，不表示实时完整持仓。股份权益比例以该类已发行股份为分母，不是组合仓位；美元 13F 合计不含港股。'}</p>` : '');
    priceFoot.appendChild(legendDiv);
  }
}

function instrument(h) { return [(h.putCall || '').toUpperCase(), (h.shareType || 'SH').toUpperCase()].join('|'); }
function consolidateHoldings(holdings) {
  const merged=new Map();
  for (const h of holdings || []) {
    const identity=h.cusip || [(h.ticker || '').toUpperCase().replace(/[./-]/g,''),h.cls || ''];
    const key=JSON.stringify([identity,instrument(h)]);
    if (!merged.has(key)) merged.set(key,{...h});
    else { const r=merged.get(key); for (const field of ['shares','value','prevShares','prevValue']) {
      if (field in r || field in h) r[field]=field.startsWith('prev') && (r[field]==null || h[field]==null)?null:(r[field] || 0)+(h[field] || 0);
    } delete r.shareAdjustment; }
  }
  return [...merged.values()];
}
function sameSecurity(a, b) {
  if(instrument(a)!==instrument(b)) return false;
  if (a.cusip && b.cusip) return a.cusip === b.cusip;
  const ticker = h => (h.ticker || '').toUpperCase().replace(/[./-]/g, '');
  if (ticker(a) && ticker(a) === ticker(b)) return true;
  return !!a.name && a.name === b.name && (a.cls || '') === (b.cls || '') &&
    ((a.ticker || '').startsWith('?') || (b.ticker || '').startsWith('?'));
}
function comparisonState(snapshot=data) {
  const cur=snapshot?.current || {},meta=snapshot?.meta || {},transition=meta.reportingTransition;
  if(meta.portfolioMode==='public_projects') return 'public_projects';
  if(meta.snapshotType) return 'snapshot';
  const idx=q=>{const m=/^(\d{4}) ?Q([1-4])$/.exec(q || '');return m?Number(m[1])*4+Number(m[2]):null;};
  const old=idx(cur.prevQuarter),now=idx(cur.quarter);
  if(old!==null && now!==null && now-old!==1) return 'gap';
  if(transition?.comparisonScopeChanged && transition.fromQuarter===cur.quarter) return (Array.isArray(cur.previousHoldings ?? snapshot.history?.holdings?.[cur.prevQuarter]) && (cur.holdings || []).some(h=>sameManagerCostHistory(h,snapshot)))?'scope_partial':'scope_changed';
  return Array.isArray(cur.previousHoldings) || Array.isArray(snapshot?.history?.holdings?.[cur.prevQuarter]) ? 'comparable':'partial';
}
function quarterlyHoldings(snapshot = data) {
  const cur=snapshot.current, previous=cur.previousHoldings ?? snapshot.history?.holdings?.[cur.prevQuarter];
  let remaining=consolidateHoldings(previous);
  const current=consolidateHoldings(cur.holdings),indexed=current.concat(remaining).every(h=>h.cusip),key=h=>JSON.stringify([h.cusip,instrument(h)]);
  const lookup=indexed?new Map(remaining.map(h=>[key(h),h])):null,consumed=new Set();
  const rows=current.map(h=>{
    const index=indexed?-1:remaining.findIndex(p=>sameSecurity(h,p)),old=indexed?lookup.get(key(h)):index<0?null:remaining.splice(index,1)[0];
    if(indexed&&old)consumed.add(old);
    const row={...h,prevShares:Array.isArray(previous)?old?.shares || 0:h.prevShares ?? null,
      prevValue:Array.isArray(previous)?old?.value || 0:h.prevValue ?? null};
    if(old && h.shareAdjustment?.reportedShares===old.shares) row.prevShares=old.shares*h.shareAdjustment.factor;
    return row;
  });
  if(indexed)remaining=remaining.filter(h=>!consumed.has(h));
  for(const old of remaining) if(old.shares>0 && comparisonState(snapshot)!=='scope_partial') rows.push({...old,shares:0,value:0,prevShares:old.shares,prevValue:old.value,exited:true});
  if(comparisonState(snapshot)==='scope_partial') for(const h of rows) if(!sameManagerCostHistory(h,snapshot)){h.prevShares=null;h.prevValue=null;h.scopeEntry=true;}
  return rows;
}
function comparableQuarter(snapshot = data) { return ['comparable','partial','scope_partial'].includes(comparisonState(snapshot)); }
function comparisonNotice(snapshot = data) {
  const state=comparisonState(snapshot),en=lang==='en';
  if(state==='public_projects')return en?'Official project associations and dated ownership filings; no quarterly position report.':'官方项目关联与带日期的权益披露；没有季度持仓申报。';
  if(state==='snapshot') return data?.meta?.snapshotType==='verified_disclosure_snapshot'?(en?'Individual disclosure dates; no quarterly comparison.':'各股披露日期不同，不作季度比较。'):(en?'Historical disclosure snapshot; no verified quarterly comparison.':'历史披露快照；没有可核实的季度比较。');
  if(state==='gap') return en?'Missing intervening quarterly report; these differences are not quarterly trades.':'中间季度缺失，不能把跨期差异当成本季度买卖。';
  if(state==='partial') return en?'Previous report unavailable; coverage is incomplete and exits cannot be verified.':'上季完整申报未取得；比较范围不全，无法完整核实清仓。';
  if(state==='scope_partial') {
    const rows=snapshot.current.holdings,known=rows.filter(h=>sameManagerCostHistory(h,snapshot)).length;
    const added=rows.filter(h=>!sameManagerCostHistory(h,snapshot)).map(h=>h.ticker).join('、');
    return en?`${known} securities retain the predecessor manager's quarterly comparison. ${added} entered the expanded scope and is not counted as a new purchase.`:`${known} 项证券已核实沿用原管理人范围，可比较季度变化；${added} 为新增覆盖，不计作新建仓。`;
  }
  return en?'Reporting entity and scope changed this quarter; changes cannot be treated as purchases or sales.':'本季申报主体与范围变更，持仓差异不能直接视为买卖。';
}
const CHANGE_KEYS=['new','added','trimmed','exited','hold','unknown'];
function changeCategory(h) {
  if(h.prevShares==null) return 'unknown';
  if(!h.prevShares) return h.shares?'new':'hold';
  if(!h.shares) return 'exited';
  return h.shares>h.prevShares?'added':h.shares<h.prevShares?'trimmed':'hold';
}
function changeLabel(key,en=lang==='en') { return (en?['New','Added','Reduced','Exited','Unchanged','Unverified']:['新建仓','增持','减持','清仓','不变','待比较'])[CHANGE_KEYS.indexOf(key)]; }
function changeText(h,en=lang==='en') {
  if(h.scopeEntry) return en?'First included in reporting scope':'本季新增覆盖';
  const k=changeCategory(h);
  let text=(en?{new:'New position',added:'Added',trimmed:'Reduced',exited:'Exited',hold:'Shares unchanged',unknown:'Previous shares unknown; no trade inference'}:
    {new:'新建仓',added:'增持',trimmed:'减持',exited:'清仓',hold:'股数不变',unknown:'上季股数未知，不判断增减'})[k];
  if(['added','trimmed'].includes(k)) {const pct=Math.abs(h.shares/h.prevShares-1)*100; text+=pct>=.05?pct.toFixed(1)+'%':(en?' (small change)':'（微量变动）');}
  if(h.shareAdjustment) text+=en?' (split adjusted)':'（拆股调整后）';
  return text;
}
function instrumentTag(h) {
  if(/\bWARRANT\b/i.test(h.cls || '')) return `<span class="instrument-tag">${lang==='en'?'Warrant':'认股权证'}</span>`;
  if(h.putCall) return `<span class="instrument-tag">${hkEscape(h.putCall.toUpperCase())} · ${lang==='en'?'long option':h.putCall.toUpperCase()==='PUT'?'看跌期权多头':'看涨期权多头'}</span>`;
  if(h.shareType && h.shareType!=='SH') {
    const convertible=/CONVERT/i.test(h.cls || ''),debt=/BOND|NOTE|DEBENT/i.test(h.cls || '');
    const label=lang==='en'?(convertible?'Convertible bond':debt?'Debt security':'Principal security'):(convertible?'可转债':debt?'债券':'本金类证券');
    return `<span class="instrument-tag">${label} · ${lang==='en'?'principal amount':'本金口径'}</span>`;
  }
  return '';
}
function portfolioFacts(snapshot,name) {
  const state=comparisonState(snapshot);
  let rows=quarterlyHoldings(snapshot);
  if(!['comparable','partial','scope_partial'].includes(state)) rows=consolidateHoldings(snapshot.current.holdings).map(h=>({...h,prevShares:null,prevValue:null}));
  rows.sort((a,b)=>Math.max(b.value || 0,b.prevValue || 0)-Math.max(a.value || 0,a.prevValue || 0));
  const stats=Object.fromEntries(CHANGE_KEYS.map(k=>[k,rows.filter(h=>changeCategory(h)===k).length]));
  const facts=rows.map(h=>({ticker:h.ticker+(h.putCall?' '+h.putCall.toUpperCase():h.shareType && h.shareType!=='SH'?' PRN':''),
    name:h.cnName || h.name || '',change:changeText(h,false),category:changeCategory(h),metric:'披露股数相对上季变化'}));
  let chosen=CHANGE_KEYS.slice(0,4).map(k=>facts.find(f=>f.category===k)).filter(Boolean);
  chosen=chosen.concat(facts.filter(f=>!['hold','unknown'].includes(f.category) && !chosen.includes(f)).slice(0,16));
  chosen=chosen.concat(facts.filter(f=>!chosen.includes(f)).slice(0,Math.max(0,20-chosen.length)));
  return {kind:'investor',investor:name,quarter:snapshot.current.quarter,comparisonState:state,complete:state==='comparable',stats,
    items:facts.filter(f=>chosen.includes(f)).map((f,i)=>({...f,id:'f'+i})),rows};
}
function highlightSelection(facts) {
  const selected=CHANGE_KEYS.slice(0,4).map(k=>facts.items.find(f=>f.category===k)).filter(Boolean);
  const ranked=facts.items.filter(f=>!['hold','unknown'].includes(f.category)).concat(facts.items.filter(f=>['hold','unknown'].includes(f.category)));
  return selected.concat(ranked.filter(f=>!selected.includes(f)).slice(0,5-selected.length)).map(f=>f.id);
}
function investorSummary(snapshot,ids,name,en=lang==='en') {
  if(!comparableQuarter(snapshot)) return comparisonNotice(snapshot);
  const facts=portfolioFacts(snapshot,name),chosen=ids || highlightSelection(facts);
  const known=new Map(facts.items.map(f=>[f.id,f]));
  if(!Array.isArray(chosen)||!chosen.length||chosen.length>5||new Set(chosen).size!==chosen.length||chosen.some(id=>!known.has(id))) return null;
  const directions=new Set(facts.items.filter(f=>CHANGE_KEYS.slice(0,4).includes(f.category)).map(f=>f.category));
  if([...directions].some(k=>!chosen.some(id=>known.get(id).category===k))) return null;
  const overview=CHANGE_KEYS.map(k=>`${k==='unknown'&&facts.comparisonState==='scope_partial'?(en?'New coverage':'新增覆盖'):changeLabel(k,en)}${en?' ':''}${facts.stats[k]}${en?'':'项'}`).join(en?', ':'、');
  const clauses=facts.items.filter(f=>chosen.includes(f.id)).map(f=>{
    const stock=f.ticker.startsWith('?')?f.name || f.ticker.slice(1):f.name && f.name!==f.ticker?`${f.name}（${f.ticker}）`:f.ticker;
    let change=f.change;
    if(en) change=change.replace('上季股数未知，不判断增减','Previous shares unknown; no trade inference').replace('新建仓','New position').replace('股数不变','Shares unchanged').replace('清仓','Exited').replace('增持','Added ').replace('减持','Reduced ').replace('（微量变动）','(small change)').replace('（拆股调整后）','(split adjusted)');
    return stock+(en?': ':'：')+change;
  });
  return en?`${name} ${facts.quarter} (reported shares): ${overview}. Highlights (partial list): ${clauses.join('; ')}.`:
    `${name} ${facts.quarter}（按披露股数比较）：${overview}。重点（非完整名单）：${clauses.join('；')}。`;
}
function costSpanText(at) {
  const first=historyQuarterIndex(at.first),last=historyQuarterIndex(at.last);
  const span=Number.isFinite(first) && Number.isFinite(last) && last>=first?last-first+1:null;
  const buys=at.buy_quarters ?? at.quarters;
  const count=Number.isInteger(buys) && buys>0?(lang==='en'?` · ${buys} buying quarters`:` · 其中${buys}季加仓`):'';
  return `${span?(lang==='en'?`${span} quarters · `:`覆盖${span}个季度 · `):''}${hkEscape(at.first || '')}–${hkEscape(at.last || '')}${count}`;
}

function renderChanges() {
  if (globalThis.window?.PublicPortfolio?.render('changes',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
  const d = data.current, en = lang === 'en';
  if (!comparableQuarter()) { document.getElementById('changesBody').innerHTML = `<tr><td colspan="7">${comparisonNotice()}</td></tr>`; return; }
  const pq = d.prevQuarter || (en ? 'Previous' : '上季');
  const cq = d.quarter || (en ? 'Current' : '本季');
  const valueVerified=!d.valueQuality && !data.history?.excludedValueQuarters?.includes(d.prevQuarter);
  document.getElementById('chPS').innerHTML = `<span class="desktop-change-detail">${hkEscape(pq)} ${en?'Shares':'持股'}</span><span class="mobile-change-detail">${en?'Shares: previous → current':'股数：上季 → 本季'}</span>`;
  document.getElementById('chCS').textContent = cq + (en ? ' Shares' : ' 持股');
  document.getElementById('chPV').innerHTML = `<span class="desktop-change-detail">${hkEscape(pq)} ${en?'Value':'市值'}</span><span class="mobile-change-detail">${en?'Value: previous → current':'市值：上季 → 本季'}</span>`;
  document.getElementById('chCV').textContent = cq + (en ? ' Value' : ' 市值');
  const changeRows=quarterlyHoldings(),visibleRows=portfolioVisibleIndexes('changes',changeRows);
  document.getElementById('changesBody').innerHTML = changeRows.filter((h,i)=>visibleRows.has(i)).map(h => {
    const vd = h.value - h.prevValue;
    const vc = !valueVerified?'qoq-flat':h.prevValue === 0 ? 'qoq-new' : (vd > 0 ? 'qoq-up' : (vd < 0 ? 'qoq-down' : 'qoq-flat'));
    const vs = vd > 0 ? '+' : vd < 0 ? '-' : '';
    const symbol = currSymbol(h.ticker);
    const exited = h.exited ? `<span class="qoq-down"> · ${en ? 'Exited' : '清仓'}</span>` : '';
    const splitNote = h.shareAdjustment ? `<div style="font-size:.65rem;color:var(--text-lighter);">${en ? 'Split adjusted; reported ' : '拆股后可比；原申报 '}${h.shareAdjustment.reportedShares.toLocaleString('en-US')} · ×${h.shareAdjustment.factor}</div>` : '';
    const shareChange=h.scopeEntry?`<span class="qoq-flat">${en?'New coverage':'新增覆盖'}</span>`:fmtShareChg(h.shares,h.prevShares);
    const sharePrevious=h.prevShares==null?'—':h.prevShares.toLocaleString('en-US');
    const valuePrevious=!valueVerified || h.prevValue==null?'—':symbol+fmtVal(h.prevValue);
    const valueCurrent=valueVerified?symbol+fmtVal(h.value):(en?'Value unverified':'金额待核实');
    const valueChange=!valueVerified?'—':h.prevValue==null?(comparisonState()==='scope_partial'?(en?'New coverage':'新增覆盖'):(en?'Unverified':'待比较')):h.prevValue===0?(en?'New':'新进'):`${vs}${symbol}${fmtVal(Math.abs(vd))} (${fmtPct(h.value,h.prevValue)})`;
    const mobileShares=`<div class="mobile-change-detail"><small>${hkEscape(pq)} → ${hkEscape(cq)}</small><span>${sharePrevious} → ${h.shares.toLocaleString('en-US')}</span><div>${shareChange}</div>${splitNote}</div>`;
    const mobileValues=`<div class="mobile-change-detail"><small>${hkEscape(pq)} → ${hkEscape(cq)}</small><span>${valuePrevious} → ${valueCurrent}</span><div class="${vc}">${valueChange}</div></div>`;
    return `<tr><td class="stock-cell"><span class="ticker-line">${fmtTicker(h.ticker,h)}${exited}</span>${instrumentTag(h)}<span class="name-line">${hkEscape(cn(h.name, h))}</span><span class="sector-badge">${ts(h.sector)}</span></td><td class="change-shares"><span class="desktop-change-detail">${h.prevShares===0?'-':(h.prevShares==null?'—':h.prevShares.toLocaleString('en-US'))}${splitNote}</span>${mobileShares}</td><td>${h.shares.toLocaleString('en-US')}</td><td>${shareChange}</td><td class="change-values"><span class="desktop-change-detail">${!valueVerified || h.prevValue==null?'—':h.prevValue===0?'-':symbol+fmtVal(h.prevValue)}</span>${mobileValues}</td><td>${valueCurrent}</td><td class="${vc}">${valueChange}</td></tr>`;
  }).join('');
}

// AI artifacts load independently; holdings and prices never wait for a model.
let _aiSupplement = {entries:{}};
const aiEscape = value => String(value ?? '').replace(/[&<>"']/g, x => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
function snapshotManagerHistory(snapshot) {return snapshot?.meta?.reportingTransition?{managerHistory:(snapshot.current?.holdings || []).filter(h=>h.cusip && sameManagerCostHistory(h,snapshot)).map(h=>h.cusip).sort()}:{};}
function aiInvestorSource(d) {
  if(d?.browserProjection?.sources?.investor)return {browserSource:d.browserProjection.sources.investor};
  const cur=d?.current || {},fields=['ticker','cusip','shares','value','prevShares','prevValue','cnName','name','cls','putCall','shareType','shareAdjustment'];
  const rows=items=>(items || []).map(h=>fields.map(k=>h[k] ?? null));
  return {...(snapshotManagerHistory(d)),quarter:cur.quarter || '',prevQuarter:cur.prevQuarter ?? null,scope:d.meta?.reportingTransition ?? null,snapshotType:d.meta?.snapshotType ?? null,
    valueQuality:cur.valueQuality ?? null,holdings:rows(cur.holdings),previousHoldings:rows(cur.previousHoldings ?? d.history?.holdings?.[cur.prevQuarter])};
}
function aiValueSource(candidates) {
  return candidates.map(c=>[c.ticker ?? null,c.cnName || c.name || null,(c.investors || []).map(h=>[h.id ?? null,h.weight ?? null,h.chg ?? null,h.name ?? null,h.reportQuarter ?? null])]);
}
function aiHoldingsSource(snapshot) {
  if(snapshot?.browserProjection?.sources?.holdings)return {browserSource:snapshot.browserProjection.sources.holdings};
  const cur=snapshot.current || {},meta=snapshot.meta || {};
  const fields=['ticker','cusip','shares','value','cnName','name','cls','putCall','shareType','sector'];
  return {section:'holdings',quarter:cur.quarter ?? null,snapshotType:meta.snapshotType ?? null,
    valueQuality:cur.valueQuality ?? null,holdings:(cur.holdings || []).map(h=>fields.map(k=>h[k] ?? null))};
}
function aiHistorySource(snapshot) {
  if(snapshot?.browserProjection?.sources?.history)return {browserSource:snapshot.browserProjection.sources.history};
  const history=snapshot.history || {},meta=snapshot.meta || {};
  const valid=n=>typeof n==='number' && Number.isFinite(n) && n>=0;
  return {...snapshotManagerHistory(snapshot),section:'history',current:aiHoldingsSource(snapshot),transition:meta.reportingTransition ?? null,
    instrumentHistoryFrom:meta.instrumentHistoryFrom ?? null,instrumentHistoryTickers:meta.instrumentHistoryTickers ?? null,
    quarters:history.quarters || [],values:history.values || [],verification:history.verification ?? null,
    excludedValueQuarters:history.excludedValueQuarters || [],
    recentHoldings:Object.fromEntries(Object.entries(history.holdings || {}).filter(([q])=>{
      const idx=s=>{const m=/^(\d{4}) ?Q([1-4])$/.exec(s || '');return m?Number(m[1])*4+Number(m[2])-1:null;};
      const now=idx(snapshot.current?.quarter),old=idx(q);return now!==null && old!==null && now-old>=0 && now-old<4;
    }).map(([q,rows])=>[q,rows.map(h=>['ticker','cusip','shares','value','cnName','name','cls','putCall','shareType','sector'].map(k=>h[k] ?? null))])),
    holdings:Object.fromEntries(Object.entries(history.holdings || {}).map(([q,rows])=>[q,{
      totalValue:rows.length && rows.every(h=>valid(h.value))?rows.reduce((s,h)=>s+h.value,0):null,
      securities:[...new Set(rows.filter(h=>valid(h.shares) && h.shares>0).map(h=>JSON.stringify([h.cusip || h.ticker,(h.putCall || '').toUpperCase(),(h.shareType || 'SH').toUpperCase()])))].sort()
    }]))};
}
function aiMatchingEntry(key, source) {
  const e=_aiSupplement.entries?.[key];
  // Object field order is not data: serializers can reorder JSON keys.
  const canonical = value => Array.isArray(value) ? value.map(canonical)
    : value && typeof value==='object'
      ? Object.fromEntries(Object.keys(value).sort().map(k=>[k,canonical(value[k])])) : value;
  return e && e.renderVersion===4 && ['model_selection','deterministic'].includes(e.mode) && typeof e.summary==='string' && JSON.stringify(canonical(e.source))===JSON.stringify(canonical(source)) ? e : null;
}
function aiValueFromSource(source,ids,en=lang==='en') {
  if(!Array.isArray(source) || !Array.isArray(ids) || !ids.length || ids.length>3 || new Set(ids).size!==ids.length) return null;
  const labels=en?{new:'New position',added:'Added',trimmed:'Reduced',hold:'Shares unchanged'}:{new:'新建仓',added:'增持',trimmed:'减持',hold:'股数不变'},facts=[];
  for(const [ticker,name,holders] of source.slice(0,12)) for(const [id,weight,chg,investorName,quarter] of holders) {
    const stock=ticker.startsWith('?')?name || ticker.slice(1):name && name!==ticker?`${name}（${ticker}）`:ticker;
    const metric=typeof weight==='number' && weight>=0 && weight<=100?(en?`, ${weight}% of that investor’s disclosed value`:`，占其披露组合市值${weight}%`):'';
    const holder=en?INVESTOR_CFG_BY_ID[id]?.nameEn || investorName || id:investorName || INVESTOR_CFG_BY_ID[id]?.name || id;
    facts.push({id:'f'+facts.length,changed:['new','added','trimmed'].includes(chg),text:`${holder}${quarter?(en?` (${quarter})`:`（${quarter}）`):''}${en?': ':'：'}${stock}${en?' — ':''}${labels[chg] || (en?'Change unknown':'增减未知')}${metric}`});
  }
  if(ids.some(id=>!facts.some(f=>f.id===id))) return null;
  if(facts.some(f=>f.changed) && !facts.some(f=>ids.includes(f.id) && f.changed)) return null;
  return (en?'Selected holders’ latest disclosures: ':'按各投资人最新披露组合：')+facts.filter(f=>ids.includes(f.id)).map(f=>f.text).join(en?'; ':'；')+(en?'.':'。');
}
async function refreshAISupplements() {
  if(data?.browserProjection)return;
  const ctrl=new AbortController(), timer=setTimeout(()=>ctrl.abort(),15000);
  try {
    const response=await fetch('ai_supplement.json?v=77&t='+Math.floor(Date.now()/300000),{signal:ctrl.signal});
    if (!response.ok) return;
    const payload=await response.json();
    if (payload.schemaVersion!==2 || !payload.entries || typeof payload.entries!=='object') return;
    _aiSupplement=payload;
    if (data) renderActiveInvestorView(true);
    _homeworkCache=null;
    if(document.getElementById('tab-homework') && !document.getElementById('tab-homework').classList.contains('d-none')) renderHomework();
  } catch {} finally { clearTimeout(timer); }
}

function aiInvestorFallback(snapshot) { return investorSummary(snapshot,null,INVESTOR_CFG_BY_ID[investor]?.name || '',lang==='en'); }
function aiValueFallback(candidates) {
  const en=lang==='en',labels=en?{new:'New position',added:'Added',trimmed:'Reduced',hold:'Shares unchanged'}:{new:'新建仓',added:'增持',trimmed:'减持',hold:'股数不变'};
  const rows=candidates.flatMap(c=>(c.investors || []).map(h=>({c,h})));
  rows.sort((a,b)=>(a.h.chg==='hold')-(b.h.chg==='hold'));
  return rows.length ? (en?'Selected holders’ latest disclosures: ':'按各投资人最新披露组合：')+rows.slice(0,3).map(({c,h})=>{
    const name=c.cnName || c.name || '', stock=name && name!==c.ticker ? `${name}（${c.ticker}）`:c.ticker;
    const weight=typeof h.weight==='number' && Number.isFinite(h.weight) && h.weight>=0 && h.weight<=100 ? (en?`, ${h.weight}% of that investor’s disclosed value`:`，占其披露组合市值${h.weight}%`):'';
    return `${h.name || INVESTOR_LABELS[h.id] || h.id}${en?': ':'：'}${stock}${en?' — ':''}${labels[h.chg] || (en?'Change unknown':'增减未知')}${weight}`;
  }).join(en?'; ':'；')+(en?'.':'。') : '';
}

function scopedSummaryEntry(kind,snapshot) {
  if(!snapshot?.current) return null;
  const source=kind==='holdings'?aiHoldingsSource(snapshot):aiHistorySource(snapshot);
  const entry=aiMatchingEntry(kind+':'+investor,source),facts=entry?.facts;
  if(!facts || facts.kind!==kind || facts.investor!==INVESTOR_CFG_BY_ID[investor]?.name || facts.quarter!==snapshot.current.quarter) return null;
  if(kind==='holdings' && entry.briefing?.format!=='concise_holdings_v2')return null;
  if(JSON.stringify(entry.briefing)!==JSON.stringify(orderedBriefing(facts.briefing,entry.selection?.topicIds)))return null;
  const ids=entry.selection?.factIds,items=facts.items;
  if(!Array.isArray(ids) || !ids.length || ids.length>3 || new Set(ids).size!==ids.length || !Array.isArray(items)) return null;
  if(items.some(f=>!Array.isArray(f.text) || f.text.length!==2 || f.text.some(t=>typeof t!=='string'))) return null;
  if(ids.some(id=>!items.some(f=>f.id===id)) || (facts.requiredIds || []).some(id=>!ids.includes(id))) return null;
  const selected=items.filter(f=>ids.includes(f.id)),title=kind==='holdings'?'持仓结构':'历史轨迹';
  if(entry.summary!==`${facts.investor} · ${title}：${selected.map(f=>f.text[0]).join('')}`) return null;
  return {...entry,texts:selected.map(f=>profileText(f.text))};
}
function scopePanelHTML(kind,texts,entry=null) {
  const en=lang==='en';
  const titles={holdings:['持仓结构解读','Holdings Structure'],changes:['季度变化解读','Quarterly Changes'],history:['历史轨迹解读','Historical Pattern']};
  const explanation=kind==='holdings'
    ? (en?'Based on this filing’s composition. HK supplementary rows retain their own dates; they are outside the USD 13F totals.':'按本次申报的组合结构解读；港股补充行保留各自日期，不计入美元 13F 统计。')
    : kind==='history'?(en?'History is based on dated disclosures. Changes in reported value are not investment returns.':'依据带日期的历史披露；申报市值变化不等于投资回报。')
    : (en?'All reported share changes are included below. Net differences are not transaction records or evidence of trading motives.':'下方保留全部披露股数变化；净变化不是逐笔成交记录，也不证明交易动机。');
  const fallbackTitle=data.meta?.snapshotType?(en?'Historical archive: present holdings are unconfirmed':'历史档案：当前持仓尚不能确认'):
    kind==='history' && data.history?.verification?.status==='unverified'?(en?'Dated history is insufficient for a reliable trend':'历史日期与范围不完整，暂不形成趋势结论'):profileText(titles[kind]);
  const fallback=kind==='holdings'?holdingsConclusion(data):{version:1,headline:[fallbackTitle,fallbackTitle],lead:[texts.join(' '),texts.join(' ')],details:[],notes:[[explanation,explanation]]};
  const selected=validBriefing(entry?.briefing) && (kind!=='holdings' || entry.briefing.format==='concise_holdings_v2')?entry.briefing:fallback;
  return `<div class="scope-heading"><h3>${profileText(titles[kind])}</h3><span class="scope-badge">${aiEscape(data.current?.quarter || '')}</span></div>
    ${briefingHTML(selected)}${globalThis.window?.DisclosureAnalysis?.render(kind,data,en)||''}`;
}
function holdingsConclusion(snapshot) {
  const rows=consolidateHoldings(snapshot.current.holdings).sort((a,b)=>b.value-a.value),en=lang==='en';
  const pair=text=>[text,text],result=(headline,lead,details=[])=>({version:1,format:'concise_holdings_v2',headline:pair(headline),lead:pair(lead),details,notes:[]});
  if(snapshot.meta?.snapshotType)return result(en?'An archive, with present holdings unconfirmed':'这是历史档案，当前持仓尚不能确认',en?`${rows.length} historically disclosed securities, with differing disclosure and valuation dates.`:`保留 ${rows.length} 项历史披露证券，披露日期和估值时点不统一。`);
  if(snapshot.current.valueQuality)return result(en?'Reported values await verification':'申报金额待核实',en?`${rows.length} securities; value percentages cannot be compared reliably.`:`本期 ${rows.length} 项证券；金额占比暂不能可靠比较。`);
  const total=rows.reduce((s,h)=>s+h.value,0);
  if(!total)return result(en?'No reported amount available':'本期没有可计算权重的申报金额',en?'Security records retained.':'保留证券记录。');
  const pct=n=>99.9<=Math.abs(n) && Math.abs(n)<100?n.toFixed(2):n!==0 && Math.abs(n)<.001?n.toPrecision(3):Math.abs(n)>=1?n.toFixed(1):n.toFixed(3).replace(/\.?0+$/,'');
  const name=h=>`${(en?h.name:h.cnName) || h.name || h.ticker} (${h.ticker}${h.putCall?' '+h.putCall.toUpperCase():h.shareType && h.shareType!=='SH'?' PRN':''})`;
  const top=rows.slice(0,3),weight=top.reduce((s,h)=>s+h.value,0)/total*100;
  const headline=en?`Top ${top.length}: ${pct(weight)}% — ${weight>=60?'concentrated':'broadly spread'}`:`${top.length===3?'前三项':`前 ${top.length} 项`}占 ${pct(weight)}%，${weight>=60?'持仓较集中':'持仓较分散'}`;
  const lead=top.map(h=>`${name(h)} ${pct(h.value/total*100)}%`).join(en?'; ':'；')+(en?'.':'。')+(rows.length>top.length?(en?` The other ${rows.length-top.length} positions total ${pct(100-weight)}%.`:`其余 ${rows.length-top.length} 项合计 ${pct(100-weight)}%。`):'');
  const details=[],add=(label,text)=>details.push({label:pair(label),text:pair(text)}),groups=new Map();
  for(const h of rows.filter(h=>!h.putCall && (!h.shareType || h.shareType==='SH') && !/\bWARRANT\b/i.test(h.cls || ''))) {
    const key=/^[A-Z0-9*@#]{8}[0-9]$/.test(h.cusip || '')?h.cusip.slice(0,6):JSON.stringify([h.ticker,h.cusip]);
    if(!groups.has(key))groups.set(key,[]);groups.get(key).push(h);
  }
  const group=[...groups.values()].sort((a,b)=>b.reduce((s,h)=>s+h.value,0)-a.reduce((s,h)=>s+h.value,0))[0];
  if(group?.length>1) {
    const combined=group.reduce((s,h)=>s+h.value,0)/total*100,names=group.map(name).join(en?'; ':'、');
    add(en?'Combined share classes':'合并看同一家公司',en?`${names} total ${combined.toFixed(1)}%. These separately listed share classes belong to the same issuer.`:`${names} 合计 ${combined.toFixed(1)}%。表中分列的不同股份类别，实际对应同一发行人。`);
  }
  const small=rows.filter(h=>h.value/total<.01);
  if(small.length){const weight=small.reduce((s,h)=>s+h.value,0)/total*100;add(en?'Small positions':'小仓位',en?`${small.length} positions each below 1% total ${weight.toFixed(2)}%.`:`${small.length} 项各自不足 1%，合计 ${weight.toFixed(2)}%。`);}
  const options=rows.filter(h=>h.putCall);
  if(options.length) {
    let text=options.slice(0,2).map(h=>en?`${h.ticker} ${h.putCall.toUpperCase()} covers ${h.shares.toLocaleString('en-US')} underlying shares, ${(h.value/total*100).toFixed(2)}% notional weight`:`${h.ticker} ${h.putCall.toUpperCase()} 覆盖标的 ${h.shares.toLocaleString('en-US')} 股、名义占比 ${(h.value/total*100).toFixed(2)}%`).join(en?'; ':'；');
    if(options.length>2){const weight=options.slice(2).reduce((s,h)=>s+h.value,0)/total*100;text+=en?`; the other ${options.length-2} options total ${weight.toFixed(2)}% notional weight`:`；其余 ${options.length-2} 项期权名义占比合计 ${weight.toFixed(2)}%`;}
    text+=en?'. Weights use underlying notional values, not option premiums.':'。比例按标的名义金额计算，不是权利金占比。';
    details.unshift({label:pair(en?'Option scale':'期权规模'),text:pair(text)});
  }
  return result(headline,lead,details.slice(0,3));
}
function validBriefing(b) {
  const bilingual=x=>Array.isArray(x) && x.length===2 && x.every(t=>typeof t==='string' && t.trim());
  return b?.version===1 && bilingual(b.headline) && bilingual(b.lead) && (b.readerGuide==null || bilingual(b.readerGuide)) && Array.isArray(b.details) && b.details.length<=3 && b.details.every(d=>bilingual(d.label) && bilingual(d.text)) && Array.isArray(b.notes) && b.notes.every(bilingual);
}
function orderedBriefing(b,topics=[]) {
  if(!validBriefing(b) || !Array.isArray(topics) || new Set(topics).size!==topics.length || topics.some(t=>typeof t!=='string' || !/^t[0-2]$/.test(t) || Number(t.slice(1))>=b.details.length))return null;
  const order=topics.concat(b.details.map((_,i)=>'t'+i).filter(t=>!topics.includes(t)));
  return {...b,details:order.map(t=>b.details[Number(t.slice(1))])};
}
function briefingHTML(b) {
  if(!validBriefing(b))return '';
  const en=lang==='en';
  return `<div class="${b.format==='concise_holdings_v2'?'briefing-compact':'briefing-content'}"><h4 class="briefing-headline">${aiEscape(profileText(b.headline))}</h4><p class="briefing-lead">${aiEscape(profileText(b.lead))}</p>
    ${b.details.length?`<ol class="briefing-drivers">${b.details.map(d=>`<li><strong>${aiEscape(profileText(d.label))}</strong><p>${aiEscape(profileText(d.text))}</p></li>`).join('')}</ol>`:''}
    ${b.notes.length?`<details class="briefing-notes"><summary>${en?'Scope and calculation notes':'统计范围与计算说明'}</summary>${b.notes.map(n=>`<p>${aiEscape(profileText(n))}</p>`).join('')}</details>`:''}</div>`;
}
function scopedFallback(kind) {
  const en=lang==='en',cur=data.current;
  if(kind==='history') {
    if(data.history?.verification?.status==='unverified')return [en?'The archive lacks comparable, dated quarterly snapshots. A reliable history cannot be reconstructed.':'历史档案缺少可比、带日期的季度快照，暂不能重建可靠的长期轨迹。'];
    const {quarters,values}=historySeries(data.history);
    return [generateHistoryInsight(quarters,values)];
  }
  const rows=consolidateHoldings(cur.holdings),total=rows.reduce((s,h)=>s+h.value,0);
  const texts=[en?`This filing lists ${rows.length} securities. Share classes and option types are counted separately.`:`本次披露 ${rows.length} 项证券，股份类别与期权分别计数。`];
  if(data.meta?.snapshotType)texts.push(en?'This is an archived disclosure snapshot, not a current complete portfolio.':'这里是历史披露快照，不能作为当前完整组合。');
  else if(cur.valueQuality)texts.push(en?'Reported values remain unverified; value and concentration analysis is suspended.':'申报值量级待核实，暂不解读金额与集中度。');
  else if(total>0){const top=rows.sort((a,b)=>b.value-a.value).slice(0,3);texts.push(en?`The top three reported securities (${top.map(h=>h.ticker).join(', ')}) account for ${(top.reduce((s,h)=>s+h.value,0)/total*100).toFixed(1)}% of this filing.`:`前三大申报证券（${top.map(h=>h.ticker).join('、')}）合计占本次披露 ${(top.reduce((s,h)=>s+h.value,0)/total*100).toFixed(1)}%。`);}
  return texts;
}
function renderScopedInsight(kind) {
  const el=document.getElementById(kind==='holdings'?'holdingsInsight':'historyInsight');
  if(!el || !data) return;
  const entry=scopedSummaryEntry(kind,data);
  el.innerHTML=scopePanelHTML(kind,entry?.texts || scopedFallback(kind),entry);
  el.style.display='';
}

function renderInsights(only=null) {
  if (globalThis.window?.PublicPortfolio?.render('insights',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
  if(!data?.current) return;
  const d=data.current,ins = [];

  // AI 摘要（如果有）
  let localAI = aiMatchingEntry('investor:'+investor,aiInvestorSource(data));
  const summaryName=INVESTOR_CFG_BY_ID[investor]?.name || '';
  if(localAI && localAI.summary!==investorSummary(data,localAI.selection?.factIds,summaryName,false)) localAI=null;
  if(localAI?.briefing && JSON.stringify(localAI.briefing)!==JSON.stringify(orderedBriefing(localAI.facts?.briefing,localAI.selection?.topicIds)))localAI=null;
  // Unverified legacy prose is never used as a fallback.
  const aiSummary = comparableQuarter() ? (localAI ? investorSummary(data,localAI.selection.factIds,summaryName) : aiInvestorFallback(data)) : comparisonNotice();
  const quarterText=aiSummary?.split(lang==='en'?'Highlights (partial list): ':'重点（非完整名单）：').at(-1) || comparisonNotice();
  const summary=document.getElementById('changesAISummary');
  if(summary) summary.innerHTML=scopePanelHTML('changes',[quarterText],localAI);
  if(!only){renderScopedInsight('holdings');renderScopedInsight('history');}
  const en=lang==='en', facts=portfolioFacts(data,summaryName);
  if(!comparableQuarter()) ins.push(aiEscape(comparisonNotice()));
  else {
    ins.push(`<strong>${CHANGE_KEYS.map(k=>`${changeLabel(k,en)} ${facts.stats[k]}`).join(en?' · ':' · ')}</strong><br><small>${en?'All share changes included, with no minimum percentage. Net report differences are not execution records.':'所有股数变化均计入，无幅度门槛；这里是披露股数净变化，不是逐笔成交记录。'} ${facts.complete?'':aiEscape(comparisonNotice())}</small>`);
    for(const k of ['trimmed','exited','added','new','unknown']) {
      const group=facts.rows.filter(h=>changeCategory(h)===k);
      if(!group.length) continue;
      ins.push(`<details><summary>${changeLabel(k,en)} · ${group.length} ${en?'positions — full list':'项 · 完整名单'}</summary><ul class="change-detail-list">${group.map(h=>{
        const quantity=h.prevShares==null?'—':h.prevShares.toLocaleString('en-US');
        const delta=h.prevShares==null?'':` · ${h.shares-h.prevShares>0?'+':''}${(h.shares-h.prevShares).toLocaleString('en-US')}`;
        return `<li><strong>${aiEscape(h.ticker)} ${instrumentTag(h)}</strong> ${aiEscape(cn(h.name,h))} · ${changeText(h,en)}<br><small>${quantity} → ${h.shares.toLocaleString('en-US')}${delta} ${h.shareType==='PRN'?(en?'principal':'本金'):(en?'shares':'股')}${h.shareAdjustment?(en?' · Split adjusted':' · 拆股后可比'):''}</small></li>`;
      }).join('')}</ul></details>`);
    }
  }
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
    const v = Number.isFinite(history.portfolioValues?.[i]) ? history.portfolioValues[i] : Array.isArray(holdings) && holdings.length && holdings.every(h => typeof h.value === 'number' && Number.isFinite(h.value) && h.value >= 0)
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
    const transition=data?.meta?.reportingTransition;
    const boundary=transition?.comparisonScopeChanged?historyQuarterIndex(transition.fromQuarter):NaN;
    if (!i || historyQuarterIndex(q) - historyQuarterIndex(quarters[i-1]) !== 1 ||
      (Number.isFinite(boundary) && historyQuarterIndex(quarters[i-1])<boundary && historyQuarterIndex(q)>=boundary)) segments.push([]);
    segments[segments.length-1].push(i);
  });
  return segments;
}
function generateHistoryInsight(quarters, values) {
  const isEn = lang === 'en';
  if (!values.length) return isEn ? 'No historical data available.' : '暂无历史数据。';
  if(data?.meta?.reportingTransition?.comparisonScopeChanged) return isEn
    ? `Reporting scope changed in ${data.meta.reportingTransition.fromQuarter}. Latest reported value: ${quarters.at(-1)} ${historyMoney(values.at(-1))}. Cross-scope changes are not portfolio growth or investment returns.`
    : `申报范围在 ${data.meta.reportingTransition.fromQuarter} 改变。最新披露值：${quarters.at(-1)} ${historyMoney(values.at(-1))}；不跨范围判断组合增长或投资回报。`;
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
  const sourceIssues=Object.entries(data?.history?.filing_sources || {}).filter(([q,s])=>quarters.includes(q) && s.sourceReconciliation && s.sourceReconciliation.status!=='reconciled');
  if(sourceIssues.length) txt += isEn ? `${sourceIssues.length} historical filings contain missing or inconsistent cover totals; chart values sum the original line items. ` : `${sourceIssues.length} 期历史原表的封面汇总缺失或与明细不一致；图中按原始持仓逐项加总。`;
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
  if (globalThis.window?.PublicPortfolio?.render('history',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
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
    renderScopedInsight('history');
    return;
  }
  const isMobile = window.innerWidth < 640;

  renderScopedInsight('history');

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
    tooltip.innerHTML = `<div style="font-weight:600;margin-bottom:2px;">${hkEscape(q)}</div><div>${historyMoney(v, 3)} ${chgStr}</div>`;
    const cx = gX(idx), cy = gY(v);
    const scaleX = rect.width / canvas.width, scaleY = rect.height / canvas.height;
    tooltip.style.left = Math.max(0, Math.min(cx * scaleX + 12, rect.width - 210)) + 'px';
    tooltip.style.top = (cy * scaleY - 16) + 'px';
    tooltip.style.display = '';
  };
  canvas.onmouseleave = () => { tooltip.style.display='none'; };
}

// ── TIMELINE ──
let timelinePageKey='', timelineLimit=200;
function showMoreTimeline(){timelineLimit+=200;renderTimelineTable();}
async function renderTimelineTable() {
  if (globalThis.window?.PublicPortfolio?.render('timeline',{data,lang,config:INVESTOR_CFG_BY_ID[investor]})) return;
  const container = document.getElementById('timelineCanvas');
  if(document.getElementById('tab-history')?.classList?.contains('d-none')) return;
  if (!data) return;
  if (data.history?.verification?.status === 'unverified') {
    container.innerHTML = `<p style="color:var(--text-lighter);">${lang === 'en' ? 'A holdings timeline requires dated historical snapshots.' : '持仓时间轴需要可核对日期的历史快照，暂不展示。'}</p>`;
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
    for (const h of consolidateHoldings(hdata[q])) {
      if(instrumentHistoryIncludes(data.meta||{},h.ticker) && q<data.meta.instrumentHistoryFrom) continue;
      if (!(h.shares > 0)) continue;
      const tk = (h.cusip || h.ticker)+'|'+instrument(h);
      if (!tickerInfo[tk]) tickerInfo[tk] = {ticker:h.ticker,cusip:h.cusip,shareType:h.shareType,putCall:h.putCall,cls:h.cls,first: q, last: q, quarters: [], sector: h.sector, name: h.name, cnName: h.cnName||'', maxShares: 0, curShares: 0};
      else tickerInfo[tk].last = q;
      tickerInfo[tk].quarters.push(q);
      const factor = shareActionsFor(h,data).filter(a =>
        q < a.quarter && a.quarter <= latest
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
  const pageKey=investor+'|'+lang+'|'+latest;
  if(timelinePageKey!==pageKey){timelinePageKey=pageKey;timelineLimit=200;}
  const visible=entries.length>200 ? [...entries].sort((a,b)=>Number(b.active)-Number(a.active)||a.first.localeCompare(b.first)).slice(0,timelineLimit) : entries;
  visible.forEach(e => {
    if (e.active && e.curShares > 0 && e.maxShares > 0) {
      const ratio = (e.curShares / e.maxShares * 100).toFixed(0);
      const s = e.curShares === e.maxShares
        ? `<span style="color:#10b981;">${isEn ? 'At peak shares' : '持股处于历史峰值'}</span>`
        : `<span style="color:#f59e0b;">${isEn ? `Shares at ${ratio}% of peak` : `持股为峰值的 ${ratio}%`}</span>`;
      const shareInfo = ratio < 100 ? `<br><span style="font-size:.68rem;color:var(--text-lighter);">${isEn?'Peak':'最高'} ${fmtNum(e.maxShares)} → ${isEn?'Current':'当前'} ${fmtNum(e.curShares)}</span>` : '';
      e.shareInfo = s + shareInfo + (e.splitAdjusted ? `<br><small>${isEn ? 'Split-adjusted shares' : '拆股后可比股数'}</small>` : '');
    } else {
      e.shareInfo = '<span style="color:var(--text-lighter);">—</span>';
    }
    let status;
    if (e.gaps.length > 0) {
      const soldQ = e.gaps[0];
      const boughtQ = e.gaps[e.gaps.length - 1];
      const afterGap = quarters[quarters.indexOf(boughtQ) + 1];
      status = `<span style="color:#f59e0b;font-weight:600;">◐ ${soldQ} ${isEn?'No holding disclosed':'未披露持仓'}</span><br><span style="font-size:.68rem;color:var(--text-lighter);">→ ${afterGap} ${isEn?`Disclosed again (${e.gaps.length} quarters absent)`:`再次披露（空窗${e.gaps.length}季）`}</span>`;
    } else if (e.active) {
      status = '<span style="color:#10b981;font-weight:600;">● '+(isEn?'Currently disclosed':'当前披露持有')+'</span>';
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
      <td class="stock-cell"><span class="ticker-line">${fmtTicker(e.ticker,e)}</span>${instrumentTag(e)}<span class="name-line">${hkEscape(cn(e.name, e))}</span><span class="sector-badge">${ts(e.sector)}</span><span style="display:block;font-size:.65rem;color:var(--text-lighter);margin-top:2px;">${e.qCount} ${isEn?'quarters':'季'}</span></td>
      <td style="white-space:nowrap">${hkEscape(e.first)}</td>
      <td style="white-space:nowrap">${hkEscape(e.last)}</td>
      <td>${status}<div style="margin-top:4px">${e.shareInfo}</div></td>
    </tr>`;
  });
  html += '</tbody></table></div>';
  if(visible.length<entries.length)html+=`<button class="btn-refresh timeline-more" type="button" onclick="showMoreTimeline()">${isEn?`Show more history (${visible.length} / ${entries.length})`:`展开更多历史（已显示 ${visible.length} / ${entries.length} 项）`}</button>`;
  html += '<div style="font-size:.68rem;color:var(--text-lighter);margin-top:8px;">'+(isEn?'● Currently disclosed | ○ No longer disclosed | ◐ Reappears after absent quarters':'● 当前披露持有 | ○ 最新申报未再披露 | ◐ 缺席后再次披露')+'</div>';
  if (isHK) html += '<div style="font-size:.68rem;color:var(--text-lighter);margin-top:4px;">⚠️ Webb 港股持仓数据来源于公开权益披露，非 13F 报告</div>';
  if(data.meta?.instrumentHistoryFrom) html+=`<p class="data-quality-note">${isEn?'Instrument types verified from':'期权相关证券仅展示已核实类别的历史，起点：'} ${data.meta.instrumentHistoryFrom}</p>`;
  container.innerHTML = html;
}

function hkEvidenceView(holding) {
  const records = (holding.verified_disclosures || []).filter(r =>
    !r.superseded_by &&
    /^\d{4}-\d{2}-\d{2}$/.test(r.event_date || '') &&
    Number.isSafeInteger(r.shares) && r.shares >= 0 &&
    typeof r.pct === 'number' && Number.isFinite(r.pct) && r.pct >= 0 && r.pct <= 100 &&
    r.filing_ref && /^https:\/\/di\.hkex\.com\.hk\//.test(r.source_url || '') &&
    (!r.form_url || /^https:\/\/di\.hkex\.com\.hk\//.test(r.form_url))
  ).sort((a,b) => a.event_date.localeCompare(b.event_date) || (a.filing_date || '').localeCompare(b.filing_date || '') || a.filing_ref.localeCompare(b.filing_ref));
  return {records, first: records[0], latest: records[records.length - 1], status: '当前持仓未核实'};
}
function hkEscape(value) {
  return String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
function hkEntityKey(entity) {return (entity || '').split(/\(\s*(?:formerly|previously)/i)[0].toLowerCase().replace(/[^\p{L}\p{N}]/gu,'');}
function hkDisclosureGroups(holdings) {
  return (holdings || []).flatMap(h=>{
    const evidence=hkEvidenceView(h), byEntity=new Map();
    for(const r of evidence.records) {const key=hkEntityKey(r.entity);if(!byEntity.has(key)) byEntity.set(key,[]);byEntity.get(key).push(r);}
    const groups=[];
    for(const records of byEntity.values()) {
      const classes=[...new Set(records.filter(r=>r.verification==='hkex_form' && r.share_class).map(r=>r.share_class))];
      for(const shareClass of classes.length?classes:['']) {
        const typed=records.filter(r=>r.share_class===shareClass);
        const history=records.filter(r=>r.share_class===shareClass || !r.share_class);
        // A newer notice without a verified class must not be hidden behind an
        // older original form. It blocks presenting that old form as latest.
        const latest=history.at(-1) || typed.at(-1) || records.at(-1);
        const previous=typed.filter(r=>r.verification==='hkex_form' && r.filing_ref!==latest.filing_ref).at(-1);
        groups.push({...h,entity:latest.entity,shareClass,records:history,latest,previous:latest.verification==='hkex_form'?previous:null});
      }
    }
    return groups.length?groups:[{...h,records:[],latest:null,previous:null}];
  }).sort((a,b)=>(b.latest?.event_date || '').localeCompare(a.latest?.event_date || '') || a.ticker.localeCompare(b.ticker));
}
function hkFinancialLatest(holding,entity) {
  return (holding.financial_disclosures || []).filter(r=>r.verification==='sec_ixbrl_investment_value' &&
    /^https:\/\/www\.sec\.gov\/Archives\/edgar\/data\//.test(r.source_url || '') &&
    Number.isFinite(r.reported_value_usd) && r.reported_value_usd>=0 &&
    hkEntityKey(r.entity)===hkEntityKey(entity)).sort((a,b)=>a.as_of.localeCompare(b.as_of)).at(-1);
}

let recentHKRows = [];
let hkDisclosures = null;
function latestReportedHKHoldings(payload,cfg,quarter,now=Date.now()) {
  // A dated, recently checked original form can supplement the table; old
  // interests and discovery/search results cannot establish a current position.
  const q=/^(\d{4}) Q([1-4])$/.exec(quarter || '');
  const checked=Date.parse(payload?.audit?.checkedAt);
  if(!q || !cfg.source13F || payload?.audit?.status!=='checked' ||
    !Number.isFinite(checked) || checked>now || now-checked>7*86400000) return [];
  const cutoff=Math.max(Date.UTC(Number(q[1]),Number(q[2])*3,0),now-120*86400000);
  const manager=hkEntityKey(cfg.manager),selected=new Map();
  for(const g of hkDisclosureGroups(payload.holdings)) {
    const r=g.latest,date=Date.parse(r?.event_date);
    const lastForManager=hkEvidenceView(g).records.filter(x=>hkEntityKey(x.entity)===manager && (!x.share_class || x.share_class===r?.share_class)).at(-1);
    if(!r || hkEntityKey(r.entity)!==manager || r.verification!=='hkex_form' ||
      !lastForManager || r.filing_ref!==lastForManager.filing_ref ||
      !r.history_complete || r.position!=='long' || !hkListedClass(r.share_class) ||
      !Number.isFinite(date) || date<cutoff || date>now || r.pct<5 || r.shares<=0) continue;
    const financial=hkFinancialLatest(g,r.entity);
    if(financial && financial.as_of>=r.event_date && financial.reported_value_usd===0) continue;
    // A single security row: controlled entities often report the same shares.
    if(selected.has(g.ticker)) {selected.set(g.ticker,null);continue;}
    selected.set(g.ticker,{ticker:g.ticker,name:g.name,cnName:g.cnName || g.legacy_name,
      shares:r.shares,pct:r.pct,shareClass:r.share_class,derivatives:r.derivative_interests,asOf:r.event_date,sourceURL:r.form_url || r.source_url});
  }
  return [...selected.values()].filter(Boolean);
}
async function loadHKDisclosures(cfg,{signal,stamp,fresh}={}) {
  if(!cfg.hkFile) return null;
  const ctrl=new AbortController(),timer=setTimeout(()=>ctrl.abort(),4000);
  const abort=()=>ctrl.abort();signal?.addEventListener('abort',abort,{once:true});
  if(signal?.aborted) ctrl.abort();
  try {
    const r=await fetch(cfg.hkFile+'?v=76&t='+stamp,{signal:ctrl.signal,cache:fresh?'no-store':'default'});
    if(!r.ok) return null;
    const payload=await r.json();
    return Array.isArray(payload?.holdings)?payload:null;
  } catch(_) { return null; }
  finally {clearTimeout(timer);signal?.removeEventListener('abort',abort);}
}

function hkStockName(h) {
  const labels={'09992.HK':['泡泡玛特',/pop\s*mart/i],'01658.HK':['邮储银行',/postal\s+savings|\bPSBC\b/i],'01211.HK':['比亚迪',/\bBYD\b/i],'01766.HK':['中国中车',/\bCRRC\b/i]};
  const alias=labels[h.ticker];
  // Never resurrect an unverified legacy Chinese name after an issuer rename.
  return lang!=='en' && alias?.[1].test(h.name || '')?alias[0]:(h.name || h.ticker);
}
function hkShareClassLabel(value) {
  if(lang==='en') return value || 'Class awaits form verification';
  return ({'ordinary shares':'普通股','h shares':'H 股','a shares':'A 股'})[(value || '').toLowerCase()] || value || '股份类别待原表核验';
}
function hkListedClass(value) {return ['ordinary shares','h shares'].includes((value || '').toLowerCase().replace(/-/g,' '));}
function hkQuoteState(ticker,shareClass,now=Date.now()) {
  const q=prices?.quotes?.[ticker],date=Number.isFinite(q?.t)?q.t*1000:NaN;
  const listed=hkListedClass(shareClass);
  const valid=listed && q?.currency==='HKD' && !q.error && Number.isFinite(q.c) && q.c>0 && Number.isFinite(date) && date<=now+300000;
  const usable=valid && !q.stale && now-date<=7*86400000;
  return {valid,usable,price:valid?q.c:null,date:valid?new Date(date).toLocaleDateString('en-CA',{timeZone:'Asia/Hong_Kong'}):'',sourceURL:q?.sourceURL};
}
function hkQuoteHTML(q) {
  const en=lang==='en';
  if(!q.valid) return `<span class="estimate-unavailable">${en?'Quote unavailable':'参考报价待更新'}</span>`;
  const price=`HK$${q.price.toFixed(3)}`;
  const url=/^https:\/\/finance\.sina\.com\.cn\/stock\/hkstock\/quotes\//.test(q.sourceURL || '')?q.sourceURL:null;
  return `<strong>${url?`<a href="${hkEscape(url)}" target="_blank" rel="noopener noreferrer">${price}</a>`:price}</strong><small class="hk-inline-note">${q.date}${q.usable?'':` · ${en?'Stale quote':'旧报价'}`}</small>`;
}
function hkPrimaryGroups(payload,cfg) {
  const groups=hkDisclosureGroups(payload?.holdings || []).filter(g=>g.latest && (!g.shareClass || hkListedClass(g.shareClass)));
  const byTicker=new Map();
  for(const g of groups) {
    if(!byTicker.has(g.ticker)) byTicker.set(g.ticker,[]);
    byTicker.get(g.ticker).push(g);
  }
  return [...byTicker.values()].map(owners=>{
    owners.sort((a,b)=>b.latest.event_date.localeCompare(a.latest.event_date) ||
      Number(hkEntityKey(b.latest.entity)===hkEntityKey(cfg?.manager))-Number(hkEntityKey(a.latest.entity)===hkEntityKey(cfg?.manager)));
    return {primary:owners[0],others:owners.slice(1)};
  }).sort((a,b)=>b.primary.latest.event_date.localeCompare(a.primary.latest.event_date) || a.primary.ticker.localeCompare(b.primary.ticker));
}
function renderHKDisclosures() {
  const el=document.getElementById('hkDisclosureSection');
  if(!el) return;
  const en=lang==='en',cfg=INVESTOR_CFG_BY_ID[investor],groups=hkVisibleGroups(hkDisclosures,cfg);
  el.hidden=!groups.length;
  if(el.hidden) {el.innerHTML='';return;}
  const checkedDate=new Date(hkDisclosures.audit?.checkedAt);
  const checkedLabel=Number.isFinite(checkedDate.getTime())?checkedDate.toLocaleDateString('en-CA',{timeZone:'Asia/Hong_Kong'}):'—';
  const headers=en?['Security','Event date','Long-interest shares','Issuer ownership','Reported event','Reference price','Evidence']:['标的','披露事件日期','多头权益股数','股份权益比例','本次申报事项','参考股价','原始证据'];
  el.innerHTML=`<div class="hk-table-heading"><h3>${en?'Hong Kong · verified recent disclosures':'港股 · 近期已核实披露'}</h3><span>${en?'Checked':'核查'} ${hkEscape(checkedLabel)}</span></div><p class="hk-evidence-note">${en?'Original forms within the last '+hkDisplayAge(cfg)+' days. Share interests may include derivatives; ownership uses the issued share class, not portfolio allocation. Refreshes daily at 08:00 and 21:00 Hong Kong time.':'展示近 '+hkDisplayAge(cfg)+' 天有原始申报表支持的记录。权益股数可能含衍生品；股份权益比例以该类已发行股份为分母，不是组合仓位。每日北京时间 08:00、21:00 自动核查。'}</p><div class="hk-table-wrap"><table class="hk-disclosure-table"><thead><tr>${headers.map(x=>`<th scope="col">${x}</th>`).join('')}</tr></thead><tbody>${groups.map((x,i)=>hkDisclosureTableRow(x,i,headers)).join('')}</tbody></table></div>`;
}

function hkDisplayAge(cfg) {const d=cfg?.hkDisclosure?.maxAgeDays;return Number.isInteger(d)&&d>0&&d<=365?d:120;}
function hkVisibleGroups(payload,cfg,now=Date.now()) {
  if(!payload || cfg?.holdingsUpdateMode==='archived') return [];
  const aliases=(cfg?.hkDisclosure?.entities?.length?cfg.hkDisclosure.entities:[cfg?.manager,...(cfg?.people || [])]).filter(Boolean).map(hkEntityKey);
  return hkPrimaryGroups(payload,cfg).filter(({primary:g})=>{
    const r=g.latest,date=Date.parse(r?.event_date),financial=hkFinancialLatest(g,r?.entity);
    return r?.verification==='hkex_form' && r.position==='long' && hkListedClass(r.share_class) &&
      aliases.includes(hkEntityKey(r.entity)) && /^https:\/\/di\.hkex\.com\.hk\/(?:di|filing\/di)\/NSForm[12]\.aspx(?:\?|$)/.test(r.form_url || '') &&
      Number.isFinite(date) && date<=now && now-date<=hkDisplayAge(cfg)*86400000 &&
      !(g.pending_newer_notices || []).some(p=>p.filing_ref && /^\d{4}-\d{2}-\d{2}$/.test(p.event_date || '') && Date.parse(p.event_date)<=now && /^https:\/\/di\.hkex\.com\.hk\//.test(p.source_url || '') && aliases.includes(hkEntityKey(p.entity)) && p.event_date>=r.event_date && p.filing_ref!==r.filing_ref) &&
      !(financial && financial.as_of>=r.event_date && financial.reported_value_usd===0);
  });
}
function hkEventLabel(r) {
  const names={1101:['买入股票','Share purchase'],1201:['卖出股票','Share sale'],11031:['衍生品权益增加（取股权利）','Derivative interest: right to take shares'],11032:['衍生品权益增加（交割义务）','Derivative interest: obligation to take shares'],1203:['衍生品交付','Delivery under derivatives'],14011:['淡仓权益增加（交付权利）','Short derivative interest: right to require delivery'],14012:['淡仓权益增加（交付义务）','Short derivative interest: obligation to deliver shares'],12041:['衍生品到期或取消','Derivative expiry or cancellation'],12042:['衍生品到期或取消','Derivative expiry or cancellation'],15011:['淡仓衍生品到期或取消','Short derivative expiry or cancellation'],15012:['淡仓衍生品到期或取消','Short derivative expiry or cancellation'],1303:['衍生品行权','Derivative exercise'],1304:['衍生品被行权','Derivative exercised against holder'],1316:['权益性质变化','Change in nature of interest'],1710:['自愿申报','Voluntary disclosure']};
  return (r.event_codes || []).filter(x=>names[x]).map(x=>names[x][lang==='en'?1:0]).join(' / ');
}
function hkFormChange(r) {
  if(r.position_details_schema<3 || !Number.isSafeInteger(r.before_long_shares) || !Number.isSafeInteger(r.long_interest_change) || r.shares-r.before_long_shares!==r.long_interest_change) return '';
  return `${lang==='en'?'Long interest':'多头权益'} ${r.long_interest_change>0?'+':''}${r.long_interest_change.toLocaleString('en-US')} ${lang==='en'?'shares':'股'}`;
}
function hkDisclosureTableRow({primary:g,others},index,headers) {
  const r=g.latest,en=lang==='en',q=hkQuoteState(g.ticker,r.share_class),derivatives=Array.isArray(r.derivative_interests)?r.derivative_interests.reduce((n,d)=>n+d.shares,0):null;
  const cells=[`<strong>${hkEscape(hkStockName(g))}</strong><small>${hkEscape(g.ticker)} · ${hkEscape(hkShareClassLabel(r.share_class))}</small><small>${hkEscape(r.entity)}</small>`,
    `${hkEscape(r.event_date)}${r.filing_date?`<small>${en?'Signed':'签署'} ${hkEscape(r.filing_date)}</small>`:''}`,`${r.shares.toLocaleString('en-US')}${derivatives>0?`<small>${en?'Includes derivative equivalents':'其中衍生品对应权益'} ${derivatives.toLocaleString('en-US')}</small>`:''}${Number.isFinite(r.short_shares)?`<small>${en?'Separate short interest':'另列淡仓权益'} ${r.short_shares.toLocaleString('en-US')}</small>`:''}`,
    `${r.pct.toFixed(2)}%${Number.isSafeInteger(r.issued_shares)&&r.issued_shares>0?`<small>${en?'Issued class shares':'该类发行股数'} ${r.issued_shares.toLocaleString('en-US')}</small>`:''}`,`${hkEscape(hkEventLabel(r)) || '—'}${hkFormChange(r)?`<small>${hkEscape(hkFormChange(r))}</small>`:''}`,
    q.usable?hkQuoteHTML(q):'—',`<a href="${hkEscape(r.form_url)}" target="_blank" rel="noopener noreferrer">${en?'HKEX form':'港交所原表'} ↗</a><button class="hk-detail-button" type="button" aria-expanded="false" aria-controls="hk-detail-${index}" onclick="toggleHKDisclosure(this)">${en?'Records':'逐次记录'}</button>`];
  const history=[g,...others].map(owner=>`<h4>${hkEscape(owner.entity)} · ${hkEscape(hkShareClassLabel(owner.shareClass))}</h4><table class="hk-event-history"><thead><tr><th>${en?'Date':'日期'}</th><th>${en?'Reported event':'申报事项'}</th><th>${en?'Long interest':'多头权益'}</th><th>${en?'Ownership':'股份权益比例'}</th><th>${en?'Source':'来源'}</th></tr></thead><tbody>${owner.records.filter(x=>x.verification==='hkex_form' && !x.superseded_by).slice().reverse().map(x=>`<tr><td>${x.event_date}</td><td>${hkEscape(hkEventLabel(x)) || '—'}${hkFormChange(x)?`<small>${hkEscape(hkFormChange(x))}</small>`:''}</td><td>${x.shares.toLocaleString('en-US')}${Number.isFinite(x.short_shares)?`<small>${en?'Separate short interest':'另列淡仓权益'} ${x.short_shares.toLocaleString('en-US')}</small>`:''}</td><td>${x.pct.toFixed(2)}%</td><td><a href="${hkEscape(x.form_url)}" target="_blank" rel="noopener noreferrer">${hkEscape(x.filing_ref)} ↗</a></td></tr>`).join('')}</tbody></table>`).join('');
  return `<tr class="hk-main-row">${cells.map((cell,i)=>`<td data-label="${headers[i]}">${cell}</td>`).join('')}</tr><tr id="hk-detail-${index}" class="hk-row-details" hidden><td colspan="7"><p class="hk-evidence-note">${en?'Entities and share classes remain separate; overlapping reports are not added together. Changes below are before/after long-interest differences in the same form, not automatically cash share purchases or sales.':'各主体、股份类别分别列示，重叠权益不可相加。下列变化使用同一原表中的事件前后多头权益之差，不直接等同现货买卖数量。'}</p><div class="hk-history-scroll" tabindex="0" aria-label="${en?'Scroll through original disclosure records':'左右滑动查看完整逐次披露记录'}">${history}</div></td></tr>`;
}
function toggleHKDisclosure(button) {
  const row=document.getElementById(button.getAttribute('aria-controls'));if(!row)return;
  row.hidden=!row.hidden;button.setAttribute('aria-expanded',String(!row.hidden));
}

function switchTab(name) {
  _activeInvestorTab=name;
  document.body?.classList?.toggle('personal-research', name === 'personal');
  document.body?.classList?.toggle('spin-research', ['spinoff','spinoff_us'].includes(name));
  ['current','changes','history','homework','spinoff','spinoff_us','game','personal'].forEach(t=>{
    document.getElementById('tab-'+t).classList.toggle('d-none',t!==name);
  });
  document.querySelectorAll('.tab-btn').forEach((b,i)=>{
    b.classList.toggle('active',['current','changes','history','homework','spinoff','spinoff_us','game','personal'][i]===name);
  });
  if(['current','changes','history'].includes(name))renderActiveInvestorView();
  if (name==='homework') { renderHomework(); }
  if (name==='spinoff') { renderSpinoff(); }
  if (name==='spinoff_us') { renderSpinoffUS(); }
  if (name==='game') { renderGame(); }
  if (name==='personal') {
    const strip=document.getElementById('tabsScroll');
    if (strip) strip.scrollLeft=strip.scrollWidth;
    if (typeof renderPersonalPortfolio === 'function') renderPersonalPortfolio();
  }
}

const GAME_URL = 'game/v2/index.html?v=6';
let _gameLoaded = false;
function renderGame() {
  const el = document.getElementById('gameContent');
  if (!el || _gameLoaded) return;
  const isEn = lang === 'en';
  el.innerHTML = `
    <div style="margin-bottom:14px;">
      <h3 style="font-family:var(--serif);font-size:1.05rem;color:var(--navy);margin:0 0 6px;font-weight:700;">
        ${isEn?'The Munger Trials: The $2 Trillion Answer':'格罗茨的试炼：2万亿的答案'}
      </h3>
      <p style="font-size:.8rem;color:var(--text-light);line-height:1.6;margin:0;">
        ${isEn
          ? 'Explore Charlie Munger\'s 1996 business thought experiment through five chapters, 16 decisions and numerical experiments, a resource-allocation finale, and a personal review. The game and companion reading are in Chinese; progress is saved in this browser.'
          : '五关推演、16 项决策与数字实验，再把有限资源分给产品、品牌和渠道。每个判断都有解释，最后生成个人复盘；进度自动保存在当前浏览器。'}
      </p>
      <a href="${GAME_URL}" target="_blank" rel="noopener"
         style="display:inline-block;margin-top:8px;font-size:.75rem;color:var(--gold);text-decoration:none;">
        ${isEn?'↗ Play in a new tab':'↗ 独立打开游戏'}
      </a>
      <a href="game/v2/article.html?v=6" target="_blank" rel="noopener noreferrer" style="display:inline-block;margin:8px 0 0 18px;font-size:.75rem;color:var(--gold);text-decoration:none;">
        ${isEn?'↗ Read the companion essay (Chinese)':'↗ 阅读完整演讲解读'}
      </a>
    </div>
    <div style="position:relative;width:100%;border:1px solid var(--border);border-radius:12px;overflow:hidden;background:var(--cream);box-shadow:0 4px 16px rgba(0,0,0,0.04);overscroll-behavior:contain;touch-action:pan-y;">
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
let _homeworkRequestId=0;
let _homeworkCachedLanguage=null;
function valueScreenOverview(candidates,en=lang==='en') {
  const deep=candidates.filter(c=>Number.isFinite(c.mos) && c.mos>=20).length;
  const shared=candidates.filter(c=>(c.investors || []).length>=2).length;
  const buying=candidates.filter(c=>(c.investors || []).some(h=>['new','added'].includes(h.chg))).length;
  const reducing=candidates.filter(c=>(c.investors || []).some(h=>h.chg==='trimmed')).length;
  const mixed=candidates.filter(c=>(c.investors || []).some(h=>['new','added'].includes(h.chg)) && (c.investors || []).some(h=>h.chg==='trimmed'));
  const unchanged=candidates.filter(c=>(c.investors || []).length && c.investors.every(h=>h.chg==='hold')).length;
  const top=[...candidates].filter(c=>Number.isFinite(c.mos)).sort((a,b)=>b.mos-a.mos).slice(0,3);
  const label=c=>((en?c.name:c.cnName || c.name) || c.ticker)+' ('+c.ticker+')';
  const active=candidates.filter(c=>(c.investors || []).some(h=>['new','added'].includes(h.chg))).slice(0,2);
  const trimmed=candidates.filter(c=>(c.investors || []).some(h=>h.chg==='trimmed')).slice(0,2);
  const headline=en
    ? (reducing>buying?`More screened names show reductions (${reducing}) than entries/additions (${buying})`:`${candidates.length} screened names; ${buying} show entries or additions`)
    : (reducing>buying?`本轮候选中，减持 ${reducing} 只，多于新建仓或增持的 ${buying} 只`:`本轮 ${candidates.length} 只候选，其中 ${buying} 只出现新建仓或增持`);
  const lead=en
    ? `${candidates.length} candidates pass this screen; ${deep} are at least 20% below estimated cost. ${buying} show a new or increased holding, ${reducing} a reduction, and ${unchanged} have unchanged shares across all qualifying holders. A large estimated-cost gap and increasing share counts are separate observations. These groups can overlap.`
    : `本轮 ${candidates.length} 只进入候选，其中 ${deep} 只价格低于估算成本至少 20%。但看各位达标持有者的最新披露，${buying} 只出现新建仓或增持，${reducing} 只出现减持，另有 ${unchanged} 只的达标持有者股数均未变。成本差较大与正在增持是两件事，两组可以重叠。`;
  const price=en?top.map(c=>`${label(c)}: price $${c.price ?? '—'}, estimated cost $${c.buy ?? '—'}, gap ${c.mos}%`).join('; '):top.map(c=>`${label(c)}：现价 $${c.price ?? '—'}、估算成本 $${c.buy ?? '—'}，差 ${c.mos}%`).join('；');
  const directions=en
    ? (active.length?`Entries/additions appear in ${active.map(label).join('; ')}. `:'No qualifying holder reported an entry or addition. ')+(trimmed.length?`Reductions appear in ${trimmed.map(label).join('; ')}. `:'')+(mixed.length?`${mixed.length} names have opposing holder directions (${mixed.slice(0,3).map(c=>c.ticker).join(', ')}).`:'No candidate has both an increase and a reduction among its qualifying holders.')
    : (active.length?`新增或增持的例子有 ${active.map(label).join('、')}。`:'本轮达标持有者没有记录新建仓或增持。')+(trimmed.length?`减持的例子有 ${trimmed.map(label).join('、')}。`:'')+(mixed.length?`其中 ${mixed.length} 只存在方向分歧（${mixed.slice(0,3).map(c=>c.ticker).join('、')}），要分别看持有者。`:'本轮候选中，没有出现达标持有者一边增持、一边减持的情况。');
  const consensus=en
    ? `${shared} candidates have at least two holders meeting the screen. `+(shared?`They include ${candidates.filter(c=>c.investors.length>=2).slice(0,3).map(label).join('; ')}.`:'Each candidate currently qualifies through just one investor’s cost estimate; other holders may exist but do not meet the same threshold.')
    : `${shared} 只同时有至少两位投资人的持仓满足筛选条件。`+(shared?`例如 ${candidates.filter(c=>c.investors.length>=2).slice(0,3).map(label).join('、')}。`:'本轮每只候选都只通过一位投资人的成本估算达标；表中“其他持有者”不能算作同样达标。');
  const b={version:1,headline:[headline,headline],lead:[lead,lead],details:[
    {label:[en?'Where the largest cost gaps are':'最大的成本差在哪里',en?'Where the largest cost gaps are':'最大的成本差在哪里'],text:[price+'。',price+'.']},
    {label:[en?'How share counts changed':'这些候选的股数怎样变',en?'How share counts changed':'这些候选的股数怎样变'],text:[directions,directions]},
    {label:[en?'How many qualifying holders agree':'有多少达标持有者重合',en?'How many qualifying holders agree':'有多少达标持有者重合'],text:[consensus,consensus]}
  ],readerGuide:[en?'Use the cost gap to identify research candidates, then check each holder’s share-count direction, report date and current business valuation. A reduction deserves attention even when the cost gap is large.':'先用成本差找到研究候选，再看各持有者的增减方向、报告日期与企业当前估值。即使成本差较大，出现减持也值得单独研究；这张表不是买入清单。',en?'Use the cost gap to identify research candidates, then check each holder’s share-count direction, report date and current business valuation. A reduction deserves attention even when the cost gap is large.':'先用成本差找到研究候选，再看各持有者的增减方向、报告日期与企业当前估值。即使成本差较大，出现减持也值得单独研究；这张表不是买入清单。'],notes:[[en?'The gap is price versus estimated historical cost, not business fair value. Holders may report different quarters; their portfolio weights cannot be added.':'差值是现价相对历史成本估算，不是企业价值折价。各持有者报告季度可能不同；组合权重不能相加。',en?'The gap is price versus estimated historical cost, not business fair value. Holders may report different quarters; their portfolio weights cannot be added.':'差值是现价相对历史成本估算，不是企业价值折价。各持有者报告季度可能不同；组合权重不能相加。']]};
  return briefingHTML(b);
}
let _homeworkData=null;
let _homeworkFilter='all',_homeworkSearch='',_homeworkSort='holders',_homeworkPage=0;
function homeworkDirection(holders,en=lang==='en') {
  const add=holders.filter(h=>['new','added'].includes(h.chg)).length,cut=holders.filter(h=>h.chg==='trimmed').length;
  if(add&&cut)return [en?`${add} adding · ${cut} reducing`:`${add} 人增加 · ${cut} 人减少`,'mixed'];
  if(add)return [en?`${add} entering / adding`:`${add} 人新进或增持`,'added'];
  if(cut)return [en?`${cut} reducing`:`${cut} 人减持`,'trimmed'];
  return [holders.every(h=>h.chg==='hold')?(en?'Shares unchanged':'股数未变'):(en?'Comparison unavailable':'本期不可比'),'hold'];
}
function homeworkChange(h,en=lang==='en') {
  const base={new:['新进','New'],added:['增持','Added'],trimmed:['减持','Reduced'],hold:['股数未变','Unchanged'],unknown:['不可比','Not comparable']}[h.chg]||['不可比','Not comparable'];
  const pct=Number.isFinite(h.shareChangePct)&&h.shareChangePct!==0?' '+(h.shareChangePct>0?'+':'')+Number(h.shareChangePct.toPrecision(3))+'%':'';
  return base[en?1:0]+pct;
}
function homeworkTableHTML(candidates) {
  const en=lang==='en',text=(a,b)=>en?b:a,esc=hkEscape;
  const price=n=>Number.isFinite(n)?'$'+n.toFixed(2):'—';
  const holder=h=>en?(h.nameEn||h.name):h.name;
  const weight=h=>Number.isFinite(h.weight)?(h.weight<.01?'<0.01%':h.weight+'%'):'—';
  const link=h=>/^[a-z][a-z0-9_]{0,30}$/.test(h.id||'')?`<button type="button" class="hw-investor-link" onclick="switchInvestor('${h.id}');switchTab('current');">${esc(holder(h))}</button>`:esc(holder(h));
  const source=h=>h.referenceKind==='adjusted_quarter_reference'?text('公司行动后季末参考','Post-action quarter-end reference'):['filing_proxy','13f-estimate'].includes(h.referenceSource)?text('申报季末价代理','Filed quarter-end proxy'):h.referenceKind==='scope_initial'?text('范围起始参考','Initial scope reference'):text('加仓价格估算','Estimated addition price');
  const detail=h=>`<div class="hw-holder-detail"><div>${link(h)} <small>${esc(h.reportQuarter||'')} · ${text('申报占比','Reported weight')} ${weight(h)}</small><span class="hw-direction ${esc(h.chg)}">${esc(homeworkChange(h))}</span></div><div>${text('参考','Reference')} <strong>${price(h.buy)}</strong> · ${esc(h.buyQuarter||'—')} · ${source(h)}${Number.isFinite(h.atAvg)?` · ${text('历次均价','Running estimate')} ${price(h.atAvg)}`:''}</div>${h.costFirst?`<small>${esc(h.costFirst)}—${esc(h.costLast||h.reportQuarter||'')} · ${h.buyQuarters||0} ${text('个加仓季度','addition quarters')}</small>`:''}</div>`;
  const rows=candidates.map(c=>{
    const [direction,tone]=homeworkDirection(c.investors),name=en?c.name:(c.cnName||c.name),refName=en?c.referenceInvestorEn:c.referenceInvestor;
    const refs=c.investors.map(h=>h.buy).filter(Number.isFinite),max=Math.max(...refs);
    const holdingLines=c.investors.map(h=>`<div class="hw-holder-line">${link(h)}<small>${esc(h.reportQuarter||'')} · ${weight(h)}</small><span class="hw-direction ${esc(h.chg)}">${esc(homeworkChange(h))}</span></div>`).join('');
    const others=c.otherHolders||[];
    return `<tr><td class="hw-company"><strong class="ticker-line">${fmtTicker(c.ticker)}</strong><span class="name-line">${esc(name)}</span><span class="hw-direction ${tone}">${esc(direction)}</span></td><td data-label="${text('现价','Price')}"><strong>${price(c.price)}</strong><small>${esc((c.priceAsOf||'').slice(0,10))}</small></td><td data-label="${text('参考价','Reference')}"><strong>${price(c.buy)}</strong><small>${esc(refName||'')} · ${esc(c.referenceQuarter||'')}</small><small>${source({referenceSource:c.referenceSource,referenceKind:c.referenceKind})}</small></td><td data-label="${text('低于参考','Below ref.')}"><strong class="hw-gap">${c.mos}%</strong>${max>c.buy?`<small>${text('取达标者最低参考','Lowest qualifying reference')}</small>`:''}</td><td class="hw-holders"><div class="hw-holder-count">${c.investors.length} ${text('人价差达标','qualify')}${others.length?` · ${others.length} ${text('位其他持有人','other holders')}`:''}</div>${holdingLines}<details class="hw-calculation"><summary>${text('查看每人的参考价与变化','References and changes by holder')}</summary>${c.investors.map(detail).join('')}${others.length?`<div class="hw-other-holders"><strong>${text('其他持有人','Other holders')}</strong>${others.map(h=>`<div>${link(h)} · ${esc(h.reportQuarter||'')} · ${esc(homeworkChange(h))}<small>${Number.isFinite(h.buy)?`${text('参考','Reference')} ${price(h.buy)} · ${text('现价低于','Gap')} ${h.mos}%`:text('暂无可用参考价','Reference unavailable')}</small></div>`).join('')}</div>`:''}</details></td></tr>`;
  }).join('');
  return `<div class="table-wrap"><table class="homework-table"><thead><tr><th>${text('股票与披露方向','Security & direction')}</th><th>${text('现价','Current price')}</th><th>${text('历史参考价','Historical reference')}</th><th>${text('价差','Price gap')}</th><th>${text('谁持有 · 最新股数变化','Holders · latest share changes')}</th></tr></thead><tbody>${rows}</tbody></table></div>`;
}
function pageHomework(delta){_homeworkPage+=delta;updateHomeworkView(false);}
function updateHomeworkView(resetPage=true) {
  if(resetPage)_homeworkPage=0;
  if(!_homeworkData)return;
  const filter=document.getElementById('hwFilter'),query=document.getElementById('hwSearch'),sort=document.getElementById('hwSort');
  if(filter)_homeworkFilter=filter.value;if(query)_homeworkSearch=query.value;if(sort)_homeworkSort=sort.value;
  const term=_homeworkSearch.trim().toLowerCase();
  let rows=_homeworkData.candidates.filter(c=>(!term||[c.ticker,c.name,c.cnName,...c.investors.flatMap(h=>[h.name,h.nameEn])].join(' ').toLowerCase().includes(term))&&(_homeworkFilter==='all'||_homeworkFilter==='adding'&&c.investors.some(h=>['new','added'].includes(h.chg))||_homeworkFilter==='shared'&&c.investors.length>=2||_homeworkFilter==='reducing'&&c.investors.every(h=>h.chg==='trimmed')||_homeworkFilter==='mixed'&&c.investors.some(h=>['new','added'].includes(h.chg))&&c.investors.some(h=>h.chg==='trimmed')));
  if(_homeworkSort==='gap')rows.sort((a,b)=>b.mos-a.mos||a.ticker.localeCompare(b.ticker));
  const pages=Math.max(1,Math.ceil(rows.length/60));_homeworkPage=Math.max(0,Math.min(pages-1,_homeworkPage));
  const pager=pages>1?`<div class="portfolio-controls hw-pager"><button type="button" onclick="pageHomework(-1)"${_homeworkPage===0?' disabled':''}>${lang==='en'?'Previous':'上一页'}</button><span>${_homeworkPage+1} / ${pages}</span><button type="button" onclick="pageHomework(1)"${_homeworkPage===pages-1?' disabled':''}>${lang==='en'?'Next':'下一页'}</button></div>`:'';
  const target=document.getElementById('hwResults');if(target)target.innerHTML=rows.length?homeworkTableHTML(rows.slice(_homeworkPage*60,(_homeworkPage+1)*60))+pager:`<p class="hw-empty">${lang==='en'?'No matches for these filters.':'当前条件下没有匹配的股票。'}</p>`;
  const count=document.getElementById('hwResultCount');if(count)count.textContent=lang==='en'?`${rows.length?_homeworkPage*60+1:0}–${Math.min((_homeworkPage+1)*60,rows.length)} of ${rows.length} matched`:`显示 ${rows.length?_homeworkPage*60+1:0}–${Math.min((_homeworkPage+1)*60,rows.length)} / ${rows.length} 只`;
  _homeworkCache=null;
}
async function renderHomework() {
  const el=document.getElementById('homeworkContent');if(!el)return;
  const requestId=++_homeworkRequestId,requestedLanguage=lang,en=lang==='en',text=(a,b)=>en?b:a;
  if(_homeworkCache&&_homeworkCachedLanguage===lang&&Date.now()-_homeworkCachedAt<300000){el.innerHTML=_homeworkCache;return;}
  el.innerHTML=`<p class="hw-empty">${text('加载中…','Loading…')}</p>`;
  try {
    const response=await fetch('value_screen.json?v=95&t='+Math.floor(Date.now()/300000));if(!response.ok)throw Error('screen unavailable');
    const screen=await response.json();if(requestId!==_homeworkRequestId||lang!==requestedLanguage)return;
    _homeworkData=screen;const candidates=screen.candidates||[];
    if(!candidates.length){el.innerHTML=`<p class="hw-empty">${text('暂无低于历史参考价至少 10% 的股票','No stocks at least 10% below their historical reference')}</p>`;return;}
    const adding=candidates.filter(c=>c.investors.some(h=>['new','added'].includes(h.chg))).length,shared=candidates.filter(c=>c.investors.length>=2).length,mixed=candidates.filter(c=>c.investors.some(h=>['new','added'].includes(h.chg))&&c.investors.some(h=>h.chg==='trimmed')).length;
    const selected=(v,state)=>v===state?' selected':'';
    el.innerHTML=`<div class="hw-intro"><div><h3>${text('抄作业 · 先看价格，再看变化','Value screen · prices and changes')}</h3><p>${text('现价低于历史参考价至少 10%；价差是历史价格比较，不是企业估值折价。','Prices at least 10% below a historical reference; this compares prices, not intrinsic value.')}</p></div><small>${text('更新','Updated')} ${hkEscape((screen.generatedAt||'').slice(0,16).replace('T',' '))} UTC</small></div><div class="hw-facts"><span><strong>${candidates.length}</strong>${text('只候选',' candidates')}</span><span><strong>${adding}</strong>${text('只有人增持或新进',' with entries/additions')}</span><span><strong>${shared}</strong>${text('只多人价差达标',' with multiple qualifying holders')}</span><span><strong>${mixed}</strong>${text('只增减分歧',' with opposing directions')}</span></div><div class="hw-controls"><label>${text('搜索','Search')}<input id="hwSearch" type="search" value="${hkEscape(_homeworkSearch)}" placeholder="${text('股票、代码或投资人','Company, ticker or investor')}" oninput="updateHomeworkView()"></label><label>${text('披露方向','Disclosures')}<select id="hwFilter" onchange="updateHomeworkView()">${[['all','全部','All'],['adding','有人新进或增持','Entries or additions'],['shared','多人价差达标','Multiple qualifying holders'],['reducing','达标者全部减持','All qualifying holders reducing'],['mixed','增减有分歧','Opposing directions']].map(([v,zh,en])=>`<option value="${v}"${selected(v,_homeworkFilter)}>${text(zh,en)}</option>`).join('')}</select></label><label>${text('排序','Sort')}<select id="hwSort" onchange="updateHomeworkView()"><option value="holders"${selected('holders',_homeworkSort)}>${text('达标人数，再按价差','Qualifying holders, then gap')}</option><option value="gap"${selected('gap',_homeworkSort)}>${text('价差从大到小','Largest gap first')}</option></select></label><span id="hwResultCount" aria-live="polite"></span></div><div id="hwResults"></div><p class="hw-method">${text('参考价取价差达标者中的最低值。展开每只股票，可查看各人的参考季度、估算依据和增减幅度。','The reference is the lowest among qualifying holders. Expand a security for each holder’s dates, calculation basis and share changes.')}</p><div id="valueInsight" class="insights-box"><div class="scope-heading"><h3>${text('本轮筛选的重点','What this screen shows')}</h3></div>${valueScreenOverview(candidates,en)}</div>`;
    updateHomeworkView(false);_homeworkCache=el.innerHTML;_homeworkCachedAt=Date.now();_homeworkCachedLanguage=lang;
  } catch(e) {
    if(requestId!==_homeworkRequestId||lang!==requestedLanguage)return;
    el.innerHTML=`<p class="hw-empty">${text('暂时无法载入筛选数据，请刷新重试。','Unable to load the screen. Please refresh and retry.')}</p>`;
  }
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
  window.InvestorBookplates?.select(investor,en);
  const text = (zh, english) => en ? english : zh;
  const setText = (selector, value) => { const el = document.querySelector(selector); if (el) el.textContent = value; };
  const setHTML = (selector, value) => { const el = document.querySelector(selector); if (el) el.innerHTML = value; };
  const projects = cfg.portfolioMode==='public_projects';
  for (const [key,zh,english] of projects ? [['tabCurrent','投资项目','Investment projects'],['tabChanges','公开披露','Public disclosures'],['tabHistory','披露历史','Disclosure history'],['tlTitle','项目目录观测','Project observations']] : [['tabCurrent','持仓明细','Holdings'],['tabChanges','季度变化','Quarterly changes'],['tabHistory','历史趋势','Historical trends'],['tlTitle','持仓时间轴','Holdings timeline']]) setText('[data-i18n="'+key+'"]',text(zh,english));
  const title = `${name} ${projects ? text('投资研究','Investment Research') : cfg.source13F ? text('13F 持仓追踪', '13F Tracker') : (data?.meta?.snapshotType==='verified_disclosure_snapshot'?text('港股公开披露','HK Public Disclosures'):text('港股历史披露', 'Historical HK Disclosures'))}`;
  setText('[data-i18n="heroTitle"]', title);
  document.title = title;
  setText('[data-i18n="footerTitle"]', title);
  setText('.hero-title .sub', `${cfg.manager} · ${projects ? text('官方项目与权益披露','Official projects & ownership filings') : cfg.source13F ? 'SEC 13F' : (data?.meta?.snapshotType==='verified_disclosure_snapshot'?text('港交所原表 · 公开披露快照','HKEX original forms · disclosure snapshot'):text('历史权益披露快照', 'Historical disclosure snapshot'))}`);
  document.getElementById('portfolioAttribution')?.remove();
  const attribution=cfg.portfolioAttribution ? `<span id="portfolioAttribution" class="data-quality-note">${hkEscape(profileText(cfg.portfolioAttribution))}</span>` : '';
  if(attribution){const row=document.getElementById('metaRow');if(row)row.insertAdjacentHTML('beforeend',attribution);}
  setText('.quote-block blockquote', profileText(p.quote?.text || p.summary));
  const quoteAttribution = p.quote ? profileText(p.quote.attribution) : `${name} · ${text('投资理念', 'Investment philosophy')}`;
  const quoteSource = p.quote?.url;
  setHTML('.quote-block .attr', /^https:\/\//.test(quoteSource || '') ? `<a href="${hkEscape(quoteSource)}" target="_blank" rel="noopener noreferrer">${hkEscape(quoteAttribution)}</a>` : hkEscape(quoteAttribution));
  setText('#aboutLabel', 'About');
  setText('#aboutTitle', profileText(p.aboutTitle) || text(`关于${cfg.name}`, `About ${cfg.nameEn}`));
  setText('#philLabel', 'Philosophy');
  setText('#philTitle', profileText(p.philosophyTitle) || text('投资理念', 'Investment Philosophy'));
  setHTML('#philosophySignature', p.signature ? `<strong>${hkEscape(profileText(p.signature.title))}</strong><p>${hkEscape(profileText(p.signature.text))}</p>` : '');
  setText('#readLabel', 'Sources');
  setText('#readTitle', text('原始资料与延伸阅读', 'Primary Sources & Further Reading'));
  setText('[data-i18n="navAbout"]', text(`关于${cfg.name}`, `About ${cfg.nameEn}`));
  setHTML('.ref-text', p.about.map(paragraph => `<p>${hkEscape(profileText(paragraph))}</p>`).join(''));
  const timeline = [...p.timeline];
  setHTML('.ref-grid .timeline', `<h3 class="timeline-heading">${text('经历与重要节点','Career & important milestones')}</h3>` + timeline.map(item => `<div class="tl-item"><div class="tl-year">${hkEscape(item.date)}</div><div class="tl-text">${hkEscape(profileText(item.text))}</div></div>`).join(''));

  setHTML('.phil-grid', p.principles.map((item,i) => `<div class="phil-card"><div class="icon">${String(i+1).padStart(2,'0')}.</div><h4>${hkEscape(profileText(item.title))}</h4><p>${hkEscape(profileText(item.text))}</p></div>`).join(''));
  setHTML('.articles-grid', p.resources.filter(item => /^https:\/\//.test(item.url)).map(item => `<a class="article-card" href="${hkEscape(item.url)}" target="_blank" rel="noopener noreferrer"><div class="year">${hkEscape(profileText(item.kind))}</div><h4>${hkEscape(profileText(item.title))}</h4><p>${hkEscape(profileText(item.description))}</p></a>`).join(''));
  if (window.SpeechArchive) window.SpeechArchive.updateInvestor(cfg, en);
  const updated = document.getElementById('updateTime');
  if (updated) updated.textContent = data?.meta?.lastUpdated || '—';
  const sec = document.getElementById('footerSEC');
  if (sec) { sec.hidden = !cfg.cik; if (cfg.cik) sec.href = `https://www.sec.gov/edgar/browse/?CIK=${encodeURIComponent(cfg.cik)}&owner=exclude`; }
  const official = document.getElementById('footerOfficial');
  if (official) { official.hidden = !cfg.officialWebsite; if (cfg.officialWebsite) { official.href = cfg.officialWebsite; official.textContent = cfg.officialWebsiteLabel || cfg.manager; } }
}

// ========== AUTO-INIT ==========
function renderAll() { for (const render of [renderSummary,renderHoldings,renderChanges,renderHistoryChart,renderInsights,renderHKDisclosures]) { try { render(); } catch(e) { console.error('Render error:',e.message); } } }

// 页面加载后静默拉取状态灯颜色（不弹抽屉）
async function initStatusDot(signal) {
  try {
    const r = await fetch('run_status.json?_=' + Date.now(), {cache: 'no-store', signal});
    if (!r.ok) throw new Error('Status unavailable');
    const statusData = await r.json();
    _runStatusData = statusData;
    updateStatusDot(statusData);
    if (data) renderActiveInvestorView(true);
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
  window.addEventListener('resize',syncInvestorLayout,{passive:true});
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
  const drawer=document.getElementById('statusDrawer');
  drawer.inert=false;
  drawer.setAttribute('aria-hidden','false');
  document.getElementById('statusDot').setAttribute('aria-expanded','true');
  document.getElementById('statusOverlay').classList.add('open');
  drawer.classList.add('open');
  drawer.querySelector('.status-drawer-close')?.focus();
  renderStatusDrawer();
}

function closeStatusDrawer() {
  const drawer=document.getElementById('statusDrawer');
  if(drawer.contains(document.activeElement)) document.getElementById('statusDot').focus();
  drawer.inert=true;
  drawer.setAttribute('aria-hidden','true');
  document.getElementById('statusDot').setAttribute('aria-expanded','false');
  document.getElementById('statusOverlay').classList.remove('open');
  drawer.classList.remove('open');
}

function closeInfoPopovers(except=null) {
  document.querySelectorAll('.info-popover.show').forEach(p=>{if(p!==except)p.classList.remove('show');});
}
document.addEventListener('click', e => {
  const badge=e.target?.closest?.('.info-badge');
  if (!badge) { if(!e.target?.closest?.('.info-wrap'))closeInfoPopovers(); return; }
  const popup=badge.closest('.info-wrap')?.querySelector('.info-popover');
  closeInfoPopovers(popup);
  if (!popup?.classList.contains('show') || innerWidth<=640) return;
  // A fixed bubble escapes the table's clipping, while staying near its label.
  const anchor=badge.getBoundingClientRect(),size=popup.getBoundingClientRect();
  const left=Math.max(16,Math.min(anchor.left+anchor.width/2-size.width/2,innerWidth-size.width-16));
  const below=anchor.bottom+8,top=below+size.height<=innerHeight-16?below:Math.max(16,anchor.top-size.height-8);
  Object.assign(popup.style,{position:'fixed',left:left+'px',right:'auto',top:top+'px',bottom:'auto',transform:'none'});
});
document.addEventListener('scroll', e=>{if(!e.target?.closest?.('.info-popover'))closeInfoPopovers();},true);
// ESC 关闭
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') { closeStatusDrawer(); closeInfoPopovers(); }
  if(e.key==='Tab') {
    const drawer=document.getElementById('statusDrawer');
    if(!drawer?.classList.contains('open'))return;
    const controls=[...drawer.querySelectorAll('button, a[href], summary, [tabindex="0"]')].filter(el=>el.getClientRects().length);
    const first=controls[0],last=controls.at(-1);
    if(e.shiftKey && document.activeElement===first){e.preventDefault();last?.focus();}
    else if(!e.shiftKey && document.activeElement===last){e.preventDefault();first?.focus();}
  }
});

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
      const visibleMessage=statusStepMessage(stepKey,s);
      const msg = visibleMessage ? `<div class="status-step-message">${hkEscape(visibleMessage)}</div>` : '';
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
  if (mutedHistoryNotice(key,step)) return 'ok';
  // Reclassify only an explicitly completed search, never an interrupted fetch.
  return key === 'lilu_13f' && step?.status === 'warn' && /^lilu 历史缺 \d+ 季：已补查SEC历史索引，仍无可用原始持仓报告；不作零持仓$/.test(step.msg || '') ? 'info' : step?.status;
}
function mutedHistoryNotice(key,step) {
  if (!key.endsWith('_13f') || !['info','warn'].includes(step?.status)) return false;
  const msg=String(step.msg || ''),match=msg.match(/历史缺\s*(\d+)\s*季/);
  if (!match || !/已补查SEC历史索引，仍无可用原始持仓报告/.test(msg)) return false;
  const cfg=INVESTOR_CFG_BY_ID[key.slice(0,-4)];
  const quiet=cfg?.historyGapNotices?.mutedQuarters || [];
  const scope=msg.match(/季（([^）]+)）/);
  const quarters=scope?scope[1].split(',').map(q=>q.trim()):[];
  return quiet.length>0 && (quarters.length?quarters.length===Number(match[1]) && quarters.every(q=>quiet.includes(q)):Number(match[1])===quiet.length);
}
function statusStepMessage(stepKey, step) {
  if (mutedHistoryNotice(stepKey,step)) return '';
  const msg = String(step?.msg || '');
  const missing = stepKey.endsWith('_13f') && ['warn','info'].includes(step.status) && msg.match(/历史缺\s*(\d+)\s*季/);
  const scope = msg.match(/季（([^）]+)）/);
  const quarters = scope ? ` (${scope[1]})` : '';
  if (missing && /已补查SEC历史索引，仍无可用原始持仓报告/.test(msg)) return lang === 'en'
    ? `${missing[1]} early historical quarters${quarters} lack verifiable SEC holdings reports, even after checking historical indexes. This notice concerns historical coverage, not a failure to load the latest holdings; gaps remain in the history chart.`
    : `早期历史资料缺 ${missing[1]} 个季度${quarters}：补查 SEC 历史索引后，仍未找到可核实的原始持仓报告。这项提示针对历史覆盖，不表示最新持仓加载失败；历史图保留断点。`;
  if (missing) return lang === 'en' ? `${missing[1]} historical quarters have no verified holdings report. See historical coverage; this is separate from the latest holdings update.` : `历史持仓缺 ${missing[1]} 个季度，请查看历史覆盖说明；此提示不表示最新持仓加载失败。`;
  return msg;
}

