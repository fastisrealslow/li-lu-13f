#!/usr/bin/env python3
"""
monitor_hk_disclosures.py
--------------------------
监控港交所权益披露系统（DI）中各投资者的港股持仓变动。

策略：
1. 访问首页自动获取 session cookie（无需硬编码）
2. 按实体名/人名搜索披露通知列表
3. 从 URL 参数 scpid2(sid) 自动反查股票代号
4. 发现新股票自动写入对应的 *_hk.json，Actions Summary 告警

已验证可监控的投资者（2026-06-30）：
- 段永平：H&H International Investment → 泡泡玛特(09992)
- 李录：  Li Lu → 中国中车、中国邮储银行、比亚迪 H股
- 巴菲特：Berkshire Hathaway → 比亚迪 H股
- 帕伯莱/斯皮尔：港交所无≥5%披露记录
"""

import json, os, re, sys, time, http.cookiejar
from datetime import datetime, timezone, timedelta
from urllib.request import build_opener, HTTPCookieProcessor
from urllib.parse import urlencode

OUT_FILE = "alerts_hk_persons.json"
BASE_URL = "https://di.hkex.com.hk/di"

# 各投资者监控配置
# exact_match: True 时只接受实体名完全包含 keyword 的结果（过滤同名噪音）
WATCH_CONFIG = [
    {
        "investor": "duan",
        "hk_file":  "duan_hk.json",
        "persons": [
            {"name": "H&H International Investment", "exact": "H&H International Investment"},
            {"name": "Duan Yong Ping",               "exact": "Duan Yong Ping"},
        ],
    },
    {
        "investor": "lilu",   # 李录（对应 hk_holdings.json）
        "hk_file":  "hk_holdings.json",
        "persons": [
            {"name": "Li Lu", "exact": "Li Lu"},
            {"name": "Himalaya Capital", "exact": "Himalaya"},
        ],
    },
    {
        "investor": "buffett",
        "hk_file":  "buffett_hk.json",
        "persons": [
            {"name": "Berkshire Hathaway", "exact": "Berkshire Hathaway"},
        ],
    },
    {
        "investor": "pabrai",
        "hk_file":  "pabrai_hk.json",
        "persons": [
            {"name": "Mohnish Pabrai",    "exact": "Pabrai"},
            {"name": "Dalal Street",      "exact": "Dalal Street"},
        ],
    },
    {
        "investor": "akre",
        "hk_file":  "akre_hk.json",
        "persons": [
            {"name": "Chuck Akre",        "exact": "Akre"},
            {"name": "Akre Capital",      "exact": "Akre Capital"},
        ],
    },
]

today     = datetime.now()
date_to   = today.strftime("%d/%m/%Y")
date_from = (today - timedelta(days=3650)).strftime("%d/%m/%Y")  # 最近10年

HEADERS = [
    ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/127.0.0.0 Safari/537.36"),
    ("Accept",     "text/html,application/xhtml+xml,*/*;q=0.8"),
    ("Accept-Language", "zh-CN,zh;q=0.9,en;q=0.8"),
]

_opener_ref = None


def get_opener():
    jar = http.cookiejar.CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    opener.addheaders = HEADERS
    try:
        opener.open(f"{BASE_URL}/NSSrchPerson.aspx?src=MAIN&lang=ZH&g_lang=zh-HK", timeout=15)
        cookies = {c.name for c in jar}
        print(f"  获得 cookies: {cookies}")
        return opener
    except Exception as e:
        print(f"  获取 session 失败: {e}", file=sys.stderr)
        return None


def search_person(opener, person_name):
    params = urlencode({
        "sa1": "pl", "scsd": date_from, "sced": date_to,
        "pn": person_name, "src": "MAIN", "lang": "ZH", "g_lang": "zh-HK",
    })
    url = f"{BASE_URL}/NSSrchPersonList.aspx?{params}"
    print(f"  GET {url}")
    try:
        resp = opener.open(url, timeout=15)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  请求失败: {e}", file=sys.stderr)
        return None


# 已知 sid → ticker 缓存，避免重复反查
_sid_cache = {
    "312028": "09992.HK",  # 泡泡玛特
    "6893":   "00700.HK",  # 腾讯控股
    "2508":   "01211.HK",  # 比亚迪 H股
    "24061":  "01766.HK",  # 中国中车 H股
    "142788": "01658.HK",  # 中国邮储银行 H股
}


def normalize_hk_ticker(code):
    """统一港股 ticker 格式：5位前缀，如 1211.HK → 01211.HK"""
    if not code:
        return code
    num = code.upper().replace(".HK", "")
    return num.zfill(5) + ".HK"


_pct_cache = {}  # noticeUrl -> pct str


