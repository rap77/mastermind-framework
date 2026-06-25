# Tasks — memory-reranking-v1

## RR1: Add reranking seam and noop provider

### Purpose

Create an internal reranking seam that can be enabled later without changing callers.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/unit/test_memory_layer_postgres_store.py tests/unit/test_memory_layer_vector.py -q`

### Acceptance Criteria

- [x] Reranking contract exists
- [x] Noop reranker preserves current Retrieval v1 behavior
- [x] Callers remain unchanged

## RR2: Add heuristic reranking

### Purpose

Improve ordering with local deterministic boosts before any model-based reranker.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/unit/test_memory_layer_postgres_store.py tests/unit/test_memory_eval_harness.py -q`

### Acceptance Criteria

- [x] Heuristic reranking can reorder fused candidates
- [x] Baseline stays green when reranking is off
- [x] Focused tests prove the new ordering behavior

## RR3: Close reranking v1 and queue graph recall

### Purpose

Document reranking as complete and explicitly defer graph-aware retrieval.

### Validation

- `cd apps/api && UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync python -m pytest tests/unit/test_memory_eval_harness.py tests/unit/test_memory_layer_postgres_store.py tests/unit/test_memory_layer_vector.py -q`

### Acceptance Criteria

- [x] Retrieval v1 + reranking path is documented
- [x] Graph recall is explicitly queued as the next separate change
- [x] AI-DLC artifacts reflect the new recommended next step
