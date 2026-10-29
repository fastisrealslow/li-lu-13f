#!/usr/bin/env python3
"""通用股价抓取脚本 — 替代所有 fetch_prices_*.py

用法:
  python3 fetch_prices_all.py --investor lilu
  python3 fetch_prices_all.py --investor duan
  python3 fetch_prices_all.py --investor pabrai
  python3 fetch_prices_all.py --investor tepper
  python3 fetch_prices_all.py --investor buffett
  python3 fetch_prices_all.py --investor akre
  python3 fetch_prices_all.py --investor greenberg
  python3 fetch_prices_all.py --investor webb
  python3 fetch_prices_all.py --investor klarman
  python3 fetch_prices_all.py --investor ackman
  python3 fetch_prices_all.py --investor abrams
  python3 fetch_prices_all.py --investor berkowitz
  python3 fetch_prices_all.py --investor hawkins

每个投资者的 data_file / prices_file / market 配置来自仓库根目录的 investors.json（单一权威来源）。
"""

import json, os, sys, time, re, hashlib, math, urllib.request, urllib.error
from functools import lru_cache
from zoneinfo import ZoneInfo
from datetime import datetime, timezone, date
from holdings_diff import share_adjustment, consolidate_holdings, same_security
from security_identity import project as project_identities, project_prices


def comparable_price_history(history, current_quarter, market_quotes=None):
    """Use today's split basis for cost estimates; keep filed snapshots unchanged."""
    result = {}
    for quarter, holdings in history.items():
        result[quarter] = []
        for h in consolidate_holdings(holdings):
            adjustment = share_adjustment(h, quarter, current_quarter)
            factor=adjustment['factor'] if adjustment else 1
            if market_quotes is not None and not h.get('putCall') and h.get('shareType','SH')=='SH':
                from holdings_diff import VERIFIED_SPLITS
                actions={a['date']:a['factor'] for a in VERIFIED_SPLITS if (h.get('cusip')==a['cusip'] or h['ticker']==a['ticker'])}
                for action in market_quotes.get(h['ticker'],{}).get('shareActions',[]):
                    from batch_market_data import is_share_split
                    if not is_share_split(action,h):continue
                    if action['date'] in actions and abs(actions[action['date']]-action['factor'])>1e-9:raise ValueError('Reported split disagrees with verified issuer action')
                    # Issuer distribution dates and exchange ex-dates can differ
                    # by a weekend. They describe one event, not two splits.
                    duplicate=next((when for when,ratio in actions.items() if abs(ratio-action['factor'])<1e-9 and abs((date.fromisoformat(when)-date.fromisoformat(action['date'])).days)<=10),None)
                    if duplicate:actions.pop(duplicate)
                    actions[action['date']]=action['factor']
                end=datetime.fromtimestamp(quarter_ts(quarter)[1]-1,timezone.utc).date().isoformat()
                factor=1
                for when,ratio in actions.items():
                    if end<when<=date.today().isoformat():factor*=ratio
            result[quarter].append({**h, "shares": h["shares"] * factor} if factor!=1 else h)
    return result


def cost_history_fingerprint(history, excluded_quarters=None):
    # Ignore descriptive metadata: only a change to the calculation inputs
    # should invalidate estimates, including corrections to older quarters.
    first=next((q for q,rows in sorted(history.items()) if any(r.get('shares',0)>0 for r in rows)),None)
    inputs=[(q,sorted((str(r.get('cusip') or r.get('ticker','')),r.get('shares',0),r.get('value',0),r.get('putCall',''),r.get('shareType','SH')) for r in rows)) for q,rows in sorted(history.items()) if first is None or q>=first]
    if excluded_quarters:inputs={'holdings':inputs,'excludedValueQuarters':sorted(excluded_quarters)}
    return hashlib.sha256(json.dumps(inputs).encode()).hexdigest()

# ─────────────────────────────────────────────
# 投资者配置表 — 从 investors.json 动态构建，见 _load_investor_config()
# ─────────────────────────────────────────────
def _load_investor_config():
    """从 investors.json 读取投资者列表（单一权威来源）。
    新增投资者只需编辑仓库根目录的 investors.json，无需在本文件手工加条目。
    注意：与 fetch_13f_all.py 不同，这里要包含 webb（他也需要抓取港股价格）。"""
    base = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base, 'investors.json'), encoding='utf-8') as f:
            investors = json.load(f)['investors']
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: investors.json 读取失败（{e}）", file=sys.stderr)
        sys.exit(1)
    return {
        inv["id"]: {
            "data": inv["dataFile"],
            "prices": inv["pricesFile"],
            "market": inv["market"],
            "hk": inv.get("hkFile"),
            "collectMarketActions": True,
        }
        for inv in investors
    }


INVESTOR_CONFIG = _load_investor_config()

