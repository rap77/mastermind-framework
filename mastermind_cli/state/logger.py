"""
Execution Logger - Log brain executions to SQLite.

This module provides logging for brain executions with:
- Input tracking (brief, context)
- Output tracking (results as JSON)
- Performance metrics (duration)
- Query interface for historical logs

Design Principles:
- Async-friendly (uses aiosqlite)
- Schema-upgradeable (JSONB ready for PostgreSQL)
- Minimal overhead (optional logging)
"""

from __future__ import annotations

import contextlib
import json
import time
import uuid
from datetime import datetime, timezone
from typing import Any, AsyncIterator

from pydantic import BaseModel, Field

from mastermind_cli.types.interfaces import Brief, BrainOutput


# =============================================================================
# CUSTOM JSON ENCODER
# =============================================================================


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


# =============================================================================
# MODELS
# =============================================================================


class BrainExecutionLog(BaseModel):
    """
    Log entry for a single brain execution.

    Stored in SQLite as JSON (upgrade path to PostgreSQL + JSONB).
    """

    execution_id: str = Field(..., description="Unique execution ID")
    brain_id: str = Field(..., description="Brain that was executed")
    brief: str = Field(..., description="User's brief (problem statement)")
    input_context: dict[str, Any] = Field(
        default_factory=dict, description="Additional input context"
    )
    output: dict[str, Any] = Field(
        default_factory=dict, description="Brain output as JSON"
    )
    status: str = Field(..., description="Execution status: success, error, timeout")
    error_message: str | None = Field(None, description="Error message if status=error")
    duration_ms: int = Field(..., description="Execution duration in milliseconds")
    timestamp: str = Field(..., description="ISO timestamp of execution")
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Additional metadata (user, session, etc.)"
    )


class ExecutionQuery(BaseModel):
    """Query parameters for filtering execution logs."""

    brain_id: str | None = None
    status: str | None = None
    limit: int = Field(default=100, ge=1, le=1000)
    offset: int = Field(default=0, ge=0)
    sort_by: str = Field(
        default="timestamp", pattern="^(timestamp|duration_ms|brain_id)$"
    )
    sort_order: str = Field(default="DESC", pattern="^(ASC|DESC)$")


# =============================================================================
# LOGGER
# =============================================================================


class ExecutionLogger:
    """
    Logger for brain executions.

    Logs to SQLite database with async support.
    Can be disabled for performance-critical paths.
    """

    def __init__(self, db_path: str = ":memory:", enabled: bool = True) -> None:
        """
        Initialize execution logger.

        Args:
            db_path: Path to SQLite database file
            enabled: Whether logging is enabled (can be disabled for perf)
        """
        self.db_path = db_path
        self.enabled = enabled
        self._conn: Any = None

    async def _get_connection(self) -> Any:
        """Get or create database connection."""
        if self._conn is None:
            import aiosqlite

            self._conn = await aiosqlite.connect(self.db_path)
            await self._enable_wal_mode()
            await self._create_schema()
        return self._conn

    async def _enable_wal_mode(self) -> None:
        """Enable WAL mode for better concurrency."""
        assert self._conn is not None
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.commit()

    async def _create_schema(self) -> None:
        """Create brain_executions table and indexes."""
        assert self._conn is not None
        await self._conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_executions (
                id TEXT PRIMARY KEY,
                execution_id TEXT NOT NULL,
                brain_id TEXT NOT NULL,
                brief TEXT NOT NULL,
                input_context TEXT,
                output TEXT,
                status TEXT NOT NULL,
                error_message TEXT,
                duration_ms INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                metadata TEXT
            )
        """)

        # Create indexes for common queries
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_executions_brain_id "
            "ON brain_executions(brain_id)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_executions_status "
            "ON brain_executions(status)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_executions_timestamp "
            "ON brain_executions(timestamp DESC)"
        )
        await self._conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_executions_execution_id "
            "ON brain_executions(execution_id)"
        )
        await self._conn.commit()

    async def log_execution(
        self,
        execution_id: str,
        brain_id: str,
        brief: Brief,
        output: BrainOutput | None,
        status: str,
        error_message: str | None = None,
        duration_ms: int = 0,
        metadata: dict[str, Any] | None = None,
    ) -> str:
        """
        Log a brain execution.

        Args:
            execution_id: Unique execution ID
            brain_id: Brain ID that was executed
            brief: User's brief
            output: Brain output (None if failed)
            status: Execution status (success, error, timeout)
            error_message: Error message if status=error
            duration_ms: Execution duration in milliseconds
            metadata: Additional metadata

        Returns:
            Log entry ID (UUID)
        """
        if not self.enabled:
            return ""

        conn = await self._get_connection()

        log_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Serialize to JSON (with datetime encoder)
        input_context_json = json.dumps(
            {
                "context": brief.context,
                "constraints": brief.constraints,
                "target_audience": brief.target_audience,
            },
            cls=DateTimeEncoder,
        )
        output_json = json.dumps(
            output.model_dump() if output else {}, cls=DateTimeEncoder
        )
        metadata_json = json.dumps(metadata or {}, cls=DateTimeEncoder)

        await conn.execute(
            """INSERT INTO brain_executions
               (id, execution_id, brain_id, brief, input_context, output,
                status, error_message, duration_ms, timestamp, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                log_id,
                execution_id,
                brain_id,
                brief.problem_statement,
                input_context_json,
                output_json,
                status,
                error_message,
                duration_ms,
                timestamp,
                metadata_json,
            ),
        )
        await conn.commit()

        return log_id

    async def query_executions(self, query: ExecutionQuery) -> list[BrainExecutionLog]:
        """
        Query execution logs.

        Args:
            query: Query parameters

        Returns:
            List of execution log entries
        """
        if not self.enabled:
            return []

        conn = await self._get_connection()

        # Build query
        sql = "SELECT * FROM brain_executions WHERE 1=1"
        params = []

        if query.brain_id:
            sql += " AND brain_id = ?"
            params.append(query.brain_id)

        if query.status:
            sql += " AND status = ?"
            params.append(query.status)

        # Sorting
        sql += f" ORDER BY {query.sort_by} {query.sort_order}"

        # Pagination
        sql += " LIMIT ? OFFSET ?"
        params.extend([str(query.limit), str(query.offset)])

        cursor = await conn.execute(sql, params)
        rows = await cursor.fetchall()

        # Parse results
        # Row order: id, execution_id, brain_id, brief, input_context,
        #             output, status, error_message, duration_ms, timestamp, metadata
        logs = []
        for row in rows:
            logs.append(
                BrainExecutionLog(
                    execution_id=row[1],
                    brain_id=row[2],
                    brief=row[3],
                    input_context=json.loads(row[4]) if row[4] else {},
                    output=json.loads(row[5]) if row[5] else {},
                    status=row[6],
                    error_message=row[7],
                    duration_ms=row[8],
                    timestamp=row[9],
                    metadata=json.loads(row[10]) if row[10] else {},
                )
            )

        return logs

    async def get_execution_by_id(self, execution_id: str) -> BrainExecutionLog | None:
        """
        Get execution log by execution ID.

        Args:
            execution_id: Unique execution ID

        Returns:
            Execution log entry or None
        """
        if not self.enabled:
            return None

        conn = await self._get_connection()

        cursor = await conn.execute(
            "SELECT * FROM brain_executions WHERE execution_id = ?", (execution_id,)
        )
        row = await cursor.fetchone()

        if row:
            return BrainExecutionLog(
                execution_id=row[1],
                brain_id=row[2],
                brief=row[3],
                input_context=json.loads(row[4]) if row[4] else {},
                output=json.loads(row[5]) if row[5] else {},
                status=row[6],
                error_message=row[7],
                duration_ms=row[8],
                timestamp=row[9],
                metadata=json.loads(row[10]) if row[10] else {},
            )
        return None

    async def get_statistics(self) -> dict[str, Any]:
        """
        Get execution statistics.

        Returns:
            Dict with stats: total executions, success rate, avg duration
        """
        if not self.enabled:
            return {}

        conn = await self._get_connection()

        # Total executions
        cursor = await conn.execute("SELECT COUNT(*) FROM brain_executions")
        total = (await cursor.fetchone())[0]

        # Success rate
        cursor = await conn.execute(
            "SELECT COUNT(*) FROM brain_executions WHERE status = 'success'"
        )
        success_count = (await cursor.fetchone())[0]
        success_rate = success_count / total if total > 0 else 0

        # Average duration
        cursor = await conn.execute(
            "SELECT AVG(duration_ms) FROM brain_executions WHERE status = 'success'"
        )
        avg_duration = await cursor.fetchone()

        return {
            "total_executions": total,
            "success_count": success_count,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration[0]
            if avg_duration and avg_duration[0]
            else 0,
        }

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None


