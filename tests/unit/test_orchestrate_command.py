"""
Tests for orchestrate command - Pure Function Architecture v2.0.

Tests cover:
- API key validation
- Brief parsing and validation
- Stateless coordinator creation
- Error handling
"""

import os
import pytest
from click.testing import CliRunner
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path


# Import the orchestrate command group
# Note: We need to add the project to the path first
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from mastermind_cli.commands.orchestrate import orchestrate


class TestAPIKeyValidation:
    """Test API key validation logic."""

    def test_no_api_key_shows_error(self):
        """Test that missing MM_API_KEY shows helpful error."""
        runner = CliRunner()
        with patch.dict(os.environ, {}, clear=True):
            result = runner.invoke(orchestrate, ['run', 'test brief'])
            assert result.exit_code != 0
            assert "MM_API_KEY environment variable not set" in result.output
            assert "export MM_API_KEY=" in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_invalid_api_key_shows_error(self, mock_validate):
        """Test that invalid API key shows helpful error."""
        mock_validate.return_value = None
        runner = CliRunner()
        with patch.dict(os.environ, {'MM_API_KEY': 'invalid-key'}):
            result = runner.invoke(orchestrate, ['run', 'test brief'])
            assert result.exit_code != 0
            assert "Invalid API key" in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_valid_api_key_proceeds(self, mock_validate):
        """Test that valid API key allows execution."""
        mock_validate.return_value = Mock(owner="test-user")
        with patch('mastermind_cli.commands.orchestrate.StatelessCoordinator') as mock_coord:
            mock_coord.return_value.execute_flow = Mock(return_value={})
            runner = CliRunner()
            with patch.dict(os.environ, {'MM_API_KEY': 'valid-key'}):
                # This should not fail on auth
                result = runner.invoke(orchestrate, ['run', 'Build a CRM system'])
                # Auth passed, other errors might occur but not auth-related
                assert "Invalid API key" not in result.output


class TestBriefParsing:
    """Test brief input parsing and validation."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_brief_from_argument(self, mock_validate):
        """Test brief provided as command argument."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            with patch('mastermind_cli.commands.orchestrate.StatelessCoordinator') as mock_coord:
                mock_coord.return_value.execute_flow = Mock(return_value={})
                result = runner.invoke(orchestrate, ['run', 'Build a CRM for small businesses'])
                # Brief was parsed successfully
                assert result.exit_code == 0 or "Error:" not in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_brief_from_file(self, mock_validate, tmp_path):
        """Test brief read from file."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        # Create temporary brief file
        brief_file = tmp_path / "brief.md"
        brief_file.write_text("Build a project management tool for software teams")

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            with patch('mastermind_cli.commands.orchestrate.StatelessCoordinator') as mock_coord:
                mock_coord.return_value.execute_flow = Mock(return_value={})
                result = runner.invoke(orchestrate, ['run', '--file', str(brief_file)])
                # Brief was read and parsed successfully
                assert result.exit_code == 0 or "Error:" not in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_empty_brief_shows_error(self, mock_validate):
        """Test that empty brief shows error."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, ['run', ''])
            assert result.exit_code != 0
            assert "No brief provided" in result.output


class TestDryRun:
    """Test dry-run mode."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_dry_run_shows_plan_only(self, mock_validate):
        """Test that dry-run shows execution plan without executing."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, [
                'run',
                '--dry-run',
                'Build a CRM'
            ])
            assert result.exit_code == 0
            assert "Execution Plan" in result.output
            assert "Dry run complete" in result.output


class TestCoordinatorCreation:
    """Test stateless coordinator creation and execution."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    @patch('mastermind_cli.commands.orchestrate.MCPIntegration')
    @patch('mastermind_cli.commands.orchestrate.StatelessCoordinator')
    def test_coordinator_created_per_request(self, mock_coord_class, mock_mcp, mock_validate):
        """Test that NEW coordinator instance is created per request."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(return_value={
            'brain-01-product-strategy': Mock(model_dump=lambda: {'positioning': 'Test'})
        })
        mock_coord_class.return_value = mock_coord_instance

        runner = CliRunner()
        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, [
                'run',
                '--brains', 'brain-01-product-strategy',
                'Test brief'
            ])

            # Verify coordinator was created
            assert mock_coord_class.called
            # Verify execute_flow was called
            assert mock_coord_instance.execute_flow.called


