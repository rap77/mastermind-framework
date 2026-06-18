"""Memory Layer contracts and models for first-party persistent memory."""

from .contracts import (
    EmbeddingProvider,
    MemoryIndexProvider,
    MemoryStore,
    VectorSearchProvider,
)
from .embeddings import (
    NoopEmbeddingProvider,
    SentenceTransformerEmbeddingProvider,
    build_memory_embedding_text,
    build_memory_index_payload,
    create_embedding_provider,
)
from .indexing import (
    NoopMemoryIndexProvider,
    UnsupportedMemoryIndexProvider,
    create_memory_index_provider,
)
from .models import (
    MemoryContextBundle,
    MemoryIndexPayload,
    MemoryItem,
    MemorySearchResult,
)
from .service import MemoryService
from .store_engram import EngramMemoryStore
from .pgvector import PgvectorMemoryIndexProvider, PgvectorVectorSearchProvider
from .runtime import (
    build_index_provider_from_env,
    build_memory_store_from_env,
    build_vector_provider_from_env,
)
from .store_postgres import PostgresMemoryStore
from .vector import (
    CallableVectorSearchProvider,
    NoopVectorSearchProvider,
    UnsupportedVectorSearchProvider,
    create_vector_search_provider,
)

__all__ = [
    "CallableVectorSearchProvider",
    "EmbeddingProvider",
    "MemoryContextBundle",
    "MemoryIndexPayload",
    "MemoryIndexProvider",
    "EngramMemoryStore",
    "MemoryItem",
    "MemorySearchResult",
    "MemoryService",
    "MemoryStore",
    "NoopEmbeddingProvider",
    "NoopMemoryIndexProvider",
    "NoopVectorSearchProvider",
    "PostgresMemoryStore",
    "PgvectorMemoryIndexProvider",
    "PgvectorVectorSearchProvider",
    "SentenceTransformerEmbeddingProvider",
    "UnsupportedMemoryIndexProvider",
    "UnsupportedVectorSearchProvider",
    "VectorSearchProvider",
    "build_index_provider_from_env",
    "build_memory_embedding_text",
    "build_memory_index_payload",
    "build_memory_store_from_env",
    "build_vector_provider_from_env",
    "create_embedding_provider",
    "create_memory_index_provider",
    "create_vector_search_provider",
]
