# Design — rag-evaluation-gate

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
- Narrow this objective to an **offline Recall@5 evaluation** slice for Brain #1.
- Reuse the existing `similarity_search()` implementation and Brain #1's
  `domain_knowledge` collection assumptions.

### Likely T2 deliverable
- Add a read-only helper plus a labeled-pair fixture that:
  - reads manual evaluation pairs
  - runs retrieval with `limit=5`
  - computes `recall_at_5`, `hits`, `total`, and `passes_sli`
  - writes a stable JSON report for operators/models

### Why this slice
- It is deterministic and testable without depending on live LLM quality or
  LangSmith availability.
- It advances one hard-gate criterion concretely instead of hand-waving the
  whole evaluation gate.
- It creates an artifact surface other gate criteria can later compose with.

### Explicit non-goals for T2
- no Brain #7 live scoring loop
- no cross-provider timing benchmark
- no automatic gate decision spanning every criterion
