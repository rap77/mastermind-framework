"""Tests for the MemoryService application layer."""

from __future__ import annotations

from unittest.mock import AsyncMock

import pytest

from mastermind_cli.memory_layer.exceptions import MemorySnapshotError
from mastermind_cli.memory_layer.models import (
    ContextSnapshot,
    MemoryItem,
    MemorySearchResult,
    RunSummary,
)
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
async def test_record_learning_merges_related_memory_ids_into_metadata() -> None:
    """Related memory IDs should be normalized into memory metadata for graph recall."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-2",
        memory_type="lesson",
        title="Follow-up note",
        content="related",
        visibility="project",
        tags=["lesson"],
        metadata={"related_memory_ids": ["mem-1", "mem-3"]},
    )
    service = MemoryService(store)

    saved = await service.record_learning(
        title="Follow-up note",
        content="related",
        visibility="project",
        related_memory_ids=["mem-3", "mem-4"],
        metadata={"source": "task-runner", "related_memory_ids": ["mem-1"]},
    )

    item = store.save_item.await_args.args[0]
    assert item.metadata == {
        "source": "task-runner",
        "related_memory_ids": ["mem-1", "mem-3", "mem-4"],
    }
    assert saved.memory_id == "mem-2"


@pytest.mark.asyncio
async def test_record_learning_accepts_non_list_related_memory_ids() -> None:
    """Tuple metadata should still normalize into related memory IDs."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-3",
        memory_type="lesson",
        title="Follow-up note",
        content="related",
        visibility="project",
        tags=["lesson"],
        metadata={"related_memory_ids": ["mem-1", "mem-2"]},
    )
    service = MemoryService(store)

    await service.record_learning(
        title="Follow-up note",
        content="related",
        visibility="project",
        related_memory_ids=("mem-2", "mem-4"),
        metadata={"related_memory_ids": ("mem-1",)},
    )

    item = store.save_item.await_args.args[0]
    assert item.metadata["related_memory_ids"] == ["mem-1", "mem-2", "mem-4"]


@pytest.mark.asyncio
async def test_record_learning_ignores_mapping_related_memory_ids() -> None:
    """Mapping payloads should not be mistaken for ordered related IDs."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-4",
        memory_type="lesson",
        title="Follow-up note",
        content="related",
        visibility="project",
        tags=["lesson"],
        metadata={},
    )
    service = MemoryService(store)

    await service.record_learning(
        title="Follow-up note",
        content="related",
        visibility="project",
        metadata={"related_memory_ids": {"a": "mem-1", "b": "mem-2"}},
    )

    item = store.save_item.await_args.args[0]
    assert "related_memory_ids" not in item.metadata


@pytest.mark.asyncio
async def test_record_learning_ignores_none_related_memory_ids() -> None:
    """None entries should not be coerced into a fake related-memory ID."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-5",
        memory_type="lesson",
        title="Follow-up note",
        content="related",
        visibility="project",
        tags=["lesson"],
        metadata={"related_memory_ids": ["mem-1"]},
    )
    service = MemoryService(store)

    await service.record_learning(
        title="Follow-up note",
        content="related",
        visibility="project",
        related_memory_ids=[None, "mem-2"],
        metadata={"related_memory_ids": [None, "mem-1"]},
    )

    item = store.save_item.await_args.args[0]
    assert item.metadata["related_memory_ids"] == ["mem-1", "mem-2"]


@pytest.mark.asyncio
async def test_record_learning_ignores_non_string_related_memory_ids() -> None:
    """Only string IDs should survive normalization."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="mem-6",
        memory_type="lesson",
        title="Follow-up note",
        content="related",
        visibility="project",
        tags=["lesson"],
        metadata={"related_memory_ids": ["mem-1"]},
    )
    service = MemoryService(store)

    await service.record_learning(
        title="Follow-up note",
        content="related",
        visibility="project",
        related_memory_ids=[1, "mem-2", True, ""],  # type: ignore[list-item]
        metadata={"related_memory_ids": [False, "mem-1"]},
    )

    item = store.save_item.await_args.args[0]
    assert item.metadata["related_memory_ids"] == ["mem-1", "mem-2"]


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


@pytest.mark.asyncio
async def test_record_checkpoint_delegates_to_store_as_checkpoint() -> None:
    """Checkpoints should persist as canonical memory items."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="ckpt-1",
        memory_type="checkpoint",
        title="Checkpoint: ckpt-1",
        content="Resume from the latest safe boundary.",
        project_id="proj-001",
        visibility="project",
        tags=["checkpoint"],
        metadata={
            "checkpoint_id": "ckpt-1",
            "task_id": "task-9",
            "run_id": "run-7",
            "context_summary": {"brief": "build"},
            "resume_state": {"phase": "verify"},
            "next_step_summary": "Resume from the latest safe boundary.",
        },
    )
    service = MemoryService(store)

    checkpoint = await service.record_checkpoint(
        checkpoint_id="ckpt-1",
        project_id="proj-001",
        task_id="task-9",
        run_id="run-7",
        context_summary={"brief": "build"},
        resume_state={"phase": "verify"},
        next_step_summary="Resume from the latest safe boundary.",
    )

    item = store.save_item.await_args.args[0]
    assert item.memory_type == "checkpoint"
    assert item.source_kind == "checkpoint"
    assert checkpoint.checkpoint_id == "ckpt-1"
    assert checkpoint.project_id == "proj-001"
    assert checkpoint.task_id == "task-9"


