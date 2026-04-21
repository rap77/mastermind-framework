"""Structured logging configuration for MasterMind Framework."""

import structlog
from typing import Any


def configure_logging() -> None:
    """Configure structlog with JSON output for production logging."""
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> Any:
    """Get a structured logger with the given name.

    Args:
        name: Logger name (usually __name__ from the calling module)

    Returns:
        BoundLogger configured with JSON output
    """
    return structlog.get_logger(name)
