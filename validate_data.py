"""Validate the same explicit file set that is committed and deployed."""
import argparse
import json
import math
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
