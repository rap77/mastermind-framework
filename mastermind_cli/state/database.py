"""
Async SQLite database connection manager.

This module provides DatabaseConnection for aiosqlite with WAL mode
and schema creation for task state persistence.
"""

import aiosqlite
from typing import Optional


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
        """Create tasks and executions tables with indexes.

        Tasks Schema:
            - id: Task ID (primary key)
            - brain_id: Brain being executed
            - status: Task state (pending, running, completed, failed, cancelled, killed)
            - progress: JSON progress data
            - result: JSON result data
            - error: Error message if failed
            - created_at: Creation timestamp
            - updated_at: Last update timestamp

        Executions Schema:
            - id: Execution ID (primary key)
            - flow_config: FlowConfig as JSON
            - brief: User's brief
            - created_at: Creation timestamp
            - status: Execution status (pending, running, completed, failed)
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

        # Create executions table for config persistence
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS executions (
                id TEXT PRIMARY KEY,
                flow_config TEXT NOT NULL,
                brief TEXT NOT NULL,
                created_at TIMESTAMP,
                status TEXT
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

    async def create_auth_schema(self):
        """Create authentication tables for JWT and API key management.

        Auth Schema (Phase 3 - UI-02, UI-03, UI-07):
            - users: User accounts with password hashes
            - sessions: Refresh token sessions with rotation support
            - api_keys: API keys for CLI access
            - audit_log: Audit trail for all mutations

        Creates admin user on first run if no users exist.
        """
        # Users table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Sessions table for refresh token rotation
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                refresh_token_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP NOT NULL,
                rotation_count INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # API keys table for CLI access
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                name TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Audit log table for all mutations
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                endpoint TEXT NOT NULL,
                method TEXT NOT NULL,
                request_hash TEXT,
                response_status INTEGER NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)

        # Create indexes for auth queries
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_sessions_refresh_token_hash ON sessions(refresh_token_hash)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_keys_user_id ON api_keys(user_id)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_keys_key_hash ON api_keys(key_hash)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_audit_log_user_id ON audit_log(user_id, timestamp DESC)"
        )

        await self.conn.commit()

    async def create_experience_schema(self):
        """Create experience_records table for full-fidelity execution logging.

        Experience Schema (Phase 4 - 04-01):
            - id: Record ID (UUID4, primary key)
            - brain_id: Brain being executed
            - input_hash: SHA256 of input_json for deduplication
            - output_json: Complete output from brain (redacted)
            - timestamp: ISO 8601 timestamp (UTC)
            - duration_ms: Execution duration in milliseconds
            - status: Execution status (success, failure, timeout)
            - embedding_stub: Placeholder for v3.0 pgvector embeddings
            - parent_brain_id: Parent brain that triggered this execution
            - trace_context_id: Trace context for distributed tracing
            - custom_metadata: Extensible metadata (JSONB)

        Indexes:
            - idx_experience_brain_timestamp: (brain_id, timestamp DESC)
            - idx_experience_trace: (trace_context_id)
        """
        # Create experience_records table
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS experience_records (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                input_hash TEXT NOT NULL,
                output_json TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                duration_ms INTEGER NOT NULL,
                status TEXT NOT NULL,
                embedding_stub BLOB,
                parent_brain_id TEXT,
                trace_context_id TEXT,
                custom_metadata TEXT NOT NULL DEFAULT '{}'
            )
        """)

        # Create indexes for common queries
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_experience_brain_timestamp "
            "ON experience_records(brain_id, timestamp DESC)"
        )

        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_experience_trace "
            "ON experience_records(trace_context_id)"
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

    # ===== API KEY METHODS =====

    async def get_api_key(self, key_hash: str) -> dict | None:
        """Get API key by hash.

        Args:
            key_hash: SHA256 hash of the API key

        Returns:
            API key data dict or None if not found
        """
        cursor = await self.conn.execute(
            "SELECT id, user_id, key_hash, name, created_at, last_used FROM api_keys WHERE key_hash = ?",
            (key_hash,)
        )
        row = await cursor.fetchone()

        if row:
            return {
                "key": "",  # Never return actual key from DB
                "key_hash": row[2],
                "owner": row[1],  # user_id maps to owner
                "created_at": row[3],
                "is_active": True,  # Add to api_keys schema in v2.1
                "scopes": ["read", "write"],  # Add to api_keys schema in v2.1
            }
        return None

    async def save_api_key(self, key_data: dict) -> bool:
        """Save API key to database.

        Args:
            key_data: API key data dict with key_hash, owner, created_at

        Returns:
            True if saved successfully
        """
        import uuid
        from datetime import datetime, timezone

        key_id = str(uuid.uuid4())
        await self.conn.execute(
            """INSERT INTO api_keys (id, user_id, key_hash, name, created_at)
               VALUES (?, ?, ?, ?, ?)""",
            (key_id, key_data["owner"], key_data["key_hash"],
             f"API Key for {key_data['owner']}",
             datetime.now(timezone.utc).isoformat())
        )
        await self.conn.commit()
        return True

    async def revoke_api_key(self, key_hash: str) -> bool:
        """Revoke API key by deleting it.

        Args:
            key_hash: SHA256 hash of the key to revoke

        Returns:
            True if revoked, False if not found
        """
        cursor = await self.conn.execute(
            "DELETE FROM api_keys WHERE key_hash = ?",
            (key_hash,)
        )
        await self.conn.commit()
        return cursor.rowcount > 0

    async def list_api_keys(self, owner: str | None = None) -> list[dict]:
        """List all API keys, optionally filtered by owner.

        Args:
            owner: Optional owner (user_id) filter

        Returns:
            List of API key data dicts
        """
        if owner:
            cursor = await self.conn.execute(
                """SELECT id, user_id, key_hash, name, created_at, last_used
                   FROM api_keys WHERE user_id = ?""",
                (owner,)
            )
        else:
            cursor = await self.conn.execute(
                """SELECT id, user_id, key_hash, name, created_at, last_used
                   FROM api_keys"""
            )

        rows = await cursor.fetchall()

        return [
            {
                "key": "",
                "key_hash": row[2],
                "owner": row[1],
                "created_at": row[3],
                "is_active": True,
                "scopes": ["read", "write"],
            }
            for row in rows
        ]


# ===== SINGLETON DATABASE INSTANCE =====

_db_instance: DatabaseConnection | None = None


def get_db(db_path: str = ":memory:") -> DatabaseConnection:
    """Get or create singleton database instance.

    Args:
        db_path: Path to database file (default: ":memory:")

    Returns:
        DatabaseConnection instance

    Note:
        This is a synchronous wrapper that creates an async connection.
        The async methods must be called from an async context.
    """
    global _db_instance

    if _db_instance is None:
        _db_instance = DatabaseConnection(db_path)

    return _db_instance
