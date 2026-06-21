#!/usr/bin/env python3
"""Build catalog/patterns.json from the final taxonomy CSV structure."""

from __future__ import annotations

import csv
import json
import re
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "method" / "prompt_taxonomy_final_29_patterns.csv"
RAW_DATASET_PATH = ROOT / "method" / "master_raw_dataset.csv"
JSON_PATH = ROOT / "catalog" / "patterns.json"
DOCS_JSON_PATH = ROOT / "docs" / "catalog" / "patterns.json"
FORMALIZATION_DIR = ROOT / "method" / "formalizations"

TODO_PATTERNS = set()

CATEGORY_TO_ENUM = {
    "In-context Learning": "IN_CONTEXT_LEARNING",
    "Reasoning": "REASONING",
    "Output Control": "OUTPUT_CONTROL",
    "Context Control": "CONTEXT_CONTROL",
    "Meta-Directives": "META_DIRECTIVES",
}
COMPONENT_TO_ENUM = {
    "Profile/Role": "PROFILE_ROLE",
    "Directive": "DIRECTIVE",
    "Context": "CONTEXT",
    "Procedural Steps": "PROCEDURAL_STEPS",
    "Examples": "EXAMPLES",
    "Output Format/Style": "OUTPUT_FORMAT",
    "Constraints": "CONSTRAINTS",
}


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def normalize_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def csv_match_keys(name: str) -> set[str]:
    keys = {normalize_name(name)}
    without_parenthetical = re.sub(r"\s*\([^)]*\)", "", name)
    keys.add(normalize_name(without_parenthetical))

    for key in list(keys):
        if key.endswith("prompting"):
            keys.add(key[: -len("prompting")])
        if key.endswith("cotcot"):
            keys.add(key[: -len("cot")])
        if key.endswith("scotscot"):
            keys.add(key[: -len("scot")])
        if key.endswith("psps"):
            keys.add(key[: -len("psps")])

    if "persona" in normalize_name(name):
        keys.add("persona")

    return {key for key in keys if key}


def json_match_keys(name: str) -> set[str]:
    return {normalize_name(name)}


def read_csv_rows() -> list[dict[str, str]]:
    with CSV_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_raw_rows() -> list[dict[str, str]]:
    with RAW_DATASET_PATH.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json() -> dict[str, Any]:
    with JSON_PATH.open(encoding="utf-8") as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def build_csv_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        keys = csv_match_keys(row["Pattern Name"])
        for key in keys:
            if key in index:
                fail(
                    "ambiguous CSV normalized key "
                    f"{key!r}: {index[key]['Pattern Name']!r} and {row['Pattern Name']!r}"
                )
            index[key] = row
    return index


def find_csv_row(pattern: dict[str, Any], csv_index: dict[str, dict[str, str]]) -> dict[str, str] | None:
    for key in json_match_keys(str(pattern["name"])):
        if key in csv_index:
            return csv_index[key]
    return None


def mapped_category(row: dict[str, str]) -> str:
    value = row["Category"].strip()
    if value not in CATEGORY_TO_ENUM:
        fail(f"unsupported category {value!r} for {row['Pattern Name']!r}")
    return CATEGORY_TO_ENUM[value]


def mapped_components(row: dict[str, str]) -> list[str]:
    components: list[str] = []
    for part in row["Component use"].split(","):
        value = part.strip()
        if not value:
            continue
        if value not in COMPONENT_TO_ENUM:
            fail(f"unsupported component {value!r} for {row['Pattern Name']!r}")
        components.append(COMPONENT_TO_ENUM[value])
    if not components:
        fail(f"empty Component use for {row['Pattern Name']!r}")
    return components


def formalization_path(pattern_id: str) -> Path:
    return FORMALIZATION_DIR / f"{pattern_id}.promptspec"


def read_formalization(pattern_id: str) -> str:
    path = formalization_path(pattern_id)
    if not path.exists():
        fail(f"missing formalization file for pattern id {pattern_id!r}: {path}")
    return path.read_text(encoding="utf-8")


def validate_formalization_files(patterns: list[dict[str, Any]]) -> None:
    expected_ids = {str(pattern.get("id")) for pattern in patterns}
    expected_paths = {formalization_path(pattern_id) for pattern_id in expected_ids}
    actual_paths = set(FORMALIZATION_DIR.glob("*.promptspec"))

    missing = sorted(path.relative_to(ROOT).as_posix() for path in expected_paths - actual_paths)
    extra = sorted(path.relative_to(ROOT).as_posix() for path in actual_paths - expected_paths)

    if missing or extra:
        parts = []
        if missing:
            parts.append(f"missing formalization files: {missing}")
        if extra:
            parts.append(f"extra formalization files: {extra}")
        fail("; ".join(parts))


