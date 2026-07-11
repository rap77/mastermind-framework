# Design — memory-retrieval-v1

## Overview

Phase 1–2 established storage and first callers. This change adds the first retrieval plane over that storage without changing ownership or introducing graph complexity too early.

## Approach

### 1. Keep the public search contract stable

The caller-facing contract remains:

- `MemoryStore.search(query, scope, limit)`
- `MemoryService.fetch_project_context(...)`

The implementation behind `PostgresMemoryStore.search(...)` can evolve without forcing caller churn.

### 2. Split retrieval into internal stages

The retrieval path should be structured internally as:

1. lexical candidate generation
2. optional vector candidate generation
3. simple score normalization / fusion
4. projection into `MemorySearchResult`

This keeps the implementation lego-friendly and allows future packaging as:

- retrieval-only
- memory + retrieval
- full MasterMind stack

### 3. Start with deterministic lexical behavior

The first sub-slice should improve lexical retrieval quality in a way that is:

- deterministic
- fully testable locally
- independent from vector infrastructure

Then add vector search behind a clear seam.

### 4. Add a small eval baseline early

Before retrieval becomes more sophisticated, add a tiny in-repo eval baseline:

- fixed fixtures
- fixed queries
- expected hits / ordering rules

This gives a regression floor before BM25/vector/fusion evolve.

## Proposed work breakdown

### Slice A

- refactor lexical retrieval into explicit candidate/ranking helpers
- add deterministic retrieval fixtures and tests

### Slice B

- introduce vector search seam and placeholder implementation contract
- keep green tests with lexical-only fallback

### Slice C

- add simple fusion logic and baseline eval assertions

## Risks

- Mixing retrieval design with graph or reranking too early
- Introducing hidden coupling to Engram search semantics
- Building vector infra before a deterministic lexical baseline exists

## Success Condition

At the end of this change, MasterMind should have a clean Retrieval v1 package over the first-party memory layer, with a small eval baseline and without disturbing Phase 1–2 ownership boundaries.
