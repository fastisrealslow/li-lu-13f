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

import json, os, sys, time, re, urllib.request, urllib.error
from datetime import datetime, timezone, date

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
                    if price > 0:
                        result[tk] = {"c": price, "currency": "HKD"}
                        print(f"  {tk}: HK${price:.3f}")
                    else:
                        print(f"  {tk}: price=0 (no data)")
                except (ValueError, IndexError):
                    print(f"  {tk}: parse error")
        except Exception as e:
            print(f"  新浪 API 请求失败: {e}", file=sys.stderr)
        time.sleep(0.2)
    return result

# ─────────────────────────────────────────────
# Yahoo Finance 历史 K 线
# ─────────────────────────────────────────────
def yahoo_chart(symbol, from_ts, to_ts):
    try:
        import yfinance as yf
        start_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        end_dt   = datetime.fromtimestamp(to_ts,   tz=timezone.utc).strftime('%Y-%m-%d')
        # yfinance 用短杠格式（BRK-B/BRK-A），上游 13F 数据里同时存在点号（BRK.B）和斜杠（BRK/B）两种写法，都需归一化，
        # 否则斜杠会被 yfinance 内部请求拼进 URL 路径导致请求失败。
        yf_symbol = symbol.replace('.B', '-B').replace('/B', '-B').replace('.A', '-A').replace('/A', '-A') if symbol.startswith('BRK') else symbol
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
    return (int(datetime(y, start_m, 1).timestamp()),
            int(datetime(y, end_m, month_days[end_m], 23, 59, 59).timestamp()))

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

    current      = data["current"]
    holdings     = current["holdings"]
    quarter      = current["quarter"]
    prev_quarter = current.get("prevQuarter", quarter)
    hist_holdings = data.get("history", {}).get("holdings", {})

    print(f"[{investor}] Fetching prices: {len(holdings)} tickers ({quarter} ← {prev_quarter})")

    # ── 加载已有缓存 ──
    existing_quotes = {}
    existing_cb     = {}
    ex = None
    try:
        with open(prices_file) as f:
            ex = json.load(f)
            existing_quotes = ex.get("quotes", {})
            existing_cb     = ex.get("costBasis", {})
            print(f"  Loaded cache: {len(existing_quotes)} quotes, {len(existing_cb)} cost basis")
    except FileNotFoundError:
        pass

    today_str = date.today().isoformat()

    # ── Part 1: 实时报价 (Finnhub) ──
    quotes = {}
    for h in holdings:
        tk = h["ticker"]
        if tk.startswith("?") or tk.endswith(".HK"):
            quotes[tk] = {"error": True}
            print(f"  Skip {tk} (unmapped/HK)")
            continue
        # 当天缓存
        if tk in existing_quotes:
            eq = existing_quotes[tk]
            if not eq.get("error") and eq.get("t"):
                qt_date = datetime.utcfromtimestamp(eq["t"]).date().isoformat()
                if qt_date == today_str:
                    quotes[tk] = eq
                    print(f"  Quote {tk}... ${eq['c']:.2f} (cached)")
                    continue
        print(f"  Quote {tk}...", end=" ", flush=True)
        # Finnhub 标准代码用句点（BRK.A/BRK.B），13F 原始数据里部分申报人用斜杠写法（BRK/A、BRK/B），
        # 若直接把斜杠传给 URL 路径会被当成路径分隔符，导致请求错误的接口地址而失败，这里统一归一化。
        if tk in ("BRK.B", "BRK/B"):
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
            eq = existing_quotes.get(tk)
            if eq and not eq.get("error") and eq.get("c", 0) > 0:
                quotes[tk] = {**eq, "stale": True}
                print(f"✗ → 回退旧报价 ${eq['c']:.2f} (stale)")
            else:
                print("✗ → 无历史缓存可回退")
                quotes[tk] = {"error": True}
        time.sleep(1.1)

    # ── Part 2: 成本估算 ──
    cost_basis = {}
    for h in holdings:
        tk = h["ticker"]
        if tk.startswith("?") or tk.endswith(".HK"):
            continue

        # 找买入季度
        buy_q = quarter
        if h.get("prevShares", 0) > 0 and h["shares"] <= h["prevShares"]:
            prev_shares = None
            for q_key in sorted(hist_holdings.keys()):
                for qh in hist_holdings.get(q_key, []):
                    if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                        if prev_shares is None:
                            buy_q = q_key
                        elif qh["shares"] > prev_shares:
                            buy_q = q_key
                        prev_shares = qh["shares"]

        # 预先推导本轮连续持有起点（gap>4 规则），用于下面的外层缓存短路判断——
        # 必须在这里就先算好，否则外层短路会在 allTime.first 需要修正时仍然直接 continue 跳过重算
        _run_first_precheck = None
        _qk_precheck = None
        for q_key, q_h in sorted(hist_holdings.items()):
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
                if _q2n_pre(_qk_precheck[_i]) - _q2n_pre(_qk_precheck[_i - 1]) > 4:
                    _run_first_precheck = _qk_precheck[_i]

        # 近期成本缓存检查（只有 allTime 也有值且 allTime.first 与本轮连续起点一致时才跳过，
        # 避免 allTime 空时永远不重算，也避免清仓重入后 allTime.first 永远回不到新起点（历史 bug）
        if tk in existing_cb:
            r = existing_cb[tk].get("recent", {})
            a = existing_cb[tk].get("allTime") or {}
            if (r.get("source") == "yahoo" and r.get("quarter") == buy_q and a.get("avg")
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
            est = round(h["value"] / h["shares"], 2)
            if h.get("prevValue", 0) > 0 and h.get("prevShares", 0) > 0 and buy_q == prev_quarter:
                est = round(h["prevValue"] / h["prevShares"], 2)
            recent = {"buy": est, "low": est, "high": est,
                      "quarter": buy_q, "source": "13f-estimate"}
            print(f"estim=${est} (13F fallback)")

        # all-time 成本：平均成本法（AVCO）
        # 买入 → 更新持仓均价；卖出 → 均价不变；gap>4季 → 重置
        quarterly_data = []
        for q_key, q_h in sorted(hist_holdings.items()):
            for qh in q_h:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})

        all_time = None
        if quarterly_data:
            ex_a = existing_cb.get(tk, {}).get("allTime")
            q_keys = [q["quarter"] for q in quarterly_data]
            # 重新推导本轮连续持有起点（与下方正式计算循环同一个 gap>4 规则），用于缓存比对
            def _q2n(q):
                y, qn = q.split(" Q"); return int(y) * 4 + int(qn)
            _run_first = q_keys[0]
            for _i in range(1, len(q_keys)):
                if _q2n(q_keys[_i]) - _q2n(q_keys[_i - 1]) > 4:
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
                        if gap > 4:  # 清仓重置：同时重置连续持有起点
                            avco_price  = 0.0
                            avco_shares = 0
                            prev_sh     = 0
                            current_run_first = qd["quarter"]
                    if cur_sh > prev_sh:  # 买入
                        delta = cur_sh - prev_sh
                        qf, qt_ = quarter_ts(qd["quarter"])
                        c2 = yahoo_chart(tk, qf, qt_)
                        if c2 and c2["closes"]:
                            buy_price = min(c2["lows"]) * 0.7 + (sum(c2["closes"]) / len(c2["closes"])) * 0.3
                        else:
                            buy_price = qd["value"] / cur_sh
                            if buy_price > 5000:
                                buy_price /= 1000
                        # AVCO 更新：(旧均价×旧仓 + 买入价×新增量) / 新仓
                        avco_price  = (avco_price * avco_shares + buy_price * delta) / (avco_shares + delta)
                        avco_shares += delta
                        buy_q_count += 1
                        time.sleep(0.5)
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

        cost_basis[tk] = {"recent": recent, "allTime": all_time}
        time.sleep(0.3)

    # ── exitPerf：已清仓持仓估算盈亏 ──────────────────────────────────
    exit_perf = {}
    current_tks = {h["ticker"] for h in data.get("current", {}).get("holdings", [])}
    # 找在 history 里出现过、但不在当前持仓的 ticker
    exited_tks = set()
    for holdings in hist_holdings.values():
        for h in holdings:
            tk2 = h["ticker"]
            if not tk2.startswith("?") and tk2 not in current_tks:
                exited_tks.add(tk2)

    existing_ep = (ex.get("exitPerf", {}) if ex else {})

    for tk2 in exited_tks:
        # 找最后出现的季度（即清仓季度）
        qtrs_with_tk = sorted(
            [q for q, hlist in hist_holdings.items()
             if any(h["ticker"] == tk2 for h in hlist)]
        )
        if not qtrs_with_tk:
            continue
        exit_q = qtrs_with_tk[-1]

        # 缓存检查：exit_q 没变就不重算
        ex_ep = existing_ep.get(tk2, {})
        if ex_ep.get("exitQuarter") == exit_q and ex_ep.get("exitPrice") and ex_ep.get("entryPrice"):
            exit_perf[tk2] = ex_ep
            continue

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
                            if q2n(q2) - q2n(prev_q2) > 4:
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
                            time.sleep(0.3)
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
        time.sleep(0.3)

    # ── 写出 ──
    out = {"updated": datetime.utcnow().isoformat() + "Z",
           "quotes": quotes, "costBasis": cost_basis, "exitPerf": exit_perf}
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
        if not tk.endswith(".HK"):
            continue
        buy_q = quarter
        prev_shares = None
        for q_key in sorted(hist_holdings.keys()):
            for qh in hist_holdings[q_key]:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    if prev_shares is None:
                        buy_q = q_key
                    prev_shares = qh["shares"]

        # 预先推导本轮连续持有起点（gap>4 规则），防止外层短路在 allTime.first 需要修正时仍直接 continue 跳过重算（与美股分支同样的历史 bug）
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
                if _q2n_pre_hk(_qt_precheck_hk[_i]) - _q2n_pre_hk(_qt_precheck_hk[_i - 1]) > 4:
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
                if gap > 4:
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

    if cfg["market"] == "HK":
        fetch_hk(investor, cfg)
    else:
        fetch_us(investor, cfg)

if __name__ == "__main__":
    main()
