"""
Async SQLite database connection manager.

This module provides DatabaseConnection for aiosqlite with WAL mode
and schema creation for task state persistence.
"""

import aiosqlite
from typing import Optional
from pathlib import Path


class DatabaseConnection:
    """Async SQLite connection manager with WAL mode.

    This class manages aiosqlite connections with:
    - WAL (Write-Ahead Logging) mode for better write concurrency
    - Automatic index creation for common queries
    - Context manager support for proper resource cleanup

    Example:
        >>> async with DatabaseConnection(":memory:") as db:
        ...     await db.create_task_schema()
        ...     cursor = await db.conn.execute("SELECT * FROM tasks")
    """

    def __init__(self, db_path: str = ":memory:"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file (":memory:" for in-memory)
        """
        self.db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        """Establish database connection and enable WAL mode."""
        self._conn = await aiosqlite.connect(self.db_path)
        await self._enable_wal_mode()
        await self._create_indexes()

    async def _enable_wal_mode(self):
        """Enable WAL (Write-Ahead Logging) mode for better concurrency."""
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.commit()

    async def _create_indexes(self):
        """Create indexes for common queries (called after schema creation)."""
        # Indexes will be created by create_task_schema()
        pass

    @property
    def conn(self) -> aiosqlite.Connection:
        """Get the underlying aiosqlite connection.

        Raises:
            RuntimeError: If database is not connected
        """
        if self._conn is None:
            raise RuntimeError("Database not connected. Call connect() first.")
        return self._conn

    async def create_task_schema(self):
        """Create tasks table with indexes.

        Schema:
            - id: Task ID (primary key)
            - brain_id: Brain being executed
            - status: Task state (pending, running, completed, failed, cancelled, killed)
            - progress: JSON progress data
            - result: JSON result data
            - error: Error message if failed
            - created_at: Creation timestamp
            - updated_at: Last update timestamp
        """
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                status TEXT NOT NULL,
                progress TEXT,
                result TEXT,
                error TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)

        # Create indexes for common queries
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_id ON tasks(brain_id)"
        )
        await self.conn.commit()

    async def close(self):
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self):
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
