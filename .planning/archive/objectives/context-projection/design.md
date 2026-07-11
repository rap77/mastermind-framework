# Design — context-projection

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- The initial slice is the project-state read model already exposed by `ProjectOverviewService` and `/api/projects/{project_id}/tasks/{task_id}/context-projection`.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain, `TaskContextProjectionResponse`, and `DoctrineProjectionResponse` where possible.
- Keep the slice read-only: derive context from project, task, checkpoint, and decision records rather than introducing a new storage layer.

## Dependencies
- Depends on `project-state-mvp`
- Depends on `postgres-hybrid-data-model`

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- Existing API coverage already includes task and doctrine projection endpoints and API tests for the seeded context-projection path.
