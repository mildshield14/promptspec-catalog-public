# PromptSpec Terminology

This document defines the canonical vocabulary used in the **public PromptSpec Pattern Catalog**. It covers only the concepts present in this artifact. The broader PromptSpec model (pattern realization and composition) is defined in the associated publication.

## Core Entities

### PatternCatalog
A controlled, versioned collection of **PatternDefinition** records. The catalog is the single source of truth for pattern metadata.

### PatternDefinition
One reusable prompt pattern derived from prompt-engineering literature. Pattern definitions in this catalog are taxonomy entries, not empirically observed corpus findings. Each definition includes:
- **id**: Stable machine-readable identifier (e.g., `pat_persona`)
- **name**: Human-readable canonical name (e.g., `Persona`)
- **description**: What the pattern does
- **category**: High-level grouping (e.g., `REASONING`, `OUTPUT_CONTROL`)
- **subcategory**: Finer-grained classification
- **componentTypes**: The prompt component type(s) the pattern relates to (see below)
- **detectionInstruction**: Heuristic for identifying this pattern in a prompt
- **placeholderExample**: A templated illustration of the pattern, using `{PLACEHOLDER}` slots
- **example**: A concrete, generic worked illustration of the pattern
- **notes**: Additional context or caveats

> All `placeholderExample` and `example` values are **generic, illustrative** examples drawn from the source taxonomy (e.g., translation, simple arithmetic). They are not production prompts and contain no corpus data.

## ComponentType

A `componentType` denotes a structural section of a prompt template. Each pattern is mapped to the component type(s) it relates to.

| Component Type | Description |
|----------------|-------------|
| `PROFILE_ROLE` | Sets the model's identity, persona, or voice |
| `DIRECTIVE` | The primary task instruction or command |
| `CONTEXT` | Background information or reference data |
| `WORKFLOW` | Multi-step procedures or reasoning chains |
| `EXAMPLES` | Demonstration input-output pairs |
| `OUTPUT_FORMAT` | Schema or format constraints on the response |
| `CONSTRAINTS` | Verification rules or negative constraints |

> **Scope note:** This catalog records *which* component type(s) each pattern relates to. The **binding semantics** — whether a pattern is *primary in*, *modifies*, or *spans* those components (the `PRIMARY_IN` / `MODIFIES` / `SPANS` distinction) — are part of the broader PromptSpec metamodel and are defined in the associated publication, not in this public catalog.

## Pattern Categories

| Category | Description |
|----------|-------------|
| `IN_CONTEXT_LEARNING` | Patterns that control whether and how examples are provided |
| `REASONING` | Patterns that structure the model's reasoning process |
| `OUTPUT_CONTROL` | Patterns that shape the format, style, or verification of output |
| `CONTEXT_CONTROL` | Patterns that manage what context the model attends to |
| `META_DIRECTIVES` | Patterns that modify the interaction model or meta-level behavior |
