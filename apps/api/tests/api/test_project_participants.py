"""API tests for project participants endpoints (collaboration-rbac slice)."""

from __future__ import annotations

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
        return db_path

    async def _override_project_state_db_url() -> str:
        return project_state_db_url

    app.dependency_overrides[get_db_path] = _override_db_path
    app.dependency_overrides[get_project_state_db_url] = _override_project_state_db_url
    return app


def _seed_project(database_url: str, project_id: str = "proj-001") -> None:
    """Seed a project record required for FK constraints."""
    from datetime import datetime, timezone

    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        session.add(
            Project(
                project_id=project_id,
                name="Test Project",
                status="active",
                metadata_json={},
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
        )
        session.commit()


@pytest.mark.asyncio
async def test_add_participant_returns_201(tmp_path: Path) -> None:
    """POST returns 201 with created record."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    _seed_project(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {"Authorization": f"Bearer {create_access_token('user-001')}"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/projects/proj-001/participants",
            json={
                "participant_id": "alice",
                "participant_type": "human",
                "role": "owner",
            },
            headers=auth_headers,
        )
    assert response.status_code == 201
    body = response.json()
    assert body["project_id"] == "proj-001"
    assert body["participant_id"] == "alice"
    assert body["role"] == "owner"


@pytest.mark.asyncio
async def test_list_participants_returns_200(tmp_path: Path) -> None:
    """GET returns 200 with participant list."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    _seed_project(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {"Authorization": f"Bearer {create_access_token('user-001')}"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/api/projects/proj-001/participants",
            json={
                "participant_id": "alice",
                "participant_type": "human",
                "role": "owner",
            },
            headers=auth_headers,
        )
        await client.post(
            "/api/projects/proj-001/participants",
            json={
                "participant_id": "bot-1",
                "participant_type": "agent",
                "role": "executor",
            },
            headers=auth_headers,
        )
        response = await client.get(
            "/api/projects/proj-001/participants", headers=auth_headers
        )
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2


@pytest.mark.asyncio
async def test_delete_participant_returns_204(tmp_path: Path) -> None:
    """DELETE returns 204."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    _seed_project(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {"Authorization": f"Bearer {create_access_token('user-001')}"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        await client.post(
            "/api/projects/proj-001/participants",
            json={
                "participant_id": "alice",
                "participant_type": "human",
                "role": "reviewer",
            },
            headers=auth_headers,
        )
        response = await client.delete(
            "/api/projects/proj-001/participants/alice", headers=auth_headers
        )
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_add_participant_invalid_role_returns_422(tmp_path: Path) -> None:
    """POST with invalid role returns 422."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    _seed_project(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {"Authorization": f"Bearer {create_access_token('user-001')}"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/projects/proj-001/participants",
            json={
                "participant_id": "alice",
                "participant_type": "human",
                "role": "not-a-real-role",
            },
            headers=auth_headers,
        )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_delete_nonexistent_participant_returns_404(tmp_path: Path) -> None:
    """DELETE non-existent participant returns 404."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    _seed_project(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {"Authorization": f"Bearer {create_access_token('user-001')}"}
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.delete(
            "/api/projects/proj-001/participants/nobody", headers=auth_headers
        )
    assert response.status_code == 404
