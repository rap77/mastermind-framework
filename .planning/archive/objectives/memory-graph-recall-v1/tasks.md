# Tasks — memory-graph-recall-v1

## GR1: Define graph recall seam

- [x] Add `MemoryGraphRecallProvider` protocol and default noop implementation.
- [x] Wire graph recall expansion into `PostgresMemoryStore.search(...)` after reranking without changing existing callers.
- [x] Cover the seam with focused unit tests.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest -q tests/unit -k 'memory and graph'`

## GR2: Add minimal relational expansion

- [x] Add `StaticMemoryGraphRecallProvider` for deterministic related-result expansion.
- [x] Append unique related memories after the ranked seed set and mark them with `why_matched='graph:related'`.
- [x] Cover relational expansion in provider and store integration tests.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest -q tests/unit -k 'graph_recall or memory_graph'`

## GR3: Close graph recall v1

- [x] Update AI-DLC state and closure notes for graph recall v1.
- [x] Run the focused retrieval regression suite and record the result.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/unit/test_memory_eval_harness.py tests/unit/test_memory_layer_postgres_store.py -q`
