#!/usr/bin/env python3
"""
fetch_spinoff_us.py
美股分拆事件追踪脚本
数据来源：SEC EDGAR 8-K 全文搜索
输出：spinoff_us.json
"""

from spinoff_events import infer_status, extract_name, extract_dates as evidence_dates, parse_evidence, filing_url, normalize, merge_evidence
from update_status import record_ai_warning, record_source_warning

import json, os, re, sys, time, urllib.parse
from datetime import datetime, timedelta, timezone
from urllib.request import Request, urlopen, build_opener, HTTPCookieProcessor
from urllib.error import HTTPError, URLError
from http.cookiejar import CookieJar

UA = "Mozilla/5.0 (research bot) research@example.com"
EDGAR_BASE = "https://efts.sec.gov"
EDGAR_ARCHIVE = "https://www.sec.gov/Archives/edgar/data"
COMPANY_FACTS = "https://data.sec.gov/api/xbrl/companyfacts"

# 市值过滤阈值（美元）
MIN_MARKET_CAP = 500_000_000  # 5亿美元

# 搜索时间窗口（天）
SEARCH_DAYS = 365

# 分拆类型判断关键词
TYPE_SPINOFF  = [r'spin-off', r'spinoff', r'spin off', r'distribution of.*shares', r'distribute.*shares.*holders']
TYPE_CARVEOUT = [r'initial public offering', r'\bipo\b', r'carve-out', r'carveout', r'raise.*proceeds', r'offer.*shares.*public']
TYPE_SPLITOFF = [r'split-off', r'splitoff', r'split off', r'exchange offer']

# 排除词（避免将 8-K 正文中的历史提及误判）
EXCLUDE_WORDS = [r'completed.*spin-off', r'former.*spin-off', r'prior.*spin-off',
                 r'following.*spin-off', r'result.*spin-off']

# 状态关键词
STATUS_COMPLETE   = [r'distribution.*complet', r'spin-off.*complet', r'shares.*distribut', r'began.*trading', r'commenced.*trading']
STATUS_APPROVED   = [r'shareholder.*approv', r'stockholder.*approv', r'vote.*approv', r'approved.*spin']
STATUS_RECORD     = [r'record date', r'holders of record']
STATUS_ANNOUNCED  = [r'intend.*spin', r'plan.*spin', r'propos.*spin', r'explor.*spin', r'evaluat.*spin']
STATUS_TERMINATED = [r'terminat.*spin', r'cancel.*spin', r'abandon.*spin', r'withdraw.*spin']

