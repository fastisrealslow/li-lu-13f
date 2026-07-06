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

# SiliconFlow 免费模型列表（按优先级排序，主模型下线自动 fallback）
_SF_MODELS_HK = [
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.5-4B",
    "THUDM/glm-4-9b-chat",
]


def _sf_call_hk(api_key, prompt, max_tokens=120, retries=2):
    """
    健壮的 SiliconFlow 调用：多模型 fallback + 重试。
    返回模型输出字符串，全部失败返回 None。
    """
    import urllib.request as _ureq, json as _json
    for model in _SF_MODELS_HK:
        for attempt in range(retries + 1):
            try:
                payload = _json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.1,
                    "stream": False,
                    "enable_thinking": False,
                }).encode()
                req = Request(
                    "https://api.siliconflow.cn/v1/chat/completions",
                    data=payload,
                    headers={"Authorization": f"Bearer {api_key}",
                             "Content-Type": "application/json"},
                    method="POST",
                )
                with _ureq.urlopen(req, timeout=35) as resp:
                    data = _json.loads(resp.read())
                text = data['choices'][0]['message']['content'].strip()
                if text:
                    return text
            except Exception as e:
                wait = 2 ** attempt
                print(f"    [{model}] 第{attempt+1}次失败: {e}"
                      + (f"，{wait}s 后重试" if attempt < retries else "，放弃"))
                if attempt < retries:
                    time.sleep(wait)
        print(f"    模型 {model} 全部失败，尝试下一个...")
    return None

today     = datetime.now()
date_to   = today.strftime("%Y%m%d")
date_from = (today - timedelta(days=365)).strftime("%Y%m%d")

KEYWORDS = ["分拆", "spin-off", "demerger", "實物分派", "以介紹方式", "獨立上市", "独立上市"]

# 公告标题否定关键词：命中任一则跳过该条公告
# 针对「分拆未發行股份/供股/股本削減」等内部资本操作，非子公司分拆
EXCLUDE_TITLE_PATTERNS = [
    r"分拆未發行股份",   # GEM 板供股配套操作
    r"分拆.*供股",       # 分拆+供股捆绑
    r"供股.*分拆",
    r"股本削減.*分拆",   # 股本削减+分拆
    r"分拆.*股本削減",
    r"未發行.*分拆",
]

# 明确排除：已确认是合股重组而非分拆的公司（股份代码）
# 注：优先靠 is_pure_split + 市值过滤自动拦截；仅将过滤逻辑无法覆盖的模糊案例加入此表
BLACKLIST_CODES = {
    "08516",  # 广駿集团：分拆未發行股份+供股操作，已由 EXCLUDE_TITLE_PATTERNS 拦截
}

