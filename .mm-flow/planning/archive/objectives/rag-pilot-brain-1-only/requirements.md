# Requirements — rag-pilot-brain-1-only

## Problem / Purpose
RAG Pilot — Brain #1 Only

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
- Brain #1 RAG seams already exist locally:
  - `apps/api/mastermind_cli/rag/context_builder.py`
  - `apps/api/mastermind_cli/rag/search.py`
  - `apps/api/mastermind_cli/orchestrator/stateless_coordinator.py`
  - `apps/api/mastermind_cli/api/services/task_runner.py`
- Existing tests already cover the isolated RAG behavior:
  - `apps/api/tests/rag/test_context_builder.py`
  - `apps/api/tests/rag/test_brain1_rag_integration.py`
  - `apps/api/tests/rag/test_brain1_rag_empty_collections.py`

### Current gap to target
- The safest remaining gap is **runtime activation alignment**, not a brand-new
  Brain #1 RAG implementation.
- The current repo mixes two Brain #1 identifiers:
  - `brain-01-product`
  - `brain-01-product-strategy`
- The normal runtime path (`task_runner` → `StatelessCoordinator.execute_flow`)
  uses `brain-01-product`, while the RAG activation checks in:
  - `StatelessCoordinator._execute_brain()`
  - `task_runner.run_brain_task()`
  are still gated on `brain-01-product-strategy`.
- That means the pilot likely works in isolated tests using the long ID but can
  silently skip RAG in the normal runtime path.

### Explicit non-goals for this objective slice
- No scale-out beyond Brain #1.
- No new evaluation gate logic here.
- No retrieval-quality redesign beyond making the intended pilot path truly run.
