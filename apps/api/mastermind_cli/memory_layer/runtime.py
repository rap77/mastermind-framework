"""Runtime helpers for building memory-layer backends from environment."""

from __future__ import annotations

import json
import os

from .contracts import (
    MemoryGraphRecallProvider,
    MemoryIndexProvider,
    MemoryReranker,
    VectorSearchProvider,
)
from .graph_recall import (
    MetadataMemoryGraphRecallProvider,
    NoopMemoryGraphRecallProvider,
    StaticMemoryGraphRecallProvider,
)
from .service import MemoryService
from .store_engram import (
    EngramMemoryStore,
    GetObservationCallable,
    SaveObservationCallable,
    SaveSessionSummaryCallable,
    SearchObservationsCallable,
)
from .indexing import create_memory_index_provider
from .models import MemorySearchResult
from .reranking import HeuristicMemoryReranker, NoopMemoryReranker
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


def build_reranker_from_env() -> MemoryReranker:
    """Build a configured reranker using the current process environment."""
    backend = os.environ.get("MM_MEMORY_RERANKER_BACKEND", "none").strip().lower()
    if backend in {"", "none", "off", "disabled"}:
        return NoopMemoryReranker()
    if backend == "heuristic":
        return HeuristicMemoryReranker()
    raise ValueError(
        f"Unsupported reranker backend: {backend!r}. Usa none o heuristic."
    )


def build_graph_recall_from_env(
    database_url: str | None = None,
) -> MemoryGraphRecallProvider:
    """Build a configured graph recall provider using the current environment."""
    backend = os.environ.get("MM_MEMORY_GRAPH_RECALL_BACKEND", "none").strip().lower()
    if backend in {"", "none", "off", "disabled"}:
        return NoopMemoryGraphRecallProvider()
    if backend == "metadata":
        if not database_url:
            raise ValueError(
                "database_url es requerido cuando "
                "MM_MEMORY_GRAPH_RECALL_BACKEND=metadata"
            )
        return MetadataMemoryGraphRecallProvider(database_url)
    if backend == "static":
        raw_map = os.environ.get("MM_MEMORY_GRAPH_RECALL_STATIC_MAP", "").strip()
        if not raw_map:
            raise ValueError(
                "MM_MEMORY_GRAPH_RECALL_STATIC_MAP es requerido cuando "
                "MM_MEMORY_GRAPH_RECALL_BACKEND=static"
            )
        parsed = json.loads(raw_map)
        if not isinstance(parsed, dict):
            raise ValueError(
                "MM_MEMORY_GRAPH_RECALL_STATIC_MAP debe ser un JSON object"
            )
        related_map: dict[str, list[MemorySearchResult]] = {}
        for memory_id, related_results in parsed.items():
            if not isinstance(related_results, list):
                raise ValueError(
                    "MM_MEMORY_GRAPH_RECALL_STATIC_MAP debe mapear cada memory_id a una lista"
                )
            related_map[str(memory_id)] = [
                MemorySearchResult.model_validate(item) for item in related_results
            ]
        return StaticMemoryGraphRecallProvider(related_map)
    raise ValueError(
        f"Unsupported graph recall backend: {backend!r}. Usa none, metadata o static."
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
    reranker = build_reranker_from_env()
    graph_recall = build_graph_recall_from_env(database_url)

    if enable_vector:
        vector_provider = build_vector_provider_from_env(database_url)

    if enable_index:
        index_provider = build_index_provider_from_env(database_url)

    return PostgresMemoryStore(
        database_url,
        vector_provider=vector_provider,
        reranker=reranker,
        graph_recall=graph_recall,
        index_provider=index_provider,
    )


def build_memory_service_from_env(
    database_url: str,
    *,
    enable_vector: bool = True,
    enable_index: bool = True,
) -> MemoryService:
    """Build the first-party MemoryService from the current process environment."""
    return MemoryService(
        build_memory_store_from_env(
            database_url,
            enable_vector=enable_vector,
            enable_index=enable_index,
        )
    )


def build_engram_memory_store(
    *,
    save_observation: SaveObservationCallable,
    search_observations: SearchObservationsCallable,
    get_observation: GetObservationCallable | None = None,
    save_session_summary: SaveSessionSummaryCallable | None = None,
) -> EngramMemoryStore:
    """Create the transitional Engram bridge store from raw hooks."""
    return EngramMemoryStore(
        save_observation=save_observation,
        search_observations=search_observations,
        get_observation=get_observation,
        save_session_summary=save_session_summary,
    )


def build_engram_bridge_store(
    *,
    save_observation: SaveObservationCallable,
    search_observations: SearchObservationsCallable,
    get_observation: GetObservationCallable | None = None,
    save_session_summary: SaveSessionSummaryCallable | None = None,
) -> EngramMemoryStore:
    """Backward-compatible alias for the transitional Engram bridge store."""
    return build_engram_memory_store(
        save_observation=save_observation,
        search_observations=search_observations,
        get_observation=get_observation,
        save_session_summary=save_session_summary,
    )


__all__ = [
    "build_engram_memory_store",
    "build_graph_recall_from_env",
    "build_index_provider_from_env",
    "build_engram_bridge_store",
    "build_memory_service_from_env",
    "build_memory_store_from_env",
    "build_reranker_from_env",
    "build_vector_provider_from_env",
]
