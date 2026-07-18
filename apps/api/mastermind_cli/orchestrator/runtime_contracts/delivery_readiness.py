"""Domain-agnostic readiness evaluation for adaptive delivery requests."""

from __future__ import annotations

from .delivery_models import (
    AdaptiveDeliveryRequest,
    DeliveryReadinessProfile,
    DeliveryReadinessStatus,
)


class DeliveryReadinessEvaluator:
    """Evaluate whether an approved request can safely enter decomposition."""

    def evaluate(
        self,
        request: AdaptiveDeliveryRequest,
        *,
        adapter_id: str | None,
        available_permissions: frozenset[str],
        evaluable_criteria: frozenset[str],
        available_dependency_refs: frozenset[str],
        available_checkpoint_refs: frozenset[str],
    ) -> DeliveryReadinessProfile:
        """Return deterministic blockers and escalation state for ``request``."""
        if adapter_id is not None and not adapter_id.strip():
            raise ValueError("adapter_id must not be empty")

        blocker_refs: list[str] = []
        rationale: list[str] = []
        escalated = False

        if adapter_id is None:
            blocker_refs.append("adapter:not-resolved")
            rationale.append("No compatible domain adapter was resolved")
            escalated = True

        permissions_compatible = not request.requires_write or (
            "write" in available_permissions
        )
        if not permissions_compatible:
            blocker_refs.append("permission:write")
            rationale.append("Write permission is required for mutating delivery")

        for criterion in request.acceptance_criteria:
            if criterion not in evaluable_criteria:
                blocker_refs.append(f"acceptance-criterion:{criterion}")
                rationale.append(f"Acceptance criterion is not evaluable: {criterion}")

        if (
            request.checkpoint_ref is not None
            and request.checkpoint_ref not in available_checkpoint_refs
        ):
            blocker_refs.append(f"checkpoint:{request.checkpoint_ref}")
            rationale.append(
                f"Requested checkpoint is unavailable: {request.checkpoint_ref}"
            )
            escalated = True

        for dependency_ref in request.dependency_refs:
            if dependency_ref not in available_dependency_refs:
                blocker_refs.append(f"dependency:{dependency_ref}")
                rationale.append(
                    f"Declared dependency is unavailable: {dependency_ref}"
                )

        status: DeliveryReadinessStatus
        if escalated:
            status = "escalated"
        elif blocker_refs:
            status = "blocked"
        else:
            status = "ready"
            rationale.append("All delivery readiness prerequisites are satisfied")

        return DeliveryReadinessProfile(
            objective_id=request.objective_id,
            status=status,
            adapter_id=adapter_id,
            permissions_compatible=permissions_compatible,
            blocker_refs=tuple(blocker_refs),
            rationale=tuple(rationale),
        )
