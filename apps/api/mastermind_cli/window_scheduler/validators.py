"""Validation helpers for the window scheduler service layer."""

from __future__ import annotations

from datetime import datetime


def require_next_step_summary(next_step_summary: str) -> str:
    """Return a normalized next-step summary or raise if it is empty."""
    normalized = next_step_summary.strip()
    if not normalized:
        raise ValueError("next_step_summary is required")
    return normalized


def require_checkpoint_id_for_switch(checkpoint_id: str | None) -> str:
    """Return the checkpoint ID for a backend switch or raise if missing."""
    if checkpoint_id is None or not checkpoint_id.strip():
        raise ValueError("checkpoint_id is required for backend_switch")
    return checkpoint_id


def require_reset_estimation_metadata(
    estimated_reset_at: datetime | None,
    estimation_source: str | None,
    estimation_confidence: str | None,
) -> tuple[str | None, str | None]:
    """Validate reset-estimate provenance when a reset timestamp is present."""
    if estimated_reset_at is None:
        return estimation_source, estimation_confidence

    if estimation_source is None or not estimation_source.strip():
        raise ValueError("estimation_source is required when estimated_reset_at is set")
    if estimation_confidence is None or not estimation_confidence.strip():
        raise ValueError(
            "estimation_confidence is required when estimated_reset_at is set"
        )
    return estimation_source.strip(), estimation_confidence.strip()
