# 52 - Phase 2 Tasks/Executions Migration Map

## Goal

Move the active task/execution runtime off the legacy SQLite layer (`state/database.py`) and onto the canonical `project_state` task/task-run model without breaking the existing HTTP contract prematurely.

This document maps:
- current legacy runtime surfaces
- target canonical surfaces
- field-by-field equivalence
- migration gaps
- implementation slices

---

## Executive Summary

Today the backend has **two separate execution domains**:

1. **Legacy runtime SQLite**
   - `executions`
   - `tasks`
   - `execution_history`
   - background task state updates
   - Web/API endpoints for task lifecycle

2. **Canonical project_state read-side / domain model**
   - `ps_tasks`
   - `ps_task_runs`
   - related `telemetry`, `decisions`, `artifacts`, `checkpoints`

The project_state side already has the **right architectural destination**, but the live task runtime still writes and reads from SQLite.

So Phase 2 is not “just replace a table”. It is:

> **re-home the runtime contract of task creation, run status, and execution history into the project_state model, then retire the SQLite runtime path.**

---

## Current Legacy Runtime Surfaces

### 1. Task creation and listing

**Files**
- `apps/api/mastermind_cli/api/routes/tasks.py`
- `apps/api/mastermind_cli/api/services/task_runner.py`

**Current storage**
- `executions` table in `state/database.py`

**Current uses**
- create task records
- list user tasks
- fetch task detail
- drive background execution status transitions

### 2. Execution history / Strategy Vault

**Files**
- `apps/api/mastermind_cli/api/routes/executions.py`
- `apps/api/mastermind_cli/api/services/execution_writer.py`

**Current storage**
- `execution_history` table in `state/database.py`

**Current uses**
- paginated execution history
- execution detail with milestones, brain outputs, graph snapshot

### 3. gRPC runtime entrypoint

**Files**
- `apps/api/mastermind_cli/api/routes/brain_runtime.py`

**Current storage**
- inserts into legacy `executions`

**Current uses**
- accepts dispatch from Rust control plane
- creates pending execution record

---

## Current Legacy SQLite Schemas

### `executions`

Defined in `state/database.py#create_task_schema()`.

| Column | Type | Meaning today |
|---|---|---|
| `id` | TEXT PK | task/execution ID |
| `flow_config` | TEXT | flow name or serialized flow config |
| `brief` | TEXT | sanitized user brief |
| `created_at` | TIMESTAMP | creation time |
| `status` | TEXT | pending/running/completed/failed |
| `user_id` | TEXT | owner/user scope |

### `tasks`

Defined in `state/database.py#create_task_schema()`.

| Column | Type | Meaning today |
|---|---|---|
| `id` | TEXT PK | task row ID |
| `brain_id` | TEXT | brain being executed |
| `status` | TEXT | task state |
| `progress` | TEXT | JSON-ish progress payload |
| `result` | TEXT | JSON-ish output |
| `error` | TEXT | error text |
| `created_at` | TIMESTAMP | created time |
| `updated_at` | TIMESTAMP | updated time |

### `execution_history`

Defined in `state/database.py#create_execution_history_schema()`.

| Column | Type | Meaning today |
|---|---|---|
| `id` | TEXT PK | execution history record ID |
| `task_id` | TEXT UNIQUE | FK-ish link to `executions.id` |
| `brief` | TEXT | brief summary |
| `status` | TEXT | success/error/running |
| `duration_ms` | INTEGER | total elapsed time |
| `brain_count` | INTEGER | total participating brains |
| `created_at` | TIMESTAMP | creation time |
| `milestones_json` | TEXT | timeline milestones |
| `brain_outputs_json` | TEXT | per-brain outputs |
| `graph_snapshot_json` | TEXT | replay graph |

---

## Canonical Destination Model

### `ps_tasks`

**File**
- `apps/api/mastermind_cli/project_state/models/task.py`

| Column | Type | Intended meaning |
|---|---|---|
| `task_id` | PK | canonical task ID |
| `project_id` | FK | project scope |
| `parent_task_id` | nullable | hierarchy/decomposition |
| `title` | string | task label/title |
| `status` | string | canonical task status |
| `priority` | string | importance |
| `owner_type` | nullable | user/brain/system/etc |
| `owner_id` | nullable | owner identity |
| `metadata` | JSON | extensible runtime metadata |
| `constraints` | JSON | execution constraints |
| `completion_criteria` | JSON | done definition |
| `created_at` | ts | created |
| `updated_at` | ts | updated |

### `ps_task_runs`

**File**
- `apps/api/mastermind_cli/project_state/models/task_run.py`

| Column | Type | Intended meaning |
|---|---|---|
| `run_id` | PK | canonical execution/run ID |
| `project_id` | FK | project scope |
| `task_id` | FK | parent task |
| `actor_type` | string | runtime actor kind |
| `actor_id` | string | actor identity |
| `status` | string | run status |
| `started_at` | ts | run start |
| `ended_at` | nullable ts | run end |
| `metadata` | JSON | run metadata |

