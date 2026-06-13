# Requirements — context-window-management

## Problem / Purpose
Context Window Management

## T1 Boundary Decision
- This objective is **not** a full runtime implementation of packing,
  compression, checkpointing, and backend switching.
- The first coherent slice should implement the smallest reusable foundation:
  **Model Capability Registry + Context Fit Evaluator**.
- Phase 1 should stay read-only and backend-authoritative:
  - extend backend inventory with context capability fields
  - add a pure fit-evaluation helper that classifies a backend/context pair as
    `fits_cleanly`, `fits_with_compression`, `unsafe_fit`, or `does_not_fit`
- This slice should not yet perform switching, packing, or destructive
  compression.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No automatic backend switching in this slice.
- No prompt packager or compressor implementation yet.
- No UI surface yet unless it becomes strictly necessary for validation.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
