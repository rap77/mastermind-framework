"""API tests for project list and detail endpoints."""

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
async def test_project_list_returns_recent_projects(tmp_path: Path) -> None:
    """Return recent projects ordered by update timestamp."""
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
        session.add_all(
            [
                Project(
                    project_id="project-old",
                    name="Project Old",
                    status="paused",
                    adapter_id="adapter-a",
                    metadata_json={"owner": "team-a"},
                    created_at=now - timedelta(days=1),
                    updated_at=now - timedelta(hours=2),
                ),
                Project(
                    project_id="project-new",
                    name="Project New",
                    status="active",
                    adapter_id="adapter-b",
                    metadata_json={"owner": "team-b"},
                    created_at=now - timedelta(hours=5),
                    updated_at=now,
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/api/projects?limit=10", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert [item["project_id"] for item in body["projects"]] == [
        "project-new",
        "project-old",
    ]


@pytest.mark.asyncio
async def test_project_detail_returns_seeded_project(tmp_path: Path) -> None:
    """Return a detailed project view for a seeded project."""
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
                project_id="project-detail",
                name="Project Detail",
                status="active",
                adapter_id="adapter-x",
                metadata_json={"domain": "finance"},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-detail", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-detail"
    assert body["name"] == "Project Detail"
    assert body["adapter_id"] == "adapter-x"
    assert body["metadata"] == {"domain": "finance"}
