#!/usr/bin/env python3
"""Fetch Pabrai (Dalal Street) stock prices from Finnhub and update pabrai_prices.json."""
import json, os, time, urllib.request
from datetime import datetime, timezone

KEY = os.environ["FINNHUB_KEY"]

with open("pabrai.json") as f:
    d = json.load(f)
tickers = [h["ticker"] for h in d["current"]["holdings"]]

quotes = {}
for tk in tickers:
    url = f"https://finnhub.io/api/v1/quote?symbol={tk}&token={KEY}"
    req = urllib.request.Request(url, headers={"User-Agent": "13F-Tracker/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            q = json.loads(resp.read().decode())
        if q.get("c", 0) > 0:
            quotes[tk] = {"c": round(q["c"], 2)}
    except Exception as e:
        print(f"  WARN {tk}: {e}")
    time.sleep(0.2)

with open("pabrai_prices.json") as f:
    pr = json.load(f)
pr["quotes"] = quotes
pr["updated"] = datetime.now(timezone.utc).isoformat() + "Z"
with open("pabrai_prices.json", "w") as f:
    json.dump(pr, f, indent=2)
    f.write("\n")
print(f"Pabrai prices: {len(quotes)} tickers")