# Requirements — harness-memory-unification

## Problem / Purpose
MasterMind needs a reusable harness + memory platform that can execute objectives deterministically, persist context, and bridge `.planning` as an operational intent layer instead of a manual side process.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using `.planning` and the MM planning flow

## Scope
### In Scope
- define a first-party project manifest for the unified initiative
- define the harness contract and loop boundary
- define the memory contract and persistence boundary
- define the planning bridge that maps `.planning` into harness inputs/outputs
- define a project adapter boundary so the stack can be reused elsewhere
- define a clear adapter boundary so the reusable core stays repo-agnostic

### Out of Scope
- replacing every historical planning artifact immediately
- collapsing AI-DLC and `.planning` into one folder
- broad refactors unrelated to harness/memory/bridge boundaries

## Non-negotiables
- Keep AI-DLC as the design source of truth.
- Keep `.planning` as the operational source of truth.
- Do not let the harness guess when the objective is ambiguous.
- Prefer additive contracts over replacement rewrites.
- Keep the initial slice small enough to execute safely and review independently.

## Objective-level Acceptance Criteria
- [ ] A canonical project manifest exists for the unified initiative.
- [ ] Harness, memory, and bridge contracts are defined with explicit boundaries.
- [ ] The adapter boundary between reusable runtime and repo-specific routing is explicit.
- [ ] The next execution slice can be resumed from package artifacts instead of chat memory.
- [ ] The package documents validation commands or checks for the next implementation step.
