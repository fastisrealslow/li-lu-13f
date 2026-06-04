#!/usr/bin/env python3
"""Replace Yahoo HTTP calls with yfinance in all price scripts."""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))

NEW_YAHOO_CHART = '''def yahoo_chart(symbol, from_ts, to_ts):
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
'''

SCRIPTS = [
    "fetch_prices_akre_greenberg.py",
    "fetch_prices_buffett.py",
    "fetch_prices_duan.py",
    "fetch_prices_spier.py",
    "fetch_prices_tepper.py",
    "fetch_prices_webb.py",
]

ok = fail = 0

for name in SCRIPTS:
    path = os.path.join(BASE, name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Replace the entire yahoo_chart function block
    # Find "def yahoo_chart" and replace until "def quarter_ts" or next def
    start = content.find("def yahoo_chart(")
    if start < 0:
        print(f"  ⚠ {name}: no yahoo_chart function found")
        continue

    # Find the end: next function definition at column 0
    end = -1
    for marker in ["\ndef quarter_ts(", "\ndef main(", "\ndef calc_", "\ndef fetch_"]:
        pos = content.find(marker, start + 20)
        if pos > 0 and (end < 0 or pos < end):
            end = pos

    if end > 0:
        content = content[:start] + NEW_YAHOO_CHART + content[end:]
        # Also remove old cookie+crumb code if present
        for block in [
            "# ── Yahoo cookie+crumb auth ──",
            "_yahoo_state",
            "def _yahoo_init",
            "from http.cookiejar import CookieJar",
        ]:
            if block in content:
                # Remove lines containing these
                lines = content.split('\n')
                cleaned = []
                skip = False
                for line in lines:
                    if block.startswith("#") and block in line:
                        skip = True
                        continue
                    if block in line and not block.startswith("#"):
                        skip = True
                        continue
                    if skip and line.strip() == '':
                        skip = False
                        continue
                    if skip and (line.startswith("def ") or line.startswith("# ──")):
                        skip = False
                    if not skip:
                        cleaned.append(line)
                content = '\n'.join(cleaned)

        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        ok += 1
        print(f"  ✅ {name}")
    else:
        print(f"  ❌ {name}: could not find end of yahoo_chart")
        fail += 1

print(f"\n{ok} updated, {fail} failed")
