# 45. Hybrid Spec Flow and Rules

## Purpose

This document explains the recommended planning and execution workflow for MasterMind after combining:

- **MasterMind strengths**: brains, handoff, auditability, execution continuity, acceptance verification
- **Kiro-style strengths**: per-objective specs, separated requirements/design/tasks, dependency-aware execution

It is written so that **another model** can learn the workflow and continue work without relying on fragile chat memory.

---

## Core Principle

The system should not rely on a model “remembering what we meant.”

Instead, every active workstream must leave behind a **structured execution contract** that contains:

1. what we are building
2. why it matters
3. how it should be built
4. how it will be validated
5. what exact step comes next

The model follows the contract. The model does not invent the contract while executing.

---

## Recommended Planning Hierarchy

### Level 1 — Project

Example:
- `mastermind`

### Level 2 — Objective / Change / Workstream

Examples:
- `project-state-mvp`
- `project-state-realtime`
- `runtime-window-scheduler`
- `doctrine-store`

This is the main unit of planning and execution.

### Level 3 — Phases within an objective

Examples for `project-state-mvp`:
- read-side foundation
- dashboard MVP
- write-side minimum
- live refresh / realtime
- audit/event hardening

### Level 4 — Tasks

A task should be a concrete deliverable with explicit acceptance criteria.

### Level 5 — Subtasks

Subtasks are the executable checklist used by `/mm:complete-task`.

---

## Recommended Filesystem Model

## Active roadmap

```text
.planning/roadmap/
  objectives.md
  dependency-graph.md
```

## Active objective

```text
.planning/changes/<objective-name>/
  requirements.md
  design.md
  tasks.md
  todo.md
  HANDOFF-CURRENT.md
```

## Archived objective

```text
.planning/archive/<objective-name>/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
  COMPLETION-SUMMARY.md
```

---

## Meaning of Each File

### `requirements.md`

Defines:
- problem statement
- target users / stakeholders
- scope
- out-of-scope
- non-negotiables
- acceptance criteria at the objective/task level

### `design.md`

Defines:
- architecture and boundaries
- data flow
- design decisions
- constraints
- testing strategy
- important tradeoffs

### `tasks.md`

Defines:
- task list
- dependency order
- parallelizable work
- purpose of each task
- likely files / areas touched
- validation commands
- acceptance checklists per task
- exactly one non-empty `### Execution Subtasks` block per root task
- authoritative unique root-task/subtask IDs, order, and descriptions
- execution order

Discovery packages intentionally omit synthetic execution children and remain non-executable scaffolds until explicitly refined with this topology. Discovery and execution use the same preferred planning surface, and normal rediscovery preserves existing refined artifacts and ledgers. During migration, an unmarked legacy package may derive topology only from explicit unique child IDs and non-placeholder descriptions scoped below the matching todo root. Every child-like line inside the selected root must match the legacy grammar; one malformed, duplicated, or unrecognized child invalidates the entire scoped topology. No fallback children are synthesized.

### `execution-state.json`

Defines:
- durable task and subtask status
- validated timestamps, durations, retries, and checkpoint metadata
- objective-scoped execution history

It does not own topology. Its task and subtask sets must match the current `tasks.md` contract exactly.

### `todo.md`

Defines:
- execution-ready checklist mirrored from `tasks.md`
- task/subtask states (`[ ]`, `[~]`, `[x]`)
- dependency hints
- validation hints
- a projected operator view generated from plan topology and durable state

### Execution authority and normalization

The precedence is `tasks.md` topology/descriptions, then `execution-state.json` durable truth, then matching objective-scoped runtime advancement. `todo.md`, acceptance checkboxes, and handoff files are projections.

Resume, checkpoint mutation, reset-stale, reconcile, and resync normalize durable/runtime entries to the exact resolved topology: removed entries are pruned, missing entries become `pending`, and parent state is recomputed. A previously completed parent reopens when a newly planned child is not complete. Fresh start and resume own the outer transaction across runtime, durable state, acceptance, todo, and handoff. Reconcile and stale reset use the same artifact boundary. Any reconcile, save, acceptance, projection, or readback failure restores the original bytes and exits nonzero. A reset with no stale child performs no normalization or projection writes. Resync consumes runtime evidence only through the normal validated loader and removes invalid runtime after successful recovery. Legacy runtimes that omit required primary fields such as `session_id` are rejected rather than interpreted by a weaker loader.

