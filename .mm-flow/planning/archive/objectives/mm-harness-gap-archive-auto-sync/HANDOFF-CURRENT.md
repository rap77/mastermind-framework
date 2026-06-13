# Handoff — mm-harness-gap-archive-auto-sync

## Current objective
- `mm-harness-gap-archive-auto-sync`

## Decisions already made
- The first coherent slice is an archive-only auto-sync hook for gap lifecycle state.
- Phase 1 should reuse `gap-registry.py sync-objective` instead of duplicating sync rules.
- Archive success should remain primary; gap sync failures due only to no match should stay informational.
- `archive-objective-handler.py` now runs a best-effort post-archive sync hook.
- Helper resolution now falls back to the sibling `gap-registry.py` path when the project-local helper is absent in test/runtime wrappers.

## Blockers / risks
- Shelling out to the helper adds a small integration seam, but keeps lifecycle rules in one place.
- Exact slug matching still will not catch semantically equivalent follow-ups.
- This slice only covers archive-time sync; activation/open hooks remain a separate follow-up.

## Exact next recommended task
- Archive `mm-harness-gap-archive-auto-sync`.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-gap-archive-auto-sync`
- `python3 -m unittest tests.unit.test_mm_gap_registry`
- `python3 -m unittest tests.unit.test_mm_discover_workflow -k "archive_objective"`
