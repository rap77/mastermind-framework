"""Deterministic capability inventory for runtime contract selection."""

from __future__ import annotations

from mastermind_cli.orchestrator.runtime_contracts.models import (
    CapabilityDefinition,
    CapabilitySet,
    TaskProfile,
)


class CapabilityRegistry:
    """Resolve compatible capabilities from a small static inventory."""

    def __init__(
        self, definitions: tuple[CapabilityDefinition, ...] | None = None
    ) -> None:
        """Initialize the registry with the provided or default inventory."""
        self._definitions = definitions or self._default_definitions()

    def resolve_for_task(self, task_profile: TaskProfile) -> CapabilitySet:
        """Filter the inventory by task compatibility and required traits."""
        compatible = tuple(
            definition
            for definition in self._definitions
            if task_profile.complexity in definition.compatible_task_classes
            and (not definition.requires_checker or task_profile.requires_checker)
            and (
                not definition.requires_fresh_context
                or task_profile.requires_fresh_context
            )
        )
        return CapabilitySet(
            harnesses=tuple(c for c in compatible if c.category == "harness"),
            loops=tuple(c for c in compatible if c.category == "loop"),
            brains=tuple(c for c in compatible if c.category == "brain"),
            skills=tuple(c for c in compatible if c.category == "skill"),
            mcps=tuple(c for c in compatible if c.category == "mcp"),
            commands=tuple(c for c in compatible if c.category == "command"),
            verifiers=tuple(c for c in compatible if c.category == "verifier"),
            recovery_policies=tuple(
                c for c in compatible if c.category == "recovery_policy"
            ),
            policies=tuple(c for c in compatible if c.category == "policy"),
        )

    def _default_definitions(self) -> tuple[CapabilityDefinition, ...]:
        """Return the MVP capability inventory."""
        return (
            CapabilityDefinition(
                capability_id="execution-basic",
                category="harness",
                label="Execution Harness",
                goal_tags=("execute", "default"),
                cost_level="low",
                risk_level="low",
                prerequisites=(),
                compatible_harnesses=("execution-default",),
                compatible_task_classes=("simple", "medium", "complex"),
            ),
            CapabilityDefinition(
                capability_id="verification-light",
                category="verifier",
                label="Verification Harness",
                goal_tags=("verify", "deterministic"),
                cost_level="low",
                risk_level="low",
                prerequisites=(),
                compatible_harnesses=("verification-default",),
                compatible_task_classes=("simple", "medium", "complex"),
            ),
            CapabilityDefinition(
                capability_id="review-maker-checker",
                category="harness",
                label="Review Harness",
                goal_tags=("review", "maker-checker"),
                cost_level="medium",
                risk_level="low",
                prerequisites=("verification-light",),
                compatible_harnesses=("review-default",),
                compatible_task_classes=("medium", "complex"),
                requires_checker=True,
            ),
            CapabilityDefinition(
                capability_id="loop-single-pass",
                category="loop",
                label="Single Pass Loop",
                goal_tags=("single-pass",),
                cost_level="low",
                risk_level="low",
                prerequisites=(),
                compatible_harnesses=("execution-default",),
                compatible_task_classes=("simple",),
            ),
            CapabilityDefinition(
                capability_id="loop-verify-light",
                category="loop",
                label="Execute Then Verify",
                goal_tags=("verify-light",),
                cost_level="low",
                risk_level="low",
                prerequisites=("verification-light",),
                compatible_harnesses=("execution-default", "verification-default"),
                compatible_task_classes=("simple", "medium", "complex"),
            ),
            CapabilityDefinition(
                capability_id="loop-review",
                category="loop",
                label="Independent Review",
                goal_tags=("review",),
                cost_level="medium",
                risk_level="low",
                prerequisites=("review-maker-checker",),
                compatible_harnesses=("execution-default", "review-default"),
                compatible_task_classes=("medium", "complex"),
                requires_checker=True,
            ),
            CapabilityDefinition(
                capability_id="recovery-bounded",
                category="recovery_policy",
                label="Bounded Recovery Ladder",
                goal_tags=("recovery", "bounded"),
                cost_level="low",
                risk_level="low",
                prerequisites=(),
                compatible_harnesses=("recovery-default",),
                compatible_task_classes=("simple", "medium", "complex"),
            ),
            CapabilityDefinition(
                capability_id="mcp-fresh-context",
                category="mcp",
                label="Fresh Context MCP",
                goal_tags=("research", "fresh-context"),
                cost_level="medium",
                risk_level="medium",
                prerequisites=(),
                compatible_harnesses=("execution-default",),
                compatible_task_classes=("medium", "complex"),
                requires_fresh_context=True,
            ),
            CapabilityDefinition(
                capability_id="policy-clean-code",
                category="policy",
                label="Clean Code Policy",
                goal_tags=("clean-code", "style", "maintainability"),
                cost_level="low",
                risk_level="low",
                prerequisites=(),
                compatible_harnesses=(
                    "execution-default",
                    "verification-default",
                    "review-default",
                    "recovery-default",
                ),
                compatible_task_classes=("simple", "medium", "complex"),
            ),
        )
