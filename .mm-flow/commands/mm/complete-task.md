---
name: mm:complete-task
description: Execute MasterMind tasks with full agent-skills cycle. Launches task-executor to run /build → /test → /review → code-reviewer → /mm:safe-commit per subtask in BACKGROUND.
argument-hint: "<task-id> [--continue|--brief]"
---

# /mm:complete-task

Execute objective-package task subtasks using the full agent-skills cycle **in BACKGROUND**.

## Usage

```bash
/mm:complete-task D1                 # Start D1 task (brief auto-injected into agent)
/mm:complete-task D2 --continue      # Resume from checkpoint
/mm:complete-task --brief D2         # Preview the brief before executing (dry-run)
/mm:complete-task --status           # Show all tasks status
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
- `MODEL_BRIEF_START` ... `MODEL_BRIEF_END` → Extract everything between these markers as `model_brief`
- `LAUNCH: task-executor` → Agent launch requested
- `PAYLOAD: {...}` → JSON payload for agent
- `STATUS: TASK COMPLETE` → All done, no agent needed
- `ERROR: ...` → Handler error, show to user

### Step 3: Launch Agent (if payload present)

If you see `LAUNCH: task-executor` with `PAYLOAD`, inject the extracted `model_brief` into the agent prompt:

```
Agent(
  subagent_type="task-executor",
  prompt=f"""
## Execution Brief
{model_brief}

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

### Step 5: On Task-Notification received

When the background agent completes and you receive its result:

1. Parse the agent result for the `NEXT_COMMAND:` line.
2. Show the user:

```
✅ <task_id> complete — <n>/<total> subtasks
➡️  Next: <NEXT_COMMAND value>
```

If `NEXT_COMMAND` is missing from the result, run `python3 .claude/commands/mm/complete-task-handler.py --status` to determine it yourself using the same logic:
- Subtask still pending → `/mm:complete-task <task_id> --continue`
- Next task pending → `/mm:complete-task <next_task_id>`
- All tasks done → `/mm:archive-objective <objective_slug>`

**Never end a task-notification response without showing the next command.**

### Special Cases

**`--status` flag**: Show handler output directly, don't launch agent.

**`--brief <TASK_ID>` flag**: Dry-run preview — prints the exact brief the agent will receive without launching execution. Use to review before committing to a run.

**`STATUS: TASK COMPLETE`**: Handler has verified exact durable completion and the acceptance projection in `tasks.md`, then syncs derived artifacts. No agent needed.

**Handler ERROR**: Show error to user, suggest next steps.

**Malformed `execution-state.json`**: Normal start, resume, checkpoint, reconcile, and status commands fail closed without rewriting state or projections. Only explicit `--resync-objective <objective>` may salvage valid fields and rebuild malformed durable state.

**Artifact containment**: `tasks.md`, `todo.md`, `execution-state.json`, and `HANDOFF-CURRENT.md` must resolve inside their objective directory. Symlink escapes fail before reads or writes.

**Topology migration**: Refined executable packages declare exactly one non-empty `### Execution Subtasks` block per root with unique `<TASK>.<number>` IDs, and mark `todo.md` as a projection of `tasks.md`. A legacy package without that marker may derive topology only from explicit child IDs and descriptions scoped under the matching todo root. Every child-like line in that root scope must match the legacy child grammar; mixed valid and malformed/unrecognized children fail the whole parse. No generic children are synthesized. Malformed/duplicate topology, absent topology in both sources, and conflicting dual-source legacy topology fail closed.

**Discovery scaffolds**: Discovery uses the same preferred planning surface as execution. Generic objective output is intentionally non-executable until task-specific `### Execution Subtasks` are refined; placeholder review/implement/validate children are not executable work. Rediscovery preserves an existing objective package, todo, and ledger. Destructive replacement requires a separate explicit flow.

**Agent returns with subtask stuck `in_progress`**: This means the agent ran out of context or failed mid-subtask before calling `--mark-done`. The ONLY valid recovery path is:
```bash
/mm:complete-task <task_id> --continue
```
**NEVER manually edit `execution-state.json`, `todo.md`, `task-progress.json`, or `HANDOFF-CURRENT.md`.** These files are handler-managed — manual edits break checkpoint integrity, corrupt the single-writer invariant, and skip notification triggers. If `--continue` also fails repeatedly, escalate to the user. Never bypass the handler.

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

1. read task/subtask topology and descriptions from `.planning/changes/<objective>/tasks.md`, or from explicit scoped legacy todo children when the plan has no topology block
2. read durable statuses and execution metadata from `.planning/changes/<objective>/execution-state.json`
3. respect dependency ordering
4. execute only the pending subtasks of the requested task
5. validate before marking progress
6. leave resumable state for the next model/session

If the plan is ambiguous or contradictory, stop and escalate instead of redesigning the architecture mid-execution.

## Execution Authority

Authority is ordered and scoped to the selected objective:

1. `tasks.md` owns root-task/subtask topology, order, and descriptions.
2. `execution-state.json` owns durable status and validated execution metadata.
3. `task-progress.json` is session runtime evidence. It may advance a matching durable subtask but cannot regress durable completion.
4. `todo.md`, acceptance checkboxes in `tasks.md`, and handoff files are projections, never independent completion evidence.

On resume, checkpoint mutation, reconcile, reset-stale, or resync, runtime and durable task/subtask sets are normalized exactly to the resolved topology: stale entries are pruned and missing planned entries are materialized as `pending`. Parent status is recomputed from current children. Fresh start, resume, reconcile, and stale reset use caller-owned transactions across runtime, durable state, acceptance, todo, and handoff. A reset with no stale children is byte-for-byte read-only. Resync consumes runtime only when the normal loader accepts it; invalid runtime is removed after successful recovery so later commands are not poisoned. Todo is rendered as one exact deterministic checklist, and duplicate checklist sections fail before mutation.

Resume requires both a valid durable ledger and an existing valid runtime checkpoint; neither one alone authorizes `--continue`. Without runtime, start explicitly without `--continue` or resync first. Legacy todo checkbox state contributes no completion evidence. Generated resume/checkpoint timestamps preserve the runtime's aware or legacy-naive timezone semantics.

Checkpoint mutations snapshot runtime, durable state, acceptance, todo, and objective handoff. Expected reconcile, persistence, acceptance, projection, or readback failure restores all snapshots byte-for-byte and exits nonzero. Initialization seeds durable state successfully before runtime is written or execution is launched. A task is complete only when the durable parent is `completed`, the durable child set exactly equals current planned children, every child is completed, and acceptance, todo, and handoff projections pass readback verification before `TASK COMPLETE` is emitted. Unknown or malformed acceptance checkbox tokens invalidate the whole acceptance block; partial rewrites are forbidden.

Git history is informational only. Matching conventional commit subjects may be displayed as `GIT_INFO`, but commits never mutate runtime, durable status, acceptance, todo, or handoff and can never emit `TASK COMPLETE`.

Every mutating complete-task CLI flow, including status projection, acquires the nonblocking planning lock at `<planning-dir>/.complete-task.lock`. Contention fails controlled and nonzero before state mutation. Help and brief remain read-only and unlocked.

Completion notification metadata is best-effort operational state, not execution truth. Its runtime checkpoint uses atomic replacement. Notification or metadata persistence failures emit a controlled warning, never corrupt runtime JSON, and never roll back verified durable completion.

## Architecture

```
/mm:complete-task
    ↓
Python handler (complete-task-handler.py)
    ↓
Reads objective `tasks.md` + `execution-state.json`
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
