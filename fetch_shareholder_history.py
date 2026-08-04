#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第二步：对已识别出"个人/家族大股东"的港股公司，抓取该股东的完整历史增减持记录（DI notices）。

数据来源：HKEX Disclosure of Interests，"List of DI notices filed by substantial shareholders"
          (NSNoticeSSList.aspx, sa2=ns) —— 与 fetch_substantial_shareholders.py 共用 sid 查找逻辑。

输入：spinoff_substantial_shareholders.json（第一步产出的快照+分类）
输出：spinoff_shareholder_history.json，每家公司 -> 目标股东 -> records[]（与 guo_haiqing.json 的
      records[] 结构一致：date, change, price, shares, pct, type, source）

分类规则（机构关键词过滤）与 fetch_substantial_shareholders.py 保持一致。
去重规则：按用户确认，同一人在不同层级重复出现时，只取其中【占比最高】的一条作为"当前持股人"，
          但历史事件记录仍按该姓名的全部呈报记录汇总（不同层级实体名称不视为同一人，只做精确姓名匹配）。

用户明确要求：不确定的条目不要瞎填。若某股东查不到任何历史事件记录，标记在 _errors 中，不构造假数据。
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

START_DATE = "01/01/2015"
END_DATE = datetime.now().strftime("%d/%m/%Y")

INSTITUTION_KEYWORDS = [
    'group', 'holdings', 'holding', 'company', 'corporation', 'corp', 'ltd', 'limited',
    'asset management', 'trust', 'capital', 'fund', 'bank', 'chase', 'blackrock',
    'jpmorgan', 'citigroup', 'vanguard', 'state street', 'ping an', '集团', '有限公司',
    '控股', '国有', '资本运营', 'communications group', 'network', 'project',
    'gk', 'sw', 'sons', '公司', 'international', 'resources',
    'morgan stanley', 'bnp paribas', 'ubs', 'hsbc', 'goldman sachs', 'inc.', 'plc',
    'nominees', 'securities', 'cantrust', 'pandanus associates', 'brandes investment',
    'industrial bank', 'fidelity', 'lion trust', 'partners, l.p.', 's.a.',
    '证券股份有限公司', '资产管理', '银行',
]


def is_institution(name):
    n = name.lower()
    return any(kw in n for kw in INSTITUTION_KEYWORDS)


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


def get_notice_list_url(stock_code, sid):
    """构造 NSNoticeSSList.aspx 的URL（8列事件日志：表单号/股东名/披露原因/买卖股数/均价/变动后总持股/总%/事件日期）"""
    scsd = urllib.parse.quote(START_DATE, safe="")
    sced = urllib.parse.quote(END_DATE, safe="")
    return (
        f"{BASE}NSNoticeSSList.aspx?sa2=ns&sid={sid}&corpn=&sd={START_DATE}&ed={END_DATE}"
        f"&cid=0&sa1=cl&scsd={scsd}&sced={sced}&sc={stock_code}&src=MAIN&lang=EN&g_lang=en&"
    )


# 基于 HKEX 官方代码表（di.hkex.com.hk/di/NSStdCode.aspx）的真实含义：四位数字代码的前2位是“系列”：
#   10xx：首次取得须具报权益（首次披露）
#   11xx：持股比例上升（确实为增持，包含1101买入股份、1113行使股本衍生工具等子代码）
#   12xx：持股比例下降（确实为减持，包含1201完成出售、1209先舊后新配售等子代码）
#   13xx：持股性质改变（非比例变动，不能推断为增持或减持方向）
#   17xx：杂项/自愿披露/其他，方向不明，常伴随公司总股本变动导致的比例漂移
# 参考：https://di.hkex.com.hk/di/NSStdCode.aspx?ft=IS&lang=ZH
_REASON_SERIES_MAP = {
    "10": "首次披露",
    "11": "增持",
    "12": "减持",
}

