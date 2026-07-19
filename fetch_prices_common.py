"""Shared utilities for fetch_prices_*.py scripts.
Provides Yahoo chart fetching via yfinance and incremental caching.
"""
import json, time, random
from datetime import datetime


def yahoo_chart(symbol, from_ts, to_ts, max_retries=2):
    """Fetch K-line data from Yahoo Finance using yfinance library."""
    try:
        import yfinance as yf
        from datetime import datetime, timezone
        start_dt = datetime.fromtimestamp(from_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        end_dt = datetime.fromtimestamp(to_ts, tz=timezone.utc).strftime('%Y-%m-%d')
        # yfinance uses BRK-B/BRK-A instead of BRK.B/BRK.A
        yf_symbol = symbol.replace('.B', '-B').replace('.A', '-A') if symbol.startswith('BRK') else symbol
        ticker = yf.Ticker(yf_symbol)
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
                    existing_cost_basis=None, yahoo_sleep=4.0):
    """Calculate cost basis for a single ticker with incremental caching."""
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

    existing = None
    if existing_cost_basis and ticker in existing_cost_basis:
        existing = existing_cost_basis[ticker]
        existing_recent = existing.get("recent", {})
        existing_alltime = existing.get("allTime") or {}
        alltime_complete = bool(existing_alltime.get("avg"))
        if existing_recent.get("source") == "yahoo" and existing_recent.get("quarter") == buy_q and alltime_complete:
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

    quarterly_data = []
    for q_key, q_holdings in sorted(hist_holdings.items()):
        for qh in q_holdings:
            if qh["ticker"] == ticker and qh.get("shares", 0) > 0:
                quarterly_data.append({"quarter": q_key, "shares": qh["shares"], "value": qh["value"]})

    # Filter to buy quarters only (delta shares > 0) — holding periods don't affect cost basis
    buy_quarters = []
    prev_q_shares = 0
    for qd in quarterly_data:
        delta = qd["shares"] - prev_q_shares
        if delta > 0:
            buy_quarters.append({**qd, "delta_shares": delta})
        prev_q_shares = qd["shares"]

    all_time = None
    if buy_quarters:
        existing_all = existing.get("allTime") if existing else None
        existing_first_q = existing_all.get("first") if existing_all else None
        existing_last_q = existing_all.get("last") if existing_all else None
        existing_quarters_count = existing_all.get("quarters") if existing_all else 0

        if (existing_all and existing_first_q == quarterly_data[0]["quarter"] and
            existing_last_q == quarterly_data[-1]["quarter"] and existing_quarters_count >= len(quarterly_data)):
            all_time = existing_all
            print(f"| all-time wavg=${existing_all.get('avg','?')} ({existing_quarters_count}q, cached)")
        else:
            total_weighted_cost = 0.0
            total_shares_sum = 0
            valid_q = 0
            first_buy_q = None
            last_buy_q = None
            for qd in buy_quarters:
                q_from, q_to = quarter_ts(qd["quarter"])
                c = yahoo_chart(qd["ticker"] if "ticker" in qd else ticker, q_from, q_to)
                if c and c["closes"]:
                    avg = sum(c["closes"]) / len(c["closes"])
                    low = min(c["lows"])
                    q_price = low * 0.7 + avg * 0.3
                else:
                    q_price = qd["value"] / qd["shares"]
                total_weighted_cost += q_price * qd["delta_shares"]
                total_shares_sum += qd["delta_shares"]
                valid_q += 1
                if first_buy_q is None: first_buy_q = qd["quarter"]
                last_buy_q = qd["quarter"]
                time.sleep(yahoo_sleep + random.uniform(0, 2))
            all_avg = round(total_weighted_cost / total_shares_sum, 2)
            all_time = {
                "avg": all_avg,
                "quarters": valid_q,
                "first": first_buy_q,
                "last": last_buy_q,
            }
            print(f"| all-time wavg=${all_avg} ({valid_q} buy qtrs, {total_shares_sum} delta shares)")

    time.sleep(yahoo_sleep + random.uniform(0, 2))
    return {"recent": recent, "allTime": all_time}
