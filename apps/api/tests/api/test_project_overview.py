"""API tests for the project overview endpoint."""

from __future__ import annotations

import uuid
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
async def test_project_overview_returns_404_for_missing_project(tmp_path: Path) -> None:
    """Return 404 when the project overview is requested for an unknown project."""
    db_path = str(tmp_path / "test.db")
    project_state_db_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(project_state_db_url)
    app = _build_test_app(db_path, project_state_db_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/missing-project/overview", headers=auth_headers
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Project not found"


@pytest.mark.asyncio
async def test_project_overview_returns_seeded_project(tmp_path: Path) -> None:
    """Return a minimal overview for a seeded project."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }
    session_factory = get_session_factory(database_url)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-beta",
                name="Project Beta",
                status="active",
                adapter_id="default-adapter",
                metadata_json={"seed": str(uuid.uuid4())},
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-beta/overview", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-beta"
    assert body["name"] == "Project Beta"
    assert body["status"] == "active"
    assert body["total_tasks"] == 0
    assert body["active_tasks"] == 0
    assert body["blocked_tasks"] == 0
