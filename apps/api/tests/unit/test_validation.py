"""
Runtime validation helper tests.
"""

import pytest
import click
from mastermind_cli.utils.validation import TypeAdapterParam, validate_brain_output


class TestTypeAdapterParam:
    """Test TypeAdapterParam Click parameter type."""

    def test_type_adapter_param_validates_click_parameters(self):
        """Test that TypeAdapterParam validates Click parameters."""
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            name: str = Field(..., min_length=1)
            score: float = Field(..., ge=0.0, le=1.0)

        param = TypeAdapterParam(TestModel)

        # Valid input
        result = param.convert('{"name": "test", "score": 0.8}', None, None)
        assert result.name == "test"
        assert result.score == 0.8

    def test_type_adapter_param_returns_validated_python_objects(self):
        """Test that TypeAdapterParam returns validated Python objects."""
        from pydantic import BaseModel

        class TestModel(BaseModel):
            value: int

        param = TypeAdapterParam(TestModel)

        # String should be coerced to int
        result = param.convert('{"value": "42"}', None, None)
        assert isinstance(result.value, int)
        assert result.value == 42

    def test_type_adapter_param_shows_clear_error_messages_on_validation_failure(self):
        """Test that TypeAdapterParam shows clear error messages on validation failure."""
        from pydantic import BaseModel, Field

        class TestModel(BaseModel):
            score: float = Field(..., ge=0.0, le=1.0)

        param = TypeAdapterParam(TestModel)

        # Invalid input
        with pytest.raises(click.BadParameter) as exc_info:
            param.convert('{"score": 1.5}', None, None)

        error_msg = str(exc_info.value)
        assert "Invalid" in error_msg or "score" in error_msg.lower()

    def test_validate_brain_output_uses_type_adapter_for_runtime_validation(self):
        """Test that validate_brain_output() uses TypeAdapter for runtime validation."""
        from mastermind_cli.types import StandardSchema

        # Valid data
        valid_data = {
            "brain_id": "test-brain",
            "content": "Test output",
            "version": "v1.0.0",
        }

        result = validate_brain_output(valid_data, StandardSchema)
        assert isinstance(result, StandardSchema)
        assert result.brain_id == "test-brain"

    def test_validate_brain_output_returns_structured_error_on_failure(self):
        """Test that validate_brain_output() returns structured error on validation failure."""
        from mastermind_cli.types import StandardSchema

        # Invalid data (missing required fields)
        invalid_data = {"brain_id": "test"}  # Missing 'content'

        result = validate_brain_output(invalid_data, StandardSchema)

        # Should return dict with validation_error
        assert isinstance(result, dict)
        assert "validation_error" in result
        assert "raw_data" in result
