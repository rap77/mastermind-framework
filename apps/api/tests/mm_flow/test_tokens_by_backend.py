"""Tests for token tracking by backend — C3.23, C3.27.

C3.23: dev_sessions.metadata includes tokens_by_provider_model (dict)
C3.27: SELECT SUM(tokens_consumed), backend_used FROM dev_sessions GROUP BY backend_used
"""

import json
import pytest
import sys
from pathlib import Path

HANDLER_DIR = Path(__file__).resolve().parents[4] / ".claude" / "commands" / "mm"
sys.path.insert(0, str(HANDLER_DIR))

try:
    from db_client import MasterMindDB
except ImportError:
    pytest.skip("db_client.py not implemented yet", allow_module_level=True)


class TestTokensByBackend:
    """C3.23, C3.27: Token tracking by provider/model."""

    def _skip_if_db_unavailable(self, db: MasterMindDB) -> None:
        if not db.available:
            pytest.skip("PostgreSQL not available — skipping integration test")

    def test_update_session_stores_tokens_consumed(self) -> None:
        """update_session stores tokens_consumed in the database."""
        db = MasterMindDB()
        self._skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            backend_used="anthropic",
            task_id="C3",
        )
        assert session_id is not None

        success = db.update_session(
            session_id=session_id,
            tokens_consumed=8500,
            status="completed",
        )
        assert success is True

        with db._conn.cursor() as cur:
            cur.execute(
                "SELECT tokens_consumed FROM dev_sessions WHERE id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] == 8500

    def test_tokens_by_provider_model_in_metadata(self) -> None:
        """C3.23: tokens_by_provider_model dict is stored in metadata."""
        db = MasterMindDB()
        self._skip_if_db_unavailable(db)

        session_id = db.save_session(
            started_by="task-executor",
            backend_used="anthropic",
            task_id="C3",
            metadata={
                "tokens_by_provider_model": {
                    "anthropic:claude-sonnet-4-6": 8500,
                    "openrouter:claude-opus": 0,
                },
            },
        )
        assert session_id is not None

        with db._conn.cursor() as cur:
            cur.execute(
                "SELECT metadata FROM dev_sessions WHERE id = %s",
                (session_id,),
            )
            row = cur.fetchone()
            assert row is not None
            meta = row[0] if isinstance(row[0], dict) else json.loads(row[0])
            tokens_map = meta.get("tokens_by_provider_model", {})
            assert "anthropic:claude-sonnet-4-6" in tokens_map
            assert tokens_map["anthropic:claude-sonnet-4-6"] == 8500

    def test_group_by_backend_query_works(self) -> None:
        """C3.27: SELECT SUM(tokens_consumed), backend_used GROUP BY backend_used."""
        db = MasterMindDB()
        self._skip_if_db_unavailable(db)

        # Create two sessions with different backends
        s1 = db.save_session(
            started_by="task-executor",
            backend_used="anthropic",
            task_id="C3",
        )
        s2 = db.save_session(
            started_by="task-executor",
            backend_used="openrouter",
            task_id="C3",
        )

        if s1:
            db.update_session(session_id=s1, tokens_consumed=5000, status="completed")
        if s2:
            db.update_session(session_id=s2, tokens_consumed=3000, status="completed")

        # C3.27: GROUP BY query
        with db._conn.cursor() as cur:
            cur.execute(
                """
                SELECT SUM(tokens_consumed), backend_used
                FROM dev_sessions
                WHERE id IN (%s, %s)
                GROUP BY backend_used
                ORDER BY backend_used
                """,
                (s1, s2),
            )
            rows = cur.fetchall()
            assert len(rows) == 2

            by_backend = {row[1]: row[0] for row in rows}
            assert by_backend.get("anthropic", 0) >= 5000
            assert by_backend.get("openrouter", 0) >= 3000