# 中文名字典（主要公司）
CN_NAMES = {
    'HON':  '霍尼韦尔',
    'HONA': '霍尼韦尔航空航天',
    'SOLV': '索尔文图姆',
    'GEV':  'GE威诺华',
    'KVUE': '科沃',
    'CMCSA':'康卡斯特',
    'MDT':  '美敦力',
    'JNJ':  '强生',
    'BDX':  '碧迪',
    'FDX':  '联邦快递',
    'FDXF': '联邦快递货运',
    'MIDD': 'Middleby集团',
    'MFP':  'Midera食品加工',
    'REZI': '瑞思迪奥',
    'APTV': '安波福',
    'DAN':  '德纳公司',
    'TEX':  '特雷克斯',
    'AMRC': 'Ameresco',
    'BTU':  '皮博迪能源',
    'HXL':  '赫氏复合材料',
    'TRAX': 'First Tracks生物',
    'ANAB': 'AnaptysBio',
    'VANI': 'Vivani医疗',
    'BLCO': '鲍希与洛姆',
    'RNA':  'Avidity生物',
    'WAT':  '沃特斯公司',
    'SOLS': '索尔斯特斯先进材料',
    'VGNT': 'Versigent',
    'DD':   '杜邦',
    'FTV':  '福迪威',
    'PEAB': '皮博迪',
    'MMM':  '3M',
    'GE':   '通用电气',
    'WBD':  '华纳兄弟探索',
    'PARA': '派拉蒙',
    'IBN':  'ICICI银行',
    'RTX':  '雷神技术',
    'J':    'Jacobs工程',
    'PWR':  'Quanta服务',
    'CELC': 'Celcuity',
    'XFOR': 'X4制药',
    'HIMS': 'Hims & Hers健康',
    'TSNDF':'TerrAscend',
    'AMRX': 'Amneal制药',
    'KDP':  '科瑞格胡椒博士',
    'NFLX': '奈飞',
    'AKAM': '阿卡迈技术',
    'JEF':  '杰富瑞金融',
    'PPL':  'PPL能源',
    'MOD':  '莫丁制造',
    'THRM': '根瑟姆',
    'NVRI': '英弗里集团',
    'WOLF': '沃尔夫斯皮德',
    'AMBC': '安贝克金融',
    'BE':   '博隆能源',
    'GPRE': '绿色平原',
    'SMR':  '纽斯凯尔动力',
    'CRGY': '新月能源',
    'PUMP': 'ProPetro控股',
    # 补充（EDGAR 搜索命中的小公司）
    'OCTV': '八度智能公司',
    'FET':  '论坛能源技术公司',
    'VRDN': '维瑞迪安治疗公司',
    'CUE':  'Cue生物制药公司',
    'AMRZ': '阿姆瑞兹有限公司',
    'VREOF':'维雷奥增长公司',
    'FLGC': '弗洛拉增长公司',
    'ZBIO': '泽纳斯生物制药公司',
    'ENTA': '恩安塔制药公司',
    'ARWR': '箭头制药公司',
    'ELVN': '恩利文治疗公司',
    'FSLY': '法斯特利公司',
    'VSNT': '沃森特媒体集团公司',
    'CPSS': '消费者投资组合服务公司',
    'COGT': '科真生物科学公司',
    'VOYG': '航海者技术公司',
    'ECG':  '埃弗鲁斯建筑集团公司',
    'SEI':  '索拉里斯能源基础设施公司',
    'ALTS': 'ALT5西格玛公司',
    'ZONE': '清洁核心解决方案公司',
    'DFDV': 'DeFi开发公司',
    'CHRO': '佩尔索斯治疗公司',
}
KNOWN_SPINOFFS = [
    {
        "ticker": "HON",
        "name": "Honeywell International",
        "nameCN": "霍尼韦尔",
        "spinoffName": "Honeywell Aerospace",
        "spinoffTicker": "HONA",
        "type": "spinoff",
        "exchange": "Nasdaq",
        "distributionDate": "2026-06-29",
        "announcements": [
            {"date": "2024-10-08", "title": "Honeywell announces plan to spin off Advanced Materials business"},
            {"date": "2025-02-05", "title": "Honeywell separates into three independent companies"},
            {"date": "2026-06-29", "title": "Honeywell Aerospace (HONA) begins trading on Nasdaq"},
        ],
        "status": "completed",
        "source": "manual",
    },
    {
        "ticker": "SOLV",
        "name": "Solventum",
        "nameCN": "索尔文图姆",
        "spinoffName": "Solventum (spun from 3M)",
        "spinoffTicker": "SOLV",
        "type": "spinoff",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2024-04-01", "title": "3M completes spin-off of Solventum healthcare business"},
        ],
        "status": "completed",
        "source": "manual",
    },
    {
        "ticker": "GEV",
        "name": "GE Vernova",
        "nameCN": "GE威诺华",
        "spinoffName": "GE Vernova (spun from GE)",
        "spinoffTicker": "GEV",
        "type": "spinoff",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2024-04-02", "title": "GE completes spin-off of GE Vernova energy business"},
        ],
        "status": "completed",
        "source": "manual",
    },
    {
        "ticker": "KVUE",
        "name": "Kenvue",
        "nameCN": "科沃",
        "spinoffName": "Kenvue (spun from J&J)",
        "spinoffTicker": "KVUE",
        "type": "carveout",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2023-05-04", "title": "Johnson & Johnson completes IPO of Kenvue consumer health business"},
            {"date": "2023-08-23", "title": "J&J completes full separation of Kenvue via exchange offer"},
        ],
        "status": "completed",
        "source": "manual",
    },
    {
        "ticker": "CMCSA",
        "name": "Comcast",
        "nameCN": "康卡斯特",
        "spinoffName": "SpinCo (NBCUniversal cable networks)",
        "spinoffTicker": "TBD",
        "type": "spinoff",
        "exchange": "Nasdaq",
        "announcements": [
            {"date": "2024-11-19", "title": "Comcast announces plan to spin off NBCUniversal cable networks"},
            {"date": "2025-06-01", "title": "Comcast SpinCo separation update"},
        ],
        "status": "in_progress",
        "source": "manual",
    },
    {
        "ticker": "MDT",
        "name": "Medtronic",
        "nameCN": "美敦力",
        "spinoffName": "Patient Monitoring & Respiratory (NewCo)",
        "spinoffTicker": "TBD",
        "type": "spinoff",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2023-10-10", "title": "Medtronic announces intent to spin off Patient Monitoring business"},
        ],
        "status": "in_progress",
        "source": "manual",
    },
    {
        "ticker": "JNJ",
        "name": "Johnson & Johnson",
        "nameCN": "强生",
        "spinoffName": "Kenvue (completed 2023)",
        "spinoffTicker": "KVUE",
        "type": "carveout",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2023-08-23", "title": "J&J completes full separation from Kenvue"},
        ],
        "status": "completed",
        "source": "manual",
    },
    {
        "ticker": "KDP",
        "name": "Keurig Dr Pepper",
        "nameCN": "科瑞格胡椒博士",
        "spinoffName": "Global Coffee Co.（Peet's + Keurig + Jacobs + L'OR）",
        "spinoffTicker": "TBD",
        "type": "spinoff",
        "exchange": "Nasdaq",
        "announcements": [
            {"date": "2025-08-25", "title": "KDP宣布以157亿欧元收购JDE Peet's，计划拆分为饮料公司与全球咖啡公司两家独立上市公司"},
            {"date": "2026-06-25", "title": "KDP重申2026年展望，拆分预计2027年初完成"},
        ],
        "status": "in_progress",
        "source": "manual",
    },
    {
        "ticker": "BDX",
        "name": "Becton Dickinson",
        "nameCN": "碧迪",
        "spinoffName": "BD MedSurg (NewCo)",
        "spinoffTicker": "TBD",
        "type": "spinoff",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2024-05-16", "title": "Becton Dickinson announces plan to spin off MedSurg segment"},
        ],
        "status": "in_progress",
        "source": "manual",
    },
    {
        "ticker": "SOLV",
        "name": "Solventum",
        "spinoffName": "Purification Solutions (to be spun off)",
        "spinoffTicker": "TBD",
        "type": "spinoff",
        "exchange": "NYSE",
        "announcements": [
            {"date": "2024-10-23", "title": "Solventum announces intent to divest Purification Solutions business"},
        ],
        "status": "announced",
        "source": "manual",
    },
]


