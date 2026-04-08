"""Trace context extraction for distributed tracing."""

import structlog
from typing import Any


def extract_trace_context(metadata: dict[str, Any]) -> dict[str, Any]:
    """Extract trace_id from gRPC metadata and bind to logger context.

    Args:
        metadata: gRPC metadata dictionary (may contain 'trace-id' key)

    Returns:
        Dictionary with trace_id for binding to logger context
    """
    trace_id = metadata.get("trace-id", "unknown")

    logger = structlog.get_logger()
    logger = logger.bind(trace_id=trace_id)

    return {"trace_id": trace_id}
