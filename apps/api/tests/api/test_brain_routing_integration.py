"""Tests for brain-to-brain routing integration in task_runner — Fase 4.

Tests that run_brain_task() integrates with brain_router to enable
sequential delegation after a flow completes.

Validates:
- route_to_brain() is called after brain task completes
- Routing triggers another brain execution when target not in original flow
- No extra execution when routing returns no match
- WebSocket events are emitted for routing decisions
- Parent task_id is preserved (Opción A)
- Routed brain failure does NOT fail the parent task
- Experience records are logged for routed brains

Brain #6 guidance: TDD estricto — tests first, then implementation.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio

from mastermind_cli.state.database import DatabaseConnection


# ===== Fixtures =====


@pytest.fixture
def task_id():
    return "task-routing-test-001"


@pytest_asyncio.fixture
async def db_with_task(tmp_path, task_id):
    """DB with an execution record pre-inserted in 'pending' state."""
    db_file = str(tmp_path / "test_routing.db")
    async with DatabaseConnection(db_file) as db:
        await db.create_task_schema()
        await db.create_experience_schema()
        await db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status, user_id)
               VALUES (?, ?, ?, datetime('now'), ?, ?)""",
            [task_id, "{}", "Crear componente React para login", "pending", "user-001"],
        )
        await db.conn.commit()
    return db_file


def _make_mock_output(data=None):
    """Create a mock brain output with model_dump."""
    mock = MagicMock()
    mock.model_dump.return_value = data or {"result": "ok"}
    return mock


# ===== Test: Routing triggers another brain =====


@pytest.mark.asyncio
async def test_routing_triggers_routed_brain_execution(db_with_task, task_id):
    """When route_to_brain returns a target, run_brain_task executes that brain too.

    Scenario: Flow runs brain-01-product, brief mentions 'react' → brain-04-frontend
    should be executed as a routed brain.
    """
    mock_output_brain1 = _make_mock_output({"positioning": "Product strategy"})
    mock_output_brain4 = _make_mock_output({"framework": "React"})

    call_count = {"execute_flow": 0}
    captured_brain_ids: list[list[str]] = []

    async def mock_execute_flow(_brief, brain_ids):
        call_count["execute_flow"] += 1
        captured_brain_ids.append(list(brain_ids))
        if call_count["execute_flow"] == 1:
            # First call: original flow
            return {"brain-01-product": mock_output_brain1}
        else:
            # Second call: routed brain
            return {"brain-04-frontend": mock_output_brain4}

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",
        ) as mock_route,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ) as _mock_emit,
    ):
        instance = MockCoord.return_value
        instance.execute_flow = mock_execute_flow

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify: route_to_brain was called with the brief and source brain
    assert mock_route.called, "route_to_brain should be called after flow completes"

    # Verify: execute_flow was called TWICE (original + routed)
    assert (
        call_count["execute_flow"] == 2
    ), f"Expected 2 execute_flow calls, got {call_count['execute_flow']}"

    # Verify: second call was for the routed brain only
    assert captured_brain_ids[1] == ["brain-04-frontend"]


@pytest.mark.asyncio
async def test_routing_no_match_no_extra_execution(db_with_task, task_id):
    """When route_to_brain returns None, no extra brain execution happens."""
    mock_output = _make_mock_output({"result": "ok"})

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value=None,
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={"brain-01-product": mock_output}
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Definir roadmap Q2 para nuevo feature",
            flow="validation_only",
            db_path=db_with_task,
        )

    # execute_flow should only be called ONCE (no routing)
    assert instance.execute_flow.call_count == 1


# ===== Test: WebSocket events =====


@pytest.mark.asyncio
async def test_routing_emits_websocket_event(db_with_task, task_id):
    """emit_brain_routing_event is called when routing triggers another brain."""
    mock_output = _make_mock_output({"result": "ok"})

    async def mock_execute_flow(_brief, brain_ids):
        if "brain-04-frontend" in brain_ids:
            return {"brain-04-frontend": mock_output}
        return {"brain-01-product": mock_output}

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ) as mock_emit,
    ):
        instance = MockCoord.return_value
        instance.execute_flow = mock_execute_flow

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify: emit_brain_routing_event was called
    assert mock_emit.called, "emit_brain_routing_event should be called on routing"

    # Verify: parent task_id is used (Opción A)
    call_kwargs = mock_emit.call_args.kwargs
    assert (
        call_kwargs["task_id"] == task_id
    ), "Parent task_id must be used in routing event (Opción A)"

    # Verify: from/to brain IDs are correct
    assert call_kwargs["from_brain"] == "brain-01-product"
    assert call_kwargs["to_brain"] == "brain-04-frontend"


