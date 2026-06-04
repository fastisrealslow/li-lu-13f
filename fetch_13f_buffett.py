#!/usr/bin/env python3
"""Fetch Berkshire Hathaway (Warren Buffett) 13F from SEC EDGAR and update buffett.json.

CIK: 0001067983
Uses only stdlib — no pip install needed.

Key difference from other investors:
- Berkshire has MANY subsidiary filers (each subsidiary reports separately)
- Same ticker appears multiple times under different subsidiary names
- MUST consolidate: sum shares + values for same ticker per quarter

Usage:
  python3 fetch_13f_buffett.py            # Normal mode: latest 2 quarters only
  python3 fetch_13f_buffett.py --full     # Full mode: ALL historical filings
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

CIK = "1067983"
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "buffett.json")
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

# Map issuer names (as they appear in SEC XML, ALL CAPS) → ticker
TICKER_MAP = {
    # Core Buffett holdings
    "APPLE INC": "AAPL",
    "COCA COLA CO": "KO",
    "AMERICAN EXPRESS CO": "AXP",
    "BANK AMERICA CORP": "BAC",
    "BANK OF AMERICA CORP": "BAC",
    "BANK AMER CORP": "BAC",
    "BANK OF AMERICA CORPORATION": "BAC",
    "CHEVRON CORPORATION": "CVX",
    "CHEVRON CORP NEW": "CVX",
    "OCCIDENTAL PETE CORP": "OXY",
    "OXYGEN PETROLEUM": "OXY",
    "KRAFT HEINZ CO": "KHC",
    "KRAFT HEINZ COMPANY": "KHC",
    "KRAFT HEINZ CO /THE": "KHC",
    "MOODYS CORP": "MCO",
    "MOODY'S CORP": "MCO",
    "DAVITA INC": "DVA",
    "DAVITA HEALTHCARE PARTNERS INC": "DVA",
    "VERISIGN INC": "VRSN",
    "KROGER CO": "KR",
    "SIRIUSXM HOLDINGS INC": "SIRI",
    "SIRIUS XM RADIO INC": "SIRI",
    "SIRIUS XM HOLDINGS INC": "SIRI",
    "LIBERTY SIRIUSXM GROUP": "LSXMA",
    "LIBERTY SIRIUS XM GROUP": "LSXMA",
    "DELTA AIR LINES INC": "DAL",
    "DELTA AIR INC": "DAL",
    "CHUBB LTD": "CB",
    "CHUBB LTD SWITZ": "CB",
    "ALPHABET INC": ("GOOGL", "GOOG"),  # CL A → GOOGL, CL C → GOOG
    "GOOGLE INC": ("GOOGL", "GOOG"),
    "CAPITAL ONE FINL CORP": "COF",
    "CAPITAL ONE FINANCIAL CORP": "COF",
    "ALLY FINL INC": "ALLY",
    "ALLY FINANCIAL INC": "ALLY",
    "NUCOR CORP": "NUE",
    "NUCOR CORPORATION": "NUE",
    "LENNAR CORP": "LEN",
    "LENNAR CORPORATION": "LEN",
    "LOUISIANA PAC CORP": "LPX",
    "LOUISIANA PACIFIC CORP": "LPX",
    "LOUISIANA PACIFIC CORPORATION": "LPX",
    "NEW YORK TIMES CO": "NYT",
    "NEW YORK TIMES CO MTN BE": "NYT",
    "NEW YORK TIMES CO NEW": "NYT",
    "CONSTELLATION BRANDS INC": "STZ",
    "CONSTELLATION BRANDS INC.": "STZ",
    "NVR INC": "NVR",
    "NVR INC.": "NVR",
    "MACYS INC": "M",
    "MACY'S INC": "M",
    "JEFFERIES FINANCIAL GROUP IN": "JEF",
    "JEFFERIES FINANCIAL GROUP INC": "JEF",
    "LIBERTY LIVE HOLDINGS INC": "LLYVA",
    "LIBERTY LIVE GROUP": "LLYVA",
    "LIBERTY MEDIA ACQUISITION CORP": "LLYVA",
    # Also common ones that might appear
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B",
    "BRK": "BRK.B",
    # ETFs
    "VANGUARD S&P 500 ETF": "VOO",
    "VANGUARD INDEX FDS S&P 500 ETF": "VOO",
    "SPDR S&P 500 ETF TRUST": "SPY",
    # Other possible holdings
    "HEICO CORP": "HEI",
    "HEICO CORPORATION": "HEI",
    "RH": "RH",
    "RH RESTORATION HARDWARE": "RH",
    "STONECO LTD": "STNE",
    "HP INC": "HPQ",
    "HP INC.": "HPQ",
    "PARAMOUNT GLOBAL": "PARA",
    "VIACOMCBS INC": "PARA",
    "VIACOMCBS INC.": "PARA",
    "ACTIVISION BLIZZARD INC": "ATVI",
    "ACTIVISION BLIZZARD": "ATVI",
    "US BANCORP DEL": "USB",
    "U S BANCORP DEL": "USB",
    "CHARLES SCHWAB CORP": "SCHW",
    "SCHWAB CHARLES CORP": "SCHW",
    "DAVITA HEALTHCARE PARTNERS IN": "DVA",
    "DAVITA HEALTHCARE": "DVA",
    "DAVITA INC.": "DVA",
    "DAVITA INC /DE/": "DVA",
    "DAVITA": "DVA",
}

# Sub-ticker map for class-specific resolution (key = (name, True) for CL A, (name, False) for others)
TICKER_CLASS_MAP = {
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    ("GOOGLE INC", True): "GOOGL",
    ("GOOGLE INC", False): "GOOG",
    ("LIBERTY SIRIUSXM GROUP", True): "LSXMA",
    ("LIBERTY SIRIUSXM GROUP", False): "LSXMK",
    ("LIBERTY SIRIUS XM GROUP", True): "LSXMA",
    ("LIBERTY SIRIUS XM GROUP", False): "LSXMK",
    ("LIBERTY LIVE HOLDINGS INC", True): "LLYVA",
    ("LIBERTY LIVE HOLDINGS INC", False): "LLYVK",
    ("LIBERTY LIVE GROUP", True): "LLYVA",
    ("LIBERTY LIVE GROUP", False): "LLYVK",
}

# Sector assignment
SECTORS = {
    "AAPL": "科技", "KO": "消费", "AXP": "金融服务", "BAC": "金融/银行",
    "CVX": "能源", "OXY": "能源", "KHC": "消费", "MCO": "金融服务",
    "DVA": "医药", "VRSN": "科技", "KR": "消费", "SIRI": "娱乐",
    "LSXMA": "娱乐", "LSXMK": "娱乐", "DAL": "消费", "CB": "保险",
    "GOOGL": "互联网", "GOOG": "互联网", "COF": "金融服务", "ALLY": "金融服务",
    "NUE": "工业", "LEN": "工业", "LPX": "工业", "NYT": "娱乐",
    "STZ": "消费", "NVR": "工业", "M": "消费", "JEF": "金融服务",
    "LLYVA": "娱乐", "LLYVK": "娱乐", "BRK.B": "综合金融",
    "VOO": "金融服务", "SPY": "金融服务",
    "HEI": "工业", "RH": "消费", "STNE": "金融服务", "HPQ": "科技",
    "PARA": "娱乐", "ATVI": "游戏", "USB": "金融/银行", "SCHW": "金融服务",
}


def sec_fetch(path: str) -> bytes:
    url = f"https://www.sec.gov{path}" if path.startswith("/") else f"https://data.sec.gov/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def get_recent_filings() -> list[dict]:
    data = json.loads(sec_fetch(f"submissions/CIK{CIK.zfill(10)}.json"))
    rec = data["filings"]["recent"]
    filings = []
    for i in range(len(rec["form"])):
        if rec["form"][i] == "13F-HR":
            filings.append({
                "accession": rec["accessionNumber"][i].replace("-", ""),
                "accessionDashed": rec["accessionNumber"][i],
                "filingDate": rec["filingDate"][i],
                "reportDate": rec["reportDate"][i],
            })
    return filings


def quarter_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year} Q{q}"


def find_info_table_xml(accession: str, accession_dashed: str) -> str:
    html = sec_fetch(
        f"/Archives/edgar/data/{CIK}/{accession}/{accession_dashed}-index.html"
    ).decode("utf-8", errors="replace")
    pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+\.xml)</a>\s*</td>\s*<td[^>]*>\s*INFORMATION TABLE'
    for m in re.finditer(pattern, html, re.IGNORECASE):
        href = m.group(1)
        if "xslForm13F" not in href:
            return href
    m = re.search(r"(\d{2})(\d)(\d)$", accession)
    if m:
        return f"/Archives/edgar/data/{CIK}/{accession}/13fhciq{m.group(2)}{m.group(3)}.xml"
    raise RuntimeError("Cannot find INFOTABLE XML")


def resolve_ticker(name: str, cls: str) -> str:
    n = name.strip()
    is_a = "CL A" in (cls or "").upper()

    # Try class-specific map first
    class_key = (n, is_a)
    if class_key in TICKER_CLASS_MAP:
        return TICKER_CLASS_MAP[class_key]

    # Try simple map
    if n in TICKER_MAP:
        val = TICKER_MAP[n]
        if isinstance(val, tuple):
            return val[0] if is_a else val[1]
        return val

    return f"?{n}"


def parse_holdings(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    raw_entries = []
    for info in root.findall("ns:infoTable", NS):
        name_el = info.find("ns:nameOfIssuer", NS)
        cls_el = info.find("ns:titleOfClass", NS)
        val_el = info.find("ns:value", NS)
        shares_el = info.find(".//ns:sshPrnamt", NS)
        name_val = name_el.text.strip() if name_el is not None and name_el.text else ""
        cls_val = cls_el.text.strip() if cls_el is not None and cls_el.text else ""
        raw_entries.append({
            "name": name_val,
            "cls": cls_val,
            "shares": int(shares_el.text) if shares_el is not None and shares_el.text else 0,
            "value": int(val_el.text) if val_el is not None and val_el.text else 0,
        })

    # Auto-detect value unit: SEC changed from kUSD to USD around 2022 Q4.
    # Heuristic: if avg value/shares < $1, values are in thousands of USD → scale ×1000.
    valid = [e for e in raw_entries if e["shares"] > 0 and e["value"] > 0]
    if valid:
        avg_price = sum(e["value"] / e["shares"] for e in valid) / len(valid)
        if avg_price < 1.0:  # clearly in kUSD
            for e in raw_entries:
                e["value"] = e["value"] * 1000

    # Resolve tickers
    for entry in raw_entries:
        entry["ticker"] = resolve_ticker(entry["name"], entry["cls"])

    # CONSOLIDATE: same ticker from different subsidiaries → sum shares + values
    consolidated = {}
    for entry in raw_entries:
        tk = entry["ticker"]
        if tk not in consolidated:
            consolidated[tk] = {
                "ticker": tk,
                "name": entry["name"],
                "cls": entry["cls"],
                "shares": entry["shares"],
                "value": entry["value"],
                "sector": SECTORS.get(tk, "其他"),
            }
        else:
            consolidated[tk]["shares"] += entry["shares"]
            consolidated[tk]["value"] += entry["value"]

    holdings = list(consolidated.values())

    # SEC 13F values are in thousands ($1,000 units).
    # Berkshire total should be ~$200B+. If total < 10M, multiply by 1000.
    total_val = sum(h["value"] for h in holdings)
    if total_val < 10_000_000:
        for h in holdings:
            h["value"] *= 1000
        total_val = sum(h["value"] for h in holdings)

    holdings.sort(key=lambda h: h["value"], reverse=True)
    return holdings


def fetch_and_parse_filing(filing: dict) -> tuple[list[dict], int]:
    info_path = find_info_table_xml(filing["accession"], filing["accessionDashed"])
    xml_bytes = sec_fetch(info_path)
    holdings = parse_holdings(xml_bytes)
    total = sum(h["value"] for h in holdings)
    return holdings, total


def save_data(data: dict):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    full_mode = "--full" in sys.argv
    print("Fetching Berkshire Hathaway 13F..." + (" (FULL MODE)" if full_mode else ""))
    filings = get_recent_filings()
    if len(filings) < 2:
        print(f"ERROR: only found {len(filings)} filings, need 2")
        sys.exit(1)

    if os.path.exists(DATA_PATH):
        with open(DATA_PATH, "r") as f:
            data = json.load(f)
    else:
        data = {
            "meta": {
                "manager": "Berkshire Hathaway Inc.",
                "managerCIK": "0001067983",
                "notablePeople": ["Warren Buffett"],
                "lastUpdated": "",
            },
            "current": {},
            "history": {"quarters": [], "values": [], "holdings": {}},
        }

    if full_mode:
        return main_full(filings, data)

    # Quick mode: latest 2 quarters
    cur_f, prev_f = filings[0], filings[1]
    print(f"  Latest: {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_xml = sec_fetch(find_info_table_xml(cur_f["accession"], cur_f["accessionDashed"]))
    prev_xml = sec_fetch(find_info_table_xml(prev_f["accession"], prev_f["accessionDashed"]))
    cur_holdings = parse_holdings(cur_xml)
    prev_holdings = parse_holdings(prev_xml)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in cur_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"] = p.get("value", 0)

    total = sum(h["value"] for h in cur_holdings)
    data["current"] = {
        "quarter": quarter_label(cur_f["reportDate"]),
        "filingDate": cur_f["filingDate"],
        "periodEnd": cur_f["reportDate"],
        "totalValue": total,
        "holdings": cur_holdings,
        "prevQuarter": quarter_label(prev_f["reportDate"]),
        "prevTotalValue": sum(h["value"] for h in prev_holdings),
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    q_label = quarter_label(cur_f["reportDate"])
    if q_label not in data["history"]["quarters"]:
        data["history"]["quarters"].append(q_label)
        data["history"]["values"].append(round(total / 1_000_000))
        data["history"]["holdings"][q_label] = cur_holdings

    save_data(data)
    print(f"Updated: {len(cur_holdings)} holdings, ${total:,.0f} total")


def main_full(filings: list[dict], data: dict):
    # filings[0] is most recent
    filings_sorted = list(reversed(filings))  # oldest first for history
    print(f"Found {len(filings_sorted)} total filings to process.")

    if "history" not in data:
        data["history"] = {"quarters": [], "values": [], "holdings": {}}
    if "holdings" not in data["history"]:
        data["history"]["holdings"] = {}

    existing_quarters = set(data["history"]["quarters"])
    new_quarters = 0
    skipped = 0
    all_fetched = {}  # q_label → (holdings, total)

    for i, f in enumerate(filings_sorted):
        q_label = quarter_label(f["reportDate"])
        if q_label in existing_quarters:
            skipped += 1
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label} (already)")
            # Still fetch to have it for prevQuarter calculation
            try:
                holdings, total = fetch_and_parse_filing(f)
                all_fetched[q_label] = (holdings, total)
            except Exception as e:
                print(f"    -> ERROR fetching skipped: {e}")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label}...")
        try:
            holdings, total = fetch_and_parse_filing(f)
            all_fetched[q_label] = (holdings, total)

            # Find previous quarter data for prevShares/prevValue
            prev_q = None
            for j in range(i - 1, -1, -1):
                prev_q_label = quarter_label(filings_sorted[j]["reportDate"])
                if prev_q_label in all_fetched:
                    prev_q = prev_q_label
                    break

            if prev_q and prev_q in all_fetched:
                prev_holdings = all_fetched[prev_q][0]
                prev_map = {h["ticker"]: h for h in prev_holdings}
                for h in holdings:
                    p = prev_map.get(h["ticker"], {})
                    h["prevShares"] = p.get("shares", 0)
                    h["prevValue"] = p.get("value", 0)
            else:
                for h in holdings:
                    h["prevShares"] = 0
                    h["prevValue"] = 0

            data["history"]["quarters"].append(q_label)
            data["history"]["values"].append(round(total / 1_000_000))
            data["history"]["holdings"][q_label] = holdings
            new_quarters += 1
            print(f"    -> {len(holdings)} holdings, ${total:,.0f}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    # Update current with latest
    latest = filings[0]
    latest_q = quarter_label(latest["reportDate"])
    if latest_q in all_fetched:
        latest_holdings, latest_total = all_fetched[latest_q]
    else:
        latest_holdings, latest_total = fetch_and_parse_filing(latest)
        all_fetched[latest_q] = (latest_holdings, latest_total)

    prev_f = filings[1]
    prev_q = quarter_label(prev_f["reportDate"])
    if prev_q in all_fetched:
        prev_holdings, _ = all_fetched[prev_q]
    else:
        prev_holdings, _ = fetch_and_parse_filing(prev_f)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in latest_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"] = p.get("value", 0)

    data["current"] = {
        "quarter": quarter_label(latest["reportDate"]),
        "filingDate": latest["filingDate"],
        "periodEnd": latest["reportDate"],
        "totalValue": latest_total,
        "holdings": latest_holdings,
        "prevQuarter": quarter_label(prev_f["reportDate"]),
        "prevTotalValue": sum(h["value"] for h in prev_holdings),
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if latest_q not in data["history"]["quarters"]:
        data["history"]["quarters"].append(latest_q)
        data["history"]["values"].append(round(latest_total / 1_000_000))
    data["history"]["holdings"][latest_q] = latest_holdings

    save_data(data)
    print(f"\nDone: {new_quarters} new quarters, {skipped} skipped.")
    print(f"Total quarters in history: {len(data['history']['quarters'])}")
    print(f"Current: {len(latest_holdings)} holdings, ${latest_total:,.0f}")


if __name__ == "__main__":
    main()
