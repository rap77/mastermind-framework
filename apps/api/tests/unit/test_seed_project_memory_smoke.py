"""Tests for the semantic-memory smoke seed corpus."""

from __future__ import annotations

import asyncio
import importlib.util
from pathlib import Path

from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.project_state.database.session import dispose_engines


def _load_seed_module():
    """Load the smoke seed script module directly from disk for testing."""
    script_path = (
        Path(__file__).resolve().parents[2] / "scripts" / "seed_project_memory_smoke.py"
    )
    spec = importlib.util.spec_from_file_location(
        "seed_project_memory_smoke", script_path
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_build_smoke_seed_items_covers_multiple_semantic_topics() -> None:
    """The smoke corpus should cover pgvector, Ollama, and backfill topics."""
    items = _load_seed_module().build_smoke_seed_items("proj-semantic-smoke")

    assert len(items) == 3
    titles = {str(item["title"]) for item in items}
    assert "Embeddings locales con Ollama" in titles
    assert "Backfill requerido tras cambiar de modelo" in titles


def test_smoke_seed_corpus_supports_embedding_query(tmp_path: Path) -> None:
    """The richer smoke corpus should answer an Ollama embedding retrieval query."""
    database_url = f"sqlite:///{tmp_path / 'smoke_seed_eval.db'}"
    dispose_engines()
    service = MemoryService(PostgresMemoryStore(database_url))
    items = _load_seed_module().build_smoke_seed_items("proj-semantic-smoke")

    for item in items:
        asyncio.run(service.record_learning(**item))

    results = asyncio.run(
        service.fetch_project_context(
            "proj-semantic-smoke",
            "embeddings locales con ollama",
            limit=3,
        )
    )

    assert results
    assert results[0].title == "Embeddings locales con Ollama"
