"""Observability module for MasterMind Framework."""

from mastermind_cli.observability.logging import configure_logging, get_logger
from mastermind_cli.observability.tracer import extract_trace_context
from mastermind_cli.observability.trace_context import (
    add_trace_id,
    get_trace_id,
    set_trace_id,
)

try:
    from mastermind_cli.observability.trace_context import TraceIdInterceptor  # noqa: F401
except ImportError:
    pass

__all__ = [
    "configure_logging",
    "get_logger",
    "extract_trace_context",
    "TraceIdInterceptor",
    "add_trace_id",
    "get_trace_id",
    "set_trace_id",
]
