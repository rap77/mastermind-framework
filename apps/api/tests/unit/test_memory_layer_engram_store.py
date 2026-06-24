"""Tests for the Engram-backed Memory Layer adapter."""

from __future__ import annotations

from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest

from mastermind_cli.memory_layer.models import MemoryItem
from mastermind_cli.memory_layer.store_engram import EngramMemoryStore


@pytest.mark.asyncio
async def test_save_item_maps_memory_item_to_engram_payload() -> None:
    """Saving an item should delegate through the Engram adapter payload shape."""
    save_observation = AsyncMock(
        return_value={
            "id": 41,
            "title": "Avoid auth drift",
            "content": "Only mmsk_ keys should remain in runtime auth.",
            "type": "lesson",
            "project_id": "proj-001",
            "brain_id": "brain-07-growth-data",
            "niche": "software-development",
            "visibility": "project",
            "tags": ["auth", "keys"],
            "metadata": {"confidence": "high"},
            "created_at": "2026-06-16T12:00:00Z",
            "updated_at": "2026-06-16T12:30:00Z",
        }
    )
    store = EngramMemoryStore(
        save_observation=save_observation,
        search_observations=AsyncMock(return_value=[]),
    )

    item = MemoryItem(
        memory_type="lesson",
        title="Avoid auth drift",
        content="Only mmsk_ keys should remain in runtime auth.",
        project_id="proj-001",
        brain_id="brain-07-growth-data",
        niche="software-development",
        visibility="project",
        tags=["auth", "keys"],
        metadata={"confidence": "high"},
    )

    saved = await store.save_item(item)

    save_observation.assert_awaited_once_with(
        title="Avoid auth drift",
        content="Only mmsk_ keys should remain in runtime auth.",
        type="lesson",
        project_id="proj-001",
        brain_id="brain-07-growth-data",
        niche="software-development",
        visibility="project",
        source_kind=None,
        source_ref=None,
        tags=["auth", "keys"],
        metadata={"confidence": "high"},
    )
    assert saved.memory_id == "41"
    assert saved.created_at == datetime(2026, 6, 16, 12, 0, tzinfo=timezone.utc)
    assert saved.updated_at == datetime(2026, 6, 16, 12, 30, tzinfo=timezone.utc)


@pytest.mark.asyncio
async def test_save_item_filters_non_string_tags() -> None:
    """Saving an item should not forward malformed tags to Engram."""
    save_observation = AsyncMock(return_value={"id": 42, "tags": ["auth"]})
    store = EngramMemoryStore(
        save_observation=save_observation,
        search_observations=AsyncMock(return_value=[]),
    )

    item = MemoryItem.model_construct(
        memory_id=None,
        memory_type="lesson",
        title="Avoid auth drift",
        content="Only mmsk_ keys should remain in runtime auth.",
        project_id="proj-001",
        brain_id="brain-07-growth-data",
        niche="software-development",
        visibility="project",
        source_kind=None,
        source_ref=None,
        tags=["auth", " ", 123],
        metadata={},
    )

    await store.save_item(item)

    assert save_observation.await_args.kwargs["tags"] == ["auth"]


@pytest.mark.asyncio
async def test_get_item_maps_engram_observation_to_memory_item() -> None:
    """Fetching an item should normalize an Engram observation into MemoryItem."""
    get_observation = AsyncMock(
        return_value={
            "id": 77,
            "title": "Portfolio review cadence",
            "content": "Weekly review should compare thesis drift and risk changes.",
            "type": "pattern",
            "project_id": "proj-invest",
            "brain_id": "brain-07-growth-data",
            "niche": "investments",
            "visibility": "org",
            "source_kind": "task_run",
            "source_ref": "run-123",
            "tags": ["investments", "risk"],
            "metadata": {"owner": "cio"},
            "created_at": "2026-06-16T08:00:00Z",
        }
    )
    store = EngramMemoryStore(
        save_observation=AsyncMock(return_value={}),
        search_observations=AsyncMock(return_value=[]),
        get_observation=get_observation,
    )

    item = await store.get_item("77")

    get_observation.assert_awaited_once_with("77")
    assert item is not None
    assert item.memory_id == "77"
    assert item.memory_type == "pattern"
    assert item.project_id == "proj-invest"
    assert item.niche == "investments"
    assert item.tags == ["investments", "risk"]
    assert item.metadata == {"owner": "cio"}


