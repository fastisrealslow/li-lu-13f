#!/usr/bin/env python3
"""
fetch_webb_holdings.py
----------------------
优先从已核实的港交所原始权益披露建立 David Webb 公开披露快照
（仅5%以上披露持股，低于5%的持仓无法从此来源获取）
更新 webb.json 的 current.holdings 中的 shares / value 字段
"""

import json, re, sys, time, io, zipfile, math
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime, timezone
from urllib.request import urlopen, Request
from urllib.error import URLError
from html.parser import HTMLParser

URL = "https://webbsite.0xmd.com/dbpub/webbchips.asp"
WEBB_JSON = "webb.json"
CONFIG_PATH = Path(__file__).resolve().parent / 'investors.json'
LISTED_SECURITIES = 'https://www.hkex.com.hk/eng/services/trading/securities/securitieslists/ListOfSecurities.xlsx'

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; 13f-dashboard/1.0; +https://github.com/fastisrealslow/li-lu-13f)",
    "Accept": "text/html,application/xhtml+xml",
}


def disclosed_positions(payload, aliases):
    """Use the newest exact HKEX form, including confirmed threshold exits."""
    from hk_disclosures import entity_matches
    positions = []
    for security in payload.get('holdings', []):
        records = [r for r in security.get('verified_disclosures', [])
                   if not r.get('superseded_by') and entity_matches(r.get('entity',''), aliases)]
        if not records:
            continue
        latest = max(records, key=lambda r:(r['event_date'],r.get('filing_date',''),r['filing_ref']))
        if latest.get('verification') != 'hkex_form' or any(p.get('event_date','') >= latest['event_date'] for p in security.get('pending_newer_notices', [])):
            continue
        if latest.get('position') != 'long' or latest.get('share_class','').casefold() not in ('ordinary shares','h shares') or latest.get('shares',0) <= 0 or latest.get('pct',0) < 5:
            continue
        positions.append({'ticker':latest['ticker'], 'name':security.get('name') or latest.get('issuer_name',''),
                          'cnName':security.get('cnName',''), 'sector':security.get('sector') or '其他',
                          'shares':latest['shares'], 'stake':latest['pct'], 'eventDate':latest['event_date'],
                          'filingDate':latest.get('filing_date'), 'sourceURL':latest['form_url'],
                          'shareType':'SH', 'putCall':'', 'cls':latest.get('share_class',''),
                          'prevShares':None, 'prevValue':None})
    return positions


def parse_active_securities(raw):
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        strings=[''.join(node.itertext()) for node in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('s:si',ns)]
        sheet=ET.fromstring(archive.read('xl/worksheets/sheet1.xml'))
    rows=[]
    for row in sheet.findall('.//s:row',ns):
        cells={re.sub(r'\d','',c.attrib['r']):(strings[int(c.findtext('s:v',namespaces=ns))] if c.attrib.get('t')=='s' else c.findtext('s:v',default='',namespaces=ns)) for c in row}
        rows.append(cells)
    heading=next((i for i,row in enumerate(rows) if row.get('A')=='Stock Code'),None)
    if heading is None:
        raise ValueError('HKEX security list headers are unavailable')
    columns={v:k for k,v in rows[heading].items()}
    updated=re.search(r'Updated as at (\d{2}/\d{2}/\d{4})',' '.join(str(v) for row in rows[:heading] for v in row.values()))
    if not updated or abs((datetime.now(timezone.utc).date()-datetime.strptime(updated[1],'%d/%m/%Y').date()).days)>14:
        raise ValueError('HKEX security list is stale or undated')
    securities={}
    for row in rows[heading+1:]:
        code=row.get(columns['Stock Code'],'')
        if not re.fullmatch(r'\d{5}',code) or row.get(columns['Category'])!='Equity' or row.get(columns['Trading Currency'])!='HKD':
            continue
        securities[code+'.HK']={'isin':row.get(columns['ISIN']), 'listedName':row.get(columns['Name of Securities']), 'listingListDate':datetime.strptime(updated[1],'%d/%m/%Y').date().isoformat()}
    if len(securities)<1000:
        raise ValueError('HKEX security list appears incomplete')
    return securities


def active_securities():
    with urlopen(Request(LISTED_SECURITIES,headers=HEADERS),timeout=20) as response:
        return parse_active_securities(response.read(8_000_001))


