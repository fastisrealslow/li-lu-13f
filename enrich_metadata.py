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

from holdings_diff import compare_holdings

from update_status import record_ai_warning

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
    "ELV": "Elevance Health（原 Anthem）",
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


def _is_chinese(s):
    """判断字符串是否包含中文字符（用于识别 cnName 里 yfinance 英文
    fallback 未被真正翻译成中文的情况）。"""
    return bool(re.search(r'[\u4e00-\u9fff]', s or ''))

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

        reviewed=cache.get(tk,{})
        if reviewed.get('labelSourceURL') and reviewed.get('cnName') and h.get('cnName')!=reviewed['cnName']:
            h['cnName']=reviewed['cnName'];changed_tickers.add(tk)
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
        with open(filepath, encoding="utf-8") as f:
            d = json.load(f)
    except Exception as e:
        print(f"  ⚠️  {filepath} load error: {e}")
        return

    changed = set()

    # current holdings
    cur = d.get('current', {}).get('holdings', [])
    if cur:
        enrich_holdings(cur, cache, changed)

    enrich_holdings(d.get('current', {}).get('previousHoldings', []), cache, changed)

    # Historical security labels must not inherit the name of a different
    # issuer that later reused the same ticker. Never request delisted-company
    # metadata once per old row: reuse only a matching current CUSIP.
    live_ids={(h.get('ticker'),h.get('cusip')) for h in cur+d.get('current',{}).get('previousHoldings',[]) if h.get('cusip')}
    # history holdings
    hist = d.get('history', {})
    # 支持两种结构：{quarter: [holdings]} 或 {holdings: {quarter: [holdings]}}
    hist_qs = hist.get('holdings', hist) if isinstance(hist, dict) else {}
    if isinstance(hist_qs, dict):
        for q, hs in hist_qs.items():
            if isinstance(hs, list):
                for h in hs:
                    if (h.get('ticker'),h.get('cusip')) in live_ids:
                        enrich_holdings([h],cache,changed)
                    elif not h.get('sector'):
                        h['sector']='其他';changed.add(h.get('ticker',''))

    if changed:
        with open(filepath, 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=None if sum(len(v) for v in d.get('history',{}).get('holdings',{}).values())>20000 else 2, separators=(',',':') if sum(len(v) for v in d.get('history',{}).get('holdings',{}).values())>20000 else None)
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


_SF_UNAVAILABLE = False
_SF_REJECTED_MODELS = set()


def _sf_call_enrich(api_key, prompt, max_tokens=400, retries=2):
    """健壮 SiliconFlow 调用：multi-model fallback + 重试"""
    try:
        from urllib.request import Request, urlopen
    except ImportError:
        return None
    global _SF_UNAVAILABLE
    if not api_key or _SF_UNAVAILABLE:
        return None
    for model in _SF_MODELS_EN:
        if model in _SF_REJECTED_MODELS:
            continue
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
                code = getattr(e, 'code', None)
                if code in (401, 402):
                    _SF_UNAVAILABLE = True
                    record_ai_warning('metadata', code)
                    print(f"::warning::AI enrichment unavailable (HTTP {code}); "
                          "skipping further model requests in this process and keeping existing text.")
                    return None
                if code in (403, 404):
                    _SF_REJECTED_MODELS.add(model)
                    print(f"::warning::AI model {model} unavailable (HTTP {code}); trying next model.")
                    break
                wait = 2 ** attempt
                print(f"  [{model}] 第{attempt+1}次失败: {e}"
                      + (f"，{wait}s后重试" if attempt < retries else "，放弃"))
                if attempt < retries:
                    time.sleep(wait)
        print(f"  模型 {model} 全部失败")
    record_ai_warning('metadata')
    return None


