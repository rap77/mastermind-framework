# Design — mm-harness-gap-dedupe-and-priority

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse the new gap registry artifact and extend the same helper instead of
  creating another gap-management command surface.
- Introduce two narrow capabilities:
  1. **duplicate suspect view**
     - normalize titles / suggested follow-up strings
     - compare open gaps using deterministic string fingerprints
     - emit “possible duplicate” relations without mutating entries
  2. **priority view**
     - rank open gaps deterministically from existing fields:
       - `promotion_readiness`
       - `impact`
       - `urgency`
       - stable tie-breaker by creation order / id
- Keep outputs read-only for phase 1:
  - list duplicates
  - show next recommended gap
  - optionally list all ranked open gaps
- Prefer helper subcommands over implicit background mutation.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer “duplicate suspect” over “duplicate truth” in phase 1.
- Prefer deterministic operator-facing ranking over hidden scoring magic.

## Context Notes
- The previous gap-registry objective already provides persistence and explicit
  promotion marking; the missing layer now is choosing and reviewing what
  deserves promotion next.
