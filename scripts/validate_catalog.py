#!/usr/bin/env python3
"""Validate the PromptSpec public pattern catalog.

Checks:
  - All pattern IDs are unique
  - All pattern names are unique
  - Every pattern has a description
  - Declared count matches the actual number of patterns

Usage:
    python3 scripts/validate_catalog.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
SCHEMA_DIR = ROOT / "schema"


def load_json(path: Path) -> dict[str, Any]:
    """Load and parse a JSON file."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def validate_patterns(data: dict[str, Any]) -> list[str]:
    """Validate patterns.json."""
    errors: list[str] = []
    patterns = data.get("patterns", [])
    declared_count = data.get("count")
    ids = set()
    names = set()

    for i, p in enumerate(patterns):
        pid = p.get("id", "")
        name = p.get("name", "")

        if not pid:
            errors.append(f"Pattern [{i}]: missing 'id'")
        elif pid in ids:
            errors.append(f"Pattern [{i}]: duplicate id '{pid}'")
        else:
            ids.add(pid)

        if not name:
            errors.append(f"Pattern [{i}]: missing 'name'")
        elif name in names:
            errors.append(f"Pattern [{i}]: duplicate name '{name}'")
        else:
            names.add(name)

        if not p.get("description"):
            errors.append(f"Pattern '{name}': missing 'description'")
    if declared_count is not None and declared_count != len(patterns):
        errors.append(
            f"Declared count ({declared_count}) != actual pattern count ({len(patterns)})"
        )

    return errors


def main() -> int:
    print("=" * 60)
    print("PromptSpec Catalog Validation")
    print("=" * 60)
    print()

    all_errors: list[str] = []

    # --- Patterns ---
    patterns_path = CATALOG_DIR / "patterns.json"
    if not patterns_path.exists():
        print(f"ERROR: {patterns_path} not found")
        return 1
    patterns_data = load_json(patterns_path)
    pattern_errors = validate_patterns(patterns_data)
    all_errors.extend(pattern_errors)
    print(f"Patterns:  {len(patterns_data.get('patterns', []))} loaded, {len(pattern_errors)} errors")

    # --- Summary ---
    print()
    if all_errors:
        print(f"FAILED: {len(all_errors)} error(s) found:")
        for error in all_errors:
            print(f"  ✗ {error}")
        print()
        return 1
    print("✓ All validations passed.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
