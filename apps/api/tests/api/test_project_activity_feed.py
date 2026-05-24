"""API tests for the project-state activity feed and realtime events endpoints."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path
import uuid

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
from mastermind_cli.project_state.models.decision import DecisionRecord
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
async def test_project_activity_feed_returns_recent_mixed_events(
    tmp_path: Path,
) -> None:
    """Return mixed activity feed events ordered by recency."""
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
                project_id="project-feed",
                name="Project Feed",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-feed",
                project_id="project-feed",
                title="Implement activity feed",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now - timedelta(minutes=4),
                updated_at=now - timedelta(minutes=1),
            )
        )
        session.add(
            Checkpoint(
                checkpoint_id="chk-feed",
                project_id="project-feed",
                task_id="task-feed",
                run_id="run-feed",
                context_summary={"stage": "implementation"},
                resume_state={"cursor": 1},
                next_step_summary="Resume endpoint work",
                created_at=now - timedelta(minutes=2),
            )
        )
        session.add(
            DecisionRecord(
                decision_id="dec-feed",
                project_id="project-feed",
                task_id="task-feed",
                title="Adopt hybrid scheduling",
                status="approved",
                rationale_markdown="Keep hybrid as default.",
                metadata_json={},
                created_at=now - timedelta(minutes=3),
            )
        )
        session.add(
            TokenUsageEvent(
                usage_event_id=str(uuid.uuid4()),
                project_id="project-feed",
                task_id="task-feed",
                run_id="run-feed",
                provider="anthropic",
                model="claude",
                auth_mode="subscription",
                prompt_tokens=50,
                completion_tokens=10,
                estimated_cost=0.4,
                metadata_json={},
                created_at=now,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-feed/activity?limit=4", headers=auth_headers
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-feed"
    assert [event["event_type"] for event in body["events"]] == [
        "token_usage_recorded",
        "task_updated",
        "checkpoint_created",
        "decision_recorded",
    ]
    assert body["events"][0]["metadata"]["provider"] == "anthropic"
    assert body["events"][1]["task_id"] == "task-feed"


@pytest.mark.asyncio
async def test_project_events_sse_returns_stream_headers(tmp_path: Path) -> None:
    """SSE /events endpoint responds with text/event-stream content type."""
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
                project_id="project-sse",
                name="Project SSE",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-sse",
                project_id="project-sse",
                title="SSE test task",
                status="in_progress",
                priority="normal",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        # Use stream=True so we can inspect headers without waiting for the stream to close.
        async with client.stream(
            "GET",
            "/api/projects/project-sse/events?once=true",
            headers=auth_headers,
        ) as response:
            assert response.status_code == 200
            assert "text/event-stream" in response.headers.get("content-type", "")
            # Read the initial batch of events (the stream starts with seeded activity).
            raw = await response.aread()

    # The SSE frame format requires "data:" lines.
    decoded = raw.decode()
    assert "data:" in decoded


@pytest.mark.asyncio
async def test_project_events_sse_returns_404_for_missing_project(
    tmp_path: Path,
) -> None:
    """SSE /events endpoint returns 404 for a non-existent project."""
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
            "/api/projects/nonexistent-project/events",
            headers=auth_headers,
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_project_events_sse_emits_typed_event_payloads(tmp_path: Path) -> None:
    """SSE events carry the ProjectStateRealtimeEvent typed contract fields."""
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
                project_id="project-sse-typed",
                name="Project SSE Typed",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-sse-typed",
                project_id="project-sse-typed",
                title="Typed SSE task",
                status="done",
                priority="high",
                owner_type="agent",
                owner_id="brain-05",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    import json as _json

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        async with client.stream(
            "GET",
            "/api/projects/project-sse-typed/events?once=true",
            headers=auth_headers,
        ) as response:
            assert response.status_code == 200
            raw = await response.aread()

    decoded = raw.decode()
    # Extract JSON payloads from SSE data: lines.
    payloads = []
    for line in decoded.splitlines():
        if line.startswith("data:"):
            payload_str = line[len("data:") :].strip()
            if payload_str and payload_str != "{}":
                payloads.append(_json.loads(payload_str))

    assert len(payloads) >= 1
    first = payloads[0]
    # Verify the typed contract fields are present.
    assert "event_type" in first
    assert "project_id" in first
    assert "entity_id" in first
    assert "occurred_at" in first
    assert "summary" in first
    assert "metadata" in first
    assert first["project_id"] == "project-sse-typed"
