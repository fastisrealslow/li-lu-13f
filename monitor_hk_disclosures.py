#!/usr/bin/env python3
"""Configuration-driven HKEX verification entry point (all investors)."""
import json
import os
from datetime import datetime, timezone

today = datetime.now(timezone.utc)


def normalize_hk_ticker(code):
    return str(code).upper().replace('.HK', '').zfill(5) + '.HK' if code else ''


def update_hk_file(hk_file, all_holdings):
    """Person search discovers historical records, never a current position.

    Only dated, separately verified filing records may supply dates/quantities.
    An absent search hit is not evidence of a sale or a below-threshold position.
    """
    if not os.path.exists(hk_file):
        return []
    with open(hk_file, encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        data = {"holdings": data}
    holdings = data.setdefault("holdings", [])
    for row in holdings:
        row["ticker"] = normalize_hk_ticker(row.get("ticker", ""))
        if row.get("evidence_schema") != 2:
            # Preserve old assertions for audit, but do not present them as facts.
            row["legacy_unverified"] = {k: row.get(k) for k in (
                "first_disclosure", "last_disclosure", "current_status", "notes",
                "pct", "pct_date", "peak_shares", "peak_pct", "peak_date", "filing_refs")}
            row.update(evidence_schema=2, first_disclosure=None, last_disclosure=None,
                       current_status="unknown", data_quality="unverified",
                       peak_known=False, peak_shares=None, peak_pct=None, peak_date=None,
                       pct=None, pct_date=None, buy_price_known=False, buy_price_note="",
                       notes="历史搜索记录；具体披露日期和数量待核实，不能据此判断当前持仓。")
    by_ticker = {row["ticker"]: row for row in holdings}
    added = []
    for hit in all_holdings:
        ticker = normalize_hk_ticker(hit.get("ticker", ""))
        if not ticker:
            continue
        if ticker not in by_ticker:
            row = dict(ticker=ticker, name=hit["stockName"], sector="",
                       entity=hit["entity"], evidence_schema=2, first_disclosure=None,
                       last_disclosure=None, current_status="unknown", data_quality="unverified",
                       peak_known=False, peak_shares=None, peak_pct=None,
                       notes="发现历史披露记录，具体日期和数量待核实；当前持仓未知。")
            by_ticker[ticker] = row
            holdings.append(row)
            added.append(f"{ticker} {hit['stockName']}")
        row = by_ticker[ticker]
        row["last_search_seen"] = today.strftime("%Y-%m-%d")
        row["discovery_url"] = hit.get("noticeUrl", "")
        # In particular, do NOT set last_disclosure, pct_date or current_status.
    data["source"] = "HKEX 权益披露：历史搜索线索及已核实披露记录"
    data["disclaimer"] = "历史披露不代表当前持仓；搜索日期不等于披露日期。未搜到记录不代表已清仓或低于5%。比例须按原披露的股份类别解读。"
    data["lastUpdated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    with open(hk_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"  {hk_file}: {len(added)} new historical leads; no current-position inference")
    return added



def main():
    from hk_disclosures import run
    run()


if __name__ == '__main__':
    main()
