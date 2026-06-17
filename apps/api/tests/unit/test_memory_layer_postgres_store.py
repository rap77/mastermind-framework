"""Tests for the SQL-backed PostgresMemoryStore."""

from __future__ import annotations

from pathlib import Path
from typing import TypeVar
from collections.abc import Awaitable

from sqlalchemy import select

from mastermind_cli.memory_layer.store_postgres import (
    MemoryPreferenceRecord,
    MemorySessionRecord,
    PostgresMemoryStore,
)
from mastermind_cli.memory_layer.models import MemoryItem
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
)

T = TypeVar("T")


def test_save_and_get_item_round_trip(tmp_path: Path) -> None:
    """Stored memory items should round-trip through the canonical model."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    saved = run_async(
        store.save_item(
            MemoryItem(
                memory_type="lesson",
                title="Avoid execution drift",
                content="Execution projections must read canonical artifacts first.",
                project_id="proj-001",
                brain_id="brain-07-growth-data",
                niche="software-development",
                visibility="project",
                tags=["executions", "artifacts"],
                metadata={"confidence": "high"},
            )
        )
    )

    fetched = run_async(store.get_item(saved.memory_id or ""))

    assert saved.memory_id is not None
    assert fetched is not None
    assert fetched.memory_id == saved.memory_id
    assert fetched.memory_type == "lesson"
    assert fetched.project_id == "proj-001"
    assert fetched.tags == ["executions", "artifacts"]
    assert fetched.metadata == {"confidence": "high"}


def test_search_matches_title_and_content_with_project_scope(tmp_path: Path) -> None:
    """Search should honor the project scope and return ranked canonical results."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_item(
            MemoryItem(
                memory_type="decision",
                title="Marketing launch checklist",
                content="Coordinate attribution, CRM sync, and CAC guardrails.",
                project_id="proj-mkt",
                visibility="project",
            )
        )
    )
    run_async(
        store.save_item(
            MemoryItem(
                memory_type="decision",
                title="Investment rebalance note",
                content="Review portfolio risk bands every Friday.",
                project_id="proj-invest",
                visibility="project",
            )
        )
    )

    results = run_async(
        store.search("launch", scope={"project_id": "proj-mkt"}, limit=5)
    )

    assert len(results) == 1
    assert results[0].title == "Marketing launch checklist"
    assert results[0].memory_type == "decision"
    assert results[0].project_id == "proj-mkt"
    assert results[0].score > 0


def test_list_recent_orders_project_items_newest_first(tmp_path: Path) -> None:
    """Recent listing should return only project-scoped items in descending order."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    first = run_async(
        store.save_item(
            MemoryItem(
                memory_type="pattern",
                title="First lesson",
                content="First content.",
                project_id="proj-001",
                visibility="project",
            )
        )
    )
    second = run_async(
        store.save_item(
            MemoryItem(
                memory_type="pattern",
                title="Second lesson",
                content="Second content.",
                project_id="proj-001",
                visibility="project",
            )
        )
    )

    items = run_async(store.list_recent("proj-001", limit=10))

    assert [item.memory_id for item in items] == [second.memory_id, first.memory_id]


def test_save_session_summary_persists_dedicated_session_record(tmp_path: Path) -> None:
    """Session summaries should persist into the dedicated session continuity table."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_session_summary(
            session_id="session-123",
            summary="Closed auth migration and stabilized strategy vault projections.",
            project_id="proj-001",
            metadata={"objective": "memory-layer-v1"},
        )
    )

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        record = session.scalar(
            select(MemorySessionRecord).where(
                MemorySessionRecord.session_id == "session-123"
            )
        )

    assert record is not None
    assert record.project_id == "proj-001"
    assert record.summary.startswith("Closed auth migration")
    assert record.metadata_json == {"objective": "memory-layer-v1"}


def test_save_preference_persists_dedicated_preference_record(tmp_path: Path) -> None:
    """Preferences should persist outside the generic memory items table."""
    database_url = f"sqlite:///{tmp_path / 'memory_layer.db'}"
    dispose_engines()
    store = PostgresMemoryStore(database_url)

    run_async(
        store.save_preference(
            key="output_verbosity",
            value={"level": "brief"},
            scope="personal",
            project_id="proj-001",
        )
    )

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        record = session.scalar(
            select(MemoryPreferenceRecord).where(
                MemoryPreferenceRecord.key == "output_verbosity"
            )
        )

    assert record is not None
    assert record.scope == "personal"
    assert record.project_id == "proj-001"
    assert record.value_json == {"level": "brief"}


def run_async(awaitable: Awaitable[T]) -> T:
    """Run an async store operation from sync unit tests."""
    import asyncio

    return asyncio.run(awaitable)
