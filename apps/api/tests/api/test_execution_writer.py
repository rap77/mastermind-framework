"""Tests for execution_writer service.

Tests:
- write_execution() persists to DB correctly
- Milestone computation (max 7, evenly spaced)
- Failure does not raise (background task safety)
- Concurrency: second write to same task_id is silently skipped

Requirements: SV-01, SV-02
"""

import json

import pytest

from mastermind_cli.api.services.execution_writer import (
    _compute_milestones,
    write_execution,
)
from mastermind_cli.state.database import DatabaseConnection


# ===== Unit tests: _compute_milestones =====


class TestComputeMilestones:
    """Tests for the milestone computation helper."""

    def _make_outputs(self, n: int) -> dict:
        """Create n brain outputs with sequential timestamps."""
        return {
            f"brain-{i:02d}": {
                "brain_id": f"brain-{i:02d}",
                "status": "complete",
                "output": f"Output {i}",
                "duration_ms": 100 * i,
                "timestamp": 1000 * (i + 1),
            }
            for i in range(1, n + 1)
        }

    def test_empty_outputs_returns_empty(self) -> None:
        """Empty brain outputs → empty milestones."""
        milestones = _compute_milestones({})
        assert milestones == []

    def test_single_brain_creates_milestones(self) -> None:
        """Single brain output creates milestones including start/complete."""
        outputs = self._make_outputs(1)
        milestones = _compute_milestones(outputs)
        assert len(milestones) >= 1
        labels = [m["label"] for m in milestones]
        assert "Task started" in labels

    def test_max_7_milestones_enforced(self) -> None:
        """8 brain outputs → at most 7 milestones."""
        outputs = self._make_outputs(8)
        milestones = _compute_milestones(outputs, max_milestones=7)
        assert len(milestones) <= 7

    def test_milestones_have_required_fields(self) -> None:
        """Each milestone has index, timestamp, label, brain_count."""
        outputs = self._make_outputs(3)
        milestones = _compute_milestones(outputs)
        for m in milestones:
            assert "index" in m
            assert "timestamp" in m
            assert "label" in m
            assert "brain_count" in m

    def test_milestones_ordered_by_index(self) -> None:
        """Milestones are ordered by index (0-based)."""
        outputs = self._make_outputs(5)
        milestones = _compute_milestones(outputs)
        indices = [m["index"] for m in milestones]
        assert indices == list(range(len(indices)))

    def test_task_complete_in_last_milestone(self) -> None:
        """Last milestone is 'Task complete' for multi-brain tasks."""
        outputs = self._make_outputs(3)
        milestones = _compute_milestones(outputs)
        assert milestones[-1]["label"] == "Task complete"

    def test_fewer_outputs_than_max_returns_all(self) -> None:
        """3 outputs with max=7 → returns all (no sampling needed)."""
        outputs = self._make_outputs(3)
        milestones = _compute_milestones(outputs, max_milestones=7)
        # 3 brains → Task started + 3 completions + Task complete = 5 milestones
        assert len(milestones) <= 7
        assert len(milestones) >= 3


# ===== Integration tests: write_execution =====


@pytest.mark.asyncio
async def test_write_execution_creates_record(db_path: str) -> None:
    """write_execution() creates an execution_history record."""
    brain_outputs = {
        "brain-01": {
            "brain_id": "brain-01",
            "status": "complete",
            "output": "## Analysis",
            "duration_ms": 1500,
            "timestamp": 1000,
        }
    }
    graph_snapshot = {"nodes": [], "edges": []}

    exec_id = await write_execution(
        task_id="task-writer-001",
        brief="Test brief",
        brain_outputs=brain_outputs,
        graph_snapshot=graph_snapshot,
        db_path=db_path,
        duration_ms=1500,
        status="success",
    )

    assert exec_id is not None

    # Verify record in DB
    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        cursor = await db.conn.execute(
            "SELECT id, task_id, status, brain_count FROM execution_history WHERE id = ?",
            [exec_id],
        )
        row = await cursor.fetchone()

    assert row is not None
    assert row[0] == exec_id
    assert row[1] == "task-writer-001"
    assert row[2] == "success"
    assert row[3] == 1  # 1 brain in output


@pytest.mark.asyncio
async def test_write_execution_stores_milestones(db_path: str) -> None:
    """write_execution() persists milestones as JSON in DB."""
    brain_outputs = {
        "brain-01": {
            "brain_id": "brain-01",
            "status": "complete",
            "output": "Output",
            "duration_ms": 1000,
            "timestamp": 2000,
        },
        "brain-02": {
            "brain_id": "brain-02",
            "status": "complete",
            "output": "Output 2",
            "duration_ms": 1500,
            "timestamp": 3000,
        },
    }

    exec_id = await write_execution(
        task_id="task-milestones-001",
        brief="Milestones test",
        brain_outputs=brain_outputs,
        graph_snapshot={},
        db_path=db_path,
    )

    assert exec_id is not None

    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        cursor = await db.conn.execute(
            "SELECT milestones_json FROM execution_history WHERE id = ?",
            [exec_id],
        )
        row = await cursor.fetchone()

    assert row is not None
    milestones = json.loads(row[0])
    assert isinstance(milestones, list)
    assert len(milestones) > 0
    assert len(milestones) <= 7


@pytest.mark.asyncio
async def test_write_execution_failure_returns_none(tmp_path) -> None:
    """DB write failure returns None (never raises)."""
    # Use a path to a directory (not a file) to force DB error
    bad_path = str(tmp_path / "nonexistent_dir" / "db.sqlite")

    result = await write_execution(
        task_id="task-fail-001",
        brief="Failure test",
        brain_outputs={},
        graph_snapshot={},
        db_path=bad_path,
    )

    # Must not raise, must return None
    assert result is None


@pytest.mark.asyncio
async def test_write_execution_second_write_skipped(db_path: str) -> None:
    """Second write_execution() for same task_id is silently skipped (INSERT OR IGNORE)."""
    kwargs = {
        "task_id": "task-idempotent-001",
        "brief": "Idempotent test",
        "brain_outputs": {},
        "graph_snapshot": {},
        "db_path": db_path,
    }

    exec_id_1 = await write_execution(**kwargs)
    exec_id_2 = await write_execution(**kwargs)

    # First write succeeds, second is skipped
    assert exec_id_1 is not None
    assert exec_id_2 is None  # Skipped due to UNIQUE constraint on task_id

    # DB has exactly one record for this task_id
    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM execution_history WHERE task_id = ?",
            ["task-idempotent-001"],
        )
        row = await cursor.fetchone()

    assert row is not None
    assert row[0] == 1


@pytest.mark.asyncio
async def test_write_execution_linked_to_task(db_path: str) -> None:
    """Execution record task_id matches the provided task_id."""
    exec_id = await write_execution(
        task_id="task-linked-001",
        brief="Linked test",
        brain_outputs={},
        graph_snapshot={},
        db_path=db_path,
    )

    async with DatabaseConnection(db_path) as db:
        await db.create_execution_history_schema()
        cursor = await db.conn.execute(
            "SELECT task_id FROM execution_history WHERE id = ?",
            [exec_id],
        )
        row = await cursor.fetchone()

    assert row is not None
    assert row[0] == "task-linked-001"
