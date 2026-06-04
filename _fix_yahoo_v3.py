#!/usr/bin/env python3
"""Fix all 6 price scripts: fix pre-existing bugs + add cookie+crumb auth."""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

SCRIPTS_CONFIG = {
    "fetch_prices_akre_greenberg.py": {"file": "akre.json"},
    "fetch_prices_buffett.py": {"file": "buffett.json"},
    "fetch_prices_duan.py": {"file": "duan.json"},
    "fetch_prices_spier.py": {"file": "spier.json"},
    "fetch_prices_tepper.py": {"file": "tepper.json"},
    "fetch_prices_webb.py": {"file": "webb.json"},
}

OLD_YAHOO_CHART = '''def yahoo_chart(symbol, from_ts, to_ts, _retries=[0]):
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
    return None'''

NEW_YAHOO_CHART = '''# ── Yahoo cookie+crumb auth ──
_yahoo_state = {"cj": None, "crumb": None, "opener": None}

def _yahoo_init():
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
            return False
        _yahoo_state["cj"] = cj
        _yahoo_state["crumb"] = crumb
        _yahoo_state["opener"] = opener
        print(f"  [Yahoo] authenticated, crumb={crumb[:8]}...", flush=True)
        return True
    except Exception as e:
        print(f"  [Yahoo auth failed] {e}", file=__import__('sys').stderr)
        return False

def yahoo_chart(symbol, from_ts, to_ts):
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
    return None'''

ok = fail = 0

for name, cfg in SCRIPTS_CONFIG.items():
    path = os.path.join(BASE, name)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    original = content

    # Fix 1: Add CookieJar import
    if "from http.cookiejar import CookieJar" not in content:
        for pat in [
            "import json, time, urllib.request, urllib.error",
            "import json, os, time, urllib.request, urllib.error",
        ]:
            if pat in content:
                content = content.replace(pat,
                    "import json, time, random, urllib.request, urllib.error\nfrom http.cookiejar import CookieJar")
                break

    # Fix 2: Add random import if missing
    if "import random" not in content:
        content = "import random\n" + content

    # Fix 3: Replace yahoo_chart function (exact match)
    if OLD_YAHOO_CHART in content:
        content = content.replace(OLD_YAHOO_CHART, NEW_YAHOO_CHART)
    else:
        # Try to find partial match - maybe the retry logic was already changed
        # Find "def yahoo_chart" and replace until "def quarter_ts"
        start = content.find("def yahoo_chart(")
        end = content.find("\ndef quarter_ts(")
        if start > 0 and end > start:
            content = content[:start] + NEW_YAHOO_CHART + content[end:]
        else:
            print(f"  ⚠ {name}: could not find yahoo_chart to replace")
            fail += 1
            continue

    if content != original:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        ok += 1
        print(f"  ✅ {name}")
    else:
        print(f"  ⚠ {name}: no changes")

print(f"\n{ok} updated, {fail} failed")
