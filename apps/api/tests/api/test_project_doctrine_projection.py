"""API tests for the project-state doctrine projection and write endpoints."""

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
async def test_task_doctrine_projection_returns_seeded_projection(
    tmp_path: Path,
) -> None:
    """Return a doctrine projection combining project and task doctrine metadata."""
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
                project_id="project-doctrine",
                name="Project Doctrine",
                status="active",
                adapter_id="default-adapter",
                metadata_json={
                    "doctrine": {
                        "methodology": "hybrid",
                        "methodology_reason": "critical runtime work",
                        "required_phases": ["spec", "implementation", "review"],
                        "architecture_constraints": [
                            "Keep core and adapter boundaries explicit"
                        ],
                        "quality_gates": ["API and service tests must pass"],
                    }
                },
            )
        )
        session.add(
            Task(
                task_id="task-doctrine",
                project_id="project-doctrine",
                title="Implement doctrine projection",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={
                    "doctrine": {
                        "mandatory_rules": [
                            {
                                "rule_id": "explicit-projection-route",
                                "summary": "Expose doctrine as a typed route",
                                "severity": "mandatory",
                                "check": "Endpoint returns doctrine projection schema",
                            }
                        ],
                        "recommended_rules": [
                            {
                                "rule_id": "projection-kept-compact",
                                "summary": "Keep doctrine payload compact",
                                "severity": "recommended",
                            }
                        ],
                        "exception_policy": {
                            "human_approval_required_for_overrides": True,
                            "pause_if_mandatory_rule_cannot_be_met": True,
                        },
                    }
                },
                constraints={},
                completion_criteria={},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get(
            "/api/projects/project-doctrine/tasks/task-doctrine/doctrine-projection",
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["project_id"] == "project-doctrine"
    assert body["task_id"] == "task-doctrine"
    assert body["methodology"]["active"] == "hybrid"
    assert body["methodology"]["required_phases"] == [
        "spec",
        "implementation",
        "review",
    ]
    assert body["mandatory_rules"][0]["rule_id"] == "explicit-projection-route"
    assert body["recommended_rules"][0]["rule_id"] == "projection-kept-compact"
    assert body["architecture_constraints"] == [
        "Keep core and adapter boundaries explicit"
    ]
    assert body["quality_gates"] == ["API and service tests must pass"]
    assert body["exception_policy"]["human_approval_required_for_overrides"] is True


@pytest.mark.asyncio
async def test_patch_project_doctrine_write_read_cycle(tmp_path: Path) -> None:
    """PATCH doctrine then GET projection to verify the write is reflected."""
    db_path = str(tmp_path / "test.db")
    database_url = f"sqlite:///{db_path}.project_state"
    dispose_engines()
    initialize_database(database_url)
    app = _build_test_app(db_path, database_url)
    auth_headers = {
        "Authorization": f"Bearer {create_access_token('test-user-id-002')}"
    }
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-doctrine-write",
                name="Project Doctrine Write",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-doctrine-write",
                project_id="project-doctrine-write",
                title="Task for doctrine write test",
                status="pending",
                priority="medium",
                owner_type="agent",
                owner_id="brain-01",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.commit()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        patch_response = await client.patch(
            "/api/projects/project-doctrine-write/doctrine",
            json={
                "methodology": "TDD",
                "methodology_reason": "reliability-critical path",
                "required_phases": ["spec", "implementation", "review"],
                "mandatory_rules": [
                    {
                        "rule_id": "write-tests-first",
                        "summary": "Tests must be written before implementation",
                        "severity": "mandatory",
                    }
                ],
                "architecture_constraints": ["No direct DB access from routes"],
                "quality_gates": ["All tests must pass before merge"],
            },
            headers=auth_headers,
        )
        assert patch_response.status_code == 200, patch_response.text
        patch_body = patch_response.json()
        assert patch_body["project_id"] == "project-doctrine-write"
        assert patch_body["methodology"] == "TDD"
        assert patch_body["methodology_reason"] == "reliability-critical path"
        assert patch_body["required_phases"] == ["spec", "implementation", "review"]
        assert patch_body["mandatory_rules"][0]["rule_id"] == "write-tests-first"
        assert patch_body["architecture_constraints"] == [
            "No direct DB access from routes"
        ]
        assert patch_body["quality_gates"] == ["All tests must pass before merge"]

        projection_response = await client.get(
            "/api/projects/project-doctrine-write/tasks/task-doctrine-write/doctrine-projection",
            headers=auth_headers,
        )
        assert projection_response.status_code == 200, projection_response.text
        proj_body = projection_response.json()
        assert proj_body["methodology"]["active"] == "TDD"
        assert proj_body["methodology"]["reason"] == "reliability-critical path"
        assert proj_body["mandatory_rules"][0]["rule_id"] == "write-tests-first"
        assert proj_body["architecture_constraints"] == [
            "No direct DB access from routes"
        ]