@pytest.mark.asyncio
async def test_routing_event_preserves_parent_task_id(db_with_task, task_id):
    """The task_id in the WS event is the parent task_id, never a sub-task endpoint.

    Brain #4 guidance: Opción A — reuse parent task_id, zero breaking changes.
    """
    mock_output = _make_mock_output({"result": "ok"})

    async def mock_execute_flow(_brief, brain_ids):
        return (
            {"brain-01-product": mock_output}
            if "brain-01-product" in brain_ids
            else {"brain-04-frontend": mock_output}
        )

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ) as mock_emit,
    ):
        instance = MockCoord.return_value
        instance.execute_flow = mock_execute_flow

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify: task_id kwarg to emit_brain_routing_event is the parent task_id
    assert mock_emit.call_args.kwargs["task_id"] == task_id


# ===== Test: Error handling =====


@pytest.mark.asyncio
async def test_routed_brain_failure_does_not_fail_parent(db_with_task, task_id):
    """If the routed brain fails, the parent task still succeeds.

    Routing is a best-effort extension — failure in routed brain should not
    affect the parent task's completed status.
    """
    mock_output = _make_mock_output({"result": "ok"})
    call_count = {"execute_flow": 0}

    async def mock_execute_flow(_brief, _brain_ids):
        call_count["execute_flow"] += 1
        if call_count["execute_flow"] == 1:
            return {"brain-01-product": mock_output}
        else:
            raise RuntimeError("Routed brain exploded")

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = mock_execute_flow

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify: parent task is still completed despite routed brain failure
    async with DatabaseConnection(db_with_task) as db:
        cursor = await db.conn.execute(
            "SELECT status FROM executions WHERE id = ?", [task_id]
        )
        row = await cursor.fetchone()
        assert row is not None, "Execution row must exist"
        assert row[0] == "completed", f"Parent task should be completed, got {row[0]}"


# ===== Test: No routing when target already in flow =====


@pytest.mark.asyncio
async def test_no_routing_when_target_brain_already_in_flow(db_with_task, task_id):
    """If route_to_brain returns a brain already in the original flow, skip it.

    Avoids duplicate brain execution.
    """
    mock_output = _make_mock_output({"result": "ok"})

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch("mastermind_cli.api.services.task_runner.FlowDetector") as MockDetector,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",  # This brain is already in the flow
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ) as mock_emit,
    ):
        # Flow includes both brain-01 AND brain-04
        det_instance = MockDetector.return_value
        det_instance.detect.return_value = "full_stack"
        det_instance.get_flow_sequence.return_value = [1, 4]

        instance = MockCoord.return_value
        instance.execute_flow = AsyncMock(
            return_value={
                "brain-01-product": mock_output,
                "brain-04-frontend": mock_output,
            }
        )

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow=None,
            db_path=db_with_task,
        )

    # Verify: execute_flow called only once (original flow, no routed execution)
    assert (
        instance.execute_flow.call_count == 1
    ), "Should not re-execute brain already in the flow"

    # Verify: no routing event emitted for already-present brain
    assert not mock_emit.called


# ===== Test: Experience logging for routed brains =====


@pytest.mark.asyncio
async def test_experience_logged_for_routed_brain(db_with_task, task_id):
    """Experience records are logged for routed brain execution too."""
    mock_output_brain1 = _make_mock_output({"positioning": "Product strategy"})
    mock_output_brain4 = _make_mock_output({"framework": "React"})

    async def mock_execute_flow(_brief, brain_ids):
        if "brain-04-frontend" in brain_ids:
            return {"brain-04-frontend": mock_output_brain4}
        return {"brain-01-product": mock_output_brain1}

    with (
        patch(
            "mastermind_cli.api.services.task_runner.create_stateless_coordinator"
        ) as MockCoord,
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.route_to_brain",
            return_value="brain-04-frontend",
        ),
        patch(
            "mastermind_cli.api.services.task_runner._brain_router.emit_brain_routing_event",
            new_callable=AsyncMock,
        ),
    ):
        instance = MockCoord.return_value
        instance.execute_flow = mock_execute_flow

        from mastermind_cli.api.services.task_runner import run_brain_task

        await run_brain_task(
            task_id=task_id,
            brief="Crear componente React para login form",
            flow="validation_only",
            db_path=db_with_task,
        )

    # Verify: experience record for routed brain exists
    async with DatabaseConnection(db_with_task) as db:
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM experience_records WHERE brain_id = ?",
            ["brain-04-frontend"],
        )
        row = await cursor.fetchone()
        count = row[0] if row else 0

    assert count >= 1, "Routed brain should have an experience record"