@pytest.mark.asyncio
async def test_save_run_summary_delegates_to_session_summary() -> None:
    """Run summaries should reuse the session-summary persistence path."""
    store = AsyncMock()
    service = MemoryService(store)

    run_summary = await service.save_run_summary(
        RunSummary(
            run_id="run-9",
            project_id="proj-001",
            summary="Closed the runtime seam.",
        )
    )

    store.save_session_summary.assert_awaited_once_with(
        session_id="run-9",
        summary="Closed the runtime seam.",
        project_id="proj-001",
        metadata={},
    )
    assert run_summary.summary == "Closed the runtime seam."


@pytest.mark.asyncio
async def test_record_decision_delegates_to_store_as_decision() -> None:
    """Decisions should persist as canonical memory items."""
    store = AsyncMock()
    store.save_item.return_value = MemoryItem(
        memory_id="dec-1",
        memory_type="decision",
        title="Keep the bridge thin",
        content="The bridge only translates and records.",
        project_id="proj-001",
        visibility="project",
        tags=["decision", "approved"],
        metadata={
            "decision_id": "dec-1",
            "task_id": "task-2",
            "status": "approved",
        },
    )
    service = MemoryService(store)

    decision = await service.record_decision(
        decision_id="dec-1",
        project_id="proj-001",
        task_id="task-2",
        title="Keep the bridge thin",
        status="approved",
        rationale_markdown="The bridge only translates and records.",
    )

    item = store.save_item.await_args.args[0]
    assert item.memory_type == "decision"
    assert item.source_kind == "decision"
    assert decision.decision_id == "dec-1"
    assert decision.status == "approved"


@pytest.mark.asyncio
async def test_build_context_snapshot_compacts_recent_memory() -> None:
    """The service should build a resumable snapshot from recent memory."""
    store = AsyncMock()
    store.list_recent.return_value = [
        MemoryItem(
            memory_id="ckpt-2",
            memory_type="checkpoint",
            title="Checkpoint: ckpt-2",
            content="Resume after review.",
            project_id="proj-001",
            visibility="project",
            metadata={
                "checkpoint_id": "ckpt-2",
                "task_id": "task-9",
                "run_id": "run-8",
                "context_summary": {"brief": "build"},
                "resume_state": {"phase": "review"},
                "next_step_summary": "Resume after review.",
            },
        ),
        MemoryItem(
            memory_id="dec-2",
            memory_type="decision",
            title="Prefer deterministic loops",
            content="Keep selection explainable.",
            project_id="proj-001",
            visibility="project",
            metadata={
                "decision_id": "dec-2",
                "task_id": "task-9",
                "status": "approved",
            },
        ),
        MemoryItem(
            memory_id="sum-1",
            memory_type="session_summary",
            title="Session summary: run-8",
            content="Closed the runtime seam.",
            project_id="proj-001",
            visibility="project",
            source_ref="run-8",
            metadata={"run_id": "run-8", "task_id": "task-9"},
        ),
    ]
    service = MemoryService(store)

    snapshot = await service.build_context_snapshot("proj-001", task_id="task-9")

    assert isinstance(snapshot, ContextSnapshot)
    assert snapshot.project_id == "proj-001"
    assert snapshot.task_id == "task-9"
    assert snapshot.checkpoints[0].checkpoint_id == "ckpt-2"
    assert snapshot.decisions[0].decision_id == "dec-2"
    assert snapshot.run_summaries[0].run_id == "run-8"
    assert snapshot.summary == "Resume after review."
    assert snapshot.open_gaps == []


@pytest.mark.asyncio
async def test_build_context_snapshot_wraps_store_failures() -> None:
    """Snapshot load failures should surface as a memory-layer error."""
    store = AsyncMock()
    store.list_recent.side_effect = RuntimeError("backend offline")
    service = MemoryService(store)

    with pytest.raises(MemorySnapshotError, match="Failed to build context snapshot"):
        await service.build_context_snapshot("proj-001")
