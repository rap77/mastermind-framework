# 53 - Strategy Vault Canonical Projection Gaps

## Goal

Document the remaining gaps to replace the legacy `execution_history` SQLite read model with a canonical Strategy Vault projection built from `project_state`.

---

## Executive Summary

`execution_history` should not be migrated as write-side truth.

It should be replaced by a read model assembled from:

- `ps_tasks`
- `ps_task_runs`
- checkpoints
- telemetry
- artifact snapshots

The list view (`/api/executions/history`) is already close to rebuildable from canonical data.

The detail view (`/api/executions/{id}`) still has real gaps.

---

## What Already Maps Cleanly

### Execution list / summary fields

These can be derived now:

| Response field | Canonical source |
|---|---|
| `id` | `ps_task_runs.run_id` |
| `task_id` | `ps_task_runs.task_id` |
| `brief` | `ps_tasks.metadata.brief` |
| `status` | `ps_task_runs.status` |
| `created_at` | `ps_task_runs.started_at` |
| `duration_ms` | derived from `started_at` / `ended_at` |
| `brain_count` | derived or temporarily metadata-backed |

### Implication

`GET /api/executions/history` is the next safe canonical migration slice.

---

## Remaining Gaps

### Gap 1 — no canonical output document convention yet

`Execution.brain_outputs` needs a canonical source.

Current project_state artifact storage has:

- artifact identity
- version metadata
- lineage links

But it does **not** yet provide a clear content-bearing convention for:

- per-brain markdown output
- bundled execution output payloads

### Recommendation

Introduce a canonical artifact convention such as:

- `artifact_type = execution_output_bundle`
- metadata:
  - `run_id`
  - `task_id`
  - `brain_outputs`
  - `format_version`

---

### Gap 2 — no canonical graph snapshot convention yet

`Execution.graph_snapshot` still lacks a defined canonical home.

Best candidates:

- artifact payload
- checkpoint metadata

### Recommendation

Store final replayable graph state as either:

1. artifact type `execution_graph_snapshot`
2. checkpoint `resume_state.graph_snapshot`

Preferred:
- artifact, because replay snapshot is a durable read artifact, not only resume state

---

### Gap 3 — milestones timeline is not modeled directly

`milestones_json` in legacy SQLite is a synthetic timeline.

Canonical project_state currently has:

- checkpoints
- token telemetry
- run timestamps

But no direct “milestone timeline” abstraction.

### Recommendation

Build milestones from:

- `ps_task_runs.started_at`
- checkpoint timestamps
- terminal run state (`ended_at`)

Optional later enhancement:
- add explicit runtime telemetry events for richer milestone reconstruction

---

### Gap 4 — task run repository lacks historical list/pagination helpers

Current `TaskRunsRepository` supports:

- `get_by_id`
- `list_active_by_project`

But not:

- historical listing
- pagination
- newest/oldest sort for Strategy Vault

### Recommendation

Add repository helpers for:

- `list_by_project(project_id, limit, cursor, sort)`
- `count_by_project(project_id)` if needed

---

### Gap 5 — execution ID semantics are transitional

Today many migrated paths still use:

- `task_id == run_id`

This works for transition, but it is not the long-term model.

### Risk

- retries/re-runs cannot be represented cleanly
- Strategy Vault identity semantics remain fuzzy

### Recommendation

For transition:
- use `run_id` as Strategy Vault execution ID

Long-term:
- separate `task_id` and `run_id`
- allow multiple runs per task

---

### Gap 6 — mixed-store history pagination during migration

During transition, some executions may exist only in:

- legacy `execution_history`

while newer ones exist in:

- canonical `ps_task_runs`

### Risk

A naive switch can hide older records or create inconsistent pagination.

### Recommendation

Use a phased transition:

1. project_state-first read path
2. fallback to legacy only when no canonical rows exist for the user scope
3. later perform full projection rebuild and remove legacy store

---

### Gap 7 — ownership remains synthetic, not true project-aware

Strategy Vault is still running under:

- `user-tasks:{user_id}`

This preserves existing contracts, but it is not the final project-aware runtime model.

### Recommendation

Accept this as transitional debt.

Do not block the read-model migration on full project-aware runtime redesign.

---

## Recommended Coverage Order

### Slice A — now

Rebuild `GET /api/executions/history` from:

- `ps_task_runs`
- `ps_tasks`

Keep fallback to legacy SQLite while mixed-state migration remains active.

### Slice B — next

Define canonical artifact/checkpoint conventions for:

- `brain_outputs`
- `graph_snapshot`
- milestones reconstruction

### Slice C — then

Rebuild `GET /api/executions/{id}` on top of canonical projection data.

### Slice D — last

Delete:

- `execution_writer.py`
- `execution_history`
- legacy Strategy Vault read paths

---

## Professional Recommendation

Do **not** port `execution_writer.py` as-is.

Do:

1. migrate the list view first
2. define canonical execution detail conventions
3. rebuild Strategy Vault as a projection over canonical data

## Key Learnings:

1. `ExecutionSummary` is already mostly derivable from canonical task/run state.
2. The hard part is execution detail, not execution list.
3. Strategy Vault should become a projection over canonical runtime data, not a parallel SQLite truth store.
