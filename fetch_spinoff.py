#!/usr/bin/env python3
"""
fetch_spinoff.py
----------------
从港交所新闻披露平台搜索分拆公告，按公司合并，写入 spinoff.json。

API（从浏览器 Network 面板确认）：
  POST https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=zh
  字段：lang=zh, category=0, market=SEHK, searchType=1,
        documentType=-1, t1code=10000, t2Gcode=-2, t2code=-2,
        stockId=-1, from=YYYYMMDD, to=YYYYMMDD, title=关键词

结果结构（已验证）：
  <td class="release-time">26/06/2026 19:20</td>
  <td class="stock-short-code">00656</td>
  <td class="stock-short-name">復星國際</td>
  <td><a href="/listedco/.../xxx_c.pdf">标题</a></td>

合并逻辑：同一股票代码的多条公告合并为一个事件，按时间线排列。
过滤：现价 < 0.5 HKD 的仙股排除。
"""

import json, os, re, sys, time, http.cookiejar, urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.request import build_opener, HTTPCookieProcessor, Request

OUT_FILE = "spinoff.json"
BASE_URL = "https://www1.hkexnews.hk"

today     = datetime.now()
date_to   = today.strftime("%Y%m%d")
date_from = (today - timedelta(days=365)).strftime("%Y%m%d")

KEYWORDS = ["分拆", "spin-off", "demerger", "實物分派", "以介紹方式"]

# 明确排除：已确认是合股重组而非分拆的公司（股份代码）
# 注：优先靠 is_pure_split + 市值过滤自动拦截；仅将过滤逻辑无法覆盖的模糊案例加入此表
BLACKLIST_CODES = {
    # 08516 广駿/中盈：靠市值 < 2亿自动过滤，无需硬编码
}

# 手动标注介绍上市（公告标题无关键词但正文已确认）
KNOWN_INTRO = {
    "00308",  # 香港中旅 → 中旅港澳文旅控股：实物分派+介绍方式（新浪财经 2026-05-20 确认）
}


def get_opener():
    jar = http.cookiejar.CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    opener.addheaders = [
        ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"),
        ("Accept", "text/html,application/xhtml+xml,*/*;q=0.8"),
        ("Accept-Language", "zh-CN,zh;q=0.9"),
    ]
    try:
        opener.open(f"{BASE_URL}/search/titlesearch.xhtml?lang=zh", timeout=15)
    except Exception as e:
        print(f"  首页访问失败: {e}", file=sys.stderr)
    return opener


def search_keyword(opener, keyword):
    form_data = urllib.parse.urlencode({
        "lang": "zh", "category": "0", "market": "SEHK",
        "searchType": "1", "documentType": "-1",
        "t1code": "10000", "t2Gcode": "-2", "t2code": "-2",
        "stockId": "-1", "from": date_from, "to": date_to,
        "MB-Daterange": "0", "title": keyword,
    }).encode()
    req = Request(
        f"{BASE_URL}/search/titlesearch.xhtml?lang=zh",
        data=form_data,
        headers={
            "Content-Type":  "application/x-www-form-urlencoded",
            "Referer":       f"{BASE_URL}/search/titlesearch.xhtml?lang=zh",
            "Origin":        BASE_URL,
            "User-Agent":    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/127",
            "Accept":        "text/html,*/*",
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
    )
    try:
        resp = opener.open(req, timeout=20)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  搜索「{keyword}」失败: {e}", file=sys.stderr)
        return ""


def parse_rows(html):
    """解析结果页，返回原始公告列表"""
    items = []
    total_m = re.search(r'共有\s*(\d+)\s*[紀记]錄|Total records[^:]*:\s*(\d+)', html)
    total = int(total_m.group(1) or total_m.group(2)) if total_m else 0
    print(f"  总记录数: {total}")
    if total == 0:
        return items

    trs = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL)
    for tr in trs:
        # 时间
        time_m = re.search(r'release-time[^>]*>[^<]*<[^>]+>[^<]*</span>\s*([\d/: ]{15,20})', tr)
        if not time_m:
            time_m = re.search(r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2})', tr)
        # 股票代码
        code_m = re.search(r'stock-short-code[^>]*>[^<]*<[^>]+>[^<]*</span>\s*(\d{5})', tr)
        if not code_m:
            code_m = re.search(r'<td[^>]*>\s*(\d{5})\s*</td>', tr)
        # 股份简称
        name_m = re.search(r'stock-short-name[^>]*>[^<]*<[^>]+>[^<]*</span>\s*([^\s<][^<]{1,30})', tr)
        # PDF链接和标题
        pdf_m = re.search(r'href=["\']([^"\']+\.pdf[^"\']*)["\'][^>]*>\s*([^<]{5,200})', tr, re.IGNORECASE)

        if not (time_m and code_m and pdf_m):
            continue

        pub_time   = time_m.group(1).strip()
        stock_code = code_m.group(1).strip()
        stock_name = name_m.group(1).strip() if name_m else ""
        doc_url    = pdf_m.group(1).strip()
        title      = re.sub(r'\s+', ' ', pdf_m.group(2)).strip()

        if not doc_url.startswith("http"):
            doc_url = BASE_URL + doc_url

        # 日期格式统一：DD/MM/YYYY → YYYY-MM-DD
        date_part = pub_time[:10]  # 26/06/2026
        try:
            d, m, y = date_part.split("/")
            date_iso = f"{y}-{m}-{d}"
        except Exception:
            date_iso = date_part

        items.append({
            "stockCode": stock_code,
            "stockName": stock_name,
            "ticker":    stock_code + ".HK",
            "title":     title[:180],
            "date":      date_iso,
            "pubTime":   pub_time,
            "docUrl":    doc_url,
        })

    return items


