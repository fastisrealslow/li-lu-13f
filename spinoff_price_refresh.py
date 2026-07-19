#!/usr/bin/env python3
"""
HK Spinoff Price Auto-Refresh Pipeline
=====================================
功能：
  1. 自动检测公告中是否已上市（多模式匹配）
  2. 按市场类型（HK/A股/美股/海外）模糊匹配子公司 ticker
  3. 拉取上市价 + 今日价，写入 spinoff.json
  4. 适合每周 cron 定时运行

用法：
  python3 spinoff_price_refresh.py [--dry-run] [--ticker 02899.HK]

  --dry-run  仅打印结果，不写入文件
  --ticker   只处理指定母公司（调试用）
"""

import json, re, sys, argparse, warnings, time, os
from pathlib import Path
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from rapidfuzz import fuzz, process as rfprocess

warnings.filterwarnings('ignore')
TODAY = datetime.today().strftime('%Y-%m-%d')

# ── 路径 ──────────────────────────────────────────────────────────
REPO_DIR     = Path(__file__).parent
BKTEST_DIR   = Path(__file__).parent / 'spinoff_cache'
SPINOFF_JSON = REPO_DIR / 'spinoff.json'
HK_DB_PATH   = BKTEST_DIR / 'hk_stock_db.json'
A_DB_PATH    = BKTEST_DIR / 'a_stock_db.json'
LOG_PATH     = BKTEST_DIR / 'refresh_log.jsonl'

# ── 手工知识库（高置信度，直接用，优先于自动匹配）─────────────────
# 格式：parent_ticker -> {spinoff, name, date, market, note?}
KNOWN_SPINOFFS = {
    '09618.HK': {'spinoff': '7618.HK',  'name': '京東工業',      'date': '2025-12-11', 'market': 'HK'},
    '00460.HK': {'spinoff': '2575.HK',  'name': '軒竹生物-B',     'date': '2025-10-15', 'market': 'HK'},
    '02899.HK': {'spinoff': '2259.HK',  'name': '紫金黃金國際',   'date': '2025-09-30', 'market': 'HK'},
    '07489.HK': {'spinoff': '7489.HK',  'name': '嵐圖汽車',       'date': '2026-02-12', 'market': 'HK',
                 'note': '介紹上市，無發行價'},
    # 可持续补充：
    # '00041.HK': {'spinoff': '778.HK', 'name': '鷹君房產信託', 'date': '2026-03-XX', 'market': 'HK'},
}

# 中文名 → 英文搜索 hint（用于港股名称库英文匹配）
CN_TO_EN_HINTS = {
    '京東工業': 'JD INDUSTRIALS', '京东工业': 'JD INDUSTRIALS',
    '軒竹生物': 'XUANZHU',        '轩竹生物': 'XUANZHU',
    '紫金黃金': 'ZIJIN GOLD',     '紫金黄金': 'ZIJIN GOLD',
    '嵐圖汽車': 'VOYAH',          '岚图汽车': 'VOYAH',
    '復星安特金': 'FOSUN ANTIGEN', '蔓迪': 'MANDI',
    '先聲再明': 'SIMCERE',        '先声再明': 'SIMCERE',
    '崑崙芯': 'KUNLUN CHIP',      '昆仑芯': 'KUNLUN CHIP',
    '惟遠能源': 'WYUN',           '通奧': 'TONAO',
    '物泊科技': 'UBOX',           '嘉泓': 'JIAHONG',
    '銅箔科技': 'COPPER FOIL',    '江銅': 'JIANGXI COPPER',
}

# ── 已上市判断（扩展版）──────────────────────────────────────────
IS_LISTED_PATTERNS = re.compile(
    r'開始買賣|开始买卖|股份開始|上市及買賣|上市及开始|'
    r'持續督導|持续督导|'
    r'介紹方式.*主板上市|以介紹方式.*香港|'
    r'完成建議分拆|完成.*分拆.*上市|'
    r'以實物分派.*生效|物分派.*完成|'
    r'悉數行使超額配股|全球發售.*最新資料.*買賣|'
    r'刊發招股章程.*開始買賣|开始交易|'
    r'股份已掛牌|已完成上市|已成功上市|已在.*交易所.*掛牌|'
    r'以實物分派.*保證.*權利|实物分派.*完成|'
    r'首日.*買賣|首日交易',
    re.I
)  # 注意：掛牌/挂牌 已移至 _WEAK_LISTED 两阶段检测，此处不再重复

