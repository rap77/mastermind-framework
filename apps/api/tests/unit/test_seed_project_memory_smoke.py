"""Tests for the semantic-memory smoke seed corpus."""

from __future__ import annotations

import asyncio
import importlib.util
from types import SimpleNamespace
from pathlib import Path

import pytest
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


def test_smoke_seed_main_links_prior_items_as_related_memory_ids(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Smoke seed main should chain related_memory_ids through the seeded corpus."""
    module = _load_seed_module()
    calls: list[dict[str, object]] = []

    class FakeService:
        async def record_learning(self, **kwargs: object) -> SimpleNamespace:
            calls.append(dict(kwargs))
            return SimpleNamespace(
                memory_id=f"mem-{len(calls)}",
                title=str(kwargs["title"]),
            )

    monkeypatch.setenv("MM_MEMORY_DATABASE_URL", "sqlite:///seed.db")
    monkeypatch.setenv("MM_MEMORY_PROJECT_ID", "proj-semantic-smoke")
    monkeypatch.setattr(
        module,
        "build_memory_store_from_env",
        lambda *args, **kwargs: object(),
    )
    monkeypatch.setattr(module, "MemoryService", lambda store: FakeService())

    asyncio.run(module.main())

    assert len(calls) == 3
    assert "related_memory_ids" not in calls[0]
    assert calls[1]["related_memory_ids"] == ["mem-1"]
    assert calls[2]["related_memory_ids"] == ["mem-1", "mem-2"]
