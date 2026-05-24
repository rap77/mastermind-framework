"""API tests for the project-state cost summary endpoint."""

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
from mastermind_cli.project_state.models.task import Task
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
async def test_project_cost_summary_returns_aggregated_totals(tmp_path: Path) -> None:
    """Return aggregated token and cost totals for a seeded project."""
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
                project_id="project-costs",
                name="Project Costs",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-costs",
                project_id="project-costs",
                title="Track runtime spend",
                status="in_progress",
                priority="normal",
                owner_type="agent",
                owner_id="brain-07",
                metadata_json={},
                constraints={},
                completion_criteria={},
            )
        )
        session.add_all(
            [
                TokenUsageEvent(
                    usage_event_id=str(uuid.uuid4()),
                    project_id="project-costs",
                    task_id="task-costs",
                    run_id="run-1",
                    provider="anthropic",
                    model="claude",
                    auth_mode="subscription",
                    prompt_tokens=100,
                    completion_tokens=50,
                    estimated_cost=1.25,
                    metadata_json={},
                ),
                TokenUsageEvent(
                    usage_event_id=str(uuid.uuid4()),
                    project_id="project-costs",
                    task_id="task-costs",
                    run_id="run-2",
                    provider="openai",
                    model="codex",
                    auth_mode="subscription",
                    prompt_tokens=30,
                    completion_tokens=20,
                    estimated_cost=0.75,
                    metadata_json={},
                ),
                TokenUsageEvent(
                    usage_event_id=str(uuid.uuid4()),
                    project_id="project-costs",
                    task_id="task-costs",
                    run_id="run-3",
                    provider="anthropic",
                    model="claude",
                    auth_mode="subscription",
                    prompt_tokens=70,
                    completion_tokens=10,
                    estimated_cost=0.5,
                    metadata_json={},
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-costs/costs/summary", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-costs"
    assert body["total_prompt_tokens"] == 200
    assert body["total_completion_tokens"] == 80
    assert body["total_estimated_cost"] == 2.5
    assert body["providers"] == [
        {
            "provider": "anthropic",
            "total_prompt_tokens": 170,
            "total_completion_tokens": 60,
            "total_estimated_cost": 1.75,
        },
        {
            "provider": "openai",
            "total_prompt_tokens": 30,
            "total_completion_tokens": 20,
            "total_estimated_cost": 0.75,
        },
    ]
