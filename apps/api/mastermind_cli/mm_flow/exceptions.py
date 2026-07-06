"""Domain exceptions for MM-Flow planning bridge boundaries."""

from __future__ import annotations


class PlanningBridgeError(Exception):
    """Raised when planning artifacts cannot be parsed or loaded."""


class PlanningManifestError(PlanningBridgeError):
    """Raised when the canonical project manifest is missing or malformed."""
