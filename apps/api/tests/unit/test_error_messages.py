"""Unit tests for error message formatting."""

import pytest
from pydantic import ValidationError
from mastermind_cli.types import CoordinatorRequest
from mastermind_cli.utils.validation import (
    format_validation_error,
    format_validation_error_compact,
)


def test_error_message_context():
    """Test that error messages include field location and type."""
    with pytest.raises(ValidationError) as exc_info:
        CoordinatorRequest(
            brief="",  # Invalid: min_length=1
            max_iterations=15,  # Invalid: le=10
        )

    formatted = format_validation_error(exc_info.value)
    # Check field location
    assert "brief" in formatted
    assert "max_iterations" in formatted
    # Check error message content (Pydantic v2 format)
    assert "at least 1 character" in formatted.lower()
    assert "less than or equal to 10" in formatted.lower()


def test_error_message_compact():
    """Test compact error format."""
    with pytest.raises(ValidationError) as exc_info:
        CoordinatorRequest(
            brief="",  # Invalid: min_length=1
            max_iterations=15,  # Invalid: le=10
        )

    compact = format_validation_error_compact(exc_info.value)
    # Should have field names
    assert "brief" in compact
    assert "max_iterations" in compact
    # Should be single-line format
    assert "\n" not in compact or compact.count("\n") <= 1


def test_error_message_with_context():
    """Test error formatting with context string."""
    with pytest.raises(ValidationError) as exc_info:
        CoordinatorRequest(brief="")

    formatted = format_validation_error(exc_info.value, context="CLI validation")
    # Should include context
    assert "CLI validation" in formatted


def test_error_message_shows_constraints():
    """Test that constraint values are shown in error messages."""
    with pytest.raises(ValidationError) as exc_info:
        CoordinatorRequest(
            brief="Test",
            max_iterations=15,  # Invalid: le=10
        )

    formatted = format_validation_error(exc_info.value)
    # Should show constraint value (10)
    assert "10" in formatted


def test_error_message_multiple_errors():
    """Test formatting multiple validation errors."""
    with pytest.raises(ValidationError) as exc_info:
        CoordinatorRequest(
            brief="",  # Error 1
            max_iterations=15,  # Error 2
        )

    formatted = format_validation_error(exc_info.value)
    # Should have both errors
    assert "brief" in formatted
    assert "max_iterations" in formatted
