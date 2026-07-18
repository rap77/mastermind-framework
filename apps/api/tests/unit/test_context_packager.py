"""Unit tests for deterministic context payload packing."""

import pytest

from mastermind_cli.window_scheduler.context_packager import (
    ContextSegment,
    pack_context,
)


def test_pack_context_orders_segments_by_priority_then_reference() -> None:
    """Packing should be deterministic regardless of input ordering."""
    result = pack_context(
        [
            ContextSegment("history-b", 10, "optional_history"),
            ContextSegment("memory-a", 10, "relevant_memory"),
            ContextSegment("decision-z", 10, "decision_critical"),
            ContextSegment("core-b", 10, "core_required"),
            ContextSegment("artifact-a", 10, "mandatory_artifact"),
            ContextSegment("core-a", 10, "core_required"),
            ContextSegment("decision-a", 10, "decision_critical"),
        ],
        token_budget=70,
    )

    assert result.status == "packed"
    assert result.selected_references == (
        "core-a",
        "core-b",
        "decision-a",
        "decision-z",
        "artifact-a",
        "memory-a",
        "history-b",
    )
    assert result.compression_required is False
    assert result.compression_reason is None


def test_pack_context_omits_optional_history_with_explicit_reason() -> None:
    """Optional omissions should preserve a successful, traceable result."""
    result = pack_context(
        [
            ContextSegment("optional-history", 30, "optional_history"),
            ContextSegment("core", 50, "core_required"),
        ],
        token_budget=70,
        output_token_reservation=10,
    )

    assert result.status == "packed"
    assert result.input_token_capacity == 60
    assert result.output_token_reservation == 10
    assert result.selected_references == ("core",)
    assert result.omitted_optional_references == ("optional-history",)
    assert result.compression_required is True
    assert result.compression_reason is not None


def test_pack_context_blocks_instead_of_dropping_critical_segments() -> None:
    """Critical context that cannot fit must produce no usable partial payload."""
    result = pack_context(
        [
            ContextSegment("decision", 40, "decision_critical"),
            ContextSegment("core", 50, "core_required"),
            ContextSegment("optional-history", 10, "optional_history"),
        ],
        token_budget=80,
    )

    assert result.status == "blocked"
    assert result.selected_references == ()
    assert result.critical_references == ("core", "decision")
    assert result.compression_required is True
    assert result.compression_reason is not None


@pytest.mark.parametrize(
    ("reference", "token_estimate", "layer", "message"),
    [
        ("", 1, "core_required", "reference must not be empty"),
        ("core", -1, "core_required", "token_estimate must be >= 0"),
        ("core", 1, "unknown", "invalid context segment layer"),
    ],
)
def test_context_segment_rejects_invalid_inputs(
    reference: str,
    token_estimate: int,
    layer: str,
    message: str,
) -> None:
    """Segment contracts should reject invalid values at their boundary."""
    with pytest.raises(ValueError, match=message):
        ContextSegment(reference, token_estimate, layer)


def test_pack_context_rejects_duplicate_segment_references() -> None:
    """A payload cannot have ambiguous duplicate references."""
    with pytest.raises(ValueError, match="segment references must be unique"):
        pack_context(
            [
                ContextSegment("checkpoint", 10, "core_required"),
                ContextSegment("checkpoint", 10, "optional_history"),
            ],
            token_budget=100,
        )
