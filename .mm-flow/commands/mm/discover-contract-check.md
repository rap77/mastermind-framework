---
name: mm:discover-contract-check
description: Validate that /mm:discover produced the minimum structured execution contract.
argument-hint: "[--objective <name>]"
---

# /mm:discover-contract-check

Validate that discovery left behind the minimum planning contract required for coherent continuation across models/sessions.

## What it checks

### Required contract
- `.planning/changes/<objective>/requirements.md`
- `.planning/changes/<objective>/design.md`
- `.planning/changes/<objective>/tasks.md`
- `.planning/changes/<objective>/todo.md`
- `.planning/changes/<objective>/HANDOFF-CURRENT.md`

Minimum structure:
- `requirements.md` includes purpose, scope, out-of-scope, non-negotiables, acceptance criteria
- `design.md` includes boundaries, approach, dependencies, validation strategy
- `tasks.md` includes task headings and acceptance checkboxes
- `todo.md` includes executable checkboxes for task execution
- `HANDOFF-CURRENT.md` includes objective, decisions, blockers, next step, validation commands

## Usage

```bash
/mm:discover-contract-check
/mm:discover-contract-check --objective project-state-mvp
```

## Protocol (For Assistant)

When user executes `/mm:discover-contract-check [--objective <name>]`:

### Step 1: Run validator

```bash
python3 .claude/commands/mm/discover-contract-check.py
# or
python3 .claude/commands/mm/discover-contract-check.py --objective <objective-name>
```

Run from the project root.

### Step 2: Return result directly

- If `STATUS: PASSED`, report that the active objective package is structurally ready for execution.
- If `STATUS: FAILED`, show the missing pieces and recommend fixing them before `/mm:complete-task`.

## Interpretation

- `STATUS: PASSED` → the output includes the exact `/mm:complete-task <TASK_ID>` command to run next
- `STATUS: FAILED` → discovery is incomplete; fix artifacts first
