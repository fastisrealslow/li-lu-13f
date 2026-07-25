#!/usr/bin/env python3
"""
独立测试脚本：复用 enrich_metadata._build_homework_prompt() 生成的真实 prompt，
并行调用多个 SiliconFlow 候选模型，对比输出质量（准确性、是否编造、字数是否符合要求）。
不修改生产逻辑，不覆盖真实 homework_summary.json，仅用于人工评估选型。
用法：SILICONFLOW_KEY 由 CI workflow 注入环境变量。
"""
import json
import os
import sys
import urllib.request

sys.path.insert(0, '.')
import enrich_metadata as em

# 候选模型：免费优先 + 低价 + 一个中端对比基准（用于判断免费模型是否有明显质量差距）
CANDIDATE_MODELS = [
    ("Qwen/Qwen3.5-4B", "免费"),
    ("Qwen/Qwen3-8B", "免费"),
    ("THUDM/GLM-4-9B-0414", "免费"),
    ("Qwen/Qwen2.5-7B-Instruct", "免费"),
    ("Qwen/Qwen3.5-9B", "低价(约¥0.1/¥0.15每M token)"),
    ("zai-org/GLM-4.5-Air", "低价(¥0.14/¥0.86每M token)"),
    ("deepseek-ai/DeepSeek-V3.2", "中端对比基准(¥0.27/¥0.42每M token)"),
]


def call_model(api_key, model, prompt, max_tokens=400):
    payload = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": max_tokens,
        "temperature": 0.3,
        "stream": False,
        "enable_thinking": False,
    }).encode()
    req = urllib.request.Request(
        "https://api.siliconflow.cn/v1/chat/completions",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode())
            return data["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"[ERROR] {e}"


def main():
    api_key = os.environ.get('SILICONFLOW_KEY', '')
    if not api_key:
        print("ERROR: 未找到 SILICONFLOW_KEY 环境变量")
        sys.exit(1)

    # 直接复用生产聚合逻辑，保证测试用的 prompt 与真实流水线完全一致
    prompt, stock_notes, candidates = em._build_homework_prompt()
    if prompt is None:
        print("ERROR: 无候选股数据，无法构造测试 prompt（请确认 data.json 等文件存在）")
        sys.exit(1)

    print("=" * 80)
    print("真实 PROMPT（与生产环境 _gen_homework_summary 完全一致）:")
    print(prompt)
    print("=" * 80)
    print(f"候选股数量: {len(candidates)}, 逐股结构化数据数量: {len(stock_notes)}")
    print("=" * 80)

    results = {}
    for model, price_tag in CANDIDATE_MODELS:
        print(f"\n### 调用模型: {model} ({price_tag}) ###")
        text = call_model(api_key, model, prompt)
        is_error = text.startswith("[ERROR]")
        length_ok = len(text) <= 180
        results[model] = {
            "price_tag": price_tag,
            "output": text,
            "length": len(text),
            "length_ok_le_180": length_ok,
            "error": is_error,
        }
        print(f"字数: {len(text)} (≤180要求: {length_ok})")
        print(f"输出: {text}")
        print("-" * 80)

    with open('llm_model_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "prompt": prompt,
            "candidate_count": len(candidates),
            "results": results,
        }, f, ensure_ascii=False, indent=2)
    print("\n结果已保存到 llm_model_test_results.json（作为 CI artifact 上传，不影响生产文件）")


if __name__ == '__main__':
    main()