# 进行中（不确定是否上市）
IN_PROGRESS_PATTERNS = re.compile(
    r'建議分拆|建议分拆|擬議分拆|拟议分拆|籌劃.*分拆|'
    r'進展公告|进展公告|更新資料|更新资料|'
    r'核查意見|法律意見書|风险提示',
    re.I
)

# 强上市信号：出现即确认已上市
_STRONG_LISTED = re.compile(
    r'開始買賣|开始买卖|股份開始|上市及買賣|首日.*買賣|首日交易|'
    r'股份已掛牌|已完成上市|完成建議分拆|以實物分派.*生效|悉數行使超額配股|'
    r'持續督導',
    re.I
)
# 弱信号：掛牌/挂牌 本身，但须排除"进展公告"/"建議分拆"类
_WEAK_LISTED   = re.compile(r'掛牌|挂牌', re.I)
_PROGRESS_EXCL = re.compile(r'之進展|进展公告|建議分拆|建议分拆|擬議|拟议|進展公告', re.I)

def detect_listing_status(titles: list[str], dates: list[str]) -> tuple[bool, str | None]:
    """两阶段检测：强信号直接确认，弱信号排除进展公告后再确认"""
    for title, date in zip(titles, dates):
        if _STRONG_LISTED.search(title):
            return True, date
        if _WEAK_LISTED.search(title) and not _PROGRESS_EXCL.search(title):
            return True, date
    # 兜底：原 IS_LISTED_PATTERNS（不含掛牌）
    for title, date in zip(titles, dates):
        if IS_LISTED_PATTERNS.search(title):
            return True, date
    return False, None

# ── 子公司名称提取 ────────────────────────────────────────────────
NAME_PATTERNS = [
    # 「分拆 X 并/至/于 [市场]上市」
    r'分拆\s*([\u4e00-\u9fff（）\(\)A-Za-z\s\-·]{2,30}?)\s*(?:並|及|至|于|在|到)\s*(?:香港|上海|深圳|全國|納|港|A股|菲律|新加|深交|上交)',
    # 「分拆 X 股份有限公司」
    r'分拆\s*([\u4e00-\u9fff\-·]{2,20}?)(?:股份有限公司|有限公司)',
    # 「建议分拆X」
    r'建[議议]分拆\s*([\u4e00-\u9fff（）A-Za-z\s\-·]{2,25}?)(?:\s|及|並|的|之|，|。)',
    # 「分拆所属子公司X」
    r'分拆所[屬属]子公司\s*([\u4e00-\u9fff（）\s\-]{2,30}?)(?:至|並|股份|有限)',
    # 「所属子公司X至...上市」
    r'所[屬属]子公司\s*([\u4e00-\u9fff（）\s\-]{2,25}?)(?:至|并|並)',
    # Maynilad / 英文名直接
    r'分拆\s*([A-Z][A-Za-z\s&\.,]{4,40}?)\s*(?:及|並|至|,|upon|on)',
]

def extract_spinoff_name(titles: list[str]) -> tuple[str, str]:
    """返回 (中文名, 英文名)"""
    full = ' '.join(titles)
    cn_name, en_name = '', ''

    for pat in NAME_PATTERNS:
        m = re.search(pat, full)
        if m:
            candidate = m.group(1).strip()
            # 清理尾部冗余词
            candidate = re.sub(r'\s*(股份有限公司|有限公司|集團控股|集團|控股|科技股份|生物科技)$', '', candidate).strip()
            if len(candidate) >= 2:
                if re.search(r'[\u4e00-\u9fff]', candidate):
                    cn_name = candidate
                else:
                    en_name = candidate
                break

    # 英文名从括号里提取
    if not en_name:
        m = re.search(r'\(([A-Z][A-Za-z\s&\.\-,]{3,50}?)\)', full)
        if m:
            c = m.group(1).strip()
            if len(c) > 3 and not re.match(r'^(CO|HK|LTD|LIMITED|INC|THE|AND|OR|FOR)$', c, re.I):
                en_name = c

    return cn_name, en_name

