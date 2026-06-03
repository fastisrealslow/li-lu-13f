"""Shared utilities for fetch_prices_*.py scripts.
Provides Yahoo chart fetching with rate-limit handling and incremental caching.
"""
import json, time, urllib.request, urllib.error
from datetime import datetime

YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "identity",
    "Referer": "https://finance.yahoo.com/",
}

def yahoo_chart(symbol, from_ts, to_ts, max_retries=3):
    """Fetch K-line data from Yahoo Finance with 429 retry + exponential backoff."""
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={from_ts}&period2={to_ts}&interval=1d"
    for attempt in range(max_retries):
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
            if e.code == 429 and attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)  # 2, 4, 8 seconds
                print(f"  [Yahoo 429] retry in {wait}s...", file=__import__('sys').stderr)
                time.sleep(wait)
                continue
            print(f"  [Yahoo error] HTTP {e.code}", file=__import__('sys').stderr)
            return None
        except Exception as e:
            print(f"  [Yahoo error] {e}", file=__import__('sys').stderr)
            return None
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

def calc_cost_basis(ticker, holdings, current_quarter, prev_quarter, hist_holdings,
                    existing_cost_basis=None, yahoo_sleep=0.5):
    """Calculate cost basis for a single ticker with incremental caching.
    
    Args:
        existing_cost_basis: dict from existing prices file, or None
        yahoo_sleep: seconds to sleep between Yahoo requests
    
    Returns:
        dict with 'recent' and 'allTime' keys
    """
    # Determine buy quarter
    buy_q = current_quarter
    h = None
    for holding in holdings:
        if holding["ticker"] == ticker:
            h = holding
            break
    if h is None:
        return None
    
    if h.get("prevShares", 0) > 0 and h["shares"] <= h["prevShares"]:
        prev_qs = sorted(hist_holdings.keys())
        prev_shares = None
        for q in prev_qs:
            for qh in hist_holdings.get(q, []):
                if qh["ticker"] == ticker and qh.get("shares", 0) > 0:
                    if prev_shares is None:
                        buy_q = q
                    elif qh["shares"] > prev_shares:
                        buy_q = q
                    prev_shares = qh["shares"]
    
    # Incremental: skip if existing data is already from Yahoo
    existing = None
    if existing_cost_basis and ticker in existing_cost_basis:
        existing = existing_cost_basis[ticker]
        existing_recent = existing.get("recent", {})
        if existing_recent.get("source") == "yahoo" and existing_recent.get("quarter") == buy_q:
            print(f"  Cost basis {ticker} ({buy_q})... skip (cached)", flush=True)
            return existing
    
    from_ts, to_ts = quarter_ts(buy_q)
    print(f"  Cost basis {ticker} ({buy_q})...", end=" ", flush=True)
    
    recent = None
    c = yahoo_chart(ticker, from_ts, to_ts)
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
    
    # allTime: check which quarters need fresh Yahoo data
    quarterly_data = []
    for q_key, q_holdings in sorted(hist_holdings.items()):
        for qh in q_holdings:
            if qh["ticker"] == ticker and qh.get("shares", 0) > 0:
                quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})
    
    all_time = None
    if quarterly_data:
        total_weighted_cost = 0.0
        total_shares_sum = 0
        valid_q = 0
        
        # Check if we can reuse existing allTime data
        existing_all = existing.get("allTime") if existing else None
        existing_first_q = existing_all.get("first") if existing_all else None
        existing_last_q = existing_all.get("last") if existing_all else None
        existing_quarters_count = existing_all.get("quarters") if existing_all else 0
        
        # If existing allTime covers all quarters and is from Yahoo, reuse it
        if (existing_all and existing_first_q == quarterly_data[0]["quarter"] and
            existing_last_q == quarterly_data[-1]["quarter"] and existing_quarters_count >= len(quarterly_data)):
            all_time = existing_all
            print(f"| all-time wavg=${existing_all.get('avg','?')} ({existing_quarters_count}q, cached)")
        else:
            for qd in quarterly_data:
                q_from, q_to = quarter_ts(qd["quarter"])
                c = yahoo_chart(qd["ticker"] if "ticker" in qd else ticker, q_from, q_to)
                if c and c["closes"]:
                    avg = sum(c["closes"]) / len(c["closes"])
                    low = min(c["lows"])
                    q_price = low * 0.7 + avg * 0.3
                else:
                    q_price = qd["value"] / qd["shares"]
                total_weighted_cost += q_price * qd["shares"]
                total_shares_sum += qd["shares"]
                valid_q += 1
                time.sleep(yahoo_sleep)
            all_avg = round(total_weighted_cost / total_shares_sum, 2)
            all_time = {
                "avg": all_avg,
                "quarters": valid_q,
                "first": quarterly_data[0]["quarter"],
                "last": quarterly_data[-1]["quarter"],
            }
            print(f"| all-time wavg=${all_avg} ({valid_q}q, {total_shares_sum} total shares)")
    
    time.sleep(yahoo_sleep)
    return {"recent": recent, "allTime": all_time}
