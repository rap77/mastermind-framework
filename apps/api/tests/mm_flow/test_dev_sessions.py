"""Tests for dev_sessions DB operations — C3.13, C3.14, C3.18, C3.20.

Tests:
- C3.13: complete-task-handler opens dev_session with task_id + backend_used + started_at
- C3.14: complete-task-handler closes dev_session with tokens_consumed + commit_hashes + ended_at
- C3.18: SELECT dev_sessions has task_id + commit_hashes
- C3.20: SELECT COUNT(*) FROM dev_sessions > 0 after first /mm:complete-task

These tests use MasterMindDB with graceful degradation (skip if DB unavailable).
"""

import json
import pytest
import sys
from pathlib import Path

# ─── Path setup ───────────────────────────────────────────────────────────────
HANDLER_DIR = Path(__file__).resolve().parents[4] / ".claude" / "commands" / "mm"
sys.path.insert(0, str(HANDLER_DIR))

try:
    from db_client import MasterMindDB
except ImportError:
    pytest.skip("db_client.py not implemented yet", allow_module_level=True)


def _skip_if_db_unavailable(db: MasterMindDB) -> None:
    """Skip test if PostgreSQL is not available."""
    if not db.available:
        pytest.skip("PostgreSQL not available — skipping integration test")


class TestDevSessionsC313:
    """C3.13: save_session now supports task_id in metadata."""

    def test_save_session_with_task_id_in_metadata(self) -> None:
        """save_session stores task_id in metadata JSONB column."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            phase_number=19,
            backend_used="anthropic",
            task_id="C3",
            tasks_total=27,
            metadata={
                "context_budget_exits": 0,
                "tokens_by_provider_model": {},
            },
        )
        assert session_id is not None, "save_session should return UUID"

        # Verify task_id is in metadata
        with db._conn.cursor() as cur:
            cur.execute(
                "SELECT metadata->>'task_id' FROM dev_sessions WHERE id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == "C3", f"Expected task_id='C3' but got '{row[0]}'"

    def test_save_session_without_task_id_doesnt_crash(self) -> None:
        """save_session without task_id still works (backward compat)."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            phase_number=19,
        )
        assert session_id is not None or db.available is False

    def test_save_session_metadata_includes_context_budget_exits(self) -> None:
        """C3.22: metadata.context_budget_exits is stored."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            task_id="C3",
            metadata={
                "context_budget_exits": 2,
                "tokens_by_provider_model": {"anthropic:claude-sonnet-4-6": 15000},
            },
        )
        assert session_id is not None

        with db._conn.cursor() as cur:
            cur.execute(
                """SELECT (metadata->>'context_budget_exits')::int
                   FROM dev_sessions WHERE id = %s""",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 2


class TestDevSessionsC314:
    """C3.14: update_session now supports commit_hashes + tokens_consumed + metadata."""

    def test_update_session_with_commit_hashes(self) -> None:
        """update_session stores commit_hashes[] in dev_sessions."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            task_id="C3",
        )
        assert session_id is not None

        commit_hashes = ["abc1234", "def5678", "ghi9012"]
        success = db.update_session(
            session_id=session_id,
            status="completed",
            tasks_completed=3,
            tasks_total=27,
            commits_count=3,
            tokens_consumed=12500,
            commit_hashes=commit_hashes,
            metadata={"context_budget_exits": 0},
        )
        assert success is True

        # C3.18: Verify commit_hashes populated
        with db._conn.cursor() as cur:
            cur.execute(
                "SELECT commit_hashes, tokens_consumed FROM dev_sessions WHERE id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == commit_hashes, f"commit_hashes mismatch: {row[0]}"
            assert row[1] == 12500, f"tokens_consumed mismatch: {row[1]}"

    def test_update_session_merges_metadata(self) -> None:
        """update_session merges new metadata with existing (JSONB || operator)."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            task_id="C3",
            metadata={"context_budget_exits": 1},
        )
        assert session_id is not None

        # Update with additional metadata
        db.update_session(
            session_id=session_id,
            metadata={
                "tokens_by_provider_model": {"anthropic:claude-sonnet-4-6": 8000}
            },
        )

        with db._conn.cursor() as cur:
            cur.execute(
                "SELECT metadata FROM dev_sessions WHERE id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            meta = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            # Both original and new metadata should be present
            assert "context_budget_exits" in meta, "Original metadata key lost"
            assert "tokens_by_provider_model" in meta, "New metadata key missing"


class TestDevSessionsC320:
    """C3.20: SELECT COUNT(*) FROM dev_sessions > 0 after first /mm:complete-task."""

    def test_dev_sessions_count_positive_after_save(self) -> None:
        """After save_session(), COUNT(*) FROM dev_sessions > 0."""
        db = MasterMindDB()
        _skip_if_db_unavailable(db)

        # Create at least one session
        session_id = db.save_session(
            started_by="task-executor",
            task_id="C3",
        )
        assert session_id is not None

        with db._conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM dev_sessions")
            row = cur.fetchone()
            assert row is not None
            count = int(row[0])
            assert count > 0, f"Expected > 0 dev_sessions, got {count}"
