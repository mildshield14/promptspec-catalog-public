# PromptSpec Pattern Catalog (Public Artifact)

This repository contains the PromptSpec prompt-pattern taxonomy: a machine-readable catalog of 29 prompt-engineering patterns identified through literature review.

> **Scope:** This repository is the **pattern catalog only**. The broader PromptSpec model — including prompt-component structure, pattern-to-component bindings, chunk-level realizations, the queryable graph representation, the DSL compiler, and the corpus analysis — is described in the associated publication and maintained in a separate private repository.

## Start here

**If you just want to read the taxonomy:** [`PATTERN_CATALOG.md`](PATTERN_CATALOG.md) — a human-readable table of all 29 patterns, grouped by category. The machine-readable source of truth is [`catalog/patterns.json`](catalog/patterns.json).

## Overview

The PromptSpec project studies how prompt-engineering patterns combine and recur across real-world prompt templates. This artifact publishes the pattern taxonomy itself, in a clean, reusable form: a human-readable Markdown table for readers and a machine-readable JSON file for reuse.

## Core Concepts

| Concept | Description |
|---------|-------------|
| **PatternCatalog** | A controlled, versioned collection of prompt patterns. |
| **PatternDefinition** | One reusable prompt pattern (e.g., Persona, FewShot, SchemaSpecs). Each pattern has a stable ID, name, description, category, the prompt **component type(s)** it relates to, a detection heuristic, and **illustrative examples** (a templated placeholder form and a concrete worked example). |

> **Related concepts (described in the publication, not included here):** PromptSpec also defines `PatternChunk`, `PromptComponent`, `PatternUse`, `PatternComponentBinding`, and `VariableDefinition`, which describe how patterns are realized and composed within prompt templates. These belong to the broader PromptSpec model and are not part of this public catalog artifact.

## Repository Structure

```
promptspec-catalog-public/
  README.md                       # This file
  PATTERN_CATALOG.md              # Human-readable taxonomy (generated from patterns.json)
  .gitignore                      # Git ignore rules
  requirements-dev.txt            # Dev/test dependencies

  catalog/
    patterns.json                 # 29 PatternDefinition records

  schema/
    pattern.schema.json           # JSON Schema for patterns.json

  docs/
    index.html                    # GitHub Pages catalog browser
    styles.css                    # Website styles
    app.js                        # Website catalog loader and filters
    terminology.md                # Vocabulary and term definitions
    methodology_summary.md        # Research methodology overview
    confidentiality.md            # Data provenance and privacy statement

  scripts/
    validate_catalog.py           # Catalog validation

  tests/
    test_catalog_integrity.py     # Integrity and schema-conformance tests
```

## Patterns

The catalog contains **29 patterns** organized into 5 categories:

| Category | Count | Examples |
|----------|-------|----------|
| IN_CONTEXT_LEARNING | 2 | ZeroShot, FewShot |
| REASONING | 6 | ChainOfThought, StructuredCoT, ComplexCoT, PlanAndSolve, LeastToMost, ReverseCoT |
| OUTPUT_CONTROL | 10 | Persona, Recipe, SchemaSpecs, OutputAutomater, Template, SelfVerification, SelfCalibration, FactCheckList, Reflection, VisualizationGenerator |
| CONTEXT_CONTROL | 1 | ContextManager |
| META_DIRECTIVES | 10 | RefusalBreaker, FlippedInteraction, GamePlay, InfiniteGeneration, QuestionRefinement, RAR, AlternativeApproaches, RE2, InstructionSelection, CognitiveVerifier |

All patterns are derived from published prompt-engineering literature. For the full per-pattern table (definitions, examples, and notes), see [`PATTERN_CATALOG.md`](PATTERN_CATALOG.md), which is generated from `catalog/patterns.json`. If you edit the JSON, regenerate the Markdown so the two stay in sync.

## Website

The `docs/` directory contains a lightweight static catalog browser for GitHub Pages. It loads `catalog/patterns.json` as the source of truth, then renders searchable and filterable pattern cards.

To enable it on GitHub:

1. Open the repository settings.
2. Go to **Pages**.
3. Set the source to the `main` branch and the `/docs` folder.
4. Save the Pages settings.

No build step is required.

## Data Provenance

- All pattern definitions are literature-derived taxonomy entries; they were **not empirically observed** in a prompt corpus.
- **No raw production prompts** are included in this repository.
- **No company names, workflow names, prompt IDs, or proprietary business logic** are included.
- **No corpus frequency statistics** are included.
- The `placeholderExample` and `example` fields are **generic, illustrative** examples (translation, simple arithmetic, etc.) carried over from the source taxonomy — they are **not** production prompts.
- Each pattern records the prompt **component type(s)** it relates to; the binding semantics (`PRIMARY_IN` / `MODIFIES` / `SPANS`) are defined in the publication, not here.

## Validation

```bash
# Validate catalog integrity
python3 scripts/validate_catalog.py

# Run tests
python3 -m pytest tests/ -v
```
