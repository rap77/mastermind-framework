"""Distributed trace context propagation via Python contextvars.

This module provides:
- A `ContextVar` that stores the current `trace_id` for the running async task.
- A structlog processor that automatically binds `trace_id` to every log event.
- A gRPC server interceptor (grpc.aio) that extracts `trace-id` from incoming
  metadata and sets the ContextVar before the RPC handler runs.

Usage:
    # In application startup (already done in observability/logging.py):
    configure_logging()   # registers the structlog processor

    # In gRPC server startup (routers/internal.py):
    server = grpc.aio.server(interceptors=[TraceIdInterceptor()])

    # After that, any log call carries trace_id automatically:
    logger = structlog.get_logger(__name__)
    logger.info("processing request")   # → {"trace_id": "...", "event": "..."}
"""

from __future__ import annotations

import uuid
from collections.abc import Callable, MutableMapping
from contextvars import ContextVar
from typing import Any

try:
    import grpc
    import grpc.aio

    _GRPC_AVAILABLE = True
except ModuleNotFoundError:
    _GRPC_AVAILABLE = False

# ---------------------------------------------------------------------------
# ContextVar — single source of truth for the current trace_id
# ---------------------------------------------------------------------------

_trace_id_var: ContextVar[str] = ContextVar("trace_id", default="unknown")


def get_trace_id() -> str:
    """Return the trace_id for the current async context."""
    return _trace_id_var.get()


def set_trace_id(trace_id: str) -> None:
    """Set the trace_id for the current async context."""
    _trace_id_var.set(trace_id)


# ---------------------------------------------------------------------------
# structlog processor — injects trace_id into every log event
# ---------------------------------------------------------------------------


def add_trace_id(
    logger: Any,
    method: str,
    event_dict: MutableMapping[str, Any],
) -> MutableMapping[str, Any]:
    """structlog processor: inject trace_id from ContextVar into log events.

    Registered in configure_logging() so all structlog calls carry trace_id
    automatically without callers needing to bind it manually.
    """
    trace_id = get_trace_id()
    if trace_id != "unknown":
        event_dict.setdefault("trace_id", trace_id)
    return event_dict


# ---------------------------------------------------------------------------
# gRPC server interceptor — grpc.aio compatible (only when grpcio is installed)
# ---------------------------------------------------------------------------

if _GRPC_AVAILABLE:

    class TraceIdInterceptor(grpc.aio.ServerInterceptor):
        """gRPC server interceptor that propagates distributed trace_id.

        Extracts the ``trace-id`` metadata key from incoming gRPC requests and
        stores it in the ``_trace_id_var`` ContextVar so all log calls made
        within the RPC handler automatically include ``trace_id``.

        If the metadata key is absent or empty, a fresh UUID v4 is generated so
        every RPC always has a traceable identifier.

        Priority (matches Rust Axum middleware behavior):
        1. ``trace-id`` gRPC metadata value, if present and non-empty
        2. Fresh UUID v4
        """

        async def intercept_service(
            self,
            continuation: Callable[..., Any],
            handler_call_details: Any,
        ) -> Any:
            """Extract trace_id from metadata and set ContextVar before handler."""
            metadata = dict(handler_call_details.invocation_metadata or [])
            val = metadata.get("trace-id", "")
            raw = (val.decode() if isinstance(val, bytes) else val).strip()
            trace_id = raw if raw else str(uuid.uuid4())
            set_trace_id(trace_id)
            return await continuation(handler_call_details)
