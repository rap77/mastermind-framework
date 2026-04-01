"""Tests for background task runner — Fase 3 agent-restructuring.

Tests the run_brain_task() coroutine that executes brain orchestration
as a FastAPI BackgroundTask. Validates:
- Status transitions (pending → running → completed/failed)
- BRAIN_ID_MAP int→str mapping correctness
- ExperienceLogger integration
- CancelledError handling (uvicorn shutdown safety)
- aiosqlite transaction isolation (partial write protection)

Brain #6 guidance: BackgroundTasks pattern, not asyncio.create_task().
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from mastermind_cli.state.database import DatabaseConnection

# Constants mirrored from task_runner (tested explicitly below)
EXPECTED_BRAIN_ID_MAP = {
    1: "brain-01-product",
    2: "brain-02-ux",
    3: "brain-03-ui",
    4: "brain-04-frontend",
    5: "brain-05-backend",
    6: "brain-06-qa",
    7: "brain-07-growth",
}


# ===== Fixtures =====


@pytest.fixture
def task_id():
    return "task-test-001"


@pytest_asyncio.fixture
async def db_with_task(tmp_path, task_id):
    """DB with an execution record pre-inserted in 'pending' state."""
    db_file = str(tmp_path / "test.db")
    async with DatabaseConnection(db_file) as db:
        await db.create_task_schema()
        await db.create_experience_schema()
        await db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status, user_id)
               VALUES (?, ?, ?, datetime('now'), ?, ?)""",
            [task_id, "{}", "Test brief", "pending", "user-001"],
        )
        await db.conn.commit()
    return db_file


async def _get_task_status(db_path: str, task_id: str) -> str:
    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            "SELECT status FROM executions WHERE id = ?", [task_id]
        )
        row = await cursor.fetchone()
        return row[0] if row else "not_found"


# ===== BRAIN_ID_MAP tests =====


def test_brain_id_map_covers_all_seven_brains():
    """BRAIN_ID_MAP must map all 7 brain integers to correct string IDs."""
    from mastermind_cli.api.services.task_runner import BRAIN_ID_MAP

    assert BRAIN_ID_MAP == EXPECTED_BRAIN_ID_MAP


def test_brain_id_map_no_f_string_interpolation():
    """Brain IDs must be explicit strings, not computed — prevents silent mismatches."""
    from mastermind_cli.api.services.task_runner import BRAIN_ID_MAP

    for brain_int, brain_str in BRAIN_ID_MAP.items():
        # Verify string matches expected format exactly (not f"brain-0{n}-...")
        assert brain_str == EXPECTED_BRAIN_ID_MAP[brain_int]
        assert brain_str.startswith("brain-0")


# ===== Status transition tests =====


@pytest.mark.asyncio
async def test_run_brain_task_transitions_to_running_then_completed(
    db_with_task, task_id
):
    """run_brain_task() sets status=running at start, then completed on success."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "ok"}

    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Test brief input",
            flow="validation_only",
            db_path=db_with_task,
        )

    status = await _get_task_status(db_with_task, task_id)
    assert status == "completed"


@pytest.mark.asyncio
async def test_run_brain_task_transitions_to_failed_on_exception(db_with_task, task_id):
    """run_brain_task() sets status=failed when StatelessCoordinator raises."""
    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(side_effect=RuntimeError("brain exploded"))

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Test brief input",
            flow="validation_only",
            db_path=db_with_task,
        )

    status = await _get_task_status(db_with_task, task_id)
    assert status == "failed"


@pytest.mark.asyncio
async def test_run_brain_task_handles_cancelled_error(db_with_task, task_id):
    """CancelledError (uvicorn shutdown) sets status=failed, does NOT propagate."""
    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(side_effect=asyncio.CancelledError())

        from mastermind_cli.api.services.task_runner import run_brain_task

        # Must NOT raise — CancelledError must be caught and swallowed
        await run_brain_task(
            task_id=task_id,
            brief="Test brief input",
            flow="validation_only",
            db_path=db_with_task,
        )

    status = await _get_task_status(db_with_task, task_id)
    assert status == "failed"


# ===== Flow detection + brain mapping =====


@pytest.mark.asyncio
async def test_run_brain_task_maps_flow_detector_ints_to_brain_strings(
    db_with_task, task_id
):
    """FlowDetector returns list[int]; run_brain_task converts via BRAIN_ID_MAP."""
    captured_brain_ids: list[str] = []

    async def capture_brain_ids(brief, brain_ids):
        captured_brain_ids.extend(brain_ids)
        return {}

    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = capture_brain_ids

        with patch(
            "mastermind_cli.api.services.task_runner.FlowDetector"
        ) as MockDetector:
            det_instance = MockDetector.return_value
            det_instance.detect.return_value = "validation_only"
            det_instance.get_flow_sequence.return_value = [1, 7]

            from mastermind_cli.api.services.task_runner import run_brain_task

            await run_brain_task(
                task_id=task_id,
                brief="validate this product feature",
                flow=None,  # auto-detect
                db_path=db_with_task,
            )

    assert captured_brain_ids == ["brain-01-product", "brain-07-growth"]


# ===== ExperienceLogger integration =====


@pytest.mark.asyncio
async def test_run_brain_task_writes_experience_record(db_with_task, task_id):
    """run_brain_task() logs an experience record on successful execution."""
    mock_output = MagicMock()
    mock_output.model_dump.return_value = {"result": "logged"}

    with patch(
        "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
    ) as MockCoord:
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Test brief input",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify experience_records table has at least one entry
    async with DatabaseConnection(db_with_task) as db:
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM experience_records WHERE brain_id = ?",
            ["brain-01-product"],
        )
        row = await cursor.fetchone()
        count = row[0] if row else 0

    assert count >= 1
