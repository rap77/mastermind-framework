"""Context fit evaluator for window scheduler capability-aware decisions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


FitState = Literal[
    "fits_cleanly",
    "fits_with_compression",
    "unsafe_fit",
    "does_not_fit",
]
RiskLevel = Literal["low", "medium", "high"]


@dataclass(frozen=True)
class ContextCapabilityProfile:
    """Minimal backend capability profile for context-fit evaluation."""

    backend_id: str
    max_context_window: int | None
    recommended_working_window: int | None
    max_output_window: int | None
    long_context_quality: str | None
    compression_preference: str | None


@dataclass(frozen=True)
class ContextFitAssessment:
    """Fit assessment returned by the phase-1 context evaluator."""

    backend_id: str
    fit_state: FitState
    compression_required: bool
    risk_level: RiskLevel
    recommended_strategy: str


def assess_context_fit(
    profile: ContextCapabilityProfile,
    *,
    required_context_tokens: int,
    expected_output_tokens: int,
) -> ContextFitAssessment:
    """Assess whether a backend can safely carry the requested context load.

    Args:
        profile: Backend capability metadata.
        required_context_tokens: Tokens required for context input.
        expected_output_tokens: Tokens expected in model output.

    Returns:
        A normalized fit assessment using the canonical four-state model.

    Raises:
        ValueError: If token counts are negative.
    """
    if required_context_tokens < 0:
        raise ValueError("required_context_tokens must be >= 0")
    if expected_output_tokens < 0:
        raise ValueError("expected_output_tokens must be >= 0")

    if profile.max_context_window is None or profile.recommended_working_window is None:
        return ContextFitAssessment(
            backend_id=profile.backend_id,
            fit_state="unsafe_fit",
            compression_required=False,
            risk_level="high",
            recommended_strategy="collect_capability_profile",
        )

    total_tokens = required_context_tokens + expected_output_tokens
    max_output_window = profile.max_output_window or expected_output_tokens

    if expected_output_tokens > max_output_window:
        return ContextFitAssessment(
            backend_id=profile.backend_id,
            fit_state="does_not_fit",
            compression_required=False,
            risk_level="high",
            recommended_strategy="reduce_expected_output",
        )

    if total_tokens <= profile.recommended_working_window:
        return ContextFitAssessment(
            backend_id=profile.backend_id,
            fit_state="fits_cleanly",
            compression_required=False,
            risk_level="low",
            recommended_strategy="keep_full_context",
        )

    if total_tokens > profile.max_context_window:
        return ContextFitAssessment(
            backend_id=profile.backend_id,
            fit_state="does_not_fit",
            compression_required=False,
            risk_level="high",
            recommended_strategy="split_task_or_switch_backend",
        )

    quality = (profile.long_context_quality or "").lower()
    if quality == "high":
        return ContextFitAssessment(
            backend_id=profile.backend_id,
            fit_state="fits_with_compression",
            compression_required=True,
            risk_level="medium",
            recommended_strategy=_compression_strategy(profile),
        )

    return ContextFitAssessment(
        backend_id=profile.backend_id,
        fit_state="unsafe_fit",
        compression_required=True,
        risk_level="high",
        recommended_strategy=_compression_strategy(profile),
    )


def _compression_strategy(profile: ContextCapabilityProfile) -> str:
    """Return the preferred compression strategy for a backend profile."""
    if profile.compression_preference:
        return profile.compression_preference
    return "summarize_history_keep_decisions"
