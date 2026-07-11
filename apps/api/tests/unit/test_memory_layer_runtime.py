"""Tests for env-driven memory-layer runtime builders."""

from __future__ import annotations

import pytest

from mastermind_cli.memory_layer.pgvector import PgvectorVectorSearchProvider
from mastermind_cli.memory_layer.runtime import (
    build_engram_bridge_store,
    build_graph_recall_from_env,
    build_index_provider_from_env,
    build_memory_service_from_env,
    build_memory_store_from_env,
    build_reranker_from_env,
    build_vector_provider_from_env,
)
from mastermind_cli.memory_layer.graph_recall import (
    MetadataMemoryGraphRecallProvider,
    StaticMemoryGraphRecallProvider,
)
from mastermind_cli.memory_layer.reranking import HeuristicMemoryReranker
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.memory_layer.store_engram import BridgeMemoryStore
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.memory_layer.vector import NoopVectorSearchProvider


def test_build_vector_provider_from_env_defaults_to_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without explicit env config, vector retrieval should stay disabled."""
    monkeypatch.delenv("MM_MEMORY_VECTOR_BACKEND", raising=False)

    provider = build_vector_provider_from_env("sqlite:///memory.db")

    assert isinstance(provider, NoopVectorSearchProvider)


def test_build_vector_provider_from_env_builds_pgvector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Pgvector vector search should be built from shared env wiring."""
    monkeypatch.setenv("MM_MEMORY_VECTOR_BACKEND", "pgvector")
    monkeypatch.setenv("MM_MEMORY_EMBEDDING_BACKEND", "none")

    provider = build_vector_provider_from_env("postgresql://memory-db")

    assert isinstance(provider, PgvectorVectorSearchProvider)


