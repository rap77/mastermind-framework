# 106. Phase 20-21 Execution Plan

## 1. Purpose

Turn the definitive operating roadmap into an executable slice for the live v3.2 lane:

- Phase 20: pgvector Schema + LangSmith Foundation
- Phase 21: RAG Pilot for Brain #1
- Phase 21.5: RAG Evaluation Gate

This plan is intentionally narrow. It exists to make the next lane concrete and finishable.

## 2. Current Baseline

### Already true

- Core canon for harnesses, loops, memory, registry, and selector policy exists.
- The runtime is already in the v3.2 lane.
- Phase 19 is formally closed.
- Phase 13-18 are complete.

### What still needs to become executable

- Phase 20 and Phase 21 are already present in code in pieces, but not yet packaged as one implementation slice.
- The code-level RAG path is partially implemented, but not yet unified with the canonical runtime docs and operator checklist.
- The next lane needs one authoritative slice, not multiple overlapping mini-plans.

## 3. Execution Principle

1. Build the minimum slice that makes Brain #1 RAG-functional.
2. Prove quality and latency before scale-out.
3. Do not start Brain #2-7 until the Brain #1 gate passes.
4. Keep project memory and domain knowledge separate.

## 4. Phase 20 - Schema + Foundation

### Goal

Prepare the retrieval substrate and observability foundation for RAG.

### Deliverables

- `brain_embeddings` schema
- HNSW index
- `sentence-transformers` runtime dependency
- `similarity_search()` utility
- LangSmith runtime instrumentation
- OEC baseline measurement for Brain #1

### Already present in code

- `apps/api/mastermind_cli/rag/migrations/001_create_brain_embeddings.sql`
- `apps/api/mastermind_cli/rag/search.py`
- `apps/api/mastermind_cli/rag/baseline.py`
- `apps/api/mastermind_cli/rag/foundation_verify.py`
- `apps/api/mastermind_cli/rag/migrate.py`
- `apps/api/mastermind_cli/rag/manual_ingestion.py`
- `apps/api/mastermind_cli/memory_layer/pgvector.py`
- `apps/api/mastermind_cli/memory_layer/embeddings.py`
- `apps/api/mastermind_cli/memory_layer/vector.py`

### Prerequisites

- pgvector already active
- runtime dependency packaging updated
- baseline sessions available for measurement

### Acceptance Criteria

- schema exists and is queryable
- similarity search returns top-k chunks with score
- LangSmith traces show latency, tokens, and cost
- quality baseline is recorded for at least 5 Brain #1 sessions

## 5. Phase 21 - Brain #1 RAG Pilot

### Goal

Make Brain #1 retrieve from both knowledge collections before answering.

### Deliverables

- `domain_knowledge` retrieval path
- `project_memory` retrieval path
- explicit `[RETRIEVED CONTEXT]` injection
- retrieval latency tracing
- `rag_enabled: true` metadata in session records

### Already present in code

- `apps/api/mastermind_cli/rag/context_builder.py`
- `apps/api/mastermind_cli/api/services/task_runner.py` asyncpg connection plumbing
- `task_runner.py` `rag_enabled` metadata persistence
- `task_runner.py` non-blocking LangSmith metadata updates

### Prerequisites

- Phase 20 complete
- retrieval utility available
- collections populated or ready to test with fixtures

### Acceptance Criteria

- Brain #1 queries `domain_knowledge` before every answer
- Brain #1 queries `project_memory` before every answer
- injected context is explicit and traceable
- P99 retrieval latency is under 200ms
- session metadata records RAG as enabled
- retrieval latency is emitted from the coordinator through a single observation object

## 6. Phase 21.5 - Evaluation Gate

### Goal

Prove RAG improves quality before any scale-out.

### Deliverables

- A/B test harness for RAG vs cold
- recall@5 evaluation
- contamination checks
- quality delta measurement
- gate verdict

### Already present in code

- `apps/api/mastermind_cli/rag/recall_eval.py`
- `apps/api/tests/unit/test_rag_foundation_verify.py`
- `apps/api/tests/unit/test_rag_langsmith.py`
- `apps/api/tests/integration/test_rag_search.py`

### Prerequisites

- Phase 21 complete
- enough labeled evaluation pairs
- Brain #7 evaluator available for scoring

### Acceptance Criteria

- RAG-enabled Brain #1 beats cold baseline by the required quality delta
- recall@5 meets threshold
- latency stays under the budget
- no self-contamination from prior same-brain answers

## 7. Phase 22 - Manual Ingestion

### Goal

Load the corpus into the two collection types in a controlled, manual way.

### Deliverables

- idempotent ingest script
- per-brain domain_knowledge population
- per-brain project_memory population
- ingest report with counts

### Prerequisites

- Phase 21.5 passed

### Acceptance Criteria

- 7 brains × 2 collections populated
- ingest can be re-run safely
- counts are visible and non-zero

## 8. Phase 23 - Scale-Out

### Goal

Apply the validated RAG pattern to the rest of the brains.

### Deliverables

- RAG enabled for brains 2-7
- LangSmith cost/latency reporting per brain
- scaling guardrails

### Prerequisites

- Phase 22 complete

### Acceptance Criteria

- Recall@5 and quality delta pass across all enabled brains
- latency guardrail holds
- cost observability exists per provider and brain

## 9. Recommended Order

1. Package Phase 20 schema and foundation.
2. Implement Brain #1 RAG pilot.
3. Run the evaluation gate.
4. Ingest the corpus manually.
5. Scale out only after the gate passes.

## 10. Completion Criteria

This plan is complete when:

- Phase 20-21 is executable as one coherent slice
- the RAG gate is measurable and repeatable
- scale-out is clearly blocked until the gate passes
- the runtime lane and canonical docs agree on what happens next
