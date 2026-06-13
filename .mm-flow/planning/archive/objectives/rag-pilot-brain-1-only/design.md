# Design — rag-pilot-brain-1-only

## Architecture / Boundaries
- Follow the existing monorepo split: Python/FastAPI product logic, Next.js UI, Rust control-plane where operationally justified.
- New behavior should enter through semantic services or explicit UI boundaries, not ad-hoc global state.

## Technical Approach
- Build the smallest coherent vertical slice that satisfies the acceptance criteria.
- Reuse the existing `project_state` incremental domain and MM command infrastructure where possible.

## Dependencies
- No explicit upstream dependency declared

## Validation Strategy
- Run targeted Python tests or validation commands for touched areas.
- Run relevant web lint/typecheck commands when frontend files change.
- Refresh handoff state after completing or partially completing the objective.

## Important Tradeoffs
- Prefer execution-ready specificity over speculative completeness.
- Prefer incremental compatibility over large migration bursts.

## Context Notes
- No additional context note available.

## T1 Implementation Direction

### Chosen phase-1 slice
- Narrow this objective to a **Brain #1 runtime ID alignment** slice.
- Make the normal execution path use one canonical Brain #1 identifier for:
  - RAG retrieval activation
  - `rag_enabled` metadata propagation
  - Brain-function dispatch compatibility

### Likely T2 deliverable
- Fix the Brain #1 runtime path so that:
  - a standard `brain-01-product` execution actually triggers
    `RAGContextBuilder.build()`
  - the resulting `rag_enabled` metadata reflects real retrieval behavior
  - focused tests prove the normal path, not only isolated helper paths

### Why this slice
- It addresses a likely silent runtime failure mode.
- It is much smaller and safer than redesigning the pilot.
- It makes existing RAG code paths operationally real before any further
  retrieval or evaluation work.

### Explicit non-goals for T2
- no new multi-brain rollout
- no new recall/OEC logic
- no schema changes
