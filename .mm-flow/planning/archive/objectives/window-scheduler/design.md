# Design — window-scheduler

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.
- The Window Scheduler belongs to the **core reusable** layer, not the Project Adapter layer.
- It must not redefine brain doctrine, decide output quality itself, skip project governance, or execute high-risk actions without respecting the active policy.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.

## Minimum Viable Entity Set
The scheduler core operates with these 5 entities:
1. **BackendSession** — backend inventory (backend_id, provider, account_id, auth_mode, model_family, priority, cost_tier, risk_tier, overnight_allowed, automatic_switch_allowed, human_confirmation_required, enabled)
2. **AvailabilityState** — temporal state per backend (backend_id, state, window_started_at, window_exhausted_at, estimated_reset_at, estimation_source, estimation_confidence, last_verified_at)
3. **RunPolicy** — active execution policy (run_id, project_id, adapter_id, execution_mode, overnight_mode, max_switches_per_run, allow_paid_api_fallback, require_human_for_high_risk_actions, max_cost_tier, pause_on_low_confidence_reset)
4. **SchedulerEvent** — auditable event record (event_id, run_id, project_id, task_id, type, from_backend, to_backend, reason, checkpoint_id, execution_mode, estimated_reset_at, decision_outcome, eligibility_basis, next_step_summary, created_at)
5. **SchedulerCheckpoint** — minimal resume point (checkpoint_id, run_id, project_id, task_id, step_id, context_summary, artifacts, next_step_summary, created_at)

## Schema Constraints (Must Be Honored)
1. **No backend_switch without checkpoint_id** — every switch event must reference a valid checkpoint
2. **No checkpoint without next_step_summary** — every checkpoint must document what comes next
3. **All reset estimations must record estimation_source and estimation_confidence** — explicit evidence not guesswork
4. **Every run must have an explicit run_policy** — no implicit policy inheritance

## Dependencies
- No explicit upstream dependency declared. Canonical docs used for context: `docs/canonical/16-WINDOW-SCHEDULER-ARCHITECTURE.md` and `docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md`.

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.
- Package consistency check: requirements.md, design.md, and tasks.md must reference the same objective name ("window-scheduler"), same entity names, and same constraints.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- The full canonical architecture defines 8 components: Provider Registry, Availability Tracker, Eligibility Engine, Switch Policy Engine, Checkpoint Manager, Resume Manager, Audit Logger, Morning Report Generator.
- Only the 5 minimum viable entities listed above need to be implemented in this slice.
- This objective does NOT implement the 8 full components — those are deferred to later phases.