def translate_names_to_chinese(names, api_key, batch_size=20):
    """批量把英文公司全名翻译成简体中文常用名（用于修复 cnName 字段里
    yfinance longName 英文 fallback 未被真正翻译的问题）。

    返回 {english_name: chinese_name}，翻译失败或 LLM 返回格式不对的
    条目不会出现在返回结果里（调用方应保留原英文名，不强行瞎填）。
    """
    if not api_key or not names:
        return {}

    result = {}
    names = list(dict.fromkeys(names))  # 去重，保持顺序
    for i in range(0, len(names), batch_size):
        batch = names[i:i + batch_size]
        numbered = "\n".join(f"{j+1}. {n}" for j, n in enumerate(batch))
        prompt = (
            "你是金融翻译专家。把下面这些美股/港股上市公司的英文全名，"
            "翻译成中国大陆投资者最熟悉的简体中文常用简称（不是逐字直译，"
            "要用业内通用叫法，例如 'Starbucks Corporation' 应译为 '星巴克'，"
            "'Marriott International, Inc.' 应译为 '万豪国际'）。\n"
            "严格按 JSON 对象格式返回，key 必须是下面列出的编号字符串（不是公司名），"
            "value 是对应的中文翻译，必须包含全部 " + str(len(batch)) + " 个编号，"
            "不要输出任何其他文字、注释或代码块标记，例如："
            "{\"1\": \"星巴克\", \"2\": \"万豪国际\"}\n\n"
            f"{numbered}"
        )
        text = _sf_call_enrich(api_key, prompt, max_tokens=800)
        if not text:
            print(f"  翻译批次 {i} 失败（LLM 无响应），跳过本批")
            continue
        # 去掉可能的 markdown 代码块包裹
        cleaned = re.sub(r'^```(?:json)?\s*|\s*```$', '', text.strip())
        try:
            translated = json.loads(cleaned)
        except json.JSONDecodeError:
            print(f"  翻译批次 {i} JSON 解析失败，原文: {text[:200]}")
            continue
        if not isinstance(translated, dict):
            print(f"  翻译批次 {i} 返回不是 JSON 对象，跳过本批")
            continue
        # 按编号回填，而不是按数组位置 zip —— 即使 LLM 漏答/多答部分编号，
        # 已经答对的编号也不会因为位置错位而被错误地归属到另一个公司名。
        matched = 0
        for j, en in enumerate(batch):
            cn = (translated.get(str(j + 1), "") or "").strip()
            if cn and _is_chinese(cn):
                result[en] = cn
                matched += 1
            elif cn:
                print(f"  跳过可疑翻译结果: \"{en}\" -> \"{cn}\"")
        if matched < len(batch):
            print(f"  翻译批次 {i}：{len(batch)} 个中 {matched} 个成功匹配编号，其余保持未翻译（不猴填）")
        print(f"  翻译批次 {min(i + batch_size, len(names))}/{len(names)} 完成")
        time.sleep(1)
    return result


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
        instrument_tickers = {h['ticker'] for h in cur.get('holdings', []) + cur.get('previousHoldings', []) if h.get('putCall') or h.get('shareType', 'SH') != 'SH'}
        holdings = [h for h in cur.get('holdings', []) if h.get('ticker') not in instrument_tickers]
        if isinstance(cur.get('previousHoldings'), list):
            holdings = compare_holdings(holdings, cur['previousHoldings'])
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
        d['meta']['aiSummaryUpdatedAt'] = datetime.now(timezone.utc).isoformat()
        with open(filepath, 'w') as f:
            json.dump(d, f, ensure_ascii=False, indent=None if sum(len(v) for v in d.get('history',{}).get('holdings',{}).values())>20000 else 2, separators=(',',':') if sum(len(v) for v in d.get('history',{}).get('holdings',{}).values())>20000 else None)
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
    from holdings_diff import consolidate_holdings
    hist=dr.get('history',{});latest=dr.get('current',{}).get('quarter','')
    series=[]
    for q in hist.get('quarters',[]):
        if q not in hist.get('holdings',{}):continue
        if tk in dr.get('meta',{}).get('instrumentHistoryTickers',[]) and q<dr['meta']['instrumentHistoryFrom']:continue
        shares=0
        for h in consolidate_holdings(hist['holdings'][q]):
            if h['ticker']!=tk or h.get('putCall') or h.get('shareType','SH')!='SH':continue
            factor=1
            for action in dr.get('meta',{}).get('shareActions',[]):
                if (h.get('cusip')==action.get('cusip') or tk==action['ticker']) and q<action['quarter']<=latest:factor*=action['factor']
            shares+=h['shares']*factor
        series.append((q,shares))
    return sorted(series,key=lambda item:_q2n(item[0]))


def _analyze_holding_pattern(series):
    result={'trend':'stable','reentry':False,'exit_quarter':None,'reentry_quarter':None}
    last_positive=None;zero_seen=False;run=[]
    for q,shares in series:
        if shares<=0:
            if last_positive:zero_seen=True
            run=[];continue
        if zero_seen:
            result.update(reentry=True,exit_quarter=last_positive,reentry_quarter=q)
            zero_seen=False
        if run and _q2n(q)-_q2n(run[-1][0])!=1:run=[]
        run.append((q,shares));last_positive=q
    if len(run)>=3:
        a,b,c=[row[1] for row in run[-3:]]
        if a<b<c:result['trend']='accumulating'
        elif a>b>c:result['trend']='reducing'
    return result


