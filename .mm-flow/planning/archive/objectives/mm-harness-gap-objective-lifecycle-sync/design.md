# Design — mm-harness-gap-objective-lifecycle-sync

## Architecture / Boundaries
- Reuse the existing gap registry artifact and helper instead of creating another lifecycle command surface.
- Keep synchronization helper-driven and artifact-visible.

## Technical Approach
- Extend `gap-registry.py` with a narrow `sync-objective` subcommand.
- `sync-objective` should accept `--objective-slug <slug>` and inspect exact artifact presence:
  - `.mm-flow/planning/changes/<slug>`
  - `.mm-flow/planning/archive/objectives/<slug>`
- Match candidate gaps by exact `suggested_followup == <slug>`.
- Phase 1 lifecycle mapping:
  - active objective exists in `changes/` => mark matching gap `promoted`
  - archived objective exists in `archive/objectives/` => mark matching gap `resolved`
- Keep matching deterministic and narrow:
  - exact slug only
  - no mutation if no matching gap exists
  - no mutation if no matching objective artifacts exist

## Dependencies
- No explicit upstream dependency declared.

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer explicit helper invocation over hidden archive hooks in phase 1.
- Prefer exact slug matching over broader heuristics.
- Prefer lifecycle synchronization of one gap/objective pair at a time.

## Context Notes
- The current registry can rank and promote gaps, but drift still appears when an objective is opened or archived without updating the registry entry.
