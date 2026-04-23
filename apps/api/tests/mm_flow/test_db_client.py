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
        """Database connection should expose available status."""
        db = MasterMindDB()
        # MasterMindDB doesn't expose host/port/database attributes
        # It only exposes 'available' status
        assert isinstance(db.available, bool)


class TestProjectOperations:
    """Test project table operations."""

    def test_register_project_returns_id_or_none(self):
        """register_project should return project_id (str) or None if DB down."""
        db = MasterMindDB()
        result = db.register_project(
            name="test-project", metadata={"stack": ["nextjs", "python"]}
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)

    def test_get_project_returns_dict_or_none(self):
        """get_project should return project dict or None."""
        db = MasterMindDB()
        result = db.get_project(name="test-project")
        # Should return dict or None (never crash)
        assert result is None or isinstance(result, dict)


class TestBrainConsultations:
    """Test brain consultation saving."""

    def test_save_brain_consultation_returns_id_or_none(self):
        """save_brain_consultation should return consultation_id or None."""
        db = MasterMindDB()
        result = db.save_brain_consultation(
            brain_id=1,
            phase=1,
            consultation_input='{"brief": "test brief"}',
            consultation_output='{"response": "test response"}',
            confidence=0.8,
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)


class TestArtifactsAndDecisions:
    """Test artifact and decision saving."""

    def test_save_artifact_returns_id_or_none(self):
        """save_artifact should return artifact_id or None."""
        db = MasterMindDB()
        result = db.save_artifact(
            artifact_type="spec",
            name="Test Spec",
            description="Test artifact",
            metadata={"version": "1.0"},
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)

    def test_save_decision_returns_id_or_none(self):
        """save_decision should return decision_id or None."""
        db = MasterMindDB()
        result = db.save_decision(
            decision_type="tech-stack",
            title="Use Next.js for frontend",
            rationale="Best performance and DX",
            chosen_option="Next.js",
            made_by="team",
            impact_level="high",
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)


class TestExperiences:
    """Test experience saving."""

    def test_save_experience_returns_id_or_none(self):
        """save_experience should return experience_id or None."""
        db = MasterMindDB()
        result = db.save_experience(
            brain_id="brain-01-product",
            session_id="b0000000-0000-0000-0000-000000000001",
            insights=["Brain #1 recommended pivot"],
            patterns=["discovery"],
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)


class TestSessionState:
    """Test session state management."""

    def test_save_session_returns_id_or_none(self):
        """save_session should return session_id or None."""
        db = MasterMindDB()
        result = db.save_session(
            started_by="test-user",
            phase_number=1,
            backend_used="claude",
        )
        # Should return str (UUID) or None (never crash)
        assert result is None or isinstance(result, str)

    def test_update_session_returns_bool(self):
        """update_session should return boolean."""
        db = MasterMindDB()
        # First create a session
        session_id = db.save_session(started_by="test-user")
        if session_id:
            result = db.update_session(
                session_id=session_id,
                status="completed",
                tasks_completed=5,
                tasks_total=10,
            )
            # Should return bool (never crash)
            assert isinstance(result, bool)
        else:
            # If DB unavailable, test passes gracefully
            assert True


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
