"""Optional vector-search providers for the first-party memory layer."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import TypeAlias

from .contracts import VectorSearchProvider
from .embeddings import create_embedding_provider
from .models import VectorCandidate
from .pgvector import PgvectorVectorSearchProvider

VectorSearchCallable: TypeAlias = Callable[
    [str, dict[str, str | None] | None, int],
    Awaitable[list[str]],
]


class NoopVectorSearchProvider:
    """Vector provider that always returns no candidates."""

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Return no vector candidates."""
        del query, scope, limit
        return []


class CallableVectorSearchProvider:
    """Adapter that wraps an async callable in the vector provider protocol."""

    def __init__(self, search_callable: VectorSearchCallable) -> None:
        """Store the wrapped async callable."""
        self._search_callable = search_callable

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Delegate vector candidate lookup to the wrapped callable."""
        return await self._search_callable(query, scope, limit)


class CallableVectorCandidateProvider:
    """Adapter that wraps an async callable returning explicit vector candidates."""

    def __init__(
        self,
        search_callable: Callable[
            [str, dict[str, str | None] | None, int],
            Awaitable[list[VectorCandidate]],
        ],
    ) -> None:
        """Store the wrapped async callable."""
        self._search_callable = search_callable

    async def search_candidates(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[VectorCandidate]:
        """Delegate scored candidate lookup to the wrapped callable."""
        return await self._search_callable(query, scope, limit)


class UnsupportedVectorSearchProvider:
    """Stub provider for configured backends that are not wired yet."""

    def __init__(self, backend: str, reason: str) -> None:
        """Store backend metadata for a clear failure message."""
        self._backend = backend
        self._reason = reason

    async def search(
        self,
        query: str,
        scope: dict[str, str | None] | None = None,
        limit: int = 10,
    ) -> list[str]:
        """Fail fast when an unwired backend is selected."""
        del query, scope, limit
        raise NotImplementedError(
            f"Vector backend '{self._backend}' todavía no está conectado: "
            f"{self._reason}"
        )


def create_vector_search_provider(
    backend: str | None = None,
    *,
    database_url: str | None = None,
    embedding_backend: str = "none",
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
    embedding_base_url: str = "http://localhost:11434",
) -> VectorSearchProvider:
    """Create a vector provider from a small backend selector.

    Supported today:
    - ``none``: returns a no-op provider

    Reserved but not yet wired:
    - ``pgvector``
    - ``qdrant``
    """
    normalized = (backend or "none").strip().lower()

    if normalized in {"", "none", "off", "disabled"}:
        return NoopVectorSearchProvider()
    if normalized == "pgvector":
        if not database_url:
            return UnsupportedVectorSearchProvider(
                "pgvector",
                "falta configurar database_url para el backend pgvector",
            )
        return PgvectorVectorSearchProvider(
            database_url,
            create_embedding_provider(
                embedding_backend,
                model_name=embedding_model,
                base_url=embedding_base_url,
            ),
        )
    if normalized == "qdrant":
        return UnsupportedVectorSearchProvider(
            "qdrant",
            "falta el puente de indexación y la sincronización del vector store",
        )

    raise ValueError(
        f"Unsupported vector backend: {backend!r}. " "Usa none, pgvector o qdrant."
    )


__all__ = [
    "CallableVectorCandidateProvider",
    "CallableVectorSearchProvider",
    "NoopVectorSearchProvider",
    "UnsupportedVectorSearchProvider",
    "VectorSearchCallable",
    "VectorSearchProvider",
    "create_vector_search_provider",
]
