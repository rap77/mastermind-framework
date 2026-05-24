"""API tests for project-state task detail and checkpoint endpoints."""

from __future__ import annotations

from datetime import datetime, timezone
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
from mastermind_cli.project_state.models.checkpoint import Checkpoint
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task


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
async def test_project_task_detail_returns_seeded_task(tmp_path: Path) -> None:
    """Return a task detail view for a seeded project task."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-gamma",
                name="Project Gamma",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-7",
                project_id="project-gamma",
                title="Design dashboard widgets",
                status="blocked",
                priority="high",
                owner_type="human",
                owner_id="designer-1",
                metadata_json={"surface": "web"},
                constraints={"review_required": True},
                completion_criteria={"mockup_approved": True},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-gamma/tasks/task-7", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["task_id"] == "task-7"
    assert body["status"] == "blocked"
    assert body["owner_type"] == "human"
    assert body["metadata"] == {"surface": "web"}


@pytest.mark.asyncio
async def test_latest_project_checkpoint_returns_seeded_checkpoint(
    tmp_path: Path,
) -> None:
    """Return the latest checkpoint for a seeded project."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-gamma",
                name="Project Gamma",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-7",
                project_id="project-gamma",
                title="Design dashboard widgets",
                status="blocked",
                priority="high",
                owner_type="human",
                owner_id="designer-1",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            Checkpoint(
                checkpoint_id="chk-99",
                project_id="project-gamma",
                task_id="task-7",
                run_id="run-99",
                context_summary={"current_step": "ux-review"},
                resume_state={"tab": "tasks"},
                next_step_summary="Resume review with UX brain",
                created_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-gamma/checkpoints/latest", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["checkpoint_id"] == "chk-99"
    assert body["run_id"] == "run-99"
    assert body["context_summary"] == {"current_step": "ux-review"}
    assert body["resume_state"] == {"tab": "tasks"}
