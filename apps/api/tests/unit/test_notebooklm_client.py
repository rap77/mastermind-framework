"""Tests for NotebookLMClient behavior."""

from __future__ import annotations

from mastermind_cli.orchestrator.notebooklm_client import NotebookLMClient


def test_query_brain_returns_mcp_required_stub() -> None:
    """NotebookLMClient should return the planning stub payload."""
    client = NotebookLMClient()

    result = client.query_brain(1, "Test query")

    assert result["status"] == "mcp_required"
    assert result["brain_id"] == 1
    assert result["notebook_id"]


def test_parse_yaml_response_returns_error_on_invalid_yaml() -> None:
    """Malformed YAML should return a parse error payload."""
    client = NotebookLMClient()

    result = client.parse_yaml_response("```yaml\ninvalid: [\n```")

    assert result["error"].startswith("Failed to parse YAML:")
