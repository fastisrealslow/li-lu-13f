#!/usr/bin/env python3
"""
更新运行状态追踪器。
workflow 的每个步骤在完成后调用:

  python3 update_status.py --step "lilu_13f" --status ok
  python3 update_status.py --step "lilu_prices" --status fail --msg "Finnhub timeout"
  python3 update_status.py --init   # 在 workflow 开始时初始化新的 run 记录

状态文件: run_status.json
格式:
{
  "runs": [
    {
      "run_id": "2026-07-05T14:00:00Z",
      "trigger": "schedule",
      "steps": {
        "lilu_13f":     {"status": "ok",   "ts": "...", "msg": ""},
        "lilu_prices":  {"status": "fail", "ts": "...", "msg": "Finnhub timeout"},
        ...
      }
    },
    ...
  ]
}
最多保留 30 条历史记录。
"""

import json, os, sys
from datetime import datetime, timezone

STATUS_FILE = "run_status.json"
MAX_RUNS    = 30

# 所有步骤的显示名（用于前端）
STEP_LABELS = {
    "lilu_13f":        "李录 13F",
    "lilu_prices":     "李录 股价",
    "pabrai_13f":      "Pabrai 13F",
    "pabrai_prices":   "Pabrai 股价",
    "duan_13f":        "段永平 13F",
    "duan_prices":     "段永平 股价",
    "tepper_13f":      "Tepper 13F",
    "tepper_prices":   "Tepper 股价",
    "webb_prices":     "Webb 股价",
    "webb_holdings":   "Webb 港股持仓",
    "buffett_13f":     "巴菲特 13F",
    "akre_greenberg_13f": "Akre/Greenberg 13F",
    "buffett_prices":  "巴菲特 股价",
    "akre_prices":     "Akre 股价",
    "greenberg_prices":"Greenberg 股价",
    "metadata":        "元数据富化",
    "hk_disclosures":  "港股披露监控",
    "spinoff_hk":      "港股分拆",
    "spinoff_us":      "美股分拆",
}

def load():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"runs": []}

def save(data):
    with open(STATUS_FILE, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def init_run(trigger):
    data = load()
    run_id = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new_run = {
        "run_id":  run_id,
        "trigger": trigger,
        "steps":   {},
    }
    data["runs"].insert(0, new_run)
    data["runs"] = data["runs"][:MAX_RUNS]
    save(data)
    print(f"✅ Initialized run: {run_id}")

def update_step(step, status, msg=""):
    data = load()
    if not data["runs"]:
        # 防御性：如果没有初始化过，自动创建
        init_run("unknown")
        data = load()
    current_run = data["runs"][0]
    current_run["steps"][step] = {
        "status": status,  # "ok" | "fail" | "skip"
        "ts":     datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "msg":    msg,
        "label":  STEP_LABELS.get(step, step),
    }
    save(data)
    icon = "✅" if status == "ok" else ("⚠️" if status == "skip" else "❌")
    print(f"{icon} Step [{step}] → {status}" + (f": {msg}" if msg else ""))

def main():
    args = sys.argv[1:]
    if "--init" in args:
        trigger = "schedule"
        if "--trigger" in args:
            idx = args.index("--trigger")
            trigger = args[idx + 1] if idx + 1 < len(args) else "schedule"
        init_run(trigger)
        return

    step   = None
    status = None
    msg    = ""
    for i, a in enumerate(args):
        if a == "--step"   and i + 1 < len(args): step   = args[i + 1]
        if a == "--status" and i + 1 < len(args): status = args[i + 1]
        if a == "--msg"    and i + 1 < len(args): msg    = args[i + 1]

    if not step or not status:
        print("Usage: python3 update_status.py --step <name> --status <ok|fail|skip> [--msg <message>]", file=sys.stderr)
        print("       python3 update_status.py --init [--trigger schedule|workflow_dispatch]", file=sys.stderr)
        sys.exit(1)

    update_step(step, status, msg)

if __name__ == "__main__":
    main()
