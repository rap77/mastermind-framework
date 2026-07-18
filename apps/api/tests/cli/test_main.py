"""Tests for top-level MasterMind CLI command registration."""

from click.testing import CliRunner

from mastermind_cli.main import cli


def test_evaluate_harness_routing_is_registered() -> None:
    """The canonical routing evaluator should be available at the CLI root."""
    result = CliRunner().invoke(cli, ["evaluate-harness-routing", "--help"])

    assert result.exit_code == 0
    assert "--project-root" in result.output
