# Phase 20 — Implementation Context
> Brain consultation complete: #5 Backend + #6 QA + #7 Evaluator
> Brain #7 score: 74/100 — APPROVED_WITH_CONDITIONS
> Generated: 2026-05-14

---

## Hard Prerequisites (must complete before writing any code)

1. `uv add sentence-transformers` — currently dev-only, Docker production crashes
2. `uv add langsmith` — completely absent from uv.lock
3. `uv add pgvector` — needed for codec registration in tests
4. Verify `docker-compose.yml` postgres image = `pgvector/pgvector:pg16` ✅ (already confirmed)

---

## Architecture Decisions (locked)

### 1. Embedding dimension: 768 (all-mpnet-base-v2)

**Single source of truth:** `apps/api/mastermind_cli/rag/constants.py`
```python
EMBEDDING_DIM: int = 768
EMBEDDING_MODEL: str = "sentence-transformers/all-mpnet-base-v2"
```
Migration SQL, EmbeddingService, AND test mock fixtures ALL import `EMBEDDING_DIM` from here.
Brain #6's fixtures used 384 (MiniLM-L6 placeholder) — corrected to 768.

### 2. Migration pattern: custom migrate.py (NOT Alembic)

Follows exact pattern of `brain_registry_module/migrate.py`. New module structure:
```
apps/api/mastermind_cli/rag/
  __init__.py
  constants.py          ← EMBEDDING_DIM = 768
  embed.py              ← EmbeddingService
  search.py             ← similarity_search()
  baseline.py           ← OEC baseline script
  migrate.py            ← copy of brain_registry_module/migrate.py
  migrations/
    004_brain_embeddings.sql
```

### 3. brain_embeddings SQL schema

```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE IF NOT EXISTS brain_embeddings (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id    INTEGER     NOT NULL REFERENCES brain_registry(brain_id) ON DELETE CASCADE,
    collection  TEXT        NOT NULL CHECK(collection IN ('domain_knowledge', 'project_memory')),
    content     TEXT        NOT NULL,
    embedding   vector(768) NOT NULL,  -- all-mpnet-base-v2, 768d
    metadata    JSONB       NOT NULL DEFAULT '{}',
    chunk_hash  TEXT        UNIQUE,    -- SHA256 for idempotent upsert
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_brain_embeddings_hnsw
ON brain_embeddings
USING hnsw (embedding vector_cosine_ops)  -- MUST match <=> operator
WITH (m = 16, ef_construction = 64);

CREATE INDEX IF NOT EXISTS idx_brain_embeddings_lookup
ON brain_embeddings(brain_id, collection);
```

**Note:** `vector_cosine_ops` is NON-OPTIONAL — without it, every `<=>` query falls back to sequential scan.

### 4. asyncpg query pattern

Pass embedding as string with `::vector` cast — NOT as Python list:
```python
embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
await conn.fetch(
    "SELECT content, metadata, (embedding <=> $1::vector) AS distance "
    "FROM brain_embeddings "
    "WHERE brain_id = $2 AND collection = $3 "
    "ORDER BY embedding <=> $1::vector LIMIT $4",
    embedding_str, brain_id, collection, limit
)
```

### 5. sentence-transformers loading: FastAPI lifespan with TESTING guard

```python
# In app.py lifespan:
if not settings.TESTING:  # ← CRITICAL: prevents 400MB load in test suite
    from sentence_transformers import SentenceTransformer
    app.state.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
else:
    app.state.embedding_model = None  # tests override via app.state directly
```

`encode()` is synchronous — offload to thread pool for batch ingestion:
```python
result = await loop.run_in_executor(
    None,
    partial(model.encode, texts, normalize_embeddings=True, show_progress_bar=False)
)
```
`normalize_embeddings=True` is NON-OPTIONAL for meaningful `<=>` comparisons.

### 6. LangSmith @traceable

```python
from langsmith import traceable

class DynamicDispatchEngine:
    @traceable(name="mm_brain_dispatch", run_type="chain")
    async def dispatch(self, ...) -> DispatchResult:
        ...  # zero changes to body
```
Without `LANGCHAIN_TRACING_V2=true` → complete no-op, zero overhead. Safe to ship without configuring key.