def sec_get(url, opener, sleep=0.3):
    """带重试的 SEC GET 请求"""
    for attempt in range(3):
        try:
            time.sleep(sleep)
            req = Request(url, headers={"User-Agent": UA})
            return opener.open(req, timeout=20).read()
        except HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)
                print(f"  429 限流，等 {wait}s ...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
        except URLError as e:
            if attempt < 2:
                time.sleep(10)
            else:
                raise
    raise RuntimeError(f"SEC GET 失败: {url}")


def search_edgar(opener, query, days=365):
    """搜索 EDGAR 8-K，返回 (adsh, cik, entity_name, file_date) 列表"""
    end_dt = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    start_dt = (datetime.now(timezone.utc) - timedelta(days=days)).strftime('%Y-%m-%d')
    results = []
    from_offset = 0
    page_size = 40

    while True:
        # 手动拼接 URL，避免 urlencode 对引号的处理问题
        q_enc = urllib.parse.quote(query, safe='')
        # EDGAR 要求空格用 + 不用 %20
        q_enc = q_enc.replace('%20', '+')
        url = (f"{EDGAR_BASE}/LATEST/search-index"
               f"?q={q_enc}&forms=8-K"
               f"&dateRange=custom&startdt={start_dt}&enddt={end_dt}"
               f"&from={from_offset}&size={page_size}")
        try:
            data = json.loads(sec_get(url, opener))
        except Exception as e:
            print(f"  搜索失败: {e}", file=sys.stderr)
            break

        hits = data.get('hits', {}).get('hits', [])
        if not hits:
            break

        for h in hits:
            src = h.get('_source', {})
            ciks = src.get('ciks', [])
            names = src.get('display_names', [])
            adsh = src.get('adsh', '')
            file_date = src.get('file_date', '')
            if ciks and names and adsh:
                cik = ciks[0].lstrip('0')
                # 提取 ticker
                name_raw = names[0]
                ticker_m = re.search(r'\(([A-Z]{1,5}(?:\.[A-Z]{1,2})?)\)', name_raw)
                ticker = ticker_m.group(1) if ticker_m else ''
                entity = re.sub(r'\s*\([^)]+\)\s*$', '', name_raw).strip()
                results.append({
                    'adsh': adsh,
                    'cik': cik,
                    'ticker': ticker,
                    'entity': entity,
                    'file_date': file_date,
                })

        total = data.get('hits', {}).get('total', {}).get('value', 0)
        from_offset += page_size
        if from_offset >= min(total, 400):  # Bounded pagination, not just the first result page
            break

    return results


def primary_8k_document(index_html, cik, adsh):
    """Select the document whose SEC document-table Type is 8-K, never the first attachment."""
    from html import unescape
    prefix = f"/Archives/edgar/data/{int(cik)}/{adsh.replace('-', '')}/"
    for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>', index_html, re.S | re.I):
        cells = re.findall(r'<td\b[^>]*>(.*?)</td>', row, re.S | re.I)
        labels = [unescape(re.sub(r'<[^>]+>', '', c)).strip() for c in cells]
        if '8-K' not in labels and '8-K/A' not in labels:
            continue
        for href in re.findall(r'href=["\']([^"\']+)["\']', row, re.I):
            href = unescape(href)
            if 'doc=' in href:
                href = urllib.parse.parse_qs(urllib.parse.urlparse(href).query).get('doc', [''])[0]
            if href.startswith(prefix) and re.search(r'\.html?$', href, re.I):
                return href.rsplit('/', 1)[-1]
    return ''


def fetch_8k_text(cik, adsh, opener, ann=None):
    """Read the exact primary 8-K identified by SEC metadata; preserve its URL."""
    from html import unescape
    try:
        document = (ann or {}).get('primaryDocument', '')
        if not document:
            index = sec_get(filing_url(cik, adsh), opener, sleep=0.2).decode('utf-8', errors='replace')
            document = primary_8k_document(index, cik, adsh)
        if not document:
            record_source_warning('spinoff_us', '部分 SEC 主文件未能读取；保留历史证据，相关档案待核实')
            return ''
        url = filing_url(cik, adsh, document)
        raw = sec_get(url, opener, sleep=0.2).decode('utf-8', errors='replace')
        raw = re.sub(r'<(?:script|style)\b[^>]*>.*?</(?:script|style)>', ' ', raw, flags=re.S | re.I)
        text = unescape(re.sub(r'<[^>]+>', ' ', raw))
        text = re.sub(r'\s+', ' ', text).strip()
        if ann is not None:
            ann.update(primaryDocument=document, url=url)
        return text[:240000]
    except Exception as exc:
        print(f"  8-K document unavailable: {adsh}: {exc}", file=sys.stderr)
        record_source_warning('spinoff_us', '部分 SEC 主文件未能读取；保留历史证据，相关档案待核实')
        return ''


def classify_type(text):
    """从 8-K 正文判断分拆类型"""
    t = text.lower()
    if re.search(r'split[- ]?off|exchange offer.{0,100}(?:subsidiary|spinco|spin-off)', t):
        return 'splitoff'
    if re.search(r'(?:equity )?carve[- ]?out|initial public offering of.{0,100}(?:subsidiary|spinco)', t):
        return 'carveout'
    if any(re.search(p, t) for p in TYPE_SPINOFF):
        return 'spinoff'
    return 'spinoff'  # 默认


def get_status(text):
    return infer_status(text)['status']


def extract_spinoff_name(text):
    return extract_name(text)


def extract_dates(text):
    dates = evidence_dates(text)
    return dates.get('recordDate', {}).get('date', ''), dates.get('distributionDate', {}).get('date', '')


def get_market_cap_from_facts(cik, opener):
    """从 EDGAR company facts 获取最新市值（用 EntityCommonStockSharesOutstanding × price 近似）"""
    # 简化：直接返回 None（跳过市值过滤，改用 yfinance 在后期过滤）
    return None


def _fetch_us_market_caps(companies):
    """
    用 Finnhub /stock/metric 批量拉母公司市值。
    写入 c['parentMarketCap']（单位：亿美元，保留1位小数）。
    已有且非0则跳过（增量）。
    """
    fh_key = os.environ.get('FINNHUB_KEY', '')
    if not fh_key:
        print("  FINNHUB_KEY 未设置，跳过市值拉取")
        return

    need = [c for c in companies if not c.get('parentMarketCap')]
    if not need:
        print(f"  所有公司已有 parentMarketCap，跳过")
        return

    print(f"  拉取母公司市值（{len(need)} 家）...")
    for c in need:
        tk = c['ticker']
        try:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={tk}&metric=all&token={fh_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())
            mc = data.get('metric', {}).get('marketCapitalization')  # 单位：百万美元
            if mc and mc > 0:
                c['parentMarketCap'] = round(mc / 100, 1)  # 转换为亿美元
                print(f"    {tk}: ${c['parentMarketCap']}亿")
            else:
                print(f"    {tk}: 无数据")
        except Exception as e:
            print(f"    {tk}: 失败 {e}")
        time.sleep(0.3)  # Finnhub 免费版限速 60次/分钟


def _fetch_spinoff_target_market_caps(companies):
    """
    用 Finnhub /stock/metric 拉分拆标的自身市值（而非母公司）。
    仅对已有 spinoffTicker 的公司生效——没有独立 ticker 就无法查市值。
    写入 c['marketCap']（单位：亿美元，保留1位小数）。
    已有且非0则跳过（增量）。
    格林布拉特分拆点评的市值比例信号依赖这个字段。
    """
    fh_key = os.environ.get('FINNHUB_KEY', '')
    if not fh_key:
        print("  FINNHUB_KEY 未设置，跳过分拆标的市值拉取")
        return

    need = [
        c for c in companies
        if c.get('spinoffTicker') and c['spinoffTicker'].upper() != 'TBD'
        and not c.get('marketCap')
    ]
    if not need:
        print("  无可拉取分拆标的市值的公司（均缺 spinoffTicker 或已有 marketCap）")
        return

    print(f"  拉取分拆标的市值（{len(need)} 家）...")
    for c in need:
        tk = c['spinoffTicker']
        try:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={tk}&metric=all&token={fh_key}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            resp = urllib.request.urlopen(req, timeout=10)
            data = json.loads(resp.read().decode())
            mc = data.get('metric', {}).get('marketCapitalization')  # 单位：百万美元
            if mc and mc > 0:
                c['marketCap'] = round(mc / 100, 1)  # 转换为亿美元
                print(f"    {c['ticker']}→{tk}: ${c['marketCap']}亿")
            else:
                print(f"    {c['ticker']}→{tk}: 无数据")
        except Exception as e:
            print(f"    {c['ticker']}→{tk}: 失败 {e}")
        time.sleep(0.3)  # Finnhub 免费版限速 60次/分钟


def dedupe(companies):
    """按 ticker 去重，保留公告最多的"""
    seen = {}
    for c in companies:
        tk = c['ticker']
        c['filingEvidence'] = merge_evidence(prev_us.get(tk, {}).get('filingEvidence', []), c.get('filingEvidence', []))
        c['identityChecks'] = dict(prev_us.get(tk, {}).get('identityChecks', {}))
        if tk not in seen or len(c['announcements']) > len(seen[tk]['announcements']):
            seen[tk] = c
    return list(seen.values())


def filter_status(companies):
    """Retain completed and terminated dossiers for the dashboard's status filters."""
    return companies


# SiliconFlow 免费模型列表（按优先级排序，主模型下线自动 fallback）
_SF_MODELS = [
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.5-4B",
    "THUDM/glm-4-9b-chat",
]


_SF_UNAVAILABLE = False
_SF_REJECTED_MODELS = set()


def _sf_call(api_key, prompt, max_tokens=300, retries=2):
    """
    健壮的 SiliconFlow 调用封装：
    - 多模型 fallback（主模型失败自动切换）
    - 请求失败自动重试（默认 2次）
    - 返回 (text, model_used) 或 (None, None)
    """
    global _SF_UNAVAILABLE
    if not api_key or _SF_UNAVAILABLE:
        return (None, None)
    for model in _SF_MODELS:
        if model in _SF_REJECTED_MODELS:
            continue
        for attempt in range(retries + 1):
            try:
                payload = json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "stream": False,
                    "enable_thinking": False,
                }).encode()
                req = Request(
                    "https://api.siliconflow.cn/v1/chat/completions",
                    data=payload,
                    headers={
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                    },
                    method="POST",
                )
                with urlopen(req, timeout=35) as resp:
                    data = json.loads(resp.read())
                text = data['choices'][0]['message']['content'].strip()
                if text:  # 非空则成功
                    return text, model
            except Exception as e:
                code = getattr(e, 'code', None)
                if code in (401, 402):
                    _SF_UNAVAILABLE = True
                    record_ai_warning('spinoff_us', code)
                    print(f"::warning::AI enrichment unavailable (HTTP {code}); "
                          "skipping further model requests in this process and keeping existing text.")
                    return (None, None)
                if code in (403, 404):
                    _SF_REJECTED_MODELS.add(model)
                    print(f"::warning::AI model {model} unavailable (HTTP {code}); trying next model.")
                    break
                wait = 2 ** attempt
                print(f"    [{model}] 第{attempt+1}次失败: {e}，{'retry in ' + str(wait) + 's' if attempt < retries else '放弃'}")
                if attempt < retries:
                    time.sleep(wait)
        print(f"    模型 {model} 全部失败，尝试下一个...")
    record_ai_warning('spinoff_us')
    return None, None


