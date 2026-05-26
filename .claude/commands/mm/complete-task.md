---
name: mm:complete-task
description: Execute MasterMind tasks with full agent-skills cycle. Launches task-executor to run /build → /test → /review → code-reviewer → /mm:safe-commit per subtask in BACKGROUND.
argument-hint: "<task-id> [--continue|--brief]"
---

# /mm:complete-task

Execute objective-package task subtasks using the full agent-skills cycle **in BACKGROUND**.

## Usage

```bash
/mm:complete-task D1          # Start D1 task
/mm:complete-task D2 --continue  # Resume from checkpoint
/mm:complete-task D2 --brief  # Print the exact brief another model should follow
/mm:complete-task --status    # Show all tasks status
```

## Protocol (For Assistant)

When user executes `/mm:complete-task <task-id> [options]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/complete-task-handler.py <task-id> [options]
```

Run from the **project root** (auto-detected via `git rev-parse --show-toplevel`)
or explicitly:

```bash
cd "$(git rev-parse --show-toplevel)" && \
python3 .claude/commands/mm/complete-task-handler.py <task-id> [options]
```

### Step 2: Parse Handler Output

Capture stdout and look for:
- `LAUNCH: task-executor` → Agent launch requested
- `PAYLOAD: {...}` → JSON payload for agent
- `STATUS: TASK COMPLETE` → All done, no agent needed
- `ERROR: ...` → Handler error, show to user

### Step 3: Launch Agent (if payload present)

If you see `LAUNCH: task-executor` with `PAYLOAD`:

```
Agent(
  subagent_type="task-executor",
  prompt=f"""
## Task Payload
{parsed_payload_json}

Working directory: {payload.working_directory}
Stack: {payload.stack}

Execute the pending subtasks sequentially following the task-executor protocol.
""",
  run_in_background=true
)
```

### Step 4: Notify User

```
✅ Task-executor launched in background
📊 Monitor: tail -f .planning/task-progress.json
🔔 You'll be notified when complete
```

### Special Cases

**`--status` flag**: Show handler output directly, don't launch agent.

**`--brief` flag**: Print the exact handoff brief for another model. Use this instead of manually writing a long prompt.

**`STATUS: TASK COMPLETE`**: Handler syncs `todo.md` from the durable ledger. No agent needed.

**Handler ERROR**: Show error to user, suggest next steps.

## What Happens

1. **Python handler** reads the active objective package under `.planning/changes/<objective>/`
2. **Checks git** for existing commits (avoids duplicate work)
3. **Generates** `task-progress.json` with pending subtasks
4. **Launches** `task-executor` agent in background
5. **Monitor** with `tail -f .planning/task-progress.json`
6. **Emits** a `MODEL_BRIEF` block so another model can resume with the right context

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

## Continuation Contract

`/mm:complete-task` is the execution phase of an already-planned task. It must:

1. read `.planning/changes/<objective>/tasks.md`
2. read `.planning/changes/<objective>/todo.md`
3. respect dependency ordering
4. execute only the pending subtasks of the requested task
5. validate before marking progress
6. leave resumable state for the next model/session

If the plan is ambiguous or contradictory, stop and escalate instead of redesigning the architecture mid-execution.

## Architecture

```
/mm:complete-task
    ↓
Python handler (complete-task-handler.py)
    ↓
Reads objective `tasks.md` + `todo.md`
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

- `.planning/changes/<objective>/tasks.md` — Objective-scoped task definitions
- `.planning/changes/<objective>/todo.md` — Objective-scoped execution checklist helper
- `.planning/changes/<objective>/execution-state.json` — Durable execution ledger for the objective
- `.claude/commands/mm/complete-task-handler.py` — Python handler
- `.claude/agents/mm/task-executor/task-executor.md` — Background agent
- `.planning/task-progress.json` — Runtime state for the active task/session

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
