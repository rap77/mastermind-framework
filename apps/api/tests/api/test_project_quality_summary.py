"""API tests for GET /api/projects/{id}/costs/quality-summary."""

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
        return db_path

    async def _override_project_state_db_url() -> str:
        return project_state_db_url

    app.dependency_overrides[get_db_path] = _override_db_path
    app.dependency_overrides[get_project_state_db_url] = _override_project_state_db_url
    return app


def _make_project(project_id: str) -> Project:
    return Project(
        project_id=project_id,
        name=f"Project {project_id}",
        status="active",
        adapter_id="default-adapter",
        metadata_json={},
    )


def _make_task(task_id: str, project_id: str) -> Task:
    return Task(
        task_id=task_id,
        project_id=project_id,
        title="Test task",
        status="in_progress",
        priority="normal",
        owner_type="agent",
        owner_id="brain-01",
        metadata_json={},
        constraints={},
        completion_criteria={},
    )


def _make_event(
    project_id: str,
    task_id: str,
    metadata: dict,
    estimated_cost: float = 1.0,
) -> TokenUsageEvent:
    return TokenUsageEvent(
        usage_event_id=str(uuid.uuid4()),
        project_id=project_id,
        task_id=task_id,
        run_id="run-1",
        provider="anthropic",
        model="claude-sonnet-4-6",
        auth_mode="api",
        prompt_tokens=100,
        completion_tokens=50,
        estimated_cost=estimated_cost,
        metadata_json=metadata,
    )


@pytest.mark.asyncio
async def test_quality_summary_returns_aggregated_signals(tmp_path: Path) -> None:
    """Return correct pass/fail counts and rates when events carry quality fields."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    with get_session_factory(database_url)() as session:
        session.add(_make_project("proj-quality"))
        session.add(_make_task("task-q", "proj-quality"))
        session.add_all(
            [
                _make_event(
                    "proj-quality",
                    "task-q",
                    {"review_pass": True, "verification_pass": True, "rework_count": 0},
                    estimated_cost=1.0,
                ),
                _make_event(
                    "proj-quality",
                    "task-q",
                    {
                        "review_pass": True,
                        "verification_pass": False,
                        "rework_count": 2,
                    },
                    estimated_cost=2.0,
                ),
                _make_event(
                    "proj-quality",
                    "task-q",
                    {
                        "review_pass": False,
                        "verification_pass": True,
                        "rework_count": 1,
                    },
                    estimated_cost=1.5,
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/proj-quality/costs/quality-summary",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "proj-quality"
    assert body["total_events"] == 3
    assert body["review_pass_count"] == 2
    assert body["review_fail_count"] == 1
    assert abs(body["review_pass_rate"] - 0.667) < 0.001
    assert body["verification_pass_count"] == 2
    assert body["verification_fail_count"] == 1
    assert abs(body["verification_pass_rate"] - 0.667) < 0.001
    assert body["avg_rework_count"] == 1.0
    assert abs(body["total_estimated_cost"] - 4.5) < 0.001
    # 4.5 total cost / 3 reviewed events
    assert body["cost_per_reviewed_event"] is not None


@pytest.mark.asyncio
async def test_quality_summary_empty_project_returns_zero_counts(
    tmp_path: Path,
) -> None:
    """Return zero aggregates when a project has no token usage events."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    with get_session_factory(database_url)() as session:
        session.add(_make_project("proj-empty"))
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/proj-empty/costs/quality-summary",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "proj-empty"
    assert body["total_events"] == 0
    assert body["review_pass_count"] == 0
    assert body["review_fail_count"] == 0
    assert body["review_pass_rate"] is None
    assert body["verification_pass_count"] == 0
    assert body["verification_fail_count"] == 0
    assert body["verification_pass_rate"] is None
    assert body["avg_rework_count"] is None
    assert body["total_estimated_cost"] == 0.0
    assert body["cost_per_reviewed_event"] is None


@pytest.mark.asyncio
async def test_quality_summary_events_without_quality_fields_not_counted(
    tmp_path: Path,
) -> None:
    """Events that omit quality fields do not inflate pass/fail counts."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    with get_session_factory(database_url)() as session:
        session.add(_make_project("proj-legacy"))
        session.add(_make_task("task-legacy", "proj-legacy"))
        # Two events without quality fields (legacy callers)
        session.add_all(
            [
                _make_event("proj-legacy", "task-legacy", {}, estimated_cost=0.5),
                _make_event("proj-legacy", "task-legacy", {}, estimated_cost=0.5),
                # One event with a review_pass only
                _make_event(
                    "proj-legacy",
                    "task-legacy",
                    {"review_pass": True},
                    estimated_cost=1.0,
                ),
            ]
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/proj-legacy/costs/quality-summary",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["total_events"] == 3
    # Only 1 event has a review_pass value
    assert body["review_pass_count"] == 1
    assert body["review_fail_count"] == 0
    assert body["review_pass_rate"] == 1.0
    # No events have verification_pass
    assert body["verification_pass_count"] == 0
    assert body["verification_pass_rate"] is None
    # No rework_count values
    assert body["avg_rework_count"] is None
    assert abs(body["total_estimated_cost"] - 2.0) < 0.001
    # cost_per_reviewed_event = 2.0 / 1 reviewed event
    assert body["cost_per_reviewed_event"] == 2.0


@pytest.mark.asyncio
async def test_quality_summary_returns_404_for_unknown_project(
    tmp_path: Path,
) -> None:
    """Return 404 when the project does not exist."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/nonexistent-project/costs/quality-summary",
            headers=auth_headers,
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_post_token_usage_persists_quality_fields(tmp_path: Path) -> None:
    """POST token-usage merges quality fields into metadata_json."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    with get_session_factory(database_url)() as session:
        session.add(_make_project("proj-write"))
        session.add(_make_task("task-write", "proj-write"))
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/projects/proj-write/tasks/task-write/token-usage",
            headers=auth_headers,
            json={
                "model": "claude-sonnet-4-6",
                "provider": "anthropic",
                "auth_mode": "api",
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "estimated_cost": 1.25,
                "agent_id": "brain-01",
                "review_pass": True,
                "verification_pass": False,
                "rework_count": 1,
            },
        )

    assert response.status_code == 201
    body = response.json()
    assert body["metadata"]["agent_id"] == "brain-01"
    assert body["metadata"]["review_pass"] is True
    assert body["metadata"]["verification_pass"] is False
    assert body["metadata"]["rework_count"] == 1
