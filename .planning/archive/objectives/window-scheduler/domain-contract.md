# Domain Contract — window-scheduler

## Purpose

Define the canonical domain contract for the reusable Window Scheduler core so future implementation work can proceed without relying on chat history.

## Canonical Entities

### 1. `backend_session`

Represents a backend/account that can be selected by the runtime.

#### Required fields

- `backend_id`
- `provider`
- `account_id`
- `auth_mode`
- `model_family`
- `priority`
- `cost_tier`
- `risk_tier`
- `overnight_allowed`
- `automatic_switch_allowed`
- `human_confirmation_required`
- `enabled`

#### Responsibility

Defines the static capability and policy-relevant attributes of an execution backend.

---

### 2. `availability_state`

Represents the current time-bounded availability of a backend.

#### Required fields

- `backend_id`
- `state`
- `window_started_at`
- `window_exhausted_at`
- `estimated_reset_at`
- `estimation_source`
- `estimation_confidence`
- `last_verified_at`

#### Responsibility

Captures operational state and reset expectations as observations, not guarantees.

---

### 3. `run_policy`

Represents the active execution policy for a run.

#### Required fields

- `run_id`
- `project_id`
- `execution_mode`
- `overnight_mode`
- `max_switches_per_run`
- `allow_paid_api_fallback`
- `require_human_for_high_risk_actions`

#### Recommended fields

- `adapter_id`
- `max_cost_tier`
- `pause_on_low_confidence_reset`

#### Responsibility

Constrains what the scheduler is allowed to do for a specific run.

---

### 4. `scheduler_event`

Represents an auditable scheduler decision or state transition.

#### Required fields

- `event_id`
- `run_id`
- `project_id`
- `type`
- `created_at`

#### Required fields for switch events

- `from_backend`
- `to_backend`
- `reason`
- `checkpoint_id`
- `decision_outcome`

#### Recommended fields

- `task_id`
- `execution_mode`
- `estimated_reset_at`
- `eligibility_basis`
- `next_step_summary`
- `error_code`
- `warning_level`
- `operator_note`

#### Responsibility

Provides the canonical audit trail for window starts, exhaustion, switching, pausing, retry scheduling, and resume behavior.

---

### 5. `scheduler_checkpoint`

Represents the minimum structured state required to continue a task on another backend.

#### Required fields

- `checkpoint_id`
- `run_id`
- `project_id`
- `task_id`
- `step_id`
- `context_summary`
- `next_step_summary`
- `created_at`

#### Recommended fields

- `artifacts`
- `decision_refs`
- `memory_refs`
- `resume_constraints`

#### Responsibility

Preserves continuity across backend changes with minimal but sufficient state.

## Canonical Relationships

- `backend_session.backend_id` ↔ `availability_state.backend_id`
- `run_policy.run_id` ↔ `scheduler_event.run_id`
- `scheduler_event.checkpoint_id` ↔ `scheduler_checkpoint.checkpoint_id`
- `scheduler_event.project_id` ↔ `run_policy.project_id`

## Canonical Invariants

### Invariant 1 — No switch without checkpoint

No `backend_switch` event is valid unless it references a `checkpoint_id`.

### Invariant 2 — No checkpoint without resumable next step

No checkpoint is valid unless `next_step_summary` is present and actionable.

### Invariant 3 — Reset estimates are confidence-scored observations

Any `estimated_reset_at` must record both:

- `estimation_source`
- `estimation_confidence`

### Invariant 4 — Every run is governed by policy

A scheduler action must run under an explicit or inherited `run_policy`.

## Boundary Decisions

### Belongs inside the core contract

- backend inventory shape
- availability state shape
- switching policy constraints
- checkpoint minimum payload
- audit event structure

### Belongs outside the core contract

- provider-specific quota probing heuristics
- adapter-specific domain context
- UI presentation details
- exact provider billing semantics
- full transcripts

## T1 Completion Check

- [x] All five canonical entities are explicitly represented
- [x] Checkpoint-before-switch is explicit
- [x] Reset estimation source/confidence requirements are explicit
- [x] Run policy requirement is explicit
