#!/usr/bin/env python3
"""自动解析未识别 ticker（?前缀）— CUSIP → 真实 ticker 的全自动化流水线。

背景：
  fetch_13f_all.py 的 resolve_ticker() 只能靠手工维护的 TICKER_MAP/
  TICKER_CLASS_MAP/CUSIP_TICKER_MAP 查表，查不到时 fallback 成 "?公司原名"
  存入 JSON（current.holdings 和 history.holdings 都可能出现）。这类记录
  enrich_metadata.py 会主动跳过（不猜测式地拿模糊公司名去问 LLM），导致
  中文名/行业永远补不上。

本脚本做的事（全自动、不依赖任何手工白名单）：
  1. 扫描所有 investors.json 里登记的投资者数据文件，收集所有 "?" 前缀
     记录的 CUSIP。
  2. 用 OpenFIGI 官方免费 API（无需 key，10 个/请求，25 请求/分钟）做
     CUSIP → ticker 权威解析。规则严格：只在候选结果里唯一确定
     "US 交易所 + Common Stock"（或退而求其次唯一的 US 交易所记录）时才
     采纳，出现多个不同 ticker 的歧义结果一律不采纳，避免引入错误映射。
  3. 新解析出的 CUSIP→ticker 结果持久化写入 resolved_cusip_map.json，
     作为运行时缓存 —— 之后 fetch_13f_all.py 启动时会自动加载合并进
     CUSIP_TICKER_MAP，重跑历史抓取或新投资者时不会重复查询已解析过的
     CUSIP。
  4. 就地回填所有历史 JSON 文件里已经落盘的 "?" 前缀记录（current 和
     history 两部分），把能用新映射解析出的 ticker 写回去。

无法通过 OpenFIGI 解析的记录（通常是已退市/被并购/私有化的历史证券，
OpenFIGI 和 SEC 官方 ticker 表都只维护当前活跃证券）保持原样，不做任何
猜测性填充 —— 这是设计原则，不是遗漏。

用法：
  python3 resolve_unmapped_tickers.py            # 全量扫描 + 解析 + 回填
  python3 resolve_unmapped_tickers.py --dry-run  # 只扫描统计，不写入任何文件
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error

BASE = os.path.dirname(os.path.abspath(__file__))
RESOLVED_MAP_PATH = os.path.join(BASE, "resolved_cusip_map.json")
OPENFIGI_URL = "https://api.openfigi.com/v3/mapping"
BATCH_SIZE = 10          # OpenFIGI 无 key 时单请求最多 10 个 job
RATE_LIMIT_SLEEP = 2.6   # 无 key 限流 25 请求/分钟，留余量


def load_investor_data_files():
    """从 investors.json 读取所有投资者的数据文件路径（单一权威来源）。"""
    with open(os.path.join(BASE, "investors.json"), encoding="utf-8") as f:
        investors = json.load(f)["investors"]
    return [os.path.join(BASE, inv["dataFile"]) for inv in investors if inv.get("dataFile")]


def load_resolved_map():
    if os.path.exists(RESOLVED_MAP_PATH):
        with open(RESOLVED_MAP_PATH, encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_resolved_map(m):
    with open(RESOLVED_MAP_PATH, "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2, sort_keys=True)
        f.write("\n")


def scan_unresolved_cusips(data_files, already_resolved):
    """扫描所有数据文件的 current + history 持仓，收集尚未解析的 CUSIP。
    返回: {cusip: 出现次数}（用于日志展示优先级，不影响解析逻辑）。"""
    cusip_counts = {}
    for path in data_files:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        def scan_holdings(holdings):
            for h in holdings:
                tk = h.get("ticker", "")
                cusip = (h.get("cusip") or "").strip()
                if tk.startswith("?") and cusip and cusip not in already_resolved:
                    cusip_counts[cusip] = cusip_counts.get(cusip, 0) + 1

        scan_holdings(data.get("current", {}).get("holdings", []))
        for holdings in data.get("history", {}).get("holdings", {}).values():
            scan_holdings(holdings)
    return cusip_counts


def resolve_via_openfigi(cusips):
    """批量调用 OpenFIGI，返回 {cusip: ticker}（仅保留高置信度唯一匹配）。"""
    resolved = {}
    cusips = list(cusips)
    for i in range(0, len(cusips), BATCH_SIZE):
        batch = cusips[i:i + BATCH_SIZE]
        jobs = [{"idType": "ID_CUSIP", "idValue": c} for c in batch]
        req = urllib.request.Request(
            OPENFIGI_URL,
            data=json.dumps(jobs).encode(),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        batch_result = None
        for attempt in range(3):
            try:
                with urllib.request.urlopen(req, timeout=20) as resp:
                    batch_result = json.loads(resp.read())
                break
            except urllib.error.HTTPError as e:
                if e.code == 429:
                    print(f"  429 限流，等待 20s...", file=sys.stderr)
                    time.sleep(20)
                else:
                    print(f"  HTTP {e.code}: {e.read()[:200]}", file=sys.stderr)
                    time.sleep(5)
            except Exception as e:
                print(f"  请求失败（第{attempt+1}次）: {e}", file=sys.stderr)
                time.sleep(10)
        if batch_result is None:
            print(f"  批次 {i} 三次重试均失败，跳过本批", file=sys.stderr)
            continue

        for cusip, r in zip(batch, batch_result):
            if "error" in r:
                continue
            data = r.get("data", [])
            # 规则1（首选）：US 交易所 + Common Stock，且候选 ticker 唯一
            candidates = [x for x in data if x.get("exchCode") == "US" and x.get("securityType") == "Common Stock"]
            tickers = {x["ticker"] for x in candidates}
            if len(tickers) == 1:
                resolved[cusip] = tickers.pop()
                continue
            if len(tickers) > 1:
                continue  # 歧义，不采纳
            # 规则2（退而求其次）：任意 US 交易所记录，候选 ticker 唯一
            us_candidates = [x for x in data if x.get("exchCode") == "US"]
            us_tickers = {x["ticker"] for x in us_candidates}
            if len(us_tickers) == 1:
                resolved[cusip] = us_tickers.pop()
            # 否则（无 US 记录，或多个不同 ticker）：不采纳，保持未解析

        print(f"  已处理 {min(i + BATCH_SIZE, len(cusips))}/{len(cusips)}")
        time.sleep(RATE_LIMIT_SLEEP)
    return resolved


def backfill_data_files(data_files, resolved_map):
    """用 resolved_map（cusip -> ticker）就地回填所有数据文件里的 ? 前缀记录。
    返回: (修改的文件数, 回填的记录数)。"""
    files_changed = 0
    records_fixed = 0
    for path in data_files:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

        changed = False

        def fix_holdings(holdings):
            nonlocal changed, records_fixed
            for h in holdings:
                tk = h.get("ticker", "")
                cusip = (h.get("cusip") or "").strip()
                if tk.startswith("?") and cusip in resolved_map:
                    h["ticker"] = resolved_map[cusip]
                    changed = True
                    records_fixed += 1

        fix_holdings(data.get("current", {}).get("holdings", []))
        for holdings in data.get("history", {}).get("holdings", {}).values():
            fix_holdings(holdings)

        if changed:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            files_changed += 1
    return files_changed, records_fixed


def main():
    dry_run = "--dry-run" in sys.argv

    data_files = load_investor_data_files()
    resolved_map = load_resolved_map()
    print(f"已缓存的 CUSIP 映射: {len(resolved_map)} 条")

    unresolved_counts = scan_unresolved_cusips(data_files, resolved_map)
    print(f"待解析 CUSIP 数（去重，排除已缓存）: {len(unresolved_counts)}")

    if not unresolved_counts:
        print("没有新的待解析 CUSIP，退出。")
        return

    if dry_run:
        print("(--dry-run) 跳过 OpenFIGI 调用和文件写入。")
        return

    print("调用 OpenFIGI 批量解析...")
    newly_resolved = resolve_via_openfigi(unresolved_counts.keys())
    print(f"本次新解析成功: {len(newly_resolved)}/{len(unresolved_counts)}")

    if newly_resolved:
        resolved_map.update(newly_resolved)
        save_resolved_map(resolved_map)
        print(f"已写入 {RESOLVED_MAP_PATH}（累计 {len(resolved_map)} 条）")

        files_changed, records_fixed = backfill_data_files(data_files, resolved_map)
        print(f"回填完成：{files_changed} 个文件被修改，{records_fixed} 条记录的 ticker 被修正")
    else:
        print("本次没有新增可用映射（剩余均为 OpenFIGI 也查不到的历史/退市证券，属预期情况）")


if __name__ == "__main__":
    main()
