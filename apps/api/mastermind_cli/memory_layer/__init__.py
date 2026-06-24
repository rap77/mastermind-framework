"""Memory Layer contracts and models for first-party persistent memory."""

from .contracts import (
    EmbeddingProvider,
    MemoryGraphRecallProvider,
    MemoryReranker,
    MemoryIndexProvider,
    MemoryStore,
    VectorCandidateProvider,
    VectorSearchProvider,
)
from .graph_recall import (
    MetadataMemoryGraphRecallProvider,
    NoopMemoryGraphRecallProvider,
    StaticMemoryGraphRecallProvider,
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
    RetrievalEvalCase,
    RetrievalEvalCaseResult,
    RetrievalEvalReport,
    VectorCandidate,
)
from .evaluation import EvalHarnessService
from .evaluation_baseline import (
    BASELINE_PROJECT_ID,
    build_retrieval_baseline_cases,
    build_retrieval_baseline_fixture,
    seed_retrieval_baseline_fixture,
)
from .service import MemoryService
from .store_engram import EngramMemoryStore
from .pgvector import PgvectorMemoryIndexProvider, PgvectorVectorSearchProvider
from .runtime import (
    build_graph_recall_from_env,
    build_index_provider_from_env,
    build_memory_store_from_env,
    build_reranker_from_env,
    build_vector_provider_from_env,
)
from .reranking import HeuristicMemoryReranker, NoopMemoryReranker
from .store_postgres import PostgresMemoryStore
from .vector import (
    CallableVectorCandidateProvider,
    CallableVectorSearchProvider,
    NoopVectorSearchProvider,
    UnsupportedVectorSearchProvider,
    create_vector_search_provider,
)

__all__ = [
    "CallableVectorCandidateProvider",
    "CallableVectorSearchProvider",
    "EmbeddingProvider",
    "MemoryGraphRecallProvider",
    "MemoryContextBundle",
    "MemoryIndexPayload",
    "MemoryReranker",
    "MemoryIndexProvider",
    "EngramMemoryStore",
    "MemoryItem",
    "MemorySearchResult",
    "MemoryService",
    "MemoryStore",
    "EvalHarnessService",
    "HeuristicMemoryReranker",
    "MetadataMemoryGraphRecallProvider",
    "NoopMemoryReranker",
    "NoopMemoryGraphRecallProvider",
    "StaticMemoryGraphRecallProvider",
    "NoopEmbeddingProvider",
    "NoopMemoryIndexProvider",
    "NoopVectorSearchProvider",
    "RetrievalEvalCase",
    "RetrievalEvalCaseResult",
    "RetrievalEvalReport",
    "PostgresMemoryStore",
    "PgvectorMemoryIndexProvider",
    "PgvectorVectorSearchProvider",
    "SentenceTransformerEmbeddingProvider",
    "UnsupportedMemoryIndexProvider",
    "UnsupportedVectorSearchProvider",
    "VectorCandidate",
    "VectorCandidateProvider",
    "VectorSearchProvider",
    "build_graph_recall_from_env",
    "build_index_provider_from_env",
    "build_memory_embedding_text",
    "build_memory_index_payload",
    "build_memory_store_from_env",
    "build_reranker_from_env",
    "BASELINE_PROJECT_ID",
    "build_retrieval_baseline_cases",
    "build_retrieval_baseline_fixture",
    "build_vector_provider_from_env",
    "create_embedding_provider",
    "create_memory_index_provider",
    "create_vector_search_provider",
    "seed_retrieval_baseline_fixture",
]
