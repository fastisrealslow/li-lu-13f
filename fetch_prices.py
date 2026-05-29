"""Fetch stock prices & estimated buy-in costs for 13F holdings.
Depends only on Python stdlib.
- Live quotes: Finnhub (requires API key)
- Historical cost basis: Yahoo Finance (free, no auth)

Usage: python3 fetch_prices.py [--key FINNHUB_KEY]
If --key is omitted, reads FINNHUB_KEY from env.
"""
import json, os, sys, time, urllib.request, urllib.error
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
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"  [Finnhub error] {e}", file=sys.stderr)
        return None

def yahoo_chart(symbol, from_ts, to_ts):
    """Fetch daily OHLC from Yahoo Finance. Returns {opens, highs, lows, closes} or None."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={from_ts}&period2={to_ts}&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]
        # Filter out null values
        closes = [c for c in quote.get("close", []) if c is not None]
        highs = [h for h in quote.get("high", []) if h is not None]
        lows = [l for l in quote.get("low", []) if l is not None]
        if not closes:
            return None
        return {
            "closes": closes,
            "highs": highs,
            "lows": lows,
        }
    except Exception as e:
        print(f"  [Yahoo error] {e}", file=sys.stderr)
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
        with open("data.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: data.json not found. Run fetch_13f.py first.", file=sys.stderr)
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
        time.sleep(0.12)

    # ── Part 2: Estimated buy-in costs ──
    # Recent: Yahoo Finance (or 13F fallback), skewed toward buy-side (lower end)
    # All-time: average of 13F quarter-end prices across entire holding history
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

        # --- All-time cost (median of quarterly 13F prices, filtering outliers) ---
        all_time = None
        quarterly_prices = []
        for q_key, q_holdings in sorted(hist_holdings.items()):
            for qh in q_holdings:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    price = qh["value"] / qh["shares"]
                    quarterly_prices.append({"quarter": q_key, "price": round(price, 2), "shares": qh["shares"]})
        if quarterly_prices:
            # Filter outliers: price below 10% of max probably has unit issue
            prices_only = [p["price"] for p in quarterly_prices]
            max_p = max(prices_only)
            valid = [p for p in quarterly_prices if p["price"] >= max_p * 0.1]
            if not valid:
                valid = quarterly_prices  # fallback
            prices_v = [p["price"] for p in valid]
            prices_v.sort()
            mid = len(prices_v) // 2
            if len(prices_v) % 2 == 0:
                all_avg = round((prices_v[mid-1] + prices_v[mid]) / 2, 2)
            else:
                all_avg = prices_v[mid]
            all_low = min(prices_v)
            all_high = max(prices_v)
            all_time = {
                "avg": all_avg, "low": all_low, "high": all_high,
                "quarters": len(valid),
                "first": valid[0]["quarter"],
                "last": valid[-1]["quarter"],
            }
            print(f"| all-time med=${all_avg} ({len(valid)}/{len(quarterly_prices)}q)")

        cost_basis[tk] = {"recent": recent, "allTime": all_time}
        time.sleep(0.15)

    # ── Write prices.json ──
    prices = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "quotes": quotes,
        "costBasis": cost_basis,
    }
    with open("prices.json", "w") as f:
        json.dump(prices, f, indent=2)
    print(f"\n✅ prices.json written ({len(quotes)} quotes, {len(cost_basis)} cost basis)")

if __name__ == "__main__":
    main()