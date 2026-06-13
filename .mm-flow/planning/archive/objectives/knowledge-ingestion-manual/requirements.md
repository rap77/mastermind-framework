# Requirements — knowledge-ingestion-manual

## Problem / Purpose
The roadmap and historical research already constrain this objective heavily:
Phase v3.2 expects a **manual ingestion script**, not an auto-update pipeline,
for loading knowledge into per-brain stores. The current package is too vague
to execute safely because it does not yet distinguish between:
- domain knowledge already living in NotebookLM/source exports, and
- future project-memory ingestion for RAG stores.

The most immediate gap is to define a narrow Phase 1 slice that prepares or
implements the manual ingestion operator path without reopening broad RAG
automation work.

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.
- Phase 1 scope is limited to the **manual ingestion operator workflow** for
  knowledge sources, with no file watcher or auto-update behavior.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.
- Do not introduce automatic ingestion triggers, file watchers, or incremental
  re-embedding in this slice.
- Do not reopen broad pgvector/RAG architecture if the first gap can be solved
  at the operator-workflow layer.
- Do not mix project-memory ingestion with domain-knowledge ingestion unless the
  first slice explicitly proves both are required.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.
