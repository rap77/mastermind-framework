"""Unit tests for context window capability and fit evaluation."""

import pytest

from mastermind_cli.window_scheduler.context_fit import (
    ContextCapabilityProfile,
    assess_context_fit,
)


def make_profile(**overrides: object) -> ContextCapabilityProfile:
    """Build a default capability profile for tests."""
    data: dict[str, object] = {
        "backend_id": "codex-sub-01",
        "max_context_window": 200_000,
        "recommended_working_window": 120_000,
        "max_output_window": 32_000,
        "long_context_quality": "medium",
        "compression_preference": "artifact_first",
    }
    data.update(overrides)
    return ContextCapabilityProfile(**data)


def test_assess_context_fit_returns_fits_cleanly_within_working_window() -> None:
    """Contexts inside the working window should fit cleanly."""
    result = assess_context_fit(
        make_profile(),
        required_context_tokens=80_000,
        expected_output_tokens=10_000,
    )

    assert result.fit_state == "fits_cleanly"
    assert result.compression_required is False
    assert result.risk_level == "low"


def test_assess_context_fit_returns_fits_with_compression_for_high_quality_long_context() -> (
    None
):
    """Contexts above working window but below max can fit with compression."""
    result = assess_context_fit(
        make_profile(long_context_quality="high"),
        required_context_tokens=130_000,
        expected_output_tokens=10_000,
    )

    assert result.fit_state == "fits_with_compression"
    assert result.compression_required is True
    assert result.risk_level == "medium"
    assert result.recommended_strategy == "artifact_first"


def test_assess_context_fit_returns_unsafe_fit_for_medium_quality_long_context() -> (
    None
):
    """Contexts above working window can be unsafe if long-context quality is weaker."""
    result = assess_context_fit(
        make_profile(long_context_quality="medium"),
        required_context_tokens=130_000,
        expected_output_tokens=10_000,
    )

    assert result.fit_state == "unsafe_fit"
    assert result.compression_required is True
    assert result.risk_level == "high"


def test_assess_context_fit_returns_does_not_fit_when_total_exceeds_max_window() -> (
    None
):
    """Contexts beyond the max window should be rejected."""
    result = assess_context_fit(
        make_profile(),
        required_context_tokens=190_000,
        expected_output_tokens=20_000,
    )

    assert result.fit_state == "does_not_fit"
    assert result.compression_required is False
    assert result.recommended_strategy == "split_task_or_switch_backend"


def test_assess_context_fit_returns_does_not_fit_when_output_window_is_exceeded() -> (
    None
):
    """Expected output larger than the backend output window should not fit."""
    result = assess_context_fit(
        make_profile(max_output_window=8_000),
        required_context_tokens=40_000,
        expected_output_tokens=10_000,
    )

    assert result.fit_state == "does_not_fit"
    assert result.recommended_strategy == "reduce_expected_output"


def test_assess_context_fit_requires_capability_metadata() -> None:
    """Missing capability metadata should degrade to unsafe fit."""
    result = assess_context_fit(
        make_profile(
            max_context_window=None,
            recommended_working_window=None,
        ),
        required_context_tokens=40_000,
        expected_output_tokens=5_000,
    )

    assert result.fit_state == "unsafe_fit"
    assert result.recommended_strategy == "collect_capability_profile"


@pytest.mark.parametrize(
    ("required_context_tokens", "expected_output_tokens"),
    [(-1, 1), (1, -1)],
)
def test_assess_context_fit_rejects_negative_token_counts(
    required_context_tokens: int,
    expected_output_tokens: int,
) -> None:
    """Negative token counts should raise a descriptive validation error."""
    with pytest.raises(ValueError):
        assess_context_fit(
            make_profile(),
            required_context_tokens=required_context_tokens,
            expected_output_tokens=expected_output_tokens,
        )
