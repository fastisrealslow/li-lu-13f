#!/usr/bin/env python3
"""
fetch_spinoff.py
----------------
从港交所新闻披露平台（www1.hkexnews.hk/search/titlesearch.xhtml）
搜索「分拆」相关公告，提取公司名、文件标题、日期、PDF链接，
写入 spinoff.json 供前端展示。

搜索关键词：分拆、spin-off、demerger
时间范围：最近2年
"""

import json, os, re, sys, time, http.cookiejar, urllib.parse
from datetime import datetime, timezone, timedelta
from urllib.request import build_opener, HTTPCookieProcessor, Request

OUT_FILE = "spinoff.json"
BASE_URL = "https://www1.hkexnews.hk"

today    = datetime.now()
date_to  = today.strftime("%Y/%m/%d")
date_from = (today - timedelta(days=730)).strftime("%Y/%m/%d")

KEYWORDS = ["分拆", "spin-off", "demerger", "spinoff"]

HEADERS = [
    ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"),
    ("Accept", "text/html,application/xhtml+xml,*/*;q=0.8"),
    ("Accept-Language", "zh-HK,zh;q=0.9,en;q=0.8"),
]


def get_opener():
    jar = http.cookiejar.CookieJar()
    opener = build_opener(HTTPCookieProcessor(jar))
    opener.addheaders = HEADERS
    return opener, jar


def get_viewstate(opener):
    """访问搜索首页，获取 JSF ViewState"""
    resp = opener.open(f"{BASE_URL}/search/titlesearch.xhtml?lang=zh", timeout=15)
    html = resp.read().decode("utf-8", errors="replace")
    m = re.search(r'name=["\']javax\.faces\.ViewState["\'][^>]*value=["\']([^"\']+)["\']', html)
    vs = m.group(1) if m else ""
    print(f"  ViewState: {vs[:30]}...")
    return vs


def search_keyword(opener, keyword, viewstate):
    """POST 搜索关键词，返回结果 HTML"""
    post_url = f"{BASE_URL}/search/titlesearch.xhtml?lang=zh"
    form_data = urllib.parse.urlencode({
        "j_idt10":                              "j_idt10",
        "j_idt10:loadMoreRange":                "200",
        "titleSearchResultControl.searchByIndex": "0",
        "titleSearchByAllResult.dateFromUi":    date_from,
        "titleSearchByAllResult.dateToUi":      date_to,
        "javax.faces.ViewState":                viewstate,
        "javax.faces.partial.ajax":             "true",
        "javax.faces.source":                   "j_idt10:j_idt46",
        "javax.faces.partial.execute":          "@all",
        "javax.faces.partial.render":           "@all",
        "j_idt10:j_idt46":                      "j_idt10:j_idt46",
        "newsTitle":                            keyword,
    }).encode()

    req = Request(post_url, data=form_data, headers={
        "Content-Type":    "application/x-www-form-urlencoded; charset=UTF-8",
        "Faces-Request":   "partial/ajax",
        "X-Requested-With": "XMLHttpRequest",
        "Referer":         f"{BASE_URL}/search/titlesearch.xhtml?lang=zh",
    })
    try:
        resp = opener.open(req, timeout=20)
        return resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"  搜索「{keyword}」失败: {e}", file=sys.stderr)
        return ""


