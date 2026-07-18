"""Pure, deterministic context packing for candidate backend payloads."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from typing import Literal


ContextSegmentLayer = Literal[
    "core_required",
    "decision_critical",
    "mandatory_artifact",
    "relevant_memory",
    "optional_history",
]
ContextPackStatus = Literal["packed", "blocked"]

_LAYER_PRIORITIES: dict[ContextSegmentLayer, int] = {
    "core_required": 0,
    "decision_critical": 1,
    "mandatory_artifact": 2,
    "relevant_memory": 3,
    "optional_history": 4,
}
_CRITICAL_LAYERS = frozenset({"core_required", "decision_critical"})


@dataclass(frozen=True)
class ContextSegment:
    """An estimated, reference-only unit of context for a candidate payload."""

    reference: str
    token_estimate: int
    layer: ContextSegmentLayer

    def __post_init__(self) -> None:
        """Validate the segment at the package boundary."""
        if not self.reference.strip():
            raise ValueError("reference must not be empty")
        if self.token_estimate < 0:
            raise ValueError("token_estimate must be >= 0")
        if self.layer not in _LAYER_PRIORITIES:
            raise ValueError(f"invalid context segment layer: {self.layer}")


@dataclass(frozen=True)
class ContextPackResult:
    """The deterministic payload projection and any required compression action."""

    status: ContextPackStatus
    input_token_capacity: int
    output_token_reservation: int
    selected_references: tuple[str, ...]
    omitted_references: tuple[str, ...]
    omitted_optional_references: tuple[str, ...]
    critical_references: tuple[str, ...]
    compression_required: bool
    compression_reason: str | None


def pack_context(
    segments: Iterable[ContextSegment],
    *,
    token_budget: int,
    output_token_reservation: int = 0,
) -> ContextPackResult:
    """Pack references into the available input capacity without critical loss.

    Args:
        segments: Context segments in any order.
        token_budget: Total token budget for input context and reserved output.
        output_token_reservation: Tokens retained for the backend response.

    Returns:
        A packed result, or a blocked result when critical context cannot fit.

    Raises:
        ValueError: If capacities are invalid or references are duplicated.
    """
    if token_budget < 0:
        raise ValueError("token_budget must be >= 0")
    if output_token_reservation < 0:
        raise ValueError("output_token_reservation must be >= 0")
    if output_token_reservation > token_budget:
        raise ValueError("output_token_reservation must not exceed token_budget")

    ordered_segments = tuple(
        sorted(
            segments,
            key=lambda segment: (_LAYER_PRIORITIES[segment.layer], segment.reference),
        )
    )
    references = tuple(segment.reference for segment in ordered_segments)
    if len(set(references)) != len(references):
        raise ValueError("segment references must be unique")

    input_token_capacity = token_budget - output_token_reservation
    critical_segments = tuple(
        segment for segment in ordered_segments if segment.layer in _CRITICAL_LAYERS
    )
    critical_tokens = sum(segment.token_estimate for segment in critical_segments)
    critical_references = tuple(segment.reference for segment in critical_segments)

    if critical_tokens > input_token_capacity:
        return ContextPackResult(
            status="blocked",
            input_token_capacity=input_token_capacity,
            output_token_reservation=output_token_reservation,
            selected_references=(),
            omitted_references=references,
            omitted_optional_references=tuple(
                segment.reference
                for segment in ordered_segments
                if segment.layer == "optional_history"
            ),
            critical_references=critical_references,
            compression_required=True,
            compression_reason=(
                "critical context exceeds input token capacity; "
                "compression or escalation is required"
            ),
        )

    selected_references: list[str] = []
    omitted_references: list[str] = []
    used_tokens = 0
    for segment in ordered_segments:
        if used_tokens + segment.token_estimate <= input_token_capacity:
            selected_references.append(segment.reference)
            used_tokens += segment.token_estimate
        else:
            omitted_references.append(segment.reference)

    omitted_optional_references = tuple(
        segment.reference
        for segment in ordered_segments
        if segment.reference in omitted_references
        and segment.layer == "optional_history"
    )
    compression_required = bool(omitted_references)
    return ContextPackResult(
        status="packed",
        input_token_capacity=input_token_capacity,
        output_token_reservation=output_token_reservation,
        selected_references=tuple(selected_references),
        omitted_references=tuple(omitted_references),
        omitted_optional_references=omitted_optional_references,
        critical_references=critical_references,
        compression_required=compression_required,
        compression_reason=(
            "segments omitted because they exceed input token capacity"
            if compression_required
            else None
        ),
    )
