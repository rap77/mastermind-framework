# Design — mm-harness-gap-discover-auto-sync

## Architecture / Boundaries
- Reuse the existing `gap-registry.py sync-objective` capability instead of duplicating lifecycle logic.
- Keep discover behavior transparent and fail-soft relative to gap synchronization.

## Technical Approach
- Extend `discover-handler.py` with a narrow post-write hook in objective mode.
- After the objective package is written under `.mm-flow/planning/changes/<slug>`, invoke the existing sync path for the same slug.
- Phase 1 behavior:
  - successful package creation still succeeds even if the gap registry has no matching entry
  - if gap sync succeeds, emit a short success line in discover output
  - if gap sync finds no matching gap, emit an informational line, not a failure
- Prefer a small helper inside `discover-handler.py` that shells out to `gap-registry.py sync-objective --objective-slug <slug>`.

## Dependencies
- Depends on the existing gap registry lifecycle sync slice.

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer reuse of the existing helper over silent duplicate logic.
- Prefer fail-soft sync on discover over blocking a valid package creation.
- Prefer exact-slug sync only in phase 1.

## Context Notes
- The archive hook now prevents stale resolved gaps after closure; the missing mirror is marking a gap promoted when its objective package is first materialized.