def classify_event_type(reason_code):
    code = reason_code.replace("(L)", "").replace("(S)", "").strip()
    series = code[:2] if len(code) >= 2 else code

    # 17xx（自愿披露/其他）代码本身不表明方向，常伴随总股本变动导致的比例漂移（即使带有很小的change值，仍不能确定是主动交易意图）
    if series == "17":
        return "百分比变动（非交易）"

    # 11xx/12xx系列代码本身已明确表明比例上升/下降方向，不依赖change值符号
    if series in _REASON_SERIES_MAP:
        return _REASON_SERIES_MAP[series]

    # 13xx（持股性质改变）以及其他未识别代码：代码本身不能推断方向，且原始change列无符号，
    # 不能用change_value正负去推断增减持（否则属于猜测/虚构方向）。按用户“不确定就不填”原则，标记为待定性事件。
    return "性质变动（方向不明）"


def parse_notice_table(html_content, target_name):
    """解析事件日志表格，仅保留股东名精确匹配 target_name 的行（大小写不敏感，去除多余空格）"""
    records = []
    target_norm = re.sub(r'\s+', ' ', target_name.strip()).upper()

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html_content, re.DOTALL | re.IGNORECASE)
    for row in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', row, re.DOTALL | re.IGNORECASE)
        if len(cells) != 8:
            continue

        def clean(c):
            t = re.sub(r'<[^>]+>', '', c)
            t = html_module.unescape(t)
            return re.sub(r'\s+', ' ', t.replace('\xa0', ' ')).strip()

        cc = [clean(c) for c in cells]
        name = cc[1]
        if re.sub(r'\s+', ' ', name.strip()).upper() != target_norm:
            continue

        form_serial = cc[0]
        reason_raw = cc[2]
        change_raw = cc[3]
        price_raw = cc[4]
        shares_raw = cc[5]
        pct_raw = cc[6]
        date_raw = cc[7]

        change_match = re.search(r'([\d,]+)\s*\(([LS])\)', change_raw)
        shares_match = re.search(r'([\d,]+)\s*\(([LS])\)', shares_raw)
        pct_match = re.search(r'(\d{1,3}\.\d{2})\s*\(([LS])\)', pct_raw)
        price_match = re.search(r'HKD\s*([\d.]+)', price_raw)
        date_match = re.search(r'(\d{2})/(\d{2})/(\d{4})', date_raw)

        if not shares_match or not date_match:
            continue

        change = int(change_match.group(1).replace(',', '')) if change_match else None
        shares = int(shares_match.group(1).replace(',', ''))
        pct = float(pct_match.group(1)) if pct_match else None
        price = float(price_match.group(1)) if price_match else None
        date_iso = f"{date_match.group(3)}-{date_match.group(2)}-{date_match.group(1)}"

        event_type = classify_event_type(reason_raw)

        # HKEX原始数据的 change 列本身是无符号的绝对值，方向完全依靠 Reason for disclosure 代码。
        # 为避免前端需要再次解析type才能判断正负，这里直接将“减持/退出”、“减持”类事件的change存为负数。
        if change is not None and event_type == "减持":
            change = -change

        # “百分比变动（非交易）”与“性质变动（方向不明）”事件：这两类事件的 change 原始值
        # 可能代表总股本变动量而非该股东实际交易量（如上面 01523 案例中 change 与
        # shares（不变）数值完全相同，显然不是真实交易量），保留会误导用户。根据
        # “不确定就不填”原则，对这两类事件强制清空 change，前端仅展示 shares/pct 实际变化。
        if event_type in ("百分比变动（非交易）", "性质变动（方向不明）"):
            change = None

        records.append({
            "date": date_iso,
            "change": change,
            "price": price,
            "shares": shares,
            "pct": pct,
            "type": event_type,
            "source": f"HKEX {form_serial}",
        })

    # 去重：同一股东在同一日期可能有两份并行申报（如 IS.../DA... 表单号），
    # 往往代表本人层面与关联公司控股架构层面的两份并行披露，实际上是同一事件。
    # 若 date+shares+pct 完全相同，只保留其中一条（保留 source 排序靠前的一条，即列表中先出现的）。
    dedup_seen = set()
    deduped = []
    for r in records:
        key = (r["date"], r["shares"], r["pct"])
        if key in dedup_seen:
            continue
        dedup_seen.add(key)
        deduped.append(r)

    # 按日期降序（与 guo_haiqing.json 的排列一致：最新在前）
    deduped.sort(key=lambda r: r["date"], reverse=True)

    # 不对"百分比变动（非交易）"事件强行推导 change —— 这类事件本质是总股本变动引发的%漂移，
    # 用前后shares差值推导会产生误导性的"增减持"叙事。保持 change=None，前端应特殊展示为无交易明细。
    return deduped


