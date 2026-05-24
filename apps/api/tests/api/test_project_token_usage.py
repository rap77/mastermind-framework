"""API tests for project token usage endpoint."""

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
from mastermind_cli.project_state.models.token_usage import TokenUsageEvent


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
async def test_project_token_usage_returns_recent_events(tmp_path: Path) -> None:
    """Return recent token usage events ordered by timestamp."""
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
                project_id="project-usage",
                name="Project Usage",
                status="active",
                adapter_id="adapter-usage",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add_all(
            [
                TokenUsageEvent(
                    usage_event_id="usage-new",
                    project_id="project-usage",
                    task_id="task-1",
                    run_id="run-1",
                    provider="anthropic",
                    model="claude",
                    auth_mode="subscription",
                    prompt_tokens=40,
                    completion_tokens=20,
                    estimated_cost=0.8,
                    metadata_json={"window_mode": "hybrid"},
                    created_at=now,
                ),
                TokenUsageEvent(
                    usage_event_id="usage-old",
                    project_id="project-usage",
                    task_id="task-2",
                    run_id="run-2",
                    provider="openai",
                    model="gpt-5",
                    auth_mode="api_key",
                    prompt_tokens=10,
                    completion_tokens=5,
                    estimated_cost=0.15,
                    metadata_json={},
                    created_at=now - timedelta(minutes=1),
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-usage/token-usage?limit=10",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert [item["usage_event_id"] for item in body["events"]] == [
        "usage-new",
        "usage-old",
    ]
    assert body["events"][0]["metadata"] == {"window_mode": "hybrid"}
