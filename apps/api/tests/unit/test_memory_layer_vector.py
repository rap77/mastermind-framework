"""Tests for vector-provider selection in the first-party memory layer."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.vector import (
    NoopVectorSearchProvider,
    UnsupportedVectorSearchProvider,
    create_vector_search_provider,
)
from mastermind_cli.memory_layer.pgvector import PgvectorVectorSearchProvider


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