def _classify_spinoff_type(titles):
    """
    识别分拆类型，返回 dict:
      { code, exchange_zh, exchange_en, label_zh, label_en, is_reit }

    类型优先级：
      1. REIT / 基础设施基金（子公司分拆为基金上市，非普通股）
      2. 港交所主板 IPO
      3. A股深交所 IPO
      4. A股上交所 IPO
      5. A股（未明确交易所）
      6. 其他交易所
      7. 直接分拆（无独立上市）
    """
    combined = ' '.join(titles)

    # REIT 判断：分拆目标明确是基金/REITs，而非子公司股票
    is_reit = any(kw in combined for kw in [
        '不動產投資信託基金', '基礎設施證券投資基金', '商業不動產證券投資基金',
        'REITs', 'REIT', '公募基金', '基礎設施基金',
    ])
    # 同时包含「子公司」「独立上市」等关键词时优先按 IPO 处理（非 REIT）
    has_subsidiary_ipo = any(kw in combined for kw in ['子公司', '獨立上市', '独立上市']) and \
                         not any(kw in combined for kw in ['信託基金', '證券投資基金'])
    if has_subsidiary_ipo:
        is_reit = False

    if is_reit:
        if '深圳證券' in combined or '深交所' in combined:
            return dict(code='reit_sz', exchange_zh='深交所', exchange_en='SZSE',
                        label_zh='REIT·深交所', label_en='REIT·SZSE', is_reit=True)
        if '上海證券' in combined or '上交所' in combined:
            return dict(code='reit_sh', exchange_zh='上交所', exchange_en='SSE',
                        label_zh='REIT·上交所', label_en='REIT·SSE', is_reit=True)
        return dict(code='reit', exchange_zh='REITs', exchange_en='REITs',
                    label_zh='REIT上市', label_en='REIT Listing', is_reit=True)

    # 介绍上市（实物分派，不发行新股不融资）——优先于港交所判断
    # 排除条件：标题同时含「建議分拆...並於...獨立上市」= 主体是IPO，实物分派只是附加安排
    is_introduction = any(kw in combined for kw in [
        '介绍方式', '以介绍式', 'listing by introduction',
        'distribution in specie', '实物分配',
        '以介紹方式', '介紹上市',   # 繁体
    ])
    # 「实物分派」单独出现才算介绍上市；若同时有「建議分拆...獨立上市」= IPO+附加实物分派
    has_ipo_spinoff = bool(re.search(r'建[議议]分拆.{0,50}(?:獨立上市|独立上市|獨立上市)', combined))
    if is_introduction and not has_ipo_spinoff:
        return dict(code='intro_hk', exchange_zh='港交所', exchange_en='HKEX',
                    label_zh='介紹上市', label_en='Intro Listing', is_reit=False)
    if '實物分派' in combined and not has_ipo_spinoff:
        return dict(code='intro_hk', exchange_zh='港交所', exchange_en='HKEX',
                    label_zh='介紹上市', label_en='Intro Listing', is_reit=False)

    # 港交所
    if any(kw in combined for kw in ['聯交所', '香港聯合交易所', '港交所', '香港主板']):
        return dict(code='ipo_hk', exchange_zh='港交所', exchange_en='HKEX',
                    label_zh='分拆·港股IPO', label_en='Spinoff·HKEX IPO', is_reit=False)

    # A股
    if '深圳證券' in combined or '深交所' in combined:
        return dict(code='ipo_a_sz', exchange_zh='深交所', exchange_en='SZSE',
                    label_zh='分拆·A股深交所', label_en='Spinoff·A-Share SZSE', is_reit=False)
    if '上海證券' in combined or '上交所' in combined:
        return dict(code='ipo_a_sh', exchange_zh='上交所', exchange_en='SSE',
                    label_zh='分拆·A股上交所', label_en='Spinoff·A-Share SSE', is_reit=False)
    if 'A股' in combined:
        return dict(code='ipo_a', exchange_zh='A股', exchange_en='A-Share',
                    label_zh='分拆·A股上市', label_en='Spinoff·A-Share IPO', is_reit=False)

    # 有上市迹象但交易所不明
    if any(kw in combined for kw in ['獨立上市', '独立上市', '上市', 'IPO', '挂牌']):
        return dict(code='ipo_other', exchange_zh='待定', exchange_en='TBD',
                    label_zh='分拆·独立上市', label_en='Spinoff·IPO', is_reit=False)

    # 直接分拆（无独立上市）
    return dict(code='split_direct', exchange_zh='直接分拆', exchange_en='Direct Split',
                label_zh='直接分拆', label_en='Direct Spinoff', is_reit=False)


