"""MasterMind DB Client — shared PostgreSQL client for all handlers.

Graceful degradation: if psycopg2 or PostgreSQL is unavailable,
all methods return None/False without crashing handlers.

Usage:
    from db_client import MasterMindDB
    db = MasterMindDB()
    if db.available:
        project_id = db.register_project("my-app")
"""

from __future__ import annotations

import json
import os
import warnings
from typing import Any

try:
    import psycopg2
    import psycopg2.extras

    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None  # type: ignore[assignment]

# Seeded IDs — deterministic UUIDs created at DB setup time
ORG_ID = "a0000000-0000-0000-0000-000000000001"
PROJECT_ID = "b0000000-0000-0000-0000-000000000001"

_DB_CONFIG = {
    "host": os.getenv("MM_DB_HOST", "localhost"),
    "port": int(os.getenv("MM_DB_PORT", "5433")),
    "dbname": os.getenv("MM_DB_NAME", "mastermind_bd"),
    "user": os.getenv("MM_DB_USER", "postgres"),
    "password": os.getenv("MM_DB_PASSWORD", "devpassword"),
    "connect_timeout": 5,
}


class MasterMindDB:
    """Synchronous PostgreSQL client for MasterMind handlers.

    Connects once in __init__. All methods are synchronous (psycopg2).
    Thread-safe for read operations; handlers are single-threaded so this is fine.
    """

    def __init__(self) -> None:
        self._conn: Any = None
        self.available = False
        self._connect()

    def _connect(self) -> None:
        if not PSYCOPG2_AVAILABLE:
            warnings.warn("psycopg2 not installed — database operations disabled")
            return
        try:
            assert psycopg2 is not None
            self._conn = psycopg2.connect(**_DB_CONFIG)
            self._conn.autocommit = True
            self.available = True
        except Exception as e:
            warnings.warn(f"PostgreSQL connection failed: {e}")

    def ping(self) -> bool:
        if not self._conn:
            return False
        try:
            with self._conn.cursor() as cur:
                cur.execute("SELECT 1")
            return True
        except Exception:
            self.available = False
            self._conn = None
            self._connect()
            return False

    # ------------------------------------------------------------------ #
    # Phase B — /mm:init
    # ------------------------------------------------------------------ #

    def register_project(
        self, name: str, metadata: dict[str, Any] | None = None
    ) -> str | None:
        """Register or update project. Returns project UUID string, or None."""
        if not self._conn:
            return None
        try:
            slug = name.lower().replace(" ", "-").replace("/", "-")[:100]
            meta_json = json.dumps(metadata or {})
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO projects (org_id, slug, name, project_type, metadata)
                    VALUES (%s, %s, %s, 'software', %s)
                    ON CONFLICT (org_id, slug)
                    DO UPDATE SET name = EXCLUDED.name, metadata = EXCLUDED.metadata,
                                  updated_at = NOW()
                    RETURNING id
                    """,
                    (ORG_ID, slug, name, meta_json),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"register_project failed: {e}")
            return None

    def get_project(self, name: str) -> dict[str, Any] | None:
        """Get project by name. Returns dict or None."""
        if not self._conn:
            return None
        try:
            assert psycopg2 is not None
            with self._conn.cursor(
                cursor_factory=psycopg2.extras.RealDictCursor
            ) as cur:
                slug = name.lower().replace(" ", "-").replace("/", "-")[:100]
                cur.execute(
                    "SELECT id, org_id, slug, name, metadata FROM projects "
                    "WHERE org_id = %s AND (name = %s OR slug = %s)",
                    (ORG_ID, name, slug),
                )
                row = cur.fetchone()
                return dict(row) if row else None
        except Exception as e:
            warnings.warn(f"get_project failed: {e}")
            return None

    def get_provider_status(self) -> dict[str, int]:
        """Return {backend_name: session_count} for active sessions."""
        if not self._conn:
            return {}
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT backend, COUNT(*)::int
                    FROM backend_sessions
                    WHERE is_active = TRUE
                    GROUP BY backend
                    """
                )
                return {row[0]: row[1] for row in cur.fetchall()}
        except Exception as e:
            warnings.warn(f"get_provider_status failed: {e}")
            return {}

    def is_provider_available(self) -> bool:
        """True if at least one active backend session exists.
        Fails open (returns True) when DB is unavailable so init is not blocked.
        """
        if not self._conn:
            warnings.warn("DB unavailable — assuming provider available (fail-open)")
            return True
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    "SELECT EXISTS(SELECT 1 FROM backend_sessions WHERE is_active = TRUE)"
                )
                row = cur.fetchone()
                return bool(row[0]) if row else False
        except Exception:
            return True

    # ------------------------------------------------------------------ #
    # Phase C — /mm:review
    # ------------------------------------------------------------------ #

    def save_brain_consultation(
        self,
        brain_id: int,
        phase: int,
        consultation_input: str,
        consultation_output: str,
        confidence: float = 0.0,
        backend_used: str | None = None,
        tokens_used: int = 0,
        project_id: str | None = None,
    ) -> str | None:
        """Save brain consultation. Returns UUID string or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO brain_consultations
                        (org_id, project_id, phase, brain_id,
                         consultation_input, consultation_output,
                         confidence, backend_used, tokens_used)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        phase,
                        brain_id,
                        consultation_input,
                        consultation_output,
                        confidence,
                        backend_used,
                        tokens_used,
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_brain_consultation failed: {e}")
            return None

    def save_artifact(
        self,
        artifact_type: str,
        name: str,
        description: str | None = None,
        file_path: str | None = None,
        git_commit_hash: str | None = None,
        git_commit_message: str | None = None,
        created_by: str | None = None,
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> str | None:
        """Save artifact reference. Returns UUID string or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO artifacts
                        (org_id, project_id, artifact_type, name,
                         description, file_path, git_commit_hash,
                         git_commit_message, created_by, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        artifact_type,
                        name,
                        description,
                        file_path,
                        git_commit_hash,
                        git_commit_message,
                        created_by,
                        json.dumps(metadata or {}),
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_artifact failed: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Phase D — /mm:ship
    # ------------------------------------------------------------------ #

    def save_decision(
        self,
        decision_type: str,
        title: str,
        rationale: str,
        chosen_option: str,
        made_by: str,
        alternatives: str | None = None,
        impact_level: str = "medium",
        impact_description: str | None = None,
        confidence: float = 0.5,
        tags: list[str] | None = None,
        project_id: str | None = None,
    ) -> str | None:
        """Save technical decision. Returns UUID string or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO decisions
                        (org_id, project_id, decision_type, title, rationale,
                         chosen_option, made_by, alternatives,
                         impact_level, impact_description, confidence, tags)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        decision_type,
                        title,
                        rationale,
                        chosen_option,
                        made_by,
                        alternatives,
                        impact_level,
                        impact_description,
                        confidence,
                        tags,
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_decision failed: {e}")
            return None

    def save_session(
        self,
        started_by: str,
        phase_number: int | None = None,
        backend_used: str | None = None,
        project_id: str | None = None,
    ) -> str | None:
        """Open a new dev session. Returns session UUID string or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO dev_sessions
                        (org_id, project_id, started_by, phase_number, backend_used)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        started_by,
                        phase_number,
                        backend_used,
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_session failed: {e}")
            return None

    def update_session(
        self,
        session_id: str,
        status: str = "completed",
        tasks_completed: int = 0,
        tasks_total: int = 0,
        commits_count: int = 0,
        discoveries: str | None = None,
        next_steps: str | None = None,
    ) -> bool:
        """Close/update an existing dev session. Returns True on success."""
        if not self._conn:
            return False
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE dev_sessions
                    SET status = %s, ended_at = NOW(), tasks_completed = %s,
                        tasks_total = %s, commits_count = %s,
                        discoveries = %s, next_steps = %s, updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        status,
                        tasks_completed,
                        tasks_total,
                        commits_count,
                        discoveries,
                        next_steps,
                        session_id,
                    ),
                )
                return cur.rowcount > 0
        except Exception as e:
            warnings.warn(f"update_session failed: {e}")
            return False

    def save_experience(
        self,
        brain_id: str,
        session_id: str,
        quality_score: float | None = None,
        insights: list[Any] | None = None,
        patterns: list[Any] | None = None,
    ) -> str | None:
        """Save brain experience record. Returns UUID string or None.

        brain_id: string identifier e.g. 'brain-01-product'
        session_id: UUID of the dev_session this experience belongs to
        """
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO experience_records
                        (brain_id, session_id, quality_score, insights, patterns)
                    VALUES (%s, %s::uuid, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        brain_id,
                        session_id,
                        quality_score,
                        json.dumps(insights or []),
                        json.dumps(patterns or []),
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_experience failed: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Brain Feedback, Checkpoints, Audit
    # ------------------------------------------------------------------ #

    def save_brain_feedback(
        self,
        brain_id: int,
        feedback_type: str,
        title: str,
        content: str,
        confidence: float | None = None,
        impact_on_phase: str | None = None,
        engram_sync_id: str | None = None,
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> str | None:
        """Save brain feedback (insight, risk, lesson, recommendation). Returns UUID or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO brain_feedback
                        (org_id, project_id, brain_id, feedback_type, title, content,
                         confidence, impact_on_phase, engram_sync_id, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        brain_id,
                        feedback_type,
                        title,
                        content,
                        confidence,
                        impact_on_phase,
                        engram_sync_id,
                        json.dumps(metadata or {}),
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_brain_feedback failed: {e}")
            return None

    def save_context_checkpoint(
        self,
        phase: int,
        reason: str,
        workspace_id: str,
        state_data: dict[str, Any] | None = None,
        from_backend: str | None = None,
        to_backend: str | None = None,
        tokens_at_checkpoint: int = 0,
        project_id: str | None = None,
    ) -> str | None:
        """Save context checkpoint (before backend switch or context limit). Returns UUID or None.

        workspace_id is required (FK to workspaces table — NOT NULL constraint).
        """
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO context_checkpoints
                        (org_id, project_id, workspace_id, phase, reason,
                         state_data, from_backend, to_backend, tokens_at_checkpoint)
                    VALUES (%s, %s, %s::uuid, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        workspace_id,
                        phase,
                        reason,
                        json.dumps(state_data or {}),
                        from_backend,
                        to_backend,
                        tokens_at_checkpoint,
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_context_checkpoint failed: {e}")
            return None

    def save_audit_log(
        self,
        action_type: str,
        actor: str,
        description: str,
        actor_type: str = "system",
        phase_number: int | None = None,
        related_entity_type: str | None = None,
        related_entity_id: str | None = None,
        severity: str = "info",
        metadata: dict[str, Any] | None = None,
        project_id: str | None = None,
    ) -> str | None:
        """Save audit log entry. Returns UUID or None."""
        if not self._conn:
            return None
        try:
            with self._conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO audit_log
                        (org_id, project_id, action_type, actor, actor_type, description,
                         phase_number, related_entity_type, related_entity_id, severity, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid, %s, %s)
                    RETURNING id
                    """,
                    (
                        ORG_ID,
                        project_id or PROJECT_ID,
                        action_type,
                        actor,
                        actor_type,
                        description,
                        phase_number,
                        related_entity_type,
                        related_entity_id,
                        severity,
                        json.dumps(metadata or {}),
                    ),
                )
                row = cur.fetchone()
                return str(row[0]) if row else None
        except Exception as e:
            warnings.warn(f"save_audit_log failed: {e}")
            return None

    # ------------------------------------------------------------------ #
    # Lifecycle
    # ------------------------------------------------------------------ #

    def close(self) -> None:
        if self._conn:
            try:
                self._conn.close()
            except Exception:
                pass
            finally:
                self._conn = None
                self.available = False

    def __enter__(self) -> MasterMindDB:
        return self

    def __exit__(self, *_args: object) -> None:
        self.close()
