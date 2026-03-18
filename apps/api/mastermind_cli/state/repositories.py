"""
Async repository for task CRUD operations.

This module provides TaskRepository for async database operations
using aiosqlite with checkpoint-based state transitions.
"""

from typing import Any, Optional, List
from datetime import datetime, timezone
import json

from .database import DatabaseConnection
from .models import TaskRecord


class TaskRepository:
    """Async repository for task CRUD operations.

    This repository provides async methods for creating, updating,
    and querying tasks using aiosqlite. All updates are checkpoint-based
    (atomic transactions) to avoid corruption.

    Example:
        >>> async with DatabaseConnection() as db:
        ...     repo = TaskRepository(db)
        ...     task = await repo.create(task_id="task-001", brain_id="brain-01")
        ...     updated = await repo.update_status(task_id, status="running")
    """

    def __init__(self, db: DatabaseConnection):
        """Initialize repository with database connection.

        Args:
            db: DatabaseConnection instance
        """
        self.db = db

    async def create(self, task_id: str, brain_id: str) -> TaskRecord:
        """Create a new task with pending status.

        Args:
            task_id: Unique task identifier
            brain_id: Brain being executed

        Returns:
            Created TaskRecord
        """
        now = datetime.now(timezone.utc).isoformat()
        await self.db.conn.execute(
            """INSERT INTO tasks (id, brain_id, status, created_at, updated_at)
               VALUES (?, ?, 'pending', ?, ?)""",
            (task_id, brain_id, now, now),
        )
        await self.db.conn.commit()
        result = await self.get(task_id)
        if result is None:
            raise RuntimeError(f"Failed to create task: {task_id}")
        return result

    async def update_status(
        self, task_id: str, status: str, error: Optional[str] = None
    ) -> TaskRecord:
        """Update task status atomically (checkpoint-based).

        This method updates the task status in a single transaction.
        If an error is provided, it also updates the error field.

        Args:
            task_id: Task identifier
            status: New status
            error: Optional error message

        Returns:
            Updated TaskRecord
        """
        now = datetime.now(timezone.utc).isoformat()
        if error:
            await self.db.conn.execute(
                """UPDATE tasks SET status = ?, error = ?, updated_at = ?
                   WHERE id = ?""",
                (status, error, now, task_id),
            )
        else:
            await self.db.conn.execute(
                """UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?""",
                (status, now, task_id),
            )
        await self.db.conn.commit()
        task = await self.get(task_id)
        if task is None:
            raise RuntimeError(f"Task {task_id} not found after update")
        return task

    async def update_result(self, task_id: str, result: dict[str, Any]) -> TaskRecord:
        """Update task result and mark as completed.

        Args:
            task_id: Task identifier
            result: Result data (will be JSON-serialized)

        Returns:
            Updated TaskRecord with completed status
        """
        now = datetime.now(timezone.utc).isoformat()
        result_json = json.dumps(result)
        await self.db.conn.execute(
            """UPDATE tasks SET status = 'completed', result = ?, updated_at = ?
               WHERE id = ?""",
            (result_json, now, task_id),
        )
        await self.db.conn.commit()
        task = await self.get(task_id)
        if task is None:
            raise RuntimeError(f"Task {task_id} not found after result update")
        return task

    async def get(self, task_id: str) -> Optional[TaskRecord]:
        """Retrieve task by ID.

        Args:
            task_id: Task identifier

        Returns:
            TaskRecord if found, None otherwise
        """
        cursor = await self.db.conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        row = await cursor.fetchone()
        if row:
            return TaskRecord(
                id=row[0],
                brain_id=row[1],
                status=row[2],
                progress=row[3],
                result=row[4],
                error=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
        return None

    async def get_by_status(self, status: str) -> List[TaskRecord]:
        """Retrieve all tasks with given status.

        Args:
            status: Status to filter by

        Returns:
            List of TaskRecords with matching status
        """
        cursor = await self.db.conn.execute(
            "SELECT * FROM tasks WHERE status = ?", (status,)
        )
        rows = await cursor.fetchall()
        return [
            TaskRecord(
                id=row[0],
                brain_id=row[1],
                status=row[2],
                progress=row[3],
                result=row[4],
                error=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            for row in rows
        ]

    async def get_task_status(self, task_id: str) -> Optional[TaskRecord]:
        """Get task status with <100ms performance target.

        This method retrieves a single task by ID with performance monitoring.
        Uses indexed columns for fast queries.

        Args:
            task_id: Task identifier

        Returns:
            TaskRecord or None if not found

        Performance:
            Uses indexed status column for fast queries.
            Target: <100ms for single task lookup.
            Logs warning if query exceeds 100ms.
        """
        import time

        start = time.perf_counter()

        cursor = await self.db.conn.execute(
            "SELECT * FROM tasks WHERE id = ?", (task_id,)
        )
        row = await cursor.fetchone()

        elapsed_ms = (time.perf_counter() - start) * 1000

        if row:
            task = TaskRecord(
                id=row[0],
                brain_id=row[1],
                status=row[2],
                progress=row[3],
                result=row[4],
                error=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            # Log performance (warn if >100ms)
            if elapsed_ms > 100:
                print(f"⚠️  Slow query: {elapsed_ms:.2f}ms for task_id={task_id}")
            return task

        return None

    async def get_all_statuses(self) -> List[TaskRecord]:
        """Get all tasks for dashboard display.

        This method retrieves all tasks ordered by creation time (newest first),
        useful for dashboard views and progress monitoring.

        Returns:
            List of all TaskRecords ordered by created_at DESC
        """
        cursor = await self.db.conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC"
        )
        rows = await cursor.fetchall()

        return [
            TaskRecord(
                id=row[0],
                brain_id=row[1],
                status=row[2],
                progress=row[3],
                result=row[4],
                error=row[5],
                created_at=row[6],
                updated_at=row[7],
            )
            for row in rows
        ]
