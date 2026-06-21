# Handoff — window-scheduler

## Current objective

- `window-scheduler`

## Starting assumptions

- `window-scheduler` is planned and ready-now in `.planning/roadmap/objectives.md`
- The canonical source docs are `docs/canonical/16-WINDOW-SCHEDULER-ARCHITECTURE.md` and `docs/canonical/19-WINDOW-SCHEDULER-DATA-SCHEMA.md`
- No active implementation package existed previously, so this package is the new source of truth for the objective kickoff

## Exact next recommended task

- Start coding `WS-01` from `implementation-slice.md` using TDD: write `apps/api/tests/window_scheduler/test_service.py` first, then add repositories and the minimal service/validator layer.

## Guardrails

- Keep the slice core and reusable
- Do not mix provider-specific heuristics into the initial planning slice
- Do not design UI/reporting details before the domain contract and switching invariants are explicit
