"""Runtime helpers for building memory-layer backends from environment."""

from __future__ import annotations

import os

from .contracts import MemoryIndexProvider, VectorSearchProvider
from .indexing import create_memory_index_provider
from .store_postgres import PostgresMemoryStore
from .vector import create_vector_search_provider

_DEFAULT_EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
_DEFAULT_EMBEDDING_BASE_URL = "http://localhost:11434"


def build_vector_provider_from_env(
    database_url: str | None = None,
) -> VectorSearchProvider:
    """Build a configured vector provider using the current process environment."""
    return create_vector_search_provider(
        os.environ.get("MM_MEMORY_VECTOR_BACKEND", "none"),
        database_url=database_url,
        embedding_backend=os.environ.get("MM_MEMORY_EMBEDDING_BACKEND", "none"),
        embedding_model=os.environ.get(
            "MM_MEMORY_EMBEDDING_MODEL",
            _DEFAULT_EMBEDDING_MODEL,
        ),
        embedding_base_url=os.environ.get(
            "MM_MEMORY_EMBEDDING_BASE_URL",
            os.environ.get("OLLAMA_HOST", _DEFAULT_EMBEDDING_BASE_URL),
        ),
    )


def build_index_provider_from_env(database_url: str) -> MemoryIndexProvider:
    """Build a configured index provider using the current process environment."""
    return create_memory_index_provider(
        os.environ.get("MM_MEMORY_INDEX_BACKEND", "none"),
        database_url=database_url,
        embedding_backend=os.environ.get("MM_MEMORY_EMBEDDING_BACKEND", "none"),
        embedding_model=os.environ.get(
            "MM_MEMORY_EMBEDDING_MODEL",
            _DEFAULT_EMBEDDING_MODEL,
        ),
        embedding_base_url=os.environ.get(
            "MM_MEMORY_EMBEDDING_BASE_URL",
            os.environ.get("OLLAMA_HOST", _DEFAULT_EMBEDDING_BASE_URL),
        ),
    )


def build_memory_store_from_env(
    database_url: str,
    *,
    enable_vector: bool = True,
    enable_index: bool = True,
) -> PostgresMemoryStore:
    """Build a configured memory store using the current process environment."""
    vector_provider = None
    index_provider = None

    if enable_vector:
        vector_provider = build_vector_provider_from_env(database_url)

    if enable_index:
        index_provider = build_index_provider_from_env(database_url)

    return PostgresMemoryStore(
        database_url,
        vector_provider=vector_provider,
        index_provider=index_provider,
    )


__all__ = [
    "build_index_provider_from_env",
    "build_memory_store_from_env",
    "build_vector_provider_from_env",
]
