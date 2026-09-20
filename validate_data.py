"""Validate the same explicit file set that is committed and deployed."""
import argparse
import json
import math
import re
from pathlib import Path
import subprocess
import sys
from spinoff_events import validate_events


EXTRA_FILES = (
    "metadata_cache.json", "alerts_hk_persons.json", "spinoff.json", "spinoff_us.json",
    "run_status.json", "homework_summary.json", "value_screen.json",
)
OPTIONAL_FILES = ("resolved_cusip_map.json",)


def read_json(path):
    def invalid_constant(value):
        raise ValueError(f"Non-finite JSON number: {value}")
    value = json.loads(path.read_text(encoding="utf-8"), parse_constant=invalid_constant)
    if not isinstance(value, dict):
        raise ValueError("Expected a JSON object")
    return value



def validate_history(history):
    if history is None:
        return
    quarters, values = history.get("quarters", []), history.get("values", [])
    if len(quarters) != len(values) or len(set(quarters)) != len(quarters):
        raise ValueError("History quarters/values must align without duplicate quarters")
    if any(not isinstance(q, str) or not re.fullmatch(r"\d{4} Q[1-4]", q) for q in quarters):
        raise ValueError("Invalid history quarter")
    for q, value in zip(quarters, values):
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value) or value < 0:
            raise ValueError(f"Invalid history value: {q}")
        holdings = history.get("holdings", {}).get(q)
        if holdings:
            amounts = [h.get("value") for h in holdings]
            if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not math.isfinite(v) or v < 0 for v in amounts):
                raise ValueError(f"Invalid historical holding value: {q}")
            # Legacy files rounded to whole millions. Reject larger discrepancies.
            if abs(sum(amounts) / 1_000_000 - value) > .500001:
                raise ValueError(f"History total disagrees with holdings: {q}")


def validate_hk_evidence(value):
    from datetime import date
    from urllib.parse import urlsplit
    if not isinstance(value.get("holdings"), list):
        raise ValueError("Missing HK disclosure holdings")
    for holding in value["holdings"]:
        if not re.fullmatch(r"\d{5}\.HK", holding.get("ticker", "")):
            raise ValueError("Invalid HK disclosure ticker")
        for record in holding.get("verified_disclosures", []):
            date.fromisoformat(record.get("event_date", ""))
            if not record.get("filing_ref"):
                raise ValueError("Missing HK filing reference")
            for key in ("source_url", "form_url"):
                if key == "form_url" and key not in record:
                    continue
                url = urlsplit(record.get(key, ""))
                if url.scheme != "https" or url.netloc != "di.hkex.com.hk":
                    raise ValueError("HK evidence must link to HKEX")
            shares, pct = record.get("shares"), record.get("pct")
            if type(shares) is not int or shares < 0 or type(pct) not in (int,float) or not math.isfinite(pct) or not 0 <= pct <= 100:
                raise ValueError("Invalid HK post-event position")


def validate(root):
    root = Path(root)
    config = read_json(root / "investors.json")
    investors = config.get("investors")
    if not isinstance(investors, list) or not investors:
        raise ValueError("investors.json: missing investor list")
    roles = {name: "extra" for name in EXTRA_FILES}
    for inv in investors:
        for key in ("dataFile", "pricesFile", "hkFile"):
            name = inv.get(key)
            if name:
                if Path(name).name != name or not name.endswith(".json"):
                    raise ValueError(f"Invalid data path: {name}")
                roles[name] = key
    for name in OPTIONAL_FILES:
        if (root / name).exists():
            roles[name] = "extra"
    errors = []
    for name, role in roles.items():
        try:
            value = read_json(root / name)
            if name in ("spinoff.json", "spinoff_us.json"):
                validate_events(value)
            if role == "dataFile":
                validate_history(value.get("history"))
                current = value.get("current", {})
                if not isinstance(current.get("holdings"), list) or not current.get("quarter"):
                    raise ValueError("Missing current holdings or quarter")
                for h in current["holdings"] + current.get("previousHoldings", []):
                    if not h.get("ticker"):
                        raise ValueError("Missing holding ticker")
                    for field in ("shares", "value"):
                        number = h.get(field)
                        if not isinstance(number, (int, float)) or isinstance(number, bool) or not math.isfinite(number) or number < 0:
                            raise ValueError(f"Invalid {field} for {h['ticker']}")
            if role == "hkFile":
                validate_hk_evidence(value)
            if role == "pricesFile" and not isinstance(value.get("quotes"), dict):
                raise ValueError("Missing price quotes")
            if name == "run_status.json" and not isinstance(value.get("runs"), list):
                raise ValueError("Missing run status list")
        except (OSError, ValueError, TypeError, AttributeError) as exc:
            errors.append(f"{name}: {exc}")
    if errors:
        raise ValueError("\n".join(errors))
    return sorted(roles)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", action="store_true", help="Stage only after every file passes validation")
    args = parser.parse_args()
    try:
        files = validate(Path.cwd())
        if args.stage:
            subprocess.run(["git", "add", "--", *files], check=True)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Data validation failed:\n{exc}", file=sys.stderr)
        return 1
    print(f"Validated {len(files)} data files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
