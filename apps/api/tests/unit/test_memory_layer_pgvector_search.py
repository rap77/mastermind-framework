"""Tests for the pgvector-backed memory search provider."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.pgvector import PgvectorVectorSearchProvider


class StubEmbeddingProvider:
    """Simple embedding stub for pgvector search provider tests."""

    def __init__(self, values: list[list[float]]) -> None:
        self._values = values

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        del texts
        return self._values


class FakeResult:
    """Tiny fetchall-compatible result wrapper."""

    def __init__(self, rows: list[tuple[object, ...]]) -> None:
        self._rows = rows

    def fetchone(self) -> tuple[object, ...] | None:
        return self._rows[0] if self._rows else None

    def fetchall(self) -> list[tuple[object, ...]]:
        return self._rows

    def scalar(self) -> object | None:
        row = self.fetchone()
        return row[0] if row else None


class FakeConnection:
    """Collect SQL statements executed inside engine.begin()."""

    def __init__(
        self,
        sink: list[tuple[str, dict[str, object] | None]],
        result_rows: list[tuple[object, ...]],
    ) -> None:
        self._sink = sink
        self._result_rows = result_rows

    def execute(
        self, statement: object, params: dict[str, object] | None = None
    ) -> FakeResult:
        self._sink.append((str(statement), params))
        return FakeResult(self._result_rows)


class FakeBeginContext:
    """Context manager returned by the fake engine."""

    def __init__(
        self,
        sink: list[tuple[str, dict[str, object] | None]],
        result_rows: list[tuple[object, ...]],
    ) -> None:
        self._sink = sink
        self._result_rows = result_rows

    def __enter__(self) -> FakeConnection:
        return FakeConnection(self._sink, self._result_rows)

    def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
        del exc_type, exc, tb
        return False


class FakeEngine:
    """Very small fake engine implementing begin()."""

    def __init__(self, result_rows: list[tuple[object, ...]]) -> None:
        self.calls: list[tuple[str, dict[str, object] | None]] = []
        self._result_rows = result_rows

    def begin(self) -> FakeBeginContext:
        return FakeBeginContext(self.calls, self._result_rows)


def test_pgvector_search_provider_requires_postgresql_url() -> None:
    """The pgvector search provider should reject non-PostgreSQL URLs."""
    with pytest.raises(ValueError, match="PostgreSQL"):
        PgvectorVectorSearchProvider(
            "sqlite:///memory.db",
            StubEmbeddingProvider([[0.1] * 768]),
        )


@pytest.mark.asyncio
async def test_pgvector_search_provider_returns_ranked_memory_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Search should read ranked memory IDs from mm_memory_embeddings."""
    engine = FakeEngine([("mem-1",), ("mem-2",)])
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorVectorSearchProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1] * 768]),
    )

    results = await provider.search(
        "customer graph",
        scope={"project_id": "proj-001", "niche": "software-development"},
        limit=2,
    )

    assert results == ["mem-1", "mem-2"]
    search_params = next(
        params for statement, params in engine.calls if "SELECT memory_id" in statement
    )
    assert search_params is not None
    assert search_params["project_id"] == "proj-001"
    assert search_params["niche"] == "software-development"
    assert search_params["limit"] == 2


@pytest.mark.asyncio
async def test_pgvector_search_provider_returns_empty_when_no_embedding_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """No query embeddings should mean no DB search work."""
    engine = FakeEngine([("mem-1",)])
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorVectorSearchProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([]),
    )

    results = await provider.search("customer graph", {"project_id": "proj-001"}, 3)

    assert results == []
    assert engine.calls == []


@pytest.mark.asyncio
async def test_pgvector_search_provider_rejects_wrong_embedding_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Wrong query embedding sizes should fail fast before DB reads."""
    engine = FakeEngine([])
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorVectorSearchProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1, 0.2]]),
        dimensions=768,
    )

    with pytest.raises(ValueError, match="Expected embedding dimension 768"):
        await provider.search("customer graph", {"project_id": "proj-001"}, 3)

    assert engine.calls == []


@pytest.mark.asyncio
async def test_pgvector_search_provider_infers_query_embedding_dimension(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The search provider should infer query vector size when using a non-default model."""
    engine = FakeEngine([("mem-1",)])
    monkeypatch.setattr(
        "mastermind_cli.memory_layer.pgvector.get_engine", lambda _: engine
    )

    provider = PgvectorVectorSearchProvider(
        "postgresql://memory-db",
        StubEmbeddingProvider([[0.1, 0.2, 0.3]]),
        dimensions=None,
    )

    results = await provider.search("customer graph", {"project_id": "proj-001"}, 1)

    assert results == ["mem-1"]
    statements = [statement for statement, _ in engine.calls]
    assert any("embedding vector(3) NOT NULL" in statement for statement in statements)
