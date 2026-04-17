---
name: mm:complete-task
description: Execute MasterMind tasks with full agent-skills cycle. Launches task-executor to run /build → /test → /review → code-reviewer → /mm:safe-commit per subtask in BACKGROUND.
argument-hint: "<task-id> [--continue]"
---

# /mm:complete-task

Execute task subtasks using the full agent-skills cycle **in BACKGROUND**.

## Usage

```bash
/mm:complete-task D1          # Start D1 task
/mm:complete-task D2 --continue  # Resume from checkpoint
/mm:complete-task --status    # Show all tasks status
```

## What Happens

1. **Python handler** reads `tasks/plan.md` + `tasks/todo.md`
2. **Checks git** for existing commits (avoids duplicate work)
3. **Generates** `task-progress.json` with pending subtasks
4. **Launches** `task-executor` agent in background
5. **Monitor** with `tail -f .planning/task-progress.json`

## Execution Cycle (per subtask)

```
1. Skill("build")     → Implement with TDD
2. Skill("test")      → Verify tests pass
3. Skill("review")     → General code review
4. Agent(code-reviewer) → 5-axis review (MANDATORY)
5. Skill("mm:safe-commit") → Validate + commit
6. Checkpoint → task-progress.json + Engram
7. Context check → if >75%, exit gracefully
```

## Features

- **Auto-retry**: 3 retries with exponential backoff (30s/60s/120s)
- **Continue on failure**: Marks failed, continues to next subtask
- **Granular checkpoint**: Saves after each subtask
- **Context budget**: Exits at 75% to allow resume
- **Git integration**: /mm:safe-commit validates before commit

## Monitor Progress

```bash
# Real-time progress
tail -f .planning/task-progress.json

# Check agent status
cat .planning/.agent-D1-running
```

## Resume from Checkpoint

If agent exits due to context limit:

```bash
/mm:complete-task D1 --continue
```

Resume reads `task-progress.json` and continues from last checkpoint.

## Architecture

```
/mm:complete-task
    ↓
Python handler (complete-task-handler.py)
    ↓
Reads plan.md + todo.md
    ↓
Checks git for existing commits
    ↓
Generates task-progress.json
    ↓
Launches task-executor agent
    ↓
[Main session FREE]
    ↓
task-executor runs in background:
  build → test → review → code-reviewer → safe-commit
  → checkpoint after each subtask
    ↓
Notification when complete
```

## Files

- `tasks/plan.md` — Task definitions
- `tasks/todo.md` — Checklist
- `.claude/commands/mm/complete-task-handler.py` — Python handler
- `.claude/agents/mm/task-executor/task-executor.md` — Background agent
- `.planning/task-progress.json` — Runtime state

## Example Output

```
INFO: Task D2 initialized
TASK: D2
TITLE: Flow Designer ↔ Simulation Wiring
SUBTASK: D2.1 pending (Create flow-execution-adapter.ts)
SUBTASK: D2.2 pending (Add Simulate button to FlowDesignerCanvas)
GIT: 0/2 subtasks have commits
PENDING: 2 subtasks to execute
INFO: Runtime state: .planning/task-progress.json
INFO: Session ID: sess-20260417-143052
LAUNCH: task-executor
PAYLOAD: {...}
```
