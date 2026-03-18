"""Integration tests for CLI-to-coordinator type boundary."""

import pytest
from click.testing import CliRunner
from mastermind_cli.commands.orchestrate import orchestrate
from mastermind_cli.types import CoordinatorRequest


def test_cli_coordinator_type_boundary():
    """Test that CLI creates valid CoordinatorRequest."""
    runner = CliRunner()

    # Test valid input
    result = runner.invoke(
        orchestrate,
        [
            "run",
            "--brief",
            "Test brief with sufficient length",
            "--flow",
            "validation_only",
            "--dry-run",
        ],
    )

    # Should not fail on validation (may fail on other things, but not type validation)
    # Exit code 0 or 1 is acceptable, but we should not see validation errors
    assert "ValidationError" not in result.output
    assert "validation error" not in result.output.lower()


def test_cli_invalid_params():
    """Test that CLI shows clear errors for invalid params."""
    runner = CliRunner()

    # Test invalid brief (empty after min_length validation in CoordinatorRequest)
    # Note: Click doesn't validate min_length, but the CoordinatorRequest will
    result = runner.invoke(
        orchestrate,
        [
            "run",
            "--brief",
            "",  # This will fail at Click level (empty string)
            "--max-iterations",
            "15",  # Invalid: > 10
        ],
    )

    # Should fail with clear error
    assert result.exit_code != 0 or "Error" in result.output

    # The brief error might come from Click or our validation
    output_lower = result.output.lower()
    # At least one of the validations should trigger
    has_brief_error = "brief" in output_lower or "no brief provided" in output_lower
    has_iterations_error = (
        "max_iterations" in output_lower or "max-iterations" in output_lower
    )

    assert (
        has_brief_error or has_iterations_error
    ), f"Expected validation error, got: {result.output}"


def test_cli_coordinator_request_model():
    """Test that CoordinatorRequest model validates correctly."""
    # Valid request
    request = CoordinatorRequest(
        brief="Test brief with enough length",
        flow="validation_only",
        dry_run=True,
        max_iterations=3,
    )
    assert request.brief == "Test brief with enough length"
    assert request.flow == "validation_only"
    assert request.dry_run is True
    assert request.max_iterations == 3

    # Invalid request (max_iterations > 10)
    with pytest.raises(Exception) as exc_info:
        CoordinatorRequest(brief="Test brief", max_iterations=15)
    assert "max_iterations" in str(exc_info.value).lower()


def test_cli_coordinator_response_format():
    """Test that CLI handles coordinator response structure."""
    # This test verifies the response structure matches CoordinatorResponse
    from mastermind_cli.types import CoordinatorResponse
    from datetime import datetime, timezone

    response = CoordinatorResponse(
        status="dry_run_complete",
        plan={"brains": ["brain1"]},
        output="Test output",
        timestamp=datetime.now(timezone.utc),
        iterations=0,
    )

    assert response.status == "dry_run_complete"
    assert response.plan is not None
    assert response.output == "Test output"
    assert response.iterations == 0
