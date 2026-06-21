#!/usr/bin/env python3
"""Validate reproducible taxonomy extraction counts."""

from __future__ import annotations

import csv
import sys
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = ROOT / "method" / "master_raw_dataset.csv"

EXPECTED_RAW_ROWS = 176
EXPECTED_SOURCE_SPLIT = {
    "white2023": 16,
    "schulhoff2024": 55,
    "sahoo2024": 41,
    "vatsal2024": 39,
    "fagbohun2024": 25,
}
EXPECTED_NORMALIZED_NAMES = 163
EXPECTED_CANONICAL_KEYS = 128
EXPECTED_STATUS_COUNTS = {
    "INCLUDED": 29,
    "EXCLUDED_WORKFLOW": 68,
    "EXCLUDED_OUT_OF_SCOPE": 31,
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def read_rows() -> list[dict[str, str]]:
    if not DATASET_PATH.exists():
        fail(f"missing dataset: {DATASET_PATH}")
    with DATASET_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def assert_equal(label: str, actual: object, expected: object) -> None:
    if actual != expected:
        fail(f"{label}: expected {expected!r}, got {actual!r}")


def main() -> None:
    rows = read_rows()

    assert_equal("raw row count", len(rows), EXPECTED_RAW_ROWS)

    source_counts = Counter(row["source_key"] for row in rows)
    assert_equal("source split", dict(source_counts), EXPECTED_SOURCE_SPLIT)

    normalized_names = {row["normalized_name"] for row in rows}
    assert_equal(
        "unique normalized_name count",
        len(normalized_names),
        EXPECTED_NORMALIZED_NAMES,
    )

    canonical_keys = {row["canonical_key"] for row in rows}
    assert_equal("unique canonical_key count", len(canonical_keys), EXPECTED_CANONICAL_KEYS)

    status_counts = {
        status: len({row["canonical_key"] for row in rows if row["status"] == status})
        for status in EXPECTED_STATUS_COUNTS
    }
    assert_equal(
        "unique canonical_key count per status",
        status_counts,
        EXPECTED_STATUS_COUNTS,
    )

    print("Taxonomy count validation passed.")
    print(f"  Raw rows: {len(rows)}")
    print(f"  Source split: {dict(source_counts)}")
    print(f"  Unique normalized names: {len(normalized_names)}")
    print(f"  Unique canonical concepts: {len(canonical_keys)}")
    print(f"  Included/excluded concepts: {status_counts}")


if __name__ == "__main__":
    main()
