# Requirements — mm-harness-gap-registry-and-promotion

## Problem / Purpose
Harness gap registry and promotion

## T1 Boundary Decision
- This objective is **not** a full autonomous “gap manager” with automatic
  prioritization, deduplication, and roadmap rewriting.
- The first coherent slice should be a **gap registry artifact plus a narrow
  helper workflow**.
- Phase 1 should introduce:
  - a root-level durable artifact for gaps
  - a minimal schema for recording a detected gap with evidence and promotion
    readiness
  - a narrow helper to register gaps, list open gaps, and mark one as promoted
    to an objective
- Phase 1 should **not** yet:
  - auto-detect every gap from arbitrary chat/runtime events
  - reprioritize the roadmap automatically
  - create objectives without an explicit operator/model decision

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No autonomous gap prioritizer in this slice.
- No automatic objective creation from every detected gap.
- No UI surface in this slice unless needed for validation.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
