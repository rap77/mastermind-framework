# Handoff — mm-harness-multi-active-exception-metadata

## Current objective
- `mm-harness-multi-active-exception-metadata`

## Decisions already made
- Single-active remains the default harness policy.
- The next useful evolution is an explicit exception model, not silent relaxation of the policy.
- Any exception must be visible in artifacts and understandable by another model/operator.
- Phase 1 uses one root artifact: `.mm-flow/planning/active-objective-exceptions.json`.
- Exceptions are narrow and opt-in: exact slug-set match plus command scoping.
- Parser ownership should live in `.mm-flow/commands/mm/active-objective-state.py`.
- Runtime touchpoints for phase 2 implementation are `discover --existing --objective <slug>` and `activate-next-objective`.

## Blockers / risks
- Handler support does not exist yet; the contract is documented but not honored in runtime logic.
- `expires_when` is still plain text, so expiration is operator-readable but not yet machine-checkable.
- Roadmap should remain conservative until runtime entrypoints can honor exceptions safely.

## Deferred follow-up gaps
- Add structured/machine-checkable expiration semantics for exceptions.
- Decide whether future phases need broader scopes than exact slug sets.
- Revisit whether roadmap outputs should become exception-aware after runtime support exists.

## Exact next recommended task
- All planning tasks for this objective are complete; next run `/mm:archive-objective mm-harness-multi-active-exception-metadata` or open the implementation follow-up objective for runtime exception recognition.

## Validation commands
- `/mm:discover-contract-check --objective mm-harness-multi-active-exception-metadata`
