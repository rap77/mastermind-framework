"""Event emitter for activity_log (brain operations)."""

import json
import uuid
from datetime import datetime, timezone
from typing import Any, Dict

import asyncpg


class EventEmitter:
    """Emits brain operation events to activity_log table."""

    def __init__(self, db_conn: asyncpg.Connection | None = None):
        """Initialize event emitter.

        Args:
            db_conn: Optional asyncpg connection (creates new if None)
        """
        self.db_conn = db_conn
        self._pool: asyncpg.Pool | None = None

    async def _get_pool(self) -> asyncpg.Pool:
        """Get or create connection pool."""
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                host="localhost",
                port=5433,
                user="postgres",
                password="devpassword",
                database="mastermind",
                min_size=1,
                max_size=5,
            )
        return self._pool

    async def _execute_query(self, query: str, *args: Any) -> None:
        """Execute query with existing connection or pool."""
        if self.db_conn:
            await self.db_conn.execute(query, *args)
        else:
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                await conn.execute(query, *args)

    async def emit_brain_started(
        self,
        brain_id: str,
        session_id: str | uuid.UUID,
        brief: str,
        flow_config: Dict[str, Any],
    ) -> None:
        """Emit brain_started event.

        Args:
            brain_id: Brain identifier (e.g., "brain-01")
            session_id: Unique session identifier
            brief: User's brief text
            flow_config: Flow configuration dict
        """
        payload = {
            "session_id": str(session_id),
            "brief": brief,
            "flow_config": flow_config,
        }

        query = """
            INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """

        await self._execute_query(
            query,
            uuid.uuid4(),
            brain_id,
            "brain_started",
            json.dumps(payload),
            datetime.now(timezone.utc),
        )

    async def emit_brain_completed(
        self,
        brain_id: str,
        session_id: str | uuid.UUID,
        duration_ms: int,
        result: Dict[str, Any],
    ) -> None:
        """Emit brain_completed event.

        Args:
            brain_id: Brain identifier
            session_id: Unique session identifier
            duration_ms: Execution duration in milliseconds
            result: Brain output result
        """
        payload = {
            "session_id": str(session_id),
            "duration_ms": duration_ms,
            "result": result,
        }

        query = """
            INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """

        await self._execute_query(
            query,
            uuid.uuid4(),
            brain_id,
            "brain_completed",
            json.dumps(payload),
            datetime.now(timezone.utc),
        )

    async def emit_brain_failed(
        self,
        brain_id: str,
        session_id: str | uuid.UUID,
        error: str,
        stage: str,
    ) -> None:
        """Emit brain_failed event.

        Args:
            brain_id: Brain identifier
            session_id: Unique session identifier
            error: Error message
            stage: Execution stage (e.g., "validation", "execution", "post-processing")
        """
        payload = {
            "session_id": str(session_id),
            "error": error,
            "stage": stage,
        }

        query = """
            INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """

        await self._execute_query(
            query,
            uuid.uuid4(),
            brain_id,
            "brain_failed",
            json.dumps(payload),
            datetime.now(timezone.utc),
        )

    async def emit_brain_routed(
        self,
        brain_id: str,
        session_id: str | uuid.UUID,
        from_brain: str,
        to_brain: str,
        reason: str,
    ) -> None:
        """Emit brain_routed event.

        Args:
            brain_id: Current brain identifier
            session_id: Unique session identifier
            from_brain: Source brain
            to_brain: Destination brain
            reason: Routing reason
        """
        payload = {
            "session_id": str(session_id),
            "from_brain": from_brain,
            "to_brain": to_brain,
            "reason": reason,
        }

        query = """
            INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
            VALUES ($1, $2, $3, $4, $5)
        """

        await self._execute_query(
            query,
            uuid.uuid4(),
            brain_id,
            "brain_routed",
            json.dumps(payload),
            datetime.now(timezone.utc),
        )

    async def close(self) -> None:
        """Close connection pool if created."""
        if self._pool:
            await self._pool.close()
            self._pool = None
