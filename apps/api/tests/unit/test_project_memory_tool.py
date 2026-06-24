"""Tests for the first-party project memory CLI bridge."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from mastermind_cli.memory_layer.indexing import NoopMemoryIndexProvider
from mastermind_cli.memory_layer.models import MemorySearchResult
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.memory_layer.store_postgres import MemoryItemRecord
from mastermind_cli.tools import project_memory


def test_get_database_url_prefers_explicit_memory_database_url(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """MM_MEMORY_DATABASE_URL should win when it is configured."""
    monkeypatch.setenv("MM_MEMORY_DATABASE_URL", "postgresql://memory-url")
    monkeypatch.setenv("DATABASE_URL", "postgresql://fallback-url")
    monkeypatch.setenv("MM_MEMORY_BACKEND", "sqlite")
    monkeypatch.setenv("MM_DB_PATH", "mastermind.db")

    assert project_memory._get_database_url() == "postgresql://memory-url"


def test_get_database_url_uses_sqlite_backend_from_mm_db_path(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """An explicit sqlite backend should normalize MM_DB_PATH into a sqlite URL."""
    monkeypatch.delenv("MM_MEMORY_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MM_MEMORY_BACKEND", "sqlite")
    monkeypatch.setenv("MM_DB_PATH", "mastermind.db")

    assert project_memory._get_database_url() == "sqlite:///mastermind.db"


def test_get_database_url_rejects_implicit_default_sqlite(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The bridge should require explicit DB config instead of guessing silently."""
    monkeypatch.delenv("MM_MEMORY_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("MM_MEMORY_BACKEND", raising=False)
    monkeypatch.delenv("MM_DB_PATH", raising=False)

    with pytest.raises(ValueError, match="Configura MM_MEMORY_DATABASE_URL"):
        project_memory._get_database_url()


def test_get_database_url_rejects_pglite_backend(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """PGlite should fail fast with a clear message in the Python CLI."""
    monkeypatch.delenv("MM_MEMORY_DATABASE_URL", raising=False)
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("MM_MEMORY_BACKEND", "pglite")

    with pytest.raises(ValueError, match="pglite"):
        project_memory._get_database_url()


def test_get_vector_provider_defaults_to_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI should default to the no-op vector provider."""
    monkeypatch.delenv("MM_MEMORY_VECTOR_BACKEND", raising=False)

    provider = project_memory._get_vector_provider()

    assert provider.__class__.__name__ == "NoopVectorSearchProvider"


def test_get_vector_provider_builds_pgvector_provider(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI should build a real pgvector provider when fully configured."""
    monkeypatch.setenv("MM_MEMORY_DATABASE_URL", "postgresql://memory-url")
    monkeypatch.setenv("MM_MEMORY_VECTOR_BACKEND", "pgvector")
    monkeypatch.setenv("MM_MEMORY_EMBEDDING_BACKEND", "none")

    provider = project_memory._get_vector_provider()

    assert provider.__class__.__name__ == "PgvectorVectorSearchProvider"


def test_get_index_provider_defaults_to_noop(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The CLI should default to the no-op index provider."""
    monkeypatch.delenv("MM_MEMORY_INDEX_BACKEND", raising=False)

    provider = project_memory._get_index_provider()

    assert isinstance(provider, NoopMemoryIndexProvider)


def test_detect_database_kind_supports_postgres_and_sqlite() -> None:
    """Status should classify the supported database families correctly."""
    assert (
        project_memory._detect_database_kind("postgresql://memory-db") == "postgresql"
    )
    assert project_memory._detect_database_kind("sqlite:///memory.db") == "sqlite"


@pytest.mark.asyncio
async def test_cmd_backfill_indexes_selected_records(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Backfill should project existing memory rows into index payloads."""
    indexed_payloads = []

    class StubIndexProvider:
        """Collect index payloads for assertion."""

        async def upsert(self, payload: object) -> None:
            indexed_payloads.append(payload)

    record = MemoryItemRecord(
        memory_id="mem-1",
        memory_type="lesson",
        title="Backfill note",
        content="Existing memories should be indexable after rollout.",
        project_id="proj-001",
        brain_id=None,
        niche=None,
        visibility="project",
        source_kind=None,
        source_ref="run-123",
        tags_json=["lesson"],
        metadata_json={"source": "backfill-test"},
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    args = argparse.Namespace(project_id="proj-001", limit=10)

    await project_memory._cmd_backfill(
        args,
        records=[record],
        index_provider=StubIndexProvider(),
    )

    payload = json.loads(capsys.readouterr().out)
    assert payload["indexed"] == 1
    assert payload["project_id"] == "proj-001"
    assert len(indexed_payloads) == 1
    assert indexed_payloads[0].memory_id == "mem-1"
    assert "Backfill note" in indexed_payloads[0].embedding_text


@pytest.mark.asyncio
async def test_cmd_status_prints_status_json(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Status should print the collected operational status as JSON."""
    monkeypatch.setattr(
        project_memory,
        "_collect_status",
        lambda project_id=None: {
            "database_kind": "postgresql",
            "project_id": project_id,
            "vector_backend": "pgvector",
            "index_backend": "pgvector",
            "graph_recall_backend": "metadata",
            "embedding_backend": "sentence-transformers",
            "tables": {
                "mm_memory_items": True,
                "mm_memory_embeddings": True,
            },
            "counts": {
                "memory_items": 10,
                "memory_embeddings": 8,
            },
            "pgvector_extension_installed": True,
        },
    )

    await project_memory._cmd_status(argparse.Namespace(project_id="proj-001"))

    payload = json.loads(capsys.readouterr().out)
    assert payload["database_kind"] == "postgresql"
    assert payload["project_id"] == "proj-001"
    assert payload["counts"]["memory_embeddings"] == 8


def test_build_doctor_report_marks_ready_when_pgvector_is_fully_operational() -> None:
    """Doctor should mark the system ready when semantic retrieval prerequisites exist."""
    report = project_memory._build_doctor_report(
        {
            "database_kind": "postgresql",
            "project_id": "proj-001",
            "vector_backend": "pgvector",
            "index_backend": "pgvector",
            "graph_recall_backend": "metadata",
            "embedding_backend": "sentence-transformers",
            "tables": {
                "mm_memory_items": True,
                "mm_memory_embeddings": True,
            },
            "counts": {
                "memory_items": 10,
                "memory_embeddings": 8,
            },
            "pgvector_extension_installed": True,
        }
    )

    assert report["ready_for_semantic_query"] is True
    assert report["next_steps"] == []


def test_build_doctor_report_recommends_backfill_when_embeddings_are_missing() -> None:
    """Doctor should guide the user toward backfill when semantic rows are absent."""
    report = project_memory._build_doctor_report(
        {
            "database_kind": "postgresql",
            "project_id": "proj-001",
            "vector_backend": "pgvector",
            "index_backend": "pgvector",
            "graph_recall_backend": "metadata",
            "embedding_backend": "sentence-transformers",
            "tables": {
                "mm_memory_items": True,
                "mm_memory_embeddings": True,
            },
            "counts": {
                "memory_items": 10,
                "memory_embeddings": 0,
            },
            "pgvector_extension_installed": True,
        }
    )

    assert report["ready_for_semantic_query"] is False
    assert any("backfill" in step for step in report["next_steps"])


def test_build_doctor_report_rejects_unconfigurable_graph_recall() -> None:
    """Doctor should not mark ready when graph recall config cannot initialize."""
    report = project_memory._build_doctor_report(
        {
            "database_kind": "postgresql",
            "project_id": "proj-001",
            "vector_backend": "pgvector",
            "index_backend": "pgvector",
            "graph_recall_backend": "static",
            "graph_recall_configured": False,
            "embedding_backend": "sentence-transformers",
            "tables": {
                "mm_memory_items": True,
                "mm_memory_embeddings": True,
            },
            "counts": {
                "memory_items": 10,
                "memory_embeddings": 8,
            },
            "pgvector_extension_installed": True,
        }
    )

    assert report["ready_for_semantic_query"] is False
    assert any("graph recall" in step for step in report["next_steps"])


@pytest.mark.asyncio
async def test_cmd_doctor_prints_actionable_report(
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Doctor should print readiness checks and next steps as JSON."""
    monkeypatch.setattr(
        project_memory,
        "_collect_status",
        lambda project_id=None: {
            "database_kind": "postgresql",
            "project_id": project_id,
            "vector_backend": "pgvector",
            "index_backend": "pgvector",
            "graph_recall_backend": "metadata",
            "embedding_backend": "sentence-transformers",
            "tables": {
                "mm_memory_items": True,
                "mm_memory_embeddings": True,
            },
            "counts": {
                "memory_items": 10,
                "memory_embeddings": 0,
            },
            "pgvector_extension_installed": True,
        },
    )

    await project_memory._cmd_doctor(argparse.Namespace(project_id="proj-001"))

    payload = json.loads(capsys.readouterr().out)
    assert payload["ready_for_semantic_query"] is False
    assert payload["checks"]["has_memory_items_table"] is True
    assert any("backfill" in step for step in payload["next_steps"])
    assert payload["checks"]["graph_recall_enabled"] is True


@pytest.mark.asyncio
async def test_cmd_query_prints_json_results(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI bridge should serialize MemorySearchResult payloads to JSON."""
    store = AsyncMock()
    store.search.return_value = [
        MemorySearchResult(
            memory_id="mem-1",
            title="Decision note",
            snippet="Use hybrid retrieval after ownership is stable.",
            score=0.9,
            memory_type="decision",
            project_id="proj-001",
            why_matched="lexical:title_or_content",
        )
    ]
    service = MemoryService(store)
    args = argparse.Namespace(project_id="proj-001", query="retrieval", limit=3)

    await project_memory._cmd_query(args, service=service)

    payload = json.loads(capsys.readouterr().out)
    assert payload[0]["memory_id"] == "mem-1"
    assert payload[0]["project_id"] == "proj-001"
    assert payload[0]["why_matched"] == "lexical:title_or_content"
