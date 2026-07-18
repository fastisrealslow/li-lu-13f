#!/usr/bin/env python3
"""
LLM ticker 推断测试脚本 - 01171.HK 兗礦能源
用于验证 SiliconFlow LLM 能否从公告标题推断出子公司 ticker
"""
import os, sys, json, re, warnings
import yfinance as yf, requests, pandas as pd
from rapidfuzz import fuzz, process as rfprocess
warnings.filterwarnings('ignore')

api_key = os.environ.get('SILICONFLOW_KEY', '')
if not api_key:
    print("❌ No SILICONFLOW_KEY"); sys.exit(1)

# ── 01171.HK 的公告标题 ───────────────────────────────────────────
parent_ticker = "01171.HK"
parent_name   = "兗礦能源"
titles = [
    "建議分拆物泊科技於香港聯合交易所有限公司主板上市之進展公告",
    "內幕消息 建議分拆物泊科技於香港聯合交易所有限公司主板上市",
    "建議分拆卡松科技於全國中小企業股份轉讓系統掛牌之進展",
    "內幕消息 建議分拆卡松科技於全國中小企業股份轉讓系統掛牌",
]

print(f"Testing: {parent_ticker} {parent_name}")
print("Titles:")
for t in titles: print(f"  - {t}")

# ── Prompt ────────────────────────────────────────────────────────
titles_text = '\n'.join(f'- {t}' for t in titles[:8])
prompt = (
    "你是港股分拆研究员。「" + parent_name + "」（" + parent_ticker + "）有两个分拆计划：\n\n"
    + titles_text + "\n\n"
    "请分别推断两个子公司的信息：\n"
    "1. 物泊科技 → 建议在香港联交所主板上市\n"
    "2. 卡松科技 → 建议在全国中小企业股份转让系统（新三板）挂牌\n\n"
    "注意：公告是\"进展公告\"，可能尚未正式上市。如果尚未上市或不确定ticker，confidence填0-30。\n"
    "港股格式：4-5位数字.HK；新三板：6位纯数字（如830XXX）。\n\n"
    '只返回JSON数组，不加其他文字：\n'
    '[{"company":"物泊科技","ticker":"港股ticker或空","confidence":0-100,"listed":true/false,"reasoning":""},'
    '{"company":"卡松科技","ticker":"新三板代码或空","confidence":0-100,"listed":true/false,"reasoning":""}]'
)

print("\n--- Calling SiliconFlow Qwen3-8B ---")
resp = requests.post(
    'https://api.siliconflow.cn/v1/chat/completions',
    headers={'Authorization': f'Bearer {api_key}', 'Content-Type': 'application/json'},
    json={'model': 'Qwen/Qwen3-8B',
          'messages': [{'role': 'user', 'content': prompt}],
          'temperature': 0.1, 'max_tokens': 500, 'enable_thinking': False},
    timeout=30
)
print(f"HTTP: {resp.status_code}")
raw = resp.json()['choices'][0]['message']['content'].strip()
print(f"\nLLM Response:\n{raw}\n")

# ── Parse ─────────────────────────────────────────────────────────
m = re.search(r'\[[\s\S]+?\]', raw)
if not m:
    print("❌ No JSON array found"); sys.exit(1)

results = json.loads(m.group())
print(f"Parsed: {json.dumps(results, ensure_ascii=False, indent=2)}")

# ── yfinance verify ────────────────────────────────────────────────
print("\n--- yfinance verification ---")
for r in results:
    tk = r.get('ticker', '').strip()
    if not tk:
        print(f"  {r.get('company')}: no ticker (confidence={r.get('confidence')})")
        continue
    if tk.upper().endswith('.HK'):
        tk = tk[:-3].lstrip('0') + '.HK'
    try:
        df = yf.download(tk, period='5d', auto_adjust=True, progress=False)
        if not df.empty:
            c = df['Close']
            if isinstance(c, pd.DataFrame): c = c.iloc[:, 0]
            v = c.dropna()
            price = round(float(v.iloc[-1]), 3) if not v.empty else None
            print(f"  ✅ {r.get('company')} → {tk} price={price}")
        else:
            print(f"  ❌ {r.get('company')} → {tk} not found on yfinance (not listed yet?)")
    except Exception as e:
        print(f"  ❌ {r.get('company')} → {tk} error: {e}")

print("\nDone.")
