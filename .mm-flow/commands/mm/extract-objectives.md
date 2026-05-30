---
name: mm:extract-objectives
description: Extract objectives from roadmap into individual planning packages.
argument-hint: "[--all] [--slug <objective-slug>]"
---

# /mm:extract-objectives

Extract objectives from the roadmap into individual objective packages.

## Usage

```bash
# Extract all objectives from roadmap
/mm:extract-objectives --all

# Extract a specific objective
/mm:extract-objectives --slug mastermind-cli
```

## What It Does

1. Reads `objectives.json` from the roadmap
2. Creates a package directory under `.mm-flow/planning/changes/<slug>/`
3. Populates it with:
   - `requirements.md`
   - `design.md`
   - `tasks.md`
   - `todo.md`
   - `HANDOFF-CURRENT.md`

## Protocol

Execute the handler directly:

```bash
python3 .mm-flow/commands/mm/extract-objectives-handler.py --all
```

---

## Examples

### Extract All Objectives

```bash
/mm:extract-objectives --all
# Creates packages for all objectives in the roadmap
```

### Extract Specific Objective

```bash
/mm:extract-objectives --slug token-cost-quality-telemetry
```

---

## See Also

- `/mm:discover --roadmap` — Generate/update roadmap
- `/mm:activate-next-objective` — Activate recommended objective