def _mos_tier(mos):
    if mos >= 30:
        return "深度折价"
    if mos >= 15:
        return "中等折价"
    return "轻度折价"


_CHG_LABEL = {'new': '本季新开仓', 'added': '本季加仓', 'trimmed': '本季减仓', 'hold': '仓位未变'}

# 持有人中文名 -> 英文名映射：从 investors.json 动态生成（单一权威来源），
# 不再手工硬编码列表 —— 之前的硬编码只覆盖7人且部分本身就是错的占位英文名
# （如 'Tepper'->'Tepper'，本该是 'David Tepper'），新增投资者时会自动漏掉。
def _investor_en(name_cn):
    if not hasattr(_investor_en, '_map'):
        _investor_en._map = {inv['name']: inv['nameEn'] for inv in load_investors()}
    return _investor_en._map.get(name_cn, name_cn)


def _gen_verdict(v, mos_tier):
    """Describe screened evidence without inventing conviction or trade motives."""
    holders=v['holders']
    n=len(holders)
    weight=max((h.get('weight',0) for h in holders if isinstance(h.get('weight'),(int,float)) and 0<=h['weight']<=100),default=0)
    adding=any(h['chg'] in ('new','added') for h in holders)
    reducing=any(h['chg']=='trimmed' for h in holders)
    if n>=2 and adding and reducing:
        zh='多位持有者同时满足筛选，但有人增加股数、有人减少股数。先分别核对报告季度和变化，不能合并成一致买入。'
        en='Multiple holders pass the screen, with opposing share-count directions. Check their report quarters separately; this is not a unanimous purchase.'
    elif n>=2 and all(h['chg'] in ('new','added') for h in holders):
        zh='符合筛选的多位持有者都出现新建仓或增持。这是披露方向一致，仍需核对成本估算与企业经营，不能据此认定买入价格或未来回报。'
        en='All qualifying holders show an entry or addition. This is agreement in disclosures, not proof of entry prices or future returns; cost estimates and business results need separate review.'
    elif n>=2 and all(h['chg']=='trimmed' for h in holders):
        zh='符合筛选的多位持有者均减少了股数。价格低于估算成本与减仓同时存在，不能只看折价而忽略这项变化。'
        en='All qualifying holders reduced their shares. A price below estimated cost coexists with reductions; the discount should not hide the change.'
    elif n==1 and holders[0]['chg']=='new':
        zh=f'新进入可比季度披露，当前占该投资人申报组合 {weight:g}%。这个比例描述本期结构，不证明实际买入成本，也不证明试探或强烈信心。'
        en=f'New in the comparable quarterly disclosure, at {weight:g}% of that investor’s reported value. This describes the current structure, not actual entry cost or a level of conviction.'
    elif n==1 and holders[0]['chg']=='added':
        zh=f'当前占该投资人申报组合 {weight:g}%，本季披露股数增加。需要区分股数增加、股价变化和成本估算，不能把权重直接当成增持幅度。'
        en=f'Currently {weight:g}% of that investor’s reported value, with more disclosed shares this quarter. Weight is not the addition percentage; prices and estimated cost have separate meanings.'
    elif n==1 and holders[0]['chg']=='trimmed':
        zh='当前价格通过成本差筛选，但本季披露股数减少。两项事实都要保留，不能仅凭减持推断基本面担忧或价值陷阱。'
        en='The price passes the estimated-cost-gap screen, while reported shares fell this quarter. Both facts matter; the reduction alone does not establish fundamental concerns or a value trap.'
    elif n==1:
        h=holders[0]
        if h.get('hold_quarters'):
            zh=f'成本参考记录起点距本期 {h["hold_quarters"]} 个季度，本季股数未变。时间跨度不证明连续持仓，也不是新的买入信号。'
            en=f'The cost-reference record spans {h["hold_quarters"]} quarters to this filing, with unchanged shares this quarter. Elapsed time does not prove continuous holdings or a new purchase.'
        else:
            zh='只有一位持有者满足本轮筛选，本季未记录新增股数。先核对成本估算与企业价值，而不是从持有状态推断后续动作。'
            en='One holder qualifies in this screen, with no added shares recorded this quarter. Examine estimated cost and business value without inferring the next trade.'
    else:
        zh=f'{n} 位持有者符合筛选，股数变化并非全部一致。分别研究报告期、持仓占比与企业经营。'
        en=f'{n} holders pass the screen without a uniform share-count direction. Examine their periods, portfolio weights and business results separately.'
    if n==1:
        investor=next((i for i in load_investors() if i['name']==holders[0]['investor']),None)
        signature=investor.get('profile',{}).get('signature') if investor else None
        if signature:
            zh+=' 研究视角：'+signature['title'][0]+'。'
            en+=' Research perspective: '+signature['title'][1]+'.'
    return zh,en


