# Requirements — rag-evaluation-gate

## Problem / Purpose
RAG Evaluation Gate

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
- Brain #1 RAG pilot seams already exist:
  - `apps/api/mastermind_cli/rag/context_builder.py`
  - `apps/api/mastermind_cli/rag/search.py`
  - `apps/api/tests/rag/test_context_builder.py`
  - `apps/api/tests/rag/test_brain1_rag_integration.py`
  - `apps/api/tests/rag/test_brain1_rag_empty_collections.py`
- Baseline/OEC groundwork already exists:
  - `apps/api/mastermind_cli/rag/baseline.py`
  - `apps/api/tests/unit/test_rag_langsmith.py`
- The broader gate criteria are documented in:
  - `.planning/ROADMAP-v3.2.md`
  - `.planning/archive/legacy/root-tasks/plan.md`
  - `.planning/archive/legacy/root-tasks/todo.md`

### Current gap to target
- The safest remaining gap is **one deterministic gate signal**, not the entire
  Phase 21.5 automation in one step.
- Live A/B execution, Brain #7 scoring deltas, LangSmith latency guardrails, and
  contamination checks are all valid future gate criteria, but they require more
  runtime coordination than the current repo evidence guarantees.
- The smallest coherent next slice should implement:
  - labeled-pair input for Brain #1 `domain_knowledge`
  - offline `Recall@5` evaluation against `similarity_search`
  - a stable JSON result artifact indicating pass/fail against the `>= 0.70`
    threshold

### Explicit non-goals for this objective slice
- No full live A/B orchestration of RAG-vs-cold runs yet.
- No LangSmith-dependent latency gate implementation yet.
- No contamination scoring pipeline yet.
