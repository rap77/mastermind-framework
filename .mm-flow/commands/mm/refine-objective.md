---
name: mm:refine-objective
description: Refine a discovery scaffold into a task-specific executable objective package.
argument-hint: "--objective <slug> (--brief|--sync)"
---

# /mm:refine-objective

Convert one discovery package from a generic scaffold to a task-specific execution plan.

## Usage

```bash
/mm:refine-objective --objective context-window-management --brief
/mm:refine-objective --objective context-window-management --sync
```

## Protocol (For Assistant)

1. First run:

   ```bash
   python3 .claude/commands/mm/refine-objective-handler.py \
     --objective <slug> --brief
   ```

2. Inspect the canonical sources and runtime package named by `MODEL_BRIEF_START` / `MODEL_BRIEF_END`.
3. Refine `requirements.md`, `design.md`, and `tasks.md` with the actual scope using `apply_patch`.
4. Add exactly one nonempty `### Execution Subtasks` block to every root task. Each child must be `- T1.1: specific work description` (and similarly for each root), not generic review, implement, or validation placeholder text.
5. Do **not** manually edit `todo.md`, `HANDOFF-CURRENT.md`, `execution-state.json`, or `task-progress.json`. They are handler-managed derived state.
6. Run:

   ```bash
   python3 .claude/commands/mm/refine-objective-handler.py \
     --objective <slug> --sync
   ```

`--sync` is the only handoff to execution. It validates the task-specific package, dependencies, and execution topology, then resynchronizes derived state through `/mm:complete-task`.

On success, run the emitted next command, for example:

```bash
/mm:complete-task T1 --brief
```
