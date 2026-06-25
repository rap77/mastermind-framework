# Tasks — memory-retrieval-v1

## MR1: Refactor lexical retrieval into explicit internal stages

### Purpose

Turn `PostgresMemoryStore.search(...)` into a retrieval pipeline that can later accept vector candidates and fusion without breaking the contract.

### Validation

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k 'memory_layer and search'`

### Acceptance Criteria

- [ ] Lexical retrieval helpers exist with deterministic behavior
- [ ] Existing search contract remains unchanged
- [ ] Focused tests cover candidate ordering and scoping

## MR2: Add retrieval fixtures and baseline eval cases

### Purpose

Create a tiny fixed retrieval benchmark before introducing more sophistication.

### Validation

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k 'memory_retrieval or retrieval_eval'`

### Acceptance Criteria

- [ ] Fixed retrieval fixtures exist
- [ ] Queries have expected hit assertions
- [ ] The baseline can be reused for later BM25/vector/fusion work

## MR3: Add vector search seam without forcing full infra

### Purpose

Define the internal seam for vector candidates while keeping the slice implementable locally.

### Validation

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k 'memory_layer and vector'`

### Acceptance Criteria

- [ ] Vector retrieval seam is explicit
- [ ] Lexical fallback still works when vector infra is absent
- [ ] Callers do not need to change

## MR4: Add simple fusion and close Retrieval v1

### Purpose

Introduce the first fusion strategy and leave the next work clearly queued.

### Validation

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit -k 'memory_layer and retrieval'`

### Acceptance Criteria

- [ ] Retrieval can combine lexical and vector candidates
- [ ] Baseline eval remains green
- [ ] Reranking and graph recall are explicitly deferred to the next change
