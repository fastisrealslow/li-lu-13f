#!/usr/bin/env python3
"""Fetch Akre Capital Management (Chuck Akre) + Brave Warrior Advisors (Glenn Greenberg)
13F from SEC EDGAR and generate akre.json / greenberg.json.

CIKs: Akre=0001112520, Greenberg=0001553733
Uses only stdlib — no pip install needed.
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
BASE = os.path.dirname(os.path.abspath(__file__))
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

CONFIG = {
    "akre": {
        "cik": "1112520",
        "manager": "Akre Capital Management, LLC",
        "people": ["Chuck Akre"],
        "path": os.path.join(BASE, "akre.json"),
    },
    "greenberg": {
        "cik": "1553733",
        "manager": "Brave Warrior Advisors, LLC",
        "people": ["Glenn Greenberg"],
        "path": os.path.join(BASE, "greenberg.json"),
    },
}

# Common ticker map
TICKER_MAP = {
    "APPLE INC": "AAPL", "MICROSOFT CORP": "MSFT", "AMAZON COM INC": "AMZN",
    "ALPHABET INC": "GOOG", "NVIDIA CORPORATION": "NVDA", "META PLATFORMS INC": "META",
    "TESLA INC": "TSLA", "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B", "JPMORGAN CHASE & CO": "JPM",
    "VISA INC": "V", "MASTERCARD INCORPORATED": "MA", "MASTERCARD INC": "MA",
    "COSTCO WHSL CORP NEW": "COST", "COSTCO WHOLESALE CORP": "COST",
    "HOME DEPOT INC": "HD", "PROCTER AND GAMBLE CO": "PG",
    "PROCTER & GAMBLE CO": "PG", "JOHNSON & JOHNSON": "JNJ",
    "UNITEDHEALTH GROUP INC": "UNH", "WALMART INC": "WMT",
    "EXXON MOBIL CORP": "XOM", "CHEVRON CORP NEW": "CVX",
    "BANK AMERICA CORP": "BAC", "BANK OF AMERICA CORP": "BAC",
    "WELLS FARGO CO NEW": "WFC", "MORGAN STANLEY": "MS",
    "GOLDMAN SACHS GROUP INC": "GS", "AMERICAN EXPRESS CO": "AXP",
    "AMERICAN TOWER CORP NEW": "AMT", "AMERICAN TOWER CORP": "AMT",
    "CROWN CASTLE INC": "CCI", "SBA COMMUNICATIONS CORP NEW": "SBAC",
    "MOODYS CORP": "MCO", "S&P GLOBAL INC": "SPGI",
    "MSCI INC": "MSCI", "VERISK ANALYTICS INC": "VRSK",
    "FACTSET RESH SYS INC": "FDS", "FACTSET RESEARCH SYSTEMS INC": "FDS",
    "MASTERCARD INCORPORATED": "MA", "VISA INC": "V",
    "THERMO FISHER SCIENTIFIC INC": "TMO", "DANAHER CORPORATION": "DHR",
    "INTUITIVE SURGICAL INC": "ISRG", "STRYKER CORPORATION": "SYK",
    "BECTON DICKINSON & CO": "BDX", "ZOETIS INC": "ZTS",
    "ADOBE INC": "ADBE", "SALESFORCE INC": "CRM", "ORACLE CORP": "ORCL",
    "SERVICENOW INC": "NOW", "INTUIT": "INTU",
    "ALPHABET INC": "GOOG", "META PLATFORMS INC": "META",
    "NETFLIX INC": "NFLX", "WALT DISNEY CO": "DIS",
    "COMCAST CORP NEW": "CMCSA", "CHARTER COMMUNICATIONS INC": "CHTR",
    "T-MOBILE US INC": "TMUS", "VERIZON COMMUNICATIONS INC": "VZ",
    "UNION PAC CORP": "UNP", "NORFOLK SOUTHN CORP": "NSC",
    "CANADIAN PACIFIC KANSAS CITY": "CP", "CANADIAN NATL RY CO": "CNI",
    "DEERE & CO": "DE", "CATERPILLAR INC": "CAT",
    "BOEING CO": "BA", "LOCKHEED MARTIN CORP": "LMT",
    "RAYTHEON TECHNOLOGIES CORP": "RTX", "NORTHROP GRUMMAN CORP": "NOC",
    "GENERAL DYNAMICS CORP": "GD", "TRANSDIGM GROUP INC": "TDG",
    "COCA COLA CO": "KO", "PEPSICO INC": "PEP",
    "PHILIP MORRIS INTL INC": "PM", "ALTRIA GROUP INC": "MO",
    "MONDELEZ INTL INC": "MDLZ", "KEURIG DR PEPPER INC": "KDP",
    "MCCORMICK & CO INC": "MKC", "HERSHEY CO": "HSY",
    "CONSTELLATION BRANDS INC": "STZ", "BROWN FORMAN CORP": "BF.B",
    "DIAGEO PLC": "DEO", "ESTEE LAUDER COMPANIES INC": "EL",
    "LOREAL CO": "LRLCY", "L'OREAL": "LRLCY",
    "NIKE INC": "NKE", "TJX COS INC NEW": "TJX",
    "ROSS STORES INC": "ROST", "DOLLAR TREE INC": "DLTR",
    "DOLLAR GEN CORP NEW": "DG", "O REILLY AUTOMOTIVE INC": "ORLY",
    "O'REILLY AUTOMOTIVE INC": "ORLY", "AUTOMATIC DATA PROCESSING INC": "ADP",
    "PAYCOM SOFTWARE INC": "PAYC", "PAYCHEX INC": "PAYX",
    "COPART INC": "CPRT", "CARMAX INC": "KMX",
    "STARBUCKS CORP": "SBUX", "MCDONALDS CORP": "MCD",
    "CHIPOTLE MEXICAN GRILL INC": "CMG", "YUM BRANDS INC": "YUM",
    "DOMINOS PIZZA INC": "DPZ", "HILTON WORLDWIDE HLDGS INC": "HLT",
    "MARRIOTT INTL INC NEW": "MAR", "AIRBNB INC": "ABNB",
    "BOOKING HOLDINGS INC": "BKNG", "EXPEDIA GROUP INC": "EXPE",
    # Akre-specific (based on known holdings)
    "AMERICAN TOWER CORP": "AMT",
    "MASTERCARD INC": "MA",
    "MOODYS CORP": "MCO",
    "S&P GLOBAL INC": "SPGI",
    "VISA INC": "V",
    "ALPHABET INC CL A": "GOOGL",
    "DANAHER CORP": "DHR",
    "THERMO FISHER SCIENTIFIC INC": "TMO",
    "ZOETIS INC": "ZTS",
    "STRYKER CORP": "SYK",
    "INTUITIVE SURGICAL": "ISRG",
    "BECTON DICKINSON": "BDX",
    "CONSTELLATION BRANDS INC": "STZ",
    "COSTCO WHSL CORP": "COST",
    "FACTSET RESH SYS INC": "FDS",
    "MSCI INC": "MSCI",
    "VERISK ANALYTICS INC": "VRSK",
    "AUTOMATIC DATA PROCESSING INC": "ADP",
    "O REILLY AUTOMOTIVE INC": "ORLY",
    "ROSS STORES INC": "ROST",
    "TJX COS INC": "TJX",
    "DOLLAR TREE INC": "DLTR",
    # Greenberg-specific
    "APOLLO GLOBAL MGMT INC": "APO",
    "KKR & CO INC": "KKR",
    "BLACKSTONE INC": "BX",
    "CARLYLE GROUP INC": "CG",
    "ARES MANAGEMENT CORPORATION": "ARES",
    "BLUE OWL CAPITAL INC": "OWL",
    "JPMORGAN CHASE & CO": "JPM",
    "BANK OF AMERICA CORP": "BAC",
    "WELLS FARGO & CO": "WFC",
    "CITIGROUP INC": "C",
    "GOLDMAN SACHS GROUP INC": "GS",
    "MORGAN STANLEY": "MS",
    "CHARLES SCHWAB CORP": "SCHW",
    "SCHWAB CHARLES CORP": "SCHW",
    "INTERACTIVE BROKERS GROUP INC": "IBKR",
    "CME GROUP INC": "CME",
    "INTERCONTINENTAL EXCHANGE INC": "ICE",
    "NASDAQ INC": "NDAQ",
    "LONDON STOCK EXCHANGE GROUP": "LNSTY",
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B",
    "ANTHEM INC": "ELV",
    "ELEVANCE HEALTH INC": "ELV",
    "CIGNA CORP": "CI",
    "UNITEDHEALTH GROUP INC": "UNH",
    "HCA HEALTHCARE INC": "HCA",
    "MCKESSON CORP": "MCK",
    "CENCORA INC": "COR",
    "CARDINAL HEALTH INC": "CAH",
    "ALPHABET INC": "GOOG", "APPLE INC": "AAPL",
    "MICROSOFT CORP": "MSFT", "META PLATFORMS INC": "META",
    "AMAZON COM INC": "AMZN", "NVIDIA CORP": "NVDA",
    "NVIDIA CORPORATION": "NVDA",
    # Akre-specific missing
    "BROOKFIELD CORP": "BN",
    "KKR & CO L P DEL": "KKR",
    "ROPER TECHNOLOGIES INC": "ROP",
    "COSTAR GROUP INC": "CSGP",
    "FAIR ISAAC CORP": "FICO",
    "OREILLY AUTOMOTIVE INC": "ORLY",
    "O REILLY AUTOMOTIVE INC": "ORLY",
    "CCC INTELLIGENT SOLUTIONS HL": "CCCS",
    "GOOSEHEAD INS INC": "GSHD",
    "SOPHIA GENETICS SA": "SOPH",
    "PERIMETER SOLUTIONS INC": "PRM",
    # Greenberg-specific missing
    "TD SYNNEX CORPORATION": "SNX",
    "ONEMAIN HLDGS INC": "OMF",
    "ICON PLC": "ICLR",
    "ELEVANCE HEALTH INC FORMERLY": "ELV",
    "AUTONATION INC": "AN",
    "SLM CORP": "SLM",
    "MILLROSE PPTYS INC": "MRP",
    "PRIMERICA INC": "PRI",
    "LENNAR CORP": "LEN",
    "BUILDERS FIRSTSOURCE INC": "BLDR",
    "MPLX LP": "MPLX",
    "CAPITAL ONE FINL CORP": "COF",
    "RYANAIR HOLDINGS PLC": "RYAAY",
    "FIDELITY NATL FINL INC": "FNF",
    "F&G ANNUITIES & LIFE INC": "FG",
    "D R HORTON INC": "DHI",
    "ANTERO MIDSTREAM CORP": "AM",
    "SUNBELT RENTALS HOLDINGS INC": "R",
    "PROGRESSIVE CORP": "PGR",
    "APPLIED MATLS INC": "AMAT",
    "FIRST AMERN FINL CORP": "FAF",
    "ENERGY TRANSFER L P": "ET",
}

# Class-specific resolution
TICKER_CLASS_MAP = {
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    ("ALPHABET INC CL A", True): "GOOGL",
    ("ALPHABET INC CL C", False): "GOOG",
    ("BROWN FORMAN CORP", True): "BF.A",
    ("BROWN FORMAN CORP", False): "BF.B",
}

SECTORS = {
    "AAPL": "科技", "MSFT": "科技", "AMZN": "电商", "GOOG": "互联网",
    "GOOGL": "互联网", "NVDA": "半导体", "META": "社交", "TSLA": "汽车",
    "BRK.B": "综合金融", "JPM": "金融/银行", "V": "金融服务",
    "MA": "金融服务", "COST": "消费", "HD": "消费", "PG": "消费",
    "JNJ": "医药", "UNH": "保险", "WMT": "消费", "XOM": "能源",
    "CVX": "能源", "BAC": "金融/银行", "WFC": "金融/银行", "MS": "金融服务",
    "GS": "金融服务", "AXP": "金融服务", "AMT": "通讯", "CCI": "通讯",
    "SBAC": "通讯", "MCO": "金融服务", "SPGI": "金融服务",
    "MSCI": "金融服务", "VRSK": "科技", "FDS": "科技",
    "TMO": "医药", "DHR": "多元工业", "ISRG": "医药", "SYK": "医药",
    "BDX": "医药", "ZTS": "医药", "ADBE": "科技", "CRM": "科技",
    "ORCL": "科技", "NOW": "科技", "INTU": "科技",
    "NFLX": "娱乐", "DIS": "娱乐", "CMCSA": "娱乐", "CHTR": "娱乐",
    "TMUS": "通讯", "VZ": "通讯", "UNP": "工业", "NSC": "工业",
    "CP": "工业", "CNI": "工业", "DE": "工业", "CAT": "工业",
    "BA": "工业", "LMT": "工业", "RTX": "工业", "NOC": "工业",
    "GD": "工业", "TDG": "工业", "KO": "消费", "PEP": "消费",
    "PM": "消费", "MO": "消费", "MDLZ": "消费", "KDP": "消费",
    "MKC": "消费", "HSY": "消费", "STZ": "消费", "BF.B": "消费",
    "DEO": "消费", "EL": "消费", "LRLCY": "消费", "NKE": "消费",
    "TJX": "消费", "ROST": "消费", "DLTR": "消费", "DG": "消费",
    "ORLY": "消费", "ADP": "科技", "PAYC": "科技", "PAYX": "科技",
    "CPRT": "科技", "KMX": "消费", "SBUX": "消费", "MCD": "消费",
    "CMG": "消费", "YUM": "消费", "DPZ": "消费", "HLT": "消费",
    "MAR": "消费", "ABNB": "消费", "BKNG": "消费", "EXPE": "消费",
    "APO": "金融服务", "KKR": "金融服务", "BX": "金融服务",
    "CG": "金融服务", "ARES": "金融服务", "OWL": "金融服务",
    "C": "金融/银行", "SCHW": "金融服务", "IBKR": "金融服务",
    "CME": "金融服务", "ICE": "金融服务", "NDAQ": "金融服务",
    "LNSTY": "金融服务", "ELV": "保险", "CI": "保险",
    "HCA": "医药", "MCK": "医药", "COR": "医药", "CAH": "医药",
    # Akre-specific
    "BN": "金融服务", "ROP": "多元工业", "CSGP": "科技", "FICO": "科技",
    "CCCS": "科技", "GSHD": "保险", "SOPH": "医药", "PRM": "工业",
    # Greenberg-specific
    "SNX": "科技", "OMF": "金融服务", "ICLR": "医药", "AN": "消费",
    "SLM": "金融服务", "MRP": "金融服务", "PRI": "保险",
    "BLDR": "工业", "MPLX": "能源", "RYAAY": "消费", "FNF": "金融服务",
    "FG": "保险", "DHI": "工业", "AM": "能源", "R": "工业",
    "PGR": "保险", "AMAT": "半导体", "FAF": "金融服务", "ET": "能源",
}


def sec_fetch(path: str) -> bytes:
    url = f"https://www.sec.gov{path}" if path.startswith("/") else f"https://data.sec.gov/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def get_recent_filings(cik: str) -> list[dict]:
    data = json.loads(sec_fetch(f"submissions/CIK{cik.zfill(10)}.json"))
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


def find_info_table_xml(cik: str, accession: str, accession_dashed: str) -> str:
    html = sec_fetch(
        f"/Archives/edgar/data/{cik}/{accession}/{accession_dashed}-index.html"
    ).decode("utf-8", errors="replace")
    pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+\.xml)</a>\s*</td>\s*<td[^>]*>\s*INFORMATION TABLE'
    for m in re.finditer(pattern, html, re.IGNORECASE):
        href = m.group(1)
        if "xslForm13F" not in href:
            return href
    m = re.search(r"(\d{2})(\d)(\d)$", accession)
    if m:
        return f"/Archives/edgar/data/{cik}/{accession}/13fhciq{m.group(2)}{m.group(3)}.xml"
    raise RuntimeError("Cannot find INFOTABLE XML")


def resolve_ticker(name: str, cls: str) -> str:
    n = name.strip()
    is_a = "CL A" in (cls or "").upper()

    class_key = (n, is_a)
    if class_key in TICKER_CLASS_MAP:
        return TICKER_CLASS_MAP[class_key]

    if n in TICKER_MAP:
        return TICKER_MAP[n]

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
        shares = int(shares_el.text) if shares_el is not None and shares_el.text else 0
        value = int(val_el.text) if val_el is not None and val_el.text else 0
        ticker = resolve_ticker(name_val, cls_val)
        holdings.append({
            "ticker": ticker,
            "name": name_val,
            "shares": shares,
            "value": value,
            "sector": SECTORS.get(ticker, "其他"),
        })

    # SEC 13F values are in thousands ($1,000 units)
    total_val = sum(h["value"] for h in holdings)
    if total_val < 100_000_000:
        for h in holdings:
            h["value"] *= 1000
        total_val = sum(h["value"] for h in holdings)

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


def save_data(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def process_investor(key: str, config: dict, full_mode: bool):
    print(f"\n{'='*60}")
    print(f"Processing {key.upper()}: {config['manager']}")
    print(f"CIK: {config['cik']}")
    print(f"{'='*60}")

    cik = config["cik"]
    filings = get_recent_filings(cik)
    if len(filings) < 2:
        print(f"ERROR: only found {len(filings)} filings, need ≥2")
        return

    if os.path.exists(config["path"]):
        with open(config["path"], "r") as f:
            data = json.load(f)
    else:
        data = {
            "meta": {
                "manager": config["manager"],
                "managerCIK": config["cik"].zfill(10),
                "notablePeople": config["people"],
                "lastUpdated": "",
            },
            "current": {},
            "history": {"quarters": [], "values": [], "holdings": {}},
        }

    if full_mode:
        return process_full(key, config, filings, data)

    # Quick mode: latest 2 quarters
    cur_f, prev_f = filings[0], filings[1]
    print(f"  Latest: {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_xml = sec_fetch(find_info_table_xml(cik, cur_f["accession"], cur_f["accessionDashed"]))
    prev_xml = sec_fetch(find_info_table_xml(cik, prev_f["accession"], prev_f["accessionDashed"]))
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

    save_data(config["path"], data)
    print(f"Updated: {len(cur_holdings)} holdings, ${total:,.0f} total")


def process_full(key, config, filings, data):
    cik = config["cik"]
    filings_sorted = list(reversed(filings))
    print(f"Found {len(filings_sorted)} total filings to process.")

    existing_quarters = set(data["history"]["quarters"])
    all_fetched = {}
    new_quarters = 0
    skipped = 0

    for i, f in enumerate(filings_sorted):
        q_label = quarter_label(f["reportDate"])
        if q_label in existing_quarters:
            skipped += 1
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label}")
            try:
                xml_bytes = sec_fetch(find_info_table_xml(cik, f["accession"], f["accessionDashed"]))
                holdings = parse_holdings(xml_bytes)
                all_fetched[q_label] = holdings
            except Exception as e:
                print(f"    -> ERROR fetching skipped: {e}")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label}...")
        try:
            xml_bytes = sec_fetch(find_info_table_xml(cik, f["accession"], f["accessionDashed"]))
            holdings = parse_holdings(xml_bytes)
            all_fetched[q_label] = holdings

            prev_q = None
            for j in range(i - 1, -1, -1):
                pql = quarter_label(filings_sorted[j]["reportDate"])
                if pql in all_fetched:
                    prev_q = pql
                    break

            if prev_q:
                prev_map = {h["ticker"]: h for h in all_fetched[prev_q]}
                for h in holdings:
                    p = prev_map.get(h["ticker"], {})
                    h["prevShares"] = p.get("shares", 0)
                    h["prevValue"] = p.get("value", 0)
            else:
                for h in holdings:
                    h["prevShares"] = 0
                    h["prevValue"] = 0

            total = sum(h["value"] for h in holdings)
            data["history"]["quarters"].append(q_label)
            data["history"]["values"].append(round(total / 1_000_000))
            data["history"]["holdings"][q_label] = holdings
            new_quarters += 1
            print(f"    -> {len(holdings)} holdings, ${total:,.0f}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    latest = filings[0]
    latest_q = quarter_label(latest["reportDate"])
    if latest_q in all_fetched:
        latest_holdings = all_fetched[latest_q]
    else:
        latest_holdings = parse_holdings(sec_fetch(
            find_info_table_xml(cik, latest["accession"], latest["accessionDashed"])))

    prev_f = filings[1]
    prev_q = quarter_label(prev_f["reportDate"])
    if prev_q in all_fetched:
        prev_holdings = all_fetched[prev_q]
    else:
        prev_holdings = parse_holdings(sec_fetch(
            find_info_table_xml(cik, prev_f["accession"], prev_f["accessionDashed"])))

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in latest_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"] = p.get("value", 0)

    latest_total = sum(h["value"] for h in latest_holdings)
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

    save_data(config["path"], data)
    print(f"\nDone: {new_quarters} new quarters, {skipped} skipped.")
    print(f"Total quarters: {len(data['history']['quarters'])}")
    print(f"Current: {len(latest_holdings)} holdings, ${latest_total:,.0f}")


def main():
    full_mode = "--full" in sys.argv
    for key in ["akre", "greenberg"]:
        try:
            process_investor(key, CONFIG[key], full_mode)
        except Exception as e:
            print(f"\nFATAL ERROR for {key}: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()