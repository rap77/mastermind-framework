---
name: mm:execute-milestone
description: Execute a complete milestone — discover context → brains → /spec → /plan → /mm:complete-task. Launches milestone-executor agent in BACKGROUND.
argument-hint: "\"<milestone description>\" [--task-id <ID>]"
---

# /mm:execute-milestone

Full autonomous pipeline: from raw description (or existing project audit) to running tasks.

## Usage

```bash
# New project — full spec + plan + execute from scratch
/mm:execute-milestone "User authentication with OAuth2 and JWT"

# Existing project — audit gaps toward MVP, fill, execute
/mm:execute-milestone "Complete MVP for production release"

# Specify first task explicitly (skip auto-detection)
/mm:execute-milestone "Payment processing flow" --task-id D3
```

## Protocol (For Assistant)

When user executes `/mm:execute-milestone <description> [options]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/execute-milestone-handler.py <description> [options]
```

Run from `/home/rpadron/proy/mastermind`

### Step 2: Parse Handler Output

Capture stdout and look for:
- `LAUNCH: milestone-executor` → Agent launch requested
- `PAYLOAD: {...}` → JSON payload for agent
- `ERROR: ...` → Handler error, show to user

### Step 3: Launch Agent

If you see `LAUNCH: milestone-executor` with `PAYLOAD`:

```
Agent(
  subagent_type="milestone-executor",
  prompt=f"""
## Milestone Payload
{parsed_payload_json}

Working directory: {payload.working_directory}

Execute the complete milestone pipeline following the milestone-executor protocol.
""",
  run_in_background=true
)
```

### Step 4: Notify User

```
✅ Milestone-executor launched in background
📋 Pipeline: discover → brains → /spec → /plan → /mm:complete-task
🔔 You'll be notified when task-executor starts running
```

### Special Cases

**Handler ERROR**: Show error to user, suggest next steps.

**`STATUS: TASK COMPLETE`** (if all tasks already done): Report to user, no agent needed.

---

## What Happens

1. **Python handler** reads project state (spec, plan, STATE.md, roadmap, git, etc.)
2. **milestone-executor** runs 5 phases in background:
   - **Phase 1** — Deep context discovery: map codebase, git log, test coverage, open TODOs
   - **Phase 2** — Brain consultation (parallel): Brain #1 (Product) + Brain #7 (Growth) analyze MVP gaps
   - **Phase 3** — Spec generation: `tasks/SPEC.md` with user stories, use cases, architecture, test strategy
   - **Phase 4** — Plan generation: `tasks/plan.md` + `tasks/todo.md` with vertical slices + acceptance criteria
   - **Phase 5** — Task execution: launches `task-executor` for first pending task

---

## Modes

| Mode | Trigger | What happens |
|------|---------|--------------|
| New Project | No spec/plan/STATE.md | Full spec + plan from scratch, then execute |
| Existing Project | Has any of the above | Audit gaps, update spec + plan for what's missing, execute next pending task |

In **Existing Project** mode:
- Already-completed tasks (with git commits) are skipped
- Only gaps vs MVP are added to plan
- Spec is updated, not replaced

---

## Architecture

```
/mm:execute-milestone "description"
    ↓
execute-milestone-handler.py
  → reads project state (fast — file reads only)
  → emits ONE LAUNCH payload
    ↓
milestone-executor agent (BACKGROUND)
  Phase 1: explore codebase + git + tests
  Phase 2: Brain #1 + Brain #7 (parallel)
  Phase 3: Skill("spec") → tasks/SPEC.md
  Phase 4: Skill("plan") → tasks/plan.md + tasks/todo.md
  Phase 5: complete-task-handler.py → task-executor (BACKGROUND)
    ↓
task-executor (BACKGROUND, nested)
  /build → /test → /review → code-reviewer → /mm:safe-commit
  checkpoint after each subtask
```

---

## Files

- `.claude/commands/mm/execute-milestone-handler.py` — Python handler (thin)
- `.claude/agents/mm/milestone-executor/milestone-executor.md` — Pipeline agent
- `tasks/SPEC.md` — Generated/updated specification
- `tasks/plan.md` — Generated/updated implementation plan
- `tasks/todo.md` — Generated/updated task checklist
- `.planning/task-progress.json` — Runtime state (from task-executor)

## Resume

If task-executor exits due to context limit:

```bash
/mm:complete-task <task-id> --continue
```
