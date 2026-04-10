"""gRPC server for Brain Runtime service.

This module implements the BrainRuntime gRPC service that accepts task
dispatch requests from the Rust Control Plane and forwards them to the
Python orchestration system.

Phase 13-03 Task 1: Python gRPC server (BrainRuntimeServicer)
"""

import time
import uuid
from typing import Optional

from mastermind_cli.orchestrator.flow_detector import FlowDetector
from mastermind_cli.proto import DispatchTaskRequest, DispatchTaskResponse
from mastermind_cli.state.database import DatabaseConnection


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
        db_path = "mastermind.db"  # TODO: Use MM_DB_PATH env var
        async with DatabaseConnection(db_path) as db:
            # Ensure schema exists
            await db.create_task_schema()

            await db.conn.execute(
                """INSERT INTO executions (id, brief, flow_config, user_id, status, created_at)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                [task_id, brief, flow, user_id, "pending", accepted_at_ms / 1000],
            )
            await db.conn.commit()

        # Return response
        # Note: In VS, we return "pending" immediately
        # Full orchestration happens in background in Phase 15
        return DispatchTaskResponse(
            task_id=task_id,
            status="pending",
            accepted_at_unix_ms=accepted_at_ms,
        )