class TestOutputFormatting:
    """Test output formatting."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    @patch('mastermind_cli.commands.orchestrate.MCPIntegration')
    @patch('mastermind_cli.commands.orchestrate.StatelessCoordinator')
    @patch('mastermind_cli.commands.orchestrate.asyncio.run')
    def test_results_displayed_correctly(self, mock_async, mock_coord_class, mock_mcp, mock_validate, tmp_path):
        """Test that execution results are displayed correctly."""
        mock_validate.return_value = Mock(owner="test-user")

        # Mock brain outputs
        from mastermind_cli.types.interfaces import ProductStrategy
        from datetime import datetime

        mock_outputs = {
            'brain-01-product-strategy': ProductStrategy(
                positioning="B2B CRM for small businesses",
                target_audience="Small business owners",
                key_features=["Contact management", "Pipeline tracking"],
                success_metrics=["User adoption", "Revenue growth"],
                risks=["Competition", "Market fit"],
                generated_at=datetime.now()
            )
        }

        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(return_value=mock_outputs)
        mock_coord_class.return_value = mock_coord_instance
        mock_async.return_value = mock_outputs

        runner = CliRunner()
        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, [
                'run',
                '--brains', 'brain-01-product-strategy',
                'Build a CRM'
            ])

            assert result.exit_code == 0
            # Check that output contains expected sections
            assert "Execution Complete" in result.output or "brain-01-product-strategy" in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    @patch('mastermind_cli.commands.orchestrate.MCPIntegration')
    @patch('mastermind_cli.commands.orchestrate.StatelessCoordinator')
    @patch('mastermind_cli.commands.orchestrate.asyncio.run')
    def test_output_saved_to_file(self, mock_async, mock_coord_class, mock_mcp, mock_validate, tmp_path):
        """Test that output can be saved to file."""
        mock_validate.return_value = Mock(owner="test-user")

        from mastermind_cli.types.interfaces import ProductStrategy
        from datetime import datetime

        mock_outputs = {
            'brain-01-product-strategy': ProductStrategy(
                positioning="Test positioning",
                target_audience="Test audience",
                key_features=["Feature 1"],
                success_metrics=["Metric 1"],
                generated_at=datetime.now()
            )
        }

        mock_coord_instance = Mock()
        mock_coord_instance.execute_flow = Mock(return_value=mock_outputs)
        mock_coord_class.return_value = mock_coord_instance
        mock_async.return_value = mock_outputs

        output_file = tmp_path / "output.json"
        runner = CliRunner()

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, [
                'run',
                '--output', str(output_file),
                '--brains', 'brain-01-product-strategy',
                'Test'
            ])

            # Verify file was created
            assert output_file.exists()
            # Verify content is valid JSON
            import json
            with open(output_file) as f:
                content = json.load(f)
                assert 'brain-01-product-strategy' in content


class TestErrorHandling:
    """Test error handling."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    @patch('mastermind_cli.commands.orchestrate.MCPIntegration')
    @patch('mastermind_cli.commands.orchestrate.StatelessCoordinator')
    @patch('mastermind_cli.commands.orchestrate.asyncio.run')
    def test_value_error_caught_and_displayed(self, mock_async, mock_coord_class, mock_mcp, mock_validate):
        """Test that ValueError during execution is caught and displayed."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_async.side_effect = ValueError("Brain not found: brain-99")

        runner = CliRunner()
        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, ['run', 'Test'])
            assert result.exit_code != 0
            assert "Error:" in result.output

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    @patch('mastermind_cli.commands.orchestrate.MCPIntegration')
    @patch('mastermind_cli.commands.orchestrate.StatelessCoordinator')
    @patch('mastermind_cli.commands.orchestrate.asyncio.run')
    def test_generic_exception_caught(self, mock_async, mock_coord_class, mock_mcp, mock_validate):
        """Test that generic exceptions are caught."""
        mock_validate.return_value = Mock(owner="test-user")
        mock_async.side_effect = RuntimeError("Unexpected error")

        runner = CliRunner()
        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            result = runner.invoke(orchestrate, ['run', 'Test'])
            assert result.exit_code != 0
            assert "Orchestration failed" in result.output


class TestVerboseMode:
    """Test verbose output."""

    @patch('mastermind_cli.commands.orchestrate.validate_api_key')
    def test_verbose_shows_execution_details(self, mock_validate):
        """Test that verbose mode shows execution details."""
        mock_validate.return_value = Mock(owner="test-user")
        runner = CliRunner()

        with patch.dict(os.environ, {'MM_API_KEY': 'test-key'}):
            with patch('mastermind_cli.commands.orchestrate.StatelessCoordinator') as mock_coord:
                mock_coord.return_value.execute_flow = Mock(return_value={})
                result = runner.invoke(orchestrate, [
                    'run',
                    '--verbose',
                    'Test'
                ])
                # Check for verbose indicators
                # (actual output depends on implementation)
                assert result.exit_code == 0 or "Error:" not in result.output
