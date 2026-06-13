# Requirements — mm-harness-gap-promotion-assistant

## Problem / Purpose
Harness gap promotion assistant

## T1 Boundary Decision
- This objective is **not** automatic objective creation from gaps.
- The first coherent slice should reduce operator friction when promoting a gap into a real objective.
- Phase 1 should stay helper-driven and read-only:
  - inspect one gap by id
  - validate whether it is promotion-ready
  - emit the exact next command to materialize the objective package when valid
- Phase 1 should **not** yet:
  - create the objective automatically
  - mutate the gap entry as part of the preflight
  - override active-objective or archived-objective conflicts silently

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the gap registry and MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve artifact authority and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No auto-creation of objective packages.
- No UI write-side controls in this slice.
- No semantic promotion inference beyond explicit registry fields.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep registry artifacts as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
