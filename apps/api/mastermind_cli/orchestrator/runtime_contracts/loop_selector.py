"""Task profiling and deterministic loop selection for runtime contracts."""

from __future__ import annotations

from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.runtime_contracts.models import (
    AcceptanceMode,
    CapabilitySet,
    Complexity,
    LoopPolicy,
    RiskLevel,
    SignalLevel,
    TaskProfile,
)


class LoopSelector:
    """Classify tasks and choose the minimum sufficient control policy."""

    RISK_TERMS = ("prod", "production", "delete", "migrate", "security", "payment")
    FRESH_CONTEXT_TERMS = ("latest", "actual", "current", "research", "investigate")
    SUBJECTIVE_TERMS = ("design", "brand", "ux", "copy", "creative")

    def classify_task(self, brief: Brief, brain_ids: list[str]) -> TaskProfile:
        """Build a normalized task profile from brief text and requested brains."""
        text = " ".join(
            [
                brief.problem_statement,
                brief.context,
                " ".join(brief.constraints),
                brief.target_audience or "",
            ]
        ).lower()
        requires_write = any(
            term in text for term in ("build", "create", "implement", "edit", "fix")
        )
        requires_fresh_context = any(term in text for term in self.FRESH_CONTEXT_TERMS)
        subjectivity: SignalLevel = (
            "high"
            if any(term in text for term in self.SUBJECTIVE_TERMS)
            else "medium"
            if len(brain_ids) > 1
            else "low"
        )
        verifiability: SignalLevel = (
            "high"
            if any(term in text for term in ("test", "validate", "metric", "api"))
            else "medium"
            if requires_write
            else "low"
        )
        risk_level: RiskLevel = (
            "high"
            if any(term in text for term in self.RISK_TERMS)
            else "medium"
            if requires_write or len(brain_ids) > 1
            else "low"
        )
        complexity: Complexity = (
            "complex"
            if len(brain_ids) >= 3 or risk_level == "high"
            else "medium"
            if len(brain_ids) == 2 or requires_fresh_context or requires_write
            else "simple"
        )
        requires_checker = complexity != "simple" or risk_level in ("high", "critical")
        acceptance_mode: AcceptanceMode = (
            "subjective"
            if subjectivity == "high"
            else "deterministic"
            if verifiability == "high"
            else "mixed"
        )
        reasons = [
            f"brain_count={len(brain_ids)}",
            f"requires_write={requires_write}",
            f"requires_fresh_context={requires_fresh_context}",
            f"risk_level={risk_level}",
        ]
        return TaskProfile(
            task_id=f"runtime-{abs(hash((brief.problem_statement, tuple(brain_ids))))}",
            complexity=complexity,
            risk_level=risk_level,
            verifiability=verifiability,
            subjectivity=subjectivity,
            requires_write=requires_write,
            requires_network=requires_fresh_context,
            requires_fresh_context=requires_fresh_context,
            requires_checker=requires_checker,
            acceptance_mode=acceptance_mode,
            reasons=tuple(reasons),
        )

    def select_loop(
        self,
        task_profile: TaskProfile,
        capability_set: CapabilitySet,
    ) -> LoopPolicy:
        """Select a deterministic loop policy from the task profile."""
        if task_profile.complexity == "simple" and not task_profile.requires_checker:
            return LoopPolicy(
                base_loop="single-pass",
                additional_loops=(),
                max_iterations=1,
                time_budget_ms=5_000,
                tool_budget=1,
                requires_review=False,
                requires_verification=False,
                recovery_policy_id="recovery-bounded",
                rationale=("simple-task", "minimum-sufficient-control"),
            )

        has_review = any(
            capability.capability_id == "review-maker-checker"
            for capability in capability_set.harnesses
        )
        additional_loops = ["verify-light"]
        requires_review = task_profile.requires_checker and has_review
        if requires_review:
            additional_loops.append("review")
        return LoopPolicy(
            base_loop="execute+verify-light",
            additional_loops=tuple(additional_loops),
            max_iterations=2 if task_profile.complexity == "medium" else 3,
            time_budget_ms=15_000 if task_profile.complexity == "medium" else 30_000,
            tool_budget=2 if task_profile.complexity == "medium" else 4,
            requires_review=requires_review,
            requires_verification=True,
            recovery_policy_id="recovery-bounded",
            rationale=(
                "minimum-sufficient-control",
                f"complexity={task_profile.complexity}",
                f"requires_checker={task_profile.requires_checker}",
            ),
        )