---

## Equivalence Mapping

## A. `executions` → `ps_tasks` + `ps_task_runs`

The legacy `executions` row is actually overloaded. It represents both:
- the user-visible task
- the active execution record

That should be split.

### Proposed split

| Legacy `executions` | Canonical target | Notes |
|---|---|---|
| `id` | `ps_tasks.task_id` | same stable external task ID |
| `id` | `ps_task_runs.run_id` OR separate derived run id | decision required; recommended: distinct `run_id` |
| `brief` | `ps_tasks.metadata.brief` | preserve raw/sanitized brief in metadata |
| `flow_config` | `ps_tasks.metadata.flow_config` | metadata, not top-level column |
| `status` | `ps_tasks.status` | user-visible task state |
| `status` | `ps_task_runs.status` | active run state |
| `user_id` | `ps_tasks.owner_type=user`, `owner_id=user_id` | preserve ownership |
| `created_at` | `ps_tasks.created_at` | canonical creation timestamp |
| `created_at` | `ps_task_runs.started_at` | if run starts immediately |

### Recommendation

Do **not** reuse the same value for both `task_id` and `run_id` long-term.

Use:
- `task_id` = external/public stable task identifier
- `run_id` = concrete execution attempt identifier

Why:
- allows retries/re-runs
- preserves audit trail of multiple executions for one task
- aligns with `ps_task_runs` semantics

---

## B. `tasks` → either `ps_task_runs.metadata` or telemetry/events

The legacy `tasks` table appears to track per-brain/per-step runtime state rather than user-facing top-level tasks.

### Proposed mapping

| Legacy `tasks` | Canonical target | Notes |
|---|---|---|
| `id` | likely not canonical task ID | probably step/subtask/runtime unit |
| `brain_id` | `ps_task_runs.metadata.brain_id` or telemetry actor field | depends on event model |
| `status` | telemetry event or subrun status | likely not `ps_tasks.status` directly |
| `progress` | telemetry/checkpoint payload | better as event/checkpoint than row overwrite |
| `result` | artifact/checkpoint/output payload | not ideal as top-level task column |
| `error` | telemetry/error event | structured event preferred |
| `created_at` | event/checkpoint timestamp | |
| `updated_at` | event/checkpoint timestamp | |

### Recommendation

Do **not** migrate the legacy `tasks` table 1:1.

Instead classify it as:
- **runtime progress / sub-step state**
- better represented by:
  - checkpoints
  - telemetry events
  - per-brain run metadata

This is a key design point: `tasks` is not the right canonical storage primitive.

---

## C. `execution_history` → `ps_task_runs` + artifacts/checkpoints/telemetry

`execution_history` is a read model for Strategy Vault, not a clean transactional runtime table.

### Proposed mapping

| Legacy `execution_history` | Canonical target | Notes |
|---|---|---|
| `id` | read-model artifact ID OR derived view key | not necessarily `run_id` |
| `task_id` | `ps_task_runs.task_id` | link to canonical task |
| `brief` | `ps_tasks.metadata.brief_summary` | or derived read model |
| `status` | `ps_task_runs.status` | primary source |
| `duration_ms` | derived from `started_at/ended_at` or stored in metadata | |
| `brain_count` | derived from outputs/telemetry | avoid redundant source if possible |
| `created_at` | `ps_task_runs.started_at` or completion time depending UI semantics | decide explicitly |
| `milestones_json` | checkpoints / telemetry timeline | |
| `brain_outputs_json` | artifacts or execution output documents | |
| `graph_snapshot_json` | artifact/checkpoint metadata | |

### Recommendation

Treat `execution_history` as a **read model to be rebuilt**, not as the write-side canonical store.

That means:
- write canonical data to `ps_tasks`, `ps_task_runs`, telemetry/artifacts/checkpoints
- then build `/api/executions/*` responses from that canonical data

---

## HTTP Contract Surfaces That Must Be Preserved First

## `/api/tasks`

### Current create response
- `task_id`
- `status`
- `created_at`

### Current list response
- list of:
  - `id`
  - `brief`
  - `created_at`
  - `status`

### Current detail response
Depends on `SELECT * FROM executions`; current handler should be treated as unstable legacy shape and normalized before migration.

### Rule
Preserve public response shapes first, even if the internal backing store changes.

---

## `/api/executions/history`

Currently returns `ExecutionSummary` with:
- `id`
- `task_id`
- `brief`
- `status`
- `duration_ms`
- `brain_count`
- `created_at`

## `/api/executions/{id}`

Currently returns `Execution` with:
- summary fields above
- `milestones`
- `brain_outputs`
- `graph_snapshot`

### Rule
This contract can remain stable while the backing model shifts to canonical tables + derived view assembly.

---

## Migration Gaps

## Gap 1 — project_state is read-oriented for tasks/runs today

Current repositories support mainly:
- get/list/count
- limited status update

Missing for full runtime migration:
- create task
- create run
- close run
- write run metadata incrementally
- append checkpoints / outputs in canonical write path

## Gap 2 — no canonical write-side replacement yet for `execution_history`

There is no existing direct replacement for:
- milestones timeline
- brain output payload bundle
- graph snapshot replay payload

This likely needs either:
- new artifact/checkpoint conventions
- or a new canonical read-model builder over existing project_state tables

## Gap 3 — user-scoped legacy runtime vs project-scoped canonical state

Legacy routes are keyed by `user_id`.
Canonical project_state is keyed by `project_id`.

This is the biggest semantic migration decision.

### Decision required
For Phase 2, choose one:

1. **Transitional mapping**
   - one synthetic/default project per user/runtime surface
   - fastest migration path

2. **True project-aware runtime**
   - clients must provide/select project_id
   - cleaner architecture, bigger contract shift

### Recommendation
Use **transitional synthetic project mapping** first.

Reason:
- preserves current auth/API contracts
- avoids blocking runtime migration on full product contract redesign
- keeps scope surgical

---

## Recommended Phase 2 Slices

## Slice 2.1 — Introduce canonical runtime write services

Create write-side services for:
- create task
- create run
- update task status
- update run status
- close run

Do not switch routes yet.

**Verify**
- unit tests for write service behavior
- no route changes yet

## Slice 2.2 — Migrate `/api/tasks` create/list/detail to canonical reads/writes

Switch:
- `create_task`
- `create_auto_task`
- `list_tasks`
- `get_task`

Preserve response shape.

**Verify**
- API tests for create/list/detail unchanged externally
- legacy SQLite no longer touched by these routes

## Slice 2.3 — Migrate `task_runner.py`

Switch runtime updates from:
- `executions.status`

to:
- `ps_tasks.status`
- `ps_task_runs.status`
- canonical metadata/checkpoint writes

**Verify**
- background task lifecycle tests
- status transitions preserved

## Slice 2.4 — Rebuild execution history as canonical read model

Replace `execution_history` writes with:
- canonical writes to runs/checkpoints/artifacts
- a response assembler for `/api/executions/*`

**Verify**
- history pagination still works
- execution detail still returns milestones/outputs/graph snapshot

## Slice 2.5 — Migrate gRPC `BrainRuntimeServicer`

Change dispatch path to create:
- canonical task
- canonical run

not legacy `executions`.

**Verify**
- dispatch still returns `task_id`, `status`, `accepted_at_unix_ms`

## Slice 2.6 — Remove runtime dependency on `DatabaseConnection` for task/execution paths

After routes/services switch:
- remove imports of `DatabaseConnection` from task/execution runtime surfaces
- keep SQLite only where still genuinely legacy

---

## File-by-File Action Map

| File | Current role | Phase 2 action |
|---|---|---|
| `api/routes/tasks.py` | create/list/detail on legacy `executions` | migrate to canonical task+run service |
| `api/routes/executions.py` | Strategy Vault read model over `execution_history` | rebuild over canonical data |
| `api/routes/brain_runtime.py` | gRPC dispatch insert into legacy `executions` | migrate to canonical create task/run |
| `api/services/task_runner.py` | lifecycle updates to legacy `executions` + experience logging | migrate status writes to canonical task/run |
| `api/services/execution_writer.py` | writes legacy `execution_history` | replace with canonical projection builder |
| `state/database.py` | schema + persistence substrate | remove task/execution usage once migrated |
| `project_state/repositories/tasks.py` | read-side repo | extend with create/update methods |
| `project_state/repositories/task_runs.py` | active run read-side repo | extend with create/update/close methods |

---

## Suggested Canonical Field Strategy

## Task-level (`ps_tasks`)
Store:
- public task ID
- owner mapping
- brief summary / flow metadata
- current user-visible status
- timestamps

## Run-level (`ps_task_runs`)
Store:
- one row per execution attempt
- start/end timestamps
- actor info
- runtime status
- duration / flow / orchestration metadata in JSON

## Artifacts / checkpoints / telemetry
Store:
- milestones timeline
- graph snapshots
- per-brain outputs
- incremental progress events
- error traces

This split is much closer to the target architecture than the current overloaded SQLite tables.

---

## Key Decisions Recommended Before Coding

1. **Use synthetic/default project mapping during migration**
2. **Separate `task_id` from `run_id`**
3. **Do not migrate legacy `tasks` table 1:1**
4. **Treat `execution_history` as rebuildable projection, not write-side truth**
5. **Preserve external HTTP responses while changing internals**

---

## Immediate Next Step

The first implementation artifact for Phase 2 should be:

> **a canonical runtime write service for project_state tasks and task runs**

That is the minimal enabling layer needed before touching routes.
