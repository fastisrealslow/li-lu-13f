import random
#!/usr/bin/env python3
"""Fetch Pabrai (Dalal Street) stock prices & estimated buy-in costs.
Depends only on Python stdlib.

Usage: python3 fetch_pabrai_prices.py
"""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
KEY = os.environ.get("FINNHUB_KEY", "")
if not KEY:
    print("ERROR: No Finnhub API key. Set FINNHUB_KEY env.", file=sys.stderr)
    sys.exit(1)
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "identity",
    "Referer": "https://finance.yahoo.com/",
}
def finnhub_quote(symbol):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={KEY}"
    req = urllib.request.Request(url, headers={"User-Agent": "13F-Tracker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
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
    a = existing_cb[ticker].get("allTime")
    if not a or not quarters_list:
    return a.get("first") == quarters_list[0] and a.get("last") == quarters_list[-1] and a.get("quarters", 0) >= len(quarters_list)
def yahoo_chart(symbol, from_ts, to_ts, _retries=[0]):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={from_ts}&period2={to_ts}&interval=1d"
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers=YAHOO_HEADERS)
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = json.loads(resp.read().decode())
            result = data["chart"]["result"][0]
            quote = result["indicators"]["quote"][0]
            closes = [c for c in quote.get("close", []) if c is not None]
            highs = [h for h in quote.get("high", []) if h is not None]
            lows = [l for l in quote.get("low", []) if l is not None]
            if not closes:
                return None
            return {"closes": closes, "highs": highs, "lows": lows}
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                wait = min(8 * (3 ** attempt) + random.randint(2, 8), 90)
                print(f"  [Yahoo 429] retry in {wait}s...", file=__import__('sys').stderr)
                time.sleep(wait)
                continue
            print(f"  [Yahoo error] HTTP {e.code}", file=__import__('sys').stderr)
            return None
        except Exception as e:
            print(f"  [Yahoo error] {e}", file=__import__('sys').stderr)
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
    with open("pabrai.json") as f:
        d = json.load(f)
    current = d["current"]
    holdings = current["holdings"]
    quarter = current["quarter"]
    prev_quarter = current.get("prevQuarter", quarter)
    hist_holdings = d.get("history", {}).get("holdings", {})
    print(f"Fetching Pabrai Prices: {len(holdings)} tickers ({quarter})")
    # Fetch Finnhub quotes
    quotes = {}
    for h in holdings:
        tk = h["ticker"]
        print(f"  Quote {tk}...", end=" ", flush=True)
        q = finnhub_quote(tk)
        if q and q.get("c", 0) > 0:
            quotes[tk] = {"c": round(q["c"], 2), "h": round(q.get("h",0),2),
                          "l": round(q.get("l",0),2), "o": round(q.get("o",0),2),
                          "pc": round(q.get("pc",0),2), "t": q.get("t",0)}
            print(f"${q['c']:.2f}")
        else:
            print("")
            quotes[tk] = {"error": True}
        time.sleep(0.2)
    # Calculate cost basis with Yahoo K-line
    # Load existing prices for incremental caching
    existing_cb = {}
        with open("pabrai_prices.json") as _f:
            existing_prices = json.load(_f)
            existing_cb = existing_prices.get("costBasis", {})
            print(f"  Loaded {len(existing_cb)} cached cost basis (incremental)")
    except FileNotFoundError:
        pass
    cost_basis = {}
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
                        prev_shares = qh["shares"]
        from_ts, to_ts = quarter_ts(buy_q)
        print(f"  Cost basis {tk} ({buy_q})...", end=" ", flush=True)
        # Incremental: skip if already have cached Yahoo data
        if should_skip_recent(tk, buy_q, existing_cb):
            recent = existing_cb[tk]["recent"]
            print("skip (cached yahoo)")
            recent = None
            c = yahoo_chart(tk, from_ts, to_ts)
        if c and c["closes"]:
            avg = sum(c["closes"]) / len(c["closes"])
            low = min(c["lows"])
            high = max(c["highs"])
            buy_est = round(low * 0.7 + avg * 0.3, 2)
            recent = {"buy": buy_est, "low": round(low,2), "high": round(high,2), "quarter": buy_q, "source": "yahoo"}
            print(f"buy≈${buy_est} [{low:.2f}-{high:.2f}]")
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
                    q_price = qd["value"] / qd["shares"]
                total_weighted_cost += q_price * qd["shares"]
                total_shares_sum += qd["shares"]
                valid_q += 1
                time.sleep(4.0 + random.uniform(0, 2))
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
    prices = {
        "updated": datetime.now(timezone.utc).isoformat() + "Z",
        "quotes": quotes,
        "costBasis": cost_basis,
    }
    with open("pabrai_prices.json", "w") as f:
        json.dump(prices, f, indent=2)
    print(f"\n✅ pabrai_prices.json written ({len(quotes)} quotes, {len(cost_basis)} cost basis)")
if __name__ == "__main__":
    main()
