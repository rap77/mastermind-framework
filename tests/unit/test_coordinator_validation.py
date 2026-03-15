"""Unit tests for coordinator @validate_call decorator."""

import pytest
from pydantic import ValidationError, validate_call, Field
from typing import Annotated


# Mock coordinator class with validate_call
class MockCoordinator:
    """Mock coordinator for testing @validate_call."""

    @validate_call
    def _process_brain_evaluation(
        self, brain_id: str, score: float, issues: list[str] = []
    ) -> dict:
        """Process brain evaluation with runtime type validation.

        Pydantic validates arguments before function executes:
        - "0.8" → 0.8 (coerce)
        - "alto" → ValidationError
        - brain_id must be str
        - score must be float
        """
        return {"brain_id": brain_id, "score": score, "issues": issues}

    @validate_call
    def process_brain_evaluation(
        self,
        brain_id: str,
        score: Annotated[float, Field(ge=0.0, le=1.0)],
        issues: list[str] = [],
    ) -> dict:
        """Process with constraints."""
        return {"brain_id": brain_id, "score": score, "issues": issues}


def test_validate_call_decorator_valid():
    """Test that @validate_call validates function arguments at runtime."""
    coordinator = MockCoordinator()

    # Valid arguments
    result = coordinator._process_brain_evaluation(
        brain_id="brain-1", score=0.8, issues=["missing_metric"]
    )

    assert result["brain_id"] == "brain-1"
    assert result["score"] == 0.8
    assert result["issues"] == ["missing_metric"]


def test_validate_call_decorator_type_coercion():
    """Test that type coercion works ("0.8" → 0.8)."""
    coordinator = MockCoordinator()

    # String to float coercion
    result = coordinator._process_brain_evaluation(
        brain_id="brain-1",
        score="0.8",  # String coerced to float
    )

    assert result["score"] == 0.8
    assert isinstance(result["score"], float)


def test_validate_call_decorator_invalid_arguments():
    """Test that invalid arguments raise ValidationError before function executes."""
    coordinator = MockCoordinator()

    # Invalid: score is not a number
    with pytest.raises(ValidationError) as exc_info:
        coordinator._process_brain_evaluation(
            brain_id="brain-1",
            score="alto",  # Cannot coerce to float
        )

    errors = exc_info.value.errors()
    assert len(errors) > 0
    assert any("score" in str(err.get("loc", "")) for err in errors)


def test_validate_call_with_constraints():
    """Test that @validate_call enforces Field constraints."""
    coordinator = MockCoordinator()

    # Valid: score within constraints
    result = coordinator.process_brain_evaluation(brain_id="brain-1", score=0.8)
    assert result["score"] == 0.8

    # Invalid: score > 1.0
    with pytest.raises(ValidationError) as exc_info:
        coordinator.process_brain_evaluation(brain_id="brain-1", score=1.5)

    errors = exc_info.value.errors()
    assert any(err.get("ctx", {}).get("le") == 1.0 for err in errors)

    # Invalid: score < 0.0
    with pytest.raises(ValidationError) as exc_info:
        coordinator.process_brain_evaluation(brain_id="brain-1", score=-0.1)

    errors = exc_info.value.errors()
    assert any(err.get("ctx", {}).get("ge") == 0.0 for err in errors)


def test_validate_call_default_values():
    """Test that default values work with @validate_call."""
    coordinator = MockCoordinator()

    # Omit optional parameter with default
    result = coordinator._process_brain_evaluation(
        brain_id="brain-1",
        score=0.8,
        # issues defaults to []
    )

    assert result["issues"] == []
