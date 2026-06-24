"""Tests for vector-provider selection in the first-party memory layer."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.vector import (
    CallableVectorCandidateProvider,
    NoopVectorSearchProvider,
    UnsupportedVectorSearchProvider,
    create_vector_search_provider,
)
from mastermind_cli.memory_layer.pgvector import PgvectorVectorSearchProvider
from mastermind_cli.memory_layer.models import VectorCandidate
from mastermind_cli.memory_layer.reranking import (
    HeuristicMemoryReranker,
    NoopMemoryReranker,
)
from mastermind_cli.memory_layer.models import MemorySearchResult


def test_create_vector_search_provider_defaults_to_noop() -> None:
    """The default backend should keep retrieval lexical-only."""
    provider = create_vector_search_provider()

    assert isinstance(provider, NoopVectorSearchProvider)


def test_create_vector_search_provider_accepts_pgvector_stub() -> None:
    """Pgvector without DB config should stay as an explicit stub."""
    provider = create_vector_search_provider("pgvector")

    assert isinstance(provider, UnsupportedVectorSearchProvider)


def test_create_vector_search_provider_builds_real_pgvector_provider() -> None:
    """Pgvector should become real when DB and embedding backend are configured."""
    provider = create_vector_search_provider(
        "pgvector",
        database_url="postgresql://memory-db",
        embedding_backend="none",
    )

    assert isinstance(provider, PgvectorVectorSearchProvider)


@pytest.mark.asyncio
async def test_unsupported_vector_provider_fails_with_clear_message() -> None:
    """Unwired vector backends should fail loudly instead of silently no-oping."""
    provider = create_vector_search_provider("qdrant")

    with pytest.raises(NotImplementedError, match="qdrant"):
        await provider.search("customer graph", {"project_id": "proj-001"}, 3)


def test_create_vector_search_provider_rejects_unknown_backend() -> None:
    """Unknown backend names should fail validation early."""
    with pytest.raises(ValueError, match="Unsupported vector backend"):
        create_vector_search_provider("mystery")


@pytest.mark.asyncio
async def test_callable_vector_candidate_provider_returns_scored_candidates() -> None:
    """Explicit vector candidate adapters should preserve candidate scores."""

    async def fake_search(
        query: str,
        scope: dict[str, str | None] | None,
        limit: int,
    ) -> list[VectorCandidate]:
        assert query == "customer graph"
        assert scope == {"project_id": "proj-001"}
        assert limit == 3
        return [VectorCandidate(memory_id="mem-1", score=0.9)]

    provider = CallableVectorCandidateProvider(fake_search)

    results = await provider.search_candidates(
        "customer graph",
        {"project_id": "proj-001"},
        3,
    )

    assert results == [VectorCandidate(memory_id="mem-1", score=0.9)]


@pytest.mark.asyncio
async def test_noop_memory_reranker_preserves_result_order() -> None:
    """Noop reranker should preserve existing Retrieval v1 ordering exactly."""
    reranker = NoopMemoryReranker()
    results = await reranker.rerank(
        "launch",
        [
            MemorySearchResult(
                memory_id="mem-1",
                title="A",
                snippet="a",
                score=2.0,
                memory_type="lesson",
                project_id="proj-001",
            ),
            MemorySearchResult(
                memory_id="mem-2",
                title="B",
                snippet="b",
                score=1.0,
                memory_type="lesson",
                project_id="proj-001",
            ),
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-2"]


@pytest.mark.asyncio
async def test_heuristic_memory_reranker_boosts_exact_title_match() -> None:
    """Heuristic reranking should prefer exact title matches over raw score alone."""
    reranker = HeuristicMemoryReranker()
    results = await reranker.rerank(
        "launch",
        [
            MemorySearchResult(
                memory_id="mem-1",
                title="Release summary",
                snippet="semantic release planning",
                score=3.0,
                memory_type="lesson",
                project_id="proj-001",
            ),
            MemorySearchResult(
                memory_id="mem-2",
                title="Launch note",
                snippet="brief summary",
                score=2.0,
                memory_type="lesson",
                project_id="proj-001",
            ),
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-2", "mem-1"]
