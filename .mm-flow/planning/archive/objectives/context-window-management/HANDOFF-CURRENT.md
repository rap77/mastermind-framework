# Handoff — context-window-management

## Current objective
- `context-window-management`

## Decisions already made
- Use a per-objective planning package instead of relying on a single root planning surface forever.
- Another model should be able to resume from artifacts, not from chat memory alone.
- The first coherent slice is **Model Capability Registry + Context Fit
  Evaluator**, not a full scheduler/runtime integration.
- The slice should live in the existing `window_scheduler` core and stay
  read-only for phase 1.
- The phase-1 slice is now implemented by:
  - extending `BackendSession` with context capability metadata
  - adding a pure `assess_context_fit(...)` helper with the canonical
    four-state output model
- The evaluator is intentionally DB-free and orchestration-free so future
  scheduler integration can consume it without hidden side effects.

## Blockers / risks
- The next gap is no longer capability metadata itself; it is wiring fit
  assessment into switching, packing, or checkpoint policy decisions.
- No migration/update path is defined yet for persisted scheduler rows that may
  need the new capability fields in a real deployment.

## Exact next recommended task
- Archive this objective and open a follow-up only when context-fit decisions
  need to influence real switching or packing behavior.

## Validation commands
- `/mm:discover-contract-check --objective context-window-management`
- `apps/api/.venv/bin/python -m pytest apps/api/tests/unit/test_context_fit.py`
