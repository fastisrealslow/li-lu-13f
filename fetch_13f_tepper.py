#!/usr/bin/env python3
"""Fetch Appaloosa LP (David Tepper) 13F from SEC EDGAR and update tepper.json.

CIK: 0001656456
Uses only stdlib — no pip install needed.

Usage:
  python3 fetch_13f_tepper.py            # Normal mode: latest 2 quarters only
  python3 fetch_13f_tepper.py --full     # Full mode: ALL historical filings
"""

import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

CIK = "1656456"
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tepper.json")
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

TICKER_MAP = {
    "APPLE INC": "AAPL",
    "MICROSOFT CORP": "MSFT",
    "AMAZON COM INC": "AMZN",
    "ALPHABET INC": "GOOGL",
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    "META PLATFORMS INC": "META",
    "FACEBOOK INC": "META",
    "TESLA INC": "TSLA",
    "NVIDIA CORPORATION": "NVDA",
    "NVIDIA CORPORATION COMMON STOCK": "NVDA",
    "MICRON TECHNOLOGY INC": "MU",
    "TAIWAN SEMICONDUCTOR MANUFAC": "TSM",
    "VISTRA CORP": "VST",
    "NRG ENERGY INC": "NRG",
    "SANDISK CORP": "SNDK",
    "CORNING INC": "GLW",
    "WHIRLPOOL CORP": "WHR",
    "LAM RESEARCH CORP": "LRCX",
    "L3HARRIS TECHNOLOGIES INC": "LHX",
    "RTX CORPORATION": "RTX",
    "ASML HLDG NV": "ASML",
    "BALL CORP": "BALL",
    "ENERGY TRANSFER L P": "ET",
    "DEUTSCHE BK AG": "DB",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "KRANESHARES TRUST": "KWEB",
    "ISHARES INC": "IEMG",
    "PALANTIR TECHNOLOGIES INC": "PLTR",
    "NETFLIX INC": "NFLX",
    "SALESFORCE INC": "CRM",
    "SALESFORCE COM INC": "CRM",
    "TAKE-TWO INTERACTIVE SOFTWARE": "TTWO",
    "TAKE TWO INTERACTIVE SOFTWARE": "TTWO",
    "TAKE-TWO INTERACTIVE SOFTWAR": "TTWO",
    "COINBASE GLOBAL INC": "COIN",
    "COINBASE GLOBAL INC NEW": "COIN",
    "CARRIER GLOBAL CORPORATION": "CARR",
    "CARRIER GLOBAL CORPORATION COMMON": "CARR",
    "FREEPORT-MCMORAN INC": "FCX",
    "FREEPORT MCMORAN INC": "FCX",
    "NEXTERA ENERGY INC": "NEE",
    "BANK OF AMERICA CORP": "BAC",
    "JPMORGAN CHASE & CO": "JPM",
    "GOLDMAN SACHS GROUP INC": "GS",
    "MORGAN STANLEY": "MS",
    "CITIGROUP INC": "C",
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B",
    "VISA INC": "V",
    "MASTERCARD INC": "MA",
    "WALT DISNEY CO": "DIS",
    "DISNEY WALT CO": "DIS",
    "COMCAST CORP NEW": "CMCSA",
    "CHARLES SCHWAB CORP": "SCHW",
    "AMERICAN TOWER CORP NEW": "AMT",
    "AMAZON.COM, INC.": "AMZN",
    "ADVANCE AUTO PARTS INC": "AAP",
    "SPDR S&P 500 ETF TRUST": "SPY",
    "ISHARES RUSSELL 2000 ETF": "IWM",
    "INVESCO QQQ TRUST SERIES 1": "QQQ",
    "INVESCO QQQ TR": "QQQ",
    "VANGUARD S&P 500 ETF": "VOO",
    "PDD HOLDINGS INC": "PDD",
    "ALIBABA GROUP HLDG LTD": "BABA",
    "TENCENT HLDGS LTD": "TCEHY",
    "JD COM INC": "JD",
    "JD.COM INC": "JD",
    "NETEASE INC": "NTES",
    "BAIDU INC": "BIDU",
    "NIO INC": "NIO",
    "LI AUTO INC": "LI",
    "XPENG INC": "XPEV",
    "BILIBILI INC": "BILI",
    "SNOWFLAKE INC": "SNOW",
    "CROWDSTRIKE HOLDINGS INC": "CRWD",
    "CROWDSTRIKE HLDGS INC": "CRWD",
    "DELL TECHNOLOGIES INC": "DELL",
    "INTEL CORP": "INTC",
    "QUALCOMM INC": "QCOM",
    "BROADCOM INC": "AVGO",
    "ADVANCED MICRO DEVICES INC": "AMD",
    "AMD": "AMD",
    "CISCO SYSTEMS INC": "CSCO",
    "ORACLE CORP": "ORCL",
    "ADOBE INC": "ADBE",
    "INTUITIVE SURGICAL INC": "ISRG",
    "UNITEDHEALTH GROUP INC": "UNH",
    "ELI LILLY & CO": "LLY",
    "MERCK & CO INC": "MRK",
    "ABBVIE INC": "ABBV",
    "JOHNSON & JOHNSON": "JNJ",
    "PROCTER & GAMBLE CO": "PG",
    "COCA COLA CO": "KO",
    "PEPSICO INC": "PEP",
    "WALMART INC": "WMT",
    "COSTCO WHOLESALE CORP": "COST",
    "HOME DEPOT INC": "HD",
    "CHEVRON CORP NEW": "CVX",
    "EXXON MOBIL CORP": "XOM",
    "CONOCO PHILLIPS": "COP",
    "GENERAL ELEC CO": "GE",
    "HONEYWELL INTL INC": "HON",
    "BOEING CO": "BA",
    "LOCKHEED MARTIN CORP": "LMT",
    "RAYTHEON TECHNOLOGIES CORPORATION": "RTX",
    "NORTHROP GRUMMAN CORP": "NOC",
    "FEDEX CORP": "FDX",
    "UNITED PARCEL SERVICE INC": "UPS",
    "MCDONALDS CORP": "MCD",
    "STARBUCKS CORP": "SBUX",
    "TARGET CORP": "TGT",
    "LOWES COS INC": "LOW",
    "AMERICAN EXPRESS CO": "AXP",
    "BLACKROCK INC": "BLK",
    "CHARLES SCHWAB CORPORATION": "SCHW",
    "U S BANCORP DEL": "USB",
    "WELLS FARGO & CO": "WFC",
    "TRUIST FINL CORP": "TFC",
    "CAPITAL ONE FINANCIAL CORP": "COF",
    "DISCOVER FINL SVCS": "DFS",
    "S&P GLOBAL INC": "SPGI",
    "MOODYS CORP": "MCO",
    "INTERACTIVE BROKERS GROUP INC": "IBKR",
    "SCHWAB CHARLES CORP": "SCHW",
    "SERES THERAPEUTICS INC": "SAGE",
    "CENCORA INC": "COR",
    "MARKETAXESS HOLDINGS INC": "MKTX",
    "MONGODB INC": "MDB",
    "SEA LTD": "SE",
    "ACTIVISION BLIZZARD INC": "ATVI",
    "SOUTHERN CO": "SO",
    "PHYSICIANS RLTY TR": "DOC",
    "COSTAR GROUP INC": "CSGP",
    "CENTENE CORP": "CNC",
    "GENUINE PARTS CO": "GPC",
    "RENT-A-CENTER INC NEW": "RCII",
    "PULMONX CORP": "LUNG",
    "BRIGHT HORIZONS FAMILY SOL INC": "BFAM",
    "CHEGG INC": "CHGG",
    "UWM HOLDINGS CORPORATION": "UWMC",
    "LENDINGTREE INC NEW": "TREE",
    "JOYY INC": "YY",
    "INNODATA INC": "INOD",
    "TEMPUS AI INC": "TEM",
    "CIRCLE INTERNET GROUP INC": "CRCL",
    "ZOOMINFO TECHNOLOGIES INC": "ZI",
    "PALO ALTO NETWORKS INC": "PANW",
    "FORTINET INC": "FTNT",
    "ZSCALER INC": "ZS",
    "WORKDAY INC": "WDAY",
    "SERVICE NOW INC": "NOW",
    "SNAP INC": "SNAP",
    "SPOTIFY TECHNOLOGY S A": "SPOT",
    "ROKU INC": "ROKU",
    "PINTEREST INC": "PINS",
    "RIVIAN AUTOMOTIVE INC": "RIVN",
    "LUCID GROUP INC": "LCID",
    "FORD MTR CO": "F",
    "GENERAL MTRS CO": "GM",
    "STELLANTIS NV": "STLA",
    "GENERAL MOTORS CO": "GM",
    "SOUTHWEST AIRLS CO": "LUV",
    "DELTA AIR LINES INC DEL": "DAL",
    "AMERICAN AIRLS GROUP INC": "AAL",
    "UNITED AIRLS HLDGS INC": "UAL",
    "UBER TECHNOLOGIES INC": "UBER",
    "LYFT INC": "LYFT",
    "DOORDASH INC": "DASH",
    "BLOCK INC": "SQ",
    "SQUARE INC": "SQ",
    "PAYPAL HLDGS INC": "PYPL",
    "AFFIRM HLDGS INC": "AFRM",
    "ROBINHOOD MKTS INC": "HOOD",
    "SOFI TECHNOLOGIES INC": "SOFI",
    "NU HOLDINGS LTD": "NU",
    "MARATHON PETE CORP": "MPC",
    "VALERO ENERGY CORP": "VLO",
    "PHILLIPS 66": "PSX",
    "OCCIDENTAL PETE CORP": "OXY",
    "DIAMONDBACK ENERGY INC": "FANG",
    "COTERRA ENERGY INC": "CTRA",
    "DEVON ENERGY CORP NEW": "DVN",
    "PIONEER NATURAL RESOURCES CO": "PXD",
    "EOG RESOURCES INC": "EOG",
    "HALLIBURTON CO": "HAL",
    "SCHLUMBERGER LTD": "SLB",
    "BAKER HUGHES CO": "BKR",
    "KINDER MORGAN INC DEL": "KMI",
    "ENERGY TRANSFER LP": "ET",
    "WILLIAMS COS INC": "WMB",
    "ONEOK INC NEW": "OKE",
    "PLAINS ALL AMERN PIPELINE LP": "PAA",
    "ENTERPRISE PRODS PARTNERS L P": "EPD",
    "MPLX LP": "MPLX",
}

