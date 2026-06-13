# Design — pgvector-schema-langsmith-foundation-paralelo

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.
- Reuse existing RAG and LangSmith code paths rather than introducing a second
  foundation layer.
- Prefer verification helpers / focused tests over speculative new runtime
  behavior.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.
- Prefer proving current foundation assumptions over reopening architecture that
  may already be live in code.

## Context Notes
- Repo evidence already shows both halves of the objective exist in some form:
  pgvector schema/search groundwork and LangSmith tracing hooks.
- The likely problem is drift and scattered verification, not pure absence.

## T1 Implementation Direction

### Chosen phase-1 slice
- Narrow this objective to a **foundation verification** slice.
- The likely T2 should add one narrow operator/model-friendly surface such as:
  - a focused verification helper/report, or
  - a tighter focused test set covering pgvector schema + fail-soft LangSmith
    behavior together

### Why this slice
- It matches current repo evidence.
- It avoids redoing work that already appears implemented.
- It produces a stable baseline for later RAG/tracing follow-ups.

### Explicit non-goals for T2
- no broad RAG ingestion feature work
- no retrieval-quality benchmark expansion
- no new tracing product integration
