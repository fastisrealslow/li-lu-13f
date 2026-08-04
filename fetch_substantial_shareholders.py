#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量抓取港股分拆标的的大股东（Substantial Shareholders）快照数据。

数据来源：港交所披露易系统（HKEX Disclosure of Interests），纯 HTTP GET，无需浏览器/登录。

流程（每个股票代码两步）：
  1. GET NSSrchCorpList.aspx?sc=<code>&scsd=...&sced=...  → 从返回HTML中提取 sid（该公司在HKEX内部数据库的ID，
     与股票代码之间没有可推导的数学关系，必须先查一次拿到）
  2. GET NSConstdSSList.aspx?sid=<sid>&...                → 解析"综合大股东名单"（Consolidated list），
     该名单已按好仓持股比例降序排列，第一行即为最大股东

输出：spinoff_substantial_shareholders.json，结构：
{
  "00308": {
    "stockName": "香港中旅",
    "sid": 523,
    "fetchedAt": "2026-08-04T...",
    "shareholders": [
      {"name": "中国旅游集团有限公司", "shares": 3385492610, "pct": 61.15, "lastNoticeDate": "30/01/2020"},
      {"name": "KWOK HOI HING", "shares": 387596000, "pct": 7.00, "lastNoticeDate": "23/05/2025"}
    ],
    "topShareholder": {...}   # shareholders[0]
  },
  ...
}

用户明确要求：不确定的条目不要瞎填，抓不到/解析失败的标的记录在 "_errors" 里，不写入伪造数据。
"""

import html as html_module
import json
import re
import time
import urllib.request
import urllib.parse
from datetime import datetime, timezone

BASE = "https://di.hkex.com.hk/di/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
}

START_DATE = "01/01/2015"  # dd/mm/yyyy，起始日期足够早以覆盖所有历史大股东
END_DATE = datetime.now().strftime("%d/%m/%Y")


def http_get(url, retries=3, timeout=20):
    last_err = None
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.read().decode("utf-8", errors="replace")
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    raise last_err


def fetch_sid_and_list_url(stock_code):
    """第一步：查股票代码 → 提取综合大股东名单(Consolidated list)的完整URL（含sid）"""
    scsd = urllib.parse.quote(START_DATE, safe="")
    sced = urllib.parse.quote(END_DATE, safe="")
    url = (
        f"{BASE}NSSrchCorpList.aspx?sa1=cl&scsd={scsd}&sced={sced}"
        f"&sc={stock_code}&src=MAIN&lang=EN&g_lang=en"
    )
    html = http_get(url)

    # 提取 "Consolidated list of substantial shareholders" 对应的链接 (NSConstdSSList.aspx?...)
    m = re.search(r'NSConstdSSList\.aspx\?[^"\'<>]+', html)
    if not m:
        return None, html
    list_url = BASE + m.group(0).replace("&amp;", "&")
    return list_url, html


def parse_shareholder_table(html):
    """解析综合大股东名单页面的HTML表格，返回股东列表。

    表格每行固定5列（HKEX NSConstdSSList.aspx 实际DOM结构，已用00308实测确认）：
      列0: 表单编号（如 CS20200203E00104），带跳转链接，非股东信息，忽略
      列1: 股东名称
      列2: 好仓股数，形如 "3,385,492,610(L)"
      列3: 好仓百分比，形如 "61.15(L)"
      列4: 最后呈报日期，形如 "30/01/2020"（可能带链接包裹）
    """
    shareholders = []

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.DOTALL | re.IGNORECASE)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(cells) != 5:
            continue

        def clean(c):
            text = re.sub(r'<[^>]+>', '', c)
            text = html_module.unescape(text)
            text = text.replace('\xa0', ' ').strip()
            return re.sub(r'\s+', ' ', text)

        clean_cells = [clean(c) for c in cells]
        name = clean_cells[1]
        shares_raw = clean_cells[2]
        pct_raw = clean_cells[3]
        date_raw = clean_cells[4]

        shares_match = re.search(r'([\d,]+)\s*\(L\)', shares_raw)
        pct_match = re.search(r'(\d{1,3}\.\d{2})\s*\(L\)', pct_raw)
        if not name or not shares_match or not pct_match:
            continue

        shares = int(shares_match.group(1).replace(',', ''))
        pct = float(pct_match.group(1))
        date_match = re.search(r'(\d{2}/\d{2}/\d{4})', date_raw)
        last_notice = date_match.group(1) if date_match else None

        shareholders.append({
            "name": name,
            "shares": shares,
            "pct": pct,
            "lastNoticeDate": last_notice,
        })

    # 按好仓%降序排列，去重（同名同股数的行只保留一条）
    seen = set()
    deduped = []
    for s in shareholders:
        key = (s["name"], s["shares"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(s)
    deduped.sort(key=lambda x: -x["pct"])
    return deduped


def main():
    hk_data = json.load(open("spinoff.json", encoding="utf-8"))
    companies = hk_data["companies"]

    result = {}
    errors = {}

    for i, c in enumerate(companies):
        code = c["stockCode"]
        name = c.get("stockName", "")
        print(f"[{i+1}/{len(companies)}] {code} {name} ...", end=" ", flush=True)

        try:
            list_url, search_html = fetch_sid_and_list_url(code)
            if not list_url:
                errors[code] = "未能从搜索结果中提取综合大股东名单链接（可能该股票代码无有效大股东披露记录，或页面结构变化）"
                print("跳过（无链接）")
                time.sleep(1.0)
                continue

            sid_match = re.search(r'sid=(\d+)', list_url)
            sid = int(sid_match.group(1)) if sid_match else None

            list_html = http_get(list_url)
            shareholders = parse_shareholder_table(list_html)

            if not shareholders:
                errors[code] = "查到公司记录但未解析出任何大股东行（可能无≥5%大股东，或表格结构与解析规则不匹配，需人工核实）"
                print("跳过（无解析结果）")
                time.sleep(1.0)
                continue

            result[code] = {
                "stockName": name,
                "sid": sid,
                "fetchedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                "shareholders": shareholders,
                "topShareholder": shareholders[0],
            }
            print(f"OK，最大股东：{shareholders[0]['name']} {shareholders[0]['pct']}%")

        except Exception as e:
            errors[code] = f"抓取异常：{type(e).__name__}: {e}"
            print(f"异常：{e}")

        time.sleep(1.2)  # 限速，避免对HKEX服务器造成压力

    output = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "HKEX Disclosure of Interests (di.hkex.com.hk), Consolidated list of substantial shareholders",
        "dateRangeQueried": f"{START_DATE} - {END_DATE}",
        "companies": result,
        "_errors": errors,
    }

    with open("spinoff_substantial_shareholders.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print(f"完成：成功 {len(result)}/{len(companies)}，失败/跳过 {len(errors)}/{len(companies)}")
    if errors:
        print("失败/跳过的代码：")
        for code, reason in errors.items():
            print(f"  {code}: {reason}")


if __name__ == "__main__":
    main()