SECTORS = {
    "AAPL": "科技", "MSFT": "科技", "AMZN": "电商", "GOOGL": "互联网", "GOOG": "互联网",
    "META": "社交", "TSLA": "汽车/新能源", "NVDA": "半导体", "PLTR": "科技",
    "NFLX": "娱乐", "CRM": "科技", "TTWO": "游戏", "COIN": "金融服务",
    "CARR": "工业", "FCX": "能源", "NEE": "公用事业", "BAC": "金融/银行",
    "JPM": "金融/银行", "GS": "金融服务", "MS": "金融服务", "C": "金融/银行",
    "BRK.B": "综合金融", "V": "金融服务", "MA": "金融服务", "DIS": "娱乐",
    "CMCSA": "娱乐", "SCHW": "金融服务", "AMT": "房地产", "AAP": "消费",
    "SPY": "ETF", "IWM": "ETF", "QQQ": "ETF", "VOO": "ETF",
    "PDD": "电商", "BABA": "电商", "TCEHY": "社交", "JD": "电商",
    "NTES": "游戏", "BIDU": "互联网", "NIO": "汽车/新能源", "LI": "汽车/新能源",
    "XPEV": "汽车/新能源", "BILI": "社交", "SNOW": "科技", "CRWD": "网络安全",
    "DELL": "科技", "INTC": "半导体", "QCOM": "半导体", "AVGO": "半导体",
    "AMD": "半导体", "CSCO": "科技", "ORCL": "科技", "ADBE": "科技",
    "ISRG": "医药", "UNH": "保险", "LLY": "医药", "MRK": "医药",
    "ABBV": "医药", "JNJ": "医药", "PG": "消费", "KO": "消费",
    "PEP": "消费", "WMT": "消费", "COST": "消费", "HD": "消费",
    "CVX": "能源", "XOM": "能源", "COP": "能源", "GE": "工业",
    "HON": "工业", "BA": "工业", "LMT": "工业", "RTX": "工业",
    "NOC": "工业", "FDX": "工业", "UPS": "工业", "MCD": "消费",
    "SBUX": "消费", "TGT": "消费", "LOW": "消费", "AXP": "金融",
    "BLK": "金融服务", "USB": "金融/银行", "WFC": "金融/银行",
    "TFC": "金融/银行", "COF": "金融", "DFS": "金融", "SPGI": "金融服务",
    "MCO": "金融服务", "IBKR": "金融服务",
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
    # SEC 13F values are in thousands ($1,000 units).
    # If total appears too small (< 100M), multiply by 1000 to convert to actual dollars.
    total_val = sum(h["value"] for h in holdings)
    if total_val < 100_000_000:
        for h in holdings:
            h["value"] *= 1000
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
    print("Fetching David Tepper 13F..." + (" (FULL MODE)" if full_mode else ""))
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
                "manager": "Appaloosa LP",
                "managerCIK": "0001656456",
                "notablePeople": ["David Tepper"],
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