# ─────────────────────────────────────────────
# CLI 参数解析
# ─────────────────────────────────────────────
def parse_args():
    investor = None
    finnhub_key = None
    for i, a in enumerate(sys.argv[1:], 1):
        if a == "--investor" and i < len(sys.argv):
            investor = sys.argv[i + 1]
        elif a == "--key" and i < len(sys.argv):
            finnhub_key = sys.argv[i + 1]
    if not investor:
        print("Usage: python3 fetch_prices_all.py --investor <name>", file=sys.stderr)
        print(f"Available: {', '.join(INVESTOR_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)
    if investor not in INVESTOR_CONFIG:
        print(f"ERROR: Unknown investor '{investor}'. Available: {', '.join(INVESTOR_CONFIG.keys())}", file=sys.stderr)
        sys.exit(1)
    return investor, finnhub_key

# ─────────────────────────────────────────────
# Finnhub (US 股票报价)
# ─────────────────────────────────────────────
_API_KEY = None

def get_finnhub_key(override=None):
    global _API_KEY
    if _API_KEY:
        return _API_KEY
    if override:
        _API_KEY = override
        return _API_KEY
    key = os.environ.get("FINNHUB_KEY", "")
    if not key:
        print("ERROR: No Finnhub API key. Pass --key or set FINNHUB_KEY env.", file=sys.stderr)
        sys.exit(1)
    _API_KEY = key
    return _API_KEY

# HTTP 状态码中，5xx 通常是服务端临时性故障（网关超时、服务重启等），
# 短暂退避重试很可能就会成功；4xx（除429限速外）多为客户端/请求本身的问题，重试无意义。
_RETRYABLE_HTTP_CODES = {500, 502, 503, 504}

def finnhub(path, _retries=3):
    # Public Yahoo quotes and historical-price fallbacks also work without a key.
    if not _API_KEY and not os.environ.get('FINNHUB_KEY'):
        return None
    key = get_finnhub_key()
    sep = "&" if "?" in path else "?"
    url = f"https://finnhub.io/api/v1{path}{sep}token={key}"
    for attempt in range(_retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "13F-Tracker/1.0"})
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 30 * (attempt + 1)
                print(f"  [Finnhub 429] 限速，等待 {wait}s 后重试...", file=sys.stderr)
                time.sleep(wait)
            elif e.code in _RETRYABLE_HTTP_CODES and attempt < _retries - 1:
                wait = 2 * (attempt + 1)
                print(f"  [Finnhub HTTP {e.code}] 临时性错误，等待 {wait}s 后重试 ({attempt + 1}/{_retries})...", file=sys.stderr)
                time.sleep(wait)
            else:
                print(f"  [Finnhub HTTP {e.code}] {e}", file=sys.stderr)
                return None
        except Exception as e:
            if attempt < _retries - 1:
                wait = 2 * (attempt + 1)
                print(f"  [Finnhub error] {e}，等待 {wait}s 后重试 ({attempt + 1}/{_retries})...", file=sys.stderr)
                time.sleep(wait)
                continue
            print(f"  [Finnhub error] {e}", file=sys.stderr)
            return None
    print(f"  [Finnhub] {_retries} 次重试均失败", file=sys.stderr)
    return None

# ─────────────────────────────────────────────
# 港股报价 (新浪财经，适用于 Webb)
# ─────────────────────────────────────────────
def get_hk_prices(tickers):
    def to_sina(tk):
        code = tk.replace('.HK', '')
        return 'hk' + code.zfill(5)

    sina_map = {to_sina(tk): tk for tk in tickers}
    result = {tk: {"error": True} for tk in tickers}

    syms = list(sina_map.keys())
    for i in range(0, len(syms), 40):
        batch = syms[i:i+40]
        url = 'https://hq.sinajs.cn/list=' + ','.join(batch)
        try:
            req = urllib.request.Request(url, headers={
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            })
            with urllib.request.urlopen(req, timeout=12) as resp:
                body = resp.read().decode('gbk', errors='replace')
            for line in body.splitlines():
                m = re.match(r'var hq_str_(hk\d+)="([^"]*)', line)
                if not m: continue
                sym, fields = m.group(1), m.group(2).split(',')
                tk = sina_map.get(sym)
                if not tk: continue
                try:
                    price = round(float(fields[6]), 3)
                    quote_time = datetime.strptime(fields[17]+' '+fields[18], '%Y/%m/%d %H:%M').replace(tzinfo=ZoneInfo('Asia/Hong_Kong'))
                    if price > 0 and quote_time.timestamp() <= time.time()+300:
                        result[tk] = {"c": price, "currency": "HKD", "t": int(quote_time.timestamp()),
                                      "source": "sina_hk", "sourceURL": 'https://finance.sina.com.cn/stock/hkstock/quotes/'+tk.replace('.HK','').zfill(5)+'.html'}
                        print(f"  {tk}: HK${price:.3f}")
                    else:
                        print(f"  {tk}: price=0 (no data)")
                except (ValueError, IndexError):
                    print(f"  {tk}: parse error")
        except Exception as e:
            print(f"  新浪 API 请求失败: {e}", file=sys.stderr)
        time.sleep(0.2)
    return result


def disclosed_hk_tickers(payload):
    """Quote only identified HK-listed classes; never guesses or A-share interests."""
    from hk_disclosures import official_url
    tickers = set()
    for h in payload.get('holdings', []):
        if not re.fullmatch(r'\d{5}\.HK', h.get('ticker', '')):
            continue
        for r in h.get('verified_disclosures', []):
            share_class = r.get('share_class', '').casefold().replace('-', ' ')
            if (r.get('verification') == 'hkex_form' and not r.get('superseded_by')
                    and r.get('position') == 'long' and r.get('shares', 0) > 0
                    and official_url(r.get('form_url') or r.get('source_url', ''))
                    and share_class in ('ordinary shares', 'h shares')):
                tickers.add(h['ticker'])
    return sorted(tickers)


def supplement_hk_quotes(cfg, quotes, cached=None):
    """Separate HK reference quotes from 13F cost calculations and USD totals."""
    if not cfg.get('hk') or not os.path.exists(cfg['hk']):
        return quotes
    with open(cfg['hk'], encoding='utf-8') as f:
        tickers = disclosed_hk_tickers(json.load(f))
    fetched = get_hk_prices(tickers) if tickers else {}
    for ticker in tickers:
        q = fetched.get(ticker, {'error': True})
        old = (cached or {}).get(ticker, {})
        if q.get('error') and old.get('currency') == 'HKD' and old.get('t') and old.get('c', 0) > 0:
            q = {**old, 'stale': True}
        quotes[ticker] = q
    return quotes

# ─────────────────────────────────────────────
# Yahoo Finance 历史 K 线
# ─────────────────────────────────────────────
@lru_cache(maxsize=8192)
def yahoo_chart(symbol, from_ts, to_ts):
    from batch_market_data import window
    covered,cached=window(symbol,from_ts,to_ts)
    if covered:return cached
    try:
        import yfinance as yf
        start_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        end_dt   = datetime.fromtimestamp(to_ts,   tz=timezone.utc).strftime('%Y-%m-%d')
        # yfinance 用短杠格式（BRK-B/BRK-A），上游 13F 数据里同时存在点号（BRK.B）和斜杠（BRK/B）两种写法，都需归一化，
        # 否则斜杠会被 yfinance 内部请求拼进 URL 路径导致请求失败。
        yf_symbol = symbol.replace('.B', '-B').replace('/B', '-B').replace('.A', '-A').replace('/A', '-A')
        t = yf.Ticker(yf_symbol)
        hist = t.history(start=start_dt, end=end_dt)
        if hist is None or len(hist) == 0:
            return None
        closes = hist['Close'].dropna().tolist()
        highs  = hist['High'].dropna().tolist()
        lows   = hist['Low'].dropna().tolist()
        return {"closes": closes, "highs": highs, "lows": lows} if closes else None
    except Exception as e:
        print(f"  [yfinance error] {e}", file=sys.stderr)
        return None

