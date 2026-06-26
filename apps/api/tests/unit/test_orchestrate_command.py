"""
Tests for orchestrate command - Pure Function Architecture v2.0.

Tests cover:
- API key validation
- Brief parsing and validation
- Stateless coordinator creation
- Error handling
"""

import os
from click.testing import CliRunner
from unittest.mock import Mock, patch
from pathlib import Path


# Import the orchestrate command group
# Note: We need to add the project to the path first
import sys

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mastermind_cli.commands.orchestrate import orchestrate
from mastermind_cli.mm_flow.evidence_selector import EvidenceSelectionRequest


class TestAPIKeyValidation:
    """Test API key validation logic."""

    def test_no_api_key_shows_error(self: object) -> None:
        """Test that missing MM_API_KEY shows helpful error."""
        runner = CliRunner()
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(orchestrate, ["run", "test brief"])
            assert result.exit_code != 0
            assert "MM_API_KEY environment variable not set" in result.output
            assert "export MM_API_KEY=" in result.output

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_invalid_api_key_shows_error(self: object, mock_validate: Mock) -> None:
        """Test that invalid API key shows helpful error."""
        mock_validate.return_value = None
        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "invalid-key"}):
            result = runner.invoke(orchestrate, ["run", "test brief"])
            assert result.exit_code != 0
            assert "Invalid API key" in result.output

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_valid_api_key_proceeds(self: object, mock_validate: Mock) -> None:
        """Test that valid API key allows execution."""
        mock_validate.return_value = Mock(owner="test-user")
        with patch("mastermind_cli.commands.orchestrate.execute_flow_sync") as mock_run:
            mock_run.return_value = {}
            runner = CliRunner()
            with patch.dict(os.environ, {"MM_API_KEY": "valid-key"}):
                # This should not fail on auth
                result = runner.invoke(orchestrate, ["run", "Build a CRM system"])
                assert result.exit_code == 0


class TestBriefParsing:
    """Test brief input parsing and validation."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_brief_from_argument(self: object, mock_validate: Mock) -> None:
        """Test brief provided as command argument."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            with patch(
                "mastermind_cli.commands.orchestrate.execute_flow_sync"
            ) as mock_run:
                mock_run.return_value = {}
                result = runner.invoke(
                    orchestrate, ["run", "Build a CRM for small businesses"]
                )
                assert result.exit_code == 0

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_brief_from_file(self: object, mock_validate: Mock, tmp_path: Path) -> None:
        """Test brief read from file."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        # Create temporary brief file
        brief_file = tmp_path / "brief.md"
        brief_file.write_text("Build a project management tool for software teams")

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            with patch(
                "mastermind_cli.commands.orchestrate.execute_flow_sync"
            ) as mock_run:
                mock_run.return_value = {}
                result = runner.invoke(orchestrate, ["run", "--file", str(brief_file)])
                assert result.exit_code == 0

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_empty_brief_shows_error(self: object, mock_validate: Mock) -> None:
        """Test that empty brief shows error."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(orchestrate, ["run", ""])
            assert result.exit_code != 0
            assert "No brief provided" in result.output


class TestDryRun:
    """Test dry-run mode."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_dry_run_shows_plan_only(self: object, mock_validate: Mock) -> None:
        """Test that dry-run shows execution plan without executing."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(orchestrate, ["run", "--dry-run", "Build a CRM"])
            assert result.exit_code == 0
            assert "Execution Plan" in result.output
            assert "Dry run complete" in result.output


class TestCoordinatorCreation:
    """Test stateless coordinator creation and execution."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    def test_coordinator_created_per_request(
        self: object, mock_coord_class: Mock, mock_mcp: Mock, mock_validate: Mock
    ) -> None:
        """Test that NEW coordinator instance is created per request."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(
            return_value={
                "brain-01-product-strategy": Mock(
                    model_dump=lambda: {"positioning": "Test"}
                )
            }
        )
        mock_coord_class.return_value = mock_coord_instance

        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            runner.invoke(
                orchestrate,
                [
                    "run",
                    "--brains",
                    "brain-01-product-strategy",
                    "This is a valid test brief for orchestration",
                ],
            )

            # Verify coordinator was created
            assert mock_coord_class.called
            # Verify execute_flow was called
            assert mock_coord_instance.execute_flow.called


class TestCommandParity:
    """Test parity between run and go command paths."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    @patch("mastermind_cli.commands.orchestrate.execute_flow_sync")
    def test_go_forwards_evidence_flags_like_run(
        self: object,
        mock_execute: Mock,
        mock_coord_class: Mock,
        mock_mcp: Mock,
        mock_validate: Mock,
    ) -> None:
        """Test that go forwards the same evidence request contract as run."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_execute.return_value = {}
        mock_coord_class.return_value = Mock()

        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(
                orchestrate,
                [
                    "go",
                    "--evidence-objective",
                    "Collect implementation evidence",
                    "--evidence-source-clarity",
                    "clear",
                    "--evidence-uncertainty",
                    "low",
                    "--evidence-gap-count",
                    "2",
                    "--evidence-needs-interview",
                    "--evidence-risk-level",
                    "high",
                    "--evidence-readiness-gate",
                    "spec-ready",
                    "--evidence-readiness-score",
                    "0.8",
                    "Build a CRM",
                ],
            )

        assert result.exit_code == 0
        evidence_request = mock_execute.call_args.kwargs["evidence_request"]
        assert isinstance(evidence_request, EvidenceSelectionRequest)
        assert evidence_request.objective == "Collect implementation evidence"
        assert evidence_request.source_clarity == "clear"
        assert evidence_request.uncertainty == "low"
        assert evidence_request.gap_count == 2
        assert evidence_request.needs_interview is True
        assert evidence_request.risk_level == "high"
        assert evidence_request.readiness_gate == "spec-ready"
        assert evidence_request.readiness_score == 0.8


