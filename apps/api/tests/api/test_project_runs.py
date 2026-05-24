"""API tests for project run endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from mastermind_cli.api.app import create_app
from mastermind_cli.api.dependencies import get_db_path, get_project_state_db_url
from mastermind_cli.api.routes.auth import create_access_token
from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun


def _build_test_app(db_path: str, project_state_db_url: str) -> FastAPI:
    """Create an app instance wired to temporary test databases."""
    app = create_app(db_path)

    async def _override_db_path() -> str:
        """Provide the test task-state database path."""
        return db_path

    async def _override_project_state_db_url() -> str:
        """Provide the test project-state database URL."""
        return project_state_db_url

    app.dependency_overrides[get_db_path] = _override_db_path
    app.dependency_overrides[get_project_state_db_url] = _override_project_state_db_url
    return app


@pytest.mark.asyncio
async def test_project_active_runs_returns_only_open_runs(tmp_path: Path) -> None:
    """Return only active runs for a project ordered by start time."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-runs",
                name="Project Runs",
                status="active",
                adapter_id="adapter-runs",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-new",
                    project_id="project-runs",
                    title="Newest active task",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-04",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-old",
                    project_id="project-runs",
                    title="Older active task",
                    status="in_progress",
                    priority="normal",
                    owner_type="agent",
                    owner_id="brain-05",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-ended",
                    project_id="project-runs",
                    title="Ended task",
                    status="done",
                    priority="normal",
                    owner_type="agent",
                    owner_id="brain-06",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.add_all(
            [
                TaskRun(
                    run_id="run-new",
                    project_id="project-runs",
                    task_id="task-new",
                    actor_type="agent",
                    actor_id="brain-04",
                    status="running",
                    started_at=now,
                    ended_at=None,
                    metadata_json={"mode": "hybrid"},
                ),
                TaskRun(
                    run_id="run-old",
                    project_id="project-runs",
                    task_id="task-old",
                    actor_type="agent",
                    actor_id="brain-05",
                    status="running",
                    started_at=now - timedelta(minutes=5),
                    ended_at=None,
                    metadata_json={},
                ),
                TaskRun(
                    run_id="run-ended",
                    project_id="project-runs",
                    task_id="task-ended",
                    actor_type="agent",
                    actor_id="brain-06",
                    status="completed",
                    started_at=now - timedelta(minutes=10),
                    ended_at=now - timedelta(minutes=1),
                    metadata_json={},
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-runs/runs/active",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert [item["run_id"] for item in body["runs"]] == ["run-new", "run-old"]
    assert body["runs"][0]["task_title"] == "Newest active task"


@pytest.mark.asyncio
async def test_project_run_detail_returns_seeded_run(tmp_path: Path) -> None:
    """Return a detailed run view for a seeded run."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-run-detail",
                name="Project Run Detail",
                status="active",
                adapter_id="adapter-runs",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-detail",
                project_id="project-run-detail",
                title="Detailed run task",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            TaskRun(
                run_id="run-detail",
                project_id="project-run-detail",
                task_id="task-detail",
                actor_type="agent",
                actor_id="brain-04",
                status="running",
                started_at=now,
                ended_at=None,
                metadata_json={"window_mode": "automatic_cycle"},
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-run-detail/runs/run-detail",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["run_id"] == "run-detail"
    assert body["task_id"] == "task-detail"
    assert body["task_title"] == "Detailed run task"
    assert body["metadata"] == {"window_mode": "automatic_cycle"}
