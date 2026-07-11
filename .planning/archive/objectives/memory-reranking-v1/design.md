# Design — memory-reranking-v1

## Overview

Retrieval v1 already supports lexical candidates, optional vector candidates, and simple fusion. The next smallest improvement is reranking the fused candidate set before final projection.

## Approach

### 1. Keep reranking internal

Do not change:

- `MemoryStore.search(query, scope, limit)`
- `MemoryService.fetch_project_context(...)`

Reranking stays behind the retrieval engine boundary.

### 2. Add a small provider seam

Introduce an internal reranking provider that receives:

- query
- fused candidates
- scope

and returns reordered candidates or adjusted scores.

### 3. Preserve deterministic fallback

If reranking is absent or disabled:

- existing lexical/vector/fusion ordering remains canonical

### 4. Start with heuristic reranking

Before model-based rerankers:

- source boosts
- exact-term boosts
- scope/intent nudges

This keeps the slice local, cheap, and testable.

## Proposed Work Breakdown

### Slice A

- add reranking contract and noop provider
- keep current behavior unchanged by default

### Slice B

- add heuristic reranker
- cover reordering cases with focused tests

### Slice C

- connect reranking to eval harness scenarios
- document graph recall as the next separate change

## Risks

- Blurring reranking with graph recall
- Making score explanations opaque
- Introducing remote-model coupling too early

## Success Condition

At the end of this change, Retrieval v1 can optionally rerank fused candidates while preserving the existing caller contract and deterministic local verification.