def _translate_via_sf(ticker_name_map, api_key):
    """调用 SiliconFlow API 批量翻译公司名为中文，返回 {ticker: nameCN} 字典"""
    if not ticker_name_map or not api_key:
        return {}

    lines = '\n'.join(f"{t}: {n}" for t, n in ticker_name_map.items())
    prompt = (
        "以下是美股上市公司的英文名称（格式：ticker: 英文名），"
        "请将每家公司翻译成中文常用名称（4-8字，简洁），"
        "输出格式严格为每行 ticker: 中文名，不要其他内容。\n\n" + lines
    )
    text, model = _sf_call(api_key, prompt, max_tokens=300)
    if not text:
        print("  SiliconFlow 翻译全部失败，跳过")
        return {}

    result = {}
    for line in text.splitlines():
        # 容错：兼容全角冒号 / 多余空格
        m = re.match(r'^([A-Z0-9.\-]+)[:\uff1a]\s*(.+)$', line.strip())
        if m:
            t, cn = m.group(1), m.group(2).strip()
            # 去掉可能的引号/括号
            cn = re.sub(r'^[\'"`「」『』【】]+|[\'"`「」『』【】]+$', '', cn)
            if t in ticker_name_map and cn:
                result[t] = cn
    print(f"  [{model}] 翻译成功 {len(result)}/{len(ticker_name_map)} 家")
    return result


