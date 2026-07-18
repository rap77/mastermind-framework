# 107. Phase 20-21 Status Map

## 1. Purpose

Map the live v3.2 lane into three operational buckets:

- already implemented
- partially implemented / ununified
- still missing

This document is the answer to: "what is actually done vs what is only planned?"

## 2. Phase 20 - pgvector Schema + LangSmith Foundation

### Implemented

- `apps/api/mastermind_cli/rag/migrations/001_create_brain_embeddings.sql`
- `apps/api/mastermind_cli/rag/search.py`
- `apps/api/mastermind_cli/rag/baseline.py`
- `apps/api/mastermind_cli/rag/foundation_verify.py`
- `apps/api/mastermind_cli/rag/embed.py`
- `apps/api/mastermind_cli/rag/migrate.py`
- `apps/api/mastermind_cli/rag/manual_ingestion.py`
- `apps/api/mastermind_cli/memory_layer/pgvector.py`
- `apps/api/mastermind_cli/memory_layer/embeddings.py`
- `apps/api/mastermind_cli/memory_layer/vector.py`
- `apps/api/pyproject.toml` now includes `sentence-transformers` and `langsmith`
- tests for pgvector, recall, baseline, and LangSmith seams

### Partially implemented

- Phase 20 exists as code pieces, but not as one single packaged slice.
- `brain_embeddings` is split across the RAG module and the first-party memory layer.
- The foundation verifier checks the expected seams, but the lane is still a composition of modules rather than one committed phase package.

### Missing

- one canonical Phase 20 package boundary in planning terms
- explicit phase summary that links all Phase 20 artifacts to one execution slice
- a single operator-facing checklist tying migration, search, baseline, and LangSmith together

### Acceptance for Phase 20

- `brain_embeddings` schema exists and is the same target the code expects
- `similarity_search()` is stable and uses pgvector cosine semantics
- `sentence-transformers` and `langsmith` are runtime dependencies
- the OEC baseline is measurable and versioned
- the foundation verifier passes

## 3. Phase 21 - RAG Pilot (Brain #1)

### Implemented

- `apps/api/mastermind_cli/rag/context_builder.py`
- `apps/api/mastermind_cli/rag/search.py` already supports collection filtering and result scoring
- `apps/api/mastermind_cli/api/services/task_runner.py` opens an asyncpg connection and passes `conn=` into the coordinator when supported
- `task_runner.py` computes `rag_enabled` per brain and stores it in `custom_metadata`
- `task_runner.py` updates LangSmith metadata with `rag_enabled` non-blockingly

### Partially implemented

- `RAGContextBuilder` exists and formats `[RETRIEVED CONTEXT]`, but it is still a helper rather than a fully packaged runtime contract at the orchestration boundary.
- `task_runner.py` can pass `conn` into the coordinator, but the retrieval-to-prompt injection path is still distributed across modules.
- Brain #1 is the only brain explicitly wired for the RAG pilot path.

### Missing

- a single definitive "Brain #1 RAG pilot" slice package in planning terms
- explicit proof that the coordinator always injects the retrieved context before Brain #1 answers in every supported path
- a consolidated phase summary that states the pilot is complete and what remains for scale-out

### Acceptance for Phase 21

- Brain #1 retrieves from `domain_knowledge`
- Brain #1 retrieves from `project_memory`
- retrieved context is injected explicitly as `[RETRIEVED CONTEXT]`
- `rag_enabled` is persisted when retrieval actually happens
- retrieval latency is traced and surfaced via a coordinator observation object

## 4. Phase 21.5 - Evaluation Gate

### Implemented

- `apps/api/mastermind_cli/rag/recall_eval.py`
- `apps/api/tests/unit/test_rag_foundation_verify.py`
- `apps/api/tests/unit/test_rag_langsmith.py`
- `apps/api/tests/integration/test_rag_search.py`

### Partially implemented

- offline recall evaluation exists, but the full gate as an operational decision point is not yet packaged as a canonical phase artifact.

### Missing

- one explicit gate summary showing pass/fail criteria in the lane itself
- a top-level operator checklist that says when to stop before Phase 22

### Acceptance for Phase 21.5

- Recall@K can be evaluated offline with labeled pairs
- Brain #7 can score quality deltas for RAG vs cold
- contamination checks are part of the gate
- the gate blocks scale-out when thresholds are not met

## 5. Summary

### Already done

- the substrate exists
- the retrieval path exists
- the baseline/evaluation helpers exist
- the observability seams exist

### Still half-done

- unification into one canonical phase package
- operator-facing packaging of the lane
- explicit phase closeout summaries

### Still missing

- the first executable phase package that ties Phase 20 + Phase 21 + gate together as one coherent slice
