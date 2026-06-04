#!/usr/bin/env python3
"""Add cookie+crumb auth to all fetch_prices_*.py scripts."""
import os, glob

BASE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [
    "fetch_prices_akre_greenberg.py",
    "fetch_prices_buffett.py",
    "fetch_prices_duan.py",
    "fetch_prices_spier.py",
    "fetch_prices_tepper.py",
    "fetch_prices_webb.py",
]

YAHOO_IMPORTS = '''import json, time, random, urllib.request, urllib.error
from datetime import datetime
from http.cookiejar import CookieJar'''

YAHOO_STATE = '''
# ── Yahoo cookie+crumb auth ──
_yahoo_state = {"cj": None, "crumb": None, "opener": None}

def _yahoo_init():
    """Initialize Yahoo session: get cookie + crumb."""
    if _yahoo_state["crumb"]:
        return True
    try:
        cj = CookieJar()
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
        opener.addheaders = list(YAHOO_HEADERS.items())
        opener.open("https://finance.yahoo.com/", timeout=15)
        time.sleep(1)
        req = opener.open("https://query2.finance.yahoo.com/v1/test/getcrumb", timeout=15)
        crumb = req.read().decode().strip()
        if not crumb or len(crumb) < 5:
            print(f"  [Yahoo] invalid crumb: {crumb!r}", file=__import__('sys').stderr)
            return False
        _yahoo_state["cj"] = cj
        _yahoo_state["crumb"] = crumb
        _yahoo_state["opener"] = opener
        print(f"  [Yahoo] authenticated, crumb={crumb[:8]}...", flush=True)
        return True
    except Exception as e:
        print(f"  [Yahoo auth failed] {e}", file=__import__('sys').stderr)
        return False
'''

YAHOO_CHART_NEW = '''def yahoo_chart(symbol, from_ts, to_ts):
    """Fetch K-line data from Yahoo Finance with cookie+crumb auth."""
    if not _yahoo_init():
        return None
    crumb = _yahoo_state["crumb"]
    opener = _yahoo_state["opener"]
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?period1={from_ts}&period2={to_ts}&interval=1d&crumb={crumb}"
    for attempt in range(4):
        try:
            req = opener.open(url, timeout=20)
            data = json.loads(req.read().decode())
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
                if attempt == 2:
                    _yahoo_state["crumb"] = None
                    _yahoo_init()
                wait = min(8 * (3 ** attempt) + random.randint(2, 8), 90)
                print(f"  [Yahoo 429] retry in {wait}s...", file=__import__('sys').stderr)
                time.sleep(wait)
                continue
            print(f"  [Yahoo error] HTTP {e.code}", file=__import__('sys').stderr)
            return None
        except Exception as e:
            print(f"  [Yahoo error] {e}", file=__import__('sys').stderr)
            return None
    return None
'''

ok = 0
fail = 0

for name in SCRIPTS:
    path = os.path.join(BASE, name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # 1. Replace imports
    import_patterns = [
        "import json, time, urllib.request, urllib.error",
        "import json, os, time, urllib.request, urllib.error",
        "import json, time, random, urllib.request, urllib.error",
    ]
    for pat in import_patterns:
        if pat in content:
            content = content.replace(pat, YAHOO_IMPORTS)
            break

    # 2. Add _yahoo_state after YAHOO_HEADERS block
    if "_yahoo_state" not in content:
        # Find the end of YAHOO_HEADERS dict (first line with just '}')
        lines = content.split('\n')
        insert_idx = None
        in_headers = False
        for i, line in enumerate(lines):
            if 'YAHOO_HEADERS' in line and '=' in line:
                in_headers = True
            if in_headers and line.strip() == '}':
                insert_idx = i + 1
                break
        if insert_idx:
            lines.insert(insert_idx, YAHOO_STATE)
            content = '\n'.join(lines)

    # 3. Replace yahoo_chart function
    # Find old yahoo_chart function and replace it
    old_func_start = "def yahoo_chart(symbol, from_ts, to_ts"
    if old_func_start in content:
        # Find the start of the function
        start_idx = content.index(old_func_start)
        # Find the end: next function def or end of file
        # Look for the next "def " or class at column 0 after the function
        search_area = content[start_idx + len(old_func_start):]
        # Find the next "def " or blank-line+non-indented text
        # Simple approach: find next "\ndef " after position start_idx+50
        end_marker = None
        for marker in ["\ndef quarter_ts", "\ndef main(", "\ndef calc_", "\ndef fetch_", "\ndef get_", "\ndef load_"]:
            pos = content.find(marker, start_idx + 50)
            if pos > 0:
                if end_marker is None or pos < end_marker:
                    end_marker = pos

        if end_marker:
            content = content[:start_idx] + YAHOO_CHART_NEW + content[end_marker:]
            print(f"  ✅ {name}: replaced yahoo_chart function")
        else:
            print(f"  ❌ {name}: could not find end of yahoo_chart")
            fail += 1
            continue
    else:
        print(f"  ⏭ {name}: no yahoo_chart function to replace")
        continue

    # 4. Remove duplicate "import random" lines that may have been added earlier
    lines = content.split('\n')
    seen_import_random = False
    cleaned = []
    for line in lines:
        if line.strip() == 'import random':
            if seen_import_random:
                continue
            seen_import_random = True
        cleaned.append(line)
    content = '\n'.join(cleaned)

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        ok += 1
    else:
        print(f"  ⚠ {name}: no changes made")

print(f"\n{ok} scripts updated, {fail} failed")
