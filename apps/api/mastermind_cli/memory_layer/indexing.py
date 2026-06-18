"""Optional indexing providers for future semantic memory retrieval."""

from __future__ import annotations

from .contracts import MemoryIndexProvider
from .embeddings import create_embedding_provider
from .models import MemoryIndexPayload
from .pgvector import PgvectorMemoryIndexProvider


class NoopMemoryIndexProvider:
    """Index provider that deliberately does nothing."""

    async def upsert(self, payload: MemoryIndexPayload) -> None:
        """Skip indexing for installations without semantic retrieval enabled."""
        del payload


class UnsupportedMemoryIndexProvider:
    """Stub index provider for backends that are not wired yet."""

    def __init__(self, backend: str, reason: str) -> None:
        """Store backend metadata for a clear failure message."""
        self._backend = backend
        self._reason = reason

    async def upsert(self, payload: MemoryIndexPayload) -> None:
        """Fail fast when an unwired index backend is selected."""
        del payload
        raise NotImplementedError(
            f"Index backend '{self._backend}' todavía no está conectado: "
            f"{self._reason}"
        )


def create_memory_index_provider(
    backend: str | None = None,
    *,
    database_url: str | None = None,
    embedding_backend: str = "none",
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
    embedding_base_url: str = "http://localhost:11434",
) -> MemoryIndexProvider:
    """Create a memory index provider from a small backend selector."""
    normalized = (backend or "none").strip().lower()

    if normalized in {"", "none", "off", "disabled"}:
        return NoopMemoryIndexProvider()
    if normalized == "pgvector":
        if not database_url:
            return UnsupportedMemoryIndexProvider(
                "pgvector",
                "falta configurar database_url para el backend pgvector",
            )
        return PgvectorMemoryIndexProvider(
            database_url,
            create_embedding_provider(
                embedding_backend,
                model_name=embedding_model,
                base_url=embedding_base_url,
            ),
            embedding_model=embedding_model,
        )
    if normalized == "qdrant":
        return UnsupportedMemoryIndexProvider(
            "qdrant",
            "falta generar embeddings y sincronizar el vector store externo",
        )

    raise ValueError(
        f"Unsupported memory index backend: {backend!r}. "
        "Usa none, pgvector o qdrant."
    )


__all__ = [
    "MemoryIndexProvider",
    "NoopMemoryIndexProvider",
    "UnsupportedMemoryIndexProvider",
    "create_memory_index_provider",
]
