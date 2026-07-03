"""Fetch stock prices for David Webb's HK holdings.
- Live quotes: 新浪财经港股 API（批量查询，无限速）
- Cost basis: yfinance 历史数据（失败时 fallback 到 13F value/shares 估算）
Usage: python3 fetch_prices_webb.py
"""
import json, os, sys, time, re
from datetime import datetime, timezone
from urllib.request import Request, urlopen

DATA_PATH = "webb.json"
OUT_PATH  = "prices_webb.json"

def get_hk_prices(tickers):
    """批量查询港股实时价格（新浪财经 API）。一次请求所有 ticker，无限速。"""
    # 构建新浪格式：01234.HK → hk01234
    def to_sina(tk):
        code = tk.replace('.HK', '')
        return 'hk' + code.zfill(5)

    sina_map = {to_sina(tk): tk for tk in tickers}  # sina_sym -> original ticker
    result = {tk: {"error": True} for tk in tickers}

    BATCH = 40
    syms = list(sina_map.keys())
    for i in range(0, len(syms), BATCH):
        batch = syms[i:i+BATCH]
        url = 'https://hq.sinajs.cn/list=' + ','.join(batch)
        try:
            req = Request(url, headers={
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            })
            with urlopen(req, timeout=12) as resp:
                body = resp.read().decode('gbk', errors='replace')
            for line in body.splitlines():
                m = re.match(r'var hq_str_(hk\d+)="([^"]*)', line)
                if not m: continue
                sym, fields = m.group(1), m.group(2).split(',')
                tk = sina_map.get(sym)
                if not tk: continue
                try:
                    price = round(float(fields[6]), 3)  # 字段[6] = 当前价
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

def quarter_ts(q_str):
    parts = q_str.split(" Q")
    y, qn = int(parts[0]), int(parts[1])
    start_m = (qn - 1) * 3 + 1
    end_m = qn * 3
    month_days = {1:31,2:29 if y%4==0 and (y%100!=0 or y%400==0) else 28,3:31,
                  4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    from_ts = int(datetime(y, start_m, 1).timestamp())
    to_ts   = int(datetime(y, end_m, month_days[end_m], 23, 59, 59).timestamp())
    return from_ts, to_ts

def get_hk_hist(ticker, from_ts, to_ts):
    """Fetch HK stock historical prices via yfinance."""
    try:
        import yfinance as yf
        from datetime import datetime, timezone
        start_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        end_dt   = datetime.fromtimestamp(to_ts,   tz=timezone.utc).strftime('%Y-%m-%d')
        t = yf.Ticker(ticker)
        hist = t.history(start=start_dt, end=end_dt)
        if hist is None or len(hist) == 0:
            return None
        closes = hist['Close'].dropna().tolist()
        highs  = hist['High'].dropna().tolist()
        lows   = hist['Low'].dropna().tolist()
        if not closes:
            return None
        return {"closes": closes, "highs": highs, "lows": lows}
    except Exception as e:
        print(f"  [yfinance hist error] {e}", file=sys.stderr)
        return None

def main():
    try:
        with open(DATA_PATH) as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"ERROR: {DATA_PATH} not found.", file=sys.stderr)
        sys.exit(1)

    current   = data["current"]
    holdings  = current["holdings"]
    quarter   = current["quarter"]
    hist_holdings = data.get("history", {}).get("holdings", {})

    tickers = [h["ticker"] for h in holdings if h["ticker"].endswith(".HK")]
    print(f"Fetching HK Prices for David Webb ({quarter}) — {len(tickers)} tickers")

    # Load existing prices
    existing = {}
    try:
        with open(OUT_PATH) as f:
            existing = json.load(f)
    except FileNotFoundError:
        pass

    existing_cb = existing.get("costBasis", {})

    # ── Live quotes via yfinance ──
    print(f"\n[1/2] Live quotes ({len(tickers)} HK tickers)...")
    quotes = get_hk_prices(tickers)

    # ── Cost basis from value/shares (HKD, already correct after ×10 fix) ──
    print(f"\n[2/2] Cost basis (from 13F value/shares)...")
    cost_basis = {}

    for h in holdings:
        tk = h["ticker"]
        if not tk.endswith(".HK"):
            continue

        # Find earliest quarter this ticker appeared
        buy_q = quarter
        prev_shares = None
        for q_key in sorted(hist_holdings.keys()):
            for qh in hist_holdings[q_key]:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    if prev_shares is None:
                        buy_q = q_key
                    prev_shares = qh["shares"]

        # Check cache
        if tk in existing_cb:
            ec = existing_cb[tk]
            if ec.get("recent", {}).get("quarter") == buy_q:
                print(f"  {tk} ({buy_q}) — cached")
                cost_basis[tk] = ec
                continue

        # Try yfinance historical for buy quarter
        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  {tk} ({buy_q})...", end=" ", flush=True)

        c = get_hk_hist(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            buy_est = round(low * 0.7 + avg * 0.3, 3)
            recent = {"buy": buy_est, "low": round(low,3), "high": round(max(c["highs"]),3),
                      "quarter": buy_q, "source": "yfinance", "currency": "HKD"}
            print(f"HK${buy_est:.3f}")
        else:
            # Fallback: value/shares (already in HKD after ×10 fix)
            est = round(h["value"] / h["shares"], 3) if h["shares"] > 0 else 0
            recent = {"buy": est, "low": est, "high": est,
                      "quarter": buy_q, "source": "13f-estimate", "currency": "HKD"}
            print(f"HK${est:.3f} (13F fallback)")

        cost_basis[tk] = {"recent": recent, "allTime": None}
        time.sleep(1)

    # ── Write output ──
    out = {
        "quarter": quarter,
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "currency": "HKD",
        "quotes": quotes,
        "costBasis": cost_basis,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    ok  = sum(1 for v in quotes.values() if not v.get("error"))
    err = sum(1 for v in quotes.values() if v.get("error"))
    print(f"\nDone: {ok} quotes OK, {err} failed. costBasis: {len(cost_basis)} tickers")

if __name__ == "__main__":
    main()
