#!/usr/bin/env python3
"""Fetch Dalal Street LLC (Mohnish Pabrai) 13F from SEC EDGAR and update pabrai_data.json.

CIK: 0001294614
Uses only stdlib — no pip install needed.

Usage:
  python3 fetch_13f_pabrai.py            # Normal mode: latest 2 quarters only
  python3 fetch_13f_pabrai.py --full     # Full mode: ALL historical filings
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CIK = "1549575"
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pabrai_data.json")
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

TICKER_MAP = {
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    "APPLE INC": "AAPL",
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "PDD HOLDINGS INC": "PDD",
    "NVIDIA CORPORATION": "NVDA",
    "WALT DISNEY CO": "DIS",
    "TESLA INC": "TSLA",
    "OCCIDENTAL PETE CORP": "OXY",
    "AMAZON COM INC": "AMZN",
    "MICROSOFT CORP": "MSFT",
    "META PLATFORMS INC": "META",
    "SERVISFIRST BANCSHARES INC": "SFBS",
    "WARRIOR MET COAL INC": "HCC",
    "TRANSOCEAN LTD": "RIG",
    "ALPHA METALLURGICAL RESOURCE": "ARLP",
    "CITIGROUP INC": "C",
    "GENERAL MOTORS CO": "GM",
    "BANK OF AMERICA CORP": "BAC",
    "CHESAPEAKE ENERGY CORP": "CHK",
    "GOLDMAN SACHS GROUP INC": "GS",
    "FREEPORT-MCMORAN INC": "FCX",
    ("ALPHABET INC", False): "GOOG",
    "S&P GLOBAL INC": "SPGI",
    "UNITEDHEALTH GROUP INC": "UNH",
    "VISA INC": "V",
    "JPMORGAN CHASE & CO": "JPM",
}

SECTORS = {
    "GOOGL": "互联网", "GOOG": "互联网", "AAPL": "科技",
    "BRK.B": "综合金融", "PDD": "电商", "NVDA": "半导体",
    "DIS": "娱乐", "TSLA": "汽车", "OXY": "能源",
    "AMZN": "电商", "MSFT": "科技", "META": "社交",
    "SFBS": "金融", "HCC": "煤炭", "RIG": "油气钻探",
    "ARLP": "煤炭", "C": "金融", "GM": "汽车",
    "BAC": "金融", "CHK": "油气", "GS": "金融",
    "FCX": "矿业", "SPGI": "金融服务", "UNH": "医疗",
    "V": "金融", "JPM": "金融",
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


def ticker(name: str, cls: str) -> str:
    n = name.strip()
    key = (n, "CL A" in (cls or ""))
    if key in TICKER_MAP:
        return TICKER_MAP[key]
    mapped = TICKER_MAP.get(n)
    if mapped:
        return mapped
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
    # Auto-detect value unit: SEC changed from kUSD to USD around 2022 Q4.
    # If avg value/shares < $1, values are in kUSD → scale ×1000.
    _valid = [h for h in holdings if h["shares"] > 0 and h["value"] > 0]
    if _valid:
        _avg = sum(h["value"] / h["shares"] for h in _valid) / len(_valid)
        if _avg < 1.0:
            for h in holdings:
                h["value"] *= 1000
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
    print("Fetching Pabrai 13F filings..." + (" (FULL MODE)" if full_mode else ""))
    filings = get_recent_filings()
    if len(filings) < 2:
        print(f"ERROR: only found {len(filings)} filings, need 2")
        sys.exit(1)

    # Create initial data structure if file doesn't exist
    if not os.path.exists(DATA_PATH):
        data = {"meta": {"name": "Mohnish Pabrai", "cik": CIK}, "current": {}, "history": {"quarters": [], "values": [], "holdings": {}}}
    else:
        with open(DATA_PATH, "r") as f:
            data = json.load(f)

    if full_mode:
        return main_full(filings, data)

    cur_f, prev_f = filings[0], filings[1]
    print(f"  Latest: {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_holdings, total = fetch_and_parse_filing(cur_f)
    prev_holdings, prev_total = fetch_and_parse_filing(prev_f)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in cur_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"] = p.get("value", 0)

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
    filings_sorted = list(reversed(filings))
    print(f"Found {len(filings_sorted)} total filings to process.")

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
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label} (cached)")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label} (filed {f['filingDate']})...")
        try:
            holdings, total = fetch_and_parse_filing(f)
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

    q_label = quarter_label(latest["reportDate"])
    if q_label not in data["history"]["quarters"]:
        data["history"]["quarters"].append(q_label)
        data["history"]["values"].append(round(latest_total / 1_000_000))
    data["history"]["holdings"][q_label] = latest_holdings

    save_data(data)
    print(f"\nDone: {new_quarters} new, {skipped} skipped.")


if __name__ == "__main__":
    main()
