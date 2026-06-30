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

KEYWORDS = ["分拆", "spin-off", "demerger"]


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
        span = f"（{c['firstDate']} ~ {c['latestDate']}）" if c["firstDate"] != c["latestDate"] else f"（{c['latestDate']}）"
        c["summary"] = (
            f"{'分拆标的：' + sub + '。' if sub else ''}"
            f"共 {n} 条相关公告{span}"
        )

    # 按最新公告日期排序
    return sorted(companies.values(), key=lambda x: x["latestDate"], reverse=True)


def filter_low_price(companies):
    """过滤现价 < 0.5 HKD 的仙股"""
    try:
        import yfinance as yf
        result = []
        for c in companies:
            ticker = c["ticker"]
            try:
                price = yf.Ticker(ticker).fast_info.last_price
                c["lastPrice"] = round(price, 3) if price else None
                time.sleep(0.3)
            except Exception:
                price = None
                c["lastPrice"] = None
            if price is None or price >= 0.5:
                result.append(c)
            else:
                print(f"  ⛔ 过滤仙股: {ticker} 现价={price:.3f} HKD")
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
