"""Integration tests for MCP wrapper validation."""

import pytest
from mastermind_cli.orchestrator.mcp_wrapper import MCPWrapper
from mastermind_cli.types import MCPRequest, MCPResponse
from pydantic import ValidationError


class MockMCPClient:
    """Mock MCP client for testing."""

    def __init__(self, extra_fields=None, raises_error=False):
        self.extra_fields = extra_fields or {}
        self.raises_error = raises_error

    def query_brain(self, brain_id, query, timeout):
        if self.raises_error:
            raise Exception("MCP connection failed")
        return {
            "response": f"Mock response for {brain_id}: {query}",
            "success": True,
            "timestamp": "2026-03-13T15:00:00Z",
            **self.extra_fields,
        }


def test_mcp_wrapper_validation():
    """Test that MCP wrapper validates requests."""
    wrapper = MCPWrapper(mcp_client=MockMCPClient())

    # Valid request
    response = wrapper.call_mcp(brain_id="test-brain", query="Test query")
    assert isinstance(response, MCPResponse)
    assert response.success is True
    assert response.response == "Mock response for test-brain: Test query"
    assert response.brain_id == "test-brain"


def test_mcp_wrapper_preserves_extra_fields():
    """Test that MCP wrapper preserves unknown fields."""
    custom_fields = {"custom_field": "custom_value", "metadata": {"key": "value"}}
    wrapper = MCPWrapper(mcp_client=MockMCPClient(extra_fields=custom_fields))

    response = wrapper.call_mcp(brain_id="test-brain", query="Test query")

    assert response.custom_field == "custom_value"  # Extra field preserved
    assert response.metadata == {"key": "value"}


def test_mcp_wrapper_error_handling():
    """Test that MCP wrapper handles errors gracefully."""
    wrapper = MCPWrapper(mcp_client=MockMCPClient(raises_error=True))

    response = wrapper.call_mcp(brain_id="test-brain", query="Test query")

    assert response.success is False
    assert response.error is not None
    assert "MCP call failed" in response.error


def test_mcp_wrapper_query_validation():
    """Test that query validation works (min_length=1)."""
    wrapper = MCPWrapper(mcp_client=MockMCPClient())

    # Empty query should fail validation
    with pytest.raises(ValidationError) as exc_info:
        wrapper.call_mcp(
            brain_id="test-brain",
            query="",  # Invalid: min_length=1
        )

    errors = exc_info.value.errors()
    assert any("query" in str(err.get("loc", "")) for err in errors)


def test_mcp_wrapper_timeout_validation():
    """Test that timeout validation works (ge=5, le=300)."""
    wrapper = MCPWrapper(mcp_client=MockMCPClient())

    # Timeout too low
    with pytest.raises(ValidationError) as exc_info:
        wrapper.call_mcp(
            brain_id="test-brain",
            query="Test query",
            timeout=3,  # Invalid: ge=5
        )

    errors = exc_info.value.errors()
    assert any(err.get("ctx", {}).get("ge") == 5 for err in errors)

    # Timeout too high
    with pytest.raises(ValidationError) as exc_info:
        wrapper.call_mcp(
            brain_id="test-brain",
            query="Test query",
            timeout=500,  # Invalid: le=300
        )

    errors = exc_info.value.errors()
    assert any(err.get("ctx", {}).get("le") == 300 for err in errors)


def test_mcp_request_model():
    """Test that MCPRequest model validates correctly."""
    # Valid request
    request = MCPRequest(brain_id="test-brain", query="Test query", timeout=30)
    assert request.brain_id == "test-brain"
    assert request.query == "Test query"
    assert request.timeout == 30

    # Invalid request (empty query)
    with pytest.raises(ValidationError) as exc_info:
        MCPRequest(
            brain_id="test-brain",
            query="",  # Invalid: min_length=1
        )

    errors = exc_info.value.errors()
    assert any("query" in str(err.get("loc", "")) for err in errors)


def test_mcp_response_extra_allow():
    """Test that MCPResponse preserves extra fields."""
    # Create response with extra fields
    response = MCPResponse(
        brain_id="test-brain",
        response="Test response",
        success=True,
        custom_field="custom_value",
        metadata={"key": "value"},
    )

    assert response.custom_field == "custom_value"
    assert response.metadata == {"key": "value"}
