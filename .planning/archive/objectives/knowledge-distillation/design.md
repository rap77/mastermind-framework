# Design — knowledge-distillation

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI handles distillation logic, SQLite-backed runtime state, and analytics surfaces.
- New behavior should enter through explicit service or handler boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice: confirm the existing distillation foundation is operating correctly across scoring, filtering, TTL, template extraction, and analytics.
- Reuse the existing `experience`, `orchestration`, and `api/routes` modules where possible.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted tests for the distillation foundation and analytics surfaces.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- The underlying distillation code already exists; this objective is about validating and consolidating the foundation rather than introducing a brand-new subsystem.