# ── 目标市场检测 ──────────────────────────────────────────────────
def detect_market(titles: list[str]) -> str:
    full = ' '.join(titles)
    # 注意优先级：A股 > HK（因为很多港股公司是分拆至A股）
    if re.search(r'上海證券交易所|深圳證券交易所|A股|科創板|創業板|全國中小企業股份轉讓|新三板', full):
        return 'A'
    if re.search(r'香港聯合交易所|香港聯交所|港交所|主板獨立上市|介紹方式.*主板|H股上市', full):
        return 'HK'
    if re.search(r'納斯達克|紐交所|NYSE|NASDAQ|美股|美國證券交易', full):
        return 'US'
    if re.search(r'菲律賓證券交易所|PSE|菲律宾', full):
        return 'PH'
    if re.search(r'新加坡交易所|SGX|新加坡', full):
        return 'SG'
    if re.search(r'泰國|泰国|泰交所', full):
        return 'TH'
    return 'UNKNOWN'

# ── 名称库 + 模糊匹配 ─────────────────────────────────────────────
_hk_names = None
_a_names  = None


# ── 名称库初始化（CI环境自动下载）────────────────────────────────
def ensure_dbs():
    """确保名称库存在，CI环境中自动拉取"""
    BKTEST_DIR.mkdir(parents=True, exist_ok=True)
    if not HK_DB_PATH.exists():
        print("Downloading HK stock database from HKEX...")
        try:
            import requests, io, openpyxl
            resp = requests.get(
                "https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx",
                timeout=30, headers={'User-Agent': 'Mozilla/5.0'}
            )
            wb = openpyxl.load_workbook(io.BytesIO(resp.content))
            ws = wb.active
            rows = list(ws.iter_rows(values_only=True))
            hk_db = {}
            header_row = None
            for i, row in enumerate(rows):
                if row and any(str(c).strip() in ('Stock Code','Name of Securities') for c in row if c):
                    header_row = i; break
            if header_row is not None:
                headers = [str(c).strip() if c else '' for c in rows[header_row]]
                ci = next((i for i,h in enumerate(headers) if 'Stock Code' in h), None)
                ni = next((i for i,h in enumerate(headers) if 'Name of Securities' in h), None)
                if ci is not None and ni is not None:
                    for row in rows[header_row+1:]:
                        code = str(row[ci]).strip() if row[ci] else ''
                        name = str(row[ni]).strip() if row[ni] else ''
                        if code and code.isdigit() and name:
                            hk_db[code.zfill(4) + '.HK'] = name
            with open(HK_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(hk_db, f, ensure_ascii=False)
            print(f"  HK DB: {len(hk_db)} stocks saved")
        except Exception as e:
            print(f"  HK DB download failed: {e}")
    
    if not A_DB_PATH.exists():
        print("Building A-share database via akshare...")
        try:
            import akshare as ak
            df = ak.stock_info_a_code_name()
            a_db = {}
            for _, row in df.iterrows():
                code, name = str(row.iloc[0]), str(row.iloc[1])
                suffix = '.SS' if code.startswith(('6','9')) else '.SZ'
                a_db[code + suffix] = name
                a_db[code] = name
            with open(A_DB_PATH, 'w', encoding='utf-8') as f:
                json.dump(a_db, f, ensure_ascii=False)
            print(f"  A DB: {len(a_db)//2} stocks saved")
        except Exception as e:
            print(f"  A DB build failed: {e}")
            with open(A_DB_PATH, 'w') as f: json.dump({}, f)

def load_dbs():
    global _hk_names, _a_names
    if _hk_names is None:
        with open(HK_DB_PATH, encoding='utf-8') as f:
            hk_db = json.load(f)
        _hk_names = [(name.upper(), ticker) for ticker, name in hk_db.items()]
    if _a_names is None:
        with open(A_DB_PATH, encoding='utf-8') as f:
            a_db = json.load(f)
        _a_names = [(name, ticker) for ticker, name in a_db.items() if '.' in ticker]
    return _hk_names, _a_names

def get_en_hint(cn_name: str) -> str:
    for k, v in CN_TO_EN_HINTS.items():
        if k in cn_name:
            return v
    return ''

def fuzzy_hk(en_query: str, threshold=60) -> list:
    if not en_query: return []
    hk_names, _ = load_dbs()
    hits = rfprocess.extract(en_query.upper(), [n for n,_ in hk_names],
                              scorer=fuzz.partial_ratio, limit=5)
    return [(s, hk_names[i][1], hk_names[i][0]) for _, s, i in hits if s >= threshold]

def fuzzy_a(cn_query: str, threshold=72) -> list:
    if not cn_query: return []
    _, a_names = load_dbs()
    hits = rfprocess.extract(cn_query, [n for n,_ in a_names],
                              scorer=fuzz.partial_ratio, limit=5)
    return [(s, a_names[i][1], a_names[i][0]) for _, s, i in hits if s >= threshold]

def search_us(en_query: str) -> list:
    if not en_query: return []
    try:
        res = yf.Search(en_query, max_results=5)
        return [(80, q.get('symbol',''), q.get('longname') or q.get('shortname',''))
                for q in (res.quotes or []) if q.get('symbol')]
    except: return []

# ── 价格拉取 ──────────────────────────────────────────────────────
def normalize_ticker(ticker: str) -> str:
    """去除港股 ticker 前导零: 07618.HK -> 7618.HK"""
    if ticker.endswith('.HK'):
        code = ticker[:-3].lstrip('0') or '0'
        return code + '.HK'
    return ticker

def fetch_price_on_date(ticker: str, date_str: str, window=7) -> float | None:
    tk = normalize_ticker(ticker)
    t0 = datetime.strptime(date_str, '%Y-%m-%d')
    for delta in list(range(0, window+1)) + list(range(-1, -(window+1), -1)):
        d = t0 + timedelta(days=delta)
        try:
            df = yf.download(tk,
                             start=d.strftime('%Y-%m-%d'),
                             end=(d+timedelta(days=2)).strftime('%Y-%m-%d'),
                             auto_adjust=True, progress=False)
            if not df.empty:
                close = df['Close']
                if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
                v = close.dropna()
                if not v.empty: return round(float(v.iloc[0]), 3)
        except: pass
    return None

def fetch_price_latest(ticker: str) -> float | None:
    tk = normalize_ticker(ticker)
    try:
        df = yf.download(tk, period='5d', auto_adjust=True, progress=False)
        if not df.empty:
            close = df['Close']
            if isinstance(close, pd.DataFrame): close = close.iloc[:,0]
            v = close.dropna()
            if not v.empty: return round(float(v.iloc[-1]), 3)
    except: pass
    try:
        info = yf.Ticker(tk).info
        p = info.get('currentPrice') or info.get('regularMarketPrice')
        return round(float(p), 3) if p else None
    except: return None

def fetch_a_price(raw_code: str, start_date: str) -> tuple[float | None, float | None]:
    """用 yfinance 拉取 A 股价格（自动尝试 .SS / .SZ 后缀）。
    Fix 4: 不再依赖 akshare，避免 CI 网络限制。
    """
    suffix_order = []
    # 上交所：6/9开头；深交所：0/2/3开头
    code = raw_code.lstrip('0') if raw_code.startswith('0') else raw_code
    if raw_code[:1] in ('6', '9'):
        suffix_order = ['.SS', '.SZ']
    else:
        suffix_order = ['.SZ', '.SS']

    for sfx in suffix_order:
        tk = raw_code + sfx
        try:
            # 拉取从上市日期到今天的历史数据
            import datetime
            start = start_date or '2020-01-01'
            df = yf.download(tk, start=start, auto_adjust=True, progress=False)
            if not df.empty:
                col = df['Close']
                if isinstance(col, pd.DataFrame): col = col.iloc[:,0]
                col = col.dropna()
                if not col.empty:
                    p0   = round(float(col.iloc[0]), 3)
                    pnow = round(float(col.iloc[-1]), 3)
                    return p0, pnow
        except: pass
    return None, None

# ── 处理单个公司 ─────────────────────────────────────────────────
def process_company(c: dict) -> dict | None:
    parent_tk  = c.get('ticker', '')
    stock_name = c.get('stockName', parent_tk)
    anns       = c.get('announcements', [])
    if not anns: return None

    titles = [a.get('title','') for a in anns if a.get('title')]
    dates  = sorted([a.get('date','') for a in anns if a.get('date')])

    # ── 优先：手工知识库 ──────────────────────────────────────────
    if parent_tk in KNOWN_SPINOFFS:
        info = KNOWN_SPINOFFS[parent_tk]
        spinoff_tk   = info['spinoff']
        listing_date = info['date']
        market       = info['market']
        has_ipo_price = not info.get('note', '').startswith('介紹')

        p0   = fetch_price_on_date(spinoff_tk, listing_date) if has_ipo_price else None
        pnow = fetch_price_latest(spinoff_tk)
        chg  = round((pnow - p0) / p0 * 100, 1) if p0 and pnow else None

        return {
            'ticker': parent_tk, 'company': stock_name,
            'spinoff_name': info['name'], 'matched_ticker': spinoff_tk,
            'target_market': market, 'is_listed': True,
            'listing_date': listing_date,
            'price_at_listing': p0, 'price_now': pnow, 'change_pct': chg,
            'currency': 'HKD', 'confidence': 100,
            'source': 'known_db', 'status': 'matched',
            'note': info.get('note', ''),
        }

    # ── 自动提取 ─────────────────────────────────────────────────
    is_listed, listing_date = detect_listing_status(titles, dates)
    if not is_listed:
        return {'ticker': parent_tk, 'status': 'not_listed_yet',
                'company': stock_name, 'is_listed': False}

    market          = detect_market(titles)
    cn_name, en_name = extract_spinoff_name(titles)
    listing_date    = listing_date or (dates[-1] if dates else TODAY)

    if not cn_name and not en_name:
        return {'ticker': parent_tk, 'status': 'name_not_extracted',
                'company': stock_name, 'is_listed': True, 'market': market}

    # ── 分市场匹配 ticker ──────────────────────────────────────────
    candidates = []
    if market == 'HK':
        en_hint = get_en_hint(cn_name) or en_name
        candidates = fuzzy_hk(en_hint, threshold=58) if en_hint else []
    elif market == 'A':
        candidates = fuzzy_a(cn_name, threshold=72)
    elif market == 'US':
        candidates = search_us(en_name or cn_name)
    else:
        return {'ticker': parent_tk, 'status': f'market_{market}',
                'company': stock_name, 'is_listed': True,
                'spinoff_name': cn_name or en_name}

    if not candidates:
        # ── LLM 兜底：模糊匹配失败时让 LLM 从公告标题直接推断 ticker ──
        sf_key = os.environ.get('SILICONFLOW_KEY', '')
        if sf_key:
            print(f"    [LLM fallback] Trying LLM ticker search for {parent_tk}...")
            llm_res = _verify_and_find(
                parent_tk, stock_name, titles, market, sf_key, _hk_names
            )
            if llm_res:
                llm_tk, llm_name, llm_price, llm_conf, llm_src = llm_res
                print(f"    [LLM] Found: {llm_tk} ({llm_name}) price={llm_price}")
                # 写入 KNOWN_SPINOFFS 日志（方便下次直接用）
                write_log(parent_tk, llm_tk, llm_name, llm_price, None,
                          float('nan'), llm_conf, llm_src)
                return {
                    'ticker': parent_tk, 'status': 'llm_found',
                    'spinoff_ticker': llm_tk, 'spinoff_name': llm_name,
                    'price_now': llm_price, 'confidence': llm_conf,
                    'source': llm_src, 'market': market,
                    'is_listed': True, 'autoMatched': True,
                }
        return {'ticker': parent_tk, 'status': 'no_ticker_match',
                'company': stock_name, 'is_listed': True,
                'spinoff_name': cn_name or en_name, 'market': market}

    best_score, best_ticker, best_name = candidates[0]
    currency = {'HK': 'HKD', 'A': 'CNY', 'US': 'USD'}.get(market, 'HKD')

    if market == 'A':
        raw = best_ticker.split('.')[0]
        p0, pnow = fetch_a_price(raw, listing_date)
    else:
        p0   = fetch_price_on_date(best_ticker, listing_date)
        pnow = fetch_price_latest(best_ticker)

    chg = round((pnow - p0) / p0 * 100, 1) if p0 and pnow and p0 > 0 else None
    status = 'matched' if best_score >= 72 else 'low_confidence'

    return {
        'ticker': parent_tk, 'company': stock_name,
        'spinoff_name': cn_name or en_name, 'spinoff_name_en': en_name,
        'matched_ticker': best_ticker, 'matched_name': best_name,
        'target_market': market, 'is_listed': True,
        'listing_date': listing_date,
        'price_at_listing': p0, 'price_now': pnow, 'change_pct': chg,
        'currency': currency, 'confidence': best_score,
        'source': 'auto', 'status': status,
    }

# ── 把结果合并写入 spinoff.json ──────────────────────────────────

# ── 美股子公司价格刷新 ────────────────────────────────────────────
# ── 美股已知分拆日期知识库（兜底 distributionDate 为空的情况）────────────
US_KNOWN_DIST_DATES = {
    'HON':  {'spinoffTicker': 'HONA', 'spinoffName': 'Honeywell Aerospace', 'date': '2026-06-29'},
    'VANI': {'spinoffTicker': 'CRGT', 'spinoffName': 'Cortigent Inc',       'date': '2025-09-01'},
}

def refresh_us_spinoff_prices(dry_run=False) -> int:
    """
    Fix 2: 刷新 spinoff_us.json 里所有 spinoffPricePerf 条目的今日价格。
    同时对有 spinoffTicker 但还没有 spinoffPricePerf 的 completed 公司补录价格。
    """
    us_path = REPO_DIR / 'spinoff_us.json'
    if not us_path.exists():
        print("  spinoff_us.json 不存在，跳过")
        return 0

    with open(us_path, encoding='utf-8') as f:
        data = json.load(f)

    written = 0
    for c in data.get('companies', []):
        parent_tk = c.get('ticker', '')
        status    = c.get('status', '')

        # ── 刷新已有 spinoffPricePerf 的今日价 ──────────────────
        for p in c.get('spinoffPricePerf', []):
            sk = p.get('spinoff', '')
            if not sk: continue
            pnow = fetch_price_latest(sk)
            if pnow is None: continue
            # 重新计算涨跌幅
            p0 = p.get('spinoffPriceAtSpin') or p.get('spinoffPriceAtListing')
            chg = round((pnow - p0) / p0 * 100, 1) if p0 and p0 > 0 else None
            old_now = p.get('spinoffPriceNow')
            p['spinoffPriceNow']    = pnow
            p['spinoffChangePct']   = chg
            p['updatedAt']          = TODAY
            # 同时刷新母公司今日价
            pnow_parent = fetch_price_latest(parent_tk)
            if pnow_parent:
                p0_parent = p.get('parentPriceAtSpin')
                chg_parent = round((pnow_parent - p0_parent) / p0_parent * 100, 1) if p0_parent and p0_parent > 0 else None
                p['parentPriceNow']    = pnow_parent
                p['parentChangePct']   = chg_parent
            if old_now != pnow:
                written += 1
                print(f"  US refresh: {parent_tk}→{sk} {old_now}→{pnow} chg={chg}%")

        # ── 补录：有 spinoffTicker 但尚无 spinoffPricePerf ──────
        # 同时从知识库兜底没有 spinoffTicker 的 known companies
        sk_field = c.get('spinoffTicker', '').strip()
        known = US_KNOWN_DIST_DATES.get(parent_tk)
        if not sk_field and known:
            sk_field = known['spinoffTicker']
            if not c.get('spinoffName'):
                c['spinoffName'] = known['spinoffName']
            c['spinoffTicker'] = sk_field
        if sk_field and sk_field.upper() != 'TBD' and not c.get('spinoffPricePerf'):
            # 找分拆日期（优先 JSON 字段，兜底知识库）
            dist_date = c.get('distributionDate', '') or c.get('recordDate', '')
            if not dist_date and known:
                dist_date = known['date']
            pnow = fetch_price_latest(sk_field)
            if pnow is None: continue
            p0 = fetch_price_on_date(sk_field, dist_date) if dist_date else None
            # 母公司
            parent_now = fetch_price_latest(parent_tk)
            parent_p0  = fetch_price_on_date(parent_tk, dist_date) if dist_date else None
            chg_spinoff = round((pnow - p0) / p0 * 100, 1) if p0 and p0 > 0 else None
            chg_parent  = round((parent_now - parent_p0) / parent_p0 * 100, 1) if parent_p0 and parent_p0 and parent_p0 > 0 else None

            new_perf = {
                'parent':            parent_tk,
                'spinoff':           sk_field,
                'spinoffDate':       dist_date,
                'parentPriceAtSpin': parent_p0,
                'parentPriceNow':    parent_now,
                'parentChangePct':   chg_parent,
                'spinoffPriceAtSpin':  p0,
                'spinoffPriceNow':     pnow,
                'spinoffChangePct':    chg_spinoff,
                'updatedAt':           TODAY,
            }
            c['spinoffPricePerf'] = [new_perf]
            written += 1
            print(f"  US new:     {parent_tk}→{sk_field} p0={p0} now={pnow} chg={chg_spinoff}%")

    if not dry_run and written > 0:
        with open(us_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  写入 spinoff_us.json: {written} 条更新")
    elif dry_run:
        print(f"  [dry-run] US spinoff: {written} 条待更新")

    return written

def merge_into_json(results: list[dict], dry_run=False) -> int:
    with open(SPINOFF_JSON, encoding='utf-8') as f:
        data = json.load(f)

    written = 0
    for r in results:
        # 接受 matched / low_confidence / llm_found 三种状态
        if r.get('status') == 'llm_found':
            # LLM 找到的结果：重新包装成 merge 可写格式
            r['matched_ticker'] = r.get('spinoff_ticker', '')
            r['spinoff_name']   = r.get('spinoff_name', '')
            r['listing_date']   = r.get('date', '')
            r['price_at_listing'] = None
            r['change_pct']     = None
            r['currency']       = {'HK': 'HKD', 'A': 'CNY', 'US': 'USD'}.get(r.get('market','HK'), 'HKD')
        elif r.get('status') not in ('matched', 'low_confidence'):
            continue
        if not r.get('matched_ticker'): continue
        if r.get('confidence', 0) < 65: continue

        parent_tk  = r['ticker']
        spinoff_tk = r['matched_ticker']

        # Fix 3: 如果上市价为 None 但有上市日期，尝试拉取首日收盘价
        price_at_listing = r.get('price_at_listing')
        listing_date     = r.get('listing_date', '')
        if price_at_listing is None and listing_date:
            p0 = fetch_price_on_date(spinoff_tk, listing_date)
            if p0:
                price_at_listing = p0
                print(f"    Backfilled listing price for {spinoff_tk}: {p0} on {listing_date}")

        # Fix 5: source 字段写入
        src = r.get('source', 'known_db')

        for c in data['companies']:
            if c.get('ticker') != parent_tk: continue

            new_pair = {
                'spinoff':               spinoff_tk,
                'spinoffName':           r.get('spinoff_name', ''),
                'spinoffDate':           listing_date,
                'spinoffPriceAtListing': price_at_listing,
                'spinoffPriceNow':       r.get('price_now'),
                'spinoffChangePct':      r.get('change_pct'),
                'currency':              r.get('currency', 'HKD'),
                'confidence':            r.get('confidence', 0),
                'autoMatched':           r.get('source') not in ('known_db',),
                'source':                src,
                'updatedAt':             TODAY,
            }
            if r.get('note'):
                new_pair['note'] = r['note']

            existing = [p for p in c.get('spinoffPricePerf', [])
                        if p.get('spinoff') != spinoff_tk]
            existing.append(new_pair)
            c['spinoffPricePerf'] = existing
            written += 1

    if not dry_run:
        with open(SPINOFF_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    return written

# ── 日志 ─────────────────────────────────────────────────────────
def write_log(results: list[dict]):
    entry = {
        'run_at': TODAY,
        'total': len(results),
        'matched': sum(1 for r in results if r.get('status') in ('matched','low_confidence')),
        'not_listed': sum(1 for r in results if r.get('status') == 'not_listed_yet'),
        'results': results,
    }
    with open(LOG_PATH, 'a', encoding='utf-8') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + '\n')

# ── 主函数 ───────────────────────────────────────────────────────
# ── 港股母公司 pricePerf 刷新 ──────────────────────────────────────────────────
def refresh_hk_parent_priceperf(dry_run=False) -> int:
    """
    对所有港股分拆公司，拉母公司自首次公告日（firstDate）以来的股价变化，
    写入 c['pricePerf'] = {priceAtAnnouncement, priceNow, changePct, firstAnnouncementDate, currency}
    """
    with open(SPINOFF_JSON, encoding='utf-8') as f:
        data = json.load(f)

    written = 0
    for c in data.get('companies', []):
        ticker = c.get('ticker', '')
        if not ticker: continue

        first_date = c.get('firstDate', '')
        if not first_date: continue

        # yfinance 港股 ticker 格式：NNNN.HK（4位，去前缀零但保留至少1位）
        if '.HK' in ticker.upper():
            code = ticker.split('.')[0].lstrip('0') or '0'
            yfk = code + '.HK'

        price_at_ann = fetch_price_on_date(yfk, first_date)
        price_now    = fetch_price_latest(yfk)

        if not price_at_ann or not price_now: continue

        chg = round((price_now - price_at_ann) / price_at_ann * 100, 1)
        old = c.get('pricePerf') or {}
        if old.get('changePct') == chg and old.get('priceNow') == price_now:
            continue  # 无变化跳过

        c['pricePerf'] = {
            'priceAtAnnouncement':  price_at_ann,
            'priceNow':             price_now,
            'changePct':            chg,
            'firstAnnouncementDate': first_date,
            'currency':             'HKD',
            'updatedAt':            TODAY,
        }
        written += 1
        print(f"  HK pricePerf: {ticker} ({yfk}) firstDate={first_date} "
              f"p0={price_at_ann} now={price_now} chg={chg:+.1f}%")

    if not dry_run and written > 0:
        with open(SPINOFF_JSON, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"  写入 spinoff.json pricePerf: {written} 条")
    elif dry_run:
        print(f"  [dry-run] HK pricePerf: {written} 条待写入")
    return written


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--dry-run', action='store_true', help='仅打印，不写入')
    parser.add_argument('--ticker', help='只处理某个母公司 ticker，如 02899.HK')
    args = parser.parse_args()

    with open(SPINOFF_JSON, encoding='utf-8') as f:
        data = json.load(f)

    companies = data['companies']
    if args.ticker:
        companies = [c for c in companies if c.get('ticker') == args.ticker]
        if not companies:
            print(f"Ticker {args.ticker} not found"); return

    print(f"\n{'='*60}")
    print(f"HK Spinoff Price Refresh  {TODAY}")
    print(f"{'='*60}")
    ensure_dbs()
    load_dbs()  # 预加载

    results = []
    for c in companies:
        ticker = c.get('ticker','')
        try:
            r = process_company(c)
            if r:
                results.append(r)
                status = r.get('status','')
                icon = {'matched':'✅','low_confidence':'⚠️','not_listed_yet':'🔜',
                        'no_ticker_match':'❌','name_not_extracted':'📝'}.get(status,'❓')
                mticker = r.get('matched_ticker','—')
                chg = r.get('change_pct')
                chg_str = f"{chg:+.1f}%" if chg is not None else "—"
                print(f"{icon} {ticker:12} → {mticker:12} | {r.get('spinoff_name','')[:14]:14} "
                      f"| conf={r.get('confidence',0):3.0f} | chg={chg_str}")
        except Exception as e:
            print(f"❗ {ticker}: {e}")
            results.append({'ticker': ticker, 'status': 'exception', 'error': str(e)})
        time.sleep(0.1)

    print(f"\n── 汇总 ──────────────────────────────────")
    from collections import Counter
    for status, n in Counter(r.get('status') for r in results).most_common():
        print(f"  {status:25}: {n}")

    if not args.dry_run:
        written = merge_into_json(results)
        print(f"\n写入 spinoff.json: {written} 条更新")
        write_log(results)
        print(f"日志追加至 {LOG_PATH}")
    else:
        print("\n[dry-run] 未写入文件")

    # Fix 2: 港股母公司 pricePerf
    print("\n── 港股母公司股价追踪 ──────────────────────────────────────")
    refresh_hk_parent_priceperf(dry_run=args.dry_run)

    # Fix 3: 刷新美股子公司价格
    print("\n── 美股子公司价格刷新 ──────────────────────────────────────")
    refresh_us_spinoff_prices(dry_run=args.dry_run)

if __name__ == '__main__':
    main()