def fetch_latest_pct(notice_url, opener):
    """从 NSNoticePersonList 列表页拿最新一条投Form链接，再进详情页拿持股比例"""
    if notice_url in _pct_cache:
        return _pct_cache[notice_url]
    try:
        resp = opener.open(notice_url, timeout=12)  # notice_url 已是完整 URL
        html = resp.read().decode("utf-8", errors="replace")
        time.sleep(0.5)
        # 找第一条记录的详情链接 NSForm1.aspx 或 NSForm2.aspx
        form_m = re.search(r'href="(NSForm[12]\.aspx[^"]+)"', html)
        if not form_m:
            return ""
        form_path = form_m.group(1).replace("&amp;", "&")
        form_url = f"{BASE_URL}/{form_path}"
        resp2 = opener.open(form_url, timeout=12)
        html2 = resp2.read().decode("utf-8", errors="replace")
        time.sleep(0.5)
        # 在 Form 表单里找持股比例（通常在 "% of relevant share capital" 附近）
        pct_m = re.search(
            r'(?:百分比|% of relevant share capital|% (?:of|of\ the)\ relevant|佔相关股本)[^\d]{0,30}'
            r'(\d{1,3}\.\d{1,4})',
            html2, re.I)
        if pct_m:
            result = pct_m.group(1) + "%"
            _pct_cache[notice_url] = result
            return result
    except Exception as e:
        print(f"  fetch_latest_pct 失败: {e}")
    _pct_cache[notice_url] = ""
    return ""


def resolve_sid_to_ticker(sid):
    """未知 sid：访问港交所大股东页面反查股票代号"""
    global _opener_ref
    if sid in _sid_cache:
        return _sid_cache[sid]
    if not _opener_ref:
        return ""
    try:
        url = f"{BASE_URL}/NSAllSSList.aspx?sa2=as&sid={sid}&sd={date_to}&ed={date_to}&sa1=cl&src=MAIN&lang=ZH"
        resp = _opener_ref.open(url, timeout=12)
        html = resp.read().decode("utf-8", errors="replace")
        m = re.search(r'[?&]sc=([0-9]{4,5})', html)
        if m:
            ticker = normalize_hk_ticker(m.group(1) + ".HK")
            _sid_cache[sid] = ticker
            print(f"  sid {sid} → {ticker}")
            return ticker
    except Exception as e:
        print(f"  resolve_sid {sid} 失败: {e}")
    return ""


def parse_holdings(html, exact_keyword, investor_label):
    """
    解析搜索结果页，只接受实体名包含 exact_keyword 的行（过滤同名噪音）。
    从 href 的 scpid2=sid 参数反查股票代号。
    """
    if not html:
        return []

    holdings = []
    pattern = re.compile(
        r'href="(NSNoticePersonList\.aspx[^"]+)"[^>]*>'
        r'([^<]+)</a></td><td[^>]*>([^<]{4,60})</td>',
        re.IGNORECASE
    )
    for m in pattern.finditer(html):
        notice_url = m.group(1).replace("&amp;", "&")
        entity     = m.group(2).replace("&amp;", "&").strip()
        stock_name = m.group(3).strip()

        # 过滤噪音：实体名必须包含 exact_keyword
        if exact_keyword.lower() not in entity.lower():
            continue

        sid_m  = re.search(r'scpid2=([0-9]+)', notice_url)
        sid    = sid_m.group(1) if sid_m else ""
        ticker = resolve_sid_to_ticker(sid) if sid else ""

        holdings.append({
            "entity":    entity[:60],
            "stockName": stock_name[:40],
            "ticker":    ticker,
            "sid":       sid,
            "noticeUrl": f"{BASE_URL}/{notice_url}",
            "investor":  investor_label,
            "foundDate": today.strftime("%Y-%m-%d"),
        })
    return holdings


