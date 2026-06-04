"""Fetch stock prices & estimated buy-in costs for 13F holdings.
Depends only on Python stdlib.
- Live quotes: Finnhub (requires API key)
- Historical cost basis: Yahoo Finance (free, no auth)

Usage: python3 fetch_prices.py [--key FINNHUB_KEY]
If --key is omitted, reads FINNHUB_KEY from env.
"""
import json, os, sys, time, random, urllib.request, urllib.error
from datetime import datetime

# ── Finnhub API key ──
def get_key():
    for i, a in enumerate(sys.argv):
        if a == "--key" and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    key = os.environ.get("FINNHUB_KEY", "")
    if not key:
        print("ERROR: No Finnhub API key. Pass --key or set FINNHUB_KEY env.", file=sys.stderr)
        sys.exit(1)
    return key

API_KEY = get_key()

def finnhub(path):
    """Call Finnhub API."""
    sep = "&" if "?" in path else "?"
    url = f"https://finnhub.io/api/v1{path}{sep}token={API_KEY}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "13F-Tracker/1.0"})
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [Finnhub error] {e}", file=sys.stderr)
        return None


def should_skip_recent(ticker, buy_q, existing_cb):
    """Skip Yahoo request if we already have cached yahoo data for this quarter."""
    if not existing_cb or ticker not in existing_cb:
        return False
    r = existing_cb[ticker].get("recent", {})
    return r.get("source") == "yahoo" and r.get("quarter") == buy_q

def should_skip_alltime(ticker, existing_cb, quarters_list):
    """Skip allTime Yahoo requests if we have complete cached data."""
    if not existing_cb or ticker not in existing_cb:
        return False
    a = existing_cb[ticker].get("allTime")
    if not a or not quarters_list:
        return False
    return a.get("first") == quarters_list[0] and a.get("last") == quarters_list[-1] and a.get("quarters", 0) >= len(quarters_list)

