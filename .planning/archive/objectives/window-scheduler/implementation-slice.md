# Implementation Slice — window-scheduler

## Goal

Define the first coding slice for `window-scheduler` using the existing SQLAlchemy models as the foundation and keeping the work small, testable, and core-only.

## Existing foundation

Already present:

- `apps/api/mastermind_cli/window_scheduler/models/backend_session.py`
- `apps/api/mastermind_cli/window_scheduler/models/availability_state.py`
- `apps/api/mastermind_cli/window_scheduler/models/run_policy.py`
- `apps/api/mastermind_cli/window_scheduler/models/scheduler_event.py`
- `apps/api/mastermind_cli/window_scheduler/models/scheduler_checkpoint.py`
- `apps/api/mastermind_cli/window_scheduler/database/base.py`
- `apps/api/mastermind_cli/window_scheduler/database/session.py`

Missing implementation seam:

- repositories over the models
- invariant enforcement helpers/service layer
- focused tests for schema and orchestration invariants

## First coding slice

### Slice WS-01 — persistence + invariant enforcement

Implement the minimum path needed to persist and validate scheduler state transitions:

1. repository layer for the five entities
2. a small service/validator layer for switch/checkpoint invariants
3. deterministic tests covering the contract

This slice should **not** implement provider heuristics, retry scheduling logic, or reporting.

## Proposed file changes

| File | Action | Why |
|---|---|---|
| `apps/api/mastermind_cli/window_scheduler/repositories/backend_sessions.py` | Create | CRUD/list access for backend inventory |
| `apps/api/mastermind_cli/window_scheduler/repositories/availability_states.py` | Create | Persist and fetch observed backend availability |
| `apps/api/mastermind_cli/window_scheduler/repositories/run_policies.py` | Create | Load explicit run policies |
| `apps/api/mastermind_cli/window_scheduler/repositories/scheduler_events.py` | Create | Append audit events and query recent run history |
| `apps/api/mastermind_cli/window_scheduler/repositories/scheduler_checkpoints.py` | Create | Create/fetch resumable checkpoints |
| `apps/api/mastermind_cli/window_scheduler/repositories/__init__.py` | Modify | Export repository types |
| `apps/api/mastermind_cli/window_scheduler/service.py` | Create | Minimal orchestration-safe API for checkpoint-then-switch validation |
| `apps/api/mastermind_cli/window_scheduler/validators.py` | Create | Explicit invariant checks with descriptive `ValueError`s |
| `apps/api/tests/window_scheduler/test_models.py` | Create | Model-level invariant and persistence tests |
| `apps/api/tests/window_scheduler/test_service.py` | Create | TDD-first switch/checkpoint behavior tests |

## Service scope

The first service surface should stay minimal:

- `record_checkpoint(...)`
- `record_event(...)`
- `record_backend_switch(...)`
- `get_latest_checkpoint(...)`

`record_backend_switch(...)` must:

1. require an explicit run policy to exist
2. require a checkpoint id before persisting `backend_switch`
3. fail with a descriptive `ValueError` when invariants are violated

## TDD plan

Write tests first for:

1. `backend_switch` without `checkpoint_id` → fails
2. checkpoint without `next_step_summary` → fails
3. reset estimate with timestamp but missing source/confidence → fails
4. valid checkpoint then valid switch → passes and persists both records
5. missing run policy for switch → fails fast

After those pass, expand only if the slice still feels minimal.

## Non-goals for WS-01

- eligibility engine
- automatic backend selection
- retry scheduling policy
- resume reconstruction
- morning reports/UI

Those belong to later slices after persistence and invariants are proven.

## T3 Completion Check

- [x] First implementation slice is identified
- [x] Follow-on items are explicitly deferred
- [x] The package is handoff-ready for coding with TDD
