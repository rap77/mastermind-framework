---
name: mm:discover
description: Discover roadmap and objective packages for the active MasterMind workflow.
argument-hint: "--roadmap --existing | --existing --objective <name> [\"Objective Name\"] [--quick]"
---

# /mm:discover

Discover and plan using the **objective-package workflow**.

## Usage

```bash
/mm:discover --roadmap --existing      # Build or refresh roadmap of objectives
/mm:discover --existing --objective project-state-mvp "Project State MVP"
/mm:discover --existing --objective small-ui-fix --quick "Add filters to dashboard"
```

## What It Does

### Mode A: Roadmap (`--roadmap --existing`)

**Purpose:** Reconcile intent + planning state + decisions + code reality into a current objective roadmap.

**Materialized output:**
- `.planning/roadmap/objectives.md`
- `.planning/roadmap/dependency-graph.md`
- `.planning/roadmap/objectives.json`
- `.planning/HANDOFF-CURRENT.md` (updated with the next recommended objective)

### Mode B: Objective Package (`--existing --objective <name>`)

**Purpose:** Create one execution-ready package for the named objective/workstream.

**Materialized output:**
```text
.planning/changes/<objective-name>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
```

The global `.planning/HANDOFF-CURRENT.md` is also refreshed to point at the next objective.

---

## Protocol (For Assistant)

## Mandatory Planning Contract

`/mm:discover` is not complete unless it leaves a **structured execution contract** that another model can follow without guessing.

### Required artifacts

1. `.planning/changes/<objective>/requirements.md`
2. `.planning/changes/<objective>/design.md`
3. `.planning/changes/<objective>/tasks.md`
4. `.planning/changes/<objective>/todo.md`
5. `.planning/changes/<objective>/HANDOFF-CURRENT.md`

### `requirements.md` must define

- problem / purpose
- scope vs out-of-scope
- stakeholders
- non-negotiables
- objective-level acceptance criteria

### `design.md` must define

- architecture / boundaries
- technical approach
- dependencies
- validation strategy

### `tasks.md` must define, per task

- task ID and title
- acceptance criteria as checkboxes
- dependency notes when order matters

### `todo.md` must define

- every task mirrored from `tasks.md`
- executable subtasks as checkboxes
- direct task-by-task execution order

### `HANDOFF-CURRENT.md` must define

- current objective
- decisions already made
- blockers / risks
- exact next recommended task
- validation commands

If any of these are missing, another model is likely to drift.

When user executes `/mm:discover [options]`:

### Step 1: Execute Python Handler

```bash
python3 .claude/commands/mm/discover-handler.py [options]
```

Run from the **project root** (auto-detected via `git rev-parse --show-toplevel`)

### Step 2: Parse Handler Output

Capture stdout and look for:
- `MODE: roadmap|objective`
- `TASK: roadmap-planner|objective-packager`
- `PAYLOAD: {...}` → JSON payload for agent
- `ERROR: ...` → Handler error, show to user

### Step 3: Materialize outputs

The handler writes roadmap/objective artifacts locally immediately.

### Step 3.5: Validate Discovery Contract

Before considering discovery complete, validate the generated artifacts:

```bash
python3 .claude/commands/mm/discover-contract-check.py
```

If validation fails, discovery is NOT complete — fix the missing artifacts/sections first.

### Step 4: Notify User

```
✅ Discovery artifacts materialized
📊 Results saved to `.planning/roadmap/` or `.planning/changes/<objective>/`
🔔 Validate with `/mm:discover-contract-check`
```

---

## Flags

| Flag | Description |
|------|-------------|
| `--existing` | Audit existing project instead of new idea |
| `--mode=fast` | Quick discovery (15 min) |
| `--mode=deep` | Deep analysis (60 min) |
| `--roadmap` | Build/refresh objective roadmap (requires `--existing`) |
| `--objective <name>` | Create/update planning package for one objective |
| `--quick` | Lighter/faster objective package generation (requires `--objective`) |

---

## Examples

### Existing Project / Objective Flow

```bash
# Refresh roadmap from current repo state
/mm:discover --roadmap --existing

# Create/update one objective package
/mm:discover --existing --objective artifact-versioning-and-lineage "Artifact Versioning and Lineage"

# Faster objective packaging
/mm:discover --existing --objective small-ui-fix --quick "Add dashboard filters"
```

---

## Architecture

```text
/mm:discover --roadmap --existing
    ↓
.planning/roadmap/objectives.md
    ↓
/mm:discover --existing --objective <slug> "Objective Name"
    ↓
.planning/changes/<objective>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
    ↓
/mm:discover-contract-check --objective <slug>
    ↓
/mm:complete-task <TASK_ID>
    ↓
/mm:archive-objective --objective <slug>
```

---

## Files

- `.claude/commands/mm/discover-handler.py` — Python handler
- `.planning/roadmap/objectives.md` — Current roadmap
- `.planning/changes/<objective>/requirements.md`
- `.planning/changes/<objective>/design.md`
- `.planning/changes/<objective>/tasks.md`
- `.planning/changes/<objective>/todo.md`
- `.planning/changes/<objective>/HANDOFF-CURRENT.md`

---

## Integration with agent-skills

**Complete flow:**

```text
/mm:discover --roadmap --existing
    ↓
/mm:discover --existing --objective <slug>
    ↓
/mm:discover-contract-check --objective <slug>
    ↓
/mm:complete-task <TASK_ID>
    ↓
/mm:archive-objective --objective <slug>
```

## Legacy note

Older global artifacts may still exist in repository history, but they are
**not** the active workflow for new execution. The active path is:
roadmap → objective package → execution → archive.

---

## Brain Integration

**Brain #1 (Product Strategy):**
- What problem are we solving?
- For whom? (User Personas)
- MVP vs v1? (MoSCoW)
- Non-negotiables?

**Brain #4 (Backend):**
- Backend tech stack
- API design
- Database choice

**Brain #5 (Frontend):**
- Frontend tech stack
- UI/UX considerations
- Component architecture

**Brain #7 (Growth/Data):**
- Validation of plan
- Success criteria quality
- Risk assessment
