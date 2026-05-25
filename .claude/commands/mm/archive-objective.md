---
name: mm:archive-objective
description: Archive a completed objective package from .planning/changes/ to .planning/archive/objectives/.
argument-hint: "[--objective <slug>] [--summary-only]"
---

# /mm:archive-objective

Archive a **completed** objective package from:

```text
.planning/changes/<objective>/
```

to:

```text
.planning/archive/objectives/<objective>/
```

## Usage

```bash
/mm:archive-objective --objective project-state-mvp
/mm:archive-objective --summary-only --objective project-state-mvp
```

If omitted, `--objective` is inferred from `.planning/HANDOFF-CURRENT.md` or the
single active directory under `.planning/changes/`.

In normal flow, if there is exactly one active objective package, you can simply run:

```bash
/mm:archive-objective
```

## What it validates

Before moving anything, the handler verifies the objective is truly complete:

- all required objective files exist
- `execution-state.json` exists and all root tasks are `completed`, **or**
- the objective handoff proves completion
- if `.planning/task-progress.json` is still pointing at this objective, its active
  subtasks must also be fully completed

If that proof is missing, archiving fails.

## Protocol (For Assistant)

When user executes `/mm:archive-objective [--objective <slug>] [--summary-only]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/archive-objective-handler.py [options]
```

### Step 2: Parse Handler Output

Look for:

- `STATUS: PASSED` → archive succeeded or is archive-safe
- `STATUS: FAILED` → objective is not safe to archive

### Step 3: Notify User

On success:

```text
✅ Objective archived
📦 Moved to .planning/archive/objectives/<objective>/
```

On `--summary-only`:

```text
✅ Objective is archive-safe
```

## Files

- `.claude/commands/mm/archive-objective-handler.py`
- `.planning/changes/<objective>/execution-state.json`
- `.planning/archive/objectives/<objective>/`
