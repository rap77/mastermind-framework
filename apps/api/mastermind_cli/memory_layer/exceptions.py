"""Domain exceptions for the memory layer boundaries."""

from __future__ import annotations


class MemoryLayerError(Exception):
    """Base class for memory layer failures."""


class MemorySnapshotError(MemoryLayerError):
    """Raised when a resumable context snapshot cannot be built."""


class MemoryPersistenceError(MemoryLayerError):
    """Raised when runtime memory artifacts cannot be persisted."""
