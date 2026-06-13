# Requirements — mm-harness-gap-registry-ui-triage

## Problem / Purpose
Harness gap registry UI triage

## T1 Boundary Decision
- This objective is **not** a full gap management workbench.
- The first coherent follow-up after the base UI panel should expose the two most useful triage signals already available from the registry helper:
  - duplicate suspects
  - next recommended gap
- Phase 1 should stay read-only and dashboard-embedded.
- Phase 1 should **not** yet:
  - mutate gaps from the UI
  - resolve duplicate suspects from the UI
  - create objectives from the UI

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators reviewing harness follow-ups in `/project-state`

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend/CLI artifact authority and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No UI write-side controls.
- No semantic dedupe beyond the existing helper output.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep backend/CLI artifacts as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
