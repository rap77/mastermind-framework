# Requirements — mm-harness-gap-objective-lifecycle-sync

## Problem / Purpose
Harness gap/objective lifecycle synchronization

## T1 Boundary Decision
- This objective is **not** a full automatic roadmap writer and is **not** a semantic planner.
- The first coherent slice should reduce lifecycle drift between:
  - gap registry entries
  - created objectives
  - archived objectives
- Phase 1 should stay explicit and helper-driven:
  - detect when a gap's suggested follow-up objective already exists
  - synchronize the gap entry to a lifecycle-aware status
- Phase 1 should **not** yet:
  - auto-create objectives
  - rewrite multiple gaps transitively
  - infer semantic resolution beyond exact objective slug matches

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators relying on artifacts instead of chat memory

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- No semantic matching or LLM-driven synchronization.
- No automatic objective creation.
- No automatic archive hooks in phase 1.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep artifacts as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
