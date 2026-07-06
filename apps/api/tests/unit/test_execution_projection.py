"""Tests for execution projection parsing helpers."""

from __future__ import annotations

from typing import Any

import pytest

from mastermind_cli.api.services.execution_projection import (
    _parse_brain_outputs,
    _parse_graph_snapshot,
    _parse_milestones,
    decode_cursor,
)


def test_decode_cursor_returns_none_for_invalid_input() -> None:
    """Invalid cursors should be rejected without raising."""
    assert decode_cursor("not-a-cursor") is None


@pytest.mark.parametrize(
    ("parser", "raw"),
    [
        (_parse_milestones, "not-json"),
        (_parse_brain_outputs, "not-json"),
        (_parse_graph_snapshot, "not-json"),
    ],
)
def test_projection_parsers_return_empty_collections_on_invalid_json(
    parser: Any, raw: str
) -> None:
    """Malformed JSON should fall back to empty structures."""
    result = parser(raw)
    assert result == [] or result == {}
