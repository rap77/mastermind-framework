"""
Async SQLite database connection manager.

This module provides DatabaseConnection for aiosqlite with WAL mode
and schema creation for task state persistence.
"""

import os
import uuid

import aiosqlite
import asyncpg  # type: ignore[import-untyped]
import bcrypt
from typing import Optional, Any


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

    async def connect(self) -> None:
        """Establish database connection and enable WAL mode."""
        self._conn = await aiosqlite.connect(self.db_path)
        await self._enable_wal_mode()
        await self._create_indexes()

    async def _enable_wal_mode(self) -> None:
        """Enable WAL (Write-Ahead Logging) mode for better concurrency."""
        assert self._conn is not None
        await self._conn.execute("PRAGMA journal_mode=WAL")
        await self._conn.commit()

    async def _create_indexes(self) -> None:
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

    async def create_task_schema(self) -> None:
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
                status TEXT,
                user_id TEXT
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

    async def create_auth_schema(self) -> None:
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

        # Seed admin user on first run if no users exist
        cursor = await self.conn.execute("SELECT COUNT(*) FROM users")
        row = await cursor.fetchone()
        if row and row[0] == 0:
            admin_password = os.environ.get("MM_ADMIN_PASSWORD", "admin")
            password_hash = bcrypt.hashpw(
                admin_password.encode("utf-8"), bcrypt.gensalt(rounds=12)
            ).decode("utf-8")
            await self.conn.execute(
                "INSERT INTO users (id, username, password_hash) VALUES (?, ?, ?)",
                [str(uuid.uuid4()), "admin", password_hash],
            )
            await self.conn.commit()

    async def create_api_keys_v2_schema(self) -> None:
        """Create api_keys_v2 table with Phase 08 show-once pattern.

        Separate from the legacy api_keys table (which uses SHA256 + mm_ prefix).
        This table adds:
        - prefix: first 13 chars (mmsk_ + 8 hex) for O(1) candidate lookup
        - suffix: last 4 chars for display
        - revoked_at: NULL=active, non-null=revoked (soft-delete pattern)
        - name: optional user-defined label

        Key format: mmsk_ + 32 hex = 37 chars total
        prefix = first 13 chars ("mmsk_" + 8 hex)
        suffix = last 4 chars

        Requirements: ER-02
        """
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS api_keys_v2 (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                key_hash TEXT NOT NULL,
                prefix TEXT NOT NULL,
                suffix TEXT NOT NULL,
                name TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_used_at TIMESTAMP,
                revoked_at TIMESTAMP
            )
        """)

        # Index on prefix for O(1) candidate lookup during validation
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_keys_v2_prefix ON api_keys_v2(prefix)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_api_keys_v2_user_id ON api_keys_v2(user_id)"
        )

        await self.conn.commit()

    async def create_execution_history_schema(self) -> None:
        """Create execution_history table for Strategy Vault.

        Separate from the executions table (which represents tasks/runs).
        execution_history stores the completed output of each execution
        with JSONB-equivalent columns (stored as JSON text in SQLite).

        Schema (Phase 08 - SV-01, SV-02):
            - id: UUID primary key
            - task_id: FK to executions table (unique - one per task)
            - brief: First 100 chars of brief text
            - status: success/error/running
            - duration_ms: Total execution time
            - brain_count: Number of brains that participated
            - created_at: ISO timestamp
            - milestones_json: JSON array of SnapshotMilestone objects
            - brain_outputs_json: JSON dict {brain_id: BrainOutput}
            - graph_snapshot_json: JSON DAG state for replay

        Concurrency:
            UNIQUE constraint on task_id enables INSERT ... ON CONFLICT DO NOTHING
            (first writer wins - handles 24 brains completing simultaneously)
        """
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS execution_history (
                id TEXT PRIMARY KEY,
                task_id TEXT UNIQUE NOT NULL,
                brief TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'running',
                duration_ms INTEGER NOT NULL DEFAULT 0,
                brain_count INTEGER NOT NULL DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                milestones_json TEXT NOT NULL DEFAULT '[]',
                brain_outputs_json TEXT NOT NULL DEFAULT '{}',
                graph_snapshot_json TEXT NOT NULL DEFAULT '{}'
            )
        """)

        # Indexes for Strategy Vault queries
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_execution_history_task_id "
            "ON execution_history(task_id)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_execution_history_created_at "
            "ON execution_history(created_at DESC)"
        )

        await self.conn.commit()

    async def create_experience_schema(self) -> None:
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
                custom_metadata TEXT NOT NULL DEFAULT '{}',
                expires_at TEXT
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

        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_experience_expires_at "
            "ON experience_records(expires_at)"
        )

        # Create knowledge_templates table (separate from experience_records)
        # Per Screaming Architecture: templates are domain concepts, logs are infrastructure
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_templates (
                id TEXT PRIMARY KEY,
                brain_id TEXT NOT NULL,
                template_name TEXT NOT NULL,
                template_data TEXT NOT NULL,
                success_rate REAL DEFAULT 1.0,
                usage_count INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                last_used_at TEXT
            )
        """)

        # Index for brain-specific template retrieval
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_templates_brain_id "
            "ON knowledge_templates(brain_id)"
        )

        # Index for success rate ranking (best templates first)
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_templates_success_rate "
            "ON knowledge_templates(success_rate DESC)"
        )

        # Index for last-used tracking
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_knowledge_templates_last_used_at "
            "ON knowledge_templates(last_used_at DESC)"
        )

        await self.conn.commit()

    async def create_audit_trail_schema(self) -> None:
        """Create audit trail tables for MM-Flow (Phase 16+).

        Audit Trail Schema (Phase 16 - Observability):
            - phase_executions: Track each phase execution with timing and status
            - decisions: Record architectural/technical decisions with rationale
            - verification_gates: Track quality gate results
            - artifacts: Track generated documents and plans
            - brain_feedback: Capture feedback from brain agents
            - dev_sessions: Track development sessions with task completion
            - audit_log: Immutable compliance audit trail

        These tables enable:
            - Phase timeline reconstruction
            - Decision history and traceability
            - Quality metrics (gate pass rates, decision approval rates)
            - Session continuity and velocity tracking
            - Compliance and governance
        """
        # phase_executions: Track each phase execution
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS phase_executions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                execution_num INTEGER NOT NULL DEFAULT 1,
                status TEXT NOT NULL,
                started_at TEXT NOT NULL,
                completed_at TEXT,
                duration_seconds INTEGER,
                backend_used TEXT,
                tokens_consumed INTEGER DEFAULT 0,
                tokens_input INTEGER DEFAULT 0,
                tokens_output INTEGER DEFAULT 0,
                output_summary TEXT,
                git_commit_hash TEXT,
                triggered_by TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # decisions: Record decisions made during phases
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                decision_type TEXT NOT NULL,
                title TEXT NOT NULL,
                rationale TEXT NOT NULL,
                chosen_option TEXT NOT NULL,
                alternatives TEXT,
                confidence REAL DEFAULT 0.5,
                impact_level TEXT NOT NULL,
                impact_description TEXT,
                status TEXT DEFAULT 'pending',
                made_by TEXT NOT NULL,
                approved_by TEXT,
                tags TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # verification_gates: Track quality gates per phase
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS verification_gates (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                gate_type TEXT NOT NULL,
                gate_name TEXT NOT NULL,
                status TEXT NOT NULL,
                score REAL,
                result TEXT,
                evaluation_notes TEXT,
                evaluated_by TEXT,
                completed_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # artifacts: Track generated plans, specs, etc.
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS artifacts (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                artifact_type TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                created_by TEXT NOT NULL,
                git_commit_hash TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # brain_feedback: Capture brain agent insights
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_feedback (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                brain_id INTEGER NOT NULL,
                feedback_text TEXT NOT NULL,
                feedback_type TEXT,
                confidence_score REAL DEFAULT 0.5,
                impact_level TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # dev_sessions: Track development sessions
        await self.conn.execute("""
            CREATE TABLE IF NOT EXISTS dev_sessions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER,
                session_date TEXT NOT NULL,
                duration_minutes INTEGER,
                status TEXT NOT NULL,
                tasks_completed INTEGER DEFAULT 0,
                tasks_total INTEGER DEFAULT 0,
                commits_count INTEGER DEFAULT 0,
                discoveries TEXT,
                blockers TEXT,
                next_steps TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_phase_executions_project_phase "
            "ON phase_executions(project_id, phase_num)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_decisions_project_phase "
            "ON decisions(project_id, phase_num)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_decisions_created_at "
            "ON decisions(project_id, created_at DESC)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_verification_gates_project_phase "
            "ON verification_gates(project_id, phase_num)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_artifacts_project_phase "
            "ON artifacts(project_id, phase_num)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_feedback_project_brain "
            "ON brain_feedback(project_id, brain_id)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_feedback_created_at "
            "ON brain_feedback(project_id, created_at DESC)"
        )
        await self.conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_dev_sessions_project_phase "
            "ON dev_sessions(project_id, phase_num)"
        )

        await self.conn.commit()

    async def close(self) -> None:
        """Close database connection."""
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def __aenter__(self) -> "DatabaseConnection":
        """Async context manager entry."""
        await self.connect()
        return self

    async def __aexit__(
        self, exc_type: object | None, exc_val: object | None, exc_tb: object | None
    ) -> None:
        """Async context manager exit."""
        await self.close()

    # ===== API KEY METHODS =====

    async def get_api_key(self, key_hash: str) -> dict[str, Any] | None:
        """Get API key by hash.

        Args:
            key_hash: SHA256 hash of the API key

        Returns:
            API key data dict or None if not found
        """
        cursor = await self.conn.execute(
            "SELECT id, user_id, key_hash, name, created_at, last_used FROM api_keys WHERE key_hash = ?",
            (key_hash,),
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

    async def save_api_key(self, key_data: dict[str, Any]) -> bool:
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
            (
                key_id,
                key_data["owner"],
                key_data["key_hash"],
                f"API Key for {key_data['owner']}",
                datetime.now(timezone.utc).isoformat(),
            ),
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
            "DELETE FROM api_keys WHERE key_hash = ?", (key_hash,)
        )
        await self.conn.commit()
        return cursor.rowcount > 0

    async def list_api_keys(self, owner: str | None = None) -> list[dict[str, Any]]:
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
                (owner,),
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


