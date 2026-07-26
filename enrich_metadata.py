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

import json, os, re, sys, time, glob, hashlib
from datetime import datetime, timezone

try:
    import yfinance as yf
except ImportError:
    print("yfinance not installed, skipping enrich")
    raise SystemExit(0)


def load_investors():
    """从 investors.json 读取投资者配置列表（单一权威来源）。
    新增投资者只需编辑 investors.json，此函数会自动反映到
    enrich_metadata 的处理范围，无需在本文件手工维护列表。"""
    try:
        with open('investors.json', encoding='utf-8') as f:
            return json.load(f)['investors']
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"WARNING: investors.json 读取失败（{e}），跳过 metadata 丰富", file=sys.stderr)
        return []

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


# SiliconFlow 模型 fallback 列表（由 test_model_comparison.yml 对比选出）：
# 主选 Qwen3.5-9B（低价几乎免费，¥0.1/¥0.15每M token，两轮测试无编造且表达最准确），
# fallback 免费模型 Qwen3.5-4B，再 fallback 到低价 GLM-4.5-Air。
# 旧的 THUDM/glm-4-9b-chat 已确认被 SiliconFlow 下线，换掉。
_SF_MODELS_EN = [
    "Qwen/Qwen3.5-9B",
    "Qwen/Qwen3.5-4B",
    "zai-org/GLM-4.5-Air",
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
    investors = load_investors()
    if investors:
        # 只对走 13F 流程的投资者生成季报变动摘要（webb 是港股权益披露，不适用）
        FILES = [(inv['dataFile'], inv['name']) for inv in investors if inv.get('source13F')]
    else:
        # investors.json 缺失时的安全兼底
        FILES = [
            ('data.json',       '李录'),
            ('pabrai_data.json','帕布莱'),
            ('duan.json',       '段永平'),
            ('tepper.json',     '泰珀'),
            ('akre.json',       '阿克雷'),
            ('greenberg.json',  '格林伯格'),
            ('buffett.json',    '巴菲特'),
            ('klarman.json',    '克拉曼'),
            ('ackman.json',     '阿克曼'),
            ('abrams.json',     '艾布拉姆斯'),
            ('berkowitz.json',  '伯科威茨'),
            ('hawkins.json',    '霍金斯'),
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


def _q2n(q):
    """'2025 Q2' -> 8101 类型的可比较整数，季度细粒度"""
    y, n = q.split(' Q')
    return int(y) * 4 + int(n)


def _hold_quarters(first_q, cur_q):
    """计算从首次建仓季度到当前季度的持仓季数"""
    try:
        return max(_q2n(cur_q) - _q2n(first_q) + 1, 1)
    except Exception:
        return None


def _ticker_quarter_series(dr, tk):
    """
    从 dr['history']['holdings'] 中提取某 ticker 在每个季度的持仓股数（同 ticker 多条记录求和），
    返回按季度升序排列的 [(quarter, shares), ...]，仅包含存在该 ticker 的季度（shares=0 不会出现，
    因为清仓季度通常不再出现在该季度的 13F holdings 列表里）。
    """
    hist = dr.get('history', {})
    quarters = hist.get('quarters', [])
    hk = hist.get('holdings', {})
    series = []
    for q in quarters:
        entries = hk.get(q, [])
        sh = sum(e.get('shares', 0) or 0 for e in entries if e.get('ticker') == tk)
        if sh > 0:
            series.append((q, sh))
    series.sort(key=lambda x: _q2n(x[0]))
    return series


def _analyze_holding_pattern(series):
    """
    基于 (quarter, shares) 序列分析持仓模式：
    - trend: 'accumulating' 连续>=3季且无减仓地加仓(末3季) / 'reducing' 连续减仓 / 'stable' 其他
    - reentry: True 若历史上存在 gap>4 季的清仓断层（与 fetch_prices_all.py 里 gap>4 重置规则保持一致）
    - exit_quarter: 若 reentry 为 True，返回最后一次清仓前的最后持仓季度（用于文案提及）
    """
    result = {'trend': 'stable', 'reentry': False, 'exit_quarter': None, 'reentry_quarter': None}
    if len(series) < 2:
        return result
    # 检测 gap>4 断层（取最后一次断层）
    for i in range(1, len(series)):
        gap = _q2n(series[i][0]) - _q2n(series[i - 1][0])
        if gap > 4:
            result['reentry'] = True
            result['exit_quarter'] = series[i - 1][0]
            result['reentry_quarter'] = series[i][0]
    # 连续趋势仅看最近一段连续持仓（断层后的部分）
    run = series
    if result['reentry']:
        rq = result['reentry_quarter']
        run = [s for s in series if _q2n(s[0]) >= _q2n(rq)]
    if len(run) >= 3:
        recent3 = run[-3:]
        if recent3[0][1] < recent3[1][1] < recent3[2][1]:
            result['trend'] = 'accumulating'
        elif recent3[0][1] > recent3[1][1] > recent3[2][1]:
            result['trend'] = 'reducing'
    return result


def _mos_tier(mos):
    if mos >= 30:
        return "深度折价"
    if mos >= 15:
        return "中等折价"
    return "轻度折价"


_CHG_LABEL = {'new': '本季新开仓', 'added': '本季加仓', 'trimmed': '本季减仓', 'hold': '仓位未变'}

# 持有人中文名 -> 英文名映射（与 app.js 中 INVESTORS_CFG 的 name/nameEn 保持一致）
_INVESTOR_EN = {
    '李录': 'Li Lu', '帕伯莱': 'Pabrai', '段永平': 'Duan', 'Tepper': 'Tepper',
    'Akre': 'Akre', 'Greenberg': 'Greenberg', '巴菲特': 'Buffett',
}


def _investor_en(name_cn):
    return _INVESTOR_EN.get(name_cn, name_cn)


def _gen_verdict(v, mos_tier):
    """
    规则式生成逐股判断结论句（代码拼接，不经过LLM，保证可复现、不编造）。
    综合维度：安全边际深浅、共识人数、持有人动作是否分化（有人加仓有人减仓）、
    是否新开仓、最大持仓权重。返回 (中文判断语, 英文判断语) 二元组。
    """
    holders = v['holders']
    n = len(holders)
    max_weight = max((h['weight'] for h in holders), default=0)
    chgs = set(h['chg'] for h in holders)
    has_added = 'added' in chgs or 'new' in chgs
    has_trimmed = 'trimmed' in chgs
    divergent = has_added and has_trimmed
    all_new = n >= 1 and all(h['chg'] == 'new' for h in holders)
    all_added = n >= 1 and all(h['chg'] in ('new', 'added') for h in holders)
    all_trimmed = n >= 1 and all(h['chg'] == 'trimmed' for h in holders)
    deep = mos_tier == '深度折价'
    shallow = mos_tier == '轻度折价'

    # 多人共识 + 动作分化
    if n >= 2 and divergent:
        depth_desc = '但折价浅' if shallow else ('且折价充足' if deep else '折价适中')
        depth_en = 'but the discount is shallow' if shallow else ('and the discount is deep enough' if deep else 'with a moderate discount')
        return (
            f"共识度高{depth_desc}、且持有人动作分化，属于\"关注但不宜追高\"的类型。",
            f"High consensus {depth_en}, but holders are diverging (some adding, some trimming) — worth watching but not chasing."
        )

    # 多人共识 + 一致加仓/新开仓
    if n >= 2 and all_added:
        depth_desc = '安全边际也较为充足' if deep else '但安全边际仅属中等'
        depth_en = 'with an ample margin of safety' if deep else 'though the margin of safety is only moderate'
        return (
            f"多位投资人一致看多且{depth_desc}，属于本期信号最强的共识股之一。",
            f"Multiple investors are unanimously bullish, {depth_en} — one of the strongest consensus signals this period."
        )

    # 多人共识 + 一致减仓/无动作
    if n >= 2 and all_trimmed:
        return (
            "多人持有但本季集体减仓，共识度虽高，动能已在减弱，宜观察后续变化。",
            "Held by multiple investors but collectively trimmed this quarter — consensus is high but momentum is fading; watch for further changes."
        )

    # 单人持有 + 深度折价 + 长期持有 + 本季减仓（如惠而浦案例）
    if n == 1 and deep and has_trimmed and (holders[0].get('hold_years') or 0) >= 5:
        yrs = int(holders[0]['hold_years'])
        return (
            f"持仓超{yrs}年的老仓位却在深度折价区减仓，可能反映基本面担忧大于估值吸引力，需警惕价值陷阱。",
            f"A position held for over {yrs} years is being trimmed despite trading at a deep discount — may signal fundamental concerns outweighing valuation appeal; watch for a value trap."
        )

    # 单人持有 + 深度折价 + 长期持有 + 仓位未变
    if n == 1 and deep and 'hold' in chgs and (holders[0].get('hold_years') or 0) >= 5:
        size_desc = '，但仓位并不重' if max_weight < 3 else ''
        size_en = ', though the position size is not large,' if max_weight < 3 else ''
        return (
            f"深度折价且长期持有未动{size_desc}，更像是低成本的安心底仓，而非新的买入信号。",
            f"Deep discount with a long-held, unchanged position{size_en} looks more like a low-cost core holding than a fresh buy signal."
        )

    # 单人 + 新开仓 + 高仓位（如帕伯莱AMR、段永平特斯拉案例）
    if n == 1 and all_new and max_weight >= 3:
        return (
            f"新开仓即给到{max_weight}%的高仓位，显示极强的信心，值得重点关注。",
            f"A brand-new position sized at {max_weight}% right away signals very strong conviction — worth watching closely."
        )

    # 单人 + 加仓 + 高仓位
    if n == 1 and 'added' in chgs and max_weight >= 10:
        return (
            f"单一持有人以{max_weight}%重仓且本季继续加仓，属于高确定性的重仓信号。",
            f"A single holder has {max_weight}% weighted in and kept adding this quarter — a high-conviction, heavily-weighted signal."
        )

    # 单人 + 加仓（仓位不到十但仍在主动加仓）+ 深度/中等折价
    if n == 1 and 'added' in chgs and deep:
        return (
            f"单一持有人在深度折价区主动加仓（{max_weight}%仓位），虽无共识但信心明确，值得关注。",
            f"A single holder is actively adding at a deep discount ({max_weight}% position) — no consensus yet, but conviction is clear; worth watching."
        )
    if n == 1 and 'added' in chgs:
        return (
            f"单一持有人本季主动加仓（{max_weight}%仓位），属于积极信号，但安全边际仅属中等，可作为次优先观察。",
            f"A single holder added this quarter ({max_weight}% position) — a positive signal, though the margin of safety is only moderate; a secondary watchlist candidate."
        )

    # 单人 + 新开仓 + 小仓位
    if n == 1 and all_new and max_weight < 3:
        who = holders[0]['investor']
        who_en = _investor_en(who)
        return (
            f"{who}新开仓但仓位较小（{max_weight}%），更像是试探性布局，信心程度有待后续季度验证。",
            f"{who_en}'s new position is small ({max_weight}%) — looks more like an exploratory stake; conviction level remains to be confirmed in future quarters."
        )

    # 单人 + 减仓
    if n == 1 and has_trimmed:
        return (
            "仅单一持有人且本季减仓，安全边际虽达标，但缺乏共识支持，须谨慎看待。",
            "Only one holder, and they trimmed this quarter — the margin of safety qualifies, but there's no consensus support; approach with caution."
        )

    # 单人 + 仓位未变，兜底（若近3季存在真实连续加仓/减仓趋势，优先用趋势描述而不是"未变"）
    if n == 1 and 'hold' in chgs:
        if deep:
            depth_desc, depth_en = '安全边际充足', 'the margin of safety is ample'
        elif shallow:
            depth_desc, depth_en = '安全边际仅略微达标', 'the margin of safety only barely qualifies'
        else:
            depth_desc, depth_en = '安全边际仅属中等', 'the margin of safety is only moderate'
        trend = holders[0].get('trend')
        if trend == 'accumulating':
            return (
                f"仅单一持有人持有，本季环比变化轻微但近3季实际上在持续加仓，{depth_desc}，倾向性信号偏积极。",
                f"Only one holder, and while the quarter-over-quarter change is small, they've been steadily accumulating over the past 3 quarters; {depth_en} — a mildly positive signal."
            )
        if trend == 'reducing':
            return (
                f"仅单一持有人持有，本季环比变化轻微但近3季实际上在持续减仓，即使{depth_desc}，仍建议谨慎对待。",
                f"Only one holder, and while the quarter-over-quarter change is small, they've been steadily trimming over the past 3 quarters; even though {depth_en}, caution is still advised."
            )
        return (
            f"仅单一持有人持有且仓位未变，{depth_desc}，可作为观察名单但暂无新增信号。",
            f"Only one holder, position unchanged, and {depth_en} — fine as a watchlist name but no new signal for now."
        )


    # 默认兜底
    depth_desc = '折价充足' if deep else ('折价较浅' if shallow else '折价适中')
    depth_en = 'the discount is ample' if deep else ('the discount is shallow' if shallow else 'the discount is moderate')
    return (
        f"{depth_desc}，共{n}人持有，暂无明显一致性信号，建议结合基本面进一步验证。",
        f"{depth_en.capitalize()}, held by {n} investor(s), with no clear consistent signal — recommend further fundamental validation."
    )


def _build_homework_prompt():
    """
    跨投资人聚合价值筛选（MOS>=10%）候选股，逐股计算结构化点评
    （仓位占比、持仓时间、安全边际分级、加减仓信号均由代码计算，保证准确）。
    返回 (prompt, stock_notes, candidates) 供 _gen_homework_summary 和
    test_llm_models.py 共用，避免两处逻辑漂移。
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

    candidates = {}  # ticker -> {name, sector, mos, buy, price, holders:[{investor,chg,weight,hold_quarters,hold_years}]}
    near_miss = {}  # ticker -> [(investor, mos)] — 持有但安全边际未达10%门槛而被过滤的持有人
    for df, pf, name_cn in FILES:
        if not (os.path.exists(df) and os.path.exists(pf)):
            continue
        try:
            dr = json.load(open(df))
            pr = json.load(open(pf))
        except Exception:
            continue
        cur = dr.get('current', {})
        holdings = cur.get('holdings', [])
        total_val = cur.get('totalValue', 0)
        cur_q = cur.get('quarter', '')
        quotes = pr.get('quotes', {})
        cb = pr.get('costBasis', {})

        # 同一持有人对同一 ticker 可能有多条 13F 记录（不同批次/份额类别），先合并
        merged = {}
        for h in holdings:
            tk = h.get('ticker', '')
            if not tk:
                continue
            if tk in merged:
                merged[tk]['shares'] += h.get('shares', 0) or 0
                merged[tk]['prevShares'] += h.get('prevShares', 0) or 0
                merged[tk]['value'] += h.get('value', 0) or 0
            else:
                merged[tk] = {
                    'shares': h.get('shares', 0) or 0,
                    'prevShares': h.get('prevShares', 0) or 0,
                    'value': h.get('value', 0) or 0,
                    'cnName': h.get('cnName') or h.get('name', tk),
                    'sector': h.get('sector', ''),
                }

        for tk, h in merged.items():
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
                if mos > 0:  # 仅记录仍有正安全边际但未达标的情况，避免噪声
                    near_miss.setdefault(tk, []).append((name_cn, round(mos, 1)))
                continue
            prev = h['prevShares']
            cur_sh = h['shares']
            if prev == 0 and cur_sh > 0:
                chg = 'new'
            elif prev > 0 and cur_sh > prev * 1.05:
                chg = 'added'
            elif prev > 0 and cur_sh < prev * 0.95:
                chg = 'trimmed'
            else:
                chg = 'hold'
            weight = (h['value'] / total_val * 100) if total_val else 0
            at = c.get('allTime') or {}
            hq_n = _hold_quarters(at['first'], cur_q) if at.get('first') else None
            hq_yrs = round(hq_n / 4, 1) if hq_n else None

            series = _ticker_quarter_series(dr, tk)
            pattern = _analyze_holding_pattern(series)

            investor_detail = {
                'investor': name_cn, 'chg': chg, 'weight': round(weight, 1),
                'hold_quarters': hq_n, 'hold_years': hq_yrs,
                'trend': pattern['trend'], 'reentry': pattern['reentry'],
                'exit_quarter': pattern['exit_quarter'], 'reentry_quarter': pattern['reentry_quarter'],
            }

            entry = candidates.get(tk)
            if entry:
                entry['holders'].append(investor_detail)
                if buy < entry['buy']:
                    entry['buy'] = round(buy, 2)
                    entry['mos'] = round(mos, 1)
            else:
                candidates[tk] = {
                    'name': h['cnName'], 'sector': h['sector'], 'mos': round(mos, 1),
                    'buy': round(buy, 2), 'price': round(price, 2),
                    'holders': [investor_detail],
                }

    if not candidates:
        return None, [], {}, None

    # 排序：共识人数 desc, MOS desc
    ranked = sorted(candidates.items(), key=lambda kv: (len(kv[1]['holders']), kv[1]['mos']), reverse=True)

    # 逐股生成结构化点评（代码拼接，不经过LLM，保证数字准确）
    stock_notes = []
    consensus_lines = []
    new_or_added = []
    strong_signals = []  # 高仓位+主动加仓/新开仓 的强信号股，供 LLM 归纳引用
    for tk, v in ranked[:15]:
        holder_names = {h['investor'] for h in v['holders']}
        v['near_miss'] = [(nm, m) for nm, m in near_miss.get(tk, []) if nm not in holder_names]
        holder_descs = []
        for h in v['holders']:
            w_desc = f"{h['weight']}%仓位" if h['weight'] >= 0.5 else "极小仓位(<0.5%)"
            if h.get('reentry') and h['hold_quarters']:
                # 清仓重入：明确标注本轮重建仓时间，避免用户误以为“持仓年限”是一直未断的
                hold_desc = f"本轮{h['reentry_quarter']}重建仓后持有{h['hold_quarters']}季/{h['hold_years']}年（此前于{h['exit_quarter']}清仓过）"
            elif h['hold_quarters']:
                hold_desc = f"持有{h['hold_quarters']}季/{h['hold_years']}年"
            else:
                hold_desc = "首次建仓"
            trend_desc = ''
            if h.get('trend') == 'accumulating':
                trend_desc = "，近3季连续加仓"
            elif h.get('trend') == 'reducing':
                trend_desc = "，近3季连续减仓"
            holder_descs.append(f"{h['investor']}（{w_desc}，{hold_desc}{trend_desc}，{_CHG_LABEL[h['chg']]}）")
            if h['chg'] in ('new', 'added') and h['weight'] >= 3:
                strong_signals.append(f"{v['name']}({tk})：{h['investor']}{w_desc}且{_CHG_LABEL[h['chg']]}")

        mos_tier = _mos_tier(v['mos'])
        verdict_cn, verdict_en = _gen_verdict(v, mos_tier)
        if v.get('near_miss'):
            nm_cn = '、'.join(f"{nm}（{m}%）" for nm, m in v['near_miss'])
            nm_en = '、'.join(f"{_investor_en(nm)} ({m}%)" for nm, m in v['near_miss'])
            nm_verb = 'holds' if len(v['near_miss']) == 1 else 'hold'
            verdict_cn += f"另外{nm_cn}也持有本股，但安全边际尚未达到10%门槛，未计入共识持有人。"
            verdict_en += f" {nm_en} also {nm_verb} this stock, but the margin of safety hasn't reached the 10% threshold yet, so {'they are' if nm_verb=='hold' else 'it is'} not counted among the consensus holders."
        note = {
            'ticker': tk, 'name': v['name'], 'sector': v['sector'],
            'mos': v['mos'], 'mosTier': mos_tier,
            'buy': v['buy'], 'price': v['price'],
            'holderCount': len(v['holders']),
            'holders': v['holders'],
            'holderText': '；'.join(holder_descs),
            'nearMiss': [
                {'investor': nm, 'mos': m, 'investorEn': _investor_en(nm)}
                for nm, m in v.get('near_miss', [])
            ],
            'verdict': verdict_cn,
            'verdictEn': verdict_en,
        }
        stock_notes.append(note)

        if len(v['holders']) >= 2:
            consensus_lines.append(f"{v['name']}({tk}) 安全边际{v['mos']}% 被{len(v['holders'])}人持有[{'/'.join(h['investor'] for h in v['holders'])}]")
        signals_here = [h['chg'] for h in v['holders'] if h['chg'] in ('new', 'added')]
        if signals_here:
            new_or_added.append(f"{v['name']}({tk}) {'/'.join(sorted(set(signals_here)))}")

    prompt = (
        "以下是根据多位价值投资人13F持仓筛选出的安全边际>=10%的股票列表分析素材。\n\n"
        "任务：写一段整体归纳，总结本期筛选结果中最值得关注的模式和信号（共识股信号是否一致、高仓位+主动加仓的强信号、新开仓仓位大小反映的信心强弱）。\n\n"
        "严格要求（必须遵守，否则作废）：\n"
        "1. 字数严格控制在 180 个中文字以内（不包含标点），超过部分会被直接截断且不会展示。宁可简短也不要超长。\n"
        "2. 最多只能提到 2-3 个具体股票代码作为例子，不要逐股列举。\n"
        "3. 不要使用 Markdown 语法（不要加粗、不要编号列表、不要用**号），只要普通段落文字。\n"
        "4. 只能基于下面提供的信息归纳，不要编造未提及的数据，不要给出买卖建议，语气客观分析。\n"
        "5. 直接输出归纳段落本身，不要加任何开头说明或标题。\n"
        "6. 若提供了“本轮跌出候选清单的股票”，可适当提及1只作为补充（说明它因安全边际不再达标而跌出），不必全部列举。\n\n"
        f"多人共识股（被2人以上持有）: {'; '.join(consensus_lines) if consensus_lines else '无'}\n"
        f"新开仓/加仓信号: {'; '.join(new_or_added) if new_or_added else '无'}\n"
        f"高仓位主动加仓/新开仓强信号: {'; '.join(strong_signals) if strong_signals else '无'}\n"
    )

    # 仅用三行信号数据本身计算哈希（不包括固定的提示词指令），
    # 这样 prompt 文字措辞小调不会触发不必要的重新生成，只有信号真正变化时才重调 LLM。
    signal_text = (
        f"consensus:{consensus_lines}|new_added:{new_or_added}|strong:{strong_signals}"
    )
    signal_hash = hashlib.sha256(signal_text.encode('utf-8')).hexdigest()

    return prompt, stock_notes, candidates, signal_hash


def _gen_homework_summary(api_key):
    """
    调用 _build_homework_prompt() 得到 prompt 、逐股数据与信号哈希，
    若信号哈希与上一次写入的相同（共识股/加仓/新开仓信号均无变化），
    就直接沿用旧的 overallSummary，跳过 LLM 调用（省钱且避免无意义重复生成）；
    否则调 LLM 重新生成整体归纳段落。写入 homework_summary.json。
    """
    prompt, stock_notes, candidates, signal_hash = _build_homework_prompt()
    if prompt is None:
        print("  无候选股，跳过 homework summary")
        return

    prev_hash, prev_overall, prev_notes = None, None, []
    if os.path.exists('homework_summary.json'):
        try:
            prev = json.load(open('homework_summary.json'))
            prev_hash = prev.get('signalHash')
            prev_overall = prev.get('overallSummary')
            prev_notes = prev.get('stockNotes', [])
        except Exception:
            pass

    # 优化①：检测跌出候选清单的股票（上一轮在、本轮不在），避免用户因“静默消失”而不知道原因
    cur_tickers = {n['ticker'] for n in stock_notes}
    prev_ticker_map = {n['ticker']: n for n in prev_notes}
    dropped_out = [prev_ticker_map[tk] for tk in prev_ticker_map if tk not in cur_tickers]
    dropped_desc = '; '.join(f"{d['name']}({d['ticker']}) 上一轮安全边际{d.get('mos','?')}%" for d in dropped_out[:5])

    if dropped_out:
        prompt += f"\n本轮跌出候选清单的股票（安全边际不再≥10%或无持有人）: {dropped_desc if dropped_desc else '无'}\n"

    if signal_hash is not None and signal_hash == prev_hash and prev_overall and not dropped_out:
        overall = prev_overall
        print("  homework summary 信号未变，复用上次 overallSummary，跳过 LLM 调用")
    else:
        overall = _sf_call_enrich(api_key, prompt, max_tokens=400)
        if not overall:
            print("  homework summary LLM 失败（整体归纳），仍写入逐股数据")
            overall = prev_overall or ""

    out = {
        'overallSummary': overall,
        'stockNotes': stock_notes,
        'droppedOut': [
            {'ticker': d['ticker'], 'name': d['name'], 'prevMos': d.get('mos')}
            for d in dropped_out
        ],
        'generatedAt': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'candidateCount': len(candidates),
        'consensusCount': sum(1 for v in candidates.values() if len(v['holders']) >= 2),
        'signalHash': signal_hash,
    }
    with open('homework_summary.json', 'w') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    print(f"  homework summary: {len(stock_notes)} 只逐股点评 + 整体归纳({len(overall)}字)")


# ── 格林布拉特分拆点评（规则驱动，不经 LLM，可复现、不编造）───────────────
# 依据 Joel Greenblatt 《股市天才》分拆筛选框架：
#   1. 机构不想要（小、被动基金无法持有）→ 用市值比例估算
#   2. 母公司规模越大，指数基金/机构强制抛售压力越大
#   3. 上市后股价被错杀（非基本面因素导致下跌）→ 潜在机会
#   4. 数据不足时降级为仅进度描述，不硬凑结论

def _greenblatt_market_cap_signal(market_cap, parent_market_cap):
    """市值比例信号：分拆标的/母公司。返回 (tier, ratio) 或 (None, None)。"""
    if not market_cap or not parent_market_cap or parent_market_cap <= 0:
        return None, None
    ratio = market_cap / parent_market_cap * 100
    if ratio < 10:
        return 'tiny', ratio
    elif ratio < 25:
        return 'small', ratio
    else:
        return 'sizable', ratio


def _greenblatt_parent_scale_signal(parent_market_cap):
    """母公司规模信号：越大越可能构成指数/被动基金强制抛售。"""
    if not parent_market_cap:
        return None
    if parent_market_cap >= 300:
        return 'large'
    elif parent_market_cap >= 50:
        return 'mid'
    else:
        return 'small'


def _gen_spinoff_verdict_hk(c):
    """
    港股分拆格林布拉特点评。输入为 spinoff.json 里单个 company dict。
    返回 (中文, 英文) 二元组。
    """
    status = c.get('_status', '')
    market_cap = c.get('marketCap')
    parent_mc = c.get('parentMarketCap')
    spin_perfs = c.get('spinoffPricePerf') or []
    spin_chg = spin_perfs[0].get('spinoffChangePct') if spin_perfs else None
    parent_perf = c.get('pricePerf') or {}
    parent_chg = parent_perf.get('changePct')

    tier, ratio = _greenblatt_market_cap_signal(market_cap, parent_mc)
    scale = _greenblatt_parent_scale_signal(parent_mc)

    # 档位1：已上市 + 有市值比例 + 有上市后走势 —— 信息最完整，可以给最具体的点评
    if tier and spin_chg is not None:
        if tier == 'tiny' and spin_chg < -10:
            return (
                f"分拆标的市值仅为母公司的{ratio:.1f}%，属于格林布拉特所说'机构大概率不会持有'的小盘股，"
                f"上市后已下跌{abs(spin_chg):.1f}%，跌幅可能主要来自机构被动抛售而非基本面恶化，值得进一步核实。",
                f"The spun-off unit is only {ratio:.1f}% of the parent's market cap — the kind of small, orphaned stock "
                f"institutions tend to dump per Greenblatt's framework. It has fallen {abs(spin_chg):.1f}% since listing, "
                f"which may reflect forced selling rather than deteriorating fundamentals — worth digging into."
            )
        if tier == 'tiny' and spin_chg >= -10:
            return (
                f"分拆标的市值仅为母公司的{ratio:.1f}%，符合'规模过小、机构懒得研究'的特征，"
                f"但上市后股价暂未出现明显错杀（{spin_chg:+.1f}%），机会窗口可能已被市场部分定价。",
                f"The spun-off unit is just {ratio:.1f}% of parent market cap — small enough that institutions typically "
                f"ignore it — but its post-listing move ({spin_chg:+.1f}%) hasn't shown the classic forced-selling dip yet."
            )
        if tier != 'tiny' and spin_chg < -15:
            return (
                f"分拆标的市值达母公司的{ratio:.1f}%，规模不算'小到没人要'，但上市后仍下跌{abs(spin_chg):.1f}%，"
                f"跌幅更可能与业务本身或情绪面有关，而非单纯的指数基金抛售，需要额外核实基本面。",
                f"At {ratio:.1f}% of parent market cap, this isn't the 'too small to bother with' profile Greenblatt "
                f"favors — yet it's down {abs(spin_chg):.1f}% since listing, more likely tied to fundamentals or sentiment "
                f"than pure index-fund selling; worth extra diligence."
            )
        return (
            f"分拆标的市值约为母公司的{ratio:.1f}%，机构强制抛售的特征不算典型，上市后表现为{spin_chg:+.1f}%，"
            f"暂未看到明显的格林布拉特式错杀信号。",
            f"At roughly {ratio:.1f}% of parent market cap, this doesn't strongly fit Greenblatt's 'unwanted small "
            f"spinoff' profile. Post-listing performance is {spin_chg:+.1f}%, with no clear sign of the classic "
            f"forced-selling mispricing yet."
        )

    # 档位2：没有市值比例，但有上市后走势
    if spin_chg is not None:
        if spin_chg < -15:
            return (
                f"分拆标的上市后已下跌{abs(spin_chg):.1f}%，跌幅明显，符合格林布拉特描述的'新股遭抛售'特征，"
                f"但因缺少分拆标的自身市值数据，暂无法判断是否为'机构懒得持有'的小盘股，建议人工核实规模。",
                f"Down {abs(spin_chg):.1f}% since listing — a meaningful drop consistent with Greenblatt's 'newly "
                f"listed spinoff gets dumped' pattern. Market-cap data for the spinoff itself isn't available yet, "
                f"so it's unclear if this is the classic small-cap orphan; worth checking size manually."
            )
        return (
            f"分拆标的上市后表现为{spin_chg:+.1f}%，暂未观察到格林布拉特式的错杀下跌，"
            f"母公司市值{f'约{parent_mc:.0f}亿美元' if parent_mc else '数据缺失'}，规模层面暂难判断机构抛售压力。",
            f"Post-listing move is {spin_chg:+.1f}%, without a clear Greenblatt-style mispricing dip so far. "
            f"Parent market cap is {f'about ${parent_mc:.0f}B' if parent_mc else 'unavailable'}, so institutional "
            f"selling pressure is hard to gauge from size alone."
        )

    # 档位3：尚未上市/进行中 —— 只能用母公司规模推测潜在担声压力，不给确定结论
    if status in ('proposed', 'approved', 'progress', 'announced'):
        if scale == 'large':
            return (
                f"母公司市值约{parent_mc:.0f}亿美元，规模较大，若分拆标的相对较小，未来上市后更可能出现"
                f"格林布拉特所说的指数基金/机构被动卖压，值得持续关注上市后的价格走势。",
                f"Parent market cap is around ${parent_mc:.0f}B — large enough that if the spinoff is meaningfully "
                f"smaller, it could see the index-fund/institutional forced-selling pattern Greenblatt describes once "
                f"listed. Worth tracking price action after the spinoff completes."
            )
        return (
            "分拆尚在进行中，暂无分拆标的市值和上市后价格数据，暂不构成可判断的格林布拉特信号，建议等待上市后再评估。",
            "The spinoff is still in progress — no market-cap or post-listing price data yet, so it's too early "
            "to apply Greenblatt's screening signals. Best to revisit once the listing completes."
        )

    return (
        "数据尚不足以判断是否符合格林布拉特分拆筛选特征，建议关注后续市值和价格数据。",
        "Not enough data yet to assess this against Greenblatt's spinoff criteria — worth watching for market-cap "
        "and price data as it becomes available."
    )


def _gen_spinoff_verdict_us(c):
    """
    美股分拆格林布拉特点评。输入为 spinoff_us.json 里单个 company dict。
    返回 (中文, 英文) 二元组。
    """
    status = c.get('status', '')
    market_cap = c.get('marketCap')
    parent_mc = c.get('parentMarketCap')
    spin_perf = c.get('spinoffPricePerf')
    spin_chg = None
    if isinstance(spin_perf, list) and spin_perf:
        spin_chg = spin_perf[0].get('spinoffChangePct') or spin_perf[0].get('changePct')
    elif isinstance(spin_perf, dict):
        spin_chg = spin_perf.get('changePct')

    tier, ratio = _greenblatt_market_cap_signal(market_cap, parent_mc)
    scale = _greenblatt_parent_scale_signal(parent_mc)

    if tier and spin_chg is not None:
        if tier == 'tiny' and spin_chg < -10:
            return (
                f"分拆标的市值仅为母公司的{ratio:.1f}%，是格林布拉特眼中典型的'机构不想要'的小盘股，"
                f"上市后已下跌{abs(spin_chg):.1f}%，符合'非基本面抛压导致的错杀'特征，值得深入研究基本面。",
                f"The spinoff is only {ratio:.1f}% of the parent's market cap — exactly the small, orphaned profile "
                f"institutions dump per Greenblatt. It's down {abs(spin_chg):.1f}% since listing, consistent with "
                f"non-fundamental forced selling — worth a closer look at the underlying business."
            )
        if tier == 'tiny':
            return (
                f"分拆标的市值仅为母公司的{ratio:.1f}%，规模符合'机构懒得持有'特征，"
                f"但上市后走势为{spin_chg:+.1f}%，尚未看到明显的错杀下跌。",
                f"At just {ratio:.1f}% of parent market cap, this fits the 'too small for institutions to bother "
                f"with' profile, though the post-listing move ({spin_chg:+.1f}%) hasn't shown a clear mispricing dip."
            )
        return (
            f"分拆标的市值约为母公司的{ratio:.1f}%，规模不算典型的'机构抛售'目标，上市后表现为{spin_chg:+.1f}%。",
            f"At roughly {ratio:.1f}% of parent market cap, this isn't the classic small-orphan target for "
            f"institutional dumping. Post-listing performance is {spin_chg:+.1f}%."
        )

    if spin_chg is not None:
        if spin_chg < -15:
            return (
                f"分拆标的上市后已下跌{abs(spin_chg):.1f}%，跌幅明显，符合格林布拉特描述的新股抛压模式，"
                f"但缺少市值比例数据，建议人工核实分拆标的相对母公司的规模。",
                f"Down {abs(spin_chg):.1f}% since listing — consistent with Greenblatt's newly-listed-spinoff-gets-"
                f"dumped pattern, though market-cap ratio data isn't available; worth checking relative size manually."
            )
        return (
            f"分拆标的上市后表现为{spin_chg:+.1f}%，暂未观察到明显的错杀信号。",
            f"Post-listing move is {spin_chg:+.1f}%, without a clear sign of Greenblatt-style mispricing so far."
        )

    if status in ('in_progress', 'announced'):
        if scale == 'large':
            return (
                f"母公司市值约{parent_mc:.0f}亿美元，规模较大，是标普型指数成分股分拆时常见的"
                f"'机构强制卖压'候选，建议关注分拆完成、独立上市后的股价表现。",
                f"Parent market cap is around ${parent_mc:.0f}B — the kind of larger, index-eligible parent where "
                f"Greenblatt's institutional forced-selling dynamic often plays out post-spinoff. Worth watching "
                f"price action once the spinoff lists independently."
            )
        return (
            "分拆尚在进行中，暂无独立市值和上市后价格数据，暂不构成可判断的格林布拉特信号。",
            "The spinoff is still in progress — no independent market-cap or post-listing price data yet, so it's "
            "too early to apply Greenblatt's screening signals."
        )

    return (
        "数据尚不足以判断是否符合格林布拉特分拆筛选特征，建议关注后续市值和价格数据。",
        "Not enough data yet to assess this against Greenblatt's spinoff criteria — worth watching for market-cap "
        "and price data as it becomes available."
    )


def _gen_spinoff_verdicts():
    """
    为 spinoff.json（港股）和 spinoff_us.json（美股）的每个公司生成格林布拉特风格的中英双语点评，
    写入 c['greenblattNote'] = {'zh': ..., 'en': ...}。规则驱动，不经 LLM。
    """
    # 港股
    if os.path.exists('spinoff.json'):
        with open('spinoff.json', encoding='utf-8') as f:
            hk_data = json.load(f)
        for c in hk_data.get('companies', []):
            zh, en = _gen_spinoff_verdict_hk(c)
            c['greenblattNote'] = {'zh': zh, 'en': en}
        with open('spinoff.json', 'w', encoding='utf-8') as f:
            json.dump(hk_data, f, ensure_ascii=False, indent=2)
        print(f"  港股分拆：为 {len(hk_data.get('companies', []))} 家公司生成格林布拉特点评")

    # 美股
    if os.path.exists('spinoff_us.json'):
        with open('spinoff_us.json', encoding='utf-8') as f:
            us_data = json.load(f)
        for c in us_data.get('companies', []):
            zh, en = _gen_spinoff_verdict_us(c)
            c['greenblattNote'] = {'zh': zh, 'en': en}
        with open('spinoff_us.json', 'w', encoding='utf-8') as f:
            json.dump(us_data, f, ensure_ascii=False, indent=2)
        print(f"  美股分拆：为 {len(us_data.get('companies', []))} 家公司生成格林布拉特点评")


def main():
    print("=== enrich_metadata.py 开始 ===")
    cache = load_cache()
    print(f"缓存已有 {len(cache)} 个 ticker")

    investors = load_investors()
    data_files = []
    for inv in investors:
        data_files.append(inv['dataFile'])
        # webb 的 hkFile 就是主数据文件（webb.json 已在 dataFile 里处理过），
        # 避免对其他投资者重复添加同一个 hkFile
        if inv.get('hkFile') and inv['hkFile'] != inv['dataFile'] and inv['hkFile'] not in data_files:
            data_files.append(inv['hkFile'])
    if not investors:
        # investors.json 缺失时的安全兼底，避免 metadata 完全跳过
        data_files = [
            'data.json', 'pabrai_data.json', 'duan.json', 'tepper.json',
            'akre.json', 'greenberg.json', 'buffett.json', 'webb.json',
            'klarman.json', 'ackman.json', 'abrams.json', 'berkowitz.json', 'hawkins.json',
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

    # 注意：_gen_spinoff_verdicts() 不在这里调用。
    # 它依赖 spinoff.json/spinoff_us.json 里的 marketCap 和 spinoffPricePerf 字段，
    # 而这些字段由 fetch_spinoff.py / fetch_spinoff_us.py / spinoff_price_refresh.py 在
    # CI 中比 enrich_metadata.py 更晚执行才会写入（见 .github/workflows/update.yml 步骤顺序）。
    # 在这里调用会读到还未刷新的旧数据，而且随后的分拆抓取步骤会重新写整个 JSON，
    # 把这里写入的 greenblattNote 覆盖掉。改为在 spinoff_price_refresh.py 之后单独调用。

if __name__ == '__main__':
    main()
