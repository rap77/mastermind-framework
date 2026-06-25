"""Test task management endpoints (CRUD operations).

Requirements: UI-06, BE-02
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from unittest.mock import patch
from typing import Any

import pytest

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.api.dependencies import get_governance
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from tests.api.conftest import TEST_USER_ID


@pytest.mark.asyncio
async def test_create_task(client: Any, auth_headers: Any) -> None:
    """POST /api/tasks creates task and returns task_id."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Build a landing page"},
    )
    assert response.status_code == 201
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "pending"
    assert "created_at" in data


@pytest.mark.asyncio
async def test_create_task_persists_project_state_task_and_run(
    client: Any, auth_headers: Any, db_path: Any
) -> None:
    """POST /api/tasks writes the transitional project_state task and run records."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Persist me in project_state"},
    )
    assert response.status_code == 201
    task_id = response.json()["task_id"]

    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        task = session.get(Task, task_id)
        run = session.get(TaskRun, task_id)

    assert task is not None
    assert task.project_id == f"user-tasks:{TEST_USER_ID}"
    assert task.status == "pending"
    assert task.metadata_json["brief"] == "Persist me in project_state"

    assert run is not None
    assert run.project_id == f"user-tasks:{TEST_USER_ID}"
    assert run.task_id == task_id
    assert run.status == "pending"


@pytest.mark.asyncio
async def test_create_task_forwards_governance_dependency(
    app: Any, client: Any, auth_headers: Any
) -> None:
    """POST /api/tasks forwards the app-scoped governance provider."""
    sentinel = object()

    async def _override_governance() -> object:
        return sentinel

    app.dependency_overrides[get_governance] = _override_governance
    try:
        with patch("mastermind_cli.api.routes.tasks.run_brain_task") as mock_runner:
            response = await client.post(
                "/api/tasks",
                headers=auth_headers,
                json={"brief": "Create task with governance"},
            )
        assert response.status_code == 201
        assert mock_runner.call_args.kwargs["governance"] is sentinel
    finally:
        app.dependency_overrides.pop(get_governance, None)


@pytest.mark.asyncio
async def test_create_task_validation(client: Any, auth_headers: Any) -> None:
    """Empty brief returns 422."""
    response = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": ""},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_list_tasks(client: Any, auth_headers: Any) -> None:
    """GET /api/tasks returns list of user's tasks."""
    # Create a task first
    await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task for list test"},
    )

    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "tasks" in data
    assert "total" in data
    assert isinstance(data["tasks"], list)
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_list_tasks_reads_project_state_records_only(
    client: Any, auth_headers: Any, db_path: Any
) -> None:
    """GET /api/tasks lists records from project_state even without legacy executions."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        session.add(
            Project(
                project_id=f"user-tasks:{TEST_USER_ID}",
                name="User task workspace",
                status="active",
                adapter_id="legacy-tasks",
                metadata_json={"user_id": TEST_USER_ID},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="ps-task-001",
                project_id=f"user-tasks:{TEST_USER_ID}",
                title="Project state task",
                status="pending",
                priority="normal",
                owner_type="user",
                owner_id=TEST_USER_ID,
                metadata_json={"brief": "Project state only task"},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    response = await client.get("/api/tasks", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    assert data["total"] == 1
    assert data["tasks"][0]["id"] == "ps-task-001"
    assert data["tasks"][0]["brief"] == "Project state only task"


@pytest.mark.asyncio
async def test_get_task(client: Any, auth_headers: Any) -> None:
    """GET /api/tasks/{id} returns task; 404 for unknown."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task for get test"},
    )
    task_id = create.json()["task_id"]

    response = await client.get(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["id"] == task_id

    not_found = await client.get("/api/tasks/nonexistent-id", headers=auth_headers)
    assert not_found.status_code == 404


@pytest.mark.asyncio
async def test_get_task_reads_project_state_record_only(
    client: Any, auth_headers: Any, db_path: Any
) -> None:
    """GET /api/tasks/{id} reads from project_state even without legacy executions."""
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        session.add(
            Project(
                project_id=f"user-tasks:{TEST_USER_ID}",
                name="User task workspace",
                status="active",
                adapter_id="legacy-tasks",
                metadata_json={"user_id": TEST_USER_ID},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="ps-task-get-001",
                project_id=f"user-tasks:{TEST_USER_ID}",
                title="Project state get task",
                status="pending",
                priority="normal",
                owner_type="user",
                owner_id=TEST_USER_ID,
                metadata_json={
                    "brief": "Project state only get",
                    "flow_config": '{"mode":"ps-only"}',
                },
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    response = await client.get("/api/tasks/ps-task-get-001", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "ps-task-get-001"
    assert data["brief"] == "Project state only get"
    assert data["status"] == "pending"
    assert data["flow_config"] == '{"mode":"ps-only"}'


@pytest.mark.asyncio
async def test_cancel_task(client: Any, auth_headers: Any) -> None:
    """DELETE /api/tasks/{id} cancels task."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task to cancel"},
    )
    task_id = create.json()["task_id"]

    response = await client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == task_id


@pytest.mark.asyncio
async def test_cancel_task_updates_project_state_status(
    client: Any, auth_headers: Any, db_path: Any
) -> None:
    """DELETE /api/tasks/{id} updates project_state task status."""
    create = await client.post(
        "/api/tasks",
        headers=auth_headers,
        json={"brief": "Task to cancel in project_state"},
    )
    task_id = create.json()["task_id"]

    response = await client.delete(f"/api/tasks/{task_id}", headers=auth_headers)
    assert response.status_code == 200

    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        task = session.get(Task, task_id)
        run = session.get(TaskRun, task_id)

    assert task is not None
    assert task.status == "cancelled"
    assert run is not None
    assert run.status == "cancelled"
    assert run.ended_at is not None


@pytest.mark.asyncio
async def test_session_isolation(
    client: Any, auth_headers: Any, auth_headers_b: Any
) -> None:
    """User A cannot access User B's tasks."""
    # Create task as user B
    create_b = await client.post(
        "/api/tasks",
        headers=auth_headers_b,
        json={"brief": "User B private task"},
    )
    task_id_b = create_b.json()["task_id"]

    # User A list — must NOT include user B's task
    list_a = await client.get("/api/tasks", headers=auth_headers)
    task_ids_a = [t["id"] for t in list_a.json()["tasks"]]
    assert task_id_b not in task_ids_a

    # User A get — must get 404
    get_resp = await client.get(f"/api/tasks/{task_id_b}", headers=auth_headers)
    assert get_resp.status_code == 404


# ===== BE-02: Graph Endpoint Contract Tests =====


class TestTaskGraphBE02:
    """Tests for GET /api/tasks/{id}/graph — BE-02 React Flow compatibility.

    Requirements: BE-02
    Covers: layout_positions field presence, source/target edge field names,
            empty flow_config shape, 404 for unknown task.
    """

    @pytest.mark.asyncio
    async def test_graph_empty_flow_config_returns_valid_shape(
        self: "TestTaskGraphBE02", client: Any, auth_headers: Any
    ) -> None:
        """Empty flow_config returns response with all required keys including layout_positions."""
        # Create a task (no flow_config set — defaults to empty)
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Graph shape test task"},
        )
        assert create.status_code == 201
        task_id = create.json()["task_id"]

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # BE-02: all required keys must be present
        assert "nodes" in data
        assert "edges" in data
        assert "max_level" in data
        assert "max_parallelism" in data
        assert "layout_positions" in data

        # Empty task → empty collections
        assert data["nodes"] == []
        assert data["edges"] == []
        assert data["max_level"] == 0
        assert data["max_parallelism"] == 0

    @pytest.mark.asyncio
    async def test_graph_layout_positions_field_is_null(
        self: "TestTaskGraphBE02", client: Any, auth_headers: Any
    ) -> None:
        """layout_positions is null when server does not compute layout (Phase 08 deferred)."""
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Layout positions null test"},
        )
        task_id = create.json()["task_id"]

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        # layout_positions must be null (not missing, not an empty dict)
        assert "layout_positions" in data
        assert data["layout_positions"] is None

    @pytest.mark.asyncio
    async def test_graph_edges_use_source_target_fields(
        self: "TestTaskGraphBE02", client: Any, auth_headers: Any, db_path: str
    ) -> None:
        """Edge objects serialize with 'source' and 'target' keys — React Flow compatible."""
        # Create task then patch canonical project_state flow_config
        create = await client.post(
            "/api/tasks",
            headers=auth_headers,
            json={"brief": "Edge field names test"},
        )
        assert create.status_code == 201
        task_id = create.json()["task_id"]

        flow_config = {
            "nodes": {
                "brain-01": [],
                "brain-02": ["brain-01"],
            },
            "edges": {
                "brain-02": ["brain-01"],
            },
        }
        database_url = f"sqlite:///{db_path}.project_state"
        dispose_engines()
        session_factory = get_session_factory(database_url)
        with session_factory() as session:
            task = session.get(Task, task_id)
            assert task is not None
            task.metadata_json = {
                **task.metadata_json,
                "flow_config": json.dumps(flow_config),
            }
            session.add(task)
            session.commit()

        response = await client.get(f"/api/tasks/{task_id}/graph", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()

        assert len(data["edges"]) == 1
        edge = data["edges"][0]

        # BE-02: React Flow requires 'source' and 'target'
        assert "source" in edge, f"Edge missing 'source' key. Got: {list(edge.keys())}"
        assert "target" in edge, f"Edge missing 'target' key. Got: {list(edge.keys())}"
        assert edge["source"] == "brain-01"
        assert edge["target"] == "brain-02"

        # Must NOT have old 'from'/'to' field names
        assert "from" not in edge
        assert "to" not in edge

    @pytest.mark.asyncio
    async def test_graph_reads_project_state_flow_config_only(
        self: "TestTaskGraphBE02", client: Any, auth_headers: Any, db_path: str
    ) -> None:
        """GET /api/tasks/{id}/graph can render from project_state without legacy executions flow_config."""
        database_url = f"sqlite:///{db_path}.project_state"
        dispose_engines()
        initialize_database(database_url)
        session_factory = get_session_factory(database_url)
        now = datetime.now(timezone.utc)
        with session_factory() as session:
            session.add(
                Project(
                    project_id=f"user-tasks:{TEST_USER_ID}",
                    name="User task workspace",
                    status="active",
                    adapter_id="legacy-tasks",
                    metadata_json={"user_id": TEST_USER_ID},
                    created_at=now,
                    updated_at=now,
                )
            )
            session.add(
                Task(
                    task_id="ps-graph-001",
                    project_id=f"user-tasks:{TEST_USER_ID}",
                    title="Project state graph task",
                    status="running",
                    priority="normal",
                    owner_type="user",
                    owner_id=TEST_USER_ID,
                    metadata_json={
                        "brief": "Project state graph brief",
                        "flow_config": json.dumps(
                            {
                                "nodes": {
                                    "brain-01": [],
                                    "brain-02": ["brain-01"],
                                },
                                "edges": {
                                    "brain-02": ["brain-01"],
                                },
                            }
                        ),
                    },
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                )
            )
            session.commit()

        response = await client.get(
            "/api/tasks/ps-graph-001/graph", headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        assert data["edges"][0]["source"] == "brain-01"
        assert data["edges"][0]["target"] == "brain-02"

    @pytest.mark.asyncio
    async def test_graph_returns_404_for_unknown_task(
        self: "TestTaskGraphBE02", client: Any, auth_headers: Any
    ) -> None:
        """GET /api/tasks/{id}/graph returns 404 for unknown task_id."""
        response = await client.get(
            "/api/tasks/nonexistent-task-id-99999/graph", headers=auth_headers
        )
        assert response.status_code == 404