def update_from_disclosures(investor, root=Path('.'), price_reader=None, listed_reader=None):
    from fetch_prices_all import get_hk_prices
    from update_status import record_source_notice, record_source_warning
    root=Path(root)
    payload=json.loads((root/investor['hkFile']).read_text())
    listed=(listed_reader or active_securities)()
    previous=json.loads((root/investor['dataFile']).read_text())
    known_isins={h['ticker']:h.get('isin') for h in previous.get('current',{}).get('holdings',[])}
    # Historical stock codes may have been reassigned to a different issuer.
    # Old-only archive records stay in the history, and an ISIN change never
    # transfers the previous issuer's reported shares to the replacement stock.
    positions=[{**h,**listed[h['ticker']]} for h in disclosed_positions(payload,investor['hkDisclosure']['entities'])
               if h['ticker'] in listed and '/di/NSForm' in h['sourceURL'] and '/filing/' not in h['sourceURL']
               and (not known_isins.get(h['ticker']) or known_isins[h['ticker']]==listed[h['ticker']]['isin'])]
    if not positions:
        record_source_warning('webb_holdings','本次未取得可用的港交所最新原表；保留上次持仓快照，继续更新股价。')
        return False
    quotes=(price_reader or get_hk_prices)([h['ticker'] for h in positions])
    for row in positions:
        quote=quotes.get(row['ticker'],{})
        if quote.get('error') or not isinstance(quote.get('c'),(int,float)) or not math.isfinite(quote['c']) or quote['c']<=0 or quote.get('currency','HKD')!='HKD':
            record_source_warning('webb_holdings','部分披露证券报价未取得；保留上次完整持仓快照，后续自动重试。')
            return False
        row.update(price=quote['c'], priceDate=datetime.fromtimestamp(quote['t'], timezone.utc).date().isoformat() if quote.get('t') else None, value=round(row['shares']*quote['c']))
    path=root/investor['dataFile'];data=previous
    data['current']={'quarter':'公开披露快照','periodEnd':None,'filingDate':None,
                     'holdings':sorted(positions,key=lambda h:-h['value']),
                     'totalValue':sum(h['value'] for h in positions),'prevQuarter':None,'prevTotalValue':None}
    data.setdefault('meta',{}).update(lastUpdated=datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        source='https://di.hkex.com.hk/',currency='HKD',snapshotType='verified_disclosure_snapshot',
        snapshotNote='每只证券采用最近一份已核实港交所原表，展示披露权益仍达5%的证券；不同披露日期不等于今日完整组合。',
        holdingsSource='hkex_original_forms',verificationDate=payload.get('audit',{}).get('checkedAt'))
    data['meta']['activeSecuritySource']=LISTED_SECURITIES
    temp=path.with_suffix('.json.tmp');temp.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temp.replace(path)
    record_source_notice('webb_holdings',f'已从港交所原表核实 {len(positions)} 项最新公开披露；按各自披露日期保留股数，股价独立更新。')
    print(f'Webb: {len(positions)} positions sourced from original HKEX forms.',flush=True)
    return True

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
    config=json.loads(CONFIG_PATH.read_text(encoding='utf-8'))['investors']
    investor=next(c for c in config if c['id']=='webb')
    if investor.get('holdingsUpdateMode')=='verified_disclosures':
        try:
            update_from_disclosures(investor)
        except Exception as exc:
            # Only a non-empty prior snapshot is a safe fallback.
            prior=json.loads(Path(investor['dataFile']).read_text())
            if not prior.get('current',{}).get('holdings'):
                raise
            from update_status import record_source_warning
            record_source_warning('webb_holdings','港交所本次核实未完成；保留上次持仓，股价继续独立更新，后续自动重试。')
            print(f'Webb disclosure refresh unavailable: {exc}',file=sys.stderr)
        return
    if investor.get('holdingsUpdateMode')=='archived':
        # Still require a readable, non-empty archive. A missing archive is
        # a genuine error; a deliberately retired network feed is not.
        with open(WEBB_JSON,encoding='utf-8') as f:archive=json.load(f)
        if not archive.get('current',{}).get('holdings'):
            raise ValueError('Archived Webb holdings are missing')
        print(f"保留 {len(archive['current']['holdings'])} 条历史持仓；报价由独立价格任务更新。")
        from update_status import record_source_notice
        record_source_notice('webb_holdings','历史档案模式：保留旧持仓，仅定期更新股价；停用不可用的持仓镜像。')
        return
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