@pytest.mark.asyncio
async def test_search_maps_engram_results_to_memory_search_results() -> None:
    """Search should translate Engram result payloads into canonical search results."""
    search_observations = AsyncMock(
        return_value=[
            {
                "id": 9,
                "title": "Marketing launch checklist",
                "content": "Check landing page, attribution, CAC guardrails, and CRM sync.",
                "type": "project_note",
                "project_id": "proj-mkt",
                "brain_id": "brain-02-marketing",
                "source_ref": "artifact:launch-checklist",
                "score": 0.91,
                "why_matched": "keyword+semantic",
            }
        ]
    )
    store = EngramMemoryStore(
        save_observation=AsyncMock(return_value={}),
        search_observations=search_observations,
    )

    results = await store.search(
        "launch checklist",
        scope={"project_id": "proj-mkt", "niche": "marketing"},
        limit=3,
    )

    search_observations.assert_awaited_once_with(
        query="launch checklist",
        scope={"project_id": "proj-mkt", "niche": "marketing"},
        limit=3,
    )
    assert len(results) == 1
    assert results[0].memory_id == "9"
    assert results[0].memory_type == "project_note"
    assert results[0].score == 0.91
    assert results[0].why_matched == "keyword+semantic"


@pytest.mark.asyncio
async def test_save_session_summary_uses_dedicated_engram_hook_when_present() -> None:
    """Session summaries should use a dedicated hook when the bridge provides one."""
    save_session_summary = AsyncMock(return_value=None)
    store = EngramMemoryStore(
        save_observation=AsyncMock(return_value={}),
        search_observations=AsyncMock(return_value=[]),
        save_session_summary=save_session_summary,
    )

    await store.save_session_summary(
        session_id="session-123",
        summary="Closed task runtime migration slice and validated hooks.",
        project_id="proj-001",
        metadata={"objective": "memory-layer-v1"},
    )

    save_session_summary.assert_awaited_once_with(
        session_id="session-123",
        summary="Closed task runtime migration slice and validated hooks.",
        project_id="proj-001",
        metadata={"objective": "memory-layer-v1"},
    )


@pytest.mark.asyncio
async def test_save_preference_falls_back_to_canonical_memory_item() -> None:
    """Preferences should be stored as canonical memory items through the adapter."""
    save_observation = AsyncMock(return_value={"id": 81})
    store = EngramMemoryStore(
        save_observation=save_observation,
        search_observations=AsyncMock(return_value=[]),
    )

    await store.save_preference(
        key="output_verbosity",
        value={"level": "brief"},
        scope="personal",
        project_id="proj-001",
    )

    save_observation.assert_awaited_once_with(
        title="Preference: output_verbosity",
        content='{"level":"brief"}',
        type="preference",
        project_id="proj-001",
        brain_id=None,
        niche=None,
        visibility="personal",
        source_kind="preference",
        source_ref="preference:output_verbosity",
        tags=["preference", "output_verbosity"],
        metadata={"key": "output_verbosity", "scope": "personal"},
    )


@pytest.mark.asyncio
async def test_list_recent_uses_search_scope_and_returns_memory_items() -> None:
    """Recent listing should remain available even when Engram exposes only search."""
    search_observations = AsyncMock(
        return_value=[
            {
                "id": 13,
                "title": "Recent lesson",
                "content": "Do not mix runtime state with memory state.",
                "type": "lesson",
                "project_id": "proj-001",
                "visibility": "project",
            }
        ]
    )
    store = EngramMemoryStore(
        save_observation=AsyncMock(return_value={}),
        search_observations=search_observations,
    )

    items = await store.list_recent("proj-001", limit=5)

    search_observations.assert_awaited_once_with(
        query="",
        scope={"project_id": "proj-001", "sort": "recent"},
        limit=5,
    )
    assert len(items) == 1
    assert items[0].memory_id == "13"
    assert items[0].title == "Recent lesson"
