"""Deterministic routing for evidence intake, canonization, and AI-DLC handoff."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

EvidenceClarity = Literal["clear", "partial", "ambiguous"]
UncertaintyLevel = Literal["low", "medium", "high"]
RiskLevel = Literal["low", "medium", "high", "critical"]
ObjectiveClass = Literal["analysis", "canonization", "spec", "implementation"]
EvidenceHarness = Literal[
    "evidence-intake-only",
    "evidence-intake-canonization",
    "full-evidence-loop",
    "ai-dlc-harness",
]
EvidenceLoop = Literal[
    "tool-loop",
    "goal-loop",
    "verification-loop",
    "reflection-loop",
]


@dataclass(frozen=True, slots=True)
class EvidenceSelectionRequest:
    """Normalized input for evidence routing."""

    objective: str
    source_clarity: EvidenceClarity = "partial"
    uncertainty: UncertaintyLevel = "medium"
    gap_count: int = 0
    needs_interview: bool = False
    risk_level: RiskLevel = "medium"
    token_budget: int = 2_000
    readiness_gate: str | None = None
    readiness_score: float | None = None
    objective_class: ObjectiveClass | None = None


@dataclass(frozen=True, slots=True)
class EvidenceSelectionResult:
    """Deterministic routing result for evidence workflows."""

    selected_harness: EvidenceHarness
    selected_loop: EvidenceLoop
    selected_brain: str | None
    reasons: tuple[str, ...]
    risks: tuple[str, ...]
    next_actions: tuple[str, ...]
    alternatives_rejected: tuple[str, ...] = field(default_factory=tuple)
    readiness_gate: str | None = None
    readiness_score: float | None = None


class EvidenceHarnessSelector:
    """Choose the minimum sufficient evidence harness and loop."""

    def classify_objective(self, objective: str) -> ObjectiveClass:
        """Classify an objective into a small routing bucket."""
        text = objective.lower()
        if any(term in text for term in ("implement", "build", "code", "ship")):
            return "implementation"
        if any(
            term in text for term in ("spec", "specification", "requirements", "design")
        ):
            return "spec"
        if any(term in text for term in ("canon", "canonical", "normalize", "distill")):
            return "canonization"
        return "analysis"

    def select(self, request: EvidenceSelectionRequest) -> EvidenceSelectionResult:
        """Select the smallest evidence route that satisfies the request."""
        objective_class = request.objective_class or self.classify_objective(
            request.objective
        )
        score = (
            float(request.readiness_score)
            if request.readiness_score is not None
            else None
        )
        gate = request.readiness_gate
        ready = gate == "ready" or (score is not None and score >= 80.0)
        conditionally_ready = gate == "conditionally_ready" or (
            score is not None and score >= 65.0
        )
        low_readiness = gate in {"not_ready", "blocked"} or (
            score is not None and score < 65.0
        )
        high_uncertainty = request.uncertainty == "high"
        interview_required = request.needs_interview or high_uncertainty
        many_gaps = request.gap_count >= 2

        if ready and objective_class in {"spec", "implementation"}:
            return EvidenceSelectionResult(
                selected_harness="ai-dlc-harness",
                selected_loop="goal-loop",
                selected_brain=None,
                reasons=(
                    "ready-for-downstream-work",
                    f"objective_class={objective_class}",
                    f"readiness_gate={gate or 'unset'}",
                    f"readiness_score={score if score is not None else 'unset'}",
                ),
                risks=("handoff_requires_traceability",),
                next_actions=("launch_ai_dlc_workflow",),
                alternatives_rejected=(
                    "evidence-intake-only",
                    "evidence-intake-canonization",
                    "full-evidence-loop",
                ),
                readiness_gate=gate,
                readiness_score=score,
            )

        if low_readiness or interview_required or many_gaps:
            if interview_required or many_gaps or request.source_clarity == "ambiguous":
                return EvidenceSelectionResult(
                    selected_harness="full-evidence-loop",
                    selected_loop="verification-loop",
                    selected_brain=None,
                    reasons=(
                        "evidence-incomplete",
                        f"source_clarity={request.source_clarity}",
                        f"gap_count={request.gap_count}",
                        f"uncertainty={request.uncertainty}",
                        f"readiness_gate={gate or 'unset'}",
                    ),
                    risks=("interview_or_gap_resolution_required",),
                    next_actions=("detect_gaps", "ask_clarifying_questions"),
                    alternatives_rejected=(
                        "evidence-intake-only",
                        "evidence-intake-canonization",
                    ),
                    readiness_gate=gate,
                    readiness_score=score,
                )

            return EvidenceSelectionResult(
                selected_harness="evidence-intake-canonization",
                selected_loop="goal-loop",
                selected_brain=None,
                reasons=(
                    "partial-evidence-with-controlled-risk",
                    f"source_clarity={request.source_clarity}",
                    f"gap_count={request.gap_count}",
                    f"readiness_gate={gate or 'unset'}",
                ),
                risks=("canonization_may_need_followup",),
                next_actions=("canonize_sources", "record_deltas"),
                alternatives_rejected=("evidence-intake-only", "full-evidence-loop"),
                readiness_gate=gate,
                readiness_score=score,
            )

        if request.source_clarity == "partial" and (
            conditionally_ready or request.gap_count <= 1
        ):
            return EvidenceSelectionResult(
                selected_harness="evidence-intake-canonization",
                selected_loop="goal-loop",
                selected_brain=None,
                reasons=(
                    "partial-evidence-with-controlled-risk",
                    f"source_clarity={request.source_clarity}",
                    f"gap_count={request.gap_count}",
                    f"readiness_gate={gate or 'unset'}",
                ),
                risks=("canonization_may_need_followup",),
                next_actions=("canonize_sources", "record_deltas"),
                alternatives_rejected=("evidence-intake-only", "full-evidence-loop"),
                readiness_gate=gate,
                readiness_score=score,
            )

        if request.source_clarity == "clear" and request.gap_count == 0:
            selected_harness: EvidenceHarness = "evidence-intake-only"
            selected_loop: EvidenceLoop = (
                "tool-loop" if request.token_budget < 1_000 else "goal-loop"
            )
            return EvidenceSelectionResult(
                selected_harness=selected_harness,
                selected_loop=selected_loop,
                selected_brain=None,
                reasons=(
                    "clear-source-minimum-path",
                    f"token_budget={request.token_budget}",
                    f"readiness_gate={gate or 'unset'}",
                ),
                risks=(),
                next_actions=("extract_summary", "store_snapshot"),
                alternatives_rejected=(
                    "evidence-intake-canonization",
                    "full-evidence-loop",
                    "ai-dlc-harness",
                ),
                readiness_gate=gate,
                readiness_score=score,
            )

        return EvidenceSelectionResult(
            selected_harness="evidence-intake-canonization",
            selected_loop="goal-loop",
            selected_brain=None,
            reasons=(
                "default-minimum-canonization",
                f"source_clarity={request.source_clarity}",
                f"readiness_gate={gate or 'unset'}",
            ),
            risks=("followup_may_be_needed",),
            next_actions=("canonize_sources",),
            alternatives_rejected=("evidence-intake-only", "full-evidence-loop"),
            readiness_gate=gate,
            readiness_score=score,
        )
