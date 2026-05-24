"""API tests for project time summary endpoint."""

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
async def test_project_time_summary_returns_eta_fields(tmp_path: Path) -> None:
    """Return heuristic ETA and time fields for a seeded project."""
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
                project_id="project-time-api",
                name="Project Time API",
                status="active",
                adapter_id="adapter-time",
                metadata_json={},
                created_at=now - timedelta(hours=2),
                updated_at=now,
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-complete",
                    project_id="project-time-api",
                    title="Complete task",
                    status="completed",
                    priority="normal",
                    owner_type="agent",
                    owner_id="brain-04",
                    metadata_json={"estimated_minutes": 45},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-open",
                    project_id="project-time-api",
                    title="Open task",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-05",
                    metadata_json={"estimated_effort": "2 hours"},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.add(
            TaskRun(
                run_id="run-open",
                project_id="project-time-api",
                task_id="task-open",
                actor_type="agent",
                actor_id="brain-05",
                status="running",
                started_at=now - timedelta(minutes=10),
                ended_at=None,
                metadata_json={},
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-time-api/time-summary",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-time-api"
    assert body["completed_tasks"] == 1
    assert body["remaining_tasks"] == 1
    assert body["estimated_total_minutes"] == 165
    assert body["estimated_remaining_minutes"] == 120
    assert body["active_run_count"] == 1
    assert body["projected_completion_at"] is not None
