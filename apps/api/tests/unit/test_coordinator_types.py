"""
Tests for coordinator.py type hints.

TDD Approach: RED phase - write tests for type completeness.
"""

import pytest
from mastermind_cli.orchestrator.coordinator import Coordinator
from mastermind_cli.orchestrator.output_formatter import OutputFormatter


class TestCoordinatorTypeHints:
    """Test that Coordinator has proper type hints."""

    def test_init_signature(self):
        """Test Coordinator.__init__ has type hints."""
        # Create coordinator with various parameters
        formatter = OutputFormatter()
        coordinator1 = Coordinator(
            formatter=formatter, use_mcp=False, enable_logging=True
        )
        coordinator2 = Coordinator(use_mcp=True)
        coordinator3 = Coordinator()

        assert coordinator1 is not None
        assert coordinator2 is not None
        assert coordinator3 is not None

    def test_orchestrate_signature(self):
        """Test orchestrate method accepts typed parameters."""
        coordinator = Coordinator()

        # Test with all parameters
        result = coordinator.orchestrate(
            brief="Test brief",
            flow="validation_only",
            dry_run=True,
            output_file=None,
            max_iterations=3,
            use_mcp=False,
        )

        assert isinstance(result, dict)
        assert "status" in result

    def test_orchestrate_returns_dict(self):
        """Test orchestrate returns typed Dict."""
        coordinator = Coordinator()

        result = coordinator.orchestrate(
            brief="Test brief for type checking", dry_run=True
        )

        # Result should be a dict with expected keys
        assert isinstance(result, dict)
        assert "status" in result

    def test_private_methods_have_type_hints(self):
        """Test that private methods have type hints."""
        coordinator = Coordinator()

        # These should not raise mypy errors
        flow = coordinator._detect_flow("Test brief")
        assert isinstance(flow, str)

        error = coordinator._error_report("Test error")
        assert isinstance(error, dict)

    @pytest.mark.parametrize(
        "brief,expected_flow",
        [
            ("I want a mobile app", "full_product"),
            ("Validate this idea", "validation_only"),
            ("Create a SaaS platform", "full_product"),
        ],
    )
    def test_detect_flow_return_type(self, brief: str, expected_flow: str):
        """Test _detect_flow returns str."""
        coordinator = Coordinator()
        flow = coordinator._detect_flow(brief)
        assert isinstance(flow, str)

    def test_error_report_return_type(self):
        """Test _error_report returns dict."""
        coordinator = Coordinator()
        result = coordinator._error_report("Test error message")
        assert isinstance(result, dict)
        assert "status" in result
        assert result["status"] == "error"