# =============================================================================
# CONTEXT MANAGER FOR TIMING
# =============================================================================


@contextlib.asynccontextmanager
async def log_brain_execution(
    logger: ExecutionLogger,
    execution_id: str,
    brain_id: str,
    brief: Brief,
    metadata: dict[str, Any] | None = None,
) -> AsyncIterator[Any]:
    """
    Context manager for timing and logging brain execution.

    Usage:
        async with log_brain_execution(logger, exec_id, brain_id, brief) as timer:
            output = await brain_function(...)
            # Log success on exit
            timer.complete(output)

    Args:
        logger: ExecutionLogger instance
        execution_id: Unique execution ID
        brain_id: Brain ID being executed
        brief: User's brief
        metadata: Optional metadata
    """
    start_time = time.time()
    output: BrainOutput | None = None
    error_message: str | None = None

    class Timer:
        output: BrainOutput | None
        error_message: str | None

        def __init__(
            self,
            logger: Any,
            execution_id: str,
            brain_id: str,
            brief: Any,
            metadata: dict[str, Any] | None,
            start: float,
        ) -> None:
            self.logger = logger
            self.execution_id = execution_id
            self.brain_id = brain_id
            self.brief = brief
            self.metadata = metadata
            self.start = start
            self.output = None
            self.error_message = None

        def complete(self, result: BrainOutput) -> None:
            """Mark execution as successful with output."""
            self.output = result

        def fail(self, error: str) -> None:
            """Mark execution as failed with error message."""
            self.error_message = error

        async def __aenter__(self) -> Any:
            return self

        async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
            duration_ms = int((time.time() - self.start) * 1000)

            if exc_type is not None:
                # Exception occurred
                status = "error"
                error_msg = str(exc_val)
            elif self.error_message:
                # Explicit failure
                status = "error"
                error_msg = self.error_message
            else:
                status = "success"
                error_msg = None

            await self.logger.log_execution(
                execution_id=self.execution_id,
                brain_id=self.brain_id,
                brief=self.brief,
                output=self.output,
                status=status,
                error_message=error_msg,
                duration_ms=duration_ms,
                metadata=self.metadata,
            )

    timer = Timer(logger, execution_id, brain_id, brief, metadata, start_time)
    try:
        yield timer
    finally:
        duration_ms = int((time.time() - start_time) * 1000)

        if error_message:
            status = "error"
        elif output is None:
            status = "error"
            error_message = "No output produced"
        else:
            status = "success"

        await logger.log_execution(
            execution_id=execution_id,
            brain_id=brain_id,
            brief=brief,
            output=output,
            status=status,
            error_message=error_message,
            duration_ms=duration_ms,
            metadata=metadata,
        )
