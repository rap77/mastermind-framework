"""API tests for the project-state decision endpoints."""

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
from mastermind_cli.project_state.models.decision import DecisionRecord
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
async def test_project_decision_list_returns_recent_decisions(tmp_path: Path) -> None:
    """Return recent decisions ordered by recency."""
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
                project_id="project-decisions",
                name="Project Decisions",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add_all(
            [
                DecisionRecord(
                    decision_id="dec-1",
                    project_id="project-decisions",
                    task_id=None,
                    title="Older decision",
                    status="proposed",
                    rationale_markdown="Old rationale",
                    metadata_json={"rank": 2},
                    created_at=now - timedelta(minutes=5),
                ),
                DecisionRecord(
                    decision_id="dec-2",
                    project_id="project-decisions",
                    task_id="task-9",
                    title="Newer decision",
                    status="approved",
                    rationale_markdown="New rationale",
                    metadata_json={"rank": 1},
                    created_at=now,
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-decisions/decisions?limit=10",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-decisions"
    assert [item["decision_id"] for item in body["decisions"]] == ["dec-2", "dec-1"]
    assert body["decisions"][0]["title"] == "Newer decision"


@pytest.mark.asyncio
async def test_project_decision_detail_returns_seeded_decision(tmp_path: Path) -> None:
    """Return a detailed decision record for a seeded project decision."""
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
                project_id="project-decisions",
                name="Project Decisions",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            DecisionRecord(
                decision_id="dec-9",
                project_id="project-decisions",
                task_id="task-9",
                title="Adopt Postgres as source of truth",
                status="approved",
                rationale_markdown="Postgres is canonical for project state.",
                metadata_json={"scope": "architecture"},
                created_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-decisions/decisions/dec-9",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["decision_id"] == "dec-9"
    assert body["status"] == "approved"
    assert body["metadata"] == {"scope": "architecture"}
    assert body["rationale_markdown"] == "Postgres is canonical for project state."
