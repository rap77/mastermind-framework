"""Tests for Execution Pydantic schemas (SV-01, SV-02).

Tests validation, defaults, and field constraints for:
- SnapshotMilestone
- BrainOutput
- ExecutionSummary
- Execution
- ExecutionHistoryResponse

Requirements: SV-01, SV-02
"""

from datetime import datetime

import pytest

from mastermind_cli.api.models.execution import (
    BrainOutput,
    Execution,
    ExecutionHistoryResponse,
    ExecutionSummary,
    SnapshotMilestone,
)


class TestSnapshotMilestone:
    """Tests for SnapshotMilestone schema."""

    def test_valid_milestone(self) -> None:
        """Valid milestone creates correctly."""
        m = SnapshotMilestone(
            index=0,
            timestamp=1711296000000,
            label="Brain #1 complete",
            brain_count=1,
        )
        assert m.index == 0
        assert m.timestamp == 1711296000000
        assert m.label == "Brain #1 complete"
        assert m.brain_count == 1

    def test_index_must_be_non_negative(self) -> None:
        """Negative index raises validation error."""
        with pytest.raises(Exception):
            SnapshotMilestone(index=-1, timestamp=0, label="test", brain_count=0)

    def test_timestamp_must_be_non_negative(self) -> None:
        """Negative timestamp raises validation error."""
        with pytest.raises(Exception):
            SnapshotMilestone(index=0, timestamp=-1, label="test", brain_count=0)

    def test_label_required(self) -> None:
        """Empty label raises validation error."""
        with pytest.raises(Exception):
            SnapshotMilestone(index=0, timestamp=0, label="", brain_count=0)


class TestBrainOutput:
    """Tests for BrainOutput schema."""

    def test_valid_brain_output(self) -> None:
        """Valid brain output creates correctly."""
        b = BrainOutput(
            brain_id="brain-01",
            status="complete",
            output="## Analysis\n\nThis is the output.",
            duration_ms=1500,
            timestamp=1711296000000,
        )
        assert b.brain_id == "brain-01"
        assert b.status == "complete"
        assert b.output == "## Analysis\n\nThis is the output."
        assert b.duration_ms == 1500

    def test_status_validation(self) -> None:
        """Invalid status raises validation error."""
        with pytest.raises(Exception):
            BrainOutput(brain_id="brain-01", status="unknown")

    def test_allowed_statuses(self) -> None:
        """All allowed statuses validate correctly."""
        for status in ["idle", "running", "complete", "error"]:
            b = BrainOutput(brain_id="brain-01", status=status)
            assert b.status == status

    def test_defaults(self) -> None:
        """Default values are set correctly."""
        b = BrainOutput(brain_id="brain-01", status="idle")
        assert b.output == ""
        assert b.duration_ms == 0
        assert b.timestamp == 0

    def test_duration_ms_non_negative(self) -> None:
        """Negative duration_ms raises validation error."""
        with pytest.raises(Exception):
            BrainOutput(brain_id="brain-01", status="idle", duration_ms=-1)


class TestExecutionSummary:
    """Tests for ExecutionSummary schema."""

    def test_valid_summary(self) -> None:
        """Valid summary creates correctly."""
        s = ExecutionSummary(
            id="exec-001",
            task_id="task-001",
            brief="Build a landing page for the product",
            status="success",
            duration_ms=5000,
            brain_count=3,
            created_at=datetime(2026, 3, 23, 12, 0, 0),
        )
        assert s.id == "exec-001"
        assert s.status == "success"
        assert s.brain_count == 3

    def test_status_validation(self) -> None:
        """Invalid status raises validation error."""
        with pytest.raises(Exception):
            ExecutionSummary(
                id="exec-001",
                task_id="task-001",
                brief="test",
                status="unknown",
                created_at=datetime.utcnow(),
            )

    def test_allowed_statuses(self) -> None:
        """All allowed statuses validate correctly."""
        for status in ["success", "error", "running"]:
            s = ExecutionSummary(
                id="exec-001",
                task_id="task-001",
                brief="test",
                status=status,
                created_at=datetime.utcnow(),
            )
            assert s.status == status

    def test_brief_max_length(self) -> None:
        """Brief truncated at 200 chars by validation."""
        long_brief = "x" * 201
        with pytest.raises(Exception):
            ExecutionSummary(
                id="exec-001",
                task_id="task-001",
                brief=long_brief,
                status="success",
                created_at=datetime.utcnow(),
            )