def main():
    snapshot = json.load(open("spinoff_substantial_shareholders.json", encoding="utf-8"))

    result = {}
    errors = {}

    companies = snapshot["companies"]
    total_targets = 0
    for code, info in companies.items():
        personal = [s for s in info["shareholders"] if not is_institution(s["name"])]
        if not personal:
            continue
        # 注：按"最新披露日期"而不是"持股比例"选人——确保选到当前仍在活跃变动的人，而非已退出但历史持股比例更高的旧快照
        def _parse_date(d):
            try:
                dd, mm, yyyy = d.split('/')
                return f"{yyyy}-{mm}-{dd}"
            except Exception:
                return "0000-00-00"

        seen_names = set()
        top_per_person = []
        for s in sorted(personal, key=lambda x: _parse_date(x["lastNoticeDate"]), reverse=True):
            key = re.sub(r'\s+', ' ', s["name"].strip()).upper()
            if key in seen_names:
                continue
            seen_names.add(key)
            top_per_person.append(s)
        total_targets += len(top_per_person)

    done = 0
    for code, info in companies.items():
        personal = [s for s in info["shareholders"] if not is_institution(s["name"])]
        if not personal:
            continue

        sid = info["sid"]
        stock_name = info["stockName"]

        def _parse_date2(d):
            try:
                dd, mm, yyyy = d.split('/')
                return f"{yyyy}-{mm}-{dd}"
            except Exception:
                return "0000-00-00"

        seen_names = set()
        top_per_person = []
        for s in sorted(personal, key=lambda x: _parse_date2(x["lastNoticeDate"]), reverse=True):
            key = re.sub(r'\s+', ' ', s["name"].strip()).upper()
            if key in seen_names:
                continue
            seen_names.add(key)
            top_per_person.append(s)

        # 按最新披露日期选取"当前最活跃的个人股东"（用户需求：只跟踪每家的单一最大股东/实际控制人）。
        # 若历史快照中持股比例更高但日期已过时的同名字行（如大小写差异的重复申报），不选它们，选最新一行。
        target = top_per_person[0]
        done += 1
        print(f"[{done}/{total_targets}] {code} {stock_name} -> {target['name']} ({target['pct']}%) ...", end=" ", flush=True)

        try:
            notice_url = get_notice_list_url(code, sid)
            notice_html = http_get(notice_url)
            records = parse_notice_table(notice_html, target["name"])

            if not records:
                errors[code] = f"股东 {target['name']} 在事件日志中未匹配到任何历史记录（可能姓名呈报格式不一致，需人工核实）"
                print("无历史记录")
                time.sleep(1.2)
                continue

            result[code] = {
                "shareholder": target["name"],
                "shareholder_en": target["name"],
                "stock_code": code,
                "stock_name": stock_name,
                "last_updated": records[0]["date"],
                "current_shares": target["shares"],
                "current_pct": target["pct"],
                "note": "数据来源：HKEX披露易系统 List of DI notices filed by substantial shareholders，自动抓取；仅代表≥5%披露门槛下的呈报记录",
                "records": records,
            }
            print(f"OK，{len(records)}条历史记录")

        except Exception as e:
            errors[code] = f"抓取异常：{type(e).__name__}: {e}"
            print(f"异常：{e}")

        time.sleep(1.2)

    output = {
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "HKEX Disclosure of Interests (di.hkex.com.hk), List of DI notices filed by substantial shareholders",
        "companies": result,
        "_errors": errors,
    }

    with open("spinoff_shareholder_history.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print()
    print(f"完成：成功 {len(result)}/{total_targets}，失败/跳过 {len(errors)}/{total_targets}")
    if errors:
        for code, reason in errors.items():
            print(f"  {code}: {reason}")


if __name__ == "__main__":
    main()
