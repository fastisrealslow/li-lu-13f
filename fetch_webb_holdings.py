#!/usr/bin/env python3
"""
fetch_webb_holdings.py
----------------------
从 webbsite.0xmd.com/dbpub/webbchips.asp 抓取 David Webb 港股持仓数据
（仅5%以上披露持股，低于5%的持仓无法从此来源获取）
更新 webb.json 的 current.holdings 中的 shares / value 字段
"""

import json, re, sys, time
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser

URL = "https://webbsite.0xmd.com/dbpub/webbchips.asp"
WEBB_JSON = "webb.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; 13f-dashboard/1.0; +https://github.com/fastisrealslow/li-lu-13f)",
    "Accept": "text/html,application/xhtml+xml",
}

# 股票代号规范化：0709 -> 0709.HK
def to_hk_ticker(code):
    return code.zfill(4) + ".HK"

class TableParser(HTMLParser):
    """简单 HTML 表格解析器"""
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_tr = False
        self.in_td = False
        self.in_a = False
        self.rows = []
        self.current_row = []
        self.current_cell = ""
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
            self.depth += 1
        elif tag == "tr" and self.in_table:
            self.in_tr = True
            self.current_row = []
        elif tag in ("td", "th") and self.in_tr:
            self.in_td = True
            self.current_cell = ""
        elif tag == "a" and self.in_td:
            self.in_a = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.depth -= 1
            if self.depth == 0:
                self.in_table = False
        elif tag == "tr" and self.in_tr:
            if self.current_row:
                self.rows.append(self.current_row[:])
            self.in_tr = False
        elif tag in ("td", "th") and self.in_td:
            self.current_row.append(self.current_cell.strip())
            self.in_td = False
        elif tag == "a":
            self.in_a = False

    def handle_data(self, data):
        if self.in_td:
            self.current_cell += data


def fetch_webbchips():
    """抓取 webbchips 页面，返回持仓列表"""
    req = Request(URL, headers=HEADERS)
    try:
        with urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except URLError as e:
        print(f"ERROR fetching {URL}: {e}", file=sys.stderr)
        return None

    parser = TableParser()
    parser.feed(html)

    holdings = []
    # 找数据行：第一列是数字（行号），第二列是股票代号
    for row in parser.rows:
        if len(row) < 7:
            continue
        # row: [行号, 股票代号, 公司名, 事件日期, 申报股数, 持股%, 价格, 价格日期, 市值HKD(m)]
        try:
            row_num = int(row[0].strip())
        except ValueError:
            continue  # 跳过表头

        try:
            code = row[1].strip()
            name = row[2].strip()
            event_date = row[3].strip()
            shares_str = row[4].replace(",", "").strip()
            stake_str = row[5].strip()
            price_str = row[6].strip()

            shares = int(shares_str) if shares_str.isdigit() else int(re.sub(r"[^\d]", "", shares_str))
            price = float(price_str) if price_str else 0.0
            stake = float(stake_str) if stake_str else 0.0
            value_hkd = int(shares * price)  # HKD

            ticker = to_hk_ticker(code)
            holdings.append({
                "ticker": ticker,
                "name": name,
                "shares": shares,
                "value": value_hkd,
                "stake": stake,
                "eventDate": event_date,
                "price": price,
            })
            print(f"  {ticker}: {shares:,} shares @ HK${price:.3f} ({stake}%)")
        except Exception as e:
            print(f"  parse error row {row}: {e}", file=sys.stderr)

    return holdings


def update_webb_json(new_holdings):
    """把新持仓数据合并进 webb.json"""
    try:
        d = json.load(open(WEBB_JSON))
    except Exception as e:
        print(f"ERROR loading {WEBB_JSON}: {e}", file=sys.stderr)
        return False

    existing = {h["ticker"]: h for h in d["current"]["holdings"]}
    new_map = {h["ticker"]: h for h in new_holdings}

    updated = 0
    for ticker, nh in new_map.items():
        if ticker in existing:
            old_shares = existing[ticker].get("shares", 0)
            existing[ticker]["prevShares"] = old_shares
            existing[ticker]["prevValue"] = existing[ticker].get("value", 0)
            existing[ticker]["shares"] = nh["shares"]
            existing[ticker]["value"] = nh["value"]
            existing[ticker]["eventDate"] = nh["eventDate"]
            if old_shares != nh["shares"]:
                updated += 1
                print(f"  ✅ {ticker}: {old_shares:,} → {nh['shares']:,}")
        else:
            # 新股票，从 webb.json 历史或默认值补充
            print(f"  🆕 {ticker}: 新进 {nh['shares']:,} shares")
            existing[ticker] = {
                "ticker": ticker,
                "name": nh["name"],
                "cnName": "",
                "shares": nh["shares"],
                "value": nh["value"],
                "prevShares": 0,
                "prevValue": 0,
                "sector": "其他",
                "eventDate": nh["eventDate"],
            }
            updated += 1

    # 检测清仓：原来有但新数据里没有的（可能跌破5%，不一定真清仓）
    for ticker in list(existing.keys()):
        if ticker not in new_map:
            print(f"  ⚠️  {ticker}: 不在最新披露中（可能跌破5%或已清仓）")

    d["current"]["holdings"] = list(existing.values())
    d["meta"]["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    d["meta"]["source"] = "webbsite.0xmd.com"

    with open(WEBB_JSON, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    # 同步生成 webb_hk.json（前端渲染需要）
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    hk_out = {
        "updated": now_str,
        "source": "webbsite.0xmd.com / HKEX Disclosures",
        "quarter": d["current"].get("quarter", ""),
        "holdings": [
            {
                "ticker": h["ticker"],
                "name": h.get("cnName") or h.get("name", ""),
                "sector": h.get("sector", "其他"),
                "entity": "David Webb (personal)",
                "shares": h.get("shares", 0),
                "value": h.get("value", 0),
                "stake": h.get("stake"),
                "eventDate": h.get("eventDate", ""),
                "current_status": "active",
                "data_quality": "official",
                "notes": f"港交所权益披露，截至 {h.get('eventDate', '')}",
            }
            for h in d["current"]["holdings"]
        ],
        "disclaimer": "仅包戴5%以上权益披露持仓，低于5%的持仓不在此列。",
        "lastUpdated": now_str,
    }
    with open("webb_hk.json", "w") as f:
        json.dump(hk_out, f, ensure_ascii=False, indent=2)
    print(f"✅ webb_hk.json 同步更新，{len(hk_out['holdings'])} 条持仓")

    print(f"\n✅ webb.json 更新完成，{updated} 条持仓有变化")
    return True


def main():
    print("=== fetch_webb_holdings.py ===")
    # 韦伯持仓网站（webbsite.0xmd.com）较脆弱，限制为每周一才更新持仓
    # 韦伯持仓网站脆弱，限制为每周一 UTC 02:00 那次（北京时间10:00）才抓，每周只请求1次
    now = datetime.now(timezone.utc)
    if not (now.weekday() == 0 and now.hour < 4):
        print(f"非周一首次窗口（UTC {now.strftime('%a %H:%M')}），跳过韦伯持仓抓取")
        return
    print(f"抓取 {URL} ...")
    holdings = fetch_webbchips()
    if not holdings:
        print("❌ 抓取失败，保留原有数据")
        sys.exit(1)

    print(f"\n共获取 {len(holdings)} 条持仓（5%以上披露）")
    update_webb_json(holdings)


if __name__ == "__main__":
    main()
