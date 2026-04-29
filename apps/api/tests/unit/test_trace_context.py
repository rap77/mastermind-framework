"""Unit tests for distributed trace context propagation.

Validates:
- B1.7: gRPC metadata with trace-id → ContextVar set
- B1.8: structlog emits {"trace_id": "test-abc"} automatically
- B1.12: Combined — gRPC metadata → structlog output contains trace_id
"""

from __future__ import annotations

import io
import json
from unittest.mock import MagicMock

import pytest
import structlog

from mastermind_cli.observability.trace_context import (
    TraceIdInterceptor,
    add_trace_id,
    get_trace_id,
    set_trace_id,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeHandlerCallDetails:
    """Minimal stand-in for grpc.HandlerCallDetails."""

    def __init__(self, metadata: list[tuple[str, str]] | None = None) -> None:
        self.invocation_metadata = metadata or []
        self.method = "/worker.Worker/ProcessWebhook"


# ---------------------------------------------------------------------------
# ContextVar tests
# ---------------------------------------------------------------------------


class TestTraceContextVar:
    """Test get/set of the ContextVar directly."""

    def test_default_is_unknown(self) -> None:
        """Before any set_trace_id call the default is 'unknown'."""
        # We can't guarantee isolation between tests in the same process, so
        # we set the var explicitly to "unknown" first.
        set_trace_id("unknown")
        assert get_trace_id() == "unknown"

    def test_set_and_get(self) -> None:
        """set_trace_id persists for subsequent get_trace_id calls."""
        set_trace_id("test-abc")
        assert get_trace_id() == "test-abc"

    def test_overwrite(self) -> None:
        """Second set_trace_id replaces the previous value."""
        set_trace_id("first-id")
        set_trace_id("second-id")
        assert get_trace_id() == "second-id"


# ---------------------------------------------------------------------------
# structlog processor tests
# ---------------------------------------------------------------------------


class TestAddTraceIdProcessor:
    """Test the add_trace_id structlog processor (B1.8)."""

    def test_injects_trace_id_from_contextvar(self) -> None:
        """Processor reads from ContextVar and adds trace_id to event dict."""
        set_trace_id("proc-test-123")
        event_dict: dict = {"event": "hello"}
        result = add_trace_id(None, "info", event_dict)
        assert result["trace_id"] == "proc-test-123"

    def test_does_not_inject_when_unknown(self) -> None:
        """Processor skips injection when ContextVar is 'unknown'."""
        set_trace_id("unknown")
        event_dict: dict = {"event": "hello"}
        result = add_trace_id(None, "info", event_dict)
        assert "trace_id" not in result

    def test_does_not_overwrite_existing_trace_id(self) -> None:
        """Processor uses setdefault — does not overwrite manually-bound trace_id."""
        set_trace_id("ctx-id")
        event_dict: dict = {"event": "hello", "trace_id": "manual-id"}
        result = add_trace_id(None, "info", event_dict)
        assert result["trace_id"] == "manual-id"


# ---------------------------------------------------------------------------
# structlog JSON output tests (B1.12)
# ---------------------------------------------------------------------------


class TestStructlogJsonOutput:
    """Verify structlog emits {"trace_id": "..."} in JSON output.

    B1.12: Python unit test — gRPC metadata with trace_id → structlog emits
    {"trace_id": "test-abc"}.
    """

    def test_log_output_contains_trace_id(self) -> None:
        """After set_trace_id, structlog JSON output must include trace_id."""
        output = io.StringIO()

        structlog.configure(
            processors=[
                add_trace_id,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.WriteLoggerFactory(file=output),
            cache_logger_on_first_use=False,
        )

        set_trace_id("test-abc")
        logger = structlog.get_logger("test")
        logger.info("payload processed")

        log_line = output.getvalue().strip()
        assert log_line, "No log output produced"

        parsed = json.loads(log_line)
        assert (
            parsed["trace_id"] == "test-abc"
        ), f"Expected trace_id='test-abc' in log output, got: {parsed}"
        assert "payload processed" in parsed.get("event", "")

    def test_log_output_missing_when_unknown(self) -> None:
        """When trace_id is 'unknown', the field must be absent from output."""
        output = io.StringIO()

        structlog.configure(
            processors=[
                add_trace_id,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.WriteLoggerFactory(file=output),
            cache_logger_on_first_use=False,
        )

        set_trace_id("unknown")
        logger = structlog.get_logger("test")
        logger.info("no trace here")

        log_line = output.getvalue().strip()
        assert log_line
        parsed = json.loads(log_line)
        assert "trace_id" not in parsed


# ---------------------------------------------------------------------------
# gRPC interceptor tests (B1.7 + B1.12 combined)
# ---------------------------------------------------------------------------


class TestTraceIdInterceptor:
    """Test the grpc.aio interceptor that extracts trace-id from metadata."""

    @pytest.mark.asyncio
    async def test_extracts_trace_id_from_metadata(self) -> None:
        """metadata with 'trace-id' → ContextVar holds the extracted value."""
        interceptor = TraceIdInterceptor()
        details = FakeHandlerCallDetails(metadata=[("trace-id", "test-abc")])

        async def fake_continuation(d: object) -> object:
            return MagicMock()

        await interceptor.intercept_service(fake_continuation, details)
        assert get_trace_id() == "test-abc"

    @pytest.mark.asyncio
    async def test_generates_uuid_when_no_metadata(self) -> None:
        """No trace-id metadata → interceptor generates a fresh UUID v4."""
        import uuid as uuid_mod

        interceptor = TraceIdInterceptor()
        details = FakeHandlerCallDetails(metadata=[])

        async def fake_continuation(d: object) -> object:
            return MagicMock()

        await interceptor.intercept_service(fake_continuation, details)
        generated = get_trace_id()
        assert generated != "unknown"
        parsed = uuid_mod.UUID(generated)
        assert parsed.version == 4

    @pytest.mark.asyncio
    async def test_empty_trace_id_falls_back_to_uuid(self) -> None:
        """Empty string trace-id → interceptor generates a fresh UUID v4."""
        import uuid as uuid_mod

        interceptor = TraceIdInterceptor()
        details = FakeHandlerCallDetails(metadata=[("trace-id", "  ")])

        async def fake_continuation(d: object) -> object:
            return MagicMock()

        await interceptor.intercept_service(fake_continuation, details)
        generated = get_trace_id()
        parsed = uuid_mod.UUID(generated)
        assert parsed.version == 4

    @pytest.mark.asyncio
    async def test_combined_grpc_to_structlog_json(self) -> None:
        """B1.12: intercept with trace-id 'test-abc' → structlog emits {trace_id: test-abc}."""

        output = io.StringIO()

        structlog.configure(
            processors=[
                add_trace_id,
                structlog.processors.JSONRenderer(),
            ],
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.WriteLoggerFactory(file=output),
            cache_logger_on_first_use=False,
        )

        interceptor = TraceIdInterceptor()
        details = FakeHandlerCallDetails(metadata=[("trace-id", "test-abc")])

        async def fake_continuation(d: object) -> object:
            # Simulate handler logging
            structlog.get_logger("worker").info("processing rpc")
            return MagicMock()

        await interceptor.intercept_service(fake_continuation, details)

        log_line = output.getvalue().strip()
        assert log_line, "No log output produced"
        parsed = json.loads(log_line)
        assert (
            parsed.get("trace_id") == "test-abc"
        ), f"Expected trace_id='test-abc', got: {parsed}"
