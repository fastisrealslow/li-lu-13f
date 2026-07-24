#!/usr/bin/env python3
"""
enrich_metadata.py
------------------
Actions 跑完 13F 抓取后执行：
1. 扫描所有持仓 JSON，找出缺少 cnName 的 ticker
2. 用 yfinance 查 longName / sector
3. 把 cnName、sector 写回各 JSON 文件
4. 同时维护一个全局缓存 metadata_cache.json，避免重复请求
"""

import json, os, re, time, glob
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed, skipping enrich")
    raise SystemExit(0)

CACHE_FILE = "metadata_cache.json"

# 行业映射：yfinance sector -> 中文标签
SECTOR_MAP = {
    "Technology": "科技",
    "Communication Services": "传媒",
    "Consumer Cyclical": "消费",
    "Consumer Defensive": "消费",
    "Financial Services": "金融",
    "Healthcare": "医药",
    "Industrials": "工业",
    "Basic Materials": "材料",
    "Energy": "能源",
    "Real Estate": "地产",
    "Utilities": "公用事业",
    "Financial": "金融",
    "Consumer Discretionary": "消费",
    "Consumer Staples": "消费",
    "Information Technology": "科技",
    "Telecommunication Services": "传媒",
    "Materials": "材料",
}

# 手动覆盖（yfinance 拿不到或分类不准的）
MANUAL_CN_NAME = {
    "BRK.B": "伯克希尔·哈撒韦B",
    "BRK.A": "伯克希尔·哈撒韦A",
    "BABA": "阿里巴巴",
    "PDD": "拼多多",
    "JD": "京东",
    "BIDU": "百度",
    "TME": "腾讯音乐",
    "NIO": "蔚来",
    "XPEV": "小鹏汽车",
    "LI": "理想汽车",
    "KWEB": "中概互联ETF",
    "SPGI": "标普全球",
    "HRB": "H&R Block",
    "HCC": "冶金煤业",
    "RIG": "越洋钻探",
    "AMR": "阿尔法金属",
    "SRG": "Seritage成长地产",
    "RACE": "法拉利",
    "GSHD": "Goosehead保险",
    "CSGP": "CoStar集团",
    "BLDR": "建筑商FirstSource",
    "ORLY": "奥莱利汽车",
    "MCO": "穆迪",
    "KKR": "KKR集团",
    "BN": "布鲁克菲尔德",
    "MA": "万事达卡",
    "V": "Visa",
    "GOOGL": "谷歌A",
    "GOOG": "谷歌C",
    "MSFT": "微软",
    "AAPL": "苹果",
    "AMZN": "亚马逊",
    "NVDA": "英伟达",
    "META": "Meta",
    "TSLA": "特斯拉",
    "CROX": "卡骆驰",
    "KHC": "卡夫亨氏",
    "STZ": "星座品牌",
    "CVX": "雪佛龙",
    "OXY": "西方石油",
    "BAC": "美国银行",
    "AXP": "美国运通",
    "KO": "可口可乐",
    "MCK": "麦克森",
    "DVA": "达维塔",
    "CB": "丘博保险",
    "DAL": "达美航空",
    "ALLY": "Ally金融",
    "LEN": "莱纳建筑",
    "SLM": "萨利美",
    "PRI": "Primerica",
    "ICLR": "ICON临床",
    "ELV": "信诺健康",
    "MPLX": "MPLX管道",
    "WHR": "惠而浦",
    "MU": "美光科技",
    "UBER": "优步",
    "TSM": "台积电",
    "LRCX": "拉姆研究",
    "AMD": "超微半导体",
    "QCOM": "高通",
    "LYFT": "Lyft",
    "ET": "能源传输",
    "NRG": "NRG能源",
    "GLW": "康宁",
    "LHX": "L3哈里斯",
    "RTX": "雷神技术",
    "BALL": "鲍尔公司",
    "UNH": "联合健康",
    "EWBC": "华美银行",
    "TEM": "Tempus AI",
}

MANUAL_SECTOR = {
    "KWEB": "电商",
    "PDD": "电商",
    "BABA": "电商",
    "JD": "电商",
    "TME": "娱乐",
    "BIDU": "科技",
    "NIO": "科技",
    "BRK.B": "金融",
    "BRK.A": "金融",
    "SRG": "地产",
    "AMR": "能源",
    "HCC": "能源",
    "RIG": "能源",
}

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            return json.load(open(CACHE_FILE))
        except:
            pass
    return {}

