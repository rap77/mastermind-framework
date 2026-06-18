"""Shared status enums for common backend contracts."""

from enum import Enum


class BrainExecutionStatus(str, Enum):
    """Lifecycle status for a single brain execution."""

    IDLE = "idle"
    RUNNING = "running"
    COMPLETE = "complete"
    ERROR = "error"


class ExecutionStatus(str, Enum):
    """Top-level execution status exposed by API responses."""

    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"
