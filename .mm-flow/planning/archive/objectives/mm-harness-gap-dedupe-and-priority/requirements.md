# Requirements — mm-harness-gap-dedupe-and-priority

## Problem / Purpose
Harness gap dedupe and priority

## T1 Boundary Decision
- This objective is **not** a semantic dedupe system powered by an LLM and is
  **not** a full roadmap prioritizer.
- The first coherent slice should add:
  - a deterministic duplicate-suspect heuristic for gap entries
  - a deterministic priority ordering for open gaps using fields that already
    exist in the phase-1 registry
- Phase 1 should stay explicit and artifact-visible:
  - surface duplicate suspects
  - surface a recommended next gap ordering
  - never auto-merge or auto-close gaps
- Phase 1 should **not** yet:
  - rewrite historical entries automatically
  - use embeddings or semantic clustering
  - auto-create objectives from ranking results

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- No semantic/LLM-based duplicate detection in this slice.
- No automatic merging of gaps.
- No roadmap rewriting or auto-promotion in this slice.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
