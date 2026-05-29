#!/usr/bin/env python3
"""Fetch Himalaya Capital's latest 13F from SEC EDGAR and update data.json.

Designed to run in GitHub Actions on a schedule (weekly).
Uses only stdlib — no pip install needed.

Usage:
  python3 fetch_13f.py            # Normal mode: latest 2 quarters only
  python3 fetch_13f.py --full     # Full mode: ALL historical filings + per-quarter holdings
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CIK = "1709323"
USER_AGENT = "HimalayaCapitalResearch guoziyuan@xiaohongshu.com"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data.json")
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

TICKER_MAP = {
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    "APPLE INC": "AAPL",
    "BK OF AMERICA CORP": "BAC",
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "CROCS INC": "CROX",
    "EAST WEST BANCORP INC": "EWBC",
    "BLOCK H & R INC": "HRB",
    "MOODYS CORP": "MCO",
    "MSCI INC": "MSCI",
    "OCCIDENTAL PETE CORP": "OXY",
    "PDD HOLDINGS INC": "PDD",
    "S&P GLOBAL INC": "SPGI",
    "TENCENT MUSIC ENTMT GROUP": "TME",
}

SECTORS = {
    "GOOGL": "互联网", "GOOG": "互联网", "AAPL": "科技",
    "BAC": "金融", "EWBC": "金融", "BRK.B": "综合金融",
    "CROX": "消费", "OXY": "能源", "PDD": "电商", "TME": "娱乐",
    "SPGI": "金融服务", "MCO": "金融服务", "HRB": "金融服务", "MSCI": "金融服务",
    "BIDU": "互联网", "SINA": "互联网", "WB": "互联网",
    "BABA": "电商", "META": "社交", "FB": "社交",
    "MU": "半导体", "SABLE": "能源", "BRK.A": "综合金融",
    "PINDUODUO INC": "电商", "FACEBOOK INC": "社交",
    "ALIBABA GROUP HLDG LTD": "电商", "BERKSHIRE HATHAWAY INC": "综合金融",
    "META PLATFORMS INC": "社交", "MICRON TECHNOLOGY INC": "半导体",
    "SABLE OFFSHORE CORP": "能源", "Baidu Inc": "互联网",
    "Sina Corp": "互联网", "Weibo Corp": "互联网",
    # Pabrai (Dalal Street)
    "WARRIOR MET COAL INC": "煤炭", "TRANSOCEAN LTD": "油气钻探",
    "ALPHA METALLURGICAL RESOUR I": "冶金/煤炭", "CITIGROUP INC": "金融",
    "GENERAL MTRS CO": "汽车", "BANK OF AMERICA CORPORATION": "金融",
    "CHESAPEAKE ENERGY CORP": "油气", "GOLDMAN SACHS GROUP INC": "金融",
    "HORSEHEAD HLDG CORP": "工业",
}


def sec_fetch(path: str) -> bytes:
    """Fetch from SEC with proper User-Agent (required by SEC)."""
    url = f"https://www.sec.gov{path}" if path.startswith("/") else f"https://data.sec.gov/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def get_recent_filings() -> list[dict]:
    """Get all recent 13F-HR filings from the submissions API."""
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
    """Fetch the filing index page and extract the INFOTABLE XML path."""
    html = sec_fetch(
        f"/Archives/edgar/data/{CIK}/{accession}/{accession_dashed}-index.html"
    ).decode("utf-8", errors="replace")
    pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+\.xml)</a>\s*</td>\s*<td[^>]*>\s*INFORMATION TABLE'
    for m in re.finditer(pattern, html, re.IGNORECASE):
        href = m.group(1)
        if "xslForm13F" not in href:
            return href
    # Fallback
    m = re.search(r"(\d{2})(\d)(\d)$", accession)
    if m:
        return f"/Archives/edgar/data/{CIK}/{accession}/13fhciq{m.group(2)}{m.group(3)}.xml"
    raise RuntimeError("Cannot find INFOTABLE XML")


def ticker(name: str, cls: str) -> str:
    n = name.strip()
    key = (n, "CL A" in (cls or ""))
    if key in TICKER_MAP:
        return TICKER_MAP[key]
    mapped = TICKER_MAP.get(n)
    if mapped:
        return mapped
    # Unmapped - return original name prefixed so frontend knows
    return f"?{n}"


def parse_holdings(xml_bytes: bytes) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    holdings = []
    for info in root.findall("ns:infoTable", NS):
        name_el = info.find("ns:nameOfIssuer", NS)
        cls_el = info.find("ns:titleOfClass", NS)
        val_el = info.find("ns:value", NS)
        shares_el = info.find(".//ns:sshPrnamt", NS)
        name_val = name_el.text.strip() if name_el is not None and name_el.text else ""
        cls_val = cls_el.text.strip() if cls_el is not None and cls_el.text else ""
        tk = ticker(name_val, cls_val)
        holdings.append({
            "ticker": tk,
            "name": name_val,
            "cls": cls_val,
            "shares": int(shares_el.text) if shares_el is not None and shares_el.text else 0,
            "value": int(val_el.text) if val_el is not None and val_el.text else 0,
            "sector": SECTORS.get(tk, "其他"),
        })
    holdings.sort(key=lambda h: h["value"], reverse=True)
    return holdings


def fetch_and_parse_filing(filing: dict) -> tuple[list[dict], int]:
    """Fetch INFOTABLE XML for a single filing and return (holdings, total_value)."""
    info_path = find_info_table_xml(filing["accession"], filing["accessionDashed"])
    xml_bytes = sec_fetch(info_path)
    holdings = parse_holdings(xml_bytes)
    total = sum(h["value"] for h in holdings)
    return holdings, total


def save_data(data: dict):
    """Write data.json to disk."""
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    full_mode = "--full" in sys.argv
    print("Fetching 13F filings..." + (" (FULL MODE: all historical)" if full_mode else ""))
    filings = get_recent_filings()
    if len(filings) < 2:
        print(f"ERROR: only found {len(filings)} filings, need 2")
        sys.exit(1)

    with open(DATA_PATH, "r") as f:
        data = json.load(f)

    if full_mode:
        return main_full(filings, data)

    # --- Normal mode (unchanged behavior) ---
    cur_f, prev_f = filings[0], filings[1]

    print(f"  Latest: {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_info = find_info_table_xml(cur_f["accession"], cur_f["accessionDashed"])
    prev_info = find_info_table_xml(prev_f["accession"], prev_f["accessionDashed"])

    cur_xml = sec_fetch(cur_info)
    prev_xml = sec_fetch(prev_info)
    cur_holdings = parse_holdings(cur_xml)
    prev_holdings = parse_holdings(prev_xml)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in cur_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"] = p.get("value", 0)

    total = sum(h["value"] for h in cur_holdings)
    prev_total = sum(h["value"] for h in prev_holdings)

    data["current"] = {
        "quarter": quarter_label(cur_f["reportDate"]),
        "filingDate": cur_f["filingDate"],
        "periodEnd": cur_f["reportDate"],
        "totalValue": total,
        "holdings": cur_holdings,
        "prevQuarter": quarter_label(prev_f["reportDate"]),
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    q_label = quarter_label(cur_f["reportDate"])
    if q_label not in data["history"]["quarters"]:
        data["history"]["quarters"].append(q_label)
        data["history"]["values"].append(round(total / 1_000_000))

    save_data(data)
    print(f"Updated: {len(cur_holdings)} holdings, ${total:,} total")


def main_full(filings: list[dict], data: dict):
    """Fetch ALL historical 13F filings and store per-quarter holdings."""
    # Reverse so oldest first
    filings_sorted = list(reversed(filings))
    print(f"Found {len(filings_sorted)} total filings to process.")

    # Ensure history structure exists
    if "history" not in data:
        data["history"] = {"quarters": [], "values": [], "holdings": {}}
    if "holdings" not in data["history"]:
        data["history"]["holdings"] = {}

    existing_quarters = set(data["history"]["quarters"])
    new_quarters = 0
    skipped = 0

    for i, f in enumerate(filings_sorted):
        q_label = quarter_label(f["reportDate"])

        if q_label in existing_quarters:
            skipped += 1
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label} (already in history)")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label} (filed {f['filingDate']})...")
        try:
            holdings, total = fetch_and_parse_filing(f)
            # Add prevShares/prevValue from the previous quarter in the sorted list
            if i > 0:
                prev_q = quarter_label(filings_sorted[i - 1]["reportDate"])
                prev_holdings = data["history"]["holdings"].get(prev_q, [])
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
            print(f"    -> {len(holdings)} holdings, ${total:,} total")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    # Also update current with the latest filing
    latest = filings[0]
    latest_holdings, latest_total = fetch_and_parse_filing(latest)
    prev_f = filings[1]
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
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Update latest quarter in history too if not already there
    q_label = quarter_label(latest["reportDate"])
    if q_label not in data["history"]["quarters"]:
        data["history"]["quarters"].append(q_label)
        data["history"]["values"].append(round(latest_total / 1_000_000))
    # Always refresh holdings for latest quarter
    data["history"]["holdings"][q_label] = latest_holdings

    save_data(data)
    print(f"\nDone: {new_quarters} new quarters fetched, {skipped} skipped.")
    print(f"Total quarters in history: {len(data['history']['quarters'])}")


if __name__ == "__main__":
    main()