def _build_value_screen():
    """One price per security, source-bound references, and transparent ranking."""
    from quote_coverage import valid_quote
    from reporting_scope import same_manager_history
    people=[i for i in load_investors() if i.get('inValueScreen')]
    sources=[];best_quotes={};all_holders={};nearby={}
    for inv in people:
        try:
            dr=json.load(open(inv['dataFile']));pr=json.load(open(inv['pricesFile']))
        except (OSError,ValueError):continue
        sources.append((inv,dr,pr))
        for tk,q in pr.get('quotes',{}).items():
            if valid_quote(q) and not q.get('stale') and time.time()-q['t']<=7*86400 and q.get('currency','USD')=='USD':
                if q['t']>best_quotes.get(tk,{}).get('t',0):best_quotes[tk]=q
    for inv,dr,pr in sources:
        cur=dr.get('current',{});total=cur.get('totalValue',0);merged={}
        for h in cur.get('holdings',[]):
            tk=h.get('ticker','')
            if h.get('putCall') or h.get('shareType','SH')!='SH' or re.search(r'\bWARRANT\b',h.get('cls',''),re.I) or not tk or tk.startswith('?') or tk.endswith('.HK'):continue
            if tk not in merged:merged[tk]={**h}
            else:
                row=merged[tk];row['shares']+=h.get('shares',0);row['value']+=h.get('value',0)
                row['prevShares']=row['prevShares']+h['prevShares'] if row.get('prevShares') is not None and h.get('prevShares') is not None else None
        for tk,h in merged.items():
            prev=h.get('prevShares');shares=h['shares'];transition=dr.get('meta',{}).get('reportingTransition',{})
            scope=transition.get('fromQuarter')==cur.get('quarter') and transition.get('comparisonScopeChanged') and not same_manager_history(dr,h)
            comparable=prev is not None and not scope
            chg=('new' if prev==0 else 'added' if shares>prev else 'trimmed' if shares<prev else 'hold') if comparable else 'unknown'
            cost=pr.get('costBasis',{}).get(tk,{}) if not cur.get('valueQuality') else {};rc=cost.get('recent') or {};buy=rc.get('buy');q=best_quotes.get(tk,{})
            buy=buy if isinstance(buy,(int,float)) and buy>0 else None
            mos=(buy-q['c'])/buy*100 if buy and q else None
            entry={'id':inv['id'],'name':inv['name'],'nameEn':inv['nameEn'],'weight':round(h['value']/total*100,2) if total and not cur.get('valueQuality') else None,'chg':chg,'reportQuarter':cur.get('quarter'),'shares':shares,'previousShares':prev if comparable else None,'shareChangePct':round((shares-prev)/prev*100,3) if comparable and prev else None,'buy':round(buy,2) if buy else None,'buyQuarter':rc.get('quarter'),'referenceKind':rc.get('kind','buying_reference'),'referenceSource':rc.get('source'),'atAvg':(cost.get('allTime') or {}).get('avg'),'costFirst':(cost.get('allTime') or {}).get('first'),'costLast':(cost.get('allTime') or {}).get('last'),'buyQuarters':(cost.get('allTime') or {}).get('buy_quarters'),'sourceFiling':cur.get('sourceFiling'),'mos':round(mos,1) if mos is not None else None,'qualifies':mos is not None and mos>=10}
            all_holders.setdefault(tk,[]).append((entry,h))
            if not entry['qualifies']:
                nearby.setdefault(tk,[]).append({'investor':inv['name'],'investorEn':inv['nameEn'],**entry})
    candidates=[]
    for tk,holders in all_holders.items():
        qualified=[e for e,h in holders if e['qualifies']]
        if not qualified:continue
        reference=min(qualified,key=lambda e:e['buy']);h=next(h for e,h in holders if e['id']==reference['id']);q=best_quotes[tk]
        candidates.append({'ticker':tk,'name':h['name'],'cnName':h.get('cnName') or h['name'],'sector':h.get('sector',''),'currency':'USD','mos':round((reference['buy']-q['c'])/reference['buy']*100,1),'price':round(q['c'],2),'priceAsOf':datetime.fromtimestamp(q['t'],timezone.utc).isoformat(),'priceSource':q.get('sourceURL'),'buy':reference['buy'],'atAvg':reference['atAvg'],'referenceInvestorId':reference['id'],'referenceInvestor':reference['name'],'referenceInvestorEn':reference['nameEn'],'referenceQuarter':reference['buyQuarter'],'referenceSource':reference['referenceSource'],'referenceKind':reference['referenceKind'],'investors':qualified,'otherHolders':[e for e,h in holders if not e['qualifies']],'totalHolders':len(holders)})
    # Qualifying holders first, then the gap to their lowest reference.
    candidates.sort(key=lambda c:(-len(c['investors']),-c['mos'],c['ticker']))
    return {'generatedAt':datetime.now(timezone.utc).isoformat(),'schemaVersion':2,'ranking':'qualifying_holders_then_cost_gap','candidates':candidates,'nearMissMap':nearby}