class TestExecution:
    """Tests for Execution (full) schema."""

    def test_valid_execution(self) -> None:
        """Valid execution creates correctly."""
        milestones = [
            SnapshotMilestone(
                index=i, timestamp=i * 1000, label=f"Step {i}", brain_count=i
            )
            for i in range(3)
        ]
        brain_outputs = {
            "brain-01": BrainOutput(brain_id="brain-01", status="complete"),
            "brain-02": BrainOutput(brain_id="brain-02", status="complete"),
        }
        e = Execution(
            id="exec-001",
            task_id="task-001",
            brief="Build a landing page",
            status="success",
            duration_ms=10000,
            brain_count=2,
            created_at=datetime.utcnow(),
            milestones=milestones,
            brain_outputs=brain_outputs,
            graph_snapshot={"nodes": [], "edges": []},
        )
        assert e.id == "exec-001"
        assert len(e.milestones) == 3
        assert len(e.brain_outputs) == 2
        assert e.graph_snapshot == {"nodes": [], "edges": []}

    def test_milestones_max_10(self) -> None:
        """More than 10 milestones raises validation error."""
        milestones = [
            SnapshotMilestone(
                index=i, timestamp=i * 1000, label=f"Step {i}", brain_count=1
            )
            for i in range(11)
        ]
        with pytest.raises(Exception):
            Execution(
                id="exec-001",
                task_id="task-001",
                brief="test",
                status="success",
                brain_count=1,
                created_at=datetime.utcnow(),
                milestones=milestones,
            )

    def test_exactly_10_milestones_allowed(self) -> None:
        """Exactly 10 milestones is allowed."""
        milestones = [
            SnapshotMilestone(
                index=i, timestamp=i * 1000, label=f"Step {i}", brain_count=1
            )
            for i in range(10)
        ]
        e = Execution(
            id="exec-001",
            task_id="task-001",
            brief="test",
            status="success",
            brain_count=1,
            created_at=datetime.utcnow(),
            milestones=milestones,
        )
        assert len(e.milestones) == 10

    def test_brain_count_ge_1(self) -> None:
        """brain_count must be >= 1."""
        with pytest.raises(Exception):
            Execution(
                id="exec-001",
                task_id="task-001",
                brief="test",
                status="success",
                brain_count=0,
                created_at=datetime.utcnow(),
            )

    def test_defaults(self) -> None:
        """Default values are correct."""
        e = Execution(
            id="exec-001",
            task_id="task-001",
            brief="test",
            status="success",
            brain_count=1,
            created_at=datetime.utcnow(),
        )
        assert e.milestones == []
        assert e.brain_outputs == {}
        assert e.graph_snapshot == {}
        assert e.duration_ms == 0


class TestExecutionHistoryResponse:
    """Tests for ExecutionHistoryResponse schema."""

    def test_empty_response(self) -> None:
        """Empty history response is valid."""
        r = ExecutionHistoryResponse(
            executions=[],
            next_cursor=None,
            has_more=False,
        )
        assert r.executions == []
        assert r.next_cursor is None
        assert r.has_more is False

    def test_with_cursor(self) -> None:
        """Response with cursor is valid."""
        r = ExecutionHistoryResponse(
            executions=[],
            next_cursor="dGVzdC1pZA==",
            has_more=True,
        )
        assert r.next_cursor == "dGVzdC1pZA=="
        assert r.has_more is True
