"""gRPC server for Brain Runtime service.

This module implements the BrainRuntime gRPC service that accepts task
dispatch requests from the Rust Control Plane and forwards them to the
Python orchestration system.

Phase 13-03 Task 1: Python gRPC server (BrainRuntimeServicer)
"""

import time
import uuid
from datetime import datetime, timezone
from typing import Optional

from mastermind_cli.orchestrator.flow_detector import FlowDetector
from mastermind_cli.project_state.database.session import (
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from mastermind_cli.proto import DispatchTaskRequest, DispatchTaskResponse
from mastermind_cli.state.database import DatabaseConnection


def _project_state_db_url_from_path(db_path: str) -> str:
    """Return the project_state database URL associated with the legacy DB path."""
    if db_path == ":memory:":
        return "sqlite:///:memory:"
    return f"sqlite:///{db_path}.project_state"


def _user_task_project_id(user_id: str) -> str:
    """Return the transitional user-scoped project ID for legacy-dispatched tasks."""
    return f"user-tasks:{user_id}"


def _persist_project_state_dispatch(
    *,
    database_url: str,
    task_id: str,
    user_id: str,
    brief: str,
    flow: str,
    accepted_at_ms: int,
) -> None:
    """Persist transitional project_state records for a dispatched task."""
    initialize_database(database_url)
    project_id = _user_task_project_id(user_id)
    session_factory = get_session_factory(database_url)
    accepted_at = datetime.fromtimestamp(accepted_at_ms / 1000, tz=timezone.utc)
    with session_factory() as session:
        project = session.get(Project, project_id)
        if project is None:
            session.add(
                Project(
                    project_id=project_id,
                    name="User task workspace",
                    status="active",
                    adapter_id="legacy-tasks",
                    metadata_json={"user_id": user_id},
                    created_at=accepted_at,
                    updated_at=accepted_at,
                )
            )

        session.add(
            Task(
                task_id=task_id,
                project_id=project_id,
                title=brief[:500],
                status="pending",
                priority="normal",
                owner_type="user",
                owner_id=user_id,
                metadata_json={
                    "brief": brief,
                    "flow_config": flow,
                    "user_id": user_id,
                },
                constraints={},
                completion_criteria={},
                created_at=accepted_at,
                updated_at=accepted_at,
            )
        )
        session.add(
            TaskRun(
                run_id=task_id,
                project_id=project_id,
                task_id=task_id,
                actor_type="user",
                actor_id=user_id,
                status="pending",
                started_at=accepted_at,
                ended_at=None,
                metadata_json={"legacy_execution_id": task_id},
            )
        )
        session.commit()


class BrainRuntimeServicer:
    """gRPC servicer for BrainRuntime service.

    Handles DispatchTask RPC calls from the Rust Control Plane.
    Reuses existing Python orchestration (FlowDetector, task_runner).
    """

    def __init__(self) -> None:
        """Initialize the servicer."""
        self.flow_detector = FlowDetector()

    async def DispatchTask(
        self,
        request: DispatchTaskRequest,
        stream: Optional[object],
    ) -> DispatchTaskResponse:
        """Dispatch task to brain orchestration system.

        Args:
            request: DispatchTaskRequest with brief, user_id, flow
            stream: gRPC stream context (unused in simple case)

        Returns:
            DispatchTaskResponse with task_id, status, accepted_at_unix_ms
        """
        # Generate task ID and timestamp
        task_id = str(uuid.uuid4())
        accepted_at_ms = int(time.time() * 1000)

        # Auto-detect flow from brief if not provided
        brief = request.brief
        user_id = request.user_id
        flow = request.flow if request.flow else self.flow_detector.detect(brief)

        # Create execution record in SQLite
        # Note: In VS, we simplify to synchronous insert
        # Full async BackgroundTask execution comes in Phase 15
        import os

        db_path = os.getenv("MM_DB_PATH", "mastermind.db")
        project_state_db_url = _project_state_db_url_from_path(db_path)

        # Ensure directory exists for relative paths
        if not os.path.isabs(db_path):
            db_dir = os.path.dirname(db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)

        async with DatabaseConnection(db_path) as db:
            # Ensure schema exists
            await db.create_task_schema()

            await db.conn.execute(
                """INSERT INTO executions (id, brief, flow_config, user_id, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [task_id, brief, flow, user_id, "pending", accepted_at_ms / 1000],
            )
            await db.conn.commit()

        _persist_project_state_dispatch(
            database_url=project_state_db_url,
            task_id=task_id,
            user_id=user_id,
            brief=brief,
            flow=flow,
            accepted_at_ms=accepted_at_ms,
        )

        # Return response
        # Note: In VS, we return "pending" immediately
        # Full orchestration happens in background in Phase 15
        return DispatchTaskResponse(
            task_id=task_id,
            status="pending",
            accepted_at_unix_ms=accepted_at_ms,
        )