### 7. OEC Baseline

`tasks/rag-baseline.json` structure with **`minimum_for_phase21: 50`** enforcement:
```json
{
  "brain_id": "brain-01",
  "rag_enabled": false,
  "sample_count": 0,
  "quality_score_mean": 0.0,
  "quality_score_std": 0.0,
  "measured_at": "2026-05-14T00:00:00Z",
  "oec_target": "mean + 0.08",
  "minimum_for_phase21": 50,
  "note": "Phase 21 A/B blocked until sample_count >= minimum_for_phase21"
}
```
If no experience_records exist: `sample_count: 0` is valid for Phase 20. Phase 21 is blocked automatically.

---

## Test Strategy (TDD order)

### Write tests FIRST (all RED), then implement

**1. Offline unit tests** (no DB, no model):
- `tests/unit/test_migrations_runner.py` — mock asyncpg.connect, assert SQL content passed
- `tests/unit/test_embedding_service.py` — mock SentenceTransformer at conftest (768d arrays)
- `tests/unit/test_dispatch_engine_contract.py` — AST gate: `@traceable` on `dispatch()`

**2. Integration tests** (`@pytest.mark.integration`, requires live DB):
- `tests/integration/test_brain_embeddings_migration.py` — real schema verification
- `tests/integration/conftest.py` — `pg_conn_with_vector` fixture

**3. AST gate** (offline, zero imports):
```python
def test_dispatch_has_traceable_decorator():
    tree = ast.parse(Path("mastermind_cli/mm_flow/dispatch_engine.py").read_text())
    # verify @traceable in dispatch() decorator_list
```

### Test fixture for EmbeddingService (session-scoped, opt-in)
```python
@pytest.fixture(scope="session")
def mock_sentence_transformer():
    from mastermind_cli.rag.constants import EMBEDDING_DIM
    fake = MagicMock()
    fake.encode = MagicMock(
        side_effect=lambda texts, **kw: np.random.rand(len(texts), EMBEDDING_DIM).astype(np.float32)
    )
    with patch("mastermind_cli.rag.embed.SentenceTransformer", return_value=fake):
        yield fake
```

### pgvector codec in integration tests
```python
@pytest_asyncio.fixture(scope="function")
async def pg_conn_with_vector():
    conn = await asyncpg.connect(TEST_DB)
    await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    await register_vector(conn)
    yield conn
    await conn.close()
```

---

## Acceptance Criteria — Verification Map

| Criterion | Verifiable | Command |
|-----------|-----------|---------|
| `sentence-transformers` in runtime deps | ✅ offline | `rg "sentence-transformers" apps/api/pyproject.toml` |
| `langsmith` in runtime deps | ✅ offline | `rg "langsmith" apps/api/pyproject.toml` |
| `rag/constants.py` with `EMBEDDING_DIM=768` | ✅ offline | file exists + grep |
| Migration SQL file exists with vector(768) | ✅ offline | file exists + grep |
| `@traceable` on `dispatch()` | ✅ offline (AST) | `uv run pytest tests/unit/test_dispatch_engine_contract.py` |
| `brain_embeddings` table created | ✅ integration | `-m integration` |
| HNSW index with `vector_cosine_ops` | ✅ integration | `-m integration` |
| `similarity_search()` uses `<=>` | ✅ offline (mock) | `uv run pytest` |
| `tasks/rag-baseline.json` exists | ✅ offline | file exists |
| LangSmith no-op without API key | ✅ offline (mock) | `uv run pytest` |
| Offline suite: zero new failures | ✅ offline | `cd apps/api && uv run pytest` |

---

## Subtasks Redlined by Brain #7

| Original | Redlined | Reason |
|----------|----------|--------|
| `column_type TEXT CHECK(...)` | `collection TEXT CHECK(...)` | Field rename for clarity |
| `chunk_text TEXT` | `content TEXT` | More semantic, matches retrieval terminology |
| Embedding dim: undefined | `vector(768)` from `constants.py` | Prevents 768 vs 384 conflict |
| Load model unconditionally | Load with `settings.TESTING` guard | Prevents 1111-test slowdown |
| OEC baseline: no fallback | `minimum_for_phase21: 50` | Prevents vanity metric |