def _build_homework_prompt():
    """Generate notes from exactly the candidates and source prices on screen."""
    screen=_build_value_screen();candidates={};notes=[]
    for c in screen['candidates']:
        holders=[{'investor':h['name'],'investorEn':h['nameEn'],'chg':h['chg'],'weight':h['weight'] or 0,'reportQuarter':h['reportQuarter'],'buy':h['buy'],'buyQuarter':h['buyQuarter'],'shareChangePct':h['shareChangePct'],'hold_quarters':0,'hold_years':0} for h in c['investors']]
        v={**c,'holders':holders};candidates[c['ticker']]=v
        adding=sum(h['chg'] in ('new','added') for h in holders);reducing=sum(h['chg']=='trimmed' for h in holders)
        verdict=f"达标持有人中，{adding} 位新增或增持，{reducing} 位减持。最低参考来自{c['referenceInvestor']}，对应 {c.get('referenceQuarter') or '未注明季度'}。"
        verdict_en=f"Among qualifying holders, {adding} show entries or additions and {reducing} reductions. The lowest reference is from {c['referenceInvestorEn']}, for {c.get('referenceQuarter') or 'an undated quarter'}."
        notes.append({'ticker':c['ticker'],'name':c['cnName'],'sector':c['sector'],'mos':c['mos'],'mosTier':_mos_tier(c['mos']),'buy':c['buy'],'price':c['price'],'holders':holders,'holderCount':len(holders),'holderText':'；'.join(h['investor']+' '+h['reportQuarter'] for h in holders),'nearMiss':screen['nearMissMap'].get(c['ticker'],[]),'verdict':verdict,'verdictEn':verdict_en})
    material=[{'ticker':c['ticker'],'gap':c['mos'],'referenceInvestor':c['referenceInvestor'],'referenceQuarter':c['referenceQuarter'],'holders':c['investors']} for c in screen['candidates']]
    signal_hash=hashlib.sha256(json.dumps(material,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
    prompt='概括下面候选的实际数字和增减方向，指出分歧，不推断交易动机或未来收益。参考价是历史价格估算，不是企业估值。只使用提供的事实。\n'+json.dumps(material,ensure_ascii=False)
    return prompt,notes,candidates,signal_hash


def _write_value_screen():
    """计算并写入 value_screen.json（不依赖 LLM key，纯代码计算，任何环境均可跑）。"""
    try:
        data = _build_value_screen()
    except Exception as e:
        print(f"WARNING: 价值筛选预计算失败（{e}），跳过 value_screen.json", file=sys.stderr)
        return
    with open('value_screen.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  已写入 value_screen.json：{len(data['candidates'])} 只候选股")


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
            overall = prev_overall if signal_hash == prev_hash else ""

    from ai_supplement import value_source
    out = {
        'valueSource': value_source(_build_value_screen()),
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
    """Factual research prompts; price/size alone cannot establish forced selling."""
    zh, en = [], []
    parent = c.get('parentMarketCap')
    if isinstance(parent, (int, float)) and parent > 0:
        zh.append(f"母公司参考市值约 {parent:.1f} 亿美元（快照，非实时）。")
        en.append(f"Parent reference market cap: ${parent / 10:.2f}B (snapshot, not live).")
    zh.append("待验证：分派比例、子公司债务与现金流、管理层持股及机构持仓变化。市值与股价变化不能单独证明强制卖压或低估。")
    en.append("Research checklist: distribution ratio, child debt and cash flow, management ownership, and institutional holdings. Size and price changes alone do not establish forced selling or undervaluation.")
    return ' '.join(zh), ' '.join(en)


def _gen_spinoff_verdict_us(c):
    return _gen_spinoff_verdict_hk(c)


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
    from listing_metadata import seed
    active={h['ticker'] for inv in load_investors() if os.path.exists(inv['dataFile']) for h in json.load(open(inv['dataFile'])).get('current',{}).get('holdings',[])}
    seed(cache,tickers=active)
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

    # 修复 cnName 里 yfinance 英文 fallback 未被真正翻译成中文的问题：
    # 扫描 cache 里所有 cnName 不含中文字符的条目，批量翻译后回写 cache
    # 和所有数据文件（全自动，不依赖手工白名单）。没有 key 时跳过，
    # 不会报错也不会用英文假装成中文。
    if sf_key:
        print("\n=== LLM 批量翻译残留英文 cnName ===")
        english_names = sorted({
            v.get('cnName', '') for v in cache.values()
            if v.get('cnName') and not _is_chinese(v.get('cnName', ''))
        })
        print(f"待翻译英文名（去重）: {len(english_names)} 个")
        if english_names:
            translations = translate_names_to_chinese(english_names, sf_key)
            print(f"成功翻译: {len(translations)}/{len(english_names)}")
            if translations:
                # 回写 cache：每个 ticker 的 cnName 如果命中翻译表就替换
                cache_updated = 0
                for tk, v in cache.items():
                    cn = v.get('cnName', '')
                    if cn in translations:
                        v['cnName'] = translations[cn]
                        cache_updated += 1
                if cache_updated:
                    save_cache(cache)
                    print(f"cache 已更新 {cache_updated} 个 ticker 的 cnName")

                # 回写所有数据文件里已落盘的旧英文 cnName
                files_updated = 0
                records_updated = 0
                for f in data_files:
                    if not os.path.exists(f):
                        continue
                    d = json.load(open(f))
                    changed = False

                    def fix_holdings(holdings):
                        nonlocal changed, records_updated
                        for h in holdings:
                            cn = h.get('cnName', '')
                            if cn in translations:
                                h['cnName'] = translations[cn]
                                changed = True
                                records_updated += 1

                    fix_holdings(d.get('current', {}).get('holdings', []))
                    fix_holdings(d.get('current', {}).get('previousHoldings', []))
                    hist = d.get('history', {})
                    hist_qs = hist.get('holdings', hist) if isinstance(hist, dict) else {}
                    if isinstance(hist_qs, dict):
                        for q, hs in hist_qs.items():
                            if isinstance(hs, list):
                                fix_holdings(hs)

                    if changed:
                        with open(f, 'w') as fp:
                            json.dump(d, fp, ensure_ascii=False, indent=None if sum(len(v) for v in d.get('history',{}).get('holdings',{}).values())>20000 else 2)
                        files_updated += 1
                print(f"已回写 {files_updated} 个文件，{records_updated} 条记录的 cnName 被翻译回写")

    print("\n=== 预计算价值筛选表格数据 ===")
    _write_value_screen()

    if sf_key:
        print("\n=== LLM 生成 13F 季报摘要 ===")
        _gen_13f_summaries(sf_key)

        print("\n=== LLM 生成价值筛选总结 ===")
        _gen_homework_summary(sf_key)
    else:
        _gen_homework_summary('')

    # 注意：_gen_spinoff_verdicts() 不在这里调用。
    # 它依赖 spinoff.json/spinoff_us.json 里的 marketCap 和 spinoffPricePerf 字段，
    # 而这些字段由 fetch_spinoff.py / fetch_spinoff_us.py / spinoff_price_refresh.py 在
    # CI 中比 enrich_metadata.py 更晚执行才会写入（见 .github/workflows/update.yml 步骤顺序）。
    # 在这里调用会读到还未刷新的旧数据，而且随后的分拆抓取步骤会重新写整个 JSON，
    # 把这里写入的 greenblattNote 覆盖掉。改为在 spinoff_price_refresh.py 之后单独调用。

if __name__ == '__main__':
    main()
