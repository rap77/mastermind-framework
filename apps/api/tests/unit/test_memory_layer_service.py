"""Tests for the MemoryService application layer."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from mastermind_cli.memory_layer.models import MemoryItem, MemorySearchResult
from mastermind_cli.memory_layer.service import MemoryService


@pytest.mark.asyncio
async def test_record_session_summary_delegates_to_store() -> None:
    """Session summaries should delegate with the same continuity payload."""
    store = AsyncMock()
    service = MemoryService(store)

    await service.record_session_summary(
        session_id="session-123",
        summary="Closed the storage ownership slice and validated tests.",
        project_id="proj-001",
        metadata={"phase": "ML4"},
    )

    store.save_session_summary.assert_awaited_once_with(
        session_id="session-123",
        summary="Closed the storage ownership slice and validated tests.",
        project_id="proj-001",
        metadata={"phase": "ML4"},
    )


@pytest.mark.asyncio
async def test_record_learning_builds_canonical_memory_item() -> None:
    """Learning records should normalize into canonical memory items."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-1",
        memory_type="lesson",
        title="Avoid runtime drift",
        content="Project-state projections should remain canonical-first.",
        project_id="proj-001",
        visibility="project",
        tags=["lesson", "strategy-vault"],
        metadata={"source": "task-runner"},
    )
    service = MemoryService(store)

    saved = await service.record_learning(
        title="Avoid runtime drift",
        content="Project-state projections should remain canonical-first.",
        project_id="proj-001",
        memory_type="lesson",
        visibility="project",
        tags=["strategy-vault"],
        metadata={"source": "task-runner"},
    )

    store.save_item.assert_awaited_once()
    item = store.save_item.await_args.args[0]
    assert item.memory_type == "lesson"
    assert item.title == "Avoid runtime drift"
    assert item.tags == ["lesson", "strategy-vault"]
    assert item.metadata == {"source": "task-runner"}
    assert saved.memory_id == "mem-1"


@pytest.mark.asyncio
async def test_record_preference_delegates_to_store() -> None:
    """Operational preferences should persist through the store contract."""
    store = AsyncMock()
    service = MemoryService(store)

    await service.record_preference(
        key="output_verbosity",
        value={"level": "brief"},
        scope="personal",
        project_id="proj-001",
    )

    store.save_preference.assert_awaited_once_with(
        key="output_verbosity",
        value={"level": "brief"},
        scope="personal",
        project_id="proj-001",
    )


@pytest.mark.asyncio
async def test_fetch_project_context_delegates_search_scope() -> None:
    """Project context retrieval should scope the search to the selected project."""
    store = AsyncMock()
    store.search.return_value = [
        MemorySearchResult(
            memory_id="mem-1",
            title="Decision note",
            snippet="Use hybrid retrieval after ownership is stable.",
            score=0.9,
            memory_type="decision",
            project_id="proj-001",
        )
    ]
    service = MemoryService(store)

    results = await service.fetch_project_context("proj-001", "retrieval", limit=3)

    store.search.assert_awaited_once_with(
        "retrieval",
        scope={"project_id": "proj-001"},
        limit=3,
    )
    assert len(results) == 1
    assert results[0].memory_id == "mem-1"