def save_cache(cache):
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def fetch_yf_info(ticker, cache):
    """查 yfinance，返回 (longName, sector_zh)，优先用缓存"""
    if ticker in cache:
        return cache[ticker].get('cnName',''), cache[ticker].get('sector','')

    # 手动覆盖优先
    cn = MANUAL_CN_NAME.get(ticker, '')
    sec = MANUAL_SECTOR.get(ticker, '')

    if not cn or not sec:
        try:
            yf_ticker = ticker.replace('BRK.B','BRK-B').replace('BRK.A','BRK-A')
            info = yf.Ticker(yf_ticker).info
            if not cn:
                cn = info.get('longName','') or info.get('shortName','')
            if not sec:
                yf_sec = info.get('sector','')
                sec = SECTOR_MAP.get(yf_sec, sec)
            time.sleep(0.4)
        except Exception as e:
            print(f"    yfinance error {ticker}: {e}")
            # 限流/失败时用 ticker 本身作为 fallback，避免前端显示空白
            if not cn:
                cn = ticker

    cache[ticker] = {'cnName': cn, 'sector': sec}
    return cn, sec

def enrich_holdings(holdings, cache, changed_tickers):
    """给 holdings 列表里缺失 cnName/sector 的条目补全"""
    for h in holdings:
        tk = h.get('ticker','')
        if not tk or tk.startswith('?'):
            continue

        need_cn = not h.get('cnName','')
        need_sec = not h.get('sector','') or h.get('sector') == '其他'

        if need_cn or need_sec:
            cn, sec = fetch_yf_info(tk, cache)
            if need_cn and cn:
                h['cnName'] = cn
                changed_tickers.add(tk)
                print(f"    {tk} cnName → {cn}")
            if need_sec and sec:
                h['sector'] = sec
                changed_tickers.add(tk)
                print(f"    {tk} sector → {sec}")

def process_file(filepath, cache):
    """处理单个数据 JSON 文件"""
    try:
        d = json.load(open(filepath))
    except Exception as e:
        print(f"  ⚠️  {filepath} load error: {e}")
        return

    changed = set()

    # current holdings
    cur = d.get('current', {}).get('holdings', [])
    if cur:
        enrich_holdings(cur, cache, changed)

    # history holdings
    hist = d.get('history', {})
    # 支持两种结构：{quarter: [holdings]} 或 {holdings: {quarter: [holdings]}}
    hist_qs = hist.get('holdings', hist) if isinstance(hist, dict) else {}
    if isinstance(hist_qs, dict):
        for q, hs in hist_qs.items():
            if isinstance(hs, list):
                enrich_holdings(hs, cache, changed)

    if changed:
        with open(filepath, 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"  ✅ {filepath} 更新了 {len(changed)} 个 ticker")
    else:
        print(f"  ⏭  {filepath} 无需更新")


# SiliconFlow 免费模型 fallback 列表
_SF_MODELS_EN = [
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.5-4B",
    "THUDM/glm-4-9b-chat",
]


