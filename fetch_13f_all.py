#!/usr/bin/env python3
"""通用 13F 抓取脚本 — 替代所有 fetch_13f_*.py

用法:
  python3 fetch_13f_all.py --investor lilu
  python3 fetch_13f_all.py --investor lilu --full
  python3 fetch_13f_all.py --investor pabrai
  python3 fetch_13f_all.py --investor duan
  python3 fetch_13f_all.py --investor tepper
  python3 fetch_13f_all.py --investor buffett
  python3 fetch_13f_all.py --investor akre
  python3 fetch_13f_all.py --investor greenberg

新增投资者只需在 INVESTOR_CONFIG 里加一行即可。
只依赖标准库，无需 pip install。
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ─────────────────────────────────────────────────────────────
# 投资者配置 — 新增投资者只需在这里加一行
# ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

INVESTOR_CONFIG = {
    "lilu": {
        "cik": "1709323",
        "manager": "Himalaya Capital Management, LLC",
        "people": ["Li Lu"],
        "path": os.path.join(BASE, "data.json"),
    },
    "pabrai": {
        "cik": "1549575",
        "manager": "Dalal Street, LLC",
        "people": ["Mohnish Pabrai"],
        "path": os.path.join(BASE, "pabrai_data.json"),
    },
    "duan": {
        "cik": "1759760",
        "manager": "H&H International Investment, LLC",
        "people": ["Duan Yongping"],
        "path": os.path.join(BASE, "duan.json"),
    },
    "tepper": {
        "cik": "1656456",
        "manager": "Appaloosa LP",
        "people": ["David Tepper"],
        "path": os.path.join(BASE, "tepper.json"),
    },
    "buffett": {
        "cik": "1067983",
        "manager": "Berkshire Hathaway Inc",
        "people": ["Warren Buffett"],
        "path": os.path.join(BASE, "buffett.json"),
        "consolidate": True,   # 合并子公司重复持仓
    },
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

# ─────────────────────────────────────────────────────────────
# 全量 TICKER_MAP（合并去重自各投资者原始脚本）
# ─────────────────────────────────────────────────────────────
TICKER_MAP = {
    # Alphabet — 用 TICKER_CLASS_MAP 区分 CL A / CL C
    "ALPHABET INC": "GOOGL",
    "GOOGLE INC": "GOOGL",
    # 大科技
    "APPLE INC": "AAPL",
    "MICROSOFT CORP": "MSFT",
    "AMAZON COM INC": "AMZN",
    "AMAZON.COM, INC.": "AMZN",
    "NVIDIA CORPORATION": "NVDA",
    "NVIDIA CORP": "NVDA",
    "NVIDIA CORPORATION COMMON STOCK": "NVDA",
    "META PLATFORMS INC": "META",
    "FACEBOOK INC": "META",
    "TESLA INC": "TSLA",
    "INTEL CORP": "INTC",
    "QUALCOMM INC": "QCOM",
    "BROADCOM INC": "AVGO",
    "ADVANCED MICRO DEVICES INC": "AMD",
    "AMD": "AMD",
    "CISCO SYSTEMS INC": "CSCO",
    "HP INC": "HPQ",
    "HP INC.": "HPQ",
    # 消费
    "APPLE INC": "AAPL",
    "COCA COLA CO": "KO",
    "AMERICAN EXPRESS CO": "AXP",
    "KRAFT HEINZ CO": "KHC",
    "KRAFT HEINZ COMPANY": "KHC",
    "KRAFT HEINZ CO /THE": "KHC",
    "PROCTER AND GAMBLE CO": "PG",
    "PROCTER & GAMBLE CO": "PG",
    "JOHNSON & JOHNSON": "JNJ",
    "WALMART INC": "WMT",
    "COSTCO WHOLESALE CORP": "COST",
    "COSTCO WHSL CORP NEW": "COST",
    "COSTCO WHSL CORP": "COST",
    "HOME DEPOT INC": "HD",
    "KROGER CO": "KR",
    "MOODYS CORP": "MCO",
    "MOODY'S CORP": "MCO",
    "MSCI INC": "MSCI",
    "S&P GLOBAL INC": "SPGI",
    "VERISIGN INC": "VRSN",
    "VERISK ANALYTICS INC": "VRSK",
    "FACTSET RESH SYS INC": "FDS",
    "AUTOMATIC DATA PROCESSING INC": "ADP",
    "O REILLY AUTOMOTIVE INC": "ORLY",
    "OREILLY AUTOMOTIVE INC": "ORLY",
    "ROSS STORES INC": "ROST",
    "TJX COS INC": "TJX",
    "DOLLAR TREE INC": "DLTR",
    "NKE": "NKE",
    # 金融
    "BK OF AMERICA CORP": "BAC",
    "BANK OF AMERICA CORP": "BAC",
    "BANK AMERICA CORP": "BAC",
    "BANK AMER CORP": "BAC",
    "BANK OF AMERICA CORPORATION": "BAC",
    "JPMORGAN CHASE & CO": "JPM",
    "GOLDMAN SACHS GROUP INC": "GS",
    "MORGAN STANLEY": "MS",
    "CITIGROUP INC": "C",
    "WELLS FARGO CO NEW": "WFC",
    "WELLS FARGO & CO": "WFC",
    "CHARLES SCHWAB CORP": "SCHW",
    "SCHWAB CHARLES CORP": "SCHW",
    "INTERACTIVE BROKERS GROUP INC": "IBKR",
    "CME GROUP INC": "CME",
    "INTERCONTINENTAL EXCHANGE INC": "ICE",
    "NASDAQ INC": "NDAQ",
    "LONDON STOCK EXCHANGE GROUP": "LNSTY",
    "APOLLO GLOBAL MGMT INC": "APO",
    "KKR & CO INC": "KKR",
    "KKR & CO L P DEL": "KKR",
    "BLACKSTONE INC": "BX",
    "CARLYLE GROUP INC": "CG",
    "ARES MANAGEMENT CORPORATION": "ARES",
    "BLUE OWL CAPITAL INC": "OWL",
    "CAPITAL ONE FINL CORP": "COF",
    "CAPITAL ONE FINANCIAL CORP": "COF",
    "ALLY FINL INC": "ALLY",
    "ALLY FINANCIAL INC": "ALLY",
    "EAST WEST BANCORP INC": "EWBC",
    "SERVISFIRST BANCSHARES INC": "SFBS",
    "ONEMAIN HLDGS INC": "OMF",
    "SLM CORP": "SLM",
    "PRIMERICA INC": "PRI",
    "MILLROSE PPTYS INC": "MRP",
    "FIDELITY NATL FINL INC": "FNF",
    "F&G ANNUITIES & LIFE INC": "FG",
    "FIRST AMERN FINL CORP": "FAF",
    # 保险
    "UNITEDHEALTH GROUP INC": "UNH",
    "ANTHEM INC": "ELV",
    "ELEVANCE HEALTH INC": "ELV",
    "ELEVANCE HEALTH INC FORMERLY": "ELV",
    "CIGNA CORP": "CI",
    "CHUBB LTD": "CB",
    "CHUBB LTD SWITZ": "CB",
    "PROGRESSIVE CORP": "PGR",
    "GOOSEHEAD INS INC": "GSHD",
    # 医药
    "DAVITA INC": "DVA",
    "DAVITA HEALTHCARE PARTNERS INC": "DVA",
    "DAVITA HEALTHCARE PARTNERS IN": "DVA",
    "DAVITA HEALTHCARE": "DVA",
    "DAVITA INC.": "DVA",
    "DAVITA INC /DE/": "DVA",
    "DAVITA": "DVA",
    "HCA HEALTHCARE INC": "HCA",
    "MCKESSON CORP": "MCK",
    "CENCORA INC": "COR",
    "CARDINAL HEALTH INC": "CAH",
    "INTUITIVE SURGICAL": "ISRG",
    "BECTON DICKINSON": "BDX",
    "STRYKER CORP": "SYK",
    "ZOETIS INC": "ZTS",
    "SOPHIA GENETICS SA": "SOPH",
    "ICON PLC": "ICLR",
    "BEIGENE LTD": "BGNE",
    "SERES THERAPEUTICS INC": "SAGE",
    # 能源
    "OCCIDENTAL PETE CORP": "OXY",
    "OXYGEN PETROLEUM": "OXY",
    "CHEVRON CORPORATION": "CVX",
    "CHEVRON CORP NEW": "CVX",
    "EXXON MOBIL CORP": "XOM",
    "ENERGY TRANSFER L P": "ET",
    "ANTERO MIDSTREAM CORP": "AM",
    "MPLX LP": "MPLX",
    "NEXTERA ENERGY INC": "NEE",
    "NRG ENERGY INC": "NRG",
    "VISTRA CORP": "VST",
    "SABLE OFFSHORE CORP": "SABLE",
    # 工业
    "NUCOR CORP": "NUE",
    "NUCOR CORPORATION": "NUE",
    "LENNAR CORP": "LEN",
    "LENNAR CORPORATION": "LEN",
    "LOUISIANA PAC CORP": "LPX",
    "LOUISIANA PACIFIC CORP": "LPX",
    "LOUISIANA PACIFIC CORPORATION": "LPX",
    "D R HORTON INC": "DHI",
    "BUILDERS FIRSTSOURCE INC": "BLDR",
    "ROPER TECHNOLOGIES INC": "ROP",
    "PERIMETER SOLUTIONS INC": "PRM",
    "L3HARRIS TECHNOLOGIES INC": "LHX",
    "RTX CORPORATION": "RTX",
    "ASML HLDG NV": "ASML",
    "BALL CORP": "BALL",
    "CORNING INC": "GLW",
    "WHIRLPOOL CORP": "WHR",
    "LAM RESEARCH CORP": "LRCX",
    "APPLIED MATLS INC": "AMAT",
    "SUNBELT RENTALS HOLDINGS INC": "R",
    # 科技/SaaS
    "ADOBE INC": "ADBE",
    "SALESFORCE INC": "CRM",
    "SALESFORCE COM INC": "CRM",
    "ORACLE CORP": "ORCL",
    "SERVICENOW INC": "NOW",
    "INTUIT INC": "INTU",
    "SNOWFLAKE INC": "SNOW",
    "CROWDSTRIKE HOLDINGS INC": "CRWD",
    "CROWDSTRIKE HLDGS INC": "CRWD",
    "PALANTIR TECHNOLOGIES INC": "PLTR",
    "MONGODB INC": "MDB",
    "ZOOMINFO TECHNOLOGIES INC": "ZI",
    "INNODATA INC": "INOD",
    "TEMPUS AI INC": "TEM",
    "COINBASE GLOBAL INC": "COIN",
    "COINBASE GLOBAL INC NEW": "COIN",
    "COSTAR GROUP INC": "CSGP",
    "FAIR ISAAC CORP": "FICO",
    "CCC INTELLIGENT SOLUTIONS HL": "CCCS",
    "ROPER TECHNOLOGIES INC": "ROP",
    "BROOKFIELD CORP": "BN",
    # 半导体
    "TAIWAN SEMICONDUCTOR MANUFACC": "TSM",
    "TAIWAN SEMICONDUCTOR MANUFAC": "TSM",
    "TAIWAN SEMICONDUCTOR MANUFACTURING": "TSM",
    "MICRON TECHNOLOGY INC": "MU",
    "SYNOPSYS INC": "SNPS",
    "CREDO TECHNOLOGY GROUP HOLDING": "CRDO",
    "CREDO TECHNOLOGY GROUP HOLDI": "CRDO",
    # 娱乐/媒体
    "NETFLIX INC": "NFLX",
    "WALT DISNEY CO": "DIS",
    "DISNEY WALT CO": "DIS",
    "COMCAST CORP NEW": "CMCSA",
    "NEW YORK TIMES CO": "NYT",
    "NEW YORK TIMES CO MTN BE": "NYT",
    "NEW YORK TIMES CO NEW": "NYT",
    "PARAMOUNT GLOBAL": "PARA",
    "VIACOMCBS INC": "PARA",
    "VIACOMCBS INC.": "PARA",
    "ACTIVISION BLIZZARD INC": "ATVI",
    "ACTIVISION BLIZZARD": "ATVI",
    "TAKE-TWO INTERACTIVE SOFTWARE": "TTWO",
    "TAKE TWO INTERACTIVE SOFTWARE": "TTWO",
    "TAKE-TWO INTERACTIVE SOFTWAR": "TTWO",
    "ELECTRONIC ARTS INC": "EA",
    "NETEASE INC": "NTES",
    "BILIBILI INC": "BILI",
    "TENCENT MUSIC ENTMT GROUP": "TME",
    # 电商/中概
    "PDD HOLDINGS INC": "PDD",
    "PINDUODUO INC": "PDD",          # 2022年底改名前的旧名称
    "ALIBABA GROUP HLDG LTD": "BABA",
    "TENCENT HLDGS LTD": "TCEHY",
    "JD.COM INC": "JD",
    "JD COM INC": "JD",
    "NIO INC": "NIO",
    "LI AUTO INC": "LI",
    "XPENG INC": "XPEV",
    "BAIDU INC": "BIDU",
    "SEA LTD": "SE",
    "YUM CHINA HOLDINGS INC": "YUMC",
    "JOYY INC": "YY",
    "CIRCLE INTERNET GROUP INC": "CRCL",
    # 综合
    "BERKSHIRE HATHAWAY INC DEL": "BRK.B",
    "BERKSHIRE HATHAWAY INC": "BRK.B",
    "BRK": "BRK.B",
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
    "LIBERTY SIRIUSXM GROUP": "LSXMA",
    "LIBERTY SIRIUS XM GROUP": "LSXMA",
    "SIRIUSXM HOLDINGS INC": "SIRI",
    "SIRIUS XM RADIO INC": "SIRI",
    "SIRIUS XM HOLDINGS INC": "SIRI",
    "DELTA AIR LINES INC": "DAL",
    "DELTA AIR INC": "DAL",
    "CARRIER GLOBAL CORPORATION": "CARR",
    "CARRIER GLOBAL CORPORATION COMMON": "CARR",
    "FREEPORT-MCMORAN INC": "FCX",
    "FREEPORT MCMORAN INC": "FCX",
    "WARRIOR MET COAL INC": "HCC",
    "TRANSOCEAN LTD": "RIG",
    "ALPHA METALLURGICAL RESOURCE": "AMR",
    "ALPHA METALLURGICAL RESOUR I": "AMR",
    "CHESAPEAKE ENERGY CORP": "CHK",
    "DEUTSCHE BK AG": "DB",
    "ADVANCE AUTO PARTS INC": "AAP",
    "HEICO CORP": "HEI",
    "HEICO CORPORATION": "HEI",
    "RH": "RH",
    "RH RESTORATION HARDWARE": "RH",
    "STONECO LTD": "STNE",
    "US BANCORP DEL": "USB",
    "U S BANCORP DEL": "USB",
    "CROCS INC": "CROX",
    "BLOCK H & R INC": "HRB",
    "AMERICAN TOWER CORP NEW": "AMT",
    "VISA INC": "V",
    "MASTERCARD INCORPORATED": "MA",
    "MASTERCARD INC": "MA",
    "AUTONATION INC": "AN",
    "TD SYNNEX CORPORATION": "SNX",
    "RYANAIR HOLDINGS PLC": "RYAAY",
    "BRIGHT HORIZONS FAMILY SOL INC": "BFAM",
    "MARKETAXESS HOLDINGS INC": "MKTX",
    "COSTAR GROUP INC": "CSGP",
    "CENTENE CORP": "CNC",
    "GENUINE PARTS CO": "GPC",
    "RENT-A-CENTER INC NEW": "RCII",
    "PULMONX CORP": "LUNG",
    "UWM HOLDINGS CORPORATION": "UWMC",
    "UWM HLDG CORP": "UWMC",
    "UWM HOLDINGS CORP": "UWMC",
    "LENDINGTREE INC NEW": "TREE",
    "CHEGG INC": "CHGG",
    "PHYSICIANS RLTY TR": "DOC",
    "SANDISK CORP": "SNDK",
    "DELL TECHNOLOGIES INC": "DELL",
    # ETFs
    "SPDR S&P 500 ETF TRUST": "SPY",
    "VANGUARD S&P 500 ETF": "VOO",
    "VANGUARD INDEX FDS S&P 500 ETF": "VOO",
    "ISHARES INC": "IEMG",
    "ISHARES RUSSELL 2000 ETF": "IWM",
    "INVESCO QQQ TRUST SERIES 1": "QQQ",
    "INVESCO QQQ TR": "QQQ",
    "KRANESHARES TRUST": "KWEB",
}

# CL A / CL C 需区分的个股
TICKER_CLASS_MAP = {
    ("ALPHABET INC", True): "GOOGL",
    ("ALPHABET INC", False): "GOOG",
    ("ALPHABET INC CL A", True): "GOOGL",
    ("ALPHABET INC CL C", False): "GOOG",
    ("GOOGLE INC", True): "GOOGL",
    ("GOOGLE INC", False): "GOOG",
    ("BROWN FORMAN CORP", True): "BF.A",
    ("BROWN FORMAN CORP", False): "BF.B",
}

# 行业映射（兜底用 enrich_metadata.py 的 LLM 标注）
SECTORS = {
    "AAPL": "科技", "MSFT": "科技", "AMZN": "电商", "GOOG": "互联网",
    "GOOGL": "互联网", "NVDA": "半导体", "META": "社交", "TSLA": "汽车/新能源",
    "BRK.B": "综合金融", "JPM": "金融/银行", "V": "金融服务", "MA": "金融服务",
    "COST": "消费", "HD": "消费", "PG": "消费", "JNJ": "医药",
    "UNH": "保险", "WMT": "消费", "XOM": "能源", "CVX": "能源",
    "BAC": "金融/银行", "WFC": "金融/银行", "MS": "金融服务", "GS": "金融服务",
    "C": "金融/银行", "SCHW": "金融服务", "IBKR": "金融服务", "CME": "金融服务",
    "ICE": "金融服务", "NDAQ": "金融服务", "APO": "金融服务", "KKR": "金融服务",
    "BX": "金融服务", "CG": "金融服务", "ARES": "金融服务", "OWL": "金融服务",
    "AXP": "金融服务", "COF": "金融/银行", "ALLY": "金融/银行", "EWBC": "金融/银行",
    "SFBS": "金融/银行", "OMF": "金融服务", "SLM": "金融服务", "USB": "金融/银行",
    "MCO": "金融服务", "SPGI": "金融服务", "MSCI": "金融服务", "VRSK": "科技",
    "FDS": "科技", "ADP": "科技", "PAYC": "科技", "FICO": "科技",
    "ELV": "保险", "CI": "保险", "CB": "保险", "PGR": "保险",
    "UNH": "保险", "GSHD": "保险", "CNC": "保险", "PRI": "保险",
    "DVA": "医药", "HCA": "医药", "MCK": "医药", "COR": "医药",
    "CAH": "医药", "ISRG": "医药", "BDX": "医药", "SYK": "医药",
    "ZTS": "医药", "SOPH": "医药", "ICLR": "医药", "BGNE": "医药",
    "SAGE": "医药", "LUNG": "医药", "JNJ": "医药",
    "OXY": "能源", "CVX": "能源", "XOM": "能源", "ET": "能源",
    "AM": "能源", "MPLX": "能源", "NEE": "能源", "NRG": "能源",
    "VST": "能源", "CHK": "油气", "RIG": "油气钻探",
    "NFLX": "娱乐", "DIS": "娱乐", "CMCSA": "娱乐",
    "NYT": "媒体", "PARA": "媒体", "ATVI": "游戏", "TTWO": "游戏",
    "NTES": "游戏", "BILI": "社交", "TME": "娱乐",
    "PDD": "电商", "BABA": "电商", "JD": "电商", "SE": "电商",
    "TCEHY": "社交", "BIDU": "互联网", "NIO": "汽车/新能源",
    "LI": "汽车/新能源", "XPEV": "汽车/新能源", "YUMC": "消费",
    "CRCL": "金融服务", "YY": "社交", "BGNE": "医药",
    "NUE": "工业", "LEN": "工业", "LPX": "工业", "DHI": "工业",
    "BLDR": "工业", "ROP": "多元工业", "LHX": "工业", "RTX": "工业",
    "ASML": "半导体", "LRCX": "半导体", "AMAT": "半导体", "SNDS": "半导体",
    "MU": "半导体", "TSM": "半导体", "SNPS": "半导体", "CRDO": "半导体",
    "AMD": "半导体", "INTC": "半导体", "QCOM": "半导体", "AVGO": "半导体",
    "SNOW": "科技", "CRWD": "网络安全", "PLTR": "科技", "MDB": "科技",
    "ZI": "科技", "INOD": "科技", "TEM": "医药", "COIN": "金融服务",
    "CSGP": "科技", "CCCS": "科技", "BN": "金融服务", "DELL": "科技",
    "CRM": "科技", "NOW": "科技", "INTU": "科技", "ADBE": "科技",
    "ORCL": "科技", "SNDK": "科技",
    "KO": "消费", "PEP": "消费", "KHC": "消费", "GPC": "消费",
    "RCII": "消费", "CROX": "消费", "NKE": "消费", "TJX": "消费",
    "ROST": "消费", "DLTR": "消费", "ORLY": "消费", "AN": "消费",
    "BFAM": "消费", "STZ": "消费", "KR": "消费", "WMT": "消费",
    "VRSN": "科技", "HRB": "金融服务", "SIRI": "娱乐", "LSXMA": "娱乐",
    "LLYVA": "娱乐", "DAL": "工业", "CARR": "工业", "FCX": "采矿",
    "HCC": "煤炭", "AMR": "冶金/煤炭", "DB": "金融/银行",
    "DOC": "房地产", "MKTX": "金融服务", "CSGP": "房地产",
    "UWMC": "金融", "TREE": "金融", "CHGG": "教育",
    "SABLE": "能源", "BF.B": "消费", "BF.A": "消费",
    "FNF": "金融服务", "FG": "保险", "FAF": "金融服务",
    "PRM": "工业", "R": "工业", "RYAAY": "消费", "SNX": "科技",
    "MRP": "金融服务", "MPLX": "能源", "STNE": "金融服务",
    "RH": "消费", "JEF": "金融服务", "NVR": "工业", "HPQ": "科技",
    "AMT": "通讯", "KWEB": "ETF", "IEMG": "ETF", "SPY": "ETF",
    "VOO": "ETF", "QQQ": "ETF", "IWM": "ETF",
}


# ─────────────────────────────────────────────────────────────
# SEC EDGAR 工具函数（所有投资者共用）
# ─────────────────────────────────────────────────────────────

def sec_fetch(path: str, retries: int = 3) -> bytes:
    """带 retry + rate-limit 的 SEC 请求。"""
    url = f"https://www.sec.gov{path}" if path.startswith("/") else f"https://data.sec.gov/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    for attempt in range(retries):
        try:
            time.sleep(0.15)  # SEC EDGAR: max 10 req/s
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read()
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)
                print(f"  429 rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"sec_fetch failed after {retries} retries: {url}")


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
    """尝试 .html 和 .htm 两种格式，提取 INFOTABLE XML 路径。"""
    index_html = None
    for ext in ["-index.html", "-index.htm"]:
        try:
            raw = sec_fetch(f"/Archives/edgar/data/{cik}/{accession}/{accession_dashed}{ext}")
            index_html = raw.decode("utf-8", errors="replace")
            break
        except Exception:
            continue
    if index_html is None:
        raise RuntimeError(f"Cannot fetch index for {accession_dashed}")
    pattern = r'<a\s+href="([^"]+)"[^>]*>([^<]+\.xml)</a>\s*</td>\s*<td[^>]*>\s*INFORMATION TABLE'
    for m in re.finditer(pattern, index_html, re.IGNORECASE):
        href = m.group(1)
        if "xslForm13F" not in href:
            return href
    # Fallback
    m2 = re.search(r"(\d{2})(\d)(\d)$", accession)
    if m2:
        return f"/Archives/edgar/data/{cik}/{accession}/13fhciq{m2.group(2)}{m2.group(3)}.xml"
    raise RuntimeError(f"Cannot find INFOTABLE XML for {accession_dashed}")


def resolve_ticker(name: str, cls: str) -> str:
    n = name.strip()
    is_a = "CL A" in (cls or "").upper()
    class_key = (n, is_a)
    if class_key in TICKER_CLASS_MAP:
        return TICKER_CLASS_MAP[class_key]
    if n in TICKER_MAP:
        return TICKER_MAP[n]
    return f"?{n}"


def parse_holdings(xml_bytes: bytes, consolidate: bool = False) -> list[dict]:
    """解析 INFOTABLE XML，返回 holdings 列表（已排序）。"""
    root = ET.fromstring(xml_bytes)
    raw_entries = []
    for info in root.findall("ns:infoTable", NS):
        name_el = info.find("ns:nameOfIssuer", NS)
        cls_el = info.find("ns:titleOfClass", NS)
        val_el = info.find("ns:value", NS)
        shares_el = info.find(".//ns:sshPrnamt", NS)
        name_val = name_el.text.strip() if name_el is not None and name_el.text else ""
        cls_val = cls_el.text.strip() if cls_el is not None and cls_el.text else ""
        shares = int(shares_el.text) if shares_el is not None and shares_el.text else 0
        value = int(val_el.text) if val_el is not None and val_el.text else 0
        tk = resolve_ticker(name_val, cls_val)
        raw_entries.append({
            "ticker": tk, "name": name_val, "cls": cls_val,
            "shares": shares, "value": value,
        })

    # 自动检测单位：SEC 2022Q4 前用 kUSD，之后用 USD
    valid = [e for e in raw_entries if e["shares"] > 0 and e["value"] > 0]
    if valid:
        avg_price = sum(e["value"] / e["shares"] for e in valid) / len(valid)
        if avg_price < 1.0:
            for e in raw_entries:
                e["value"] *= 1000

    if consolidate:
        # 合并同一 ticker 的多个子公司持仓（主要针对 Berkshire）
        merged: dict[str, dict] = {}
        for e in raw_entries:
            tk = e["ticker"]
            if tk not in merged:
                merged[tk] = dict(e)
                merged[tk]["sector"] = SECTORS.get(tk, "其他")
            else:
                merged[tk]["shares"] += e["shares"]
                merged[tk]["value"] += e["value"]
        holdings = list(merged.values())
    else:
        for e in raw_entries:
            e["sector"] = SECTORS.get(e["ticker"], "其他")
        holdings = raw_entries

    holdings.sort(key=lambda h: h["value"], reverse=True)
    return holdings


def save_data(path: str, data: dict):
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def warn_unmapped(data: dict):
    """打印所有未识别的 ticker（以 ? 开头），提醒补充 TICKER_MAP。"""
    unmapped = set()
    for h in data.get("current", {}).get("holdings", []):
        if h["ticker"].startswith("?"):
            unmapped.add(h["ticker"])
    for holdings in data.get("history", {}).get("holdings", {}).values():
        for h in holdings:
            if h["ticker"].startswith("?"):
                unmapped.add(h["ticker"])
    if unmapped:
        print(f"⚠️  未识别 ticker（需补充 TICKER_MAP）: {sorted(unmapped)}")
    else:
        print("✅ 所有 ticker 均已识别")


# ─────────────────────────────────────────────────────────────
# 主流程
# ─────────────────────────────────────────────────────────────

def process_investor(key: str, config: dict, full_mode: bool):
    print(f"\n{'='*60}")
    print(f"Processing {key.upper()}: {config['manager']}")
    print(f"CIK: {config['cik']}")
    print(f"{'='*60}")

    cik = config["cik"]
    consolidate = config.get("consolidate", False)
    filings = get_recent_filings(cik)
    if len(filings) < 2:
        print(f"ERROR: only found {len(filings)} filings, need ≥2")
        sys.exit(1)

    if os.path.exists(config["path"]):
        with open(config["path"], "r") as f:
            data = json.load(f)
    else:
        data = {
            "meta": {
                "manager": config["manager"],
                "managerCIK": cik.zfill(10),
                "notablePeople": config["people"],
                "lastUpdated": "",
            },
            "current": {},
            "history": {"quarters": [], "values": [], "holdings": {}},
        }

    if full_mode:
        return process_full(key, config, filings, data)

    # ── 普通模式：只抓最新两期，更新 current ──
    cur_f, prev_f = filings[0], filings[1]
    print(f"  Latest:   {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_xml  = sec_fetch(find_info_table_xml(cik, cur_f["accession"], cur_f["accessionDashed"]))
    prev_xml = sec_fetch(find_info_table_xml(cik, prev_f["accession"], prev_f["accessionDashed"]))
    cur_holdings  = parse_holdings(cur_xml,  consolidate=consolidate)
    prev_holdings = parse_holdings(prev_xml, consolidate=consolidate)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in cur_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"]  = p.get("value", 0)

    total      = sum(h["value"] for h in cur_holdings)
    prev_total = sum(h["value"] for h in prev_holdings)

    data["current"] = {
        "quarter":        quarter_label(cur_f["reportDate"]),
        "filingDate":     cur_f["filingDate"],
        "periodEnd":      cur_f["reportDate"],
        "totalValue":     total,
        "holdings":       cur_holdings,
        "prevQuarter":    quarter_label(prev_f["reportDate"]),
        "prevTotalValue": prev_total,
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    q_label = quarter_label(cur_f["reportDate"])
    if q_label not in data["history"]["quarters"]:
        data["history"]["quarters"].append(q_label)
        data["history"]["values"].append(round(total / 1_000_000))
        data["history"]["holdings"][q_label] = cur_holdings

    save_data(config["path"], data)
    warn_unmapped(data)
    print(f"Updated: {len(cur_holdings)} holdings, ${total:,.0f} total")


def process_full(key: str, config: dict, filings: list[dict], data: dict):
    """全量模式：抓取所有历史报告期。"""
    cik = config["cik"]
    consolidate = config.get("consolidate", False)
    filings_sorted = list(reversed(filings))  # 从最早到最新
    print(f"Found {len(filings_sorted)} total filings to process.")

    if "history" not in data:
        data["history"] = {"quarters": [], "values": [], "holdings": {}}
    if "holdings" not in data["history"]:
        data["history"]["holdings"] = {}

    existing_quarters = set(data["history"]["quarters"])
    all_fetched: dict[str, list[dict]] = {}
    new_quarters = 0
    skipped = 0

    for i, f in enumerate(filings_sorted):
        q_label = quarter_label(f["reportDate"])

        if q_label in existing_quarters:
            skipped += 1
            print(f"  [{i+1}/{len(filings_sorted)}] SKIP {q_label} (already in history)")
            # 仍然加载进内存，供后续 prevShares diff 使用
            try:
                xml_bytes = sec_fetch(find_info_table_xml(cik, f["accession"], f["accessionDashed"]))
                all_fetched[q_label] = parse_holdings(xml_bytes, consolidate=consolidate)
            except Exception as e:
                print(f"    -> WARN: could not reload skipped quarter: {e}")
            continue

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label} (filed {f['filingDate']})...")
        try:
            xml_bytes = sec_fetch(find_info_table_xml(cik, f["accession"], f["accessionDashed"]))
            holdings = parse_holdings(xml_bytes, consolidate=consolidate)
            all_fetched[q_label] = holdings

            # 找最近的前一期用于 prevShares
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
                    h["prevValue"]  = p.get("value", 0)
            else:
                for h in holdings:
                    h["prevShares"] = 0
                    h["prevValue"]  = 0

            total = sum(h["value"] for h in holdings)
            data["history"]["quarters"].append(q_label)
            data["history"]["values"].append(round(total / 1_000_000))
            data["history"]["holdings"][q_label] = holdings
            new_quarters += 1
            print(f"    -> {len(holdings)} holdings, ${total:,.0f}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    # 更新 current 为最新一期
    latest = filings[0]
    latest_q = quarter_label(latest["reportDate"])
    if latest_q in all_fetched:
        latest_holdings = all_fetched[latest_q]
    else:
        xml_bytes = sec_fetch(find_info_table_xml(cik, latest["accession"], latest["accessionDashed"]))
        latest_holdings = parse_holdings(xml_bytes, consolidate=consolidate)

    prev_f = filings[1]
    prev_q = quarter_label(prev_f["reportDate"])
    if prev_q in all_fetched:
        prev_holdings = all_fetched[prev_q]
    else:
        xml_bytes = sec_fetch(find_info_table_xml(cik, prev_f["accession"], prev_f["accessionDashed"]))
        prev_holdings = parse_holdings(xml_bytes, consolidate=consolidate)

    prev_map = {h["ticker"]: h for h in prev_holdings}
    for h in latest_holdings:
        p = prev_map.get(h["ticker"], {})
        h["prevShares"] = p.get("shares", 0)
        h["prevValue"]  = p.get("value", 0)

    latest_total = sum(h["value"] for h in latest_holdings)
    data["current"] = {
        "quarter":        quarter_label(latest["reportDate"]),
        "filingDate":     latest["filingDate"],
        "periodEnd":      latest["reportDate"],
        "totalValue":     latest_total,
        "holdings":       latest_holdings,
        "prevQuarter":    quarter_label(prev_f["reportDate"]),
        "prevTotalValue": sum(h["value"] for h in prev_holdings),
    }
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if latest_q not in data["history"]["quarters"]:
        data["history"]["quarters"].append(latest_q)
        data["history"]["values"].append(round(latest_total / 1_000_000))
    data["history"]["holdings"][latest_q] = latest_holdings

    save_data(config["path"], data)
    warn_unmapped(data)
    print(f"\nDone: {new_quarters} new quarters, {skipped} skipped.")
    print(f"Total quarters: {len(data['history']['quarters'])}")
    print(f"Current: {len(latest_holdings)} holdings, ${latest_total:,.0f}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="通用 13F 抓取脚本")
    parser.add_argument("--investor", required=True,
                        choices=list(INVESTOR_CONFIG.keys()),
                        help="投资者 key")
    parser.add_argument("--full", action="store_true",
                        help="全量模式：抓取所有历史报告期")
    args = parser.parse_args()

    config = INVESTOR_CONFIG[args.investor]
    try:
        process_investor(args.investor, config, args.full)
    except Exception as e:
        print(f"\nFATAL ERROR for {args.investor}: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
