"""API tests for the project-state context projection endpoint."""

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
from mastermind_cli.project_state.models.decision import DecisionRecord
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
async def test_task_context_projection_returns_seeded_projection(
    tmp_path: Path,
) -> None:
    """Return a compact task context projection for a seeded task."""
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
                project_id="project-context",
                name="Project Context",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-context",
                project_id="project-context",
                title="Implement context projection",
                status="in_progress",
                priority="critical",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={
                    "blockers": ["awaiting schema review"],
                    "dependencies": ["task-overview", "task-decisions"],
                    "relevant_artifacts": ["SPEC.md", "PLAN.md"],
                },
                constraints={"must_use": ["postgres"]},
                completion_criteria={"tests": "passing"},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            Checkpoint(
                checkpoint_id="chk-context",
                project_id="project-context",
                task_id="task-context",
                run_id="run-context",
                context_summary={"slice": "context-projection"},
                resume_state={"step": 2},
                next_step_summary="Wire doctrine projection next",
                created_at=created_at,
            )
        )
        session.add(
            DecisionRecord(
                decision_id="dec-context",
                project_id="project-context",
                task_id="task-context",
                title="Use explicit projection endpoints",
                status="approved",
                rationale_markdown="Read-side projections deserve explicit routes.",
                metadata_json={"scope": "api"},
                created_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-context/tasks/task-context/context-projection",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-context"
    assert body["task_id"] == "task-context"
    assert body["objective"] == "Implement context projection"
    assert body["blockers"] == ["awaiting schema review"]
    assert body["dependencies"] == ["task-overview", "task-decisions"]
    assert body["relevant_artifacts"] == ["SPEC.md", "PLAN.md"]
    assert body["latest_checkpoint_id"] == "chk-context"
    assert body["next_step"] == "Wire doctrine projection next"
    assert body["critical_decisions"][0]["decision_id"] == "dec-context"
