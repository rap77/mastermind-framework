"""
Tests for EngramContextLoader context recovery.

Note: These are basic integration tests. Full end-to-end tests would require
Engram API access and actual observations in the database.
"""

import pytest

from context_loader import (
    EngramContextLoader,
    EngramObservation,
    generate_context_for_phase,
)


class TestEngramObservation:
    """Tests for EngramObservation data class."""

    def test_category_ux_design(self):
        """Test categorization of UX/design observations."""
        obs = EngramObservation(
            id=1,
            title="Fix button alignment in header",
            content="Adjusted padding",
            observation_type="bugfix",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "UX/Design"

    def test_category_backend(self):
        """Test categorization of backend observations."""
        obs = EngramObservation(
            id=2,
            title="Refactor API response schema",
            content="Changed structure",
            observation_type="architecture",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "Backend/API"

    def test_category_testing(self):
        """Test categorization of testing observations."""
        obs = EngramObservation(
            id=3,
            title="Fixed test coverage gap",
            content="Added unit tests",
            observation_type="discovery",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "Testing/QA"

    def test_category_security(self):
        """Test categorization of security observations."""
        obs = EngramObservation(
            id=4,
            title="Vulnerability in authentication",
            content="Fixed token expiry",
            observation_type="bugfix",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "Security"

    def test_category_performance(self):
        """Test categorization of performance observations."""
        obs = EngramObservation(
            id=5,
            title="Database query optimization",
            content="Added index",
            observation_type="pattern",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "Performance"

    def test_category_architecture(self):
        """Test categorization of architecture observations."""
        obs = EngramObservation(
            id=6,
            title="Refactored state management pattern",
            content="Changed approach",
            observation_type="decision",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "Architecture"

    def test_category_devops(self):
        """Test categorization of DevOps observations."""
        obs = EngramObservation(
            id=7,
            title="CI/CD pipeline improvement",
            content="Added automatic testing",
            observation_type="pattern",
            project="mastermind",
            scope="project",
        )
        assert obs.category() == "DevOps/Deployment"


class TestEngramContextLoader:
    """Tests for EngramContextLoader."""

    def test_loader_init(self):
        """Test loader initialization."""
        loader = EngramContextLoader(project="mastermind", phase_num=19)
        assert loader.project == "mastermind"
        assert loader.phase_num == 19
        assert loader.phase_str == "19"

    def test_render_context_md_empty(self):
        """Test rendering context when no observations."""
        loader = EngramContextLoader(project="mastermind", phase_num=19)
        loader.observations = []

        md = loader._render_context_md({})

        assert "Phase 19 Context Recovery" in md
        assert "Cross-Phase Contracts" in md
        assert "Phases must not contradict prior decisions" in md

    def test_render_context_md_with_decisions(self):
        """Test rendering context with decisions."""
        loader = EngramContextLoader(project="mastermind", phase_num=19)

        decisions = [
            EngramObservation(
                id=1,
                title="Refactored state management architecture",
                content="**What**: Selected Zustand for state management\n**Why**: Simpler API",
                observation_type="decision",
                project="mastermind",
                scope="project",
                created_at="2026-04-12",
            )
        ]
        loader.observations = decisions

        md = loader._render_context_md(loader._categorize_observations())

        assert "Prior Decisions" in md
        assert "Refactored state management architecture" in md
        # Category should be Architecture (based on keywords in title)
        assert "Architecture" in md or "Decision" in md

    def test_render_context_md_with_warnings(self):
        """Test rendering context with warnings."""
        loader = EngramContextLoader(project="mastermind", phase_num=19)

        warnings = [
            EngramObservation(
                id=2,
                title="Warning: N+1 query issue in user list",
                content="Discovered performance issue during testing",
                observation_type="bugfix",
                project="mastermind",
                scope="project",
                created_at="2026-04-10",
            )
        ]
        loader.observations = warnings

        md = loader._render_context_md(loader._categorize_observations())

        assert "Warnings from History" in md
        assert "⚠️" in md


class TestGenerateContextForPhase:
    """Tests for generate_context_for_phase convenience function."""

    def test_function_signature(self):
        """Test that function accepts correct parameters."""
        # Should not raise
        result = generate_context_for_phase(
            project="mastermind",
            phase_num=99,  # Use a phase with no folder (won't create)
            output_path=None,
        )
        # Will return None because phase 99 doesn't exist, but that's OK
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
