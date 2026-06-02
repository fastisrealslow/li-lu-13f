"""Fetch stock prices & estimated buy-in costs for Guy Spier (Aquamarine Capital) 13F holdings.
Depends only on Python stdlib.

Usage: python3 fetch_prices_spier.py [--key FINNHUB_KEY]
"""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime

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
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={from_ts}&period2={to_ts}&interval=1d"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        result = data["chart"]["result"][0]
        quote = result["indicators"]["quote"][0]
        closes = [c for c in quote.get("close", []) if c is not None]
        highs = [h for h in quote.get("high", []) if h is not None]
        lows = [l for l in quote.get("low", []) if l is not None]
        if not closes:
            return None
        return {"closes": closes, "highs": highs, "lows": lows}
    except Exception as e:
        print(f"  [Yahoo error] {e}", file=sys.stderr)
        return None

def quarter_ts(q_str):
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
        with open("spier.json") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("ERROR: spier.json not found. Run fetch_13f_spier.py first.", file=sys.stderr)
        sys.exit(1)

    current = data["current"]
    holdings = current["holdings"]
    quarter = current["quarter"]
    prev_quarter = current.get("prevQuarter", quarter)

    print(f"Fetching Prices for Spier: {len(holdings)} tickers ({quarter} ← {prev_quarter})")

    quotes = {}
    for h in holdings:
        tk = h["ticker"]
        if tk.startswith("?") or tk.endswith(".HK"):
            print(f"  Skip {tk} (HK or unmapped)")
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
        time.sleep(0.12)

    cost_basis = {}
    hist_holdings = data.get("history", {}).get("holdings", {})

    for h in holdings:
        tk = h["ticker"]
        if tk.startswith("?") or tk.endswith(".HK"):
            cost_basis[tk] = {"recent": {"buy": 0, "low": 0, "high": 0, "quarter": quarter, "source": "unavailable"}, "allTime": None}
            continue

        buy_q = quarter
        if h.get("prevShares", 0) > 0 and h["shares"] <= h["prevShares"]:
            prev_qs = sorted(hist_holdings.keys())
            prev_shares = None
            for q in prev_qs:
                for qh in hist_holdings.get(q, []):
                    if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                        if prev_shares is None:
                            buy_q = q
                        elif qh["shares"] > prev_shares:
                            buy_q = q
                        prev_shares = qh["shares"]
        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  Cost basis {tk} ({buy_q})...", end=" ", flush=True)

        recent = None
        c = yahoo_chart(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            high = max(c["highs"])
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

        all_time = None
        quarterly_data = []
        for q_key, q_holdings in sorted(hist_holdings.items()):
            for qh in q_holdings:
                if qh["ticker"] == tk and qh.get("shares", 0) > 0:
                    quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})
        if quarterly_data:
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
                    q_price = qd["value"] / qd["shares"]
                total_weighted_cost += q_price * qd["shares"]
                total_shares_sum += qd["shares"]
                valid_q += 1
                time.sleep(0.05)
            all_avg = round(total_weighted_cost / total_shares_sum, 2)
            all_time = {
                "avg": all_avg,
                "quarters": valid_q,
                "first": quarterly_data[0]["quarter"],
                "last": quarterly_data[-1]["quarter"],
            }
            print(f"| all-time wavg=${all_avg} ({valid_q}q, {total_shares_sum} total shares)")

        cost_basis[tk] = {"recent": recent, "allTime": all_time}
        time.sleep(0.15)

    prices = {
        "updated": datetime.utcnow().isoformat() + "Z",
        "quotes": quotes,
        "costBasis": cost_basis,
    }
    with open("prices_spier.json", "w") as f:
        json.dump(prices, f, indent=2)
    print(f"\n✅ prices_spier.json written ({len(quotes)} quotes, {len(cost_basis)} cost basis)")

if __name__ == "__main__":
    main()
