# Handoff — memory-layer-v1

## Current objective

- `memory-layer-v1`

## Decisions already made

- The first slice uses **SDD for planning** and **TDD for execution**.
- `project_state` remains the runtime source of truth; memory is a separate layer.
- Engram is treated as a temporary bridge, not as the primary contract.
- The architecture must support future niches such as investments and marketing.
- The architecture must support lego-style modular packaging and future commercialization.
- ML1 is complete: `MemoryStore`, `MemoryItem`, `MemorySearchResult`, and `MemoryContextBundle` exist with green contract tests.
- ML2 is complete: `EngramMemoryStore` now hides raw Engram observation payloads behind the memory contract with green adapter tests.
- ML3 minimum viable is complete: `PostgresMemoryStore` now persists items, preferences, and session summaries through SQLAlchemy-backed tables owned by the memory layer.
- ML4 is complete: `MemoryService` exists and now has three first real callers wired through the first-party memory layer.
- Session summaries are recorded from `mm_flow.cli --complete --summary`.
- Learning/fix memory is recorded from `ErrorTracker.record_error_memory(...)` as `fix` and `pattern` items.
- Project-scoped backend preference is recorded from `mm_flow.cli start` using `MM_FLOW_BACKEND` and `MM_MEMORY_PROJECT_ID`.
- ML5 is complete: the Phase 1–2 slice was validated, split into atomic commits, and passed GGA, Ruff, and mypy with hooks enabled.
- Phase 1–2 commit checkpoints are:
  - `6997b847` — docs/SDD package
  - `6f5de7c8` — memory layer implementation and initial callers

## Blockers / risks

- The first production callers for session summaries / learnings / preferences are now selected and migrated.
- Migration should avoid pulling hybrid retrieval into the same slice prematurely.
- There is still no in-repo Engram client, so the adapter stays fully dependency-injected until cutover work selects a concrete bridge surface.
- The current ML3 validation uses SQLite URLs for fast deterministic tests even though the runtime target is Postgres; this is acceptable for the contract slice but should be complemented later with a true Postgres integration path if needed.
- Retrieval is still lexical-only in `PostgresMemoryStore.search(...)`; vector search, BM25/RRF, scoping weights, and graph-aware recall are intentionally deferred.
- There is still no first-party eval harness for memory quality, source isolation, or retrieval regressions.

## Exact next recommended task

- Start the follow-on change for **Memory Retrieval v1**.
- First slice recommendation:
  1. define a new SDD package for hybrid retrieval (`vector + lexical + simple fusion`)
  2. keep storage ownership untouched
  3. add a minimal eval baseline for search quality before introducing reranking or graph recall

## Validation commands

- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit/test_memory_layer_contracts.py tests/unit/test_memory_layer_engram_store.py`
- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit/test_memory_layer_postgres_store.py`
- `cd apps/api && . .venv/bin/activate && pytest -q tests/unit/test_memory_layer_service.py tests/unit/test_cli.py -k 'records_session_summary_in_memory_service or start_records_backend_preference_in_memory_service'`
- `cd apps/api && . .venv/bin/activate && pytest -q tests/mm_flow/test_error_tracker.py -k 'record_error_memory'`
- Keep retrieval/graph work explicitly out of Phase 1–2 storage/caller maintenance; open a separate change for retrieval.