def update_hk_file(hk_file, all_holdings):
    """把新持仓合并进对应的 *_hk.json"""
    if not os.path.exists(hk_file):
        print(f"  {hk_file} 不存在，跳过")
        return []
    try:
        data = json.load(open(hk_file))
    except:
        return []

    # 兼容两种结构：有 holdings 字段 或 直接是列表
    holdings_list = data.get("holdings", data if isinstance(data, list) else [])
    # 先规范化所有现有 ticker
    for h in holdings_list:
        h["ticker"] = normalize_hk_ticker(h.get("ticker",""))
    existing_tickers = {h.get("ticker","") for h in holdings_list}
    new_added = []

    for h in all_holdings:
        ticker = h.get("ticker", "")
        if not ticker:
            continue
        if ticker in existing_tickers:
            # 更新已有条目的 last_disclosure 和比例
            for existing in holdings_list:
                if existing.get("ticker") == ticker:
                    existing["last_disclosure"] = today.strftime("%Y")
                    existing["current_status"]  = "active"
                    # 尝试更新持股比例
                    if h.get("noticeUrl") and _opener_ref:
                        pct = fetch_latest_pct(h["noticeUrl"], _opener_ref)
                        if pct:
                            existing["pct"] = pct
                            existing["pct_date"] = today.strftime("%Y-%m-%d")
                            print(f"  📊 {ticker} 持股比例: {pct}")
            continue

        # 新股票自动追加
        pct = ""
        if h.get("noticeUrl") and _opener_ref:
            pct = fetch_latest_pct(h["noticeUrl"], _opener_ref)
        new_entry = {
            "ticker":           ticker,
            "name":             h["stockName"],
            "cnName":           h["stockName"],
            "sector":           "",
            "entity":           h["entity"],
            "pct":              pct,
            "pct_date":         today.strftime("%Y-%m-%d") if pct else "",
            "first_disclosure": today.strftime("%Y"),
            "last_disclosure":  today.strftime("%Y"),
            "peak_known":       False,
            "peak_shares":      0,
            "peak_pct":         pct,
            "buy_price_note":   "",
            "current_status":   "active",
            "notes":            f"来源：港交所权益披露系统（di.hkex.com.hk）。持股达到或超过5%时触发强制披露，首次披露日期：{today.strftime('%Y-%m-%d')}。",
        }
        holdings_list.append(new_entry)
        existing_tickers.add(ticker)
        new_added.append(f"{ticker} {h['stockName']}")
        print(f"  ✅ 新增到 {hk_file}: {ticker} {h['stockName']}{' ' + pct if pct else ''}")

    # 本次抓到的 ticker 集合
    found_tickers = {normalize_hk_ticker(h.get("ticker","")) for h in all_holdings if h.get("ticker")}
    # 对「本次未搜到」但之前 status=active 的条目降级为 below_5pct
    for existing in holdings_list:
        t = existing.get("ticker","")
        if existing.get("current_status") == "active" and t and t not in found_tickers:
            existing["current_status"] = "below_5pct"
            print(f"  ⬇️  {t} {existing.get('name','')[:15]} 降级为 below_5pct（本次未搜到）")

    if "holdings" in data:
        data["holdings"] = holdings_list
    data["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(hk_file, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  {hk_file} 已更新（新增 {len(new_added)} 条）")
    return new_added


def load_existing():
    if os.path.exists(OUT_FILE):
        try:
            return json.load(open(OUT_FILE))
        except:
            pass
    return {"updatedAt": "", "knownStocks": {}, "snapshots": []}


def main():
    global _opener_ref
    print("=== monitor_hk_disclosures.py ===")
    print(f"搜索范围: {date_from} ~ {date_to}")

    existing     = load_existing()
    # knownStocks 改为 dict: investor -> set of tickers
    known_map    = existing.get("knownStocks", {})
    all_new      = []

    print("\n获取 session...")
    opener = get_opener()
    if not opener:
        print("❌ 无法访问 di.hkex.com.hk，跳过")
        sys.exit(0)
    _opener_ref = opener
    time.sleep(1)

    snapshot = {"date": today.strftime("%Y-%m-%d"), "investors": {}}

    for config in WATCH_CONFIG:
        investor  = config["investor"]
        hk_file   = config["hk_file"]
        known_set = set(known_map.get(investor, []))

        print(f"\n{'='*40}")
        print(f"投资者: {investor}  文件: {hk_file}")

        seen_entities = set()
        investor_holdings = []

        for person in config["persons"]:
            name    = person["name"]
            exact   = person["exact"]
            label   = f"{investor}({name})"

            print(f"\n  搜索: {name}")
            html = search_person(opener, name)
            if not html:
                continue

            holdings = parse_holdings(html, exact, label)
            print(f"  解析到: {len(holdings)} 条")

            for h in holdings:
                key = h["ticker"] or h["stockName"][:20]
                if key in seen_entities:
                    continue
                seen_entities.add(key)
                investor_holdings.append(h)
                print(f"  → {h['entity']} | {h['stockName']} | {h['ticker']}")

                if key not in known_set:
                    all_new.append({**h, "investor": investor})
                    known_set.add(key)
                    print(f"  🆕 新持股!")

            time.sleep(1.5)

        snapshot["investors"][investor] = investor_holdings
        known_map[investor] = list(known_set)

        # 写入对应 hk_file
        if investor_holdings:
            print(f"\n  更新 {hk_file}...")
            update_hk_file(hk_file, investor_holdings)

    # 保存状态
    existing["updatedAt"]   = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    existing["knownStocks"] = known_map
    existing["snapshots"].append(snapshot)
    existing["snapshots"] = existing["snapshots"][-90:]
    with open(OUT_FILE, "w") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"\n保存到 {OUT_FILE}")

    if all_new:
        print(f"\n🔔 发现 {len(all_new)} 条新持股！")
        summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "")
        if summary_file:
            with open(summary_file, "a") as f:
                f.write(f"\n## 🔔 港股新披露\n")
                for h in all_new:
                    f.write(f"- **{h['investor']}** {h['stockName']} `{h['ticker']}` ({h['entity']}) {h['foundDate']}\n")
    else:
        print("✅ 无新持股")


if __name__ == "__main__":
    main()
