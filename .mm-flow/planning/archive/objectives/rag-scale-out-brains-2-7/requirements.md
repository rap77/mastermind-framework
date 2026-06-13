# Requirements — rag-scale-out-brains-2-7

## Problem / Purpose
RAG Scale-Out — Brains 2–7

## T1 Boundary Decision
- This objective is **not** a single big-bang rollout across all remaining
  brains.
- The first coherent slice is to extend the existing Brain #1 RAG prompt seam
  into a **shared multi-brain plumbing path** for a narrow first cohort of
  prompt-driven brains.
- Phase 1 should target **Brains #2, #3, and #7** first:
  - `brain-02-ux-research`
  - `brain-03-ui-design`
  - `brain-07-growth-data`
- These brains already follow the same NotebookLM/prompt-building pattern as
  Brain #1, so they are the safest place to prove shared scale-out before
  touching the rest of the runtime.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not try to activate all brains 2–7 in one slice.
- No new pgvector schema work, ingestion work, or eval gate redesign here.
- Do not fold the separate `run_brain_task` test-isolation gap into this
  objective unless it blocks the first cohort directly.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
