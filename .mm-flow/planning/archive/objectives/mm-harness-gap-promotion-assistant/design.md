# Design — mm-harness-gap-promotion-assistant

## Architecture / Boundaries
- Reuse the existing `gap-registry.py` helper instead of introducing another command surface.
- Keep the first slice read-only and explicit.

## Technical Approach
- Extend `gap-registry.py` with a narrow `prepare-promotion` subcommand.
- `prepare-promotion --id <gap-id>` should:
  - locate the registry entry
  - require `status` in `{open, deferred}`
  - require `promotion_readiness == ready`
  - require a non-empty `suggested_followup`
  - inspect exact objective artifact presence under:
    - `.mm-flow/planning/changes/<slug>`
    - `.mm-flow/planning/archive/objectives/<slug>`
- When valid, emit:
  - objective slug
  - gap title/id
  - exact next discover command
- When invalid/conflicting, fail with a narrow reason.

## Dependencies
- Depends on the phase-1 gap registry helper and lifecycle sync work.

## Validation Strategy
- Run targeted Python tests for the helper.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer exact slug checks over broader inference.
- Prefer command suggestion over automatic mutation.
- Prefer helper reuse over another planner-specific wrapper.

## Context Notes
- The registry can already rank and sync gaps, but operators still need a narrow bridge from “recommended gap” to “safe objective command”.
