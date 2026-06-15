"""Tests for the brain_memory CLI bridge."""

from __future__ import annotations

import argparse
import json
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from mastermind_cli.tools import brain_memory


@pytest.mark.asyncio
async def test_cmd_query_uses_injected_logger_and_prints_json(capsys) -> None:
    """Query should serialize records from an injected logger."""
    fake_record = SimpleNamespace(
        id="rec-001",
        timestamp="2026-06-15T00:00:00+00:00",
        status="success",
        duration_ms=123,
        output_json={"result": "ok"},
        custom_metadata={"quality_score": 2.0},
    )
    fake_logger = AsyncMock()
    fake_logger.get_recent_by_brain.return_value = [fake_record]
    args = argparse.Namespace(brain_id="brain-01-product", limit=5)

    await brain_memory._cmd_query(args, logger=fake_logger)

    fake_logger.get_recent_by_brain.assert_awaited_once_with(
        "brain-01-product", limit=5
    )
    output = json.loads(capsys.readouterr().out)
    assert output[0]["id"] == "rec-001"
    assert output[0]["output_json"] == {"result": "ok"}


@pytest.mark.asyncio
async def test_cmd_log_uses_injected_logger_and_prints_result(capsys) -> None:
    """Log should parse JSON args and delegate to an injected logger."""
    fake_logger = AsyncMock()
    fake_logger.log_execution.return_value = "rec-logged"
    args = argparse.Namespace(
        brain_id="brain-01-product",
        input='{"brief":"hello"}',
        output='{"result":"world"}',
        metadata='{"category":"product"}',
        duration_ms=321,
        status="success",
        trace_id="trace-123",
    )

    await brain_memory._cmd_log(args, logger=fake_logger)

    fake_logger.log_execution.assert_awaited_once_with(
        brain_id="brain-01-product",
        input_json={"brief": "hello"},
        output_json={"result": "world"},
        duration_ms=321,
        status="success",
        trace_context_id="trace-123",
        custom_metadata={"category": "product"},
    )
    output = json.loads(capsys.readouterr().out)
    assert output == {"record_id": "rec-logged", "status": "logged"}


def test_parse_json_arg_exits_on_invalid_json(capsys) -> None:
    """Invalid JSON should emit a stable error payload and exit."""
    with pytest.raises(SystemExit) as excinfo:
        brain_memory._parse_json_arg("{bad", "--input")

    assert excinfo.value.code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["error"].startswith("Invalid --input JSON:")


def test_parse_json_arg_exits_on_non_object_json(capsys) -> None:
    """Non-object JSON should be rejected for CLI payload flags."""
    with pytest.raises(SystemExit) as excinfo:
        brain_memory._parse_json_arg('["not","an","object"]', "--metadata")

    assert excinfo.value.code == 1
    output = json.loads(capsys.readouterr().out)
    assert output["error"] == "Invalid --metadata JSON: expected object"
