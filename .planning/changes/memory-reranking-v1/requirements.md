# Requirements — memory-reranking-v1

## Goal

Add the first reranking slice on top of Retrieval v1 so MasterMind can improve ordering quality without changing the stable `MemoryStore.search(...)` caller contract.

## In Scope

- Add an internal reranking seam after lexical/vector candidate fusion
- Keep reranking optional and local-first
- Allow source-aware and intent-aware score adjustments
- Preserve deterministic fallback when reranking is disabled
- Reuse the sealed Retrieval v1 baseline as regression protection

## Out of Scope

- Graph traversal or graph-aware recall
- Full cross-encoder infra tied to remote services
- Caller contract changes
- Niche-specific custom ranking policies beyond a small shared baseline

## Non-Negotiables

- `MemoryStore.search(...)` must remain stable
- Reranking off must preserve current Retrieval v1 behavior
- Tests must stay deterministic and runnable locally
- Explanation fields (`why_matched`) must remain intelligible after reranking

## Acceptance Criteria

- A reranking seam exists and can be switched on/off without caller churn
- Retrieval v1 baseline remains green when reranking is disabled
- Focused tests cover reranked ordering and fallback behavior
- Graph recall remains deferred to a separate change
