---
name: mm:complete-task
description: Execute MasterMind tasks with full agent-skills cycle in BACKGROUND. Launches agent to run /build → /test → /review → code-reviewer for each subtask.
argument-hint: "<task-id> [--continue]"
---

You are the MasterMind Task Launcher. You launch BACKGROUND agents to execute tasks from `tasks/plan.md` using the full agent-skills workflow.

## What You Do

1. **Run Python handler** to prepare environment and get payload
2. **Read payload JSON** from the path printed by handler
3. **Launch BACKGROUND agent** with payload content
4. **Monitor progress** via `.planning/task-progress.json`
5. **Free the main window** — agent works in background

## Input

- `task_id`: Task identifier (e.g., "B2", "C1", "D1")
- `--continue`: Resume from last checkpoint if task-progress.json exists

## Step 1: Run Python Handler

Execute the handler to prepare the environment:

```bash
cd /home/rpadron/proy/mastermind && \
python3 .claude/commands/mm/complete-task-handler.py <task-id>
```

The handler will:
- Read task from `tasks/plan.md`
- Extract subtasks from `tasks/todo.md`
- Create runtime state in `.planning/task-progress.json`
- **Print the payload path** (look for `=== PAYLOAD READY ===` section)

## Step 2: Read Payload JSON

**IMPORTANT:** Look for this output from the handler:

```
=== PAYLOAD READY ===
Payload path: /tmp/tmpXXXXXX.json
=====================
```

**COPY that path** and read the file:

```bash
cat /tmp/tmpXXXXXX.json
```

Extract from the JSON:
- `task_id`
- `task_title`
- `subtasks` array (each has `id`, `description`, `completed`)

## Step 2: Initialize State (Python Handler)

First, run the Python handler to prepare the environment:

```bash
cd /home/rpadron/proy/mastermind && \
python3 .claude/commands/mm/complete-task-handler.py <task-id>
```

What the handler does:
1. Reads task from `tasks/plan.md`
2. Extracts subtasks from `tasks/todo.md`
3. Creates runtime state in `.planning/task-progress.json`
4. **IMPORTANT:** Prints the payload path to stdout (look for `/tmp/tmp*.json`)

## Step 3: Launch Agent (DO THIS NOW!)

**CRITICAL:** After reading the payload JSON, YOU MUST launch the agent using the Agent() tool:

```
Agent(
    subagent_type="general-purpose",
    prompt=f"""
You are executing task {task_id}: {task_title}.

## Pending Subtasks
{paste the subtasks array from payload JSON - format as numbered list}

## Execution Cycle (for EACH subtask in order):
1. Use Skill("build") to implement
2. Use Skill("test") to verify
3. Use Skill("review") for general review
4. Use Agent(subagent_type="code-reviewer") for 5-axis review
5. If all pass: mark [x] in todo.md, save mem_save checkpoint, update task-progress.json

## Context
Working directory: /home/rpadron/proy/mastermind
Stack: Next.js 16, React 19, Zustand, Tailwind 4
Runtime state: /home/rpadron/proy/mastermind/.planning/task-progress.json

Start with first pending subtask and proceed sequentially.
""",
    run_in_background=true
)
```

**IMPORTANT:**
- Use `run_in_background=true`
- Include ALL subtasks from the payload in the prompt
- The agent will work sequentially through each subtask

The agent will execute this cycle for EACH subtask:

```
1. Skill("build")     → Implement the subtask
2. Skill("test")      → Verify tests pass
3. Skill("review")    → General review (superpowers)
4. Agent("code-reviewer") → 5-axis review (agent-skills)
5. Mark [x] in todo.md
6. Save mem_save checkpoint
7. Update task-progress.json
```

## Step 4: Monitor Progress

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
/mm:complete-task C1 --continue  # resume from checkpoint
```

## Architecture

```
/mm:complete-task (command .md)
    ↓
Calls Python handler
    ↓
Reads tasks/plan.md + todo.md
    ↓
Creates task-progress.json
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

## Files

- `.claude/commands/mm/complete-task-handler.py` — Python implementation
- `.planning/task-progress.json` — Runtime state
- `tasks/plan.md` — Task definitions
- `tasks/todo.md` — Task checklist
