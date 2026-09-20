"""Compare report holdings without treating ticker spelling changes as trades."""
import re


def same_security(a, b):
    if a.get("cusip") and b.get("cusip"):
        return a["cusip"] == b["cusip"]
    ticker = lambda h: re.sub(r"[./-]", "", h.get("ticker", "").upper())
    if ticker(a) and ticker(a) == ticker(b):
        return True
    return bool(a.get("name")) and a.get("name") == b.get("name") and (
        a.get("cls", "") == b.get("cls", "")
    ) and (a.get("ticker", "").startswith("?") or b.get("ticker", "").startswith("?"))


def compare_holdings(current, previous):
    remaining = list(previous)
    rows = []
    for holding in current:
        match = next((i for i, p in enumerate(remaining) if same_security(holding, p)), None)
        old = remaining.pop(match) if match is not None else {}
        rows.append(dict(holding, prevShares=old.get("shares", 0), prevValue=old.get("value", 0)))
    for old in remaining:
        if old.get("shares", 0) > 0:
            rows.append(dict(old, shares=0, value=0, prevShares=old["shares"],
                             prevValue=old.get("value", 0), exited=True))
    return rows


def attach_previous(current, previous):
    """Keep exited positions out of current totals, counts and allocation charts."""
    for holding, compared in zip(current, compare_holdings(current, previous)):
        holding["prevShares"] = compared["prevShares"]
        holding["prevValue"] = compared["prevValue"]


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
