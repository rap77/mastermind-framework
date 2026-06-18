"""Tests for memory-item indexing provider selection."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.indexing import (
    NoopMemoryIndexProvider,
    UnsupportedMemoryIndexProvider,
    create_memory_index_provider,
)
from mastermind_cli.memory_layer.pgvector import PgvectorMemoryIndexProvider
from mastermind_cli.memory_layer.models import MemoryIndexPayload


def test_create_memory_index_provider_defaults_to_noop() -> None:
    """The default index backend should do nothing."""
    provider = create_memory_index_provider()

    assert isinstance(provider, NoopMemoryIndexProvider)


@pytest.mark.asyncio
async def test_noop_memory_index_provider_accepts_upsert() -> None:
    """The no-op index provider should safely accept saved memory items."""
    provider = create_memory_index_provider("none")

    await provider.upsert(
        MemoryIndexPayload(
            memory_id="mem-1",
            memory_type="lesson",
            title="Avoid retrieval drift",
            content="Keep lexical and semantic layers decoupled until indexing exists.",
            tags=["lesson"],
            embedding_text="type: lesson\ntitle: Avoid retrieval drift",
        )
    )


def test_create_memory_index_provider_accepts_pgvector_stub() -> None:
    """Pgvector without a database URL should stay as an explicit stub."""
    provider = create_memory_index_provider("pgvector")

    assert isinstance(provider, UnsupportedMemoryIndexProvider)


def test_create_memory_index_provider_builds_real_pgvector_provider() -> None:
    """Pgvector should become real when DB and embedding backend are configured."""
    provider = create_memory_index_provider(
        "pgvector",
        database_url="postgresql://memory-db",
        embedding_backend="none",
    )

    assert isinstance(provider, PgvectorMemoryIndexProvider)


@pytest.mark.asyncio
async def test_unsupported_memory_index_provider_fails_with_clear_message() -> None:
    """Unwired index backends should fail loudly when used."""
    provider = create_memory_index_provider("qdrant")

    with pytest.raises(NotImplementedError, match="qdrant"):
        await provider.upsert(
            MemoryIndexPayload(
                memory_id="mem-2",
                memory_type="lesson",
                title="Customer graph note",
                content="Future semantic indexing will route here.",
                tags=[],
                embedding_text="type: lesson\ntitle: Customer graph note",
            )
        )


def test_create_memory_index_provider_rejects_unknown_backend() -> None:
    """Unknown backend names should fail validation early."""
    with pytest.raises(ValueError, match="Unsupported memory index backend"):
        create_memory_index_provider("mystery")
