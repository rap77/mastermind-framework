# Requirements — memory-retrieval-v1

## Goal

Add the first retrieval phase on top of the new first-party Memory Layer so MasterMind can search project memory without depending conceptually on Engram.

## In Scope

- Define the first retrieval slice for `PostgresMemoryStore.search(...)`
- Introduce a hybrid retrieval contract for:
  - lexical search
  - vector search
  - simple rank fusion
- Add a minimal evaluation baseline for retrieval quality
- Preserve the existing memory storage contract and initial callers

## Out of Scope

- Reranking
- Graph traversal or graph-aware recall
- Engram cutover
- Full eval harness parity with `gbrain-evals`
- Niche-specific retrieval weighting

## Non-Negotiables

- Keep `project_state` and memory ownership separated
- Keep the slice modular so retrieval can be packaged independently later
- Do not regress the current Phase 1–2 callers
- Keep tests deterministic and local

## Acceptance Criteria

- A new retrieval design exists for lexical + vector + fusion
- Retrieval behavior is covered by focused tests
- A minimal eval baseline exists to compare future retrieval changes
- The next follow-on work after this slice is explicit: reranking, graph recall, and eval expansion
