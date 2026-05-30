# Requirements — window-scheduler

## Problem / Purpose
Window Scheduler: the core layer responsible for managing temporal execution capacity across multiple backends, preserving work continuity, governance, and traceability when subscription time windows are limited.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.
- Implement minimum viable scheduler entities: BackendSession, AvailabilityState, RunPolicy, SchedulerEvent, SchedulerCheckpoint.
- Define schema constraints that ensure auditability: no switch without checkpoint, no checkpoint without next_step_summary.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Full 8-component implementation (Provider Registry, Availability Tracker, Eligibility Engine, Switch Policy Engine, Checkpoint Manager, Resume Manager, Audit Logger, Morning Report Generator) is deferred to later phases.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.
- All canonical schema constraints from `docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md` must be honored.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] All three docs (requirements.md, design.md, tasks.md) reference "window-scheduler" consistently (not "runtime-window-scheduler" or other aliases).
- [ ] The minimum viable entity set (BackendSession, AvailabilityState, RunPolicy, SchedulerEvent, SchedulerCheckpoint) is clearly defined with field lists in design.md.
- [ ] All 4 schema constraints are explicitly stated in design.md: (1) no switch without checkpoint, (2) no checkpoint without next_step_summary, (3) reset estimations need estimation_source+estimation_confidence, (4) every run needs explicit run_policy.
- [ ] T1 acceptance criteria in tasks.md are specific and verifiable (not vague statements).
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