def merge_by_company(all_items):
    """
    按股票代码合并，每家公司汇总为一个事件：
    {
      stockCode, stockName, ticker, lastPrice,
      latestDate,       # 最新公告日期
      firstDate,        # 最早公告日期
      announcements: [  # 所有相关公告，按时间倒序
        { date, title, docUrl }
      ],
      summary           # 自动生成的脉络摘要
    }
    """
    companies = {}
    for item in all_items:
        code = item["stockCode"]
        if code not in companies:
            companies[code] = {
                "stockCode":     code,
                "stockName":     item["stockName"],
                "ticker":        item["ticker"],
                "lastPrice":     None,
                "latestDate":    item["date"],
                "firstDate":     item["date"],
                "announcements": [],
            }
        c = companies[code]
        # 更新日期范围
        if item["date"] > c["latestDate"]:
            c["latestDate"] = item["date"]
        if item["date"] < c["firstDate"]:
            c["firstDate"] = item["date"]
        # 去重
        existing_urls = {a["docUrl"] for a in c["announcements"]}
        if item["docUrl"] not in existing_urls:
            c["announcements"].append({
                "date":   item["date"],
                "title":  item["title"],
                "docUrl": item["docUrl"],
            })

    # 每家公司公告按日期倒序
    for c in companies.values():
        c["announcements"].sort(key=lambda x: x["date"], reverse=True)
        # 自动生成脉络摘要（包含分拆标的）
        n = len(c["announcements"])
        # 尝试提取分拆子公司名称
        sub = ""
        for a in c["announcements"]:
            t = a.get("title", "")
            import re
            m1 = re.search(r"分拆\s*([^\s，,。（(【]{3,20})\s*(?:並於|并于|至|在|于|to|upon)", t)
            m2 = re.search(r"子公司\s*([^\s，,。（(]{4,20})\s*(?:至|在|于|to)", t)
            if m1: sub = m1.group(1).strip(); break
            if m2: sub = m2.group(1).strip(); break
        c["spinTarget"] = sub
        # 分拆类型识别（手动标注优先）
        if code in KNOWN_INTRO:
            c["spinType"] = dict(code='intro_hk', exchange_zh='港交所', exchange_en='HKEX',
                                  label_zh='介紹上市', label_en='Intro Listing', is_reit=False,
                                  note='manually confirmed')
        else:
            c["spinType"] = _classify_spinoff_type([a["title"] for a in c["announcements"]])
        span = f"（{c['firstDate']} ~ {c['latestDate']}）" if c["firstDate"] != c["latestDate"] else f"（{c['latestDate']}）"
        c["summary"] = (
            f"{'分拆标的：' + sub + '。' if sub else ''}"
            f"共 {n} 条相关公告{span}"
        )

    # 按最新公告日期排序
    return sorted(companies.values(), key=lambda x: x["latestDate"], reverse=True)


