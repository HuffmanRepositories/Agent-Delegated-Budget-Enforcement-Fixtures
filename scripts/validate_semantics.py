#!/usr/bin/env python3
"""Semantic consistency checks for synthetic delegated-budget event fixtures.

This validates scenario references and accounting relationships. It does not
simulate a production ledger, concurrency control, or implementation behavior.
"""
from __future__ import annotations

import json
import math
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
EVENT_TYPES = {
    "reserve", "allocate", "delegate", "usage_commit", "settle", "release",
    "request_additional", "aggregate", "cancel", "window_reset",
    "reserve_request", "reserve_result", "revoke",
}


def _number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def validate_data(data: Any, name: str = "<fixture>") -> list[str]:
    errors: list[str] = []
    if not isinstance(data, dict):
        return [f"{name}: root must be an object"]

    budget = data.get("budget")
    if not isinstance(budget, dict):
        errors.append(f"{name}: budget must be an object")
    else:
        if "limits" in budget:
            limits = budget.get("limits")
            if not isinstance(limits, list) or not limits:
                errors.append(f"{name}: budget.limits must be a non-empty list")
            else:
                for i, limit in enumerate(limits):
                    if not isinstance(limit, dict) or not isinstance(limit.get("unit"), str) or not limit["unit"].strip():
                        errors.append(f"{name}: budget.limits[{i}] needs a unit")
                    if not isinstance(limit, dict) or not _number(limit.get("amount")) or limit["amount"] <= 0:
                        errors.append(f"{name}: budget.limits[{i}].amount must be positive")
        elif not _number(budget.get("limit")) or budget["limit"] <= 0:
            errors.append(f"{name}: budget.limit must be a positive finite number")

    actors = data.get("actors")
    if not isinstance(actors, list) or not actors:
        errors.append(f"{name}: actors must be a non-empty list")
        actors = []
    actor_map: dict[str, dict[str, Any]] = {}
    for i, actor in enumerate(actors):
        if not isinstance(actor, dict):
            errors.append(f"{name}: actors[{i}] must be an object")
            continue
        actor_id = actor.get("id")
        if not isinstance(actor_id, str) or not actor_id.strip():
            errors.append(f"{name}: actors[{i}].id must be a non-empty string")
            continue
        if actor_id in actor_map:
            errors.append(f"{name}: duplicate actor id {actor_id!r}")
        actor_map[actor_id] = actor

    for actor_id, actor in actor_map.items():
        parent = actor.get("parent_id")
        if parent is not None and parent not in actor_map:
            errors.append(f"{name}: actor {actor_id!r} references missing parent {parent!r}")
        seen = {actor_id}
        current = parent
        while current in actor_map:
            if current in seen:
                errors.append(f"{name}: actor hierarchy contains a cycle from {actor_id!r}")
                break
            seen.add(current)
            current = actor_map[current].get("parent_id")

    events = data.get("events")
    if not isinstance(events, list) or not events:
        errors.append(f"{name}: events must be a non-empty list")
        events = []

    reserved: dict[str, float] = {}
    committed: dict[str, float] = {}
    released: dict[str, float] = {}

    for i, event in enumerate(events):
        label = f"{name}: events[{i}]"
        if not isinstance(event, dict):
            errors.append(f"{label} must be an object")
            continue
        event_type = event.get("type")
        if event_type not in EVENT_TYPES:
            errors.append(f"{label}.type is unsupported: {event_type!r}")
        actor_id = event.get("actor_id")
        if not isinstance(actor_id, str) or actor_id not in actor_map:
            errors.append(f"{label}.actor_id references unknown actor {actor_id!r}")
        target_id = event.get("target_id")
        if target_id is not None and (not isinstance(target_id, str) or target_id not in actor_map):
            errors.append(f"{label}.target_id references unknown actor {target_id!r}")

        for field in ("amount", "reserved", "actual"):
            if field in event and (not _number(event[field]) or event[field] < 0):
                errors.append(f"{label}.{field} must be a finite non-negative number")

        owner = target_id if event_type in {"release"} and isinstance(target_id, str) else actor_id
        if event_type == "reserve" and isinstance(actor_id, str) and actor_id in actor_map:
            reserved[actor_id] = reserved.get(actor_id, 0.0) + float(event.get("amount", 0))
        elif event_type == "usage_commit" and isinstance(actor_id, str) and actor_id in actor_map:
            committed[actor_id] = committed.get(actor_id, 0.0) + float(event.get("amount", 0))
        elif event_type == "release" and isinstance(owner, str) and owner in actor_map:
            available_to_release = reserved.get(owner, 0.0) - committed.get(owner, 0.0) - released.get(owner, 0.0)
            amount = float(event.get("amount", 0))
            if amount > available_to_release:
                errors.append(f"{label}: release {amount:g} exceeds remaining reservation {available_to_release:g} for {owner!r}")
            released[owner] = released.get(owner, 0.0) + amount
        elif event_type == "settle" and isinstance(actor_id, str) and actor_id in actor_map:
            reserved_amount = event.get("reserved")
            actual_amount = event.get("actual")
            if not _number(reserved_amount) or not _number(actual_amount):
                errors.append(f"{label}: settle requires finite reserved and actual amounts")
            else:
                if reserved_amount > reserved.get(actor_id, 0.0):
                    errors.append(f"{label}: settlement reserved amount exceeds preceding reservations")
                if actual_amount > reserved_amount:
                    errors.append(f"{label}: actual usage exceeds reserved amount")

    expected = data.get("expected_invariants")
    if not isinstance(expected, list) or not expected or any(not isinstance(x, str) or not x.strip() for x in expected):
        errors.append(f"{name}: expected_invariants must be a non-empty list of non-empty strings")
    failure_mode = data.get("failure_mode")
    if not isinstance(failure_mode, str) or not failure_mode.strip():
        errors.append(f"{name}: failure_mode must be a non-empty string")
    return errors


def validate(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.name}: invalid JSON: {exc}"]
    return validate_data(data, path.name)


def validate_all() -> tuple[list[str], int]:
    files = sorted(FIXTURES.glob("*.json"))
    errors = []
    if not files:
        errors.append("No fixture files found")
    for path in files:
        errors.extend(validate(path))
    return errors, len(files)


def main() -> int:
    errors, count = validate_all()
    if errors:
        print("Semantic fixture consistency check failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Semantic fixture consistency checks passed for {count} draft fixtures.")
    print("This validates scenario structure/accounting relationships only—not runtime enforcement.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
