# Requirements — pgvector-schema-langsmith-foundation-paralelo

## Problem / Purpose
pgvector Schema + LangSmith Foundation (paralelo)

## Stakeholders / Users
- Primary: repository maintainers and future execution models
- Secondary: human operators using the `/project-state` console or MM planning commands

## Scope
- Deliver the smallest coherent slice that advances this objective without rewriting adjacent systems.
- Preserve backend-authority boundaries and the current incremental architecture.

## Out of Scope
- No unrelated rewrites or speculative refactors.
- Do not bypass backend services with direct model/database access.

## Non-negotiables
- Preserve a model/provider-agnostic harness direction.
- Keep the backend as the authority for state, validation, and auditability.
- Do not introduce unstructured chat-only continuity as the primary workflow.

## Objective-level Acceptance Criteria
- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.
- [ ] The implementation slice advances the target objective without breaking adjacent flows.
- [ ] Validation commands are documented and usable by another model or human operator.

## T1 Boundary Decision

### What already exists
- `pgvector`/RAG foundation is not greenfield in this repo:
  - `apps/api/mastermind_cli/rag/migrations/001_create_brain_embeddings.sql`
  - `apps/api/mastermind_cli/rag/migrate.py`
  - `apps/api/mastermind_cli/rag/search.py`
  - existing RAG schema/search tests
- LangSmith hooks are also partially present already:
  - `apps/api/mastermind_cli/mm_flow/dispatch_engine.py`
  - `apps/api/mastermind_cli/api/services/task_runner.py`
  - existing `test_rag_langsmith.py`

### Current gap to target
- The safest remaining gap is **foundation verification / drift reduction**, not
  “add pgvector” or “add LangSmith from scratch”.
- The first slice should prove that:
  - pgvector schema assumptions still match the current repo/runtime path
  - LangSmith instrumentation remains optional and fail-soft
  - another operator/model can verify the foundation without rediscovering the
    scattered evidence manually

### Explicit non-goals for this objective slice
- No new RAG product behavior yet.
- No broad retrieval-quality work or pilot rollout.
- No new tracing vendor expansion beyond the existing LangSmith seam.
