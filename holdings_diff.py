"""Compare report holdings without treating ticker spelling changes as trades."""
import re

# Confirmed issuer actions only; never infer a split from a price/share change.
VERIFIED_SPLITS = (
    {"ticker": "GOOG", "cusip": "02079K107", "quarter": "2022 Q3", "factor": 20,
     "date": "2022-07-15", "source": "https://www.sec.gov/Archives/edgar/data/1652044/000165204422000071/goog-20220630.htm"},
    {"ticker": "GOOGL", "cusip": "02079K305", "quarter": "2022 Q3", "factor": 20,
     "date": "2022-07-15", "source": "https://www.sec.gov/Archives/edgar/data/1652044/000165204422000071/goog-20220630.htm"},
    {"ticker": "CVNA", "cusip": "146869102", "quarter": "2026 Q2", "factor": 5,
     "date": "2026-05-08", "source": "https://www.sec.gov/Archives/edgar/data/1690820/000169082026000055/cvna-20260630.htm"},
)


def share_adjustment(holding, previous_quarter, current_quarter):
    if not all(isinstance(q, str) and re.fullmatch(r"\d{4} Q[1-4]", q)
               for q in (previous_quarter, current_quarter)):
        return None
    actions = [s for s in VERIFIED_SPLITS if
               (holding.get("cusip") == s["cusip"] or holding.get("ticker") == s["ticker"])
               and previous_quarter < s["quarter"] <= current_quarter]
    if not actions:
        return None
    factor = 1
    for action in actions:
        factor *= action["factor"]
    return {"factor": factor, "date": actions[-1]["date"], "source": actions[-1]["source"]}


def instrument(holding):
    return (str(holding.get('putCall') or '').upper(), str(holding.get('shareType') or 'SH').upper())


def consolidate_holdings(holdings):
    """Sum manager/discretion rows, keeping options and principal distinct."""
    merged = {}
    for holding in holdings:
        identity = holding.get('cusip') or (re.sub(r'[./-]', '', holding.get('ticker', '').upper()), holding.get('cls', ''))
        key = (identity, *instrument(holding))
        if key not in merged:
            merged[key] = dict(holding)
        else:
            row = merged[key]
            for field in ('shares', 'value', 'prevShares', 'prevValue'):
                if field in row or field in holding:
                    row[field] = None if field.startswith('prev') and (row.get(field) is None or holding.get(field) is None) else (row.get(field) or 0) + (holding.get(field) or 0)
            # Cached per-line split adjustments cannot describe a grouped position.
            row.pop('shareAdjustment', None)
    return list(merged.values())


def same_security(a, b):
    if instrument(a) != instrument(b):
        return False
    if a.get("cusip") and b.get("cusip"):
        return a["cusip"] == b["cusip"]
    ticker = lambda h: re.sub(r"[./-]", "", h.get("ticker", "").upper())
    if ticker(a) and ticker(a) == ticker(b):
        return True
    return bool(a.get("name")) and a.get("name") == b.get("name") and (
        a.get("cls", "") == b.get("cls", "")
    ) and (a.get("ticker", "").startswith("?") or b.get("ticker", "").startswith("?"))


def compare_holdings(current, previous, *, previous_quarter=None, current_quarter=None):
    current = consolidate_holdings(current)
    remaining = consolidate_holdings(previous)
    rows = []
    for holding in current:
        match = next((i for i, p in enumerate(remaining) if same_security(holding, p)), None)
        old = remaining.pop(match) if match is not None else {}
        adjustment = share_adjustment(holding, previous_quarter, current_quarter)
        cached = holding.get("shareAdjustment") or {}
        if adjustment is None and previous_quarter is None and cached.get("reportedShares") == old.get("shares"):
            adjustment = cached
        row = dict(holding, prevShares=old.get("shares", 0), prevValue=old.get("value", 0))
        row.pop("shareAdjustment", None)
        if adjustment and old.get("shares", 0) > 0:
            row["shareAdjustment"] = {**adjustment, "reportedShares": old["shares"]}
            row["prevShares"] = old["shares"] * adjustment["factor"]
        rows.append(row)
    for old in remaining:
        if old.get("shares", 0) > 0:
            rows.append(dict(old, shares=0, value=0, prevShares=old["shares"],
                             prevValue=old.get("value", 0), exited=True))
    return rows


def attach_previous(current, previous, *, previous_quarter=None, current_quarter=None):
    """Keep exited positions out of current totals, counts and allocation charts."""
    for holding, compared in zip(current, compare_holdings(current, previous,
            previous_quarter=previous_quarter, current_quarter=current_quarter)):
        holding["prevShares"] = compared["prevShares"]
        holding["prevValue"] = compared["prevValue"]
        holding.pop("shareAdjustment", None)
        if "shareAdjustment" in compared:
            holding["shareAdjustment"] = compared["shareAdjustment"]


def update_history(data, quarter, holdings):
    """Replace refreshed quarters as well as adding new ones; old snapshots may be stale."""
    history = data.setdefault("history", {"quarters": [], "values": [], "holdings": {}})
    if quarter not in history["quarters"]:
        history["quarters"].append(quarter)
        history["values"].append(0)
    history["values"][history["quarters"].index(quarter)] = round(sum(h["value"] for h in holdings) / 1_000_000, 6)
    history.setdefault("holdings", {})[quarter] = holdings
    pairs = sorted(zip(history["quarters"], history["values"]))
    history["quarters"] = [q for q, _ in pairs]
    history["values"] = [v for _, v in pairs]
