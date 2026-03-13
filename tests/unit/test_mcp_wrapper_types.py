"""
Tests for mcp_wrapper.py type-safe models.

TDD Approach: RED phase - write tests for type safety.
"""

import pytest
from mastermind_cli.types import MCPRequest, MCPResponse
from pydantic import ValidationError


class TestMCPRequestModel:
    """Test MCPRequest model validation."""

    def test_valid_request_creation(self):
        """Test creating a valid MCPRequest."""
        request = MCPRequest(
            brain_id="brain-1",
            query="What is the product strategy?",
            timeout=30
        )
        assert request.brain_id == "brain-1"
        assert request.query == "What is the product strategy?"
        assert request.timeout == 30
        assert request.context is None

    def test_request_with_context(self):
        """Test creating MCPRequest with context."""
        request = MCPRequest(
            brain_id="brain-7",
            query="Evaluate this output",
            context={"output": "test output"},
            timeout=60
        )
        assert request.context == {"output": "test output"}

    def test_request_validation_empty_query(self):
        """Test that empty query fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MCPRequest(brain_id="brain-1", query="")

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("query",) and "at least 1" in error["msg"] for error in errors)

    def test_request_validation_timeout_too_low(self):
        """Test that timeout < 5 fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MCPRequest(brain_id="brain-1", query="test", timeout=4)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("timeout",) and "greater than or equal to 5" in error["msg"] for error in errors)

    def test_request_validation_timeout_too_high(self):
        """Test that timeout > 300 fails validation."""
        with pytest.raises(ValidationError) as exc_info:
            MCPRequest(brain_id="brain-1", query="test", timeout=301)

        errors = exc_info.value.errors()
        assert any(error["loc"] == ("timeout",) and "less than or equal to 300" in error["msg"] for error in errors)


class TestMCPResponseModel:
    """Test MCPResponse model validation."""

    def test_successful_response(self):
        """Test creating a successful MCPResponse."""
        response = MCPResponse(
            brain_id="brain-1",
            response="Product strategy generated",
            success=True
        )
        assert response.brain_id == "brain-1"
        assert response.response == "Product strategy generated"
        assert response.success is True
        assert response.error is None
        assert response.timestamp is None

    def test_failed_response(self):
        """Test creating a failed MCPResponse."""
        response = MCPResponse(
            brain_id="brain-1",
            response="",
            success=False,
            error="Connection timeout"
        )
        assert response.success is False
        assert response.error == "Connection timeout"

    def test_response_with_extra_fields(self):
        """Test that MCPResponse accepts extra fields (evolutivo approach)."""
        response = MCPResponse(
            brain_id="brain-1",
            response="Response",
            success=True,
            timestamp="2026-03-13T14:00:00Z",
            extra_field="This should be allowed",
            another_field=123
        )
        assert response.extra_field == "This should be allowed"
        assert response.another_field == 123

    def test_response_model_dump(self):
        """Test that response can be serialized."""
        response = MCPResponse(
            brain_id="brain-1",
            response="Test response",
            success=True
        )
        data = response.model_dump()
        assert data["brain_id"] == "brain-1"
        assert data["response"] == "Test response"
        assert data["success"] is True


class TestMCPWrapperTypeSafety:
    """Test that MCP wrapper uses type models."""

    def test_wrapper_accepts_mcp_request(self):
        """Test that wrapper can accept MCPRequest model."""
        from mastermind_cli.orchestrator.mcp_wrapper import MCPWrapper

        # This should work with typed model
        spec = MCPWrapper.create_notebook_query_spec(
            notebook_id="test-notebook",
            query="Test query"
        )
        assert isinstance(spec, dict)
        assert spec["tool"] == "mcp__notebooklm-mcp__notebook_query"

    def test_wrapper_returns_dict(self):
        """Test that wrapper methods return typed dicts."""
        from mastermind_cli.orchestrator.mcp_wrapper import MCPWrapper

        response = MCPWrapper.parse_notebook_response("test response")
        assert isinstance(response, dict)
        assert "status" in response

    def test_direct_invoker_returns_dict(self):
        """Test that DirectMCPInvoker returns typed dict."""
        from mastermind_cli.orchestrator.mcp_wrapper import DirectMCPInvoker

        spec = DirectMCPInvoker.query_brain(brain_id=1, query="test")
        assert isinstance(spec, dict)
        assert "status" in spec

    def test_brain_1_query_returns_str(self):
        """Test that create_brain_1_query returns string."""
        from mastermind_cli.orchestrator.mcp_wrapper import DirectMCPInvoker

        query = DirectMCPInvoker.create_brain_1_query("Test brief")
        assert isinstance(query, str)
        assert "Test brief" in query

    def test_brain_7_query_returns_str(self):
        """Test that create_brain_7_query returns string."""
        from mastermind_cli.orchestrator.mcp_wrapper import DirectMCPInvoker

        query = DirectMCPInvoker.create_brain_7_query({"test": "output"}, brain_id=1)
        assert isinstance(query, str)
        assert "evaluate" in query.lower()
