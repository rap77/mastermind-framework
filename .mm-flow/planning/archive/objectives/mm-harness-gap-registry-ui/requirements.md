# Requirements — mm-harness-gap-registry-ui

## Problem / Purpose
Harness gap registry UI

## T1 Boundary Decision
- This objective is **not** a full planning console rewrite and is **not** a rich gap-editing interface.
- The first coherent slice should expose the new gap registry in a read-only UI surface.
- Phase 1 should stay narrow:
  - show gap entries from the registry
  - show enough lifecycle fields for an operator/model to understand gap state
  - prefer an existing operational UI surface instead of inventing a new app section
- Phase 1 should **not** yet:
  - mutate gap entries from the UI
  - create objectives from the UI
  - run semantic dedupe in the browser

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators reviewing harness continuity from `/project-state`

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No UI write-side controls for gaps in this slice.
- No new dedicated frontend subsystem if the existing dashboard can host the panel.
- No semantic dedupe visualization beyond current artifact-backed data.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep backend/CLI artifacts as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
