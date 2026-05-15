# Phase 20 — Domain Brain Outputs
> Generated: 2026-05-14
> Status: complete

## Brain #5 — Backend Architecture

### Migration Pattern
- Use custom migrate.py (NOT Alembic) — codebase has NO Alembic, uses raw SQL + schema_migrations table
- New module: `apps/api/mastermind_cli/rag/` with `migrate.py` + `migrations/004_brain_embeddings.sql`
- SQL file uses `brain_id INTEGER NOT NULL REFERENCES brain_registry(brain_id) ON DELETE CASCADE`
- Column naming correction: `collection TEXT` (not `collection_type`) + `content TEXT` (not `chunk_text`) + `metadata JSONB DEFAULT '{}'`

### HNSW Parameters
- m=16, ef_construction=64 → correct for ~1400 vectors initial scale (~4.6MB index)
- `vector_cosine_ops` in index definition is NON-OPTIONAL — must match `<=>` operator or falls back to seq scan
- Parameters adequate up to ~100k vectors; revisit at m=32, ef_construction=128 when scale demands
- **CRITICAL:** Docker image must be `pgvector/pgvector:pg16` NOT `postgres:16`

### asyncpg + pgvector Query
- Pass embedding as string with explicit `::vector` cast — DO NOT pass Python list directly
- Pattern: `embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"`
- Query uses `ORDER BY embedding <=> $1::vector LIMIT $n`
- `<=>` cosine distance + `vector_cosine_ops` index = HNSW acceleration

### sentence-transformers Loading
- Load in existing FastAPI lifespan in `app.py` → `app.state.embedding_model`
- `SentenceTransformer.encode()` is SYNCHRONOUS — must offload to thread pool for batch ingestion
- Pattern: `await loop.run_in_executor(None, partial(model.encode, texts, normalize_embeddings=True))`
- `normalize_embeddings=True` is NON-OPTIONAL for meaningful `<=>` comparisons
- FastAPI dependency: `def get_embedding_model(request: Request) -> SentenceTransformer`

### LangSmith @traceable
- Works with async def — wraps coroutine correctly
- asyncpg.Connection is NOT JSON-serializable → don't pass as function argument (dispatch() doesn't, safe)
- Without `LANGCHAIN_TRACING_V2=true` + valid key → complete no-op, zero overhead
- Decorator: `@traceable(name="mm_brain_dispatch", run_type="chain")`

### Hard Prerequisites (verified against codebase)
1. `uv add sentence-transformers` — currently dev-only, crashes Docker
2. `uv add langsmith` — completely absent from uv.lock
3. `uv add pgvector` — needed for codec registration in tests
4. docker-compose.yml postgres image must be `pgvector/pgvector:pg16`

---

## Brain #6 — QA/DevOps

### Migration Tests
- BOTH unit (mock asyncpg) AND integration (real DB, `@pytest.mark.integration`) required
- Unit: capture `conn.execute.call_args_list` and assert SQL content was passed
- Integration: test schema after migration + drop table in teardown for idempotency
- Integration tests do NOT run in default `uv run pytest` — separate CI job

### EmbeddingService Tests
- Mock SentenceTransformer at conftest.py level — session-scoped, opt-in (NOT autouse)
- `fake_model.encode` returns `np.random.rand(batch_size, 384).astype(np.float32)` — note 384 not 768 for MiniLM-L6
- Assert on dimension and type, not specific float values

### asyncpg + pgvector Codec
- `register_vector(conn)` is per-connection (not pool-level for tests)
- Fixture order: connect → `CREATE EXTENSION IF NOT EXISTS vector` → `register_vector(conn)` → run test
- Pool-level: `init=init_pool_connection` where `init_pool_connection` calls `await register_vector(conn)`
- Guard: `pytest.skip("pgvector not installed")` if import fails — don't fail the offline suite

### LangSmith Mock
- Replace `langsmith.traceable` with passthrough factory in tests
- AST gate test (like Phase 19 auth gate): verify `@traceable` present on `dispatch()` via `ast.walk()`
- AST test runs OFFLINE — zero imports of dispatch_engine, zero network

### Acceptance Criteria Split
- Offline (no DB): migration unit tests, embed unit tests, search `<=>` operator test, AST gate
- Integration (requires DB): brain_embeddings table exists, HNSW index has vector_cosine_ops
- Target after Phase 20: ~1147 backend tests (unit), ~4 integration tests tagged separately

### Files to Create (TDD order)
1. `tests/unit/test_migrations_runner.py`
2. `tests/unit/test_embedding_service.py`
3. `tests/unit/test_dispatch_engine_contract.py` (AST gate)
4. `tests/integration/test_brain_embeddings_migration.py`
5. `tests/integration/conftest.py` (pg_conn_with_vector fixture)

---

## Dispatch Meta
| Property | Value |
|----------|-------|
| Total brains dispatched | 2 (#5 Backend, #6 QA) |
| All returned successfully | yes |
| Key conflicts | None — brains agreed on all major decisions |
| Embedding dimension | Brain #5 says 768 (all-mpnet-base-v2), Brain #6 says 384 (MiniLM-L6) — needs resolution |