def _refine_spinoff_names(companies, api_key):
    """用 LLM 批量精化占位符式 spinoffName，每批最多 10 家"""
    BATCH = 10
    for i in range(0, len(companies), BATCH):
        batch = companies[i:i+BATCH]
        lines = []
        for c in batch:
            anns = c.get('announcements', [])
            titles = ' | '.join(a.get('title', '') for a in anns[:3])
            lines.append(f"{c['ticker']} ({c['name']}): {titles[:120]}")
        prompt = (
            "以下每行是一家美股公司及其相关公告标题，这家公司正在分拆或分离一部分业务。\n"
            "请根据公告标题推断被分拆出去的子公司名称（英文，2-6个单词，如无法判断则回答 unknown）。\n"
            "输出格式严格为每行 ticker: 子公司名称，不要其他内容。\n\n"
            + '\n'.join(lines)
        )
        text, model = _sf_call(api_key, prompt, max_tokens=200)
        if not text:
            print(f"  第{i//BATCH+1}批 LLM 失败，跳过")
            continue
        # 解析
        result = {}
        for line in text.splitlines():
            m = re.match(r'^([A-Z0-9.\-]+)[:\uff1a]\s*(.+)$', line.strip())
            if m:
                t, name = m.group(1), m.group(2).strip()
                name = re.sub(r'^[\'"`]+|[\'"`]+$', '', name)
                if name.lower() not in ('unknown', 'n/a', ''):
                    result[t] = name
        for c in batch:
            t = c['ticker']
            if t in result:
                old = c.get('spinoffName', '')
                c['spinoffName'] = result[t]
                print(f"  {t}: '{old}' → '{result[t]}'")
        time.sleep(0.5)


