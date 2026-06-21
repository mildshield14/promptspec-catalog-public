#!/usr/bin/env python3
"""Integrity tests for the PromptSpec pattern catalog."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CATALOG_DIR = ROOT / "catalog"
SCHEMA_DIR = ROOT / "schema"


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture
def patterns_data():
    return load_json(CATALOG_DIR / "patterns.json")


@pytest.fixture
def pattern_ids(patterns_data):
    return {p["id"] for p in patterns_data["patterns"]}


class TestPatterns:
    def test_patterns_file_exists(self):
        assert (CATALOG_DIR / "patterns.json").exists()

    def test_docs_catalog_copy_matches(self):
        assert (ROOT / "docs" / "catalog" / "patterns.json").exists()
        assert (ROOT / "docs" / "catalog" / "patterns.json").read_text(
            encoding="utf-8"
        ) == (CATALOG_DIR / "patterns.json").read_text(encoding="utf-8")

    def test_pattern_count_is_29(self, patterns_data):
        assert len(patterns_data["patterns"]) == 29

    def test_declared_count_matches(self, patterns_data):
        assert patterns_data["count"] == len(patterns_data["patterns"])

    def test_all_pattern_ids_unique(self, patterns_data):
        ids = [p["id"] for p in patterns_data["patterns"]]
        assert len(ids) == len(set(ids)), f"Duplicate IDs: {[x for x in ids if ids.count(x) > 1]}"

    def test_all_pattern_names_unique(self, patterns_data):
        names = [p["name"] for p in patterns_data["patterns"]]
        assert len(names) == len(set(names))

    def test_all_patterns_have_required_fields(self, patterns_data):
        for p in patterns_data["patterns"]:
            assert p.get("id"), f"Missing id for pattern: {p}"
            assert p.get("name"), f"Missing name for pattern: {p}"
            assert p.get("description"), f"Missing description for {p.get('name')}"

    def test_pattern_ids_follow_convention(self, patterns_data):
        import re
        for p in patterns_data["patterns"]:
            assert re.match(r"^[a-z0-9_]+$", p["id"]), (
                f"Pattern ID '{p['id']}' doesn't match [a-z0-9_]+ convention"
            )


class TestSchemaFiles:
    def test_pattern_schema_exists(self):
        assert (SCHEMA_DIR / "pattern.schema.json").exists()

    def test_pattern_schema_is_valid_json(self):
        data = load_json(SCHEMA_DIR / "pattern.schema.json")
        assert "$schema" in data or "type" in data


class TestSchemaConformance:
    """Validate catalog data against the JSON Schema (skipped if jsonschema absent)."""

    @pytest.fixture(autouse=True)
    def _check_jsonschema(self):
        pytest.importorskip("jsonschema")

    def test_patterns_conform_to_schema(self):
        from jsonschema import validate
        schema = load_json(SCHEMA_DIR / "pattern.schema.json")
        data = load_json(CATALOG_DIR / "patterns.json")
        validate(instance=data, schema=schema)


class TestArtifactProvenance:
    def test_no_production_prompt_ids(self):
        """Ensure no production-style prompt IDs (UUIDs) appear."""
        import re
        for path in CATALOG_DIR.glob("*.json"):
            content = path.read_text(encoding="utf-8")
            uuids = re.findall(
                r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
                content,
                re.IGNORECASE,
            )
            assert not uuids, f"Possible production UUID found in {path.name}: {uuids}"


class TestPatternCatalogMarkdown:
    """Guard against the human-readable table drifting from the JSON source."""

    def test_markdown_exists(self):
        assert (ROOT / "PATTERN_CATALOG.md").exists()

    def test_docs_markdown_copy_matches(self):
        assert (ROOT / "docs" / "PATTERN_CATALOG.md").exists()
        assert (ROOT / "docs" / "PATTERN_CATALOG.md").read_text(
            encoding="utf-8"
        ) == (ROOT / "PATTERN_CATALOG.md").read_text(encoding="utf-8")

    def test_every_pattern_name_appears(self, patterns_data):
        md = (ROOT / "PATTERN_CATALOG.md").read_text(encoding="utf-8")
        missing = [p["name"] for p in patterns_data["patterns"] if p["name"] not in md]
        assert not missing, f"Patterns missing from PATTERN_CATALOG.md: {missing}"


class TestDocumentation:
    def test_readme_exists(self):
        assert (ROOT / "README.md").exists()

    def test_terminology_exists(self):
        assert (ROOT / "docs" / "terminology.md").exists()

    def test_methodology_exists(self):
        assert (ROOT / "docs" / "methodology_summary.md").exists()

    def test_formalization_grammar_exists(self):
        assert (ROOT / "docs" / "formalization_grammar.md").exists()