def build_extensions(
    csv_rows: list[dict[str, str]], raw_rows: list[dict[str, str]]
) -> dict[str, list[OrderedDict[str, str]]]:
    csv_names = {row["Pattern Name"] for row in csv_rows}
    included_rows = [row for row in raw_rows if row["status"] == "INCLUDED"]
    by_final_name: dict[str, list[OrderedDict[str, str]]] = {
        name: [] for name in csv_names
    }
    errors: list[str] = []

    for row in included_rows:
        final_name = row["canonical_final_name"]
        if final_name not in csv_names:
            errors.append(
                f"INCLUDED raw row {row.get('raw_id', '<missing raw_id>')} has "
                f"canonical_final_name {final_name!r}, which is not exactly one CSV Pattern Name"
            )
            continue
        by_final_name[final_name].append(
            OrderedDict([("name", row["raw_name"]), ("source", row["source_key"])])
        )

    for final_name, extensions in by_final_name.items():
        if not extensions:
            errors.append(f"CSV Pattern Name {final_name!r} has no INCLUDED raw extensions")
        extensions.sort(key=lambda item: (item["source"], item["name"]))

    total_extensions = sum(len(extensions) for extensions in by_final_name.values())
    if total_extensions != len(included_rows):
        errors.append(
            f"extension total mismatch: built {total_extensions}, "
            f"but master_raw_dataset.csv has {len(included_rows)} INCLUDED rows"
        )

    if errors:
        fail("; ".join(errors))
    return by_final_name


def ordered_pattern(
    existing: dict[str, Any],
    row: dict[str, str],
    extensions: list[OrderedDict[str, str]],
) -> OrderedDict[str, Any]:
    name = str(existing["name"])

    return OrderedDict(
        [
            ("id", existing.get("id")),
            ("name", name),
            ("description", existing.get("description")),
            ("category", mapped_category(row)),
            ("subcategory", row["Subcategory"].strip()),
            ("componentTypes", mapped_components(row)),
            ("detectionInstruction", existing.get("detectionInstruction")),
            ("placeholderExample", existing.get("placeholderExample")),
            ("example", existing.get("example")),
            ("notes", existing.get("notes")),
            ("formalization", read_formalization(str(existing.get("id")))),
            ("extensions", extensions),
        ]
    )


def main() -> None:
    csv_rows = read_csv_rows()
    raw_rows = read_raw_rows()
    data = read_json()
    patterns = data.get("patterns", [])

    if len(csv_rows) != 29:
        fail(f"CSV pattern count must be 29; got {len(csv_rows)}")
    if len(patterns) != 29:
        fail(f"JSON pattern count must be 29; got {len(patterns)}")
    validate_formalization_files(patterns)

    csv_index = build_csv_index(csv_rows)
    extensions_by_final_name = build_extensions(csv_rows, raw_rows)
    matched_csv_names: set[str] = set()
    generated_patterns: list[OrderedDict[str, Any]] = []

    for pattern in patterns:
        row = find_csv_row(pattern, csv_index)
        if row is None:
            fail(f"JSON pattern {pattern.get('name')!r} has no CSV match")
        matched_csv_names.add(row["Pattern Name"])
        generated_patterns.append(
            ordered_pattern(pattern, row, extensions_by_final_name[row["Pattern Name"]])
        )

    csv_names = {row["Pattern Name"] for row in csv_rows}
    if matched_csv_names != csv_names:
        missing = sorted(csv_names - matched_csv_names)
        extra = sorted(matched_csv_names - csv_names)
        fail(f"CSV/JSON match mismatch; only in CSV={missing}, unexpected matches={extra}")

    output = OrderedDict()
    for key, value in data.items():
        if key == "patterns":
            output[key] = generated_patterns
        elif key == "count":
            output[key] = len(generated_patterns)
        else:
            output[key] = value

    payload = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    JSON_PATH.write_text(payload, encoding="utf-8")
    DOCS_JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    DOCS_JSON_PATH.write_text(payload, encoding="utf-8")
    print(
        "Built "
        f"{JSON_PATH.relative_to(ROOT)} and {DOCS_JSON_PATH.relative_to(ROOT)} "
        f"from {CSV_PATH.relative_to(ROOT)}"
    )


if __name__ == "__main__":
    main()
