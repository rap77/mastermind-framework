"""Tests for the pgvector-backed memory index provider."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.models import MemoryIndexPayload
from mastermind_cli.memory_layer.pgvector import PgvectorMemoryIndexProvider


class StubEmbeddingProvider:
    """Simple embedding stub for pgvector provider tests."""

    def __init__(self, values: list[list[float]]) -> None:
        self._values = values

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        del texts
        return self._values


class FakeConnection:
    """Collect SQL statements executed inside engine.begin()."""

    def __init__(
        self,
        sink: list[tuple[str, dict[str, object] | None]],
        *,
        existing_dimensions: int | None = None,
        row_count: int = 0,
    ) -> None:
        self._sink = sink
        self._existing_dimensions = existing_dimensions
        self._row_count = row_count

    def execute(
        self, statement: object, params: dict[str, object] | None = None
    ) -> object:
        text_value = str(statement)
        self._sink.append((text_value, params))
        if "SELECT format_type" in text_value:
            return FakeResult(
                [(f"vector({self._existing_dimensions})",)]
                if self._existing_dimensions is not None
                else []
            )
        if "SELECT COUNT(*) FROM mm_memory_embeddings" in text_value:
            return FakeResult([(self._row_count,)])
        return FakeResult([])


class FakeResult:
    """Tiny result wrapper supporting fetchone/scalar for schema checks."""

    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self._rows = rows

    def fetchone(self) -> tuple[object, ...] | None:
        return self._rows[0] if self._rows else None

    def scalar(self) -> object | None:
        row = self.fetchone()
        return row[0] if row else None


class FakeBeginContext:
    """Context manager returned by the fake engine."""

    def __init__(
        self,
        sink: list[tuple[str, dict[str, object] | None]],
        *,
        existing_dimensions: int | None = None,
        row_count: int = 0,
    ) -> None:
        self._sink = sink
        self._existing_dimensions = existing_dimensions
        self._row_count = row_count

    def __enter__(self) -> FakeConnection:
        return FakeConnection(
            self._sink,
            existing_dimensions=self._existing_dimensions,
            row_count=self._row_count,
        )

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        del exc_type, exc, tb
        return False


class FakeEngine:
    """Very small fake engine implementing begin()."""

    def __init__(
        self,
        *,
        existing_dimensions: int | None = None,
        row_count: int = 0,
    ) -> None:
        self.calls: list[tuple[str, dict[str, object] | None]] = []
        self._existing_dimensions = existing_dimensions
        self._row_count = row_count

    def begin(self) -> FakeBeginContext:
        return FakeBeginContext(
            self.calls,
            existing_dimensions=self._existing_dimensions,
            row_count=self._row_count,
        )


def _payload() -> MemoryIndexPayload:
    """Build a reusable memory index payload for tests."""
    return MemoryIndexPayload(
        memory_id="mem-123",
        memory_type="lesson",
        title="Customer graph note",
        content="Store canonical memory embeddings in a dedicated table.",
        tags=["lesson", "retrieval"],
        project_id="proj-001",
        brain_id="brain-07-growth-data",
        niche="software-development",
        source_ref="run-123",
        embedding_text="type: lesson\ntitle: Customer graph note",
    )


def test_pgvector_provider_requires_postgresql_url() -> None:
    """The pgvector provider should reject non-PostgreSQL URLs."""
    with pytest.raises(ValueError, match="PostgreSQL"):
        PgvectorMemoryIndexProvider(
            "sqlite:///memory.db",
            StubEmbeddingProvider([[0.1] * 768]),
        )


@pytest.mark.asyncio
async def test_pgvector_provider_upsert_creates_schema_and_writes_embedding(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Upsert should create pgvector-owned schema and insert the embedding row."""
    engine = FakeEngine()
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorMemoryIndexProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1] * 768]),
    )

    await provider.upsert(_payload())

    statements = [statement for statement, _ in engine.calls]
    assert any(
        "CREATE EXTENSION IF NOT EXISTS vector" in statement for statement in statements
    )
    assert any(
        "CREATE TABLE IF NOT EXISTS mm_memory_embeddings" in statement
        for statement in statements
    )
    insert_params = next(
        params
        for statement, params in engine.calls
        if "INSERT INTO mm_memory_embeddings" in statement
    )
    assert insert_params is not None
    assert insert_params["memory_id"] == "mem-123"
    assert str(insert_params["embedding"]).startswith("[0.1,0.1")


@pytest.mark.asyncio
async def test_pgvector_provider_skips_db_write_when_no_embeddings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No embeddings should mean no schema or DB write work."""
    engine = FakeEngine()
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorMemoryIndexProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([]),
    )

    await provider.upsert(_payload())

    assert engine.calls == []


@pytest.mark.asyncio
async def test_pgvector_provider_rejects_wrong_embedding_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wrong embedding sizes should fail fast before DB writes."""
    engine = FakeEngine()
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorMemoryIndexProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1, 0.2]]),
        dimensions=768,
    )

    with pytest.raises(ValueError, match="Expected embedding dimension 768"):
        await provider.upsert(_payload())

    assert engine.calls == []


@pytest.mark.asyncio
async def test_pgvector_provider_infers_embedding_dimension_from_first_vector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The provider should infer vector dimensions when the backend is not fixed to 768."""
    engine = FakeEngine()
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorMemoryIndexProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1, 0.2, 0.3]]),
        dimensions=None,
    )

    await provider.upsert(_payload())

    statements = [statement for statement, _ in engine.calls]
    assert any("embedding vector(3) NOT NULL" in statement for statement in statements)


def test_pgvector_schema_auto_migrates_empty_table_dimension() -> None:
    """An empty embeddings table should be widened when the model dimension changes."""
    from mastermind_cli.memory_layer.pgvector import _ensure_pgvector_memory_schema

    engine = FakeEngine(existing_dimensions=768, row_count=0)

    _ensure_pgvector_memory_schema(engine, 1024)

    statements = [statement for statement, _ in engine.calls]
    assert any(
        "ALTER TABLE mm_memory_embeddings" in statement for statement in statements
    )
    assert any("vector(1024)" in statement for statement in statements)


def test_pgvector_schema_rejects_dimension_change_with_existing_rows() -> None:
    """A populated embeddings table should fail loudly on incompatible dimensions."""
    from mastermind_cli.memory_layer.pgvector import _ensure_pgvector_memory_schema

    engine = FakeEngine(existing_dimensions=768, row_count=2)

    with pytest.raises(ValueError, match="uses 768 dimensions"):
        _ensure_pgvector_memory_schema(engine, 1024)
