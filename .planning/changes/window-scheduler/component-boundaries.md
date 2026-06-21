# Component Boundaries — window-scheduler

## Purpose

Define the responsibility boundaries and handoff points between the core Window Scheduler components so implementation can start without ambiguity.

## Components

### 1. Provider Registry

**Owns**
- `backend_session` inventory
- enable/disable status
- static backend capability and policy attributes

**Does not own**
- live availability
- switching decisions
- checkpoint persistence

**Primary output**
- candidate backend definitions for eligibility evaluation

### 2. Availability Tracker

**Owns**
- `availability_state`
- observed window start/exhaustion timestamps
- reset estimation source/confidence
- last verification timestamp

**Does not own**
- whether a backend should be chosen
- policy escalation decisions

**Primary output**
- current backend availability observations

### 3. Eligibility Engine

**Owns**
- filtering candidate backends by policy-compatible constraints
- evaluating whether a backend is eligible now

**Inputs**
- `backend_session`
- `availability_state`
- `run_policy`

**Does not own**
- switch ordering
- human escalation
- checkpoint creation

**Primary output**
- eligible backend set with eligibility basis

### 4. Switch Policy Engine

**Owns**
- continue vs switch vs pause vs escalate decision
- switch ordering rules
- retry timing intent when all options are blocked
- max-switch enforcement for a run

**Inputs**
- current backend state
- eligible backend set
- `run_policy`
- task/risk context

**Does not own**
- raw backend inventory
- checkpoint storage details

**Primary output**
- decision outcome:
  - `continue`
  - `switch`
  - `pause_for_user`
  - `retry_scheduled`
  - `all_backends_blocked`

### 5. Checkpoint Manager

**Owns**
- creation of `scheduler_checkpoint`
- capture of minimum resumable context before switching

**Required payload**
- task identity
- current step
- context summary
- next step summary
- relevant artifacts/refs if available

**Does not own**
- backend choice
- retry logic

**Primary output**
- valid checkpoint id and structured resume payload

### 6. Resume Manager

**Owns**
- reconstruction of minimum execution state on the next backend
- rehydration from checkpoint and referenced artifacts

**Does not own**
- deciding whether a switch should happen
- inferring missing checkpoint fields

**Primary output**
- resumable execution package for the next backend

### 7. Audit Logger

**Owns**
- `scheduler_event` persistence
- auditable event trail for starts, exhaustion, switches, pauses, retries, resumes

**Does not own**
- policy decisions
- checkpoint generation

**Primary output**
- append-only scheduler event history

## Decision Flow

1. Provider Registry supplies backend inventory
2. Availability Tracker supplies live observations
3. Eligibility Engine filters candidates
4. Switch Policy Engine decides continue/switch/pause/retry
5. If decision is `switch`, Checkpoint Manager must create checkpoint first
6. Audit Logger records the decision event
7. Resume Manager reconstructs execution on the selected backend

## Hard Boundaries

### Automatic switch boundary

Automatic switching is allowed only when:

- target backend is eligible
- `automatic_switch_allowed` is true
- `run_policy` allows the move
- required human confirmation is false
- a valid checkpoint exists first

### Pause / escalation boundary

The scheduler must pause or escalate when:

- no eligible backend exists
- the target action exceeds risk/cost policy
- high-risk action requires human approval
- reset confidence is too low and policy says pause
- max switches per run has been reached

## Minimum Resume Payload

The Resume Manager requires at least:

- `checkpoint_id`
- `run_id`
- `project_id`
- `task_id`
- `step_id`
- `context_summary`
- `next_step_summary`

Recommended additions:

- `artifacts`
- `decision_refs`
- `memory_refs`
- `resume_constraints`

## Verification-Oriented Criteria

These boundaries should be implementable with deterministic tests:

1. ineligible backends are excluded before switch policy runs
2. switch policy cannot emit `switch` without checkpoint creation succeeding
3. pause/escalate decisions occur when policy or eligibility blocks automatic continuation
4. resume reconstruction fails fast if minimum checkpoint payload is incomplete
5. audit events reflect the final decision outcome, not intermediate guesses

## T2 Completion Check

- [x] Component boundaries are clear and non-overlapping
- [x] Automatic switch vs pause/escalation decision points are explicit
- [x] Minimum resume payload is defined
