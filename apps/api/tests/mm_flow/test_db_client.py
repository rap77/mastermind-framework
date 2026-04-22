"""
Tests for MasterMind DB Client — shared PostgreSQL client for handlers.

These tests use TDD methodology:
1. Test database connection (graceful degradation)
2. Test project registration
3. Test brain consultation saving
4. Test artifact and decision saving
5. Test experience saving
6. Test session state management
7. Test provider status checking
"""

import pytest
import sys
from pathlib import Path

# Add db_client to path (go up to repo root)
handler_dir = Path(__file__).resolve().parents[4] / ".claude" / "commands" / "mm"
sys.path.insert(0, str(handler_dir))

try:
    from db_client import MasterMindDB
except ImportError:
    pytest.skip("db_client.py not implemented yet", allow_module_level=True)


class TestMasterMindDBConnection:
    """Test database connection and graceful degradation."""

    def test_ping_returns_bool(self):
        """ping() should return boolean (True if DB up, False if down)."""
        db = MasterMindDB()
        assert isinstance(db.ping(), bool)

    def test_connection_graceful_degradation(self):
        """If PostgreSQL is down, available should be False (no crash)."""
        db = MasterMindDB()
        # Should not raise exception even if DB is down
        assert isinstance(db.available, bool)

    def test_db_attributes(self):
        """Database connection attributes should be set correctly."""
        db = MasterMindDB()
        assert db.host == "localhost"
        assert db.port == 5433
        assert db.database == "mastermind_bd"


class TestProjectOperations:
    """Test project table operations."""

    def test_register_project_returns_id_or_none(self):
        """register_project should return project_id (int) or None if DB down."""
        db = MasterMindDB()
        result = db.register_project(
            name="test-project", path="/tmp/test-project", stack=["nextjs", "python"]
        )
        # Should return int or None (never crash)
        assert result is None or isinstance(result, int)

    def test_get_project_returns_dict_or_none(self):
        """get_project should return project dict or None."""
        db = MasterMindDB()
        result = db.get_project(path="/tmp/test-project")
        # Should return dict or None (never crash)
        assert result is None or isinstance(result, dict)


class TestBrainConsultations:
    """Test brain consultation saving."""

    def test_save_brain_consultation_returns_id_or_none(self):
        """save_brain_consultation should return consultation_id or None."""
        db = MasterMindDB()
        result = db.save_brain_consultation(
            brain_id="brain-01-product",
            input_data={"brief": "test brief"},
            output_data={"response": "test response"},
            confidence=0.8,
        )
        # Should return int or None (never crash)
        assert result is None or isinstance(result, int)


class TestArtifactsAndDecisions:
    """Test artifact and decision saving."""

    def test_save_artifact_returns_id_or_none(self):
        """save_artifact should return artifact_id or None."""
        db = MasterMindDB()
        result = db.save_artifact(
            project_id=1,
            artifact_type="spec",
            content={"title": "Test Spec"},
            metadata={"version": "1.0"},
        )
        # Should return int or None (never crash)
        assert result is None or isinstance(result, int)

    def test_save_decision_returns_id_or_none(self):
        """save_decision should return decision_id or None."""
        db = MasterMindDB()
        result = db.save_decision(
            project_id=1,
            decision="Use Next.js for frontend",
            rationale="Best performance and DX",
            impact="High",
        )
        # Should return int or None (never crash)
        assert result is None or isinstance(result, int)


class TestExperiences:
    """Test experience saving."""

    def test_save_experience_returns_id_or_none(self):
        """save_experience should return experience_id or None."""
        db = MasterMindDB()
        result = db.save_experience(
            project_id=1,
            session_id="sess-test-123",
            experience="Brain #1 recommended pivot",
            context={"phase": "discovery"},
        )
        # Should return int or None (never crash)
        assert result is None or isinstance(result, int)


class TestSessionState:
    """Test session state management."""

    def test_save_session_state_returns_bool(self):
        """save_session_state should return boolean."""
        db = MasterMindDB()
        result = db.save_session_state(
            session_id="sess-test-123",
            state={"current_phase": 1, "status": "running"},
            ttl_seconds=3600,
        )
        # Should return bool (never crash)
        assert isinstance(result, bool)

    def test_get_session_state_returns_dict_or_none(self):
        """get_session_state should return state dict or None."""
        db = MasterMindDB()
        result = db.get_session_state(session_id="sess-test-123")
        # Should return dict or None (never crash)
        assert result is None or isinstance(result, dict)


class TestProviderStatus:
    """Test provider status checking."""

    def test_get_provider_status_returns_dict(self):
        """get_provider_status should return dict (empty if DB down)."""
        db = MasterMindDB()
        result = db.get_provider_status()
        # Should return dict (never crash)
        assert isinstance(result, dict)

    def test_is_provider_available_returns_bool(self):
        """is_provider_available should return boolean."""
        db = MasterMindDB()
        result = db.is_provider_available()
        # Should return bool (never crash)
        assert isinstance(result, bool)
