# Requirements — task-time-and-estimation

## Problem / Purpose
Task Time and Estimation

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.

## T1 Boundary Decision

### What already exists
- Project-state already exposes a heuristic project ETA surface:
  - `apps/api/mastermind_cli/project_state/services/project_overview.py`
  - `apps/api/mastermind_cli/project_state/schemas/overview.py`
  - `apps/api/mastermind_cli/api/routes/project_overview.py`
  - `/project-state` already renders the returned time summary
- Existing tests already prove the basic API/service/UI path:
  - `apps/api/tests/unit/test_project_overview_service.py`
  - `apps/api/tests/api/test_project_time_summary.py`
  - `apps/web/src/components/project-state/__tests__/ProjectStateDashboard.test.tsx`

### Current gap to target
- The safest remaining gap is **estimation coverage visibility**, not the full
  canonical time-event model from `docs/canonical/24-TASK-TIME-AND-ESTIMATION-MODEL.md`.
- Operators can see `confidence` and `estimated_remaining_minutes`, but they
  cannot see **why** confidence is low or how much of the plan still depends on
  priority-based fallback estimates.
- The smallest coherent next slice should expose:
  - how many tasks have explicit estimates
  - how many remaining tasks still rely on fallback heuristics
  - a stable explanation surface for estimation quality

### Explicit non-goals for this objective slice
- No new `task_time_events`, `task_metrics`, or historical rollups yet.
- No automatic actual-vs-estimated rework model yet.
- No speculative prediction model beyond the current heuristic ETA path.
