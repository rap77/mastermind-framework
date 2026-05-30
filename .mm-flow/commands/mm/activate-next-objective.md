---
name: mm:activate-next-objective
description: Activate the roadmap's recommended next objective automatically.
argument-hint: "[--quick]"
---

# /mm:activate-next-objective

Activate the **recommended next objective** from `.planning/roadmap/objectives.json`
without manually repeating its slug.

## Usage

```bash
/mm:activate-next-objective
/mm:activate-next-objective --quick
```

## What it does

1. Reads `.planning/roadmap/objectives.json`
2. Finds the entry with `recommended_next = true`
3. Fails if another objective package is still active under `.planning/changes/`
4. Materializes the objective package automatically

## Output

Creates:

```text
.planning/changes/<recommended-slug>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
```

## Protocol (For Assistant)

When user executes `/mm:activate-next-objective`:

1. Run:

```bash
python3 .claude/commands/mm/activate-next-objective-handler.py [--quick]
```

2. Parse:
- `STATUS: PASSED` → package activated
- `STATUS: FAILED` → explain why activation was blocked

3. On success, tell the user to continue with:

```bash
/mm:discover-contract-check --objective <slug>
/mm:complete-task <FIRST_TASK_ID> --brief
```
