"""Stable execution envelope helpers for runtime contracts."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.models import (
    ExecutionEnvelope,
    LoopPolicy,
    RecoveryDecision,
    RecoveryPayload,
    ReviewOutcome,
    TaskProfile,
    VerificationOutcome,
    VerificationPayload,
)


def build_execution_envelope(
    *,
    task_profile: TaskProfile,
    loop_policy: LoopPolicy,
    artifacts: tuple[str, ...],
    risks: tuple[str, ...] = (),
    next_actions: tuple[str, ...] = (),
) -> ExecutionEnvelope:
    """Build a stable envelope from runtime selection context."""
    verification = VerificationPayload(
        performed=loop_policy.requires_verification,
        passed=not loop_policy.requires_review,
        checks=("loop-policy-selected", "capabilities-resolved"),
        acceptance_criteria_satisfied=not loop_policy.requires_review,
        evidence_refs=(task_profile.task_id,),
    )
    recovery = RecoveryPayload(
        retryable=loop_policy.max_iterations > 1,
        suggested_action="patch" if loop_policy.requires_review else "stop",
        attempt_count=0,
        failure_class="",
        reason="review required before acceptance"
        if loop_policy.requires_review
        else "no recovery needed",
    )
    return ExecutionEnvelope(
        status="warning" if loop_policy.requires_review else "success",
        summary=(
            f"{task_profile.complexity} task using {loop_policy.base_loop}"
            f" with {len(artifacts)} artifact(s)"
        ),
        artifacts=artifacts,
        risks=risks,
        next_actions=next_actions,
        verification=verification,
        recovery=recovery,
    )


def validate_execution_envelope(
    envelope: ExecutionEnvelope,
) -> tuple[bool, tuple[str, ...]]:
    """Validate the stable envelope shape for continuation decisions."""
    errors: list[str] = []
    if not envelope.status:
        errors.append("status is required")
    if not envelope.summary:
        errors.append("summary is required")
    if envelope.status == "warning" and envelope.recovery is None:
        errors.append("warning envelopes require recovery payload")
    if envelope.status in {"success", "warning"} and envelope.verification is None:
        errors.append("verification payload required for non-error envelopes")
    return (len(errors) == 0, tuple(errors))


def synthesize_execution_envelope(
    *,
    base_envelope: ExecutionEnvelope,
    verification_outcome: VerificationOutcome | None = None,
    review_outcome: ReviewOutcome | None = None,
    recovery_decision: RecoveryDecision | None = None,
) -> ExecutionEnvelope:
    """Build the final envelope from the most restrictive available verdict."""
    verification_payload = base_envelope.verification
    if verification_outcome is not None:
        verification_payload = VerificationPayload(
            performed=verification_outcome.performed,
            passed=verification_outcome.passed,
            checks=tuple(check.label for check in verification_outcome.checks),
            acceptance_criteria_satisfied=verification_outcome.acceptance_criteria_satisfied,
            evidence_refs=verification_outcome.evidence_refs,
        )
    recovery_payload = base_envelope.recovery
    if recovery_decision is not None:
        recovery_payload = RecoveryPayload(
            retryable=recovery_decision.action in {"retry", "patch", "replan"},
            suggested_action=recovery_decision.action,
            attempt_count=0,
            failure_class=""
            if recovery_decision.action == "stop"
            else recovery_decision.action,
            reason=recovery_decision.reason,
        )

    status = base_envelope.status
    next_actions = list(base_envelope.next_actions)
    risks = list(base_envelope.risks)
    if review_outcome is not None:
        risks.extend(review_outcome.risk_flags)
    if recovery_decision is not None:
        next_actions = [recovery_decision.action]
        status = (
            "error" if recovery_decision.action in {"escalate", "stop"} else "warning"
        )
    elif review_outcome is not None and not review_outcome.approved:
        next_actions = [review_outcome.recommended_next_action]
        status = "warning"
    elif verification_outcome is not None and not verification_outcome.passed:
        next_actions = ["patch"]
        status = "warning"
    else:
        next_actions = ["continue"]
        status = "success"

    return ExecutionEnvelope(
        status=status,
        summary=base_envelope.summary,
        artifacts=base_envelope.artifacts,
        risks=tuple(dict.fromkeys(risks)),
        next_actions=tuple(next_actions),
        verification=verification_payload,
        review=review_outcome,
        recovery=recovery_payload
        if status != "success" or recovery_decision is not None
        else None,
    )
