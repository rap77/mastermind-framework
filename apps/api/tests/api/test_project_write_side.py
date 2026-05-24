"""API tests for minimal project_state write-side endpoints."""

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
async def test_create_project_task_checkpoint_persists_record(tmp_path: Path) -> None:
    """Create a new checkpoint through the project_state API."""
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
                project_id="project-checkpoint",
                name="Project Checkpoint",
                status="active",
                adapter_id="adapter-write",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-checkpoint",
                project_id="project-checkpoint",
                title="Checkpoint task",
                status="in_progress",
                priority="high",
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

    payload = {
        "run_id": "run-checkpoint",
        "context_summary": {"stage": "review"},
        "resume_state": {"cursor": 9},
        "next_step_summary": "Resume from the review branch.",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/projects/project-checkpoint/tasks/task-checkpoint/checkpoints",
            headers=auth_headers,
            json=payload,
        )

    assert response.status_code == 201
    body = response.json()
    assert body["task_id"] == "task-checkpoint"
    assert body["run_id"] == "run-checkpoint"
    assert body["context_summary"] == {"stage": "review"}


@pytest.mark.asyncio
async def test_create_project_decision_persists_record(tmp_path: Path) -> None:
    """Create a new decision through the project_state API."""
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
                project_id="project-decision-write",
                name="Project Decision Write",
                status="active",
                adapter_id="adapter-write",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-decision-write",
                project_id="project-decision-write",
                title="Decision write task",
                status="in_progress",
                priority="high",
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

    payload = {
        "task_id": "task-decision-write",
        "title": "Approve project state write-side",
        "status": "approved",
        "rationale_markdown": "Checkpoint and decision creation are needed for the MVP.",
        "metadata": {"brain": "backend"},
    }

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post(
            "/api/projects/project-decision-write/decisions",
            headers=auth_headers,
            json=payload,
        )

    assert response.status_code == 201
    body = response.json()
    assert body["task_id"] == "task-decision-write"
    assert body["title"] == "Approve project state write-side"
    assert body["metadata"]["brain"] == "backend"
    assert body["metadata"]["recorded_by"] == "test-user-id-001"


@pytest.mark.asyncio
async def test_update_task_status_persists_change(tmp_path: Path) -> None:
    """PATCH task status through the project_state API updates the task record."""
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
                project_id="project-status-update",
                name="Project Status Update",
                status="active",
                adapter_id="adapter-write",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-status-update",
                project_id="project-status-update",
                title="Status update task",
                status="pending",
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

    payload = {"status": "in_progress", "reason": "Starting execution now"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(
            "/api/projects/project-status-update/tasks/task-status-update/status",
            headers=auth_headers,
            json=payload,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["task_id"] == "task-status-update"
    assert body["status"] == "in_progress"
    assert body["metadata"]["status_reason"] == "Starting execution now"
    assert body["metadata"]["status_updated_by"] == "test-user-id-001"


@pytest.mark.asyncio
async def test_update_task_status_rejects_unknown_project(tmp_path: Path) -> None:
    """PATCH task status returns 404 for unknown project."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-001')}"
    }

    payload = {"status": "done"}

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.patch(
            "/api/projects/no-such-project/tasks/no-such-task/status",
            headers=auth_headers,
            json=payload,
        )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_checkpoint_write_appears_in_activity_feed(tmp_path: Path) -> None:
    """Creating a checkpoint produces a native audit event visible in the activity feed."""
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
                project_id="project-audit-chk",
                name="Project Audit Checkpoint",
                status="active",
                adapter_id="adapter-audit",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-audit-chk",
                project_id="project-audit-chk",
                title="Audit checkpoint task",
                status="in_progress",
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

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        write_response = await client.post(
            "/api/projects/project-audit-chk/tasks/task-audit-chk/checkpoints",
            headers=auth_headers,
            json={
                "run_id": "run-audit",
                "context_summary": {"stage": "audit"},
                "resume_state": {},
                "next_step_summary": "Verify audit trail via activity feed.",
            },
        )
        assert write_response.status_code == 201

        feed_response = await client.get(
            "/api/projects/project-audit-chk/activity?limit=10",
            headers=auth_headers,
        )

    assert feed_response.status_code == 200
    body = feed_response.json()
    event_types = [e["event_type"] for e in body["events"]]
    assert "checkpoint_created" in event_types


@pytest.mark.asyncio
async def test_decision_write_appears_in_activity_feed(tmp_path: Path) -> None:
    """Creating a decision produces a native audit event visible in the activity feed."""
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
                project_id="project-audit-dec",
                name="Project Audit Decision",
                status="active",
                adapter_id="adapter-audit",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        write_response = await client.post(
            "/api/projects/project-audit-dec/decisions",
            headers=auth_headers,
            json={
                "title": "Audit trail via native events",
                "status": "approved",
                "rationale_markdown": "project_state decisions are the native audit record.",
                "metadata": {},
            },
        )
        assert write_response.status_code == 201

        feed_response = await client.get(
            "/api/projects/project-audit-dec/activity?limit=10",
            headers=auth_headers,
        )

    assert feed_response.status_code == 200
    body = feed_response.json()
    event_types = [e["event_type"] for e in body["events"]]
    assert "decision_recorded" in event_types


@pytest.mark.asyncio
async def test_task_status_update_appears_in_activity_feed(tmp_path: Path) -> None:
    """Updating task status produces a native audit event visible in the activity feed."""
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
                project_id="project-audit-status",
                name="Project Audit Status",
                status="active",
                adapter_id="adapter-audit",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-audit-status",
                project_id="project-audit-status",
                title="Audit status task",
                status="pending",
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
        write_response = await client.patch(
            "/api/projects/project-audit-status/tasks/task-audit-status/status",
            headers=auth_headers,
            json={"status": "done", "reason": "Completed for audit test."},
        )
        assert write_response.status_code == 200

        feed_response = await client.get(
            "/api/projects/project-audit-status/activity?limit=10",
            headers=auth_headers,
        )

    assert feed_response.status_code == 200
    body = feed_response.json()
    event_types = [e["event_type"] for e in body["events"]]
    assert "task_updated" in event_types
    # Confirm the updated status is visible in the event metadata.
    task_event = next(e for e in body["events"] if e["event_type"] == "task_updated")
    assert task_event["metadata"]["status"] == "done"
