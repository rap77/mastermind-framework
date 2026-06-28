"""Deterministic harness core for runtime contract execution."""

from __future__ import annotations

from dataclasses import dataclass

from .capability_registry import CapabilityRegistry
from .envelope import (
    build_execution_envelope,
    synthesize_execution_envelope,
    validate_execution_envelope,
)
from .harness_registry import HarnessRegistry
from .loop_selector import LoopSelector
from .models import (
    RuntimeRequest,
    RuntimeExecutionResult,
    RuntimeSelection,
    VerificationOutcome,
    ReviewOutcome,
    RecoveryDecision,
)
from .recovery import FailureClassifier, RecoveryHarness
from .review import ReviewHarness, ReviewRubricResolver
from .verification import VerificationHarness


@dataclass(frozen=True, slots=True)
class HarnessCore:
    """Compose deterministic selection, verification, review, and recovery."""

    selector: LoopSelector = LoopSelector()
    capability_registry: CapabilityRegistry = CapabilityRegistry()
    harness_registry: HarnessRegistry = HarnessRegistry()
    verification_harness: VerificationHarness = VerificationHarness()
    review_rubric_resolver: ReviewRubricResolver = ReviewRubricResolver()
    review_harness: ReviewHarness = ReviewHarness()
    failure_classifier: FailureClassifier = FailureClassifier()
    recovery_harness: RecoveryHarness = RecoveryHarness()

    def select_runtime(
        self,
        request: RuntimeRequest,
    ) -> RuntimeSelection:
        """Select the deterministic runtime contract for a request."""
        if not request.brain_ids:
            raise ValueError("Runtime request must include at least one brain id")
        task_profile = self.selector.classify_task(
            request.brief,
            list(request.brain_ids),
        )
        capability_set = self.capability_registry.resolve_for_task(task_profile)
        harnesses = self.harness_registry.resolve_for_capabilities(capability_set)
        if not harnesses:
            raise ValueError("No compatible runtime harnesses available")
        loop_policy = self.selector.select_loop(
            task_profile,
            capability_set,
            evidence_readiness_score=request.evidence_readiness_score,
            evidence_readiness_gate=request.evidence_readiness_gate,
        )
        rationale = list(loop_policy.rationale)
        resolved_memory_snapshot = request.memory_snapshot
        if resolved_memory_snapshot is not None and resolved_memory_snapshot.open_gaps:
            rationale.extend(
                f"memory_gap={gap}" for gap in resolved_memory_snapshot.open_gaps
            )
        return RuntimeSelection(
            task_profile=task_profile,
            capability_set=capability_set,
            harnesses=harnesses,
            loop_policy=loop_policy,
            memory_snapshot=resolved_memory_snapshot,
            rationale=tuple(rationale),
        )

    def build_execution_result(
        self,
        selection: RuntimeSelection,
        *,
        artifacts: tuple[str, ...],
        risks: tuple[str, ...] = (),
        next_actions: tuple[str, ...] = (),
    ) -> RuntimeExecutionResult:
        """Build and validate the canonical execution result for a selection."""
        base_envelope = build_execution_envelope(
            task_profile=selection.task_profile,
            loop_policy=selection.loop_policy,
            artifacts=artifacts,
            risks=risks,
            next_actions=next_actions,
        )
        verification_outcome: VerificationOutcome | None = None
        review_outcome: ReviewOutcome | None = None
        recovery_decision: RecoveryDecision | None = None

        if selection.loop_policy.requires_verification:
            verification_outcome = self.verification_harness.verify(
                base_envelope, selection.task_profile
            )
        if selection.loop_policy.requires_review:
            review_rubric = self.review_rubric_resolver.resolve(
                selection.task_profile,
                selection.loop_policy,
            )
            review_outcome = self.review_harness.review(
                base_envelope,
                verification_outcome
                if verification_outcome is not None
                else VerificationOutcome(
                    performed=False,
                    passed=False,
                    checks=(),
                    acceptance_criteria_satisfied=False,
                ),
                review_rubric,
            )

        failure_record = self.failure_classifier.classify(
            base_envelope=base_envelope,
            verification_outcome=verification_outcome,
            review_outcome=review_outcome,
        )
        if failure_record is not None:
            recovery_decision = self.recovery_harness.decide(
                failure_record,
                selection.loop_policy,
            )

        execution_envelope = synthesize_execution_envelope(
            base_envelope=base_envelope,
            verification_outcome=verification_outcome,
            review_outcome=review_outcome,
            recovery_decision=recovery_decision,
        )
        valid, errors = validate_execution_envelope(execution_envelope)
        if not valid:
            raise ValueError("Invalid runtime execution envelope: " + "; ".join(errors))

        return RuntimeExecutionResult(
            selection=selection,
            base_envelope=base_envelope,
            verification_outcome=verification_outcome,
            review_outcome=review_outcome,
            recovery_decision=recovery_decision,
            execution_envelope=execution_envelope,
        )
