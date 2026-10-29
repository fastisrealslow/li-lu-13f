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
  python3 fetch_13f_all.py --investor klarman
  python3 fetch_13f_all.py --investor ackman
  python3 fetch_13f_all.py --investor abrams
  python3 fetch_13f_all.py --investor berkowitz
  python3 fetch_13f_all.py --investor hawkins

新增投资者只需在仓库根目录的 investors.json 里加一条记录即可，
INVESTOR_CONFIG 会在启动时从该文件自动构建，无需在本文件手工修改。
只依赖标准库，无需 pip install。
"""

from holdings_diff import attach_previous, update_history, VERIFIED_SPLITS, consolidate_holdings

import json
import os
import re
import sys
import time
import threading
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, date
from decimal import Decimal

# ─────────────────────────────────────────────────────────────
# 投资者配置 — 新增投资者只需在这里加一行
# ─────────────────────────────────────────────────────────────
BASE = os.path.dirname(os.path.abspath(__file__))
USER_AGENT = "13F-Tracker guoziyuan@xiaohongshu.com"
NS = {"ns": "http://www.sec.gov/edgar/document/thirteenf/informationtable"}

def _load_investor_config():
    """从 investors.json 读取投资者列表（单一权威来源），转换为
    本脚本原有的 INVESTOR_CONFIG 字典结构。只纳入 source13F=true 的
    投资者（webb 是港股权益披露，走独立的 fetch_webb_holdings.py，
    不需要 CIK，也不走 SEC 13F 抓取流程）。新增投资者只需编辑 investors.json，
    无需在本文件手工加条目。"""
    try:
        with open(os.path.join(BASE, 'investors.json'), encoding='utf-8') as f:
            investors = json.load(f)['investors']
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"ERROR: investors.json 读取失败（{e}）", file=sys.stderr)
        sys.exit(1)

    cfg = {}
    for inv in investors:
        if not inv.get('source13F'):
            continue
        entry = {
            "cik": inv["cik"],
            "manager": inv["manager"],
            "people": inv["people"],
            "path": os.path.join(BASE, inv["dataFile"]),
            "useRestatements": inv.get("useRestatements", True),
        }
        if inv.get("consolidate"):
            entry["consolidate"] = True
        if inv.get("legacyFilers"):
            entry["legacyFilers"] = inv["legacyFilers"]
        for field in ("reportingFrom", "reportingTransition", "historyGapNotices", "useRestatements", "fullArchiveWorkers"):
            if inv.get(field): entry[field] = inv[field]
        cfg[inv["id"]] = entry
    return cfg


INVESTOR_CONFIG = _load_investor_config()

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
    "NETFLIX INC.": "NFLX",
    "PERSHING SQUARE USA LTD": "PSUS",
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

# CUSIP → ticker（当名称匹配失败或有多股票类别歧义时优先使用，人工逐条核对）
# 由 Klarman/Ackman/Abrams/Berkowitz/Hawkins 5 位投资者持仓补充
CUSIP_TICKER_MAP = {
    "526057104": "LEN",
    "526057302": "LEN/B",
    "530909100": "LLYVA",
    "530909308": "LLYVK",
    # RV Capital holdings: security identifiers from original SEC information tables.
    "146869102": "CVNA",  # CARVANA CO
    "244199105": "DE",    # DEERE & CO
    "45841N107": "IBKR",  # INTERACTIVE BROKERS GROUP IN
    "617700109": "MORN",  # MORNINGSTAR INC
    "70432V102": "PAYC",  # PAYCOM SOFTWARE INC
    "819047101": "SHAK",  # SHAKE SHACK INC
    "83088V102": "WORK",  # SLACK TECHNOLOGIES INC (historical, acquired)
    "L8681T102": "SPOT",  # SPOTIFY TECHNOLOGY S A
    "898202106": "TRUP",  # TRUPANION INC
    "M98068105": "WIX",   # WIX COM LTD
    "00108J109": "ACMR",  # ACM RESH INC
    "008252108": "AMG",  # AFFILIATED MANAGERS GROUP
    "013091103": "ACI",  # ALBERTSONS COS INC
    "014752109": "ALX",  # ALEXANDERS INC
    "03064D108": "COLD",  # AMERICOLD REALTY TRUST INC
    "G0403H108": "AON",  # AON PLC
    "043436104": "ABG",  # ASBURY AUTOMOTIVE GROUP INC
    "047726302": "BATRK",  # ATLANTA BRAVES HLDGS INC
    "05352A100": "AVTR",  # AVANTOR INC
    "06417N103": "OZK",  # BANK OZK
    "090572207": "BIO",  # BIO RAD LABS INC
    "100557107": "SAM",  # BOSTON BEER INC
    "G21810109": "CLVT",  # CLARIVATE PLC
    "18538R103": "CLW",  # CLEARWATER PAPER CORP
    "N20944109": "CNH",  # CNH INDL N V
    "12653C108": "CNX",  # CNX RES CORP
    "22266T109": "CPNG",  # COUPANG INC
    "67011P100": "DNOW",  # DNOW INC
    "G27907107": "DOLE",  # DOLE PLC
    "26969P108": "EXP",  # EAGLE MATLS INC
    "292104106": "ESRT",  # EMPIRE ST RLTY TR INC
    "194014502": "ENOV",  # ENOVIS CORPORATION
    "293792107": "EPD",  # ENTERPRISE PRODS PARTNERS L
    "31428X106": "FDX",  # FEDEX CORP
    "31488V107": "FERG",  # FERGUSON ENTERPRISES INC
    "31620M106": "FIS",  # FIDELITY NATL INFORMATION SV
    "337738108": "FISV",  # FISERV INC
    "34964C106": "FBIN",  # FORTUNE BRANDS INNOVATIONS I
    "36164V800": "GLIBK",  # GCI LIBERTY INC (now Liberty Capital Corp, ticker unchanged) — Series C
    "36164V602": "GLIBA",  # GCI LIBERTY INC — Series A common stock
    "36165L108": "GDS",  # GDS HLDGS LTD
    "372460105": "GPC",  # GENUINE PARTS CO
    "384637104": "GHC",  # GRAHAM HLDGS CO
    "40054J109": "AERO",  # GRUPO AEROMEXICO SAB DE CV
    "44332N106": "HTHT",  # H WORLD GROUP LTD
    "40415F101": "HDB",  # HDFC BANK LTD
    "G4412G101": "HLF",  # HERBALIFE LTD
    "42806J700": "HTZ",  # HERTZ GLOBAL HLDGS INC
    "436893200": "HOMB",  # HOME BANCSHARES INC
    "44267T102": "HHH",  # HOWARD HUGHES HOLDINGS INC
    "448579102": "H",  # HYATT HOTELS CORP
    "44891N208": "IAC",  # IAC INC (renamed People Inc / PPLI on 2026-06-04, AFTER this filing period)
    "48581R205": "KSPI",  # KASPI KZ JSC
    "500754106": "KHC",  # KRAFT HEINZ CO
    "52110M109": "LAZ",  # LAZARD INC
    "G61188127": "LBTYA",  # LIBERTY GLOBAL LTD
    "536797103": "LAD",  # LITHIA MTRS INC
    "538034109": "LYV",  # LIVE NATION ENTERTAINMENT IN
    "53947R105": "LOAR",  # LOAR HOLDINGS INC
    "55825T103": "MSGS",  # MADISON SQUARE GRDN SPRT COR
    "N5505D105": "MICC",  # MAGNUM ICE CREAM CO NV
    "577081102": "MAT",  # MATTEL INC
    "585464100": "MLCO",  # MELCO RESORTS AND ENTMNT LTD
    "552953101": "MGM",  # MGM RESORTS INTERNATIONAL
    "60855R100": "MOH",  # MOLINA HEALTHCARE INC
    "647581206": "EDU",  # NEW ORIENTAL ED & TECHNOLOGY
    "G66721104": "NCLH",  # NORWEGIAN CRUISE LINE HLDGS
    "67080N101": "NUVB",  # NUVATION BIO INC
    "70450Y103": "PYPL",  # PAYPAL HLDGS INC
    "693656100": "PVH",  # PVH CORPORATION
    "754907103": "RYN",  # RAYONIER INC
    "75886F107": "REGN",  # REGENERON PHARMACEUTICALS
    "76131D103": "QSR",  # RESTAURANT BRANDS INTL INC
    "74982T103": "RXO",  # RXO INC
    "806407102": "HSIC",  # SCHEIN HENRY INC
    "812215200": "SEG",  # SEAPORT ENTMT GROUP INC
    "G8068L108": "SN",  # SHARKNINJA INC
    "82312B106": "SHEN",  # SHENANDOAH TELECOMMUNICATION
    "88023U101": "SGI",  # SOMNIGROUP INTERNATIONAL INC
    "790148100": "JOE",  # ST JOE CO
    "879369106": "TFX",  # TELEFLEX INCORPORATED
    "896945201": "TRIP",  # TRIPADVISOR INC
    "023586100": "UHAL",  # U HAUL HOLDING COMPANY — common stock
    "023586506": "UHAL.B",  # U HAUL HOLDING COMPANY — Series N Non-Voting Common Stock
    "90353T100": "UBER",  # UBER TECHNOLOGIES INC
    "92243G108": "PCVX",  # VAXCYTE INC
    "95082P105": "WCC",  # WESCO INTL INC
    "G9618E107": "WTM",  # WHITE MTNS INS GROUP LTD
    "G96629103": "WTW",  # WILLIS TOWERS WATSON PLC LTD
    "084423102": "WRB",  # WR BERKLEY CORP
    "983793100": "XPO",  # XPO INC
    "907818108": "UNP",  # UNION PAC CORP
}


def _load_auto_resolved_cusip_map():
    """合并 resolve_unmapped_tickers.py 自动解析并持久化的 CUSIP→ticker
    映射（见 resolved_cusip_map.json）。该文件由 OpenFIGI API 权威解析
    生成，不存在时静默跳过 —— 不影响手工维护的 CUSIP_TICKER_MAP。"""
    path = os.path.join(BASE, "resolved_cusip_map.json")
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARN: resolved_cusip_map.json 读取失败（{e}），跳过自动映射", file=sys.stderr)
        return {}


# 手工映射优先于自动解析映射（如有冲突，人工核对过的条目更可信）
CUSIP_TICKER_MAP = {**_load_auto_resolved_cusip_map(), **CUSIP_TICKER_MAP}
# Issuer/SEC-verified identities; name abbreviations in 13F are not stable keys.
CUSIP_TICKER_MAP.update({'H1467J104':'CB','G4705A100':'ICLR','G6683N103':'NU','G0750C108':'AXTA','12510Q100':'CCC'})
_symbol_changes_path=os.path.join(BASE,'security_symbol_changes.json')
if os.path.exists(_symbol_changes_path):
    with open(_symbol_changes_path,encoding='utf-8') as _f:
        for _cusip,_change in json.load(_f).get('entries',{}).items():
            if re.fullmatch(r'[A-Z0-9]{9}',_cusip) and re.fullmatch(r'[A-Z][A-Z0-9./-]*',_change.get('ticker','')):
                CUSIP_TICKER_MAP[_cusip]=_change['ticker']

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
    # Klarman/Ackman/Abrams/Berkowitz/Hawkins 补充
    "ACMR": "半导体", "AMG": "金融服务", "ACI": "消费", "ALX": "地产",
    "COLD": "地产", "AON": "金融服务", "ABG": "消费", "BATRK": "娱乐",
    "AVTR": "医药", "OZK": "金融/银行", "BIO": "医药", "SAM": "消费",
    "CLVT": "科技", "CLW": "工业", "CNH": "工业", "CNX": "能源",
    "CPNG": "电商", "DNOW": "能源", "DOLE": "消费", "EXP": "工业",
    "ESRT": "地产", "ENOV": "医药", "EPD": "能源", "FDX": "工业",
    "FERG": "工业", "FIS": "金融服务", "FISV": "金融服务", "FBIN": "消费",
    "GLIBK": "通讯", "GLIBA": "通讯", "GDS": "科技", "GPC": "消费", "GHC": "多元工业",
    "AERO": "工业", "HTHT": "消费", "HDB": "金融/银行", "HLF": "消费",
    "HTZ": "消费", "HOMB": "金融/银行", "HHH": "地产", "H": "消费",
    "IAC": "互联网", "KSPI": "金融服务", "LAZ": "金融服务",
    "LBTYA": "通讯", "LAD": "消费", "LYV": "娱乐", "LOAR": "工业",
    "MSGS": "娱乐", "MICC": "消费", "MLCO": "娱乐",
    "MGM": "娱乐", "MOH": "保险", "EDU": "教育", "NCLH": "娱乐",
    "NUVB": "医药", "PYPL": "金融服务", "PVH": "消费", "RYN": "地产",
    "REGN": "医药", "QSR": "消费", "RXO": "工业", "HSIC": "医药",
    "SEG": "地产", "SN": "消费", "SHEN": "通讯", "SGI": "消费",
    "JOE": "地产", "TFX": "医药", "TRIP": "消费", "UHAL": "工业", "UHAL.B": "工业",
    "UBER": "科技", "PCVX": "医药", "WCC": "工业", "WTM": "保险", "WTW": "金融服务", "WRB": "保险",
    "XPO": "工业",
}


# ─────────────────────────────────────────────────────────────
# SEC EDGAR 工具函数（所有投资者共用）
# ─────────────────────────────────────────────────────────────

_SEC_RATE_LOCK = threading.Lock()

def sec_fetch(path: str, retries: int = 3) -> bytes:
    """带 retry + rate-limit 的 SEC 请求。"""
    url = f"https://www.sec.gov{path}" if path.startswith("/") else f"https://data.sec.gov/{path}"
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    immutable = path.startswith('/Archives/edgar/data/')
    import hashlib
    cache = Path(BASE)/'.cache'/'sec-originals'/(hashlib.sha256(url.encode()).hexdigest()+'.bin')
    if immutable and cache.exists():
        return cache.read_bytes()
    for attempt in range(retries):
        try:
            with _SEC_RATE_LOCK:
                time.sleep(0.15)  # shared budget across historical fetch workers
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                if immutable:
                    cache.parent.mkdir(parents=True, exist_ok=True)
                    cache.write_bytes(raw)
                return raw
        except urllib.error.HTTPError as e:
            if e.code == 429:
                wait = 60 * (attempt + 1)
                print(f"  429 rate limited, waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
            elif e.code in (500, 502, 503, 504) and attempt + 1 < retries:
                time.sleep(attempt + 1)
            else:
                raise
        except (urllib.error.URLError, TimeoutError, ConnectionError):
            if attempt + 1 == retries:
                raise
            time.sleep(attempt + 1)
    raise RuntimeError(f"sec_fetch failed after {retries} retries: {url}")


def get_recent_filings(cik: str, include_archives: bool = False, include_restatements: bool = False) -> list[dict]:
    data = json.loads(sec_fetch(f"submissions/CIK{cik.zfill(10)}.json"))
    batches = [data["filings"]["recent"]]
    if include_archives:
        for archive in data["filings"].get("files", []):
            name = archive["name"]
            if not re.fullmatch(r"CIK[0-9]+-submissions-[0-9]+\.json", name):
                raise ValueError(f"Unexpected SEC archive filename: {name}")
            batches.append(json.loads(sec_fetch(f"submissions/{name}")))
    filings = {}
    for rec in batches:
        for i, form in enumerate(rec.get("form", [])):
            if form != "13F-HR" and not (include_restatements and form == "13F-HR/A"):
                continue
            accession = rec["accessionNumber"][i]
            filings[accession] = {
                "accession": accession.replace("-", ""), "accessionDashed": accession,
                "filingDate": rec["filingDate"][i], "reportDate": rec["reportDate"][i],
                **({"form": form, "primaryDocument": rec["primaryDocument"][i]} if include_restatements else {}),
            }
    ordered = sorted(filings.values(), key=lambda f: (f["reportDate"], f["filingDate"], f["accession"]), reverse=True)
    if not include_restatements:
        return ordered
    # Only a complete RESTATEMENT can replace a quarter. Additive amendments
    # contain a subset of securities and must never become a full portfolio.
    complete = {}
    for filing in ordered:
        period = filing['reportDate']
        if period in complete:
            continue
        if filing['form'] == '13F-HR/A':
            if period < '2013-06-30':
                continue  # pre-XML amendments require a separate legacy parser
            document = filing['primaryDocument'].split('/')[-1]
            if not re.fullmatch(r'[A-Za-z0-9_.-]+\.xml', document):
                raise ValueError('Unexpected amendment cover document')
            path = f"/Archives/edgar/data/{int(cik)}/{filing['accession']}/{document}"
            try:
                cover = ET.fromstring(sec_fetch(path))
                fields = {node.tag.split('}')[-1]: (node.text or '').strip() for node in cover.iter()}
                report = datetime.strptime(fields.get('periodOfReport', ''), '%m-%d-%Y').strftime('%Y-%m-%d')
            except (urllib.error.URLError, TimeoutError, ConnectionError):
                from sec_history_index import bind_submission
                submission = f"/Archives/edgar/data/{int(cik)}/{filing['accessionDashed']}.txt"
                bound = bind_submission(sec_fetch(submission), {**filing, 'submissionPath':submission}, cik)
                report = bound['reportDate']
                fields = {'amendmentType':bound['amendmentType']}
                path = submission
            if report != period:
                raise ValueError('Amendment cover period differs from SEC submissions')
            if fields.get('amendmentType', '').upper() != 'RESTATEMENT':
                continue
            filing.update(amendmentType='RESTATEMENT', coverSource='https://www.sec.gov'+path)
        complete[period] = filing
    return list(complete.values())


def missing_history_quarters(data):
    quarters = data.get("history", {}).get("quarters", [])
    indices = {int(m[1]) * 4 + int(m[2]) - 1 for q in quarters
               if (m := re.fullmatch(r"(\d{4}) Q([1-4])", q))}
    if not indices:
        return []
    return [f"{i // 4} Q{i % 4 + 1}" for i in range(min(indices), max(indices) + 1)
            if i not in indices]


def history_notice_quarters(coverage, config):
    """Silence only acknowledged archive holes, never new missing quarters."""
    quiet=set(config.get('historyGapNotices',{}).get('mutedQuarters',[]))
    coverage['quietMissingQuarters']=[q for q in coverage['missingQuarters'] if q in quiet]
    return [q for q in coverage['missingQuarters'] if q not in quiet]


def backfill_filing_provenance(data,filings):
    """Recover omitted source links from a matching, already verified unit proof."""
    from audit_13f_history import VERSION,digest
    history=data.get('history',{});sources=history.setdefault('filing_sources',{})
    for q,rows in history.get('holdings',{}).items():
        if q in sources:continue
        proof=history.get('valueAudit',{}).get(q,{})
        if proof.get('version')!=VERSION or proof.get('status')!='verified' or proof.get('normalizedHash')!=digest(rows):continue
        url=proof.get('source','')
        candidates=[f for f in filings if quarter_label(f['reportDate'])==q and (f['accession'] in url or f['accessionDashed'] in url)]
        if len(candidates)==1:sources[q]={**candidates[0],'url':url}


def backfill_history_gaps(cik, data, filings, consolidate=False, limit=4):
    """Repair bounded gaps on normal runs; failures remain gaps, never zeroes."""
    # Discover leading/trailing omissions too: interior-gap detection alone
    # silently loses years when an initial import starts late.
    backfill_filing_provenance(data,filings)
    stored=set(data.get('history',{}).get('holdings',{}))
    available={quarter_label(f['reportDate']) for f in filings}
    from legacy_13f import VERSION as legacy_version
    refresh_legacy={q for q,source in data.get('history',{}).get('filing_sources',{}).items() if source.get('url','').endswith('.txt') and source.get('parserVersion')!=legacy_version}
    actual_gaps=set(missing_history_quarters(data)) | (available-stored)
    missing=sorted(actual_gaps | refresh_legacy)
    prior_coverage=data.get("history",{}).get("coverage",{})
    errors, repaired, audit = {q:e for q,e in prior_coverage.get("errors",{}).items() if q in missing}, [], None
    attempts = data.get("history", {}).get("coverage", {}).get("attempts", {})
    if missing:
        known = {quarter_label(f["reportDate"]) for f in filings}
        if any(q not in known for q in missing):
            try:
                filings = filings + get_recent_filings(cik, include_archives=True)
            except Exception as exc:
                errors["archive_index"] = str(exc)
        by_quarter = {}
        for filing in filings:
            by_quarter.setdefault(quarter_label(filing["reportDate"]), filing)
        from audit_13f_history import discover_restatements
        replacements={}
        try:
            replacements=discover_restatements({'cik':cik},data['history'],set(missing),sec_fetch)
            by_quarter.update(replacements)
        except Exception as exc:
            data['history']['restatementLookupError']=str(exc)
        for q in missing:
            prior=data['history'].get('filing_sources',{}).get(q,{})
            if prior.get('amendmentType')=='RESTATEMENT' and all(prior.get(k) for k in ('accession','accessionDashed','filingDate')) and prior['filingDate']>=by_quarter.get(q,{}).get('filingDate','') and q not in replacements:
                by_quarter[q]=prior
        absent = [q for q in missing if q not in by_quarter]
        if absent:
            from sec_history_index import discover
            expanded, audit = discover(cik, absent, sec_fetch,
                data.get("history", {}).get("coverage", {}).get("expandedLookup"))
            for filing in expanded:
                by_quarter.setdefault(quarter_label(filing["reportDate"]), filing)
            print(f"  SEC historical index lookup: {audit['status']}, {len(expanded)} complete portfolio candidates")
        else:
            audit = None
        for quarter in missing:
            if quarter not in by_quarter:
                related = any(quarter_label(f["reportDate"]) == quarter for f in (audit or {}).get("candidateFilings", []))
                errors[quarter] = ("Related notice/additive amendment found; no complete portfolio verified" if related else
                    "Expanded SEC index lookup incomplete; will retry" if audit and audit["status"] == "partial" else
                    "No matching complete 13F portfolio in submissions and checked quarterly indexes; not a zero position")
        candidates = sorted((q for q in missing if q in by_quarter), key=lambda q: (q not in replacements, q not in actual_gaps, attempts.get(q, 0), q))
        selected=candidates[:limit]
        refresh_only=[q for q in candidates if q not in actual_gaps]
        if limit>1 and refresh_only and len(selected)==limit and all(q in actual_gaps for q in selected) and not all(q in replacements for q in selected):
            selected=selected[:-1]+refresh_only[:1]
        for quarter in selected:
            filing = by_quarter[quarter]
            attempts[quarter] = attempts.get(quarter, 0) + 1
            try:
                path = find_info_table_xml(filing.get("cik", cik), filing["accession"], filing["accessionDashed"])
                original = sec_fetch(path)
                if filing.get("expected13FFileNumber"):
                    from legacy_13f import verify_report_file_number
                    verify_report_file_number(original, filing["expected13FFileNumber"])
                rows = parse_holdings(original, consolidate=consolidate,
                                      filing_date=filing["filingDate"], retain_legacy_discrepancies=True)
                if not rows:
                    raise ValueError("Empty information table requires manual verification")
                from audit_13f_history import refresh_parser_proof
                if filing.get('amendmentType')!='RESTATEMENT':
                    refresh_parser_proof(data, quarter, rows, original)
                else:
                    # A replacement is a different primary document; the old
                    # price-unit proof cannot be silently attached to its rows.
                    data['history'].get('valueAudit',{}).pop(quarter,None)
                update_history(data, quarter, rows)
                data["history"].setdefault("filing_sources", {})[quarter] = {
                    **filing, "url": "https://www.sec.gov" + path,
                    **({"format":"legacy_13f","parserVersion":legacy_version} if path.endswith('.txt') else {}),
                    **({'sourceReconciliation': rows.reconciliation} if getattr(rows,'reconciliation',None) else {}),
                }
                repaired.append(quarter)
                errors.pop(quarter,None)
                print(f"  Backfilled {quarter}: {len(rows)} rows")
            except Exception as exc:
                errors[quarter] = str(exc)
    remaining = sorted(set(missing_history_quarters(data)) | (available-set(data.get("history",{}).get("holdings",{}))))
    data["history"]["coverage"] = {
        "checkedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "missingQuarters": remaining, "repairedThisRun": repaired, "errors": errors,
        "attempts": {q: attempts[q] for q in set(remaining) | (refresh_legacy-set(repaired)) if q in attempts},
        "pendingRefreshQuarters":sorted(refresh_legacy-set(repaired)),
        "expandedLookup": audit,
        "status": "gaps_remaining" if remaining else "continuous_within_stored_range",
    }
    if remaining:
        print(f"  WARNING: historical gaps remain: {remaining}; details: {errors}")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary and (missing or errors):
        with open(summary, "a") as f:
            f.write(f"\n### 13F history coverage — CIK {cik}\n"
                    f"- Repaired: {', '.join(repaired) or 'none'}\n"
                    f"- Remaining gaps: {', '.join(remaining) or 'none'}\n")
            if audit:
                f.write(f"- Expanded SEC quarterly-index lookup: {audit['status']}\n")
                f.write("- Scope: same CIK; two filing quarters after each missing report quarter. A search miss is not a zero holding.\n")
                for key, entry in audit['indexes'].items():
                    f.write(f"  - [{key}]({entry['url']}): {entry['status']} ({entry['checkedAt']})\n")


def quarter_label(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    q = (dt.month - 1) // 3 + 1
    return f"{dt.year} Q{q}"


def find_info_table_xml(cik: str, accession: str, accession_dashed: str) -> str:
    """尝试 .html 和 .htm 两种格式，提取 INFOTABLE XML 路径。"""
    if re.fullmatch(r'\d{10}-\d{2}-\d{6}',accession_dashed) and int(accession_dashed[11:13]) < 13:
        return f"/Archives/edgar/data/{int(cik)}/{accession_dashed}.txt"
    index_html = None
    for ext in ["-index.htm", "-index.html"]:
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
    # Pre-XML filings have a complete SGML submission, not an information XML.
    # The legacy reader requires entry-count and value-total reconciliation.
    if not re.search(r'INFORMATION TABLE', index_html, re.I) or not re.search(r'\.xml</a>', index_html, re.I):
        return f"/Archives/edgar/data/{cik}/{accession_dashed}.txt"
    # Fallback
    m2 = re.search(r"(\d{2})(\d)(\d)$", accession)
    if m2:
        return f"/Archives/edgar/data/{cik}/{accession}/13fhciq{m2.group(2)}{m2.group(3)}.xml"
    raise RuntimeError(f"Cannot find INFOTABLE XML for {accession_dashed}")


def resolve_ticker(name: str, cls: str, cusip: str = "") -> str:
    n = name.strip()
    c = (cusip or "").strip()
    if c in CUSIP_TICKER_MAP:
        return CUSIP_TICKER_MAP[c]
    is_a = "CL A" in (cls or "").upper()
    class_key = (n, is_a)
    if class_key in TICKER_CLASS_MAP:
        return TICKER_CLASS_MAP[class_key]
    if n in TICKER_MAP:
        return TICKER_MAP[n]
    return f"?{n}"


def parse_holdings(xml_bytes: bytes, consolidate: bool = False, *, filing_date: str, retain_legacy_discrepancies=False) -> list[dict]:
    """解析 INFOTABLE XML，返回 holdings 列表（已排序）。"""
    if b'<SEC-HEADER>' in xml_bytes[:20000] or b'<SEC-DOCUMENT>' in xml_bytes[:2000]:
        embedded=[]
        for block in re.findall(rb'<XML>(.*?)</XML>',xml_bytes,re.I|re.S):
            try:
                if ET.fromstring(block.strip()).tag=='{'+NS['ns']+'}informationTable':embedded.append(block.strip())
            except ET.ParseError:continue
        if len(embedded)>1:raise ValueError('Multiple information tables in the SEC submission require reconciliation')
        if embedded:
            return parse_holdings(embedded[0],consolidate=consolidate,filing_date=filing_date)
        from legacy_13f import parse_legacy, LegacyHoldings
        raw_entries = parse_legacy(xml_bytes, retain_source_discrepancies=retain_legacy_discrepancies)
        for row in raw_entries:
            row['ticker']=resolve_ticker(row['name'],row['cls'],row['cusip'])
        holdings=consolidate_holdings(raw_entries)
        for row in holdings:row['sector']=SECTORS.get(row['ticker'],'其他')
        return LegacyHoldings(sorted(holdings,key=lambda h:-h['value']), raw_entries.reconciliation)
    root = ET.fromstring(xml_bytes)
    if root.tag!='{'+NS['ns']+'}informationTable':raise ValueError('Unexpected SEC information-table XML root')
    filed=datetime.strptime(filing_date,'%Y-%m-%d')
    multiplier=1000 if filed<datetime(2023,1,3) else 1
    def whole(text,multiplier=1):
        value=Decimal(text)*multiplier
        if not value.is_finite() or value<0 or value!=value.to_integral():raise ValueError('Non-integral filed quantity after unit conversion')
        return int(value)
    raw_entries = []
    for info in root.findall("ns:infoTable", NS):
        name_el = info.find("ns:nameOfIssuer", NS)
        cls_el = info.find("ns:titleOfClass", NS)
        cusip_el = info.find("ns:cusip", NS)
        val_el = info.find("ns:value", NS)
        shares_el = info.find(".//ns:sshPrnamt", NS)
        share_type = info.findtext('.//ns:sshPrnamtType', default='SH', namespaces=NS).strip()
        put_call = info.findtext('ns:putCall', default='', namespaces=NS).strip()
        name_val = name_el.text.strip() if name_el is not None and name_el.text else ""
        cls_val = cls_el.text.strip() if cls_el is not None and cls_el.text else ""
        cusip_val = cusip_el.text.strip() if cusip_el is not None and cusip_el.text else ""
        shares = whole(shares_el.text) if shares_el is not None and shares_el.text else 0
        value = whole(val_el.text,multiplier) if val_el is not None and val_el.text else 0
        tk = resolve_ticker(name_val, cls_val, cusip_val)
        manager_reference=info.findtext('ns:otherManager',default='',namespaces=NS).strip()
        manager_ids=list(dict.fromkeys(re.findall(r'\d+',manager_reference)))
        discretion=info.findtext('ns:investmentDiscretion',default='',namespaces=NS).strip()
        voting_node=info.find('ns:votingAuthority',NS)
        evidence={}
        if discretion:evidence['investmentDiscretion']=discretion
        if voting_node is not None:
            evidence['votingAuthority']={key:whole(voting_node.findtext('ns:'+key,namespaces=NS)) for key in ('Sole','Shared','None') if voting_node.findtext('ns:'+key,namespaces=NS) is not None}

        raw_entries.append({
            "ticker": tk, "name": name_val, "cls": cls_val, "cusip": cusip_val,
            "shares": shares, "value": value,
            "shareType": share_type, "putCall": put_call, **evidence,
            # Keep every source line, including a blank/NONE other-manager
            # field. Omitting those lines makes mixed allocations incomplete.
            'managerAllocations':[{'managerIds':manager_ids,'shares':shares,'value':value,**evidence,
                                   **({'managerReference':manager_reference} if manager_reference else {})}],
        })

    # The filing date determines dollar/thousand units, including decimal
    # legacy values that become exact whole dollars after conversion.
    # https://www.sec.gov/divisions/investment/13ffaq (FAQs 61–62)

    # Every filing may contain multiple manager/discretion rows for one security.
    # Ticker alone cannot distinguish common shares, PUT/CALL and principal.
    holdings = consolidate_holdings(raw_entries)
    for e in holdings:
        e['sector'] = SECTORS.get(e['ticker'], '其他')

    holdings.sort(key=lambda h: h["value"], reverse=True)
    return holdings


def _quarter_sort_key(q_label: str) -> int:
    """'2024 Q3' -> 20243，用于按时间顺序排序（跨字段名不受影响）。"""
    year, q = q_label.split(" Q")
    return int(year) * 10 + int(q)


def _sort_history_in_place(data: dict):
    """history.quarters / values 是分批抓取追加写入的，顺序可能不是时间序
    （例如先抓近期再回填更早历史）。写盘前统一按季度时间顺序重排，
    避免前端图表/摘要按原始数组顺序读取时出现乱序。"""
    hist = data.get("history")
    if not hist or "quarters" not in hist or "values" not in hist:
        return
    quarters = hist["quarters"]
    values = hist["values"]
    if len(quarters) != len(values) or len(quarters) < 2:
        return
    order = sorted(range(len(quarters)), key=lambda i: _quarter_sort_key(quarters[i]))
    if order == list(range(len(quarters))):
        return  # 已经是时间序，无需改动
    hist["quarters"] = [quarters[i] for i in order]
    hist["values"] = [values[i] for i in order]


def save_data(path: str, data: dict):
    from reporting_scope import refresh
    config=next((c for c in INVESTOR_CONFIG.values() if c['path']==str(path)),{})
    if config.get('reportingTransition'):
        filing=data.get('history',{}).get('filing_sources',{}).get(data.get('current',{}).get('quarter'))
        if filing:refresh(data,config,filing,sec_fetch)
    _sort_history_in_place(data)
    holdings = [h for rows in data.get("history", {}).get("holdings", {}).values() for h in rows]
    actions = [action for action in VERIFIED_SPLITS if any(
        h.get("cusip") == action["cusip"] or h.get("ticker") == action["ticker"] for h in holdings)]
    for action in data.get('meta',{}).get('shareActions',[]):
        if action.get('sourceKind')!='market_share_split':continue
        if any(a.get('cusip')==action.get('cusip') and abs(a['factor']-action['factor'])<1e-9 and abs((date.fromisoformat(a['date'])-date.fromisoformat(action['date'])).days)<=10 for a in actions):continue
        actions.append(action)
    if actions:
        data.setdefault("meta", {})["shareActions"] = actions
    with open(path, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=None if len(holdings)>20000 else 2, separators=(',',':') if len(holdings)>20000 else None)
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

def investor_filings(config, full_mode=False):
    """Prefer the current reporter; retain dated, explicitly verified predecessors."""
    sources = [(config['cik'], None, None)] + [(old['cik'], old['beforePeriod'], old) for old in config.get('legacyFilers', [])]
    by_period = {}
    for cik, before, legacy in sources:
        if config.get('useRestatements'):
            rows = get_recent_filings(cik, include_archives=full_mode, include_restatements=True)
        else:
            rows = get_recent_filings(cik, include_archives=True) if full_mode else get_recent_filings(cik)
        for filing in rows:
            period = filing['reportDate']
            if (legacy and legacy.get('fromPeriod') and period < legacy['fromPeriod']) or (before and period >= before) or (not before and config.get('reportingFrom') and period < config['reportingFrom']):
                continue
            # Current reporting entity wins over a predecessor for the same period.
            by_period.setdefault(period, {**filing, 'cik': cik, **({'expected13FFileNumber':legacy['reportFileNumber']} if legacy and legacy.get('reportFileNumber') else {})})
    return sorted(by_period.values(), key=lambda f: (f['reportDate'], f['filingDate']), reverse=True)


def backfill_security_classes(data, filings, max_quarters=4):
    """Gradually repair legacy option/class history from original SEC tables."""
    holdings=data['current']['holdings']+data['current'].get('previousHoldings',[])
    by_name={}
    for h in holdings:
        by_name.setdefault(h.get('name') or h['ticker'],set()).add((h.get('cusip'),h.get('putCall','')))
    names={name for name,classes in by_name.items() if len(classes)>1}
    affected={h['ticker'] for h in holdings if h.get('putCall') or h.get('shareType','SH')!='SH' or (h.get('name') or h['ticker']) in names}
    if not affected: return
    data['meta']['instrumentHistoryTickers']=sorted(affected)
    history=data.get('history',{}).get('holdings',{})
    pending=[q for q,rows in history.items() if any(h['ticker'] in affected and ('putCall' not in h or 'shareType' not in h) for h in rows)]
    filings_by_quarter={quarter_label(f['reportDate']):f for f in reversed(filings)}
    errors={}
    for q in sorted(pending,reverse=True)[:max_quarters]:
        f=filings_by_quarter.get(q)
        if not f:
            errors[q]='No original filing found';continue
        try:
            path=find_info_table_xml(f['cik'],f['accession'],f['accessionDashed'])
            parsed=parse_holdings(sec_fetch(path),filing_date=f['filingDate'])
            for h in parsed:
                old=next((r for r in history[q] if r.get('cusip')==h['cusip']),{})
                for key in ('cnName','sector'):
                    if old.get(key): h[key]=old[key]
            update_history(data,q,parsed)
            data['history'].setdefault('filing_sources',{})[q]={**f,'url':'https://www.sec.gov'+path}
        except Exception as exc: errors[q]=str(exc)
    pending=[q for q,rows in history.items() if any(h['ticker'] in affected and ('putCall' not in h or 'shareType' not in h) for h in rows)]
    known=[q for q in sorted(history) if not pending or q>max(pending)]
    data['meta']['instrumentHistoryFrom']=known[0] if known else data['current']['prevQuarter']
    data['history']['instrumentVerification']={'pendingQuarters':sorted(pending),'errors':errors,'checkedAt':datetime.now(timezone.utc).isoformat()}


def backfill_restatements(data, filings, cik, consolidate=False, limit=4):
    """Replace stored original quarters when a verified complete restatement exists."""
    sources = data['history'].setdefault('filing_sources', {})
    repaired = []
    for filing in filings:
        quarter = quarter_label(filing['reportDate'])
        if filing.get('amendmentType') != 'RESTATEMENT' or sources.get(quarter, {}).get('accession') == filing['accession']:
            continue
        if len(repaired)>=limit:break
        path = find_info_table_xml(filing.get('cik', cik), filing['accession'], filing['accessionDashed'])
        rows = parse_holdings(sec_fetch(path), consolidate=consolidate, filing_date=filing['filingDate'])
        data['history'].get('valueAudit',{}).pop(quarter,None)
        update_history(data, quarter, rows)
        sources[quarter] = {**filing, 'url':'https://www.sec.gov'+path}
        repaired.append(quarter)
    if repaired:
        history = data['history']['holdings']
        ordered = sorted(history)
        for previous, current in zip(ordered, ordered[1:]):
            attach_previous(history[current], history[previous], previous_quarter=previous, current_quarter=current)
        print('  Applied complete restatements:', ', '.join(repaired))
    return repaired


def process_investor(key: str, config: dict, full_mode: bool):
    print(f"\n{'='*60}")
    print(f"Processing {key.upper()}: {config['manager']}")
    print(f"CIK: {config['cik']}")
    print(f"{'='*60}")

    cik = config["cik"]
    consolidate = config.get("consolidate", False)
    filings = investor_filings(config, True)
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

    data['meta'].update(manager=config['manager'], managerCIK=cik.zfill(10))
    if config.get('legacyFilers'):
        data['meta']['legacyFilers'] = config['legacyFilers']
    if config.get('reportingTransition'):
        data['meta']['reportingTransition'] = config['reportingTransition']
    if full_mode:
        return process_full(key, config, filings, data)

    # ── 普通模式：只抓最新两期，更新 current ──
    cur_f, prev_f = filings[0], filings[1]
    print(f"  Latest:   {quarter_label(cur_f['reportDate'])} (filed {cur_f['filingDate']})")
    print(f"  Previous: {quarter_label(prev_f['reportDate'])} (filed {prev_f['filingDate']})")

    cur_path = find_info_table_xml(cur_f.get('cik', cik), cur_f['accession'], cur_f['accessionDashed'])
    prev_path = find_info_table_xml(prev_f.get('cik', cik), prev_f['accession'], prev_f['accessionDashed'])
    cur_xml  = sec_fetch(cur_path)
    prev_xml = sec_fetch(prev_path)
    cur_holdings  = parse_holdings(cur_xml, consolidate=consolidate, filing_date=cur_f["filingDate"])
    prev_holdings = parse_holdings(prev_xml, consolidate=consolidate, filing_date=prev_f["filingDate"])

    attach_previous(cur_holdings, prev_holdings,
                    previous_quarter=quarter_label(prev_f["reportDate"]),
                    current_quarter=quarter_label(cur_f["reportDate"]))

    total      = sum(h["value"] for h in cur_holdings)
    prev_total = sum(h["value"] for h in prev_holdings)

    quality = data.get("current", {}).get("valueQuality") if data.get("current", {}).get("quarter") == quarter_label(cur_f["reportDate"]) else None
    data["current"] = {
        "quarter":        quarter_label(cur_f["reportDate"]),
        "filingDate":     cur_f["filingDate"],
        "sourceFiling":   f"https://www.sec.gov/Archives/edgar/data/{int(cur_f.get('cik', cik))}/{cur_f['accession']}/{cur_f['accessionDashed']}-index.html",
        "periodEnd":      cur_f["reportDate"],
        "totalValue":     total,
        "holdings":       cur_holdings,
        "prevQuarter":    quarter_label(prev_f["reportDate"]),
        "previousHoldings": prev_holdings,
        "prevTotalValue": prev_total,
    }
    if quality: data["current"]["valueQuality"] = quality
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    update_history(data, quarter_label(prev_f["reportDate"]), prev_holdings)
    update_history(data, quarter_label(cur_f["reportDate"]), cur_holdings)
    data['history'].setdefault('filing_sources', {}).update({
        quarter_label(cur_f['reportDate']): {**cur_f, 'url': 'https://www.sec.gov' + cur_path},
        quarter_label(prev_f['reportDate']): {**prev_f, 'url': 'https://www.sec.gov' + prev_path},
    })
    if config.get('useRestatements'):
        backfill_restatements(data, filings, cik, consolidate)
    backfill_security_classes(data, filings)
    backfill_history_gaps(cik, data, filings, consolidate)
    remaining = history_notice_quarters(data["history"]["coverage"],config)
    if remaining:
        from update_status import record_source_warning, record_source_notice
        step = "akre_greenberg_13f" if key in ("akre", "greenberg") else f"{key}_13f"
        audit = data["history"]["coverage"].get("expandedLookup") or {}
        source_gap = audit.get("status") == "checked" and all(str(data["history"]["coverage"]["errors"].get(q, "")).startswith(("No matching complete 13F portfolio", "Related notice/additive amendment found")) for q in remaining)
        reason = "已补查SEC历史索引，仍无可用原始持仓报告" if source_gap else "补查未完成或原表未核实，后续重试"
        record = record_source_notice if source_gap else record_source_warning
        record(step, f"{key} 历史缺 {len(remaining)} 季（{', '.join(remaining)}）：{reason}；不作零持仓")

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
    refreshed = 0

    def fetch_quarter(filing):
        path = find_info_table_xml(filing.get('cik', cik), filing['accession'], filing['accessionDashed'])
        rows = parse_holdings(sec_fetch(path), consolidate=consolidate, filing_date=filing['filingDate'])
        return path, rows

    # A bounded pool speeds initial onboarding; immutable SEC originals are cached
    # locally, so an interrupted backfill resumes without re-downloading history.
    pool = ThreadPoolExecutor(max_workers=max(1, min(3, config.get('fullArchiveWorkers', 1))))
    futures = {f['accession']:pool.submit(fetch_quarter, f) for f in filings_sorted}

    for i, f in enumerate(filings_sorted):
        q_label = quarter_label(f["reportDate"])

        print(f"  [{i+1}/{len(filings_sorted)}] Fetching {q_label} (filed {f['filingDate']})...")
        try:
            xml_path, holdings = futures[f['accession']].result()
            all_fetched[q_label] = holdings

            # 找最近的前一期用于 prevShares
            prev_q = None
            for j in range(i - 1, -1, -1):
                pql = quarter_label(filings_sorted[j]["reportDate"])
                if pql in all_fetched:
                    prev_q = pql
                    break

            if prev_q:
                attach_previous(holdings,all_fetched[prev_q],previous_quarter=prev_q,current_quarter=q_label)
            else:
                for h in holdings: h.update(prevShares=None,prevValue=None)
            data['history'].setdefault('filing_sources',{})[q_label]={**f,'url':'https://www.sec.gov'+xml_path}

            total = sum(h["value"] for h in holdings)
            update_history(data, q_label, holdings)
            if q_label in existing_quarters:
                refreshed += 1
            else:
                new_quarters += 1
            print(f"    -> {len(holdings)} holdings, ${total:,.0f}")
        except Exception as e:
            print(f"    -> ERROR: {e}")
            continue

    pool.shutdown(wait=True)

    # 更新 current 为最新一期
    latest = filings[0]
    latest_q = quarter_label(latest["reportDate"])
    if latest_q in all_fetched:
        latest_holdings = all_fetched[latest_q]
    else:
        xml_bytes = sec_fetch(find_info_table_xml(latest.get('cik', cik), latest["accession"], latest["accessionDashed"]))
        latest_holdings = parse_holdings(xml_bytes, consolidate=consolidate, filing_date=latest["filingDate"])

    prev_f = filings[1]
    prev_q = quarter_label(prev_f["reportDate"])
    if prev_q in all_fetched:
        prev_holdings = all_fetched[prev_q]
    else:
        xml_bytes = sec_fetch(find_info_table_xml(prev_f.get('cik', cik), prev_f["accession"], prev_f["accessionDashed"]))
        prev_holdings = parse_holdings(xml_bytes, consolidate=consolidate, filing_date=prev_f["filingDate"])

    attach_previous(latest_holdings, prev_holdings,
                    previous_quarter=prev_q, current_quarter=latest_q)

    latest_total = sum(h["value"] for h in latest_holdings)
    quality = data.get("current", {}).get("valueQuality") if data.get("current", {}).get("quarter") == latest_q else None
    data["current"] = {
        "quarter":        quarter_label(latest["reportDate"]),
        "filingDate":     latest["filingDate"],
        "sourceFiling":   f"https://www.sec.gov/Archives/edgar/data/{int(latest.get('cik', cik))}/{latest['accession']}/{latest['accessionDashed']}-index.html",
        "periodEnd":      latest["reportDate"],
        "totalValue":     latest_total,
        "holdings":       latest_holdings,
        "prevQuarter":    quarter_label(prev_f["reportDate"]),
        "previousHoldings": prev_holdings,
        "prevTotalValue": sum(h["value"] for h in prev_holdings),
    }
    if quality: data["current"]["valueQuality"] = quality
    data["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    update_history(data, prev_q, prev_holdings)
    update_history(data, latest_q, latest_holdings)

    save_data(config["path"], data)
    warn_unmapped(data)
    print(f"\nDone: {new_quarters} new quarters, {refreshed} refreshed.")
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