def _gen_us_ai_summary(companies, api_key):
    """为每家美股分拆公司生成一句话摘要，写入 aiSummary 字段。每批 8 家。"""
    BATCH = 8
    for i in range(0, len(companies), BATCH):
        batch = companies[i:i+BATCH]
        lines = []
        for c in batch:
            type_label = {'spinoff':'纯分拆','carveout':'子公司IPO','splitoff':'换股分拆'}.get(c.get('type',''), c.get('type',''))
            spin_name  = c.get('spinoffName','') or ''
            ann_titles = ' | '.join(a.get('title','')[:50] for a in c.get('announcements',[])[:2])
            lines.append(
                f"{c['ticker']} ({c.get('nameCN') or c.get('name','')})"
                f"（类型:{type_label}" + (f"，分拆目标:{spin_name}" if spin_name else "") + f"）"
                f" 公告: {ann_titles[:100]}"
            )
        prompt = (
            "以下每行是一家美股公司及其分拆公告摘要。\n"
            "请为每家公司生成一句话中文摘要（20-45字），说明分拆进展和子公司业务，如知道请指出预计完成时间。\n"
            "输出格式严格为每行 ticker: 摘要，不要其他内容。\n\n"
            + '\n'.join(lines)
        )
        text, model = _sf_call(api_key, prompt, max_tokens=400)
        if not text:
            print(f"  第{i//BATCH+1}批 aiSummary 失败")
            continue
        result = {}
        for line in text.splitlines():
            m = re.match(r'^([A-Z0-9.\-]+)[:\uff1a]\s*(.+)$', line.strip())
            if m:
                result[m.group(1)] = m.group(2).strip()
        for c in batch:
            t = c['ticker']
            if t in result:
                c['aiSummary'] = result[t]
                print(f"  [{model}] {t}: {result[t]}")
        time.sleep(0.5)


def _load_prev_us():
    """加载上次 spinoff_us.json，返回 {ticker: company_dict}，用于增量合并。"""
    try:
        with open('spinoff_us.json', encoding='utf-8') as f:
            data = json.load(f)
        return {c['ticker']: c for c in data.get('companies', [])}
    except Exception:
        return {}


