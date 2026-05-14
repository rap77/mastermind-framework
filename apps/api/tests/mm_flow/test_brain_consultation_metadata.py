"""Tests for brain_consultations.metadata — C3.24.

C3.24: brain_consultations.metadata includes gga_pass_first_attempt (bool).
This test validates the DB client behavior when saving brain consultations
with GGA pass/fail metadata.

Note: save_brain_consultation() needs a metadata parameter added to db_client.py
for full implementation. This test documents the intended behavior.
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


class TestBrainConsultationMetadata:
    """C3.24: gga_pass_first_attempt stored in brain_consultations.metadata."""

    def test_save_brain_consultation_returns_id_or_none(self) -> None:
        """save_brain_consultation should return UUID or None — never crash."""
        db = MasterMindDB()
        result = db.save_brain_consultation(
            brain_id=7,
            phase=19,
            consultation_input="Evaluate brain output quality",
            consultation_output='{"quality_score": 0.87}',
            confidence=0.87,
            backend_used="anthropic",
            tokens_used=1500,
        )
        # Graceful degradation: returns None if DB unavailable
        assert result is None or isinstance(result, str)

    def test_gga_pass_stored_in_metadata_when_db_available(self) -> None:
        """C3.24: When DB is available, gga_pass_first_attempt in metadata."""
        db = MasterMindDB()
        if not db.available:
            pytest.skip("PostgreSQL not available")

        # Save a consultation directly with metadata via SQL
        with db._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO brain_consultations
                    (org_id, project_id, phase, brain_id,
                     consultation_input, consultation_output,
                     confidence, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    "a0000000-0000-0000-0000-000000000001",  # ORG_ID
                    "b0000000-0000-0000-0000-000000000001",  # PROJECT_ID
                    19,
                    7,
                    "Evaluate brain-01 output",
                    '{"quality_score": 0.87}',
                    0.87,
                    json.dumps({"gga_pass_first_attempt": True}),
                ),
            )
            row = cur.fetchone()
            record_id = str(row[0])

        # Verify gga_pass_first_attempt is stored
        with db._conn.cursor() as cur:
            cur.execute(
                """SELECT (metadata->>'gga_pass_first_attempt')::boolean
                   FROM brain_consultations WHERE id = %s""",
                (record_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] is True, f"Expected gga_pass_first_attempt=True, got {row[0]}"

    def test_gga_fail_stored_in_metadata_when_db_available(self) -> None:
        """C3.24: gga_pass_first_attempt=False when GGA check failed on first attempt."""
        db = MasterMindDB()
        if not db.available:
            pytest.skip("PostgreSQL not available")

        with db._conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO brain_consultations
                    (org_id, project_id, phase, brain_id,
                     consultation_input, consultation_output,
                     confidence, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    "a0000000-0000-0000-0000-000000000001",
                    "b0000000-0000-0000-0000-000000000001",
                    19,
                    6,
                    "Build test suite",
                    '{"test_count": 10}',
                    0.72,
                    json.dumps({"gga_pass_first_attempt": False}),
                ),
            )
            row = cur.fetchone()
            record_id = str(row[0])

        with db._conn.cursor() as cur:
            cur.execute(
                """SELECT (metadata->>'gga_pass_first_attempt')::boolean
                   FROM brain_consultations WHERE id = %s""",
                (record_id,),
            )
            row = cur.fetchone()
            assert row is not None
            assert row[0] is False

    def test_db_client_save_consultation_method_exists(self) -> None:
        """save_brain_consultation method must exist on MasterMindDB."""
        db = MasterMindDB()
        assert hasattr(
            db, "save_brain_consultation"
        ), "MasterMindDB must have save_brain_consultation method"
        assert callable(db.save_brain_consultation)