# ─────────────────────────────────────────────
# 季度时间戳工具
# ─────────────────────────────────────────────
def quarter_ts(q_str):
    parts = q_str.split(" Q")
    y, qn = int(parts[0]), int(parts[1])
    start_m = (qn - 1) * 3 + 1
    end_m   = qn * 3
    month_days = {1:31, 2:29 if y%4==0 and (y%100!=0 or y%400==0) else 28, 3:31,
                  4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    return (int(datetime(y, start_m, 1, tzinfo=timezone.utc).timestamp()),
            int(datetime(y, end_m, month_days[end_m], 23, 59, 59, tzinfo=timezone.utc).timestamp()))

# ─────────────────────────────────────────────
# 核心：US 市场股票处理
# ─────────────────────────────────────────────
def fetch_us(investor, cfg):
    data_file   = cfg["data"]
    prices_file = cfg["prices"]

    try:
        with open(data_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {data_file} not found.", file=sys.stderr)
        sys.exit(1)

    data = project_identities(data)
    current      = data["current"]
    holdings     = current["holdings"]
    quarter      = current["quarter"]
    prev_quarter = current.get("prevQuarter", quarter)
    raw_history = data.get("history", {}).get("holdings", {})
    excluded_values=set(data.get("history", {}).get("excludedValueQuarters", []))
    hist_holdings = comparable_price_history(raw_history, quarter)
    split_tickers = {h["ticker"] for q, hs in raw_history.items() for h in hs
                     if share_adjustment(h, q, quarter)}

    print(f"[{investor}] Fetching prices: {len(holdings)} tickers ({quarter} ← {prev_quarter})")

    # ── 加载已有缓存 ──
    existing_quotes = {}
    existing_cb     = {}
    ex = None
    try:
        with open(prices_file) as f:
            ex = project_prices(data, json.load(f))
            existing_quotes = ex.get("quotes", {})
            existing_cb     = ex.get("costBasis", {})
            print(f"  Loaded cache: {len(existing_quotes)} quotes, {len(existing_cb)} cost basis")
    except FileNotFoundError:
        pass

    hist_holdings=comparable_price_history(raw_history,quarter,existing_quotes if cfg.get('collectMarketActions') else None)

    for ticker in split_tickers:
        if existing_cb.get(ticker, {}).get("splitAdjustedThrough") != quarter:
            existing_cb.pop(ticker, None)

    today_str = date.today().isoformat()

    # A broad manager must not make one quote request per quarter or exceed
    # the updater timeout. Fetch one dated series per security with four workers.
    bulk_quotes={}
    if len(holdings)>100 or cfg.get('collectMarketActions'):
        from batch_market_data import prefetch
        from security_lifecycle import event_for
        tickers=[h['ticker'] for h in holdings if not event_for(h) and h.get('shareType','SH')=='SH' and not h['ticker'].startswith('?') and not h['ticker'].endswith('.HK')]
        start=quarter_ts(min(hist_holdings) if hist_holdings else quarter)[0]
        source_fingerprint=cost_history_fingerprint(hist_holdings,excluded_values)
        since=datetime.fromtimestamp(start,timezone.utc).date().isoformat()
        needs_history=tickers if not ex or ex.get('sourceHistoryFingerprint')!=source_fingerprint else [tk for tk in tickers if (existing_cb.get(tk,{}).get('averageUnavailable')!='corporate_action' and (existing_cb.get(tk,{}).get('recent',{}).get('source')!='yahoo' or not (existing_cb.get(tk,{}).get('allTime') or {}).get('avg'))) or existing_quotes.get(tk,{}).get('shareActionsSince','9999')>since]
        bulk_quotes=prefetch(needs_history,start)
        from batch_market_data import prefetch_quotes
        bulk_quotes.update(prefetch_quotes([tk for tk in tickers if tk not in bulk_quotes]))
        from batch_market_data import merge_actions
        changed=[tk for tk in tickers if tk not in needs_history and not bulk_quotes[tk].get('error') and merge_actions(existing_quotes.get(tk,{}),bulk_quotes[tk]).get('shareActions',[])!=existing_quotes.get(tk,{}).get('shareActions',[])]
        if changed:bulk_quotes.update(prefetch(changed,start))
    # ── Part 1: 实时报价 (Finnhub) ──
    quotes = {}
    for h in holdings:
        tk = h["ticker"]
        if h.get('shareType', 'SH') != 'SH':
            continue  # principal amounts are not shares of the quoted stock
        from security_lifecycle import event_for
        event = event_for(h)
        if event:
            quotes[tk] = {'status':'ceased_trading', 'event':event}
            continue
        if tk.startswith("?") or tk.endswith(".HK"):
            quotes[tk] = {"error": True}
            print(f"  Skip {tk} (unmapped/HK)")
            continue
        if tk in bulk_quotes:
            from quote_coverage import valid_quote, warrant_reference
            fresh=bulk_quotes[tk];old=existing_quotes.get(tk,{})
            from batch_market_data import merge_actions
            quotes[tk]=merge_actions(old,fresh) if valid_quote(fresh) else {**old,'stale':True} if valid_quote(old) else warrant_reference(h,current) or {'error':True}
            continue
        # 当天缓存
        if tk in existing_quotes:
            eq = existing_quotes[tk]
            if not eq.get("error") and eq.get("t"):
                qt_date = datetime.utcfromtimestamp(eq["t"]).date().isoformat()
                fetched_at=eq.get('fetchedAt')
                try:recent_fetch=fetched_at and 0<datetime.now(timezone.utc).timestamp()-datetime.fromisoformat(fetched_at.replace('Z','+00:00')).timestamp()<6*3600
                except (ValueError,TypeError):recent_fetch=False
                recent_trade=0<datetime.now(timezone.utc).timestamp()-eq['t']<3*86400
                if not eq.get('stale') and (qt_date == today_str or recent_fetch and recent_trade):
                    quotes[tk] = eq
                    print(f"  Quote {tk}... ${eq['c']:.2f} (cached)")
                    continue
        print(f"  Quote {tk}...", end=" ", flush=True)
        # Finnhub 标准代码用句点（BRK.A/BRK.B），13F 原始数据里部分申报人用斜杠写法（BRK/A、BRK/B），
        # 若直接把斜杠传给 URL 路径会被当成路径分隔符，导致请求错误的接口地址而失败，这里统一归一化。
        if tk.endswith(("/B", ".B")):
            sym = tk.replace("/B", "%2EB").replace(".B", "%2EB")
        elif tk.endswith(("/A", ".A")):
            sym = tk.replace("/A", "%2EA").replace(".A", "%2EA")
        elif tk in ("BRK.B", "BRK/B"):
            sym = "BRK%2EB"
        elif tk in ("BRK.A", "BRK/A"):
            sym = "BRK%2EA"
        else:
            sym = tk
        q = finnhub(f"/quote?symbol={sym}")
        if (not q or q.get("c", 0) == 0) and sym != tk:
            q = finnhub(f"/quote?symbol={tk}")
        if q and q.get("c", 0) > 0:
            quotes[tk] = {"c": round(q["c"],2), "h": round(q["h"],2),
                          "l": round(q["l"],2), "o": round(q["o"],2),
                          "pc": round(q["pc"],2), "t": q["t"]}
            print(f"${q['c']:.2f}")
        else:
            # 本次拉取失败（如 Finnhub 偶发502等）——回退到上一次成功缓存的报价，
            # 而不是直接覆盖为 error，避免前端“参考股价”因一次接口抖动就彻底消失。
            from quote_coverage import yahoo_quote, valid_quote
            fallback = yahoo_quote(tk)
            eq = existing_quotes.get(tk)
            if valid_quote(fallback):
                quotes[tk] = fallback
                print(f"Yahoo ${fallback['c']:.2f}")
            elif eq and not eq.get("error") and eq.get("c", 0) > 0:
                quotes[tk] = {**eq, "stale": True}
                print(f"✗ → 回退旧报价 ${eq['c']:.2f} (stale)")
            else:
                print("✗ → 无历史缓存可回退")
                from quote_coverage import warrant_reference
                quotes[tk] = warrant_reference(h,current) or {"error": True}
        time.sleep(1.1)

    if cfg.get('collectMarketActions'):
        hist_holdings=comparable_price_history(raw_history,quarter,quotes)
        if bulk_quotes:source_fingerprint=cost_history_fingerprint(hist_holdings,excluded_values)
        from holdings_diff import attach_previous
        from batch_market_data import is_share_split
        import copy
        before=copy.deepcopy(current);before_meta=copy.deepcopy(data.get('meta',{}))
        action_meta=[a for a in data.get('meta',{}).get('shareActions',[]) if a.get('sourceKind')!='market_share_split']
        for h in holdings:
            if h.get('putCall') or h.get('shareType','SH')!='SH':continue
            q=quotes.get(h['ticker'],{})
            for e in q.get('shareActions',[]):
                if not is_share_split(e,h):continue
                if any(a.get('cusip')==h.get('cusip') and abs(a['factor']-e['factor'])<1e-9 and abs((date.fromisoformat(a['date'])-date.fromisoformat(e['date'])).days)<=10 for a in action_meta):continue
                action_meta.append(dict(ticker=h['ticker'],cusip=h.get('cusip'),date=e['date'],factor=e['factor'],quarter=e['date'][:4]+' Q'+str((int(e['date'][5:7])-1)//3+1),source=q['sourceURL'],sourceKind='market_share_split'))
        if action_meta:data.setdefault('meta',{})['shareActions']=action_meta
        previous=current.get('previousHoldings',raw_history.get(prev_quarter))
        if isinstance(previous,list):
            old_rows={(h.get('cusip'),(h.get('putCall') or '').upper(),h.get('shareType','SH')):h for h in previous}
            for h in holdings:
                old=old_rows.get((h.get('cusip'),(h.get('putCall') or '').upper(),h.get('shareType','SH')))
                if not old or h.get('putCall') or h.get('shareType','SH')!='SH':continue
                q=quotes.get(h['ticker'],{})
                events=[e for e in q.get('shareActions',[]) if prev_quarter<e['date'][:4]+' Q'+str((int(e['date'][5:7])-1)//3+1)<=quarter and is_share_split(e,h)]
                if events:
                    factor=math.prod(e['factor'] for e in events)
                    h['shareAdjustment']={'factor':factor,'date':events[-1]['date'],'source':q['sourceURL'],'reportedShares':old['shares'],'sourceKind':'market_share_split','fromQuarter':prev_quarter,'toQuarter':quarter}
            attach_previous(holdings,previous,previous_quarter=prev_quarter,current_quarter=quarter)
            if current!=before or data.get('meta',{})!=before_meta:
                from fetch_13f_all import save_data
                save_data(data_file,data)
    security_key=lambda row:(row.get('cusip'),(row.get('putCall') or '').upper(),(row.get('shareType') or 'SH').upper())
    cost_index={};unidentified={}
    for q,rows in hist_holdings.items():
        for row in rows:
            if row.get('cusip'):cost_index.setdefault(security_key(row),{}).setdefault(q,[]).append(row)
            else:unidentified.setdefault(q,[]).append(row)
    # ── Part 2: 成本估算 ──
    cost_basis = {}
    for h in holdings:
        if h.get('putCall') or h.get('shareType', 'SH') != 'SH':
            continue
        tk = h["ticker"]
        from security_lifecycle import event_for
        if event_for(h):
            if tk in existing_cb:cost_basis[tk]=existing_cb[tk]
            continue
        boundary = data.get('meta',{}).get('instrumentHistoryFrom','') if tk in data.get('meta',{}).get('instrumentHistoryTickers',[]) else ''
        transition=data.get('meta',{}).get('reportingTransition',{})
        from reporting_scope import same_manager_history
        scope_boundary=transition.get('fromQuarter','') if transition.get('comparisonScopeChanged') and not same_manager_history(data,h) else ''
        boundary=max(boundary,scope_boundary,data.get('meta',{}).get('costHistoryFrom',''))
        matched=cost_index.get(security_key(h),{})
        security_history = {q: [{**row,'ticker':tk} for row in (matched.get(q,[])+unidentified.get(q,[]) if h.get('cusip') else rows) if same_security(h,row)] for q,rows in hist_holdings.items() if boundary <= q <= quarter}
        if data.get("current", {}).get("valueQuality"):
            continue
        if tk.startswith("?") or tk.endswith(".HK"):
            continue
        history_fingerprint=cost_history_fingerprint(security_history, [q for q in excluded_values if any(r.get('shares',0)>0 for r in security_history.get(q,[]))])
        if cfg.get('collectMarketActions'):history_fingerprint=hashlib.sha256((history_fingerprint+json.dumps(quotes.get(tk,{}).get('shareActions',[]),sort_keys=True)).encode()).hexdigest()
        if existing_cb.get(tk,{}).get('historyFingerprint') != history_fingerprint:
            existing_cb.pop(tk,None)

        if existing_cb.get(tk,{}).get('averageUnavailable')=='corporate_action':
            cost_basis[tk]=existing_cb[tk];continue

        # 找买入季度
        buy_q = quarter
        prev_shares, previous_index = 0, None
        for q_key in sorted(security_history):
            if q_key > quarter: continue
            if tk in data.get('meta', {}).get('instrumentHistoryTickers', []) and q_key < data['meta']['instrumentHistoryFrom']: continue
            year,number=q_key.split(' Q'); index=int(year)*4+int(number)
            if previous_index is not None and index-previous_index>1:prev_shares=0
            shares=sum(row.get('shares',0) for row in security_history[q_key])
            if shares>prev_shares:buy_q=q_key
            prev_shares,previous_index=shares,index

        # 预先推导本轮连续持有起点（gap>1 规则），用于下面的外层缓存短路判断——
        # 必须在这里就先算好，否则外层短路会在 allTime.first 需要修正时仍然直接 continue 跳过重算
        _run_first_precheck = None
        _qk_precheck = None
        for q_key, q_h in sorted(security_history.items()):
            if tk in data.get('meta', {}).get('instrumentHistoryTickers', []) and q_key < data['meta']['instrumentHistoryFrom']: continue
            for qh in q_h:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    if _qk_precheck is None:
                        _qk_precheck = []
                    _qk_precheck.append(q_key)
        if _qk_precheck:
            def _q2n_pre(q):
                y, qn = q.split(" Q"); return int(y) * 4 + int(qn)
            _run_first_precheck = _qk_precheck[0]
            for _i in range(1, len(_qk_precheck)):
                if _q2n_pre(_qk_precheck[_i]) - _q2n_pre(_qk_precheck[_i - 1]) > 1:
                    _run_first_precheck = _qk_precheck[_i]

        pending_value_quarters=[q for q in excluded_values if (_run_first_precheck or '') <= q <= quarter and any(r.get('shares',0)>0 for r in security_history.get(q,[]))]

        # 近期成本缓存检查（只有 allTime 也有值且 allTime.first 与本轮连续起点一致时才跳过，
        # 避免 allTime 空时永远不重算，也避免清仓重入后 allTime.first 永远回不到新起点（历史 bug）
        if tk in existing_cb:
            r = existing_cb[tk].get("recent", {})
            a = existing_cb[tk].get("allTime") or {}
            if (not pending_value_quarters and r.get("source") == "yahoo" and r.get("quarter") == buy_q and a.get("avg")
                    and (_run_first_precheck is None or a.get("first") == _run_first_precheck)):
                cost_basis[tk] = existing_cb[tk]
                print(f"  Cost {tk} ({buy_q})... (cached)")
                continue

        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  Cost {tk} ({buy_q})...", end=" ", flush=True)

        c = yahoo_chart(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            high = max(c["highs"])
            buy_est = round(low * 0.7 + avg * 0.3, 2)
            recent = {"buy": buy_est, "low": round(low,2), "high": round(high,2),
                      "quarter": buy_q, "source": "yahoo"}
            print(f"buy≈${buy_est} [{low:.2f}-{high:.2f}]")
        else:
            proxy = next((row for row in security_history.get(buy_q,[]) if row.get('shares',0)>0),None) if buy_q not in excluded_values else None
            est = round(proxy['value'] / proxy['shares'],2) if proxy else None
            recent = {"buy": est, "low": est, "high": est,
                      "quarter": buy_q, "source": "13f-estimate"}
            if est is None:recent['error']=True
            print(f"estim=${est} (13F fallback)")

        # all-time 成本：平均成本法（AVCO）
        # 买入 → 更新持仓均价；卖出 → 均价不变；gap>1季 → 重置
        quarterly_data = []
        for q_key, q_h in sorted(security_history.items()):
            if tk in data.get('meta', {}).get('instrumentHistoryTickers', []) and q_key < data['meta']['instrumentHistoryFrom']: continue
            for qh in q_h:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})

        all_time = None
        if quarterly_data and not pending_value_quarters:
            ex_a = existing_cb.get(tk, {}).get("allTime")
            q_keys = [q["quarter"] for q in quarterly_data]
            # 重新推导本轮连续持有起点（与下方正式计算循环同一个 gap>1 规则），用于缓存比对
            def _q2n(q):
                y, qn = q.split(" Q"); return int(y) * 4 + int(qn)
            _run_first = q_keys[0]
            for _i in range(1, len(q_keys)):
                if _q2n(q_keys[_i]) - _q2n(q_keys[_i - 1]) > 1:
                    _run_first = q_keys[_i]
            # 缓存检查：first(本轮起点)/last 季度一致且 allTime 有值，直接复用
            if (ex_a and ex_a.get("avg") and ex_a.get("first") == _run_first
                    and ex_a.get("last") == q_keys[-1] and ex_a.get("method") == "avco"):
                all_time = ex_a
                print(f"| all-time avco=${ex_a['avg']} ({ex_a['buy_quarters']}q buy, cached)")
            else:
                avco_price  = 0.0   # 当前持仓均价
                avco_shares = 0     # 当前持仓数量
                prev_sh = 0
                prev_q  = None
                buy_q_count = 0
                current_run_first = q_keys[0]  # 本轮（未被清仓中断的）连续持有起点
                for qd in quarterly_data:
                    cur_sh = qd["shares"]
                    if prev_q is not None:
                        def q2n(q):
                            y, qn = q.split(" Q"); return int(y)*4 + int(qn)
                        gap = q2n(qd["quarter"]) - q2n(prev_q)
                        if gap > 1:  # 清仓重置：同时重置连续持有起点
                            avco_price  = 0.0
                            avco_shares = 0
                            prev_sh     = 0
                            buy_q_count = 0
                            current_run_first = qd["quarter"]
                    if cur_sh > prev_sh:  # 买入
                        delta = cur_sh - prev_sh
                        qf, qt_ = quarter_ts(qd["quarter"])
                        c2 = yahoo_chart(tk, qf, qt_)
                        if c2 and c2["closes"]:
                            buy_price = min(c2["lows"]) * 0.7 + (sum(c2["closes"]) / len(c2["closes"])) * 0.3
                        else:
                            buy_price = qd["value"] / cur_sh
                        # AVCO 更新：(旧均价×旧仓 + 买入价×新增量) / 新仓
                        avco_price  = (avco_price * avco_shares + buy_price * delta) / (avco_shares + delta)
                        avco_shares += delta
                        buy_q_count += 1
                        time.sleep(0 if bulk_quotes else 0.5)
                    elif cur_sh < prev_sh:  # 卖出：均价不变，仓位减少
                        avco_shares = cur_sh
                    prev_sh = cur_sh
                    prev_q  = qd["quarter"]

                if avco_shares > 0 and avco_price > 0:
                    all_avg  = round(avco_price, 2)
                    all_time = {"avg": all_avg, "buy_quarters": buy_q_count,
                                "first": current_run_first, "last": q_keys[-1],
                                "method": "avco"}
                    print(f"| all-time avco=${all_avg} ({buy_q_count}q buy, run-first={current_run_first})")

        if scope_boundary and buy_q==scope_boundary:recent['kind']='scope_initial'
        cost_basis[tk] = {"recent": recent, "allTime": all_time, "historyFingerprint":history_fingerprint}
        if cfg.get('collectMarketActions'):
            from batch_market_data import is_share_split
            events=quotes.get(tk,{}).get('shareActions',[])
            uncertain=[e for e in events if not is_share_split(e,h)]
            if events:cost_basis[tk]['splitAdjustedThrough']=quarter
            if uncertain:
                last=max(e['date'] for e in uncertain);last_q=last[:4]+' Q'+str((int(last[5:7])-1)//3+1)
                if all_time and all_time['first']<=last_q:
                    cost_basis[tk]['allTime']=None;cost_basis[tk]['averageUnavailable']='corporate_action'
                if buy_q<=last_q and h.get('shares',0)>0:
                    after=math.prod(e['factor'] for e in events if e['date']>current.get('periodEnd','9999'))
                    reference=round(h['value']/h['shares']/after,2)
                    cost_basis[tk]['recent']={'buy':reference,'low':reference,'high':reference,'quarter':quarter,'source':'13f-estimate','kind':'adjusted_quarter_reference','basisAdjustment':after}
        if pending_value_quarters:cost_basis[tk]["averageUnavailable"]="units"
        time.sleep(0 if bulk_quotes else 0.3)

    # Publish the complete current quote/cost snapshot before optional old exits.
    # An interrupted historical extension must not discard fresh market data.
    supplement_hk_quotes(cfg, quotes, existing_quotes)
    for ticker in split_tickers:
        if ticker in cost_basis:
            cost_basis[ticker]["splitAdjustedThrough"] = quarter
    with open(prices_file, 'w') as output:
        mixed_tickers={h['ticker'] for rows in hist_holdings.values() for h in rows if h.get('putCall') or h.get('shareType','SH')!='SH'}
        json.dump(dict(updated=datetime.utcnow().isoformat()+'Z', securityIdentityVersion=1, quotes=quotes,
                       costBasis=cost_basis, exitPerf={k:v for k,v in (ex or {}).get('exitPerf',{}).items() if k not in mixed_tickers}), output, indent=2)

    # ── exitPerf：已清仓持仓估算盈亏 ──────────────────────────────────
    exit_perf = {}
    current_tks = {h["ticker"] for h in data.get("current", {}).get("holdings", [])}
    # 找在 history 里出现过、但不在当前持仓的 ticker
    exited_tks = set()
    exit_quarters = {}
    for history_quarter, holdings in hist_holdings.items():
        for h in holdings:
            tk2 = h["ticker"]
            if not tk2.startswith("?") and tk2 not in current_tks:
                exited_tks.add(tk2)
                exit_quarters.setdefault(tk2,set()).add(history_quarter)

    existing_ep = (ex.get("exitPerf", {}) if ex else {})

    # An issuer's historical options or principal cannot establish stock profits.
    mixed = {h['ticker'] for rows in hist_holdings.values() for h in rows
             if h.get('putCall') or h.get('shareType', 'SH') != 'SH'}
    exited_tks -= mixed
    exit_attempts = 0
    for tk2 in sorted(exited_tks):
        # 找最后出现的季度（即清仓季度）
        qtrs_with_tk = sorted(exit_quarters[tk2])
        if not qtrs_with_tk:
            continue
        exit_q = qtrs_with_tk[-1]

        # 缓存检查：exit_q 没变就不重算
        ex_ep = existing_ep.get(tk2, {})
        if ex_ep.get("exitQuarter") == exit_q and ex_ep.get("exitPrice") and ex_ep.get("entryPrice"):
            exit_perf[tk2] = ex_ep
            continue

        # Extend old estimates in bounded batches while keeping verified caches.
        if exit_attempts >= cfg.get('exitRequestLimit',20):
            continue
        exit_attempts += 1
        # 清仓季度均价作为卖出价估算
        qf, qt_ = quarter_ts(exit_q)
        c2 = yahoo_chart(tk2, qf, qt_)
        if not c2 or not c2["closes"]:
            # 用 13F value/shares 兜底
            for h in hist_holdings.get(exit_q, []):
                if h["ticker"] == tk2 and h.get("shares", 0) > 0:
                    exit_price = round(h["value"] / h["shares"], 2)
                    break
            else:
                continue
        else:
            avg2  = sum(c2["closes"]) / len(c2["closes"])
            high2 = max(c2.get("highs", c2["closes"]))
            exit_price = round(high2 * 0.7 + avg2 * 0.3, 2)

        # 单季度持仓（建仓=清仓同季）：无论哪种方式都不可信，跳过
        if qtrs_with_tk[0] == exit_q:
            continue
        # 建仓成本：用 allTime.avg（如果已算过）
        entry_price = (cost_basis.get(tk2, {}).get("allTime") or {}).get("avg")
        if not entry_price:
            # exitPerf fallback：AVCO 重算建仓成本
            avco_p2  = 0.0
            avco_s2  = 0
            prev_sh2 = 0
            prev_q2  = None
            for q2 in qtrs_with_tk:
                for h in hist_holdings.get(q2, []):
                    if h["ticker"] == tk2 and h.get("shares", 0) > 0:
                        sh2 = h["shares"]
                        if prev_q2:
                            def q2n(q): y, qn = q.split(" Q"); return int(y) * 4 + int(qn)
                            if q2n(q2) - q2n(prev_q2) > 1:
                                avco_p2 = 0.0; avco_s2 = 0; prev_sh2 = 0
                        if sh2 > prev_sh2:
                            delta2 = sh2 - prev_sh2
                            qf2, qt2_ = quarter_ts(q2)
                            c_buy = yahoo_chart(tk2, qf2, qt2_)
                            if c_buy and c_buy["closes"]:
                                avg_b = sum(c_buy["closes"]) / len(c_buy["closes"])
                                low_b = min(c_buy.get("lows", c_buy["closes"]))
                                p_buy = low_b * 0.7 + avg_b * 0.3
                            else:
                                p_buy = h["value"] / sh2 if sh2 else 0
                            avco_p2 = (avco_p2 * avco_s2 + p_buy * delta2) / (avco_s2 + delta2)
                            avco_s2 += delta2
                            time.sleep(0 if bulk_quotes else 0.3)
                        elif sh2 < prev_sh2:
                            avco_s2 = sh2  # 卖出：均价不变
                        prev_sh2 = sh2
                        prev_q2  = q2
            if avco_s2 <= 0 or avco_p2 <= 0:
                continue
            entry_price = round(avco_p2, 2)

        if not entry_price:
            continue

        chg = round((exit_price - entry_price) / entry_price * 100, 1)
        # 找最早建仓季度（清仓重置后的第一个 buy quarter）
        entry_q = qtrs_with_tk[0]
        exit_perf[tk2] = {
            "entryQuarter": entry_q,
            "entryPrice":   entry_price,
            "exitQuarter":  exit_q,
            "exitPrice":    exit_price,
            "changePct":    chg,
        }
        print(f"  exitPerf {tk2}: entry~${entry_price} ({entry_q}) → exit~${exit_price} ({exit_q}) {chg:+.1f}%")
        time.sleep(0 if bulk_quotes else 0.3)

    # ── 写出 ──
    supplement_hk_quotes(cfg, quotes, existing_quotes)
    for ticker in split_tickers:
        if ticker in cost_basis:
            cost_basis[ticker]["splitAdjustedThrough"] = quarter
    out = {"updated": datetime.utcnow().isoformat() + "Z",
           "quotes": quotes, "costBasis": cost_basis, "exitPerf": exit_perf, "securityIdentityVersion": 1}
    if bulk_quotes:out['sourceHistoryFingerprint']=source_fingerprint
    with open(prices_file, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n✅ {prices_file} written ({len(quotes)} quotes, {len(cost_basis)} cost basis)")

# ─────────────────────────────────────────────
# 核心：HK 市场 (Webb)
# ─────────────────────────────────────────────
def fetch_hk(investor, cfg):
    data_file   = cfg["data"]
    prices_file = cfg["prices"]

    try:
        with open(data_file) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {data_file} not found.", file=sys.stderr)
        sys.exit(1)

    current       = data["current"]
    holdings      = current["holdings"]
    quarter       = current["quarter"]
    hist_holdings = data.get("history", {}).get("holdings", {})

    tickers = [h["ticker"] for h in holdings if h["ticker"].endswith(".HK")]
    print(f"[{investor}] Fetching HK prices ({quarter}) — {len(tickers)} tickers")

    existing = {}
    try:
        with open(prices_file) as f:
            existing = json.load(f)
    except FileNotFoundError:
        pass
    existing_cb = existing.get("costBasis", {})

    # 实时报价
    print(f"\n[1/2] Live quotes ({len(tickers)} HK tickers)...")
    quotes = get_hk_prices(tickers)

    # 成本估算
    print(f"\n[2/2] Cost basis...")
    cost_basis = {}
    for h in holdings:
        tk = h["ticker"]
        if not tk.endswith(".HK") or data.get("meta", {}).get("snapshotType"):
            continue
        buy_q = quarter
        prev_shares = None
        for q_key in sorted(hist_holdings.keys()):
            for qh in hist_holdings[q_key]:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    if prev_shares is None:
                        buy_q = q_key
                    prev_shares = qh["shares"]

        # 预先推导本轮连续持有起点（gap>1 规则），防止外层短路在 allTime.first 需要修正时仍直接 continue 跳过重算（与美股分支同样的历史 bug）
        _qt_precheck_hk = []
        for q_key in sorted(hist_holdings.keys()):
            for qh in hist_holdings[q_key]:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    _qt_precheck_hk.append(q_key)
        _run_first_hk_precheck = None
        if _qt_precheck_hk:
            def _q2n_pre_hk(q):
                y, qn = q.split(" Q"); return int(y) * 4 + int(qn)
            _run_first_hk_precheck = _qt_precheck_hk[0]
            for _i in range(1, len(_qt_precheck_hk)):
                if _q2n_pre_hk(_qt_precheck_hk[_i]) - _q2n_pre_hk(_qt_precheck_hk[_i - 1]) > 1:
                    _run_first_hk_precheck = _qt_precheck_hk[_i]

        if tk in existing_cb:
            ec = existing_cb[tk]
            _ec_at = ec.get("allTime") or {}
            if (ec.get("recent", {}).get("quarter") == buy_q
                    and (_run_first_hk_precheck is None or _ec_at.get("first") == _run_first_hk_precheck)):
                print(f"  {tk} ({buy_q}) — cached")
                cost_basis[tk] = ec
                continue

        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  {tk} ({buy_q})...", end=" ", flush=True)
        c = yahoo_chart(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            buy_est = round(low * 0.7 + avg * 0.3, 3)
            recent = {"buy": buy_est, "low": round(low,3),
                      "high": round(max(c["highs"]),3),
                      "quarter": buy_q, "source": "yfinance", "currency": "HKD"}
            print(f"HK${buy_est:.3f}")
        else:
            est = round(h["value"] / h["shares"], 3) if h["shares"] > 0 else 0
            recent = {"buy": est, "low": est, "high": est,
                      "quarter": buy_q, "source": "13f-estimate", "currency": "HKD"}
            print(f"HK${est:.3f} (13F fallback)")

        # allTime — 按买入季度加权（港股同样逻辑）
        all_time = None
        qt_data = []
        for q_key in sorted(hist_holdings.keys()):
            for qh in hist_holdings[q_key]:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    qt_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})
        buy_qtrs_hk = []
        prev_sh_hk = 0
        prev_q_hk = None
        current_run_first_hk = qt_data[0]["quarter"] if qt_data else None
        for qd in qt_data:
            if prev_q_hk is not None:
                def q2n(q):
                    y, qn = q.split(" Q"); return int(y)*4 + int(qn)
                gap = q2n(qd["quarter"]) - q2n(prev_q_hk)
                if gap > 1:
                    buy_qtrs_hk = []
                    prev_sh_hk = 0
                    current_run_first_hk = qd["quarter"]
            if qd["shares"] > prev_sh_hk:
                buy_qtrs_hk.append({**qd, "delta": qd["shares"] - prev_sh_hk})
            prev_sh_hk = qd["shares"]
            prev_q_hk = qd["quarter"]

        if buy_qtrs_hk:
            ex_a = existing_cb.get(tk, {}).get("allTime") or {}
            q_keys_hk = [q["quarter"] for q in qt_data]
            if (ex_a.get("avg") and ex_a.get("first") == current_run_first_hk
                    and ex_a.get("last") == q_keys_hk[-1]
                    and ex_a.get("quarters", 0) >= len(buy_qtrs_hk)):
                all_time = ex_a
                print(f"  {tk} all-time wavg=HK${ex_a['avg']} (cached)")
            else:
                tc, ts_, vq = 0.0, 0, 0
                for qd in buy_qtrs_hk:
                    qf, qt_ = quarter_ts(qd["quarter"])
                    c2 = yahoo_chart(tk, qf, qt_)
                    if c2 and c2["closes"]:
                        qp = min(c2["lows"]) * 0.7 + (sum(c2["closes"]) / len(c2["closes"])) * 0.3
                    else:
                        qp = qd["value"] / qd["shares"] if qd["shares"] else 0
                    tc += qp * qd["delta"]
                    ts_ += qd["delta"]
                    vq += 1
                    time.sleep(0.5)
                if ts_ > 0:
                    all_avg = round(tc / ts_, 3)
                    all_time = {"avg": all_avg, "quarters": vq,
                                "first": current_run_first_hk,
                                "last":  qt_data[-1]["quarter"],
                                "currency": "HKD"}
                    print(f"  {tk} all-time wavg=HK${all_avg} ({vq}q, run-first={current_run_first_hk})")

        cost_basis[tk] = {"recent": recent, "allTime": all_time}
        time.sleep(1)

    supplement_hk_quotes(cfg, quotes, existing.get('quotes', {}))
    out = {"quarter": quarter,
           "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
           "currency": "HKD", "quotes": quotes, "costBasis": cost_basis}
    with open(prices_file, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    ok  = sum(1 for v in quotes.values() if not v.get("error"))
    err = sum(1 for v in quotes.values() if v.get("error"))
    print(f"\nDone: {ok} quotes OK, {err} failed. costBasis: {len(cost_basis)} tickers")

# ─────────────────────────────────────────────
# 入口
# ─────────────────────────────────────────────
def main():
    investor, finnhub_key = parse_args()
    if finnhub_key:
        get_finnhub_key(finnhub_key)

    cfg = INVESTOR_CONFIG[investor]
    # A long source audit may finish after a symbol-map checkpoint. Reapply
    # verified cached identities before reading any price/cost inputs.
    from resolve_unmapped_tickers import backfill_data_files,load_resolved_map
    from fetch_13f_all import CUSIP_TICKER_MAP
    backfill_data_files([cfg['data']],{**load_resolved_map(),**CUSIP_TICKER_MAP})

    if '--hk-only' in sys.argv:
        with open(cfg['prices'], encoding='utf-8') as f:
            existing = json.load(f)
        existing['quotes'] = supplement_hk_quotes(cfg, dict(existing.get('quotes', {})), existing.get('quotes', {}))
        existing['hkQuotesUpdatedAt'] = datetime.now(timezone.utc).isoformat()
        with open(cfg['prices'], 'w', encoding='utf-8') as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
            f.write('\n')
        return

    if cfg["market"] == "HK":
        fetch_hk(investor, cfg)
    else:
        fetch_us(investor, cfg)

if __name__ == "__main__":
    main()
