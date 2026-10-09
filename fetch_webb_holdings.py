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
            price_date = row[7].strip() if len(row) > 7 else ""
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
                "priceDate": price_date,
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

    if not new_holdings or len({h['ticker'] for h in new_holdings}) != len(new_holdings):
        return False
    existing = {h['ticker']: h for h in d['current']['holdings']}
    rows = []
    for nh in new_holdings:
        # Disappearance from a thresholded archive is not evidence of a sale.
        old = existing.get(nh['ticker'], {})
        rows.append({**old, **nh, 'prevShares': None, 'prevValue': None})
    rows.sort(key=lambda h: h['value'], reverse=True)
    dates = [h.get('priceDate', '') for h in rows if re.fullmatch(r'\d{4}-\d{2}-\d{2}', h.get('priceDate', ''))]
    d['current'] = {'quarter': '历史快照', 'periodEnd': None, 'filingDate': None,
                    'totalValue': sum(h['value'] for h in rows), 'holdings': rows,
                    'prevQuarter': None, 'prevTotalValue': None}
    d['meta'].update(lastUpdated=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        currency='HKD', source=URL, snapshotType='historical_disclosure_snapshot',
        valuationDate=max(dates) if len(dates) == len(rows) else None)
    updated = len(rows)

    with open(WEBB_JSON, "w") as f:
        json.dump(d, f, ensure_ascii=False, indent=2)

    # webb_hk.json is owned by the shared HKEX evidence pipeline. A secondary
    # holdings/price feed must never overwrite verified notices or their dates.

    print(f"\n✅ webb.json 更新完成，{updated} 条持仓有变化")
    return True


def main():
    print("=== fetch_webb_holdings.py ===")
    # 调度控制由 CI workflow 负责（仅周一执行），脚本本身无条件运行
    now = datetime.now(timezone.utc)
    print(f"执行时间：UTC {now.strftime('%a %Y-%m-%d %H:%M')}")
    print(f"抓取 {URL} ...")
    holdings = fetch_webbchips()
    if not holdings:
        print("❌ 抓取失败，保留原有数据")
        sys.exit(1)

    print(f"\n共获取 {len(holdings)} 条持仓（5%以上披露）")
    if not update_webb_json(holdings):
        sys.exit(1)


if __name__ == "__main__":
    main()
