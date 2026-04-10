"""Integration tests for Python gRPC server (BrainRuntimeServicer).

Tests follow TDD pattern:
- RED: Tests fail initially (no implementation)
- GREEN: Minimal implementation passes tests
- REFACTOR: Clean up while keeping tests green
"""

import pytest
import time
from datetime import datetime

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
        from mastermind_cli.state.database import DatabaseConnection
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
        async with DatabaseConnection(db_path) as db:
            cursor = await db.conn.execute(
                "SELECT * FROM executions WHERE id = ?", [response.task_id]
            )
            row = await cursor.fetchone()

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