def test_build_memory_store_from_env_can_disable_index_or_vector(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shared store builder should support focused operational modes."""
    monkeypatch.delenv("MM_MEMORY_VECTOR_BACKEND", raising=False)
    monkeypatch.delenv("MM_MEMORY_INDEX_BACKEND", raising=False)

    store = build_memory_store_from_env(
        "sqlite:///memory.db",
        enable_vector=False,
        enable_index=False,
    )

    assert isinstance(store, PostgresMemoryStore)
    assert store._vector_provider.__class__.__name__ == "NoopVectorSearchProvider"  # type: ignore[attr-defined]
    assert store._index_provider.__class__.__name__ == "NoopMemoryIndexProvider"  # type: ignore[attr-defined]


def test_build_reranker_from_env_builds_heuristic(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Heuristic reranking should be selectable from shared runtime env config."""
    monkeypatch.setenv("MM_MEMORY_RERANKER_BACKEND", "heuristic")

    reranker = build_reranker_from_env()

    assert isinstance(reranker, HeuristicMemoryReranker)


def test_build_graph_recall_from_env_builds_static_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Static graph recall should be selectable from shared runtime env config."""
    monkeypatch.setenv("MM_MEMORY_GRAPH_RECALL_BACKEND", "static")
    monkeypatch.setenv(
        "MM_MEMORY_GRAPH_RECALL_STATIC_MAP",
        """
        {
          "mem-1": [
            {
              "memory_id": "mem-2",
              "title": "Linked decision",
              "snippet": "related",
              "score": 0.5,
              "memory_type": "decision",
              "project_id": "proj-001"
            }
          ]
        }
        """,
    )

    provider = build_graph_recall_from_env()

    assert isinstance(provider, StaticMemoryGraphRecallProvider)


def test_build_graph_recall_from_env_rejects_non_list_static_entries(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Static graph recall should reject malformed adjacency payloads."""
    monkeypatch.setenv("MM_MEMORY_GRAPH_RECALL_BACKEND", "static")
    monkeypatch.setenv(
        "MM_MEMORY_GRAPH_RECALL_STATIC_MAP",
        """
        {
          "mem-1": {
            "memory_id": "mem-2",
            "title": "Linked decision",
            "snippet": "related",
            "score": 0.5,
            "memory_type": "decision",
            "project_id": "proj-001"
          }
        }
        """,
    )

    with pytest.raises(ValueError, match="debe mapear cada memory_id a una lista"):
        build_graph_recall_from_env()


def test_build_graph_recall_from_env_builds_metadata_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Metadata graph recall should be selectable from shared runtime env config."""
    monkeypatch.setenv("MM_MEMORY_GRAPH_RECALL_BACKEND", "metadata")

    provider = build_graph_recall_from_env("sqlite:///memory.db")

    assert isinstance(provider, MetadataMemoryGraphRecallProvider)


def test_build_memory_store_from_env_wires_reranker_and_graph_recall(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shared runtime store builder should wire retrieval follow-ons from env."""
    monkeypatch.delenv("MM_MEMORY_VECTOR_BACKEND", raising=False)
    monkeypatch.delenv("MM_MEMORY_INDEX_BACKEND", raising=False)
    monkeypatch.setenv("MM_MEMORY_RERANKER_BACKEND", "heuristic")
    monkeypatch.setenv("MM_MEMORY_GRAPH_RECALL_BACKEND", "static")
    monkeypatch.setenv(
        "MM_MEMORY_GRAPH_RECALL_STATIC_MAP",
        """
        {
          "mem-1": [
            {
              "memory_id": "mem-2",
              "title": "Linked decision",
              "snippet": "related",
              "score": 0.5,
              "memory_type": "decision",
              "project_id": "proj-001"
            }
          ]
        }
        """,
    )

    store = build_memory_store_from_env(
        "sqlite:///memory.db",
        enable_vector=False,
        enable_index=False,
    )

    assert isinstance(store, PostgresMemoryStore)
    assert isinstance(store._reranker, HeuristicMemoryReranker)  # type: ignore[attr-defined]
    assert isinstance(store._graph_recall, StaticMemoryGraphRecallProvider)  # type: ignore[attr-defined]


def test_build_memory_service_from_env_wraps_shared_store() -> None:
    """The runtime helper should build the first-party service over the shared store."""

    service = build_memory_service_from_env(
        "sqlite:///memory.db",
        enable_vector=False,
        enable_index=False,
    )

    assert isinstance(service, MemoryService)


def test_build_engram_bridge_store_builds_adapter() -> None:
    """The runtime helper should expose the transitional Engram bridge as a store."""

    async def save_observation(**_: object) -> dict[str, object]:
        return {"id": "mem-1"}

    async def search_observations(**_: object) -> list[dict[str, object]]:
        return []

    store = build_memory_store_from_env(
        "sqlite:///memory.db",
        enable_vector=False,
        enable_index=False,
    )
    assert isinstance(store, PostgresMemoryStore)

    engram_store = build_engram_bridge_store(
        save_observation=save_observation,
        search_observations=search_observations,
    )

    assert isinstance(engram_store, BridgeMemoryStore)


def test_build_index_provider_from_env_defaults_to_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Without explicit env config, indexing should stay disabled."""
    monkeypatch.delenv("MM_MEMORY_INDEX_BACKEND", raising=False)

    provider = build_index_provider_from_env("sqlite:///memory.db")

    assert provider.__class__.__name__ == "NoopMemoryIndexProvider"


def test_build_index_provider_from_env_passes_ollama_host(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Ollama embedding config should flow through the shared runtime builder."""
    captured: dict[str, object] = {}

    def fake_create_memory_index_provider(
        backend: str | None = None,
        *,
        database_url: str | None = None,
        embedding_backend: str = "none",
        embedding_model: str = "sentence-transformers/all-mpnet-base-v2",
        embedding_base_url: str = "http://localhost:11434",
    ) -> object:
        captured["backend"] = backend
        captured["database_url"] = database_url
        captured["embedding_backend"] = embedding_backend
        captured["embedding_model"] = embedding_model
        captured["embedding_base_url"] = embedding_base_url
        return object()

    monkeypatch.setattr(
        "mastermind_cli.memory_layer.runtime.create_memory_index_provider",
        fake_create_memory_index_provider,
    )
    monkeypatch.setenv("MM_MEMORY_INDEX_BACKEND", "pgvector")
    monkeypatch.setenv("MM_MEMORY_EMBEDDING_BACKEND", "ollama")
    monkeypatch.setenv("MM_MEMORY_EMBEDDING_MODEL", "mxbai-embed-large")
    monkeypatch.setenv("OLLAMA_HOST", "http://127.0.0.1:11434")

    build_index_provider_from_env("postgresql://memory-db")

    assert captured == {
        "backend": "pgvector",
        "database_url": "postgresql://memory-db",
        "embedding_backend": "ollama",
        "embedding_model": "mxbai-embed-large",
        "embedding_base_url": "http://127.0.0.1:11434",
    }