def main():
    opener = build_opener(HTTPCookieProcessor(CookieJar()))

    print("=== fetch_spinoff_us.py ===")
    # 加载旧数据，用于保留 completed 案例和 aiSummary
    prev_us = _load_prev_us()
    print(f"  旧数据: {len(prev_us)} 家")

    date_from = (datetime.now(timezone.utc) - timedelta(days=SEARCH_DAYS)).strftime('%Y%m%d')
    date_to = datetime.now(timezone.utc).strftime('%Y%m%d')
    print(f"搜索范围: {date_from} ~ {date_to}")

    # Step 1: 搜索 EDGAR
    queries = [
        '"spin-off" "distribution date"',
        '"spin-off" "record date" "separation"',
        '"spinoff" "distribution date"',
        '"separation" "distribution date" "spin"',
    ]

    all_hits = {}
    for q in queries:
        print(f"\n搜索: {q}")
        hits = search_edgar(opener, q, days=SEARCH_DAYS)
        print(f"  找到 {len(hits)} 条 8-K")
        for h in hits:
            key = h['adsh']
            if key not in all_hits:
                all_hits[key] = h

    print(f"\n去重后共 {len(all_hits)} 条 8-K")
    if not all_hits:
        raise RuntimeError('No SEC search results; refusing to overwrite the last successful dataset')

    # Step 2: 分两步处理
    # 第一步：按 ticker 分组，建立公司列表（不拉正文）
    companies_map = {}  # ticker -> {company info}
    for adsh, hit in all_hits.items():
        ticker = hit['ticker']
        if not ticker or len(ticker) < 2:
            continue
        ann = {
            'date': hit['file_date'],
            'title': f"SEC 8-K: {hit['entity']} spin-off filing",
            'url': filing_url(hit['cik'], adsh),
            'adsh': adsh,
        }
        if ticker in companies_map:
            existing_ids = {a.get('adsh') for a in companies_map[ticker]['announcements']}
            if adsh not in existing_ids:
                companies_map[ticker]['announcements'].append(ann)
                companies_map[ticker]['announcements'].sort(key=lambda x: x['date'], reverse=True)
        else:
            companies_map[ticker] = {
                'ticker': ticker,
                'name': hit['entity'],
                'spinoffName': '',
                'spinoffTicker': '',
                'type': 'spinoff',  # 默认，第二步再精化
                'exchange': 'NYSE/Nasdaq',
                'recordDate': '',
                'distributionDate': '',
                'announcements': [ann],
                'status': 'in_progress',
                'source': 'edgar',
                'cik': hit['cik'],
            }

    print(f"  初步收录 {len(companies_map)} 家公司")

    # 第二步：解析每家公司的最新正文，并保留已有证据。
    print("  拉取全部候选公司的 8-K 正文...")
    for ticker, company in companies_map.items():
        latest_ann = company['announcements'][0]
        adsh = latest_ann.get('adsh', '')
        cik = company['cik']
        if not adsh or not cik:
            continue
        print(f"  {ticker} ...", end=' ', flush=True)
        company['filingEvidence'] = list(prev_us.get(ticker, {}).get('filingEvidence', []))
        text = fetch_8k_text(cik, adsh, opener, latest_ann)
        if not text:
            print('(no text)')
            continue
        t = text.lower()
        # 判断是否真实分拆公告
        if not any(re.search(p, t) for p in TYPE_SPINOFF + TYPE_CARVEOUT + TYPE_SPLITOFF):
            print('(not spinoff, skip)')
            company['filingEvidence'] = merge_evidence(company['filingEvidence'], [parse_evidence(text, latest_ann, cik)])
            continue
        company['type'] = classify_type(text)
        company['status'] = get_status(text)
        sname = extract_spinoff_name(text)
        if sname:
            company['spinoffName'] = sname
        rd, dd = extract_dates(text)
        company['recordDate'] = rd
        company['distributionDate'] = dd
        company['filingEvidence'] = merge_evidence(company['filingEvidence'], [parse_evidence(text, latest_ann, cik)])
        # Parse another relevant filing independently so distinct named targets remain separate.
        for other_ann in company['announcements'][1:2]:
            other_text = fetch_8k_text(cik, other_ann['adsh'], opener, other_ann)
            if other_text:
                company['filingEvidence'] = merge_evidence(company['filingEvidence'], [parse_evidence(other_text, other_ann, cik)])
        print(f"({company['type']}, {company['status']})")

    # Resolve exact primary documents only for search-matched filings. Ordinary
    # Item 1.01/8.01 filings are not automatically spin-off announcements.
    for company in list(companies_map.values())[:50]:
        cik = company.get('cik', '')
        try:
            sub = json.loads(sec_get(f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json", opener, sleep=0.1))
            recent = sub['filings']['recent']
            docs = dict(zip(recent['accessionNumber'], recent['primaryDocument']))
            for ann in company['announcements']:
                ann['primaryDocument'] = docs.get(ann['adsh'], '')
                ann['url'] = filing_url(cik, ann['adsh'], ann['primaryDocument'])
        except Exception as exc:
            print(f"  Exact document lookup unavailable: {company['ticker']}: {exc}")

    # Step 3: 合并手动维护的已知案例
    print("\n合并已知案例...")
    for known in KNOWN_SPINOFFS:
        tk = known['ticker']
        if tk in companies_map:
            # 补充手动信息
            if known.get('spinoffName') and companies_map[tk]['spinoffName'] in ('(解析中)', ''):
                companies_map[tk]['spinoffName'] = known['spinoffName']
            if known.get('spinoffTicker'):
                companies_map[tk]['spinoffTicker'] = known['spinoffTicker']
            # 合并公告（避免重复）
            existing_dates = {a['date'] for a in companies_map[tk]['announcements']}
            for ann in known.get('announcements', []):
                if ann['date'] not in existing_dates:
                    companies_map[tk]['announcements'].append(ann)
            companies_map[tk]['announcements'].sort(key=lambda x: x['date'], reverse=True)
        else:
            companies_map[tk] = {
                'ticker': known['ticker'],
                'name': known['name'],
                'spinoffName': known.get('spinoffName', ''),
                'spinoffTicker': known.get('spinoffTicker', ''),
                'type': known.get('type', 'spinoff'),
                'exchange': known.get('exchange', 'NYSE/Nasdaq'),
                'recordDate': known.get('recordDate', ''),
                'distributionDate': known.get('distributionDate', ''),
                'announcements': known.get('announcements', []),
                'status': known.get('status', 'in_progress'),
                'source': 'manual',
                'cik': '',
            }
            print(f"  + 手动添加: {known['ticker']} {known['name']}")

    companies = list(companies_map.values())

    # Step 3.1: 从旧数据恢复 aiSummary 和 parentMarketCap（避免重复消耗 API 额度）
    for c in companies:
        tk = c['ticker']
        if not c.get('aiSummary') and tk in prev_us and prev_us[tk].get('aiSummary'):
            c['aiSummary'] = prev_us[tk]['aiSummary']
        if not c.get('parentMarketCap') and tk in prev_us and prev_us[tk].get('parentMarketCap'):
            c['parentMarketCap'] = prev_us[tk]['parentMarketCap']

    # Step 3.2: 将旧数据中 completed 案例补回（本次搜索窗口外的不会重新出现）
    cutoff_completed = (datetime.now(timezone.utc) - timedelta(days=365)).strftime('%Y-%m-%d')
    current_tickers = {c['ticker'] for c in companies}
    for tk, old_c in prev_us.items():
        if tk in current_tickers:
            continue
        # 只保留最近365天内有公告的旧案例（completed 或 in_progress）
        dates = [a['date'] for a in old_c.get('announcements', []) if a.get('date')]
        if dates and max(dates) >= cutoff_completed:
            companies.append(old_c)
            print(f"  [旧数据恢复] {tk} {old_c.get('name','')} ({old_c.get('status','')})")

    # Step 3.5: 自动匹配子公司 ticker（通过 EDGAR 搜索子公司名称）
    def lookup_spinoff_ticker(spinoff_name, parent_ticker, opener):
        """用 EDGAR 全文搜索找到子公司 CIK，再查 submissions 拿 ticker"""
        if not spinoff_name or spinoff_name in ('TBD', '(\u89e3\u6790\u4e2d)', ''):
            return ''
        # 取前20字符做关键词，过滤过于通用的名字
        kw = spinoff_name.split('\uff08')[0].split('(')[0].strip()
        kw = kw[:20].rstrip(', ')
        GENERIC_NAMES = {'SpinCo', 'NewCo', 'Spinoff', 'New Company', 'TBD', 'Holdco',
                         'BD MedSurg', 'Global Coffee Co', 'Patient Monitoring'}
        if not kw or len(kw) < 4 or kw in GENERIC_NAMES:
            return ''
        try:
            q = urllib.parse.quote(f'"{kw}"', safe='').replace('%20', '+')
            url = (f"https://efts.sec.gov/LATEST/search-index"
                   f"?q={q}&forms=10-12B,S-1,S-11,10-K"
                   f"&dateRange=custom&startdt=2022-01-01&enddt=2026-12-31")
            hits = json.loads(sec_get(url, opener, sleep=0.1))['hits']['hits']
            if not hits:
                return ''
            def identity(value):
                words = re.findall(r'[a-z0-9]+', value.lower())
                return [w for w in words if w not in {'inc', 'corp', 'corporation', 'ltd', 'llc', 'the', 'co'}]
            expected = identity(spinoff_name)
            candidates = set()
            for hit in hits:
                src = hit.get('_source', {})
                for display in src.get('display_names', []):
                    issuer = re.sub(r'\s*\([^)]*\)', '', display)
                    if expected and identity(issuer) == expected and len(src.get('ciks', [])) == 1:
                        candidates.add(src['ciks'][0])
            if len(candidates) != 1:
                return ''
            cik = candidates.pop()
            cik_padded = cik.zfill(10)
            sub = json.loads(sec_get(f"https://data.sec.gov/submissions/CIK{cik_padded}.json", opener, sleep=0.1))
            tickers = [t for t in sub.get('tickers', []) if t]
            # 过滤：不能是母公司自己的 ticker
            tickers = [t for t in tickers if t != parent_ticker]
            return tickers[0] if len(tickers) == 1 else ''
        except Exception:
            return ''

    print("\n  匹配子公司 ticker...")
    for c in companies:
        if c.get('spinoffTicker') in ('', 'TBD', None) and c.get('spinoffName'):
            t = lookup_spinoff_ticker(c['spinoffName'], c['ticker'], opener)
            if t:
                c['spinoffTicker'] = t
                print(f"  {c['ticker']} → spinoffTicker={t}")
        time.sleep(0.05)

    # Step 3.8: 拉取母公司市值
    print("\nStep 3.8: 拉取母公司市值...")
    _fetch_us_market_caps(companies)

    # Step 3.9: 拉取分拆标的自身市值（仅已有 spinoffTicker 的公司）
    print("\nStep 3.9: 拉取分拆标的市值...")
    _fetch_spinoff_target_market_caps(companies)

    # Step 4: 状态过滤
    print("\n状态过滤...")
    before = len(companies)
    companies = filter_status(companies)
    print(f"  {before} → {len(companies)} 家（保留已完成及已终止档案）")

    # Step 5: 添加中文名（手动字典 + SiliconFlow 兜底翻译）
    for c in companies:
        t = c.get('ticker', '')
        c['nameCN'] = CN_NAMES.get(t, '')

    # Step 5b: 对字典缺失的条目，用 SiliconFlow API 批量翻译
    sf_key = os.environ.get('SILICONFLOW_KEY', '')
    if sf_key:
        missing = {c['ticker']: c['name'] for c in companies if not c.get('nameCN') and c.get('name')}
        if missing:
            print(f"  Step 5b: 调用 SiliconFlow 翻译 {len(missing)} 家...")
            translated = _translate_via_sf(missing, sf_key)
            for c in companies:
                t = c.get('ticker', '')
                if not c.get('nameCN') and t in translated:
                    c['nameCN'] = translated[t]
        else:
            print("  Step 5b: 无缺失中文名，跳过翻译")
    else:
        missing_count = sum(1 for c in companies if not c.get('nameCN'))
        if missing_count:
            print(f"  Step 5b: SILICONFLOW_KEY 未设置，{missing_count} 家缺中文名")

    companies.sort(key=lambda c: max((a['date'] for a in c['announcements']), default=''), reverse=True)

    # Step 6: LLM 精化 spinoffName（对占位符/空值用公告标题推断）
    sf_key = os.environ.get('SILICONFLOW_KEY', '')
    if sf_key:
        need_name = [
            c for c in companies
            if not c.get('spinoffName') or
               c.get('spinoffName', '').lower() in ('spinco', 'newco', 'tbd') or
               re.search(r'\b(spinco|newco)\b', c.get('spinoffName', ''), re.I)
        ]
        if need_name:
            print(f"\nStep 6: LLM 精化 spinoffName（{len(need_name)} 家）...")
            _refine_spinoff_names(need_name, sf_key)
        else:
            print("\nStep 6: 无需 spinoffName 精化")

        # Step 7: LLM 生成 aiSummary（已有则跳过，节省 API 额度）
        need_summary = [c for c in companies if not c.get('aiSummary')]
        if need_summary:
            print(f"\nStep 7: LLM 生成 aiSummary（{len(need_summary)}/{len(companies)} 家需更新）...")
            _gen_us_ai_summary(need_summary, sf_key)
        else:
            print(f"\nStep 7: 所有 {len(companies)} 家已有 aiSummary，跳过")

    # 输出
    out = {
        'updatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'dateFrom': date_from,
        'dateTo': date_to,
        'count': len(companies),
        'companies': companies,
    }

    try:
        with open('spinoff_us.json', encoding='utf-8') as old_file:
            previous = json.load(old_file)
    except (OSError, ValueError):
        previous = {}
    out = normalize(out, 'us', previous=previous)

    with open('spinoff_us.json', 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(f"\n✅ {len(companies)} 家美股分拆事件 → spinoff_us.json")

    # 打印摘要
    type_count = {}
    for c in companies:
        type_count[c['type']] = type_count.get(c['type'], 0) + 1
    for t, n in sorted(type_count.items()):
        print(f"  {t}: {n} 家")


if __name__ == '__main__':
    main()
