"""Typed runtime contract models for orchestrator control selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal


Complexity = Literal["simple", "medium", "complex"]
RiskLevel = Literal["low", "medium", "high", "critical"]
SignalLevel = Literal["low", "medium", "high"]
AcceptanceMode = Literal["deterministic", "mixed", "subjective"]
HarnessCategory = Literal["execution", "verification", "review", "recovery"]
CapabilityCategory = Literal[
    "harness",
    "loop",
    "brain",
    "skill",
    "mcp",
    "command",
    "verifier",
    "recovery_policy",
]
EnvelopeStatus = Literal["success", "warning", "error"]
RecoveryAction = Literal["retry", "patch", "replan", "escalate", "stop"]


@dataclass(frozen=True, slots=True)
class TaskProfile:
    """Normalized task profile used for loop and capability selection."""

    task_id: str
    complexity: Complexity
    risk_level: RiskLevel
    verifiability: SignalLevel
    subjectivity: SignalLevel
    requires_write: bool
    requires_network: bool
    requires_fresh_context: bool
    requires_checker: bool
    acceptance_mode: AcceptanceMode
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class HarnessDefinition:
    """Typed definition for a supported harness."""

    harness_id: str
    name: str
    category: HarnessCategory
    purpose: str
    supported_loops: tuple[str, ...]
    required_inputs: tuple[str, ...]
    output_contract: str
    constraints: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class LoopPolicy:
    """Selected control policy for a task."""

    base_loop: str
    additional_loops: tuple[str, ...]
    max_iterations: int
    time_budget_ms: int
    tool_budget: int
    requires_review: bool
    requires_verification: bool
    recovery_policy_id: str
    rationale: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class CapabilityDefinition:
    """Typed capability inventory entry."""

    capability_id: str
    category: CapabilityCategory
    label: str
    goal_tags: tuple[str, ...]
    cost_level: RiskLevel
    risk_level: RiskLevel
    prerequisites: tuple[str, ...]
    compatible_harnesses: tuple[str, ...]
    compatible_task_classes: tuple[Complexity, ...]
    requires_fresh_context: bool = False
    requires_checker: bool = False


@dataclass(frozen=True, slots=True)
class CapabilitySet:
    """Selected capability set for a task."""

    harnesses: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    loops: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    brains: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    skills: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    mcps: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    commands: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    verifiers: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)
    recovery_policies: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class VerificationPayload:
    """Validation and acceptance outcome inside an execution envelope."""

    performed: bool
    passed: bool
    checks: tuple[str, ...]
    acceptance_criteria_satisfied: bool
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class VerificationCheck:
    """Deterministic single verification check."""

    check_id: str
    label: str
    passed: bool
    reason: str


@dataclass(frozen=True, slots=True)
class VerificationOutcome:
    """Aggregated deterministic verification outcome."""

    performed: bool
    passed: bool
    checks: tuple[VerificationCheck, ...]
    acceptance_criteria_satisfied: bool
    evidence_refs: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class ReviewRubric:
    """Minimum rubric for the local maker-checker MVP."""

    rubric_id: str
    criteria: tuple[str, ...]
    requires_verification_pass: bool
    blocks_self_approval: bool


@dataclass(frozen=True, slots=True)
class ReviewOutcome:
    """Aggregated review outcome for maker-checker decisions."""

    performed: bool
    approved: bool
    findings: tuple[str, ...]
    risk_flags: tuple[str, ...]
    recommended_next_action: str


@dataclass(frozen=True, slots=True)
class FailureRecord:
    """Normalized failure snapshot used by bounded recovery."""

    failure_class: str
    reason: str
    attempt_count: int
    retryable: bool
    previous_action: str | None = None


@dataclass(frozen=True, slots=True)
class RecoveryPayload:
    """Recovery state inside an execution envelope."""

    retryable: bool
    suggested_action: RecoveryAction
    attempt_count: int
    failure_class: str
    reason: str


@dataclass(frozen=True, slots=True)
class ExecutionEnvelope:
    """Canonical outcome contract for runtime execution."""

    status: EnvelopeStatus
    summary: str
    artifacts: tuple[str, ...]
    risks: tuple[str, ...]
    next_actions: tuple[str, ...]
    verification: VerificationPayload | None = None
    review: ReviewOutcome | None = None
    recovery: RecoveryPayload | None = None


@dataclass(frozen=True, slots=True)
class RecoveryDecision:
    """Bounded next-step decision produced by recovery."""

    action: RecoveryAction
    reason: str
    updated_loop_policy: LoopPolicy | None
    escalate_to_human: bool
