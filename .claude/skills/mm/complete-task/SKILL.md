---
name: mm:complete-task
description: Execute MasterMind tasks with full agent-skills cycle in BACKGROUND. Launches agent to run /build → /test → /review → code-reviewer for each subtask.
argument-hint: "<task-id> [--continue]"
effort: high
---

You are the MasterMind Task Launcher. You launch BACKGROUND agents to execute tasks from `tasks/plan.md` using the full agent-skills workflow.

## What You Do

1. **Read task details** from `tasks/plan.md` and `tasks/todo.md`
2. **Launch BACKGROUND agent** to execute all pending subtasks
3. **Monitor progress** via `.planning/task-progress.json`
4. **Free the main window** — agent works in background

## Input

- `task_id`: Task identifier (e.g., "B2")
- `--continue`: Resume from last checkpoint if task-progress.json exists

## Step 1: Read Task Details

Read these files BEFORE launching agent:

```bash
cat tasks/plan.md
cat tasks/todo.md
cat .planning/task-progress.json  # if exists (for --continue)
```

Extract:
- Task title and description
- List of pending subtasks (marked `[ ]`)
- Current progress from runtime state

## Step 2: Launch BACKGROUND Agent

Create a payload with the task details and launch a background agent:

```
Agent(
    subagent_type="general-purpose",
    prompt=f"""
You are executing task {task_id}: {task_title}.

## Pending Subtasks
{list of subtasks from todo.md}

## Execution Cycle (for EACH subtask in order):
1. Use Skill("build") to implement
2. Use Skill("test") to verify
3. Use Skill("review") for general review
4. Use Agent(subagent_type="code-reviewer") for 5-axis review
5. If all pass: mark [x] in todo.md, save mem_save checkpoint, update task-progress.json

## Context
Working directory: /home/rpadron/proy/mastermind
Stack: Next.js 16, React 19, Zustand, Tailwind 4

Start with first pending subtask and proceed sequentially.
""",
    run_in_background=true
)
```

## Step 3: Monitor Progress

The agent runs in BACKGROUND. Monitor with:

```bash
tail -f .planning/task-progress.json
```

You'll be notified when the agent completes.

## Final Report

When agent completes notification arrives, summarize:

```
## Task {task_id} Complete ✅

**Agent ran in background**
**Subtasks completed:** {count}/{total}
**Monitor:** tail -f .planning/task-progress.json
```

## Usage

```bash
/mm:complete-task B2      # start new task
/mm:complete-task B2 --continue  # resume from checkpoint (if agent crashed)
```

## Architecture

```
/mm:complete-task (skill)
    ↓
Reads tasks/plan.md + todo.md
    ↓
Launches Agent(general-purpose, run_in_background=true)
    ↓
[Ventana principal LIBRE]
    ↓
Agente ejecuta:
  - /build → /test → /review → code-reviewer (por cada subtarea)
  - Marca [x] en todo.md
  - Guarda checkpoints en Engram
  - Actualiza task-progress.json
    ↓
Notificación cuando termina
```
