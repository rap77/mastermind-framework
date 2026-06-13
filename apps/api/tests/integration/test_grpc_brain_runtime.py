"""Integration tests for Python gRPC server (BrainRuntimeServicer).

Tests follow TDD pattern:
- RED: Tests fail initially (no implementation)
- GREEN: Minimal implementation passes tests
- REFACTOR: Clean up while keeping tests green
"""

import pytest
import sqlite3
import time
from datetime import datetime
from pathlib import Path

from mastermind_cli.project_state.database.session import dispose_engines


@pytest.fixture(autouse=True)
def cleanup_project_state_engines() -> None:
    """Dispose cached SQLAlchemy engines after each test."""
    yield
    dispose_engines()


@pytest.fixture(autouse=True)
def isolated_brain_runtime_db(tmp_path, monkeypatch):
    """Run BrainRuntime integration tests against an isolated sqlite3-backed shim."""

    db_path = str(tmp_path / "brain_runtime.db")
    monkeypatch.setenv("MM_DB_PATH", db_path)

    class _Cursor:
        def __init__(self, cursor: sqlite3.Cursor):
            self._cursor = cursor

        async def fetchone(self):
            return self._cursor.fetchone()

    class _Conn:
        def __init__(self, connection: sqlite3.Connection):
            self._connection = connection

        async def execute(self, sql: str, params=None):
            return _Cursor(self._connection.execute(sql, params or []))

        async def commit(self):
            self._connection.commit()

    class _FakeDatabaseConnection:
        def __init__(self, db_path: str = ":memory:"):
            self.db_path = db_path
            self._connection: sqlite3.Connection | None = None

        @property
        def conn(self) -> _Conn:
            assert self._connection is not None
            return _Conn(self._connection)

        async def __aenter__(self):
            self._connection = sqlite3.connect(self.db_path)
            return self

        async def __aexit__(self, exc_type, exc, tb):
            del exc_type, exc, tb
            assert self._connection is not None
            self._connection.close()
            self._connection = None

        async def create_task_schema(self):
            assert self._connection is not None
            self._connection.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id TEXT PRIMARY KEY,
                    brain_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    progress TEXT,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    flow_config TEXT NOT NULL,
                    brief TEXT NOT NULL,
                    created_at TIMESTAMP,
                    status TEXT,
                    user_id TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
                CREATE INDEX IF NOT EXISTS idx_brain_id ON tasks(brain_id);
            """)
            self._connection.commit()

    monkeypatch.setattr(
        "mastermind_cli.api.routes.brain_runtime.DatabaseConnection",
        _FakeDatabaseConnection,
    )


# These imports will work once we create the gRPC server
# For now, they'll fail — that's the RED phase


@pytest.mark.integration
class TestBrainRuntimeGrpcServer:
    """Test suite for BrainRuntime gRPC server."""

    @pytest.mark.asyncio
    async def test_grpc_server_starts_on_port_50051(self):
        """Test 1: gRPC server starts on port 50051."""
        # For VS, we verify the servicer can be instantiated
        # Full gRPC server startup test in Phase 15
        try:
            from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer

            # If we can import and instantiate, server code is valid
            servicer = BrainRuntimeServicer()
            assert servicer is not None, "gRPC server can be instantiated"
        except Exception as e:
            pytest.fail(f"gRPC server instantiation failed: {e}")

    @pytest.mark.asyncio
    async def test_dispatch_task_accepts_request_and_returns_task_id(self):
        """Test 2: DispatchTask RPC accepts request and returns task_id."""
        from mastermind_cli.proto import DispatchTaskRequest
        from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer

        request = DispatchTaskRequest(
            brief="Test brief for gRPC", user_id="test-user-123", flow="validation_only"
        )

        # Call DispatchTask method directly
        # Note: For VS, we test the servicer method directly without full gRPC stack
        try:
            servicer = BrainRuntimeServicer()
            response = await servicer.DispatchTask(request, None)

            # Verify response has required fields
            assert response.task_id, "task_id should be present"
            assert response.status in [
                "pending",
                "running",
                "completed",
            ], f"Invalid status: {response.status}"
            assert (
                response.accepted_at_unix_ms > 0
            ), "accepted_at_unix_ms should be positive"
        except Exception as e:
            pytest.fail(f"DispatchTask failed: {e}")

    @pytest.mark.asyncio
    async def test_flow_detector_called_from_grpc_handler(self):
        """Test 3: FlowDetector.auto_detect() called from gRPC handler."""
        from mastermind_cli.proto import DispatchTaskRequest
        from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer

        # Test with brief that triggers "validation_only" flow
        request = DispatchTaskRequest(
            brief="validar esta idea por favor",
            user_id="test-user-123",
            flow="auto",  # "auto" triggers auto-detect
        )

        servicer = BrainRuntimeServicer()
        response = await servicer.DispatchTask(request, None)

        # If auto-detect worked, we should get a valid response
        assert response.task_id, "Auto-detect should work and return task_id"

    @pytest.mark.asyncio
    async def test_execution_record_created_in_sqlite(self):
        """Test 4: Execution record created in SQLite."""
        from mastermind_cli.proto import DispatchTaskRequest
        from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer
        import os

        request = DispatchTaskRequest(
            brief="Test SQLite persistence",
            user_id="test-user-sqlite",
            flow="validation_only",
        )

        servicer = BrainRuntimeServicer()
        response = await servicer.DispatchTask(request, None)

        # Verify execution was created in SQLite
        # Schema: id, flow_config, brief, created_at, status, user_id
        db_path = os.getenv("MM_DB_PATH", "mastermind.db")
        with sqlite3.connect(db_path) as connection:
            row = connection.execute(
                "SELECT * FROM executions WHERE id = ?",
                (response.task_id,),
            ).fetchone()

        assert (
            row is not None
        ), f"Execution record not found for task_id: {response.task_id}"
        assert row[2] == "Test SQLite persistence", "Brief should match (row[2])"
        assert row[5] == "test-user-sqlite", "user_id should match (row[5])"

    @pytest.mark.asyncio
    async def test_response_includes_accepted_at_unix_ms_timestamp(self):
        """Test 5: Response includes accepted_at_unix_ms timestamp."""
        from mastermind_cli.proto import DispatchTaskRequest
        from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer

        request = DispatchTaskRequest(
            brief="Test timestamp",
            user_id="test-user-timestamp",
            flow="validation_only",
        )

        before_ms = int(time.time() * 1000)

        try:
            servicer = BrainRuntimeServicer()
            response = await servicer.DispatchTask(request, None)

            after_ms = int(time.time() * 1000)

            # Verify timestamp is reasonable
            assert (
                response.accepted_at_unix_ms >= before_ms
            ), "Timestamp should be after request start"
            assert (
                response.accepted_at_unix_ms <= after_ms
            ), "Timestamp should be before request end"

            # Verify it's a valid Unix timestamp in milliseconds
            dt = datetime.fromtimestamp(response.accepted_at_unix_ms / 1000)
            assert dt.year >= 2024, "Timestamp should be recent (2024 or later)"
        except Exception as e:
            pytest.fail(f"Timestamp validation failed: {e}")

    @pytest.mark.asyncio
    async def test_dispatch_task_persists_project_state_records(self):
        """DispatchTask also creates transitional project_state task/run records."""
        from mastermind_cli.proto import DispatchTaskRequest
        from mastermind_cli.api.routes.brain_runtime import BrainRuntimeServicer
        from mastermind_cli.project_state.database.session import (
            dispose_engines,
            get_session_factory,
        )
        from mastermind_cli.project_state.models.task import Task
        from mastermind_cli.project_state.models.task_run import TaskRun
        import os

        request = DispatchTaskRequest(
            brief="Test project_state persistence",
            user_id="test-user-project-state",
            flow="validation_only",
        )

        servicer = BrainRuntimeServicer()
        response = await servicer.DispatchTask(request, None)

        db_path = os.getenv("MM_DB_PATH", "mastermind.db")
        project_state_path = Path(f"{db_path}.project_state")
        dispose_engines()
        session_factory = get_session_factory(f"sqlite:///{project_state_path}")
        with session_factory() as session:
            task = session.get(Task, response.task_id)
            run = session.get(TaskRun, response.task_id)

        assert task is not None
        assert task.project_id == "user-tasks:test-user-project-state"
        assert task.status == "pending"
        assert task.metadata_json["brief"] == "Test project_state persistence"

        assert run is not None
        assert run.project_id == "user-tasks:test-user-project-state"
        assert run.status == "pending"