# 手动标注介绍上市（公告标题无关键词但正文已确认）
# 注：现已通过 PDF 正文检测自动识别，本字典仅保留为备用
KNOWN_INTRO = {
    # "00308",  # 香港中旅 → 已通过 PDF 检测自动识别
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

        # 标题否定过滤：匹配内部资本操作，跳过该公告
        if any(re.search(pat, title) for pat in EXCLUDE_TITLE_PATTERNS):
            continue

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
    # 预计算：是否是「建議分拆+獨立上市」格式（标准 IPO 分拆）
    has_ipo_spinoff = bool(re.search(r'建[議议]分拆.{0,50}(?:獨立上市|独立上市|獨立上市)', combined))

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

    # IPO + 实物分派（发行新股融资，同时将现有股份分派给原股东）
    if has_ipo_spinoff and '實物分派' in combined:
        return dict(code='ipo_hk_dist', exchange_zh='港交所', exchange_en='HKEX',
                    label_zh='IPO+实物分派', label_en='IPO+Distribution', is_reit=False)

    # 介绍上市（实物分派，不发行新股不融资）——优先于港交所判断
    # 排除条件：标题同时含「建議分拆...並於...獨立上市」= 主体是IPO，实物分派只是附加安排
    is_introduction = any(kw in combined for kw in [
        '介绍方式', '以介绍式', 'listing by introduction',
        'distribution in specie', '实物分配',
        '以介紹方式', '介紹上市',   # 繁体
    ])
    # 「实物分派」单独出现才算介绍上市；若同时有「建議分拆...獨立上市」= IPO+附加实物分派
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


def _pdf_check_intro(doc_url, opener):
    """读 PDF 前2页，检测是否是介绍上市/实物分派方式。返回 True/False"""
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        from io import StringIO, BytesIO
        req = Request(doc_url, headers={"User-Agent": "Mozilla/5.0"})
        data = opener.open(req, timeout=20).read()
        out = StringIO()
        extract_text_to_fp(BytesIO(data), out, laparams=LAParams(), page_numbers=[0, 1])
        text = out.getvalue()
        return bool(re.search(r'實物分派|以介紹方式|介紹式上市|listing by introduction|distribution in specie', text, re.I))
    except Exception as e:
        print(f"    PDF检测失败 ({doc_url[-40:]}): {e}", file=sys.stderr)
        return False


def _pdf_check_reit(doc_url, opener):
    """读 PDF 前2页，检测是否是 REIT 分拆。返回 (is_reit, exchange) 元组。"""
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        from io import StringIO, BytesIO
        req = Request(doc_url, headers={"User-Agent": "Mozilla/5.0"})
        data = opener.open(req, timeout=20).read()
        out = StringIO()
        extract_text_to_fp(BytesIO(data), out, laparams=LAParams(), page_numbers=[0, 1])
        text = out.getvalue()
        is_reit = bool(re.search(
            r'不動產投資信託|房地產投資信託|基礎設施基金|基礎設施REITs?|Infrastructure REITs?|'
            r'不动产投资信托|房地产投资信托|基础设施基金|基础设施REITs?|REIT',
            text, re.I))
        if not is_reit:
            return False, None
        # 判断交易所
        if re.search(r'深圳證券交易所|深交所|SZSE|Shenzhen Stock Exchange', text, re.I):
            return True, 'sz'
        if re.search(r'上海證券交易所|上交所|SSE|Shanghai Stock Exchange', text, re.I):
            return True, 'sh'
        return True, None
    except Exception as e:
        print(f"    REIT PDF检测失败 ({doc_url[-40:]}): {e}", file=sys.stderr)
        return False, None


def refine_reit_type(companies, opener):
    """
    对被判为 ipo_hk / ipo_other 的公司，读 PDF 确认是否实为 REIT 分拆。
    命中 → 改为 reit_sz / reit_sh / reit。
    典型误判案例：阿里巴巴（公告标题无 REIT 字样，正文才提到）。
    """
    for c in companies:
        code = c.get('spinType', {}).get('code', '')
        if code not in ('ipo_hk', 'ipo_other'):
            continue
        # 公告标题里有没有任何 REIT 相关词 → 有则已被正确识别，跳过
        all_titles = ' '.join(a.get('title', '') for a in c.get('announcements', []))
        if re.search(r'REIT|不動產投資信託|房地產投資信託|基礎設施基金|基礎設施REITs?', all_titles, re.I):
            continue  # 标题已命中，_classify_spinoff_type 应该已处理，跳过
        # 拿最新（第一条）公告的 PDF
        doc_url = _full_url(c['announcements'][0].get('docUrl', '') if c.get('announcements') else '')
        if not doc_url.endswith('.pdf'):
            continue
        print(f"  🔍 REIT PDF检测: {c['stockCode']} {c['stockName'][:12]} ...", end=' ', flush=True)
        time.sleep(1)
        is_reit, exchange = _pdf_check_reit(doc_url, opener)
        if is_reit:
            if exchange == 'sz':
                c['spinType'] = dict(code='reit_sz', exchange_zh='深交所', exchange_en='SZSE',
                                     label_zh='REIT·深交所', label_en='REIT·SZSE', is_reit=True)
            elif exchange == 'sh':
                c['spinType'] = dict(code='reit_sh', exchange_zh='上交所', exchange_en='SSE',
                                     label_zh='REIT·上交所', label_en='REIT·SSE', is_reit=True)
            else:
                c['spinType'] = dict(code='reit', exchange_zh='REITs', exchange_en='REITs',
                                     label_zh='REIT上市', label_en='REIT Listing', is_reit=True)
            print(f'✅ REIT ({c["spinType"]["code"]}) 确认')
        else:
            print('— 非REIT')
    return companies


def refine_status_from_pdf(companies, opener):
    """
    读最新公告 PDF 前2页，提取记录日期/分派日期，精化状态。
    能识别：已完成分派 / 已批准 / 已定记录日 / 进行中
    """
    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        from io import StringIO, BytesIO
    except ImportError:
        print("  跳过 PDF 状态检测（pdfminer 未安装）")
        return companies

    today_str = today.strftime('%Y-%m-%d')

    for c in companies:
        # 只对状态不明确的公司做 PDF 检测
        cur_status = c.get('_status', get_status(c))
        if cur_status in ('listed', 'terminated'):
            continue
        doc_url = _full_url(c['announcements'][0].get('docUrl', '') if c.get('announcements') else '')
        if not doc_url.endswith('.pdf'):
            continue

        print(f"  🔍 状态PDF检测: {c['stockCode']} {c['stockName'][:12]} ...", end=' ', flush=True)
        time.sleep(1)
        try:
            req = Request(doc_url, headers={"User-Agent": "Mozilla/5.0"})
            data = opener.open(req, timeout=20).read()
            out = StringIO()
            extract_text_to_fp(BytesIO(data), out, laparams=LAParams(), page_numbers=[0, 1])
            text = out.getvalue()
        except Exception as e:
            print(f"失败: {e}")
            continue

        # 1. 已完成：分派日期已过
        dist_m = re.search(
            r'(?:分派日期|分派时间|以实物分派|實物分派|分派日|distribution date)[^\d]{0,20}'
            r'(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            text, re.I)
        if dist_m:
            dist_date = f"{dist_m.group(1)}-{int(dist_m.group(2)):02d}-{int(dist_m.group(3)):02d}"
            if dist_date <= today_str:
                c['_status'] = 'listed'
                c['distributionDate'] = dist_date
                print(f"✅ 已完成分派 ({dist_date})")
                continue
            else:
                c['distributionDate'] = dist_date
                c['_status'] = 'approved'
                print(f"✅ 已确定分派日 ({dist_date})")
                continue

        # 2. 已批准：株东大会通过
        if re.search(r'股東大會.*特別決議案已獲通過|特別決議案已獲通過|特別決議案通過|特别决议案已获通过|特别决议案通过|股東大會批准|股东大会批准', text, re.I):
            if cur_status not in ('prospectus', 'listed'):
                c['_status'] = 'approved'
                print(f"✅ 已批准")
                continue

        # 3. 已定记录日
        rec_m = re.search(
            r'(?:记录日期|记录日|持有人记录日|record date)[^\d]{0,20}'
            r'(20\d{2})\s*年\s*(\d{1,2})\s*月\s*(\d{1,2})\s*日',
            text, re.I)
        if rec_m:
            rec_date = f"{rec_m.group(1)}-{int(rec_m.group(2)):02d}-{int(rec_m.group(3)):02d}"
            c['recordDate'] = rec_date
            if cur_status in ('announced', 'proposed'):
                c['_status'] = 'approved'
                print(f"✅ 已定记录日 ({rec_date})")
                continue

        print('— 无新信息')

    return companies


def _full_url(doc_url):
    """将相对路径补全为完整 URL"""
    if doc_url and not doc_url.startswith('http'):
        return BASE_URL + doc_url
    return doc_url


def refine_intro_type(companies, opener):
    """
    对被判为 ipo_hk 但存在实物分派远项的公司，读 PDF 正文确认是否介绍上市。
    确认为介绍上市 → 改为 intro_hk。
    """
    INTRO_TYPE = dict(code='intro_hk', exchange_zh='港交所', exchange_en='HKEX',
                     label_zh='介紹上市', label_en='Intro Listing', is_reit=False)
    for c in companies:
        if c.get('spinType', {}).get('code') != 'ipo_hk':
            continue
        # 对所有 ipo_hk 公司都做 PDF 检测（介绍上市不一定在标题里体现）
        doc_url = _full_url(c['announcements'][0].get('docUrl', '') if c.get('announcements') else '')
        if not doc_url.endswith('.pdf'):
            continue
        print(f"  🔍 PDF检测: {c['stockCode']} {c['stockName'][:12]} ...", end=' ', flush=True)
        time.sleep(1)
        if _pdf_check_intro(doc_url, opener):
            c['spinType'] = INTRO_TYPE
            print('✅ 介紹上市确认')
        else:
            print('— 保持 IPO')
    return companies


def get_status(company):
    """从公告标题推断分拆进展状态（与前端 _soProgress 保持一致）"""
    ann = company.get('announcements', [])
    if not ann:
        return 'announced'
    t = (ann[0].get('title', '') + (ann[1].get('title', '') if len(ann) > 1 else ''))
    if re.search(r'終止|终止|撤回|撤销|withdraw|cancel', t, re.I):
        return 'terminated'
    if re.search(r'開始買賣|开始买卖|股份開始|股份开始|持續督導|持续督导|行使超額|行使超额|實物分派.*生效|实物分派.*生效', t, re.I):
        return 'listed'
    if re.search(r'刊發招股|招股書|招股章程|招股说明|prospectus', t, re.I):
        return 'prospectus'
    if re.search(r'批準|批准|approved|聯交所批准|获批', t, re.I):
        return 'approved'
    if re.search(r'進展|进展|最新情況|最新情况|延遲|延迟|update|progress', t, re.I):
        return 'progress'
    if re.search(r'建議|建议|擬議|拟议|propose|擬|拟', t, re.I):
        return 'proposed'
    return 'announced'


def load_prev_data():
    """读取上次 spinoff.json，返回 {stockCode: company_dict} 索引"""
    if not os.path.exists(OUT_FILE):
        return {}
    try:
        with open(OUT_FILE) as f:
            data = json.load(f)
        return {c['stockCode']: c for c in data.get('companies', [])}
    except Exception:
        return {}


def refine_ipo_other_via_llm(companies, opener):
    """
    对 spinType=ipo_other（目标交易所待定）的公司，读最新 PDF 前2页，
    用 SiliconFlow LLM 判断目标交易所和子公司名称。
    需要环境变量 SILICONFLOW_KEY。
    """
    sf_key = os.environ.get('SILICONFLOW_KEY', '')
    if not sf_key:
        print("  refine_ipo_other: 无 SILICONFLOW_KEY，跳过")
        return companies

    try:
        from pdfminer.high_level import extract_text_to_fp
        from pdfminer.layout import LAParams
        from io import StringIO, BytesIO
    except ImportError:
        print("  refine_ipo_other: pdfminer 未安装，跳过")
        return companies

    TYPE_MAP = {
        'hkex':  dict(code='ipo_hk',   exchange_zh='港交所', exchange_en='HKEX',
                      label_zh='分拆·港股IPO', label_en='Spinoff·HKEX IPO', is_reit=False),
        'sse':   dict(code='ipo_a_sh',  exchange_zh='上交所', exchange_en='SSE',
                      label_zh='分拆·A股上交所', label_en='Spinoff·A-Share SSE', is_reit=False),
        'szse':  dict(code='ipo_a_sz',  exchange_zh='深交所', exchange_en='SZSE',
                      label_zh='分拆·A股深交所', label_en='Spinoff·A-Share SZSE', is_reit=False),
        'intro': dict(code='intro_hk',  exchange_zh='港交所', exchange_en='HKEX',
                      label_zh='介紹上市', label_en='Intro Listing', is_reit=False),
        'other': None,  # 保持 ipo_other
    }

    targets = [c for c in companies if c.get('spinType', {}).get('code') == 'ipo_other']
    if not targets:
        return companies

    print(f"  refine_ipo_other: 对 {len(targets)} 家调用 LLM 精化...")

    for c in targets:
        doc_url = _full_url(c['announcements'][0].get('docUrl', '') if c.get('announcements') else '')
        if not doc_url.endswith('.pdf'):
            continue
        print(f"  🤖 LLM分类: {c['stockCode']} {c['stockName'][:12]} ...", end=' ', flush=True)
        time.sleep(1)
        try:
            req = Request(doc_url, headers={"User-Agent": "Mozilla/5.0"})
            data = opener.open(req, timeout=20).read()
            out = StringIO()
            extract_text_to_fp(BytesIO(data), out, laparams=LAParams(), page_numbers=[0, 1])
            pdf_text = out.getvalue()[:2000]  # 只取前2000字符
        except Exception as e:
            print(f"PDF读取失败: {e}")
            continue

        prompt = (
            "以下是一份港股上市公司发布的分拆公告（前2页文本）。\n"
            "请判断：\n"
            "1. 子公司计划在哪个交易所上市？选项：hkex（港交所IPO）/ intro（港交所介绍上市）/ sse（A股上交所）/ szse（A股深交所）/ other（其他/未明确）\n"
            "2. 子公司的名称是什么？（如公告未提及，回答'未知'）\n\n"
            "严格按以下格式回答，不要其他内容：\n"
            "exchange: <选项>\n"
            "spinoff_name: <子公司名称>\n\n"
            f"公告文本：\n{pdf_text}"
        )

        text = _sf_call_hk(sf_key, prompt)
        if text is None:
            print("— LLM全部失败，保持 ipo_other")
            continue

        # 解析输出（容错：兼容中英文冒号、多余空格）
        exc_m = re.search(r'exchange[:\uff1a]\s*(\w+)', text, re.I)
        name_m = re.search(r'spinoff_name[:\uff1a]\s*(.+)', text, re.I)
        exc_code = exc_m.group(1).strip().lower() if exc_m else 'other'
        spin_name = name_m.group(1).strip() if name_m else ''
        spin_name = re.sub(r'^[\'"`]+|[\'"`]+$', '', spin_name)  # 去引号
        if spin_name.lower() in ('未知', 'unknown', 'n/a', ''):
            spin_name = ''

        new_type = TYPE_MAP.get(exc_code)
        if new_type:
            c['spinType'] = new_type
            if spin_name:
                c['spinTarget'] = spin_name
            print(f"✅ → {exc_code} | {spin_name or '子公司名未知'}")
        else:
            print(f"— 保持 ipo_other | {spin_name or ''}")
            if spin_name:
                c['spinTarget'] = spin_name

    return companies


# 常用港股公司简体中文名字典（手动维护，优先级高于 LLM）
HK_CN_NAMES = {
    '01171': '兖矿能源',
    '03337': '安东油田',
    '00836': '华润电力',
    '00656': '复星国际',
    '02196': '复星医药',
    '00308': '中旅国际',
    '01109': '华润置地',
    '01979': '天宝集团',
    '00358': '江西铜业',
    '00902': '华能国际',
    '09988': '阿里巴巴',
    '02899': '紫金矿业',
    '00842': '理士国际',
    '01530': '三生制药',
    '00384': '中国燃气',
    '01030': '新城发展',
    '01523': '珩湾科技',
    '00041': '鹰君',
    '07489': '岚图汽车',
    '03393': '威胜控股',
    '02382': '舜宇光学',
    '02096': '先声药业',
    '09888': '百度',
    '01766': '中国中车',
    '00142': '第一太平',
    '08516': '广骏集团',
    '00400': '硬蛋创新',
    '00762': '中国联通',
    '00019': '太古股份',
    '09896': '名创优品',
    '04604': '华润新能源',
    '06655': '华新水泥',
    '00460': '四环医药',
}


def _add_hk_cn_names(companies, api_key):
    """为港股分拆公司添加简体中文名 (nameCN字段)。
    优先级: HK_CN_NAMES 字典 > LLM 翻译。
    """
    need_llm = []
    for c in companies:
        code = c.get('stockCode', '').lstrip('0') or c['ticker'].replace('.HK', '').lstrip('0')
        code5 = c.get('stockCode', c['ticker'].replace('.HK', ''))
        if code5 in HK_CN_NAMES:
            c['nameCN'] = HK_CN_NAMES[code5]
        elif code in HK_CN_NAMES:
            c['nameCN'] = HK_CN_NAMES[code]
        elif not c.get('nameCN'):
            need_llm.append(c)

    if not need_llm or not api_key:
        return

    # LLM 批量翻译（每批 10 家）
    BATCH = 10
    for i in range(0, len(need_llm), BATCH):
        batch = need_llm[i:i+BATCH]
        lines = [f"{c['ticker']} {c['stockName']}" for c in batch]
        prompt = (
            "以下是港股公司的 ticker 和繁体全称。"
            "请输出每家公司简洁的简体中文名称（2-8字，不要股份、集团、有限公司等后缀）。"
            "输出格式：每行 ticker: 简体名，不要其他内容。\n\n"
            + '\n'.join(lines)
        )
        text = _sf_call_hk(api_key, prompt, max_tokens=200)
        if not text:
            continue
        result = {}
        for line in text.splitlines():
            import re as _re
            m = _re.match(r'^(\d{5}\.HK)[:\uff1a]\s*(.+)$', line.strip())
            if m:
                result[m.group(1)] = m.group(2).strip()
        for c in batch:
            if c['ticker'] in result:
                c['nameCN'] = result[c['ticker']]
                # 也写入字典供下次直接命中
                code5 = c.get('stockCode', c['ticker'].replace('.HK', ''))
                HK_CN_NAMES[code5] = result[c['ticker']]
                print(f"  [{c['ticker']}] nameCN={result[c['ticker']]}")
        time.sleep(0.5)


def _gen_hk_ai_summary(companies, api_key):
    """为每家港股分拆公司生成一句话摘要，写入 aiSummary 字段。每批 8 家。"""
    BATCH = 8
    for i in range(0, len(companies), BATCH):
        batch = companies[i:i+BATCH]
        lines = []
        for c in batch:
            spin_type = c.get('spinType', {}).get('label_zh', '')
            spin_target = c.get('spinTarget', '') or c.get('spinTarget', '')
            ann_titles = ' | '.join(
                a.get('title', '')[:40] for a in c.get('announcements', [])[:3]
            )
            lines.append(
                f"{c['stockCode']} {c['stockName']}"
                f"（分拆类型:{spin_type}"
                + (f"，子公司:{spin_target}" if spin_target else "")
                + f"）公告: {ann_titles}"
            )
        prompt = (
            "以下每行是一家港股公司及其分拆公告摘要。\n"
            "请为每家公司生成一句话中文摘要（20-40字），说明分拆进展和子公司业务。\n"
            "输出格式严格为每行 stockCode: 摘要，不要其他内容。\n\n"
            + '\n'.join(lines)
        )
        text = _sf_call_hk(api_key, prompt, max_tokens=300)
        if not text:
            print(f"  第{i//BATCH+1}批 aiSummary 失败")
            continue
        result = {}
        for line in text.splitlines():
            m = re.match(r'^(\d{5})[:\uff1a]\s*(.+)$', line.strip())
            if m:
                result[m.group(1)] = m.group(2).strip()
        for c in batch:
            code = c.get('stockCode', '')
            if code in result:
                c['aiSummary'] = result[code]
                print(f"  {code} {c['stockName'][:8]}: {result[code]}")
        time.sleep(0.5)


def filter_status_driven(companies):
    """状态驱动过滤：已上市超12个月 / 已终止 → 移除"""
    prev = load_prev_data()
    cutoff = (today - timedelta(days=365)).strftime('%Y-%m-%d')
    result = []
    removed = []
    for c in companies:
        status = get_status(c)
        c['_status'] = status  # 暂存，写入 JSON 供调试
        if status == 'terminated':
            removed.append((c['stockCode'], c['stockName'], '已终止'))
            continue
        if status == 'listed':
            # 最新公告日期 <= cutoff（上市超6个月）才移除
            if c.get('latestDate', '9999') <= cutoff:
                removed.append((c['stockCode'], c['stockName'], f'已上市>{cutoff}'))
                continue
        result.append(c)
    if removed:
        print(f"  ⛔ 状态驱动移除: {len(removed)} 家")
        for code, name, reason in removed:
            print(f"      {code} {name} ({reason})")
    return result


def filter_low_price(companies):
    """过滤现价 < 0.2 HKD 的仙股/空壳公司。
    使用新浪财经港股行情 API（批量查询，不限速）替代 yfinance。
    """
    from urllib.request import Request, urlopen
    import re as _re

    # 构建批量查询列表： hkXXXXX 格式
    sina_symbols = ['hk' + c['ticker'].replace('.HK','').lstrip('0').rjust(5,'0')
                    if c['ticker'].replace('.HK','').isdigit()
                    else 'hk' + c['ticker'].replace('.HK','')
                    for c in companies]
    symbol_to_idx = {s: i for i, s in enumerate(sina_symbols)}

    prices = {}  # sina_symbol -> float
    BATCH = 30
    for i in range(0, len(sina_symbols), BATCH):
        batch_syms = sina_symbols[i:i+BATCH]
        url = 'https://hq.sinajs.cn/list=' + ','.join(batch_syms)
        try:
            req = Request(url, headers={
                'Referer': 'https://finance.sina.com.cn',
                'User-Agent': 'Mozilla/5.0'
            })
            with urlopen(req, timeout=10) as resp:
                body = resp.read().decode('gbk', errors='replace')
            for line in body.splitlines():
                m = _re.match(r'var hq_str_(hk\d+)="([^"]*)', line)
                if not m: continue
                sym, fields = m.group(1), m.group(2).split(',')
                # 字段[2] = 昨收，[6] = 现价
                try: prices[sym] = float(fields[6]) if len(fields) > 6 else None
                except (ValueError, IndexError): prices[sym] = None
        except Exception as e:
            print(f"  新浪行情查询失败: {e}")
        time.sleep(0.2)

    result = []
    for c, sym in zip(companies, sina_symbols):
        price = prices.get(sym)
        c['lastPrice'] = round(price, 3) if price else None
        c['marketCap'] = None  # 新浪 API 不返回市值，留空
        if price is not None and price < 0.2:
            print(f"  ⛔ 过滤仙股: {c['ticker']} 现价={price:.3f} HKD")
            continue
        result.append(c)
    print(f"  过滤后剩余: {len(result)} 家公司")
    return result


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
        # 迁册重组：把境外注册的控股公司換成香港注册，不涉及业务分拆
        # 典型：「重组安排计划方式」+「变更.*控股公司」
        is_redomicile = re.search(r'重組安排計劃|重组安排计划|redomicil|scheme of arrangement', all_titles, re.I)
        has_change_holding = re.search(r'變更.*控股公司|更改.*注册地|change.*holding.*compan|將.*控股公司.*變更為|将.*控股公司.*变更为', all_titles, re.I)
        if is_redomicile and has_change_holding:
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

    # PDF 检测：对边缘案例的 ipo_hk 公司确认是否是介绍上市
    print("\nPDF 检测介绍上市...")
    companies = refine_intro_type(companies, opener)

    # PDF 检测：对标题无 REIT 字样的 ipo_hk/ipo_other 公司确认是否是 REIT 分拆
    print("\nPDF 检测 REIT...")
    companies = refine_reit_type(companies, opener)

    # PDF 检测：提取分派日期/记录日，精化状态
    print("\nPDF 检测状态...")
    companies = refine_status_from_pdf(companies, opener)

    # LLM 精化：对目标交易所待定的 ipo_other 公司判断分类
    print("\nLLM 精化 ipo_other 分类...")
    companies = refine_ipo_other_via_llm(companies, opener)

    # 状态驱动过滤：已上市>6个月 / 已终止 → 移除
    print("\n状态驱动过滤...")
    companies = filter_status_driven(companies)

    # 价格过滤
    print("\n价格过滤（排除 <0.5 HKD 仙股）...")
    companies = filter_low_price(companies)

    for c in companies:
        print(f"  {c['ticker']} {c['stockName']} — {len(c['announcements'])} 条公告，最新: {c['latestDate']}")

    # Step 最终: LLM 生成港股分拆 aiSummary
    sf_key = os.environ.get('SILICONFLOW_KEY', '')
    if sf_key:
        print("\nLLM 生成 nameCN（繁转简）...")
        _add_hk_cn_names(companies, sf_key)
        # 已有 aiSummary 的先从旧数据恢复，不重复调用 API
        prev_hk = load_prev_data()
        for c in companies:
            code = c.get('stockCode', '')
            if not c.get('aiSummary') and code in prev_hk and prev_hk[code].get('aiSummary'):
                c['aiSummary'] = prev_hk[code]['aiSummary']
        need_summary_hk = [c for c in companies if not c.get('aiSummary')]
        if need_summary_hk:
            print(f"\nLLM 生成 aiSummary（{len(need_summary_hk)}/{len(companies)} 家需更新）...")
            _gen_hk_ai_summary(need_summary_hk, sf_key)
        else:
            print(f"\naiSummary: 所有 {len(companies)} 家已有，跳过")

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
