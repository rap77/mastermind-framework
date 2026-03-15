"""
Experience logger for full-fidelity execution logging with PII redaction.

This module provides async logger for experience records with automatic PII redaction
before persistence to SQLite database.
"""

from .models import ExperienceRecord
from .redaction import redact_for_storage
from mastermind_cli.state.database import DatabaseConnection
from typing import List, Optional, Dict, Any
import aiosqlite
import json


# Whitelist of allowed metadata keys for search_by_metadata (prevents SQL injection)
ALLOWED_METADATA_KEYS = {
    "quality_score",
    "user_id",
    "session_id",
    "brain_version",
    "model_version",
    "prompt_version",
    "test_id",
    "trace_id",
    "category",
    "priority",
    "tags",
}


class ExperienceLogger:
    """Async logger for experience records with PII redaction.

    This logger provides full-fidelity execution logging with:
    - Automatic PII redaction before storage
    - Async operations for performance
    - JSONB metadata queries
    - Brain-specific record retrieval
    """

    def __init__(self, db: DatabaseConnection):
        """Initialize experience logger.

        Args:
            db: DatabaseConnection instance (must be connected)
        """
        self.db = db

    async def log_execution(
        self,
        brain_id: str,
        input_json: Dict[str, Any],
        output_json: Dict[str, Any],
        duration_ms: int,
        status: str,
        parent_brain_id: Optional[str] = None,
        trace_context_id: Optional[str] = None,
        custom_metadata: Dict[str, Any] | None = None,
    ) -> str:
        """Log execution with automatic PII redaction.

        Args:
            brain_id: Brain being executed
            input_json: Input dictionary (will be hashed)
            output_json: Output dictionary (will be redacted)
            duration_ms: Execution duration in milliseconds
            status: Execution status (success, failure, timeout)
            parent_brain_id: Optional parent brain ID
            trace_context_id: Optional trace context ID
            custom_metadata: Optional custom metadata dictionary

        Returns:
            Record ID (UUID4)
        """
        # Create record with auto-generated fields
        record = ExperienceRecord.create(
            brain_id=brain_id,
            input_json=input_json,
            output_json=output_json,
            duration_ms=duration_ms,
            status=status,
            parent_brain_id=parent_brain_id,
            trace_context_id=trace_context_id,
            custom_metadata=custom_metadata,
        )

        # Redact PII before storage
        redacted_output = redact_for_storage(record.output_json)

        await self.db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status,
                parent_brain_id, trace_context_id, custom_metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                record.id,
                record.brain_id,
                record.input_hash,
                redacted_output,
                record.timestamp,
                record.duration_ms,
                record.status,
                record.parent_brain_id,
                record.trace_context_id,
                json.dumps(record.custom_metadata),
            ),
        )
        await self.db.conn.commit()
        return record.id

    async def get_by_id(self, record_id: str) -> Optional[ExperienceRecord]:
        """Retrieve single record by ID.

        Args:
            record_id: Record ID (UUID4)

        Returns:
            ExperienceRecord or None if not found
        """
        cursor = await self.db.conn.execute(
            "SELECT * FROM experience_records WHERE id = ?", (record_id,)
        )
        row = await cursor.fetchone()
        if row:
            return self._row_to_record(row)
        return None

    async def get_recent_by_brain(
        self, brain_id: str, limit: int = 100
    ) -> List[ExperienceRecord]:
        """Get last N records for a brain.

        Args:
            brain_id: Brain ID to filter by
            limit: Maximum number of records to return (default: 100)

        Returns:
            List of ExperienceRecord objects, ordered by timestamp DESC
        """
        cursor = await self.db.conn.execute(
            """SELECT * FROM experience_records
               WHERE brain_id = ?
               ORDER BY timestamp DESC
               LIMIT ?""",
            (brain_id, limit),
        )
        rows = await cursor.fetchall()
        return [self._row_to_record(row) for row in rows]

    async def search_by_trace_context(
        self, trace_context_id: str
    ) -> List[ExperienceRecord]:
        """Search all records with the same trace context (for lineage tracking).

        Args:
            trace_context_id: Trace context ID to search for

        Returns:
            List of ExperienceRecord objects with the same trace context,
            ordered by timestamp ASC (execution order)
        """
        cursor = await self.db.conn.execute(
            """SELECT * FROM experience_records
               WHERE trace_context_id = ?
               ORDER BY timestamp ASC""",
            (trace_context_id,),
        )
        rows = await cursor.fetchall()
        return [self._row_to_record(row) for row in rows]

    async def search_by_metadata(self, key: str, value: Any) -> List[ExperienceRecord]:
        """Keyword search over custom_metadata JSONB field.

        Args:
            key: Metadata key to search for (must be in ALLOWED_METADATA_KEYS)
            value: Value to match (converted to string)

        Returns:
            List of ExperienceRecord objects matching the metadata query

        Raises:
            ValueError: If key is not in the allowed metadata keys whitelist

        Note:
            Uses SQLite's json_extract() function for JSONB queries
            Key validation prevents SQL injection attacks
        """
        # Validate key is in whitelist (prevents SQL injection)
        if key not in ALLOWED_METADATA_KEYS:
            raise ValueError(
                f"Metadata key '{key}' is not allowed. "
                f"Allowed keys: {', '.join(sorted(ALLOWED_METADATA_KEYS))}"
            )

        # Try numeric comparison first, then string comparison
        # This handles cases where value is passed as string but stored as number in JSON
        cursor = await self.db.conn.execute(
            f"SELECT * FROM experience_records WHERE json_extract(custom_metadata, '$.{key}') = CAST(? AS REAL)",
            (str(value),),
        )
        rows = await cursor.fetchall()

        # If no results with numeric comparison, try string comparison
        if not rows:
            cursor = await self.db.conn.execute(
                f"SELECT * FROM experience_records WHERE json_extract(custom_metadata, '$.{key}') = ?",
                (str(value),),
            )
            rows = await cursor.fetchall()

        return [self._row_to_record(row) for row in rows]

    def _row_to_record(self, row: aiosqlite.Row) -> ExperienceRecord:
        """Convert SQLite row to ExperienceRecord.

        Args:
            row: SQLite row from experience_records table

        Returns:
            ExperienceRecord instance
        """
        return ExperienceRecord(
            id=row[0],
            brain_id=row[1],
            input_hash=row[2],
            output_json=json.loads(row[3]),
            timestamp=row[4],
            duration_ms=row[5],
            status=row[6],
            embedding_stub=row[7],
            parent_brain_id=row[8],
            trace_context_id=row[9],
            custom_metadata=json.loads(row[10]),
        )


# Convenience function for logging
async def log_execution(
    db: DatabaseConnection,
    brain_id: str,
    input_json: Dict[str, Any],
    output_json: Dict[str, Any],
    duration_ms: int,
    status: str,
    parent_brain_id: Optional[str] = None,
    trace_context_id: Optional[str] = None,
    custom_metadata: Dict[str, Any] = {},
) -> str:
    """Convenience function for logging execution.

    Args:
        db: DatabaseConnection instance
        brain_id: Brain being executed
        input_json: Input dictionary
        output_json: Output dictionary
        duration_ms: Execution duration in milliseconds
        status: Execution status
        parent_brain_id: Optional parent brain ID
        trace_context_id: Optional trace context ID
        custom_metadata: Optional custom metadata

    Returns:
        Record ID (UUID4)
    """
    logger = ExperienceLogger(db)
    return await logger.log_execution(
        brain_id=brain_id,
        input_json=input_json,
        output_json=output_json,
        duration_ms=duration_ms,
        status=status,
        parent_brain_id=parent_brain_id,
        trace_context_id=trace_context_id,
        custom_metadata=custom_metadata,
    )
