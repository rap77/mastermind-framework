"""Local rubric-driven review harness for runtime contracts."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.models import (
    ExecutionEnvelope,
    LoopPolicy,
    ReviewOutcome,
    ReviewRubric,
    TaskProfile,
    VerificationOutcome,
)


class ReviewRubricResolver:
    """Resolve the minimum rubric for maker-checker review."""

    def resolve(
        self, task_profile: TaskProfile, loop_policy: LoopPolicy
    ) -> ReviewRubric:
        """Return a deterministic rubric for the given control policy."""
        return ReviewRubric(
            rubric_id=f"review-{task_profile.complexity}",
            criteria=(
                "artifacts_sufficient",
                "verification_passed",
                "risks_addressed",
            ),
            requires_verification_pass=loop_policy.requires_verification,
            blocks_self_approval=loop_policy.requires_review,
        )


class ReviewHarness:
    """Apply a deterministic rubric over the verified result."""

    def review(
        self,
        base_envelope: ExecutionEnvelope,
        verification_outcome: VerificationOutcome,
        review_rubric: ReviewRubric,
    ) -> ReviewOutcome:
        """Return the aggregated review verdict."""
        findings: list[str] = []
        risk_flags: list[str] = []
        approved = True
        if review_rubric.requires_verification_pass and not verification_outcome.passed:
            approved = False
            findings.append("verification_failed")
            risk_flags.append("verification_blocker")
        if not base_envelope.artifacts:
            approved = False
            findings.append("artifacts_missing")
            risk_flags.append("insufficient_evidence")
        if base_envelope.risks:
            risk_flags.extend(base_envelope.risks)
        return ReviewOutcome(
            performed=True,
            approved=approved,
            findings=tuple(findings),
            risk_flags=tuple(dict.fromkeys(risk_flags)),
            recommended_next_action="continue" if approved else "patch",
        )
