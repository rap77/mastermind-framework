# Design — mm-harness-gap-archive-auto-sync

## Architecture / Boundaries
- Reuse the existing `gap-registry.py sync-objective` capability instead of duplicating lifecycle logic in another helper.
- Keep archive behavior transparent and fail-soft relative to gap synchronization.

## Technical Approach
- Extend `archive-objective-handler.py` with a narrow post-archive hook.
- After the objective is moved into `.mm-flow/planning/archive/objectives/<slug>`, invoke the existing sync path for the same slug.
- Phase 1 behavior:
  - successful archive still succeeds even if the gap registry has no matching entry
  - if gap sync succeeds, emit a short success line in archive output
  - if gap sync finds no matching gap, emit an informational line, not a failure
- Prefer a small helper inside `archive-objective-handler.py` that shells out to `gap-registry.py sync-objective --objective-slug <slug>`.

## Dependencies
- Depends on the existing gap registry lifecycle sync slice.

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer reuse of the existing helper over silent duplicate logic.
- Prefer fail-soft sync on archive over blocking a valid archive.
- Prefer exact-slug sync only in phase 1.

## Context Notes
- The manual sync helper solved the lifecycle drift, but another model/operator can still forget to run it after archive.