class DualWriteDatabaseConnection(DatabaseConnection):
    """Dual-write database connection manager (SQLite + PostgreSQL).

    Extends DatabaseConnection to write to both SQLite and PostgreSQL simultaneously.
    Reads from PostgreSQL (primary source after migration).

    Attributes:
        postgres_url: PostgreSQL connection URL (optional)
        _pg_conn: asyncpg connection to PostgreSQL

    Example:
        >>> db = DualWriteDatabaseConnection("mastermind.db", "postgresql://...")
        >>> await db.connect()
        >>> await db.execute_write("INSERT INTO tasks ...")
        >>> result = await db.execute_read("SELECT * FROM tasks")
    """

    def __init__(self, db_path: str = ":memory:", postgres_url: Optional[str] = None):
        """Initialize dual-write database connection.

        Args:
            db_path: Path to SQLite database file
            postgres_url: PostgreSQL connection URL (optional)
        """
        super().__init__(db_path)
        self.postgres_url = postgres_url
        self._pg_conn: Optional[asyncpg.Connection] = None

    async def connect(self) -> None:
        """Connect to both SQLite and PostgreSQL."""
        await super().connect()  # SQLite connection

        if self.postgres_url:
            try:
                self._pg_conn = await asyncpg.connect(self.postgres_url)
            except Exception as e:
                # Log but don't fail - dual-write is optional during migration
                print(f"Warning: Failed to connect to PostgreSQL: {e}")

    async def execute_write(self, sql: str, *args: Any) -> None:
        """Write to both SQLite and PostgreSQL.

        Args:
            sql: SQL statement to execute
            *args: Query parameters

        Note:
            PostgreSQL write failures don't affect SQLite writes (graceful degradation)
        """
        # Write to SQLite
        await self.conn.execute(sql, *args)

        # Write to PostgreSQL (non-blocking)
        if self._pg_conn:
            try:
                # Convert SQLite ? placeholders to PostgreSQL $1, $2, etc.
                pg_sql = self._convert_placeholders(sql)
                await self._pg_conn.execute(pg_sql, *args)
            except Exception as e:
                # Log but don't fail - dual-write is optional
                print(f"Warning: PostgreSQL write failed: {e}")

    async def execute_read(
        self, sql: str, *args: Any, fetch_one: bool = False, fetch_val: bool = False
    ) -> Any:
        """Read from PostgreSQL (primary source) or fallback to SQLite.

        Args:
            sql: SQL query to execute
            *args: Query parameters
            fetch_one: Return single row instead of all rows
            fetch_val: Return single value instead of row

        Returns:
            Query result (row, rows, or value)
        """
        # Try PostgreSQL first
        if self._pg_conn:
            try:
                pg_sql = self._convert_placeholders(sql)
                if fetch_val:
                    return await self._pg_conn.fetchval(pg_sql, *args)
                elif fetch_one:
                    return await self._pg_conn.fetchrow(pg_sql, *args)
                else:
                    return await self._pg_conn.fetch(pg_sql, *args)
            except Exception as e:
                # Fallback to SQLite on error
                print(f"Warning: PostgreSQL read failed, using SQLite: {e}")

        # Fallback to SQLite
        if fetch_val:
            cursor = await self.conn.execute(sql, *args)
            row = await cursor.fetchone()
            return row[0] if row else None
        elif fetch_one:
            cursor = await self.conn.execute(sql, *args)
            return await cursor.fetchone()
        else:
            cursor = await self.conn.execute(sql, *args)
            return await cursor.fetchall()

    async def verify_consistency(self) -> list[str]:
        """Verify row counts match between SQLite and PostgreSQL.

        Returns:
            List of inconsistency messages (empty if all consistent)
        """
        if not self._pg_conn:
            return ["PostgreSQL not connected"]

        inconsistencies = []
        tables = [
            "users",
            "sessions",
            "tasks",
            "executions",
            "api_keys",
            "experience_records",
        ]

        for table in tables:
            try:
                # SQLite count
                cursor = await self.conn.execute(f"SELECT COUNT(*) FROM {table}")
                sqlite_row = await cursor.fetchone()
                sqlite_count = sqlite_row[0] if sqlite_row else 0

                # PostgreSQL count
                pg_count = await self._pg_conn.fetchval(f"SELECT COUNT(*) FROM {table}")

                if sqlite_count != pg_count:
                    inconsistencies.append(
                        f"{table}: SQLite={sqlite_count}, PostgreSQL={pg_count}"
                    )
            except Exception as e:
                inconsistencies.append(f"{table}: Error - {e}")

        return inconsistencies

    def _convert_placeholders(self, sql: str) -> str:
        """Convert SQLite ? placeholders to PostgreSQL $1, $2, etc.

        Args:
            sql: SQL query with ? placeholders

        Returns:
            SQL query with $1, $2, etc. placeholders
        """
        param_count = 0
        result = []

        for char in sql:
            if char == "?":
                param_count += 1
                result.append(f"${param_count}")
            else:
                result.append(char)

        return "".join(result)


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
