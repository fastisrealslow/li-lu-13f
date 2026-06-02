#!/usr/bin/env python3
"""Fetch Aquamarine Capital Management (Guy Spier) 13F from SEC EDGAR and update spier.json.

CIK: 0001404599
Uses only stdlib — no pip install needed.

Usage:
  python3 fetch_13f_spier.py            # Normal mode: latest 2 quarters only
  python3 fetch_13f_spier.py --full     # Full mode: ALL historical filings
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CIK = "1404599"
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "spier.json")
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

TICKER_MAP = {
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B",
    "BERKSHIRE HATHAWAY IN": "BRK.B",
    "APPLE INC": "AAPL",
    "BANK OF AMERICA CORP": "BAC",
    "AMERICAN EXPRESS CO": "AXP",
    "COCA COLA CO": "KO",
    "CHEVRON CORP NEW": "CVX",
    "OCCIDENTAL PETE CORP": "OXY",
    "DAVITA INC": "DVA",
    "DAVITA HEALTHCARE PARTNERS INC": "DVA",
    "MARKEL GROUP INC": "MKL",
    "MARKEL CORP": "MKL",
    "WALMART INC": "WMT",
    "MASTERCARD INC": "MA",
    "VISA INC": "MA",
    "VISA INC": "V",
    "UNITEDHEALTH GROUP INC": "UNH",
    "UNITED HEALTH GROUP INC": "UNH",
    "JOHNSON & JOHNSON": "JNJ",
    "PROCTER & GAMBLE CO": "PG",
    "PROCTER AND GAMBLE CO": "PG",
    "COSTCO WHOLESALE CORP": "COST",
    "MICROSOFT CORP": "MSFT",
    "ALPHABET INC": "GOOGL",
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    "META PLATFORMS INC": "META",
    "FACEBOOK INC": "META",
    "NVIDIA CORPORATION": "NVDA",
    "AMAZON COM INC": "AMZN",
    "AMAZON.COM, INC.": "AMZN",
    "HOME DEPOT INC": "HD",
    "THE HOME DEPOT, INC.": "HD",
    "MERCK & CO INC": "MRK",
    "ABBVIE INC": "ABBV",
    "ELI LILLY & CO": "LLY",
    "ELI LILLY": "LLY",
    "ALTRIA GROUP INC": "MO",
    "PHILIP MORRIS INTL INC": "PM",
    "GENERAL REINSURANCE CORPORATION": "BRK.B",
    "CHARLES SCHWAB CORP": "SCHW",
    "SCHWAB CHARLES CORP": "SCHW",
    "JPMORGAN CHASE & CO": "JPM",
    "WELLS FARGO & CO": "WFC",
    "U S BANCORP DEL": "USB",
    "PNC FINL SVCS GROUP INC": "PNC",
    "MORGAN STANLEY": "MS",
    "GOLDMAN SACHS GROUP INC": "GS",
    "BLACKROCK INC": "BLK",
    "S&P GLOBAL INC": "SPGI",
    "MOODYS CORP": "MCO",
    "AON PLC": "AON",
    "CHUBB LIMITED": "CB",
    "TRAVELERS COS INC": "TRV",
    "ALLSTATE CORP": "ALL",
    "LOEWS CORP": "L",
    "BROOKFIELD CORP": "BN",
    "BROOKFIELD ASSET MGMT LTD": "BN",
    "FAIRFAX FINL HOLDINGS INC": "FFH",
    "FAIRFAX FINANCIAL HOLDINGS": "FFH",
    "MARKEL GROUP INC": "MKL",
    "ALLEGIANT TRAVEL CO": "ALGT",
    "WALT DISNEY CO": "DIS",
    "COMCAST CORP NEW": "CMCSA",
    "NETFLIX INC": "NFLX",
    "TAKE TWO INTERACTIVE SOFTWARE": "TTWO",
    "TAKE-TWO INTERACTIVE SOFTWARE": "TTWO",
    "ACTIVISION BLIZZARD INC": "ATVI",
    "ELECTRONIC ARTS INC": "EA",
    "CISCO SYSTEMS INC": "CSCO",
    "INTEL CORP": "INTC",
    "ORACLE CORP": "ORCL",
    "ADOBE INC": "ADBE",
    "INTUITIVE SURGICAL INC": "ISRG",
    "DANAHER CORP": "DHR",
    "THERMO FISHER SCIENTIFIC INC": "TMO",
    "SYNOPSYS INC": "SNPS",
    "CADENCE DESIGN SYSTEMS INC": "CDNS",
    "APPLIED MATERIALS INC": "AMAT",
    "LAM RESEARCH CORP": "LRCX",
    "TEXAS INSTRUMENTS INC": "TXN",
    "ANALOG DEVICES INC": "ADI",
    "NXP SEMICONDUCTORS N V": "NXPI",
    "MICRON TECHNOLOGY INC": "MU",
    "QUALCOMM INC": "QCOM",
    "BROADCOM INC": "AVGO",
    "ADVANCED MICRO DEVICES INC": "AMD",
    "ADVANCED MICRO DEVICES": "AMD",
    "PALO ALTO NETWORKS INC": "PANW",
    "CROWDSTRIKE HOLDINGS INC": "CRWD",
    "FORTINET INC": "FTNT",
    "ZSCALER INC": "ZS",
    "CLOUDFLARE INC": "NET",
    "SNOWFLAKE INC": "SNOW",
    "MONGODB INC": "MDB",
    "DATADOG INC": "DDOG",
    "PALANTIR TECHNOLOGIES INC": "PLTR",
    "SERVICENOW INC": "NOW",
    "WORKDAY INC": "WDAY",
    "SALESFORCE INC": "CRM",
    "INTUIT INC": "INTU",
    "BLOCK INC": "SQ",
    "SQUARE INC": "SQ",
    "PAYPAL HLDGS INC": "PYPL",
    "ADYEN N V": "ADYEY",
    "VISA INC": "V",
    "MASTERCARD INC": "MA",
    "FISERV INC": "FI",
    "FIDELITY NATIONAL INFORMATION SVCS": "FIS",
    "GLOBAL PAYMENTS INC": "GPN",
    "WEX INC": "WEX",
    "STONECO LTD": "STNE",
    "NU HOLDINGS LTD": "NU",
    "MELI MERCADOLIBRE INC": "MELI",
    "MERCADO LIBRE INC": "MELI",
    "SEA LTD": "SE",
    "PDD HOLDINGS INC": "PDD",
    "ALIBABA GROUP HLDG LTD": "BABA",
    "JD.COM INC": "JD",
    "JD COM INC": "JD",
    "TENCENT HLDGS LTD": "TCEHY",
    "TENCENT MUSIC ENTMT GROUP": "TME",
    "NETEASE INC": "NTES",
    "BAIDU INC": "BIDU",
    "BILIBILI INC": "BILI",
    "NIO INC": "NIO",
    "LI AUTO INC": "LI",
    "XPENG INC": "XPEV",
    "BYD CO LTD": "BYDDY",
    "PETROCHINA CO LTD": "PTR",
    "CHINA PETROLEUM & CHEMICAL": "SNP",
    "CNOOC LTD": "CEO",
    "SEMPRA": "SRE",
    "ENBRIDGE INC": "ENB",
    "TC ENERGY CORP": "TRP",
    "TRANSCANADA CORP": "TRP",
    "ENTERPRISE PRODS PARTNERS L P": "EPD",
    "ENERGY TRANSFER LP": "ET",
    "KINDER MORGAN INC DEL": "KMI",
    "WILLIAMS COS INC": "WMB",
    "ONEOK INC NEW": "OKE",
    "PLAINS GP HOLDINGS LP": "PAGP",
    "MPLX LP": "MPLX",
    "EXXON MOBIL CORP": "XOM",
    "CHEVRON CORP": "CVX",
    "CONOCOPHILLIPS": "COP",
    "CONOCO PHILLIPS": "COP",
    "OCCIDENTAL PETE CORP": "OXY",
    "PHILLIPS 66": "PSX",
    "VALERO ENERGY CORP": "VLO",
    "MARATHON PETE CORP": "MPC",
    "DIAMONDBACK ENERGY INC": "FANG",
    "DEVON ENERGY CORP NEW": "DVN",
    "EOG RESOURCES INC": "EOG",
    "COTERRA ENERGY INC": "CTRA",
    "PIONEER NATURAL RESOURCES CO": "PXD",
    "HALLIBURTON CO": "HAL",
    "SCHLUMBERGER LTD": "SLB",
    "BAKER HUGHES CO": "BKR",
}

SECTORS = {
    "BRK.B": "综合金融", "AAPL": "科技", "BAC": "金融/银行", "AXP": "金融",
    "KO": "消费", "CVX": "能源", "OXY": "能源", "DVA": "医药", "MKL": "金融服务",
    "WMT": "消费", "MA": "金融服务", "V": "金融服务", "UNH": "保险",
    "JNJ": "医药", "PG": "消费", "COST": "消费", "MSFT": "科技",
    "GOOGL": "互联网", "GOOG": "互联网", "META": "社交", "NVDA": "半导体",
    "AMZN": "电商", "HD": "消费", "MRK": "医药", "ABBV": "医药",
    "LLY": "医药", "MO": "消费", "PM": "消费", "SCHW": "金融服务",
    "JPM": "金融/银行", "WFC": "金融/银行", "USB": "金融/银行", "PNC": "金融/银行",
    "MS": "金融服务", "GS": "金融服务", "BLK": "金融服务", "SPGI": "金融服务",
    "MCO": "金融服务", "AON": "金融服务", "CB": "保险", "TRV": "保险",
    "ALL": "保险", "L": "综合金融", "BN": "金融服务", "FFH": "金融服务",
    "ALGT": "消费", "DIS": "娱乐", "CMCSA": "娱乐", "NFLX": "娱乐",
    "TTWO": "游戏", "ATVI": "游戏", "EA": "游戏", "CSCO": "科技",
    "INTC": "半导体", "ORCL": "科技", "ADBE": "科技", "ISRG": "医药",
    "DHR": "医药", "TMO": "医药", "SNPS": "半导体", "CDNS": "半导体",
    "AMAT": "半导体", "LRCX": "半导体", "TXN": "半导体", "ADI": "半导体",
    "NXPI": "半导体", "MU": "半导体", "QCOM": "半导体", "AVGO": "半导体",
    "AMD": "半导体", "PANW": "网络安全", "CRWD": "网络安全", "FTNT": "网络安全",
    "ZS": "网络安全", "NET": "科技", "SNOW": "科技", "MDB": "科技",
    "DDOG": "科技", "PLTR": "科技", "NOW": "科技", "WDAY": "科技",
    "CRM": "科技", "INTU": "科技", "SQ": "金融服务", "PYPL": "金融服务",
    "ADYEY": "金融服务", "FI": "金融服务", "FIS": "金融服务", "GPN": "金融服务",
    "WEX": "金融服务", "STNE": "金融服务", "NU": "金融服务", "MELI": "电商",
    "SE": "电商", "PDD": "电商", "BABA": "电商", "JD": "电商",
    "TCEHY": "社交", "TME": "娱乐", "NTES": "游戏", "BIDU": "互联网",
    "BILI": "社交", "NIO": "汽车/新能源", "LI": "汽车/新能源", "XPEV": "汽车/新能源",
    "BYDDY": "汽车/新能源", "PTR": "能源", "SNP": "能源", "CEO": "能源",
    "SRE": "公用事业", "ENB": "能源", "TRP": "能源", "EPD": "能源",
    "ET": "能源", "KMI": "能源", "WMB": "能源", "OKE": "能源",
    "PAGP": "能源", "MPLX": "能源", "XOM": "能源", "COP": "能源",
    "PSX": "能源", "VLO": "能源", "MPC": "能源", "FANG": "能源",
    "DVN": "能源", "EOG": "能源", "CTRA": "能源", "PXD": "能源",
    "HAL": "能源", "SLB": "能源", "BKR": "能源",
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
    print("Fetching Guy Spier 13F..." + (" (FULL MODE)" if full_mode else ""))
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
                "manager": "Aquamarine Capital Management, LLC",
                "managerCIK": "0001404599",
                "notablePeople": ["Guy Spier"],
                "lastUpdated": "",
            },
            "current": {},
            "history": {"quarters": [], "values": [], "holdings": {}},
        }

    if full_mode:
        return main_full(filings, data)

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
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label} (already)")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label}...")
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
            print(f"    -> {len(holdings)} holdings, ${total:,}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    # Update current with latest
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
    print(f"\nDone: {new_quarters} new quarters, {skipped} skipped.")
    print(f"Total quarters: {len(data['history']['quarters'])}")


if __name__ == "__main__":
    main()
