#!/usr/bin/env python3
"""Add cookie+crumb auth to all fetch_prices_*.py scripts carefully."""
import os, re

BASE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = [
    "fetch_prices_akre_greenberg.py",
    "fetch_prices_buffett.py",
    "fetch_prices_duan.py",
    "fetch_prices_spier.py",
    "fetch_prices_tepper.py",
    "fetch_prices_webb.py",
]

YAHOO_AUTH_CODE = '''
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

ok = fail = 0

for name in SCRIPTS:
    path = os.path.join(BASE, name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # 1. Fix imports - add CookieJar, random if missing
    if "from http.cookiejar import CookieJar" not in content:
        # Add CookieJar import after urllib imports
        for pattern in [
            "import json, time, urllib.request, urllib.error",
            "import json, os, time, urllib.request, urllib.error",
        ]:
            if pattern in content:
                content = content.replace(
                    pattern,
                    "import json, time, random, urllib.request, urllib.error\nfrom http.cookiejar import CookieJar"
                )
                break

    # 2. Add random import if still missing
    if "import random" not in content:
        content = "import random\n" + content

    # 3. Add _yahoo_state + _yahoo_init after YAHOO_HEADERS block
    if "_yahoo_state" not in content:
        # Find the closing brace of YAHOO_HEADERS
        pattern = r"(YAHOO_HEADERS\s*=\s*\{[^}]+\})"
        m = re.search(pattern, content)
        if m:
            insert_pos = m.end()
            content = content[:insert_pos] + YAHOO_AUTH_CODE + content[insert_pos:]

    # 4. Replace the old yahoo_chart function with the new one
    # Find "def yahoo_chart" and replace until the next "def " at column 0
    old_func_pattern = r'\ndef yahoo_chart\(symbol, from_ts, to_ts.*?\n(?=\ndef |\Z)'
    new_func = '''
def yahoo_chart(symbol, from_ts, to_ts):
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
    content_new = re.sub(old_func_pattern, new_func, content, flags=re.DOTALL)
    if content_new != content:
        content = content_new

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        ok += 1
        print(f"  ✅ {name}")
    else:
        print(f"  ⚠ {name}: no changes")

print(f"\n{ok} scripts updated")
