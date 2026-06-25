# Design — window-scheduler

## Overview

Window Scheduler is a reusable core capability that manages temporary backend availability across multiple providers, accounts, and models. Its job is to preserve execution continuity while enforcing governance and auditability.

## Approach

### 1. Model the minimum reusable entities first

The first slice should establish only the minimal scheduler entities:

- `backend_session`
- `availability_state`
- `run_policy`
- `scheduler_event`
- `scheduler_checkpoint`

### 2. Enforce checkpoint-before-switch as a hard invariant

The scheduler must not allow `backend_switch` without a checkpoint reference. This is the main continuity guarantee and should be encoded early in the design and validation path.

### 3. Separate eligibility, policy, and persistence concerns

The core design should keep these concerns distinct:

- **eligibility**: which backends can run now
- **policy**: whether the system should continue, switch, pause, or escalate
- **persistence/audit**: what must be recorded for replay and reporting

### 4. Keep adapter details out of the core schema

Provider-specific details such as quota probing or domain constraints should stay outside this slice. The scheduler core should remain reusable and domain-neutral.

## Proposed work breakdown

### Slice A

- codify the canonical entities and invariants
- map relationships between events, policies, checkpoints, and availability

### Slice B

- define eligibility and switch-policy decision boundaries
- specify the minimum checkpoint payload needed for safe resume

### Slice C

- define audit events and validation expectations
- queue follow-on implementation work for reports, heuristics, and UI

## Risks

- Mixing core scheduler responsibilities with adapter-specific behavior too early
- Treating reset estimates as facts instead of confidence-scored observations
- Allowing automatic switching without a structured checkpoint

## Success Condition

At the end of this planning slice, `window-scheduler` has an active package with clear requirements, design boundaries, and a task list that another session can implement directly.