Resync includes the global handoff in its transaction, reprojects acceptance after parent recomputation, and never deletes or normalizes runtime owned by another objective. Status validates every objective before writing and projects all objective todo/handoff files in one rollback boundary. Resume requires a valid durable ledger and fails read-only with a resync instruction when it is absent. Runtime timestamps must be parseable ISO datetimes with compatible offset-awareness.

Completion and prior-task acceptance require an exact durable child set with every child and parent `completed`, plus written and read-back-verified acceptance, todo, and handoff projections. `TASK COMPLETE` is emitted only after those checks. Any malformed checkbox-like criterion invalidates the complete acceptance block and prevents partial projection. Checkpoint persistence/projection failures restore runtime, ledger, acceptance, todo, and objective handoff bytes; durable seeding precedes runtime initialization and launch.

Todo is an exact deterministic projection of current topology and durable status, not a patch over stale lines. Exactly one `## Execution Checklist` is allowed; duplicates fail before mutation. Objective artifact paths (`tasks.md`, `todo.md`, `execution-state.json`, `HANDOFF-CURRENT.md`) must resolve within the objective directory; symlink escapes are rejected before I/O.

For unmarked legacy packages, todo contributes IDs and descriptions only. Checkbox state never seeds durable completion; new entries start pending unless valid durable or matching runtime evidence advances them.

Git commits are never execution evidence. Exact objective-scoped conventional subjects may be reported informationally, but no Git history path can promote runtime or durable state.

All mutating complete-task CLI modes serialize through a nonblocking `fcntl.flock` file under the active planning directory. Lock contention fails before mutation. Since status can project todo/handoff, it is locked; brief and help remain unlocked. Explicit `--continue` requires an existing runtime checkpoint and never falls through to fresh start.

Notification delivery and `completion_notified_at` are best-effort operational metadata, not execution truth. Metadata persistence uses atomic replacement; failure warns without traceback or invalid JSON and does not roll back verified durable completion.

### `HANDOFF-CURRENT.md`

Defines:
- current objective
- decisions already made
- blockers / risks
- exact next recommended task
- validation commands
- anything a new model must know before resuming

This file is the **operational bridge** between sessions/models.

---

## Workflow Lifecycle

## Step 1 — Discover the roadmap

Goal:
- identify the major objectives for the project
- order them by value and dependency
- avoid generating full specs for every future objective too early

Recommended output:
- `.planning/roadmap/objectives.md`
- `.planning/roadmap/dependency-graph.md`

### Rule
Do **not** fully spec every future objective at once.

Create a roadmap of objectives, but fully expand only the **active** objective.

---

## Step 2 — Select one active objective

Example:
- `project-state-mvp`

Only one objective should be the main active planning target at a time unless there is an explicit reason to run multiple tracks in parallel.

---

## Step 3 — Generate the objective package

For the active objective, generate:

```text
.planning/changes/<objective-name>/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
```

### Rule
Execution should not begin until this package is structurally complete.

---

## Step 4 — Validate the contract

Run the discovery contract validator before execution.

Current command:

```bash
/mm:discover-contract-check
```

Current script behind it:

```bash
python3 .mm-flow/commands/mm/discover-contract-check.py --objective <objective>
```

### What it validates

It checks the active per-objective layout:

- `.planning/changes/<objective>/requirements.md`
- `.planning/changes/<objective>/design.md`
- `.planning/changes/<objective>/tasks.md`
- `.planning/changes/<objective>/todo.md`
- `.planning/changes/<objective>/HANDOFF-CURRENT.md`

---

## Step 5 — Execute one task

Use:

```bash
/mm:complete-task <TASK_ID>
```

The task must belong to one active objective package under `.planning/changes/`.

This is the implementation phase.

### Execution rules

The executing model/agent must:

1. read the plan
2. read the todo/checklist
3. respect task dependencies
4. implement only the pending subtasks for the selected task
5. run tests and validation
6. checkpoint progress
7. update execution state
8. let the handler project completion state from the ledger

### Important note

`/mm:complete-task` is ledger-driven.

The current handler supports:
- runtime state
- resumption
- todo synchronization
- handoff synchronization
- task gating based on durable execution state

---

## Step 6 — Resume if interrupted

Use:

```bash
/mm:continue-task <TASK_ID>
```

Alias of:

```bash
/mm:complete-task <TASK_ID> --continue
```