def parse_results(html, keyword):
    """从结果页 HTML 提取公告条目"""
    results = []

    # 匹配结果行：股票代码 + 标题 + 日期 + PDF链接
    # 典型结构：
    # <td class="...">01234</td>
    # <td class="..."><a href="...pdf">标题文字</a></td>
    # <td class="...">2025/06/01</td>
    row_pattern = re.compile(
        r'<tr[^>]*>\s*'
        r'<td[^>]*>\s*([0-9]{4,5})\s*</td>\s*'        # 股票代码
        r'<td[^>]*>.*?<a\s+href=["\']([^"\']+)["\'][^>]*>\s*(.*?)\s*</a>.*?</td>\s*'  # 标题+链接
        r'<td[^>]*>\s*([0-9/\-]{8,10})\s*</td>',       # 日期
        re.DOTALL | re.IGNORECASE
    )

    for m in row_pattern.finditer(html):
        stock_code = m.group(1).zfill(5)
        doc_url    = m.group(2).strip()
        title      = re.sub(r'<[^>]+>', '', m.group(3)).strip()
        doc_date   = m.group(4).strip()

        if not doc_url.startswith("http"):
            doc_url = BASE_URL + doc_url

        results.append({
            "stockCode": stock_code,
            "ticker":    stock_code + ".HK",
            "title":     title[:120],
            "date":      doc_date,
            "docUrl":    doc_url,
            "keyword":   keyword,
        })

    # 如果上面匹配不到，尝试更宽松的模式：只找包含关键词的 PDF 链接行
    if not results:
        loose = re.compile(
            r'href=["\']([^"\']*\.(?:pdf|PDF))["\'][^>]*>\s*([^<]*(?:分拆|spin|demerger)[^<]*)\s*<',
            re.IGNORECASE
        )
        for m in loose.finditer(html):
            url_  = m.group(1)
            title_ = m.group(2).strip()
            if not url_.startswith("http"):
                url_ = BASE_URL + url_
            results.append({
                "stockCode": "",
                "ticker":    "",
                "title":     title_[:120],
                "date":      today.strftime("%Y/%m/%d"),
                "docUrl":    url_,
                "keyword":   keyword,
            })

    return results


def load_existing():
    if os.path.exists(OUT_FILE):
        try:
            return json.load(open(OUT_FILE))
        except:
            pass
    return {"updatedAt": "", "items": []}


def main():
    print("=== fetch_spinoff.py ===")
    print(f"搜索范围: {date_from} ~ {date_to}")
    print(f"关键词: {KEYWORDS}")

    opener, jar = get_opener()

    print("\n获取 ViewState...")
    try:
        viewstate = get_viewstate(opener)
    except Exception as e:
        print(f"❌ 无法访问搜索页: {e}")
        sys.exit(0)
    time.sleep(1)

    all_items = []
    seen_urls = set()

    for kw in KEYWORDS:
        print(f"\n搜索「{kw}」...")
        html = search_keyword(opener, kw, viewstate)
        if not html:
            continue

        items = parse_results(html, kw)
        print(f"  解析到: {len(items)} 条")

        for item in items:
            if item["docUrl"] not in seen_urls:
                seen_urls.add(item["docUrl"])
                all_items.append(item)
                print(f"  → [{item['ticker']}] {item['title'][:50]} ({item['date']})")

        time.sleep(2)

    # 过滤：股价极低的公司（<0.5 HKD）通常是合股/仙股，不是真正的分拆投资标的
    if all_items:
        print("\n过滤低价股...")
        try:
            import yfinance as yf
            filtered = []
            for item in all_items:
                ticker = item.get("ticker", "")
                if not ticker or not ticker.endswith(".HK"):
                    filtered.append(item)
                    continue
                try:
                    info = yf.Ticker(ticker).fast_info
                    price = getattr(info, "last_price", None) or getattr(info, "regularMarketPrice", None)
                    if price is None or price >= 0.5:
                        item["lastPrice"] = round(price, 3) if price else None
                        filtered.append(item)
                    else:
                        print(f"  ⛔ 过滤低价股: {ticker} 现价={price:.3f} HKD")
                except Exception:
                    filtered.append(item)  # 查不到价格就保留
                time.sleep(0.3)
            all_items = filtered
            print(f"  过滤后剩余: {len(all_items)} 条")
        except ImportError:
            print("  yfinance 未安装，跳过价格过滤")

    # 按日期降序
    all_items.sort(key=lambda x: x["date"], reverse=True)

    data = {
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "dateFrom":  date_from,
        "dateTo":    date_to,
        "count":     len(all_items),
        "items":     all_items,
    }

    with open(OUT_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 共 {len(all_items)} 条分拆公告 → {OUT_FILE}")

    summary_file = os.environ.get("GITHUB_STEP_SUMMARY", "")
    if summary_file and all_items:
        with open(summary_file, "a") as f:
            f.write(f"\n## 📋 港股分拆公告（最近2年，共{len(all_items)}条）\n")
            for item in all_items[:10]:
                f.write(f"- **{item['ticker']}** [{item['title'][:50]}]({item['docUrl']}) {item['date']}\n")


if __name__ == "__main__":
    main()
