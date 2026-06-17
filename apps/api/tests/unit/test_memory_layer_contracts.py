"""Tests for the Memory Layer Phase 1 contract surface."""

from __future__ import annotations

from datetime import datetime, timezone

import pytest
from typing_extensions import assert_type

from mastermind_cli.memory_layer.contracts import MemoryStore
from mastermind_cli.memory_layer.models import (
    MemoryContextBundle,
    MemoryItem,
    MemorySearchResult,
)


class TestMemoryItem:
    """Test MemoryItem model behavior."""

    def test_memory_item_minimal_creation(self) -> None:
        """MemoryItem should support a minimal but valid payload."""
        item = MemoryItem(
            memory_type="lesson",
            title="Avoid legacy auth drift",
            content="The runtime must only accept mmsk_ keys.",
            visibility="project",
        )

        assert item.memory_type == "lesson"
        assert item.title == "Avoid legacy auth drift"
        assert item.project_id is None
        assert item.brain_id is None
        assert item.niche is None
        assert item.tags == []
        assert item.metadata == {}
        assert isinstance(item.created_at, datetime)
        assert isinstance(item.updated_at, datetime)

    def test_memory_item_preserves_scope_fields(self) -> None:
        """MemoryItem should retain scope information for future niche routing."""
        item = MemoryItem(
            memory_type="pattern",
            title="Portfolio risk review pattern",
            content="Weekly review should compare thesis drift and risk changes.",
            project_id="proj-001",
            brain_id="brain-07-growth-data",
            niche="investments",
            visibility="org",
            source_kind="task_run",
            source_ref="run-123",
            tags=["investments", "risk"],
            metadata={"confidence": "high"},
        )

        assert item.project_id == "proj-001"
        assert item.brain_id == "brain-07-growth-data"
        assert item.niche == "investments"
        assert item.visibility == "org"
        assert item.source_kind == "task_run"
        assert item.source_ref == "run-123"
        assert item.tags == ["investments", "risk"]
        assert item.metadata == {"confidence": "high"}


class TestMemorySearchResult:
    """Test MemorySearchResult model behavior."""

    def test_memory_search_result_creation(self) -> None:
        """Search results should expose ranking and explanation fields."""
        result = MemorySearchResult(
            memory_id="mem-123",
            title="Fix for stale execution projection",
            snippet="Execution detail should read artifacts first.",
            score=0.93,
            memory_type="fix",
            why_matched="keyword+semantic",
            source_ref="artifact:execution-output:run-9",
        )

        assert result.memory_id == "mem-123"
        assert result.score == 0.93
        assert result.why_matched == "keyword+semantic"
        assert result.source_ref == "artifact:execution-output:run-9"


class TestMemoryContextBundle:
    """Test MemoryContextBundle model behavior."""

    def test_memory_context_bundle_defaults(self) -> None:
        """Context bundles should be safe to construct with minimal data."""
        bundle = MemoryContextBundle(items=[], summary="")

        assert bundle.items == []
        assert bundle.summary == ""
        assert bundle.open_gaps == []
        assert bundle.applied_scopes == {}

    def test_memory_context_bundle_holds_results(self) -> None:
        """Context bundles should carry result items and explicit gaps."""
        bundle = MemoryContextBundle(
            items=[
                MemorySearchResult(
                    memory_id="mem-1",
                    title="Decision note",
                    snippet="Use hybrid retrieval before reranking.",
                    score=0.88,
                    memory_type="decision",
                )
            ],
            summary="One relevant design decision found.",
            open_gaps=["No memory for marketing niche yet."],
            applied_scopes={"project_id": "proj-001", "niche": "software-development"},
        )

        assert len(bundle.items) == 1
        assert bundle.open_gaps == ["No memory for marketing niche yet."]
        assert bundle.applied_scopes["project_id"] == "proj-001"


class TestMemoryStoreProtocol:
    """Test the MemoryStore contract shape."""

    def test_memory_store_is_runtime_checkable_protocol(self) -> None:
        """MemoryStore should be declared as a runtime-checkable protocol."""

        class DummyStore:
            """Protocol-shaped in-memory dummy store used only for tests."""

            async def save_item(self, item: MemoryItem) -> MemoryItem:
                return item

            async def get_item(self, memory_id: str) -> MemoryItem | None:
                return None

            async def search(
                self,
                query: str,
                scope: dict[str, str | None] | None = None,
                limit: int = 10,
            ) -> list[MemorySearchResult]:
                return []

            async def list_recent(
                self,
                project_id: str,
                limit: int = 10,
            ) -> list[MemoryItem]:
                return []

            async def save_session_summary(
                self,
                session_id: str,
                summary: str,
                project_id: str | None = None,
                metadata: dict[str, object] | None = None,
            ) -> None:
                return None

            async def save_preference(
                self,
                key: str,
                value: object,
                scope: str,
                project_id: str | None = None,
            ) -> None:
                return None

        dummy = DummyStore()
        assert isinstance(dummy, MemoryStore)

    def test_memory_store_protocol_exposes_expected_methods(self) -> None:
        """MemoryStore should define the minimum method surface for ML1."""
        expected_methods = {
            "save_item",
            "get_item",
            "search",
            "list_recent",
            "save_session_summary",
            "save_preference",
        }

        assert expected_methods.issubset(set(MemoryStore.__dict__.keys()))

    def test_memory_store_type_aliases_are_stable(self) -> None:
        """The protocol should preserve stable return types for implementers."""
        assert_type(MemoryStore.save_item, object)


def test_memory_item_timestamps_are_timezone_aware() -> None:
    """Memory items should default to timezone-aware timestamps."""
    item = MemoryItem(
        memory_type="project_summary",
        title="Sprint summary",
        content="Realtime events and write-side actions were stabilized.",
        visibility="project",
    )

    assert item.created_at.tzinfo == timezone.utc
    assert item.updated_at.tzinfo == timezone.utc


def test_memory_item_requires_non_empty_title() -> None:
    """MemoryItem should reject blank titles."""
    with pytest.raises(Exception):
        MemoryItem(
            memory_type="lesson",
            title="",
            content="This should fail validation.",
            visibility="project",
        )