def _sf_call_enrich(api_key, prompt, max_tokens=400, retries=2):
    """健壮 SiliconFlow 调用：multi-model fallback + 重试"""
    try:
        from urllib.request import Request, urlopen
    except ImportError:
        return None
    for model in _SF_MODELS_EN:
        for attempt in range(retries + 1):
            try:
                payload = json.dumps({
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": 0.3,
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
                with urlopen(req, timeout=40) as resp:
                    data = json.loads(resp.read())
                text = data['choices'][0]['message']['content'].strip()
                if text:
                    return text
            except Exception as e:
                wait = 2 ** attempt
                print(f"  [{model}] 第{attempt+1}次失败: {e}"
                      + (f"，{wait}s后重试" if attempt < retries else "，放弃"))
                if attempt < retries:
                    time.sleep(wait)
        print(f"  模型 {model} 全部失败")
    return None


def _gen_13f_summaries(api_key):
    """
    读取各投资者最新季报变动，用 LLM 生成中文摘要，
    写入各 JSON 文件的 meta.aiSummary 字段。
    """
    FILES = [
        ('data.json',       '李录'),
        ('pabrai_data.json','帕布莱'),
        ('duan.json',       '段永平'),
        ('tepper.json',     '泰珀'),
        ('akre.json',       '阿克雷'),
        ('greenberg.json',  '格林伯格'),
        ('buffett.json',    '巴达特'),
    ]
    for filepath, investor_cn in FILES:
        if not os.path.exists(filepath):
            continue
        try:
            d = json.load(open(filepath))
        except Exception:
            continue

        cur = d.get('current', {})
        quarter = cur.get('quarter', '')
        holdings = cur.get('holdings', [])
        if not holdings:
            continue

        # 构造变动列表
        new_pos, added, reduced, exited = [], [], [], []
        for h in holdings:
            t   = h.get('ticker', '')
            cn  = h.get('cnName', '') or h.get('name', t)
            s   = h.get('shares', 0)
            ps  = h.get('prevShares')
            if ps is None or ps == 0:
                new_pos.append(cn)
            elif s == 0:
                exited.append(cn)
            elif s > ps * 1.1:
                pct = (s - ps) / ps * 100
                added.append(f"{cn}(+{pct:.0f}%)")
            elif s < ps * 0.9:
                pct = (ps - s) / ps * 100
                reduced.append(f"{cn}(-{pct:.0f}%)")

        if not (new_pos or added or exited or reduced):
            print(f"  {investor_cn} {quarter}: 无变动，跳过")
            continue

        parts = []
        if new_pos:  parts.append("新建仓位: " + '、'.join(new_pos[:4]))
        if added:    parts.append("增持: " + '、'.join(added[:4]))
        if reduced:  parts.append("减持: " + '、'.join(reduced[:4]))
        if exited:   parts.append("清仓: " + '、'.join(exited[:4]))
        change_str = '；'.join(parts)

        top5 = '、'.join(
            (h.get('cnName') or h.get('name', h.get('ticker', '')))
            for h in sorted(holdings, key=lambda x: x.get('value', 0), reverse=True)[:5]
        )

        prompt = (
            f"以下是价値投资人{investor_cn}在{quarter}的季报变动。\n"
            f"重仓前5: {top5}\n"
            f"变动: {change_str}\n\n"
            "请用中文写一句话（30-60字）概述本季最重要的操作和可能含义。"
            "不要编造没有的信息，不要写剥析和预测。"
        )

        text = _sf_call_enrich(api_key, prompt, max_tokens=120)
        if not text:
            print(f"  {investor_cn} LLM 失败")
            continue

        # 写入 meta.aiSummary
        if 'meta' not in d:
            d['meta'] = {}
        d['meta']['aiSummary'] = text
        d['meta']['aiSummaryQuarter'] = quarter
        with open(filepath, 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        print(f"  {investor_cn} {quarter}: {text}")
        time.sleep(1)


def _gen_homework_summary(api_key):
    """
    跨投资人聚合价值筛选（MOS>=10%）候选股，
    用 LLM 生成一段总结，写入 homework_summary.json
    逻辑与前端 renderHomework() 保持一致（MOS计算、共识计数、新开仓/加仓标记）
    """
    FILES = [
        ('data.json',        'prices.json',           '李录'),
        ('pabrai_data.json', 'pabrai_prices.json',     '帕伯莱'),
        ('duan.json',        'prices_duan.json',       '段永平'),
        ('tepper.json',      'prices_tepper.json',     'Tepper'),
        ('akre.json',        'prices_akre.json',       'Akre'),
        ('greenberg.json',   'prices_greenberg.json',  'Greenberg'),
        ('buffett.json',     'prices_buffett.json',    '巴菲特'),
    ]

    candidates = {}  # ticker -> {name, mos, buy, investors:[], holders:set}
    for df, pf, name_cn in FILES:
        if not (os.path.exists(df) and os.path.exists(pf)):
            continue
        try:
            dr = json.load(open(df))
            pr = json.load(open(pf))
        except Exception:
            continue
        holdings = dr.get('current', {}).get('holdings', [])
        total_val = dr.get('current', {}).get('totalValue', 0)
        quotes = pr.get('quotes', {})
        cb = pr.get('costBasis', {})
        for h in holdings:
            tk = h.get('ticker', '')
            if not tk or tk.startswith('?') or tk.endswith('.HK'):
                continue
            q = quotes.get(tk)
            c = cb.get(tk)
            if not q or q.get('error') or not c:
                continue
            rc = c.get('recent')
            if not rc or not rc.get('buy'):
                continue
            price = q.get('c', 0)
            buy = rc.get('buy', 0)
            if price <= 0 or buy <= 0:
                continue
            mos = (buy - price) / buy * 100
            if mos < 10:
                continue
            prev = h.get('prevShares', 0) or 0
            cur_sh = h.get('shares', 0) or 0
            if prev == 0 and cur_sh > 0:
                chg = 'new'
            elif prev > 0 and cur_sh > prev * 1.05:
                chg = 'added'
            elif prev > 0 and cur_sh < prev * 0.95:
                chg = 'trimmed'
            else:
                chg = 'hold'
            entry = candidates.get(tk)
            cn_name = h.get('cnName') or h.get('name', tk)
            if entry:
                entry['holders'].add(name_cn)
                if chg in ('new', 'added'):
                    entry['signals'].add(chg)
                if buy < entry['buy']:
                    entry['buy'] = buy
                    entry['mos'] = round(mos, 1)
            else:
                candidates[tk] = {
                    'name': cn_name, 'mos': round(mos, 1), 'buy': buy,
                    'holders': {name_cn},
                    'signals': {chg} if chg in ('new', 'added') else set(),
                }

    if not candidates:
        print("  无候选股，跳过 homework summary")
        return

    # 排序：共识人数 desc, MOS desc
    ranked = sorted(candidates.items(), key=lambda kv: (len(kv[1]['holders']), kv[1]['mos']), reverse=True)

    consensus_lines = []
    new_or_added = []
    for tk, v in ranked[:15]:
        if len(v['holders']) >= 2:
            consensus_lines.append(f"{v['name']}({tk}) 安全边际{v['mos']}% 被{len(v['holders'])}人持有[{'/'.join(sorted(v['holders']))}]")
        if v['signals']:
            new_or_added.append(f"{v['name']}({tk}) {'/'.join(v['signals'])}")

    prompt = (
        "以下是根据多位价值投资人13F持仓筛选出的安全边际>=10%的股票列表。\n"
        f"多人共识股（被2人以上持有）: {'; '.join(consensus_lines) if consensus_lines else '无'}\n"
        f"最近新开仓/加仓信号: {'; '.join(new_or_added) if new_or_added else '无'}\n\n"
        "请用中文写一段话（40-80字）概述这个筛选列表中最值得关注的信号（如多人共识或新开仓/加仓）。"
        "不要编造没有的信息，不要给出投资建议。"
    )

    text = _sf_call_enrich(api_key, prompt, max_tokens=200)
    if not text:
        print("  homework summary LLM 失败")
        return

    out = {
        'aiSummary': text,
        'generatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'candidateCount': len(candidates),
        'consensusCount': sum(1 for v in candidates.values() if len(v['holders']) >= 2),
    }
    with open('homework_summary.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  homework summary: {text}")


def main():
    print("=== enrich_metadata.py 开始 ===")
    cache = load_cache()
    print(f"缓存已有 {len(cache)} 个 ticker")

    data_files = [
        'data.json', 'pabrai_data.json', 'duan.json', 'tepper.json',
        'akre.json', 'greenberg.json', 'buffett.json', 'webb.json',
        'hk_holdings.json', 'duan_hk.json', 'tepper_hk.json',
        'buffett_hk.json', 'akre_hk.json', 'greenberg_hk.json', 'pabrai_hk.json',
    ]

    for f in data_files:
        if os.path.exists(f):
            print(f"\n处理 {f}...")
            process_file(f, cache)
        else:
            print(f"\n跳过 {f}（不存在）")

    save_cache(cache)
    print(f"\n=== 完成，缓存更新为 {len(cache)} 个 ticker ===")

    # LLM 生成 13F 季报变动摘要
    sf_key = os.environ.get('SILICONFLOW_KEY', '')
    if sf_key:
        print("\n=== LLM 生成 13F 季报摘要 ===")
        _gen_13f_summaries(sf_key)

        print("\n=== LLM 生成价值筛选总结 ===")
        _gen_homework_summary(sf_key)

if __name__ == '__main__':
    main()
