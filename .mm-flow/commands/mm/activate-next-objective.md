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

2. Parse output:

**`STATUS: PASSED`** → package activated. Tell the user:
```
▶ Next: /mm:complete-task <FIRST_TASK_ID> --brief
```

**`STATUS: FAILED` — active objective already exists** → do NOT ask questions. Instead:

a. Read `.mm-flow/planning/changes/<active-slug>/tasks.md` to find the first non-completed task ID.

b. Reply with exactly:
```
⚠ Already active: <active-slug>

▶ Next: /mm:complete-task <FIRST_PENDING_TASK_ID>
```

No extra questions. No offers to read more files. Stop there.

**`STATUS: FAILED` — other reason** → explain the specific error and stop.

3. Never ask clarifying questions after parsing the handler output. Always close with the next command.
