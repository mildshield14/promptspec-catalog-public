#!/usr/bin/env python3
"""Validate PromptSpec formalization scaffolds."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORMALIZATION_DIR = ROOT / "method" / "formalizations"
VALID_CATEGORIES = {
    "IN_CONTEXT_LEARNING",
    "REASONING",
    "OUTPUT_CONTROL",
    "META_DIRECTIVES",
    "CONTEXT_CONTROL",
}

PATTERN_RE = re.compile(r"^pattern\s+([A-Za-z_][A-Za-z0-9_]*)\s*$", re.MULTILINE)
CATEGORY_RE = re.compile(r"^category\s+([A-Z_]+)\s*$", re.MULTILINE)
VARIABLES_RE = re.compile(r"variables\s*\{.*?\}", re.DOTALL)
TEMPLATE_RE = re.compile(r"template\s*```\n?(.*?)```", re.DOTALL)
TAG_RE = re.compile(r"\{\{([#^/])\s*([A-Za-z_][A-Za-z0-9_]*)(?:\s+[^}]*)?\}\}")
TRIGGER_RE = re.compile(r"^trigger\s+(.+?)\s*$", re.MULTILINE)
VALID_TRIGGERS = {
    "ALWAYS",
    "AFTER_ANSWER",
    "ON_REFUSAL",
    "ON_ERROR",
}


def fail_with_errors(errors: list[str]) -> None:
    print("ERROR: formalization validation failed:", file=sys.stderr)
    for error in errors:
        print(f"  - {error}", file=sys.stderr)
    raise SystemExit(1)


def validate_tags(path: Path, template: str, errors: list[str]) -> None:
    stack: list[str] = []
    for match in TAG_RE.finditer(template):
        marker, name = match.groups()
        if marker in {"#", "^"}:
            stack.append(name)
            continue
        if not stack:
            errors.append(f"{path}: closing tag {{{{/ {name}}}}} has no opener")
            continue
        expected = stack.pop()
        if expected != name:
            errors.append(
                f"{path}: closing tag {{{{/ {name}}}}} does not match opener {expected!r}"
            )
    if stack:
        errors.append(f"{path}: unclosed template tag(s): {', '.join(stack)}")


def validate_file(path: Path) -> tuple[str, list[str]]:
    content = path.read_text(encoding="utf-8")
    errors: list[str] = []

    if not content.strip():
        errors.append(f"{path}: file is empty")
        return "invalid", errors

    first_line = content.splitlines()[0] if content.splitlines() else ""
    if not re.match(r"^pattern\s+[A-Za-z_][A-Za-z0-9_]*\s*$", first_line):
        errors.append(f"{path}: first line must be 'pattern <NAME>'")

    if not PATTERN_RE.search(content):
        errors.append(f"{path}: missing pattern declaration")

    category_match = CATEGORY_RE.search(content)
    if not category_match:
        errors.append(f"{path}: missing category declaration")
    elif category_match.group(1) not in VALID_CATEGORIES:
        errors.append(f"{path}: invalid category {category_match.group(1)!r}")

    if not VARIABLES_RE.search(content):
        errors.append(f"{path}: missing variables {{ ... }} block")

    trigger_match = TRIGGER_RE.search(content)
    if trigger_match:
        trigger = trigger_match.group(1).strip()
        is_conditional = trigger.startswith("CONDITIONAL(") and trigger.endswith(")")
        if trigger not in VALID_TRIGGERS and not is_conditional:
            errors.append(f"{path}: invalid trigger {trigger!r}")

    template_match = TEMPLATE_RE.search(content)
    if not template_match:
        errors.append(f"{path}: missing template ``` ... ``` block")
    else:
        validate_tags(path, template_match.group(1), errors)

    return ("invalid" if errors else "valid"), errors


def main() -> None:
    if not FORMALIZATION_DIR.exists():
        fail_with_errors([f"missing formalization directory: {FORMALIZATION_DIR}"])

    total = 0
    valid = 0
    invalid = 0
    errors: list[str] = []

    for path in sorted(FORMALIZATION_DIR.glob("*.promptspec")):
        total += 1
        status, file_errors = validate_file(path)
        if status == "valid":
            valid += 1
        else:
            invalid += 1
        errors.extend(file_errors)

    if errors:
        fail_with_errors(errors)

    print("Formalization validation passed.")
    print(f"  Total .promptspec files: {total}")
    print(f"  Authored and valid: {valid}")
    print(f"  Invalid: {invalid}")


if __name__ == "__main__":
    main()
