"""Runtime contract endpoints for policy and harness registry data."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from mastermind_cli.orchestrator.runtime_contracts.capability_registry import (
    CapabilityRegistry,
)

router = APIRouter()


class PolicyCapabilityResponse(BaseModel):
    """Policy metadata exposed to the web UI."""

    capability_id: str = Field(..., description="Canonical policy identifier")
    label: str = Field(..., description="Display label")
    summary: str = Field(..., description="Short UI summary")
    compatible_harnesses: list[str] = Field(
        default_factory=list,
        description="Harness identifiers where this policy is valid",
    )


class PolicyCatalogResponse(BaseModel):
    """List of policy capabilities available to the current runtime."""

    policies: list[PolicyCapabilityResponse] = Field(
        default_factory=list, description="Canonical policy capabilities"
    )


_POLICY_SUMMARIES: dict[str, str] = {
    "policy-clean-code": "Keep the implementation readable, small, and easy to change.",
    "policy-security": "Treat untrusted input as hostile and prefer safe defaults.",
    "policy-architecture": "Preserve layer boundaries and avoid coupling concerns.",
    "policy-naming": "Use explicit names that reflect intent and scope.",
    "policy-testing-discipline": "Keep behavior covered with stable, focused tests.",
}


@router.get("/policies", response_model=PolicyCatalogResponse)
async def list_policies() -> PolicyCatalogResponse:
    """Return the canonical policy catalog used by project doctrine."""
    registry = CapabilityRegistry()
    policies = [
        PolicyCapabilityResponse(
            capability_id=capability.capability_id,
            label=capability.label,
            summary=_POLICY_SUMMARIES.get(
                capability.capability_id, capability.capability_id
            ),
            compatible_harnesses=list(capability.compatible_harnesses),
        )
        for capability in registry.policy_definitions()
    ]
    return PolicyCatalogResponse(policies=policies)
