#!/usr/bin/env python3
"""Structural validation for draft synthetic budget fixtures."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
REQUIRED = {"id", "title", "category", "status", "synthetic", "description", "budget", "actors", "events", "expected_invariants", "failure_mode"}

def validate(path: Path):
    errors = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    missing = REQUIRED - data.keys() if isinstance(data, dict) else REQUIRED
    if missing:
        errors.append(f"{path.name}: missing required keys: {', '.join(sorted(missing))}")
        return errors
    if data["synthetic"] is not True:
        errors.append(f"{path.name}: synthetic must be true")
    if data["status"] != "draft":
        errors.append(f"{path.name}: status must remain draft until reviewed")
    if not isinstance(data["actors"], list) or not data["actors"]:
        errors.append(f"{path.name}: actors must be a non-empty list")
    if not isinstance(data["events"], list) or not data["events"]:
        errors.append(f"{path.name}: events must be a non-empty list")
    if not isinstance(data["expected_invariants"], list) or not data["expected_invariants"]:
        errors.append(f"{path.name}: expected_invariants must be a non-empty list")
    if not isinstance(data["budget"], dict) or not data["budget"]:
        errors.append(f"{path.name}: budget must be a non-empty object")
    if not isinstance(data["id"], str) or not data["id"].startswith("DBEF-"):
        errors.append(f"{path.name}: id must use DBEF- prefix")
    return errors

def main():
    files = sorted(FIXTURES.glob("*.json"))
    if not files:
        print("No fixtures found", file=sys.stderr)
        return 1
    errors = [error for path in files for error in validate(path)]
    if errors:
        print("\\n".join(errors), file=sys.stderr)
        return 1
    print(f"Validated {len(files)} synthetic draft fixtures (structure only).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
