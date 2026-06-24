"""Tests for the graph recall seam in the first-party memory layer."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.memory_layer.graph_recall import (
    MetadataMemoryGraphRecallProvider,
    NoopMemoryGraphRecallProvider,
    StaticMemoryGraphRecallProvider,
)
from mastermind_cli.memory_layer.models import MemoryItem, MemorySearchResult
from mastermind_cli.memory_layer.store_postgres import PostgresMemoryStore
from mastermind_cli.project_state.database.session import dispose_engines


def _search_result(
    memory_id: str,
    title: str,
    snippet: str,
    score: float,
    memory_type: str,
    project_id: str,
    brain_id: str | None = None,
    why_matched: str | None = None,
    source_ref: str | None = None,
) -> MemorySearchResult:
    """Build a fully typed search result for graph-recall tests."""
    return MemorySearchResult(
        memory_id=memory_id,
        title=title,
        snippet=snippet,
        score=score,
        memory_type=memory_type,
        project_id=project_id,
        brain_id=brain_id,
        why_matched=why_matched,
        source_ref=source_ref,
    )


def _memory_item(
    memory_id: str,
    memory_type: str,
    title: str,
    content: str,
    project_id: str,
    brain_id: str,
    visibility: str,
    metadata: dict[str, object] | None = None,
) -> MemoryItem:
    """Build a fully typed memory item for graph-recall tests."""
    return MemoryItem(
        memory_id=memory_id,
        memory_type=memory_type,
        title=title,
        content=content,
        project_id=project_id,
        brain_id=brain_id,
        niche=None,
        visibility=visibility,
        source_kind=None,
        source_ref=None,
        metadata=metadata or {},
    )


@pytest.mark.asyncio
async def test_noop_graph_recall_preserves_result_order() -> None:
    """Noop graph recall should preserve ranked results exactly."""
    provider = NoopMemoryGraphRecallProvider()

    results = await provider.expand(
        "launch",
        [
            _search_result("mem-1", "A", "a", 2.0, "lesson", "proj-001"),
            _search_result("mem-2", "B", "b", 1.0, "lesson", "proj-001"),
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-2"]


@pytest.mark.asyncio
async def test_static_graph_recall_appends_related_results_without_duplicates() -> None:
    """Static graph recall should append unique related results after the seed set."""
    provider = StaticMemoryGraphRecallProvider(
        {
            "mem-1": [
                _search_result(
                    "mem-3",
                    "Decision link",
                    "linked by decision lineage",
                    0.5,
                    "decision",
                    "proj-001",
                ),
                _search_result(
                    "mem-2",
                    "Duplicate",
                    "already present",
                    0.4,
                    "lesson",
                    "proj-001",
                ),
            ]
        }
    )

    results = await provider.expand(
        "launch",
        [
            _search_result("mem-1", "Launch note", "seed", 2.0, "lesson", "proj-001"),
            _search_result(
                "mem-2",
                "Weekly review",
                "existing second result",
                1.0,
                "lesson",
                "proj-001",
            ),
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-2", "mem-3"]
    assert results[2].why_matched == "graph:related"


@pytest.mark.asyncio
async def test_static_graph_recall_respects_project_and_type_scope() -> None:
    """Static graph recall should not append related results outside the active scope."""
    provider = StaticMemoryGraphRecallProvider(
        {
            "mem-1": [
                _search_result(
                    "mem-3",
                    "Wrong project",
                    "cross-project relation",
                    0.5,
                    "decision",
                    "proj-002",
                    brain_id="brain-2",
                ),
                _search_result(
                    "mem-4",
                    "Wrong type",
                    "same project but wrong type",
                    0.4,
                    "lesson",
                    "proj-001",
                    brain_id="brain-2",
                ),
                _search_result(
                    "mem-5",
                    "Scoped match",
                    "same project and type",
                    0.3,
                    "decision",
                    "proj-001",
                    brain_id="brain-2",
                ),
            ]
        }
    )

    results = await provider.expand(
        "launch",
        [
            _search_result(
                "mem-1",
                "Launch note",
                "seed",
                2.0,
                "lesson",
                "proj-001",
                brain_id="brain-1",
            )
        ],
        {"project_id": "proj-001", "memory_type": "decision"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-5"]
    assert results[1].why_matched == "graph:related"


@pytest.mark.asyncio
async def test_metadata_graph_recall_expands_persisted_related_memory(
    tmp_path: Path,
) -> None:
    """Metadata graph recall should append persisted related memory items."""
    database_url = f"sqlite:///{tmp_path / 'memory_graph_recall.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)
    provider = MetadataMemoryGraphRecallProvider(database_url)

    await store.save_item(
        _memory_item(
            "mem-1",
            "lesson",
            "Launch note",
            "seed",
            "proj-001",
            "brain-1",
            "project",
            metadata={"related_memory_ids": ["mem-2"]},
        )
    )
    await store.save_item(
        _memory_item(
            "mem-2",
            "decision",
            "Linked decision",
            "persisted related memory",
            "proj-001",
            "brain-1",
            "project",
        )
    )

    results = await provider.expand(
        "launch",
        [
            _search_result(
                "mem-1",
                "Launch note",
                "seed",
                2.0,
                "lesson",
                "proj-001",
                brain_id="brain-1",
            )
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-2"]
    assert results[1].why_matched == "graph:metadata"


@pytest.mark.asyncio
async def test_metadata_graph_recall_ignores_non_string_related_ids(
    tmp_path: Path,
) -> None:
    """Metadata graph recall should skip malformed related-memory IDs."""
    database_url = f"sqlite:///{tmp_path / 'memory_graph_recall.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)
    provider = MetadataMemoryGraphRecallProvider(database_url)

    await store.save_item(
        _memory_item(
            "mem-1",
            "lesson",
            "Launch note",
            "seed",
            "proj-001",
            "brain-1",
            "project",
            metadata={"related_memory_ids": [123, "mem-2", None]},
        )
    )
    await store.save_item(
        _memory_item(
            "mem-2",
            "decision",
            "Linked decision",
            "persisted related memory",
            "proj-001",
            "brain-1",
            "project",
        )
    )

    results = await provider.expand(
        "launch",
        [
            _search_result(
                "mem-1",
                "Launch note",
                "seed",
                2.0,
                "lesson",
                "proj-001",
                brain_id="brain-1",
            )
        ],
        {"project_id": "proj-001"},
        5,
    )

    assert [result.memory_id for result in results] == ["mem-1", "mem-2"]
    assert results[1].why_matched == "graph:metadata"
