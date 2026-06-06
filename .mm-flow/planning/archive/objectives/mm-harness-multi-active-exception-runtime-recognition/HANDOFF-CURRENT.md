# Handoff — mm-harness-multi-active-exception-runtime-recognition

## Current objective
- `mm-harness-multi-active-exception-runtime-recognition`

## Decisions already made
- Single-active remains the default harness policy.
- The exception contract already exists at `.mm-flow/planning/active-objective-exceptions.json`.
- Runtime support should be narrow: exact slug-set matching plus command scoping only.
- Shared parser ownership belongs in `.mm-flow/commands/mm/active-objective-state.py`.
- T1 fixed the intended helper surface around `load_active_objective_exceptions(...)` and `find_active_objective_exception(...)`.
- T1 fixed the runtime touchpoints to `discover --existing --objective` and `activate-next-objective` only.
- T2 implemented shared exception loading/matching in `active-objective-state.py` and allowed `discover --existing --objective` to proceed when a valid matching exception exists.
- T3 extended the same recognition path to `activate-next-objective` and kept it fail-closed when the delegated discover path is not authorized.

## Blockers / risks
- The runtime path now honors documented exceptions, but delegated flows still require explicit command coverage for every participating entrypoint.
- `expires_when` remains operator-readable text, not machine-checked policy.

## Deferred follow-up gaps
- Model composite/delegated command scopes so operators do not need to manually list both `activate-next-objective` and `discover --existing --objective` when one command delegates to the other.
- Add structured/machine-checkable expiration semantics for active-objective exceptions.
- Decide whether roadmap outputs should become exception-aware now that runtime recognition exists.

## Exact next recommended task
- All objective tasks are complete; run `/mm:archive-objective mm-harness-multi-active-exception-runtime-recognition` and open the next exception-related follow-up objective.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-multi-active-exception-runtime-recognition`
- `python3 -m unittest tests.unit.test_mm_discover_workflow`
