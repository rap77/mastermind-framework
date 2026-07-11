# Design — rust-control-plane-hardening

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice: auth refresh token rotation and the login/refresh/logout handlers around it.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.

## Dependencies
- Depends on `backend-service-boundary-for-agents`

## Validation Strategy
- Run targeted tests for the auth refresh flow and related handlers.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- No additional context note available.
