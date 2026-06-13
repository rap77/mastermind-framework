# Design — task-time-and-estimation

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.

## Dependencies
- Depends on `project-state-mvp`

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- No additional context note available.

## T1 Implementation Direction

### Chosen phase-1 slice
- Narrow this objective to a **read-only estimation coverage** slice.
- Keep the existing heuristic ETA path intact, but make its basis more
  operator-visible from the same project-state flow.

### Likely T2 deliverable
- Extend the current project time summary with narrow diagnostics such as:
  - explicit estimate coverage counts
  - fallback estimate counts for remaining tasks
  - optional missing-estimate task identifiers/titles if needed for UI
- Surface those diagnostics in `/project-state` without introducing a second
  estimation subsystem.

### Why this slice
- It advances the objective without pretending the full canonical timing model
  is already implemented.
- It makes the current ETA more actionable for operators.
- It reuses the existing service/API/UI path instead of opening a new one.

### Explicit non-goals for T2
- no write-side time event capture
- no historical estimation-accuracy scoring
- no background recalculation service
