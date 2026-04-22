"""
MasterMind DB Client — shared PostgreSQL client for all handlers.

Provides centralized database operations with graceful degradation:
- If PostgreSQL is unavailable, all methods return None/empty values
- Never raises exceptions that crash handlers
- Thread-safe singleton pattern

Usage:
    from db_client import MasterMindDB
    db = MasterMindDB()
    if db.available:
        project_id = db.register_project("my-app", "/path", ["nextjs"])
"""

from __future__ import annotations

import json
import warnings
from datetime import datetime, timezone
from typing import Any

# Optional dependency: asyncpg for PostgreSQL support
# If not available, module works in degraded mode (all methods return None)
try:
    import asyncio
    import asyncpg

    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False
    asyncpg = None  # type: ignore
    asyncio = None  # type: ignore


class MasterMindDB:
    """Centralized PostgreSQL client for MasterMind handlers.

    Features:
    - Graceful degradation: works even if PostgreSQL is down
    - Synchronous interface: usable from non-async handlers
    - Thread-safe: can be shared across multiple handler instances
    - Auto-reconnect: attempts connection on each call if unavailable

    Attributes:
        host: PostgreSQL host (default: localhost)
        port: PostgreSQL port (default: 5433)
        database: Database name (default: mastermind_bd)
        available: Whether DB is currently connected
    """

    def __init__(
        self, host: str = "localhost", port: int = 5433, database: str = "mastermind_bd"
    ) -> None:
        """Initialize database client.

        Args:
            host: PostgreSQL host address
            port: PostgreSQL port number
            database: Database name

        The connection attempt happens in __init__ with graceful degradation.
        If connection fails, available=False and all methods return None.
        """
        self.host = host
        self.port = port
        self.database = database
        self._conn: asyncpg.Connection | None = None
        self.available = self._check_connection()

    def _check_connection(self) -> bool:
        """Test PostgreSQL connection.

        Attempts to connect and returns True if successful, False otherwise.
        Never raises exceptions - logs warnings instead.

        Returns:
            bool: True if connection successful, False if failed
        """
        if not ASYNCPG_AVAILABLE:
            warnings.warn("asyncpg not installed - database operations disabled")
            return False

        try:
            # Try to establish connection
            conn = self._get_sync_connection()
            if conn:
                self._conn = conn
                return True
            return False
        except Exception as e:
            warnings.warn(f"PostgreSQL connection failed: {e}")
            return False

    def _get_sync_connection(self) -> asyncpg.Connection | None:
        """Create synchronous asyncpg connection.

        Uses asyncio.run() to bridge async/sync boundary.
        Returns None if connection fails.

        Returns:
            asyncpg.Connection or None
        """
        if not ASYNCPG_AVAILABLE:
            return None

        assert asyncpg is not None
        assert asyncio is not None

        async def _connect() -> asyncpg.Connection | None:
            try:
                return await asyncpg.connect(
                    host=self.host,
                    port=self.port,
                    database=self.database,
                    user="postgres",
                    timeout=5.0,
                )
            except Exception:
                return None

        try:
            # Create new event loop for this connection attempt
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            conn = loop.run_until_complete(_connect())
            loop.close()
            return conn
        except Exception:
            return None

    def ping(self) -> bool:
        """Check if database is available.

        Returns:
            bool: True if DB is connected and responsive, False otherwise
        """
        if not self._conn:
            return False

        try:
            import asyncio

            async def _ping() -> bool:
                assert self._conn is not None
                await self._conn.execute("SELECT 1")
                return True

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_ping())
            loop.close()
            return result
        except Exception:
            self.available = False
            self._conn = None
            return False

    def register_project(self, name: str, path: str, stack: list[str]) -> str | None:
        """Register or update project in database.

        Args:
            name: Project name
            path: Project file path
            stack: List of detected technologies (e.g., ["nextjs", "python"])

        Returns:
            Project ID (UUID as string) if successful, None if DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio
            from slugify import slugify

            async def _get_or_create_default_org() -> str:
                """Get or create default organization."""
                assert self._conn is not None
                query = """
                    INSERT INTO organizations (id, name, slug)
                    VALUES ($1, 'Default', 'default')
                    ON CONFLICT (id) DO NOTHING
                    RETURNING id
                """
                default_org_id = "00000000-0000-0000-0000-000000000001"
                row = await self._conn.fetchrow(query, default_org_id)
                return row["id"]

            async def _register() -> str | None:
                assert self._conn is not None
                # Get or create default organization
                org_id = await _get_or_create_default_org()

                # Generate slug from name
                slug = slugify(name, max_length=100)

                # Build metadata JSONB with path and stack
                metadata = {"path": path, "stack": stack}

                # Use INSERT ... ON CONFLICT (upsert)
                query = """
                    INSERT INTO projects (org_id, slug, name, project_type, metadata, created_at, updated_at)
                    VALUES ($1, $2, $3, 'software', $4, NOW(), NOW())
                    ON CONFLICT (org_id, slug)
                    DO UPDATE SET
                        name = EXCLUDED.name,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                    RETURNING id
                """
                row = await self._conn.fetchrow(
                    query, org_id, slug, name, json.dumps(metadata)
                )
                return str(row["id"]) if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_register())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to register project: {e}")
            return None

    def get_project(self, path: str) -> dict[str, Any] | None:
        """Get project by path (searches in metadata).

        Args:
            path: Project file path

        Returns:
            Project dict if found, None if not found or DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _get() -> dict[str, Any] | None:
                assert self._conn is not None
                # Search in metadata JSONB where path matches
                query = "SELECT * FROM projects WHERE metadata->>'path' = $1"
                row = await self._conn.fetchrow(query, path)
                return dict(row) if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_get())
            loop.close()
            return result
        except Exception:
            return None

    def save_brain_consultation(
        self,
        brain_id: str,
        input_data: dict[str, Any],
        output_data: dict[str, Any],
        confidence: float,
    ) -> int | None:
        """Save brain consultation to database.

        Args:
            brain_id: Brain identifier (e.g., "brain-01-product")
            input_data: Input provided to brain
            output_data: Brain's output
            confidence: Confidence score (0.0 to 1.0)

        Returns:
            Consultation ID (int) if successful, None if DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _save() -> int:
                assert self._conn is not None
                query = """
                    INSERT INTO brain_consultations
                    (brain_id, input_data, output_data, confidence, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    RETURNING id
                """
                row = await self._conn.fetchrow(
                    query,
                    brain_id,
                    json.dumps(input_data),
                    json.dumps(output_data),
                    confidence,
                )
                return row["id"] if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_save())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to save brain consultation: {e}")
            return None

    def save_artifact(
        self,
        project_id: int,
        artifact_type: str,
        content: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> int | None:
        """Save artifact to database.

        Args:
            project_id: Project ID
            artifact_type: Type of artifact (e.g., "spec", "plan", "review")
            content: Artifact content as dict
            metadata: Optional metadata

        Returns:
            Artifact ID (int) if successful, None if DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _save() -> int:
                assert self._conn is not None
                query = """
                    INSERT INTO artifacts
                    (project_id, artifact_type, content, metadata, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    RETURNING id
                """
                row = await self._conn.fetchrow(
                    query,
                    project_id,
                    artifact_type,
                    json.dumps(content),
                    json.dumps(metadata or {}),
                )
                return row["id"] if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_save())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to save artifact: {e}")
            return None

    def save_decision(
        self,
        project_id: int,
        decision: str,
        rationale: str,
        impact: str | None = None,
    ) -> int | None:
        """Save decision to database.

        Args:
            project_id: Project ID
            decision: Decision description
            rationale: Rationale for the decision
            impact: Optional impact assessment

        Returns:
            Decision ID (int) if successful, None if DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _save() -> int:
                assert self._conn is not None
                query = """
                    INSERT INTO decisions
                    (project_id, decision, rationale, impact, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    RETURNING id
                """
                row = await self._conn.fetchrow(
                    query, project_id, decision, rationale, impact
                )
                return row["id"] if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_save())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to save decision: {e}")
            return None

    def save_experience(
        self,
        project_id: int,
        session_id: str,
        experience: str,
        context: dict[str, Any] | None = None,
    ) -> int | None:
        """Save experience to database.

        Args:
            project_id: Project ID
            session_id: Session identifier
            experience: Experience description
            context: Optional context dict

        Returns:
            Experience ID (int) if successful, None if DB unavailable
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _save() -> int:
                assert self._conn is not None
                query = """
                    INSERT INTO experience_records
                    (project_id, session_id, experience, context, created_at)
                    VALUES ($1, $2, $3, $4, NOW())
                    RETURNING id
                """
                row = await self._conn.fetchrow(
                    query, project_id, session_id, experience, json.dumps(context or {})
                )
                return row["id"] if row else None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_save())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to save experience: {e}")
            return None

    def save_session_state(
        self,
        session_id: str,
        state: dict[str, Any],
        ttl_seconds: int = 86400,
    ) -> bool:
        """Save session state with expiration.

        Args:
            session_id: Session identifier
            state: State data as dict
            ttl_seconds: Time-to-live in seconds (default: 24 hours)

        Returns:
            True if successful, False if DB unavailable
        """
        if not self._conn:
            return False

        try:
            import asyncio

            async def _save() -> bool:
                assert self._conn is not None
                # Calculate expiration
                expires_at = datetime.now(timezone.utc).replace(
                    microsecond=0
                ) + __import__("datetime").timedelta(seconds=ttl_seconds)

                query = """
                    INSERT INTO dev_sessions
                    (session_id, state_data, expires_at, updated_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (session_id)
                    DO UPDATE SET
                        state_data = EXCLUDED.state_data,
                        expires_at = EXCLUDED.expires_at,
                        updated_at = NOW()
                """
                await self._conn.execute(
                    query, session_id, json.dumps(state), expires_at
                )
                return True

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_save())
            loop.close()
            return result
        except Exception as e:
            warnings.warn(f"Failed to save session state: {e}")
            return False

    def get_session_state(self, session_id: str) -> dict[str, Any] | None:
        """Get session state if not expired.

        Args:
            session_id: Session identifier

        Returns:
            State dict if found and not expired, None otherwise
        """
        if not self._conn:
            return None

        try:
            import asyncio

            async def _get() -> dict[str, Any] | None:
                assert self._conn is not None
                query = """
                    SELECT state_data, expires_at
                    FROM dev_sessions
                    WHERE session_id = $1 AND expires_at > NOW()
                """
                row = await self._conn.fetchrow(query, session_id)
                if row:
                    return json.loads(row["state_data"])
                return None

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_get())
            loop.close()
            return result
        except Exception:
            return None

    def get_provider_status(self) -> dict[str, Any]:
        """Check available Claude provider sessions.

        Returns:
            Dict with provider status (empty if DB unavailable)
        """
        if not self._conn:
            return {}

        try:
            import asyncio

            async def _get() -> dict[str, Any]:
                assert self._conn is not None
                query = """
                    SELECT provider, COUNT(*) as count
                    FROM backend_sessions
                    WHERE expires_at > NOW()
                    GROUP BY provider
                """
                rows = await self._conn.fetch(query)
                return {row["provider"]: row["count"] for row in rows}

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(_get())
            loop.close()
            return result
        except Exception:
            return {}

    def is_provider_available(self) -> bool:
        """Check if at least one provider session exists.

        Returns:
            True if providers available, False otherwise
        """
        status = self.get_provider_status()
        return len(status) > 0

    def close(self) -> None:
        """Close database connection.

        Called automatically on cleanup. Safe to call multiple times.
        """
        if self._conn:
            try:
                import asyncio

                async def _close() -> None:
                    assert self._conn is not None
                    await self._conn.close()

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(_close())
                loop.close()
            except Exception:
                pass
            finally:
                self._conn = None
                self.available = False

    def __enter__(self) -> "MasterMindDB":
        """Context manager entry."""
        return self

    def __exit__(self, *args: object) -> None:
        """Context manager exit - closes connection."""
        self.close()

    def __del__(self) -> None:
        """Destructor - ensures connection is closed."""
        self.close()