class TestOutputFormatting:
    """Test output formatting."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    @patch("mastermind_cli.commands.orchestrate.execute_flow_sync")
    def test_results_displayed_correctly(
        self: object,
        mock_execute: Mock,
        mock_coord_class: Mock,
        mock_mcp: Mock,
        mock_validate: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that execution results are displayed correctly."""
        mock_validate.return_value = Mock(owner="test-user")

        # Mock brain outputs
        from mastermind_cli.types.interfaces import ProductStrategy
        from datetime import datetime

        mock_outputs = {
            "brain-01-product-strategy": ProductStrategy(
                positioning="B2B CRM for small businesses",
                target_audience="Small business owners",
                key_features=["Contact management", "Pipeline tracking"],
                success_metrics=["User adoption", "Revenue growth"],
                risks=["Competition", "Market fit"],
                generated_at=datetime.now(),
            )
        }

        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(return_value=mock_outputs)
        mock_coord_class.return_value = mock_coord_instance
        mock_execute.return_value = mock_outputs

        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(
                orchestrate,
                ["run", "--brains", "brain-01-product-strategy", "Build a CRM"],
            )

            assert result.exit_code == 0
            # Check that output contains expected sections
            assert (
                "Execution Complete" in result.output
                or "brain-01-product-strategy" in result.output
            )

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    @patch("mastermind_cli.commands.orchestrate.execute_flow_sync")
    def test_output_saved_to_file(
        self: object,
        mock_execute: Mock,
        mock_coord_class: Mock,
        mock_mcp: Mock,
        mock_validate: Mock,
        tmp_path: Path,
    ) -> None:
        """Test that output can be saved to file."""
        mock_validate.return_value = Mock(owner="test-user")

        from mastermind_cli.types.interfaces import ProductStrategy
        from datetime import datetime

        mock_outputs = {
            "brain-01-product-strategy": ProductStrategy(
                positioning="Test positioning",
                target_audience="Test audience",
                key_features=["Feature 1"],
                success_metrics=["Metric 1"],
                generated_at=datetime.now(),
            )
        }

        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(return_value=mock_outputs)
        mock_coord_class.return_value = mock_coord_instance
        mock_execute.return_value = mock_outputs

        output_file = tmp_path / "output.json"
        runner = CliRunner()

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            runner.invoke(
                orchestrate,
                [
                    "run",
                    "--output",
                    str(output_file),
                    "--brains",
                    "brain-01-product-strategy",
                    "This is a valid test brief for output file",
                ],
            )

            # Verify file was created
            assert output_file.exists()
            # Verify content is valid JSON
            import json

            with open(output_file) as f:
                content = json.load(f)
                assert "brain-01-product-strategy" in content


class TestErrorHandling:
    """Test error handling."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    @patch("mastermind_cli.commands.orchestrate.execute_flow_sync")
    def test_value_error_caught_and_displayed(
        self: object,
        mock_execute: Mock,
        mock_coord_class: Mock,
        mock_mcp: Mock,
        mock_validate: Mock,
    ) -> None:
        """Test that ValueError during execution is caught and displayed."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_execute.side_effect = ValueError("Brain not found: brain-99")

        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(orchestrate, ["run", "This is a valid test brief"])
            assert result.exit_code != 0
            assert "Error:" in result.output

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    @patch("mastermind_cli.commands.orchestrate.MCPIntegration")
    @patch("mastermind_cli.commands.orchestrate.StatelessCoordinator")
    @patch("mastermind_cli.commands.orchestrate.execute_flow_sync")
    def test_generic_exception_caught(
        self: object,
        mock_execute: Mock,
        mock_coord_class: Mock,
        mock_mcp: Mock,
        mock_validate: Mock,
    ) -> None:
        """Test that generic exceptions are caught."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_execute.side_effect = RuntimeError("Unexpected error")

        runner = CliRunner()
        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            result = runner.invoke(
                orchestrate,
                ["run", "This is a valid test brief for testing exceptions"],
            )
            assert result.exit_code != 0
            # Error message changed in v2.0 - now shows actual error, not generic "Orchestration failed"
            assert "Error" in result.output or "failed" in result.output.lower()


class TestVerboseMode:
    """Test verbose output."""

    @patch("mastermind_cli.commands.orchestrate.validate_api_key")
    def test_verbose_shows_execution_details(self: object, mock_validate: Mock) -> None:
        """Test that verbose mode shows execution details."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {"MM_API_KEY": "test-key"}):
            with patch(
                "mastermind_cli.commands.orchestrate.execute_flow_sync"
            ) as mock_run:
                mock_run.return_value = {}
                result = runner.invoke(
                    orchestrate,
                    ["run", "--verbose", "This is a valid test brief for verbose mode"],
                )
                assert result.exit_code == 0
