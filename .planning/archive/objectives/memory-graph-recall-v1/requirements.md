# Requirements — memory-graph-recall-v1

## Goal

Add the first graph-aware retrieval slice after Retrieval v1 + reranking, improving relational recall without changing the stable `MemoryStore.search(...)` caller contract.

## In Scope

- Define minimal graph recall over memory/runtime relations
- Add relational expansion after retrieval candidates are selected
- Keep graph recall optional and local-first
- Reuse retrieval baseline/eval conventions where possible

## Out of Scope

- Full graph database adoption
- Broad domain ontology expansion
- Remote graph services
- Caller contract changes

## Acceptance Criteria

- A separate graph recall seam is defined
- Focused tests prove relational expansion behavior
- Existing retrieval and reranking behavior remain stable when graph recall is off