def yahoo_chart(symbol, from_ts, to_ts):
    """Fetch K-line data from Yahoo Finance using yfinance library."""
    try:
        import yfinance as yf
        from datetime import datetime, timezone
        start_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        end_dt = datetime.fromtimestamp(to_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        ticker = yf.Ticker(symbol)
        hist = ticker.history(start=start_dt, end=end_dt)
        if hist is None or len(hist) == 0:
            return None
        closes = hist['Close'].dropna().tolist()
        highs = hist['High'].dropna().tolist()
        lows = hist['Low'].dropna().tolist()
        if not closes:
            return None
        return {"closes": closes, "highs": highs, "lows": lows}
    except Exception as e:
        print(f"  [yfinance error] {e}", file=__import__('sys').stderr)
        return None

def quarter_ts(q_str):
    """Parse '2026 Q1' → (from_unix, to_unix)."""
    parts = q_str.split(" Q")
    y, qn = int(parts[0]), int(parts[1])
    start_m = (qn - 1) * 3 + 1
    end_m = qn * 3
    month_days = {1:31, 2:29 if y%4==0 and (y%100!=0 or y%400==0) else 28, 3:31,
                  4:30, 5:31, 6:30, 7:31, 8:31, 9:30, 10:31, 11:30, 12:31}
    from_ts = int(datetime(y, start_m, 1).timestamp())
    to_ts = int(datetime(y, end_m, month_days[end_m], 23, 59, 59).timestamp())
    return from_ts, to_ts

def main():
    try:
        with open("duan.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: duan.json not found. Run fetch_13f_duan.py first.", file=sys.stderr)
        sys.exit(1)

    current = data["current"]
    holdings = current["holdings"]
    quarter = current["quarter"]
    prev_quarter = current.get("prevQuarter", quarter)

    print(f"Fetching prices for {len(holdings)} tickers ({quarter} ← {prev_quarter})")

    # ── Part 1: Live quotes (Finnhub) ──
    quotes = {}
    for h in holdings:
        tk = h["ticker"]
        if tk.startswith("?") or tk.endswith(".HK"):
            print(f"  Skip {tk} (unmapped or HK stock)")
            quotes[tk] = {"error": True}
            continue
        print(f"  Quote {tk}...", end=" ", flush=True)
        q = finnhub(f"/quote?symbol={tk}")
        if q and q.get("c", 0) > 0:
            quotes[tk] = {"c": round(q["c"], 2), "h": round(q["h"], 2),
                          "l": round(q["l"], 2), "o": round(q["o"], 2),
                          "pc": round(q["pc"], 2), "t": q["t"]}
            print(f"${q['c']:.2f}")
        else:
            print("✗")
            quotes[tk] = {"error": True}
        time.sleep(0.2)

    # ── Part 2: Estimated buy-in costs ──
    # Recent: Yahoo Finance (or 13F fallback), skewed toward buy-side (lower end)
    # All-time: average of 13F quarter-end prices across entire holding history
    # Load existing prices for incremental caching
    existing_cb = {}
    try:
        with open("prices_duan.json") as _f:
            existing_prices = json.load(_f)
            existing_cb = existing_prices.get("costBasis", {})
            print(f"  Loaded {len(existing_cb)} cached cost basis (incremental)")
    except FileNotFoundError:
        pass
    cost_basis = {}

    # Pre-load history holdings for all-time computation
    hist_holdings = data.get("history", {}).get("holdings", {})

    for h in holdings:
        tk = h["ticker"]
        # Smart buy quarter: new→current, find last buy quarter for existing, fallback→first quarter
        buy_q = quarter
        if h.get("prevShares", 0) > 0 and h["shares"] <= h["prevShares"]:
            # No new shares this quarter - find last quarter where shares went up
            prev_qs = sorted(hist_holdings.keys())
            prev_shares = None
            for q in prev_qs:
                for qh in hist_holdings.get(q, []):
                    if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                        if prev_shares is None:
                            buy_q = q  # first appearance
                        elif qh["shares"] > prev_shares:
                            buy_q = q  # shares increased = bought
                        prev_shares = qh["shares"]
        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  Cost basis {tk} ({buy_q})...", end=" ", flush=True)

        # --- Recent cost (skewed toward low end = buy-side estimate) ---
        recent = None
        c = yahoo_chart(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            high = max(c["highs"])
            # Skew toward low end: 70% weight on low, 30% on avg
            buy_est = round(low * 0.7 + avg * 0.3, 2)
            recent = {"buy": buy_est, "low": round(low,2), "high": round(high,2), "quarter": buy_q, "source": "yahoo"}
            print(f"buy≈${buy_est} [{low:.2f}-{high:.2f}]")
        else:
            est_price = round(h["value"] / h["shares"], 2)
            if h.get("prevValue", 0) > 0 and h.get("prevShares", 0) > 0:
                prev_price = round(h["prevValue"] / h["prevShares"], 2)
                if buy_q == prev_quarter:
                    est_price = prev_price
            recent = {"buy": est_price, "low": est_price, "high": est_price, "quarter": buy_q, "source": "13f-estimate"}
            print(f"estim=${est_price} (13F fallback)")

        # --- All-time cost: weighted avg (price per quarter × shares) / total shares ---
        # Same buy-side formula as recent cost, applied to EVERY quarter the holding was held
        all_time = None
        quarterly_data = []
        for q_key, q_holdings in sorted(hist_holdings.items()):
            for qh in q_holdings:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})
        if quarterly_data:
            # Incremental: skip allTime if we have complete cached data
            if should_skip_alltime(tk, existing_cb, [q["quarter"] for q in quarterly_data]):
                all_time = existing_cb[tk]["allTime"]
                print(f"| all-time wavg=${existing_cb[tk]['allTime']['avg']} ({existing_cb[tk]['allTime']['quarters']}q, cached)")
            else:
                total_weighted_cost = 0.0
                total_shares_sum = 0
                valid_q = 0
                for qd in quarterly_data:
                    q_from, q_to = quarter_ts(qd["quarter"])
                    c = yahoo_chart(tk, q_from, q_to)
                    if c and c["closes"]:
                        avg = sum(c["closes"]) / len(c["closes"])
                        low = min(c["lows"])
                        q_price = low * 0.7 + avg * 0.3
                    else:
                        q_price = qd["value"] / qd["shares"]  # fallback: 13F quarter-end
                    total_weighted_cost += q_price * qd["shares"]
                    total_shares_sum += qd["shares"]
                    valid_q += 1
                    time.sleep(0.5)
                all_avg = round(total_weighted_cost / total_shares_sum, 2)
                all_time = {
                    "avg": all_avg,
                    "quarters": valid_q,
                    "first": quarterly_data[0]["quarter"],
                    "last": quarterly_data[-1]["quarter"],
                }
                print(f"| all-time wavg=${all_avg} ({valid_q}q, {total_shares_sum} total shares)")

        cost_basis[tk] = {"recent": recent, "allTime": all_time}
        time.sleep(0.3)

    # ── Write prices.json ──
    prices = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "quotes": quotes,
        "costBasis": cost_basis,
    }
    with open("prices_duan.json", "w") as f:
        json.dump(prices, f, indent=2)
    print(f"\n✅ prices.json written ({len(quotes)} quotes, {len(cost_basis)} cost basis)")

if __name__ == "__main__":
    main()