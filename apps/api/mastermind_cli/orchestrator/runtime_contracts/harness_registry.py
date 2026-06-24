"""Typed harness inventory for runtime contract selection."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.models import (
    CapabilitySet,
    HarnessDefinition,
)


class HarnessRegistry:
    """Resolve compatible harness definitions from a static inventory."""

    def __init__(
        self, definitions: tuple[HarnessDefinition, ...] | None = None
    ) -> None:
        """Initialize the registry with the provided or default inventory."""
        self._definitions = definitions or self._default_definitions()

    def resolve_for_capabilities(
        self, capability_set: CapabilitySet
    ) -> tuple[HarnessDefinition, ...]:
        """Return harnesses referenced by the selected capabilities."""
        allowed = {
            harness_id
            for capability in capability_set.harnesses + capability_set.verifiers
            for harness_id in capability.compatible_harnesses
        }
        if capability_set.recovery_policies:
            allowed.add("recovery-default")
        return tuple(
            definition
            for definition in self._definitions
            if definition.harness_id in allowed
        )

    def _default_definitions(self) -> tuple[HarnessDefinition, ...]:
        """Return the MVP harness inventory."""
        return (
            HarnessDefinition(
                harness_id="execution-default",
                name="Execution Harness",
                category="execution",
                purpose="Run the requested brains and capture outputs.",
                supported_loops=("single-pass", "execute+verify-light", "review"),
                required_inputs=("brief", "brain_ids", "task_profile"),
                output_contract="ExecutionEnvelope",
            ),
            HarnessDefinition(
                harness_id="verification-default",
                name="Verification Harness",
                category="verification",
                purpose="Apply deterministic checks before acceptance.",
                supported_loops=("execute+verify-light",),
                required_inputs=("execution_result", "criteria"),
                output_contract="VerificationPayload",
            ),
            HarnessDefinition(
                harness_id="review-default",
                name="Review Harness",
                category="review",
                purpose="Provide maker-checker separation for medium/high risk work.",
                supported_loops=("review",),
                required_inputs=("execution_result", "review_rubric"),
                output_contract="ExecutionEnvelope",
            ),
            HarnessDefinition(
                harness_id="recovery-default",
                name="Recovery Harness",
                category="recovery",
                purpose="Escalate through the bounded recovery ladder.",
                supported_loops=("retry", "patch", "replan", "escalate"),
                required_inputs=("execution_result", "attempt_history"),
                output_contract="RecoveryPayload",
            ),
        )