def filter_low_price(companies):
    """过滤现价 < 0.5 HKD 或市值 < 2亿 HKD 的住股/空壳公司"""
    try:
        import yfinance as yf
        result = []
        for c in companies:
            ticker = c["ticker"]
            try:
                info = yf.Ticker(ticker).fast_info
                price = info.last_price
                mktcap = getattr(info, 'market_cap', None)
                c["lastPrice"] = round(price, 3) if price else None
                c["marketCap"] = int(mktcap) if mktcap else None
                time.sleep(0.3)
            except Exception:
                price = None
                mktcap = None
                c["lastPrice"] = None
                c["marketCap"] = None
            # 价格过滤：< 0.2 HKD
            if price is not None and price < 0.2:
                print(f"  ⛔ 过滤仙股: {ticker} 现价={price:.3f} HKD")
                continue
            # 市值过滤：< 2亿 HKD（小市值空壳/堆垃公司）
            if mktcap is not None and mktcap < 200_000_000:
                print(f"  ⛔ 过滤小市值: {ticker} 市值={mktcap/1e8:.1f}亿 HKD")
                continue
            result.append(c)
        print(f"  过滤后剩余: {len(result)} 家公司")
        return result
    except ImportError:
        print("  yfinance 未安装，跳过价格过滤")
        return companies


def main():
    print("=== fetch_spinoff.py ===")
    print(f"搜索范围: {date_from} ~ {date_to}")

    opener = get_opener()
    time.sleep(1)

    raw_items = []
    seen_urls = set()

    for kw in KEYWORDS:
        print(f"\n搜索「{kw}」...")
        html = search_keyword(opener, kw)
        if not html:
            continue
        rows = parse_rows(html)
        print(f"  解析到: {len(rows)} 条")
        for item in rows:
            if item["docUrl"] not in seen_urls:
                seen_urls.add(item["docUrl"])
                raw_items.append(item)
        time.sleep(2)

    print(f"\n去重后共 {len(raw_items)} 条原始公告")

    # 按公司合并
    companies = merge_by_company(raw_items)
    print(f"合并后共 {len(companies)} 家公司")

    # 剔除纯拆股（拆股/合股，无子公司上市）
    def is_pure_split(c):
        """剔除仅有股份拆分/合股重组（非业务分拆）的公告"""
        all_titles = " ".join(a.get("title","") for a in c.get("announcements",[]))
        # 判断是否包含子公司/上市等关键词
        has_spinoff_kw = re.search(r"建議分拆|建议分拆|擬議分拆|拟议分拆|獨立上市|独立上市|spin.?off|demerger", all_titles, re.I)
        # 判断是否是纯股份分拆/拆股
        is_share_split = re.search(r"股份分拆|股份分割|share.?split|免費換領股票|免费换领", all_titles, re.I)
        # 如果只有拆股信号、没有子公司上市信号，则过滤
        if is_share_split and not has_spinoff_kw:
            return True
        # 判断是否是合股重组（削减资本+分拆未发行股份，无子公司上市）
        # 典型格式："削減已發行股份之資本及分拆未發行股份"
        is_capital_reorg = re.search(r"削減.{0,10}股份.{0,10}資本|削减.{0,10}股份.{0,10}资本", all_titles, re.I)
        has_unissued_split = re.search(r"分拆未發行股份|分拆未发行股份", all_titles, re.I)
        if is_capital_reorg and has_unissued_split and not has_spinoff_kw:
            return True
        return False

    before_filter = len(companies)
    companies = [c for c in companies if c['stockCode'] not in BLACKLIST_CODES]
    if before_filter != len(companies):
        print(f"  ⛔ 黑名单过滤: {before_filter - len(companies)} 家")

    before_filter = len(companies)
    companies = [c for c in companies if not is_pure_split(c)]
    if before_filter != len(companies):
        print(f"  ⛔ 过滤纯拆股: {before_filter - len(companies)} 家")

    # 价格过滤
    print("\n价格过滤（排除 <0.5 HKD 仙股）...")
    companies = filter_low_price(companies)

    for c in companies:
        print(f"  {c['ticker']} {c['stockName']} — {len(c['announcements'])} 条公告，最新: {c['latestDate']}")

    data = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dateFrom":  date_from,
        "dateTo":    date_to,
        "count":     len(companies),
        "companies": companies,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n✅ {len(companies)} 家公司分拆事件 → {OUT_FILE}")

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_file and companies:
        with open(summary_file, "a") as f:
            f.write(f"\n## 📋 港股分拆公告（{len(companies)} 家公司）\n")
            for c in companies[:10]:
                latest = c["announcements"][0]
                f.write(f"- **{c['ticker']}** {c['stockName']} [{latest['title'][:50]}]({latest['docUrl']}) {c['latestDate']}\n")


if __name__ == "__main__":
    main()