### Resume rules

The resuming model must:

1. read the runtime state
2. read the plan and todo again
3. continue from the last checkpoint
4. not re-plan the task unless the plan is invalid

---

## Step 7 — Verify completion

Verification happens at two levels:

### A. Task-level execution verification
Performed by the execution flow through targeted tests, review, and safe-commit.

### B. Objective-level completion review
When all tasks in the objective are done, create a completion summary and archive the objective package.

Current command:

```bash
/mm:archive-objective <objective>
```

Recommended archive result:

```text
.planning/archive/<objective-name>/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
  COMPLETION-SUMMARY.md
```

---

## Step 8 — Move to the next objective

After archiving the completed objective:

1. choose the next objective from the roadmap
2. generate or refresh its package
3. validate it
4. execute it

Current activation command:

```bash
/mm:activate-next-objective
```

Do not manually choose or mark the next objective active before archival.

This prevents the active planning surface from becoming an unmanageable pile of stale specs.

---

## Current State

The active MM command flow now centers on objective packages:

The intended next evolution is:

```text
.planning/changes/<objective-name>/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
```

with a separate roadmap at:

```text
.planning/roadmap/
```

Historical root-level planning artifacts may still exist under archive/legacy
for reference, but they are not part of the active workflow.

---

## Command Semantics

## Current commands

### `/mm:discover`
Used to generate the planning artifacts.

Current reality:
- generates roadmap and per-objective packages
- uses the objective-package contract
- no longer depends on root-level planning files

### `/mm:discover-contract-check`
Validates that discovery produced the minimum structural contract.

### `/mm:complete-task <TASK_ID>`
Executes a concrete task from the active plan.

### `/mm:continue-task <TASK_ID>`
Resumes a previously interrupted task.

---

## Recommended future command model

### Roadmap mode

```bash
/mm:discover --roadmap --existing
```

Proposed output:
- `.planning/roadmap/objectives.md`
- `.planning/roadmap/dependency-graph.md`

### Objective mode

```bash
/mm:discover --objective project-state-mvp --existing
```

Proposed output:

```text
.planning/changes/project-state-mvp/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
```

### Quick mode

```bash
/mm:discover --objective small-ui-fix --quick
```

Same package, but lighter/faster.

### Important note
These future flags are the **recommended direction**, not yet the full implemented behavior today.

---

## Hard Rules for Any Model

Any model continuing work must follow these rules:

1. **Do not work from chat alone**
   - always read the active planning artifacts first

2. **Do not execute on an incomplete discovery**
   - run `/mm:discover-contract-check`

3. **Do not improvise architecture during execution**
   - if the plan is clear, execute it
   - if the plan is broken, replan explicitly

4. **Do not skip acceptance criteria**
   - code compiling is not enough

5. **Do not keep zombie tasks alive forever**
   - if an objective is done, archive it

6. **Do not mix multiple active sources of truth**
   - one roadmap
   - one active objective package
   - one runtime state for the executing task

7. **Do not trust “memory” over artifacts**
   - artifacts are the authority
   - chat is context, not truth

---

## Why This Workflow Exists

Without this workflow, model handoff tends to fail in predictable ways:

- the next model reinterprets the goal
- tasks become too vague
- acceptance criteria are skipped
- stale plans stay mixed with current work
- implementation drifts from architecture
- context is rebuilt from memory instead of state

This workflow exists to make continuation:

- explicit
- auditable
- resumable
- dependency-aware
- multi-model safe

---

## Practical Example

## Roadmap

`objectives.md` says:

1. `project-state-mvp`
2. `project-state-realtime`
3. `project-state-native-audit`

## Active objective

Work on:
- `project-state-mvp`

Generate:

```text
.planning/changes/project-state-mvp/
  requirements.md
  design.md
  tasks.md
  HANDOFF-CURRENT.md
```

Validate.

Execute:

```bash
/mm:complete-task P1
/mm:complete-task P2
/mm:continue-task P2
```

When complete:

```text
.planning/archive/project-state-mvp/
```

Then activate:
- `project-state-realtime`

---

## Summary

The desired MasterMind planning flow is:

1. roadmap of objectives
2. one active objective package
3. explicit contract validation
4. task-by-task execution
5. checkpointed resume
6. acceptance verification
7. archive completed objective
8. activate next objective

This is the safest way to preserve coherence across models, sessions, and long-running work.
