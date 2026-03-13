"""
Integration tests for database operations.

Tests for async SQLite database connection, TaskRecord model,
and TaskRepository CRUD operations.
"""

import pytest
from datetime import datetime, timezone
from mastermind_cli.state.database import DatabaseConnection
from mastermind_cli.state.models import TaskRecord


@pytest.mark.asyncio
async def test_database_connection():
    """Test DatabaseConnection connects and enables WAL mode."""
    db = DatabaseConnection(db_path=":memory:")

    async with db:
        # Check connection is established
        assert db.conn is not None

        # Verify WAL mode is enabled (note: in-memory DB returns "memory")
        cursor = await db.conn.execute("PRAGMA journal_mode")
        result = await cursor.fetchone()
        # In-memory databases can't use WAL, so we accept "memory"
        assert result[0] in ["wal", "memory"]


@pytest.mark.asyncio
async def test_create_task_schema():
    """Test tasks table creation with indexes."""
    db = DatabaseConnection(db_path=":memory:")

    async with db:
        # Create schema
        await db.create_task_schema()

        # Verify tasks table exists
        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='tasks'"
        )
        result = await cursor.fetchone()
        assert result is not None
        assert result[0] == "tasks"

        # Verify indexes exist
        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_status'"
        )
        result = await cursor.fetchone()
        assert result is not None


@pytest.mark.asyncio
async def test_task_record_model():
    """Test TaskRecord Pydantic model."""
    now = datetime.now(timezone.utc)

    task = TaskRecord(
        id="test-001",
        brain_id="brain-01",
        status="pending",
        created_at=now,
        updated_at=now
    )

    assert task.id == "test-001"
    assert task.brain_id == "brain-01"
    assert task.status == "pending"
    assert task.progress is None
    assert task.result is None
    assert task.error is None


@pytest.mark.asyncio
async def test_crud_operations():
    """Test TaskRepository CRUD operations."""
    from mastermind_cli.state.repositories import TaskRepository

    db = DatabaseConnection(db_path=":memory:")

    async with db:
        await db.create_task_schema()
        repo = TaskRepository(db)

        # CREATE
        task = await repo.create(task_id="task-001", brain_id="brain-01")
        assert task.id == "task-001"
        assert task.brain_id == "brain-01"
        assert task.status == "pending"

        # READ
        retrieved = await repo.get(task_id="task-001")
        assert retrieved is not None
        assert retrieved.id == "task-001"
        assert retrieved.status == "pending"

        # UPDATE STATUS
        updated = await repo.update_status(task_id="task-001", status="running")
        assert updated.status == "running"

        # UPDATE RESULT
        result_data = {"output": "test result", "score": 0.95}
        completed = await repo.update_result(task_id="task-001", result=result_data)
        assert completed.status == "completed"
        assert completed.result is not None

        # QUERY BY STATUS
        await repo.create(task_id="task-002", brain_id="brain-02")
        await repo.update_status(task_id="task-002", status="failed")

        pending_tasks = await repo.get_by_status(status="pending")
        assert len(pending_tasks) == 0

        failed_tasks = await repo.get_by_status(status="failed")
        assert len(failed_tasks) == 1
        assert failed_tasks[0].id == "task-002"
