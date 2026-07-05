"""Typed runtime contract models for orchestrator control selection."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from mastermind_cli.memory_layer.models import ContextSnapshot as MemoryContextSnapshot
from mastermind_cli.types.interfaces import Brief


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
HarnessPackageType = Literal[
    "role",
    "lifecycle",
    "verification",
    "recovery",
    "shared_skill",
]
BundleValidationStatus = Literal["pending", "passed", "failed", "warning"]


@dataclass(frozen=True, slots=True)
class ObjectiveProfile:
    """Normalized objective signals used for multi-harness composition."""

    objective_id: str
    objective_text: str
    domain: str
    phase: str
    output_type: str
    complexity: Complexity
    risk_level: RiskLevel
    verifiability: SignalLevel
    requires_write: bool
    requires_fresh_context: bool
    requires_memory: bool
    requires_mcp: bool
    requires_review: bool
    requires_recovery: bool
    evidence_readiness_gate: str | None = None
    evidence_readiness_score: float | None = None
    reasons: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class HarnessPackage:
    """Agent Harness package discovered from the harness library."""

    package_id: str
    name: str
    package_type: HarnessPackageType
    path: str
    description: str
    domains: tuple[str, ...]
    phases: tuple[str, ...]
    outputs: tuple[str, ...]
    supported_loops: tuple[str, ...]
    skills: tuple[str, ...] = field(default_factory=tuple)
    references: tuple[str, ...] = field(default_factory=tuple)
    constraints: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class SkillPackage:
    """Reusable atomic skill package available to harness compositions."""

    skill_id: str
    name: str
    path: str
    description: str
    domains: tuple[str, ...]
    phases: tuple[str, ...]
    supported_harnesses: tuple[str, ...] = field(default_factory=tuple)
    requires_mcp: bool = False
    requires_write: bool = False


@dataclass(frozen=True, slots=True)
class HarnessCompositionPlan:
    """Deterministic plan for composing one primary harness with support."""

    plan_id: str
    objective_profile: ObjectiveProfile
    primary_harness: HarnessPackage
    supporting_harnesses: tuple[HarnessPackage, ...]
    selected_skills: tuple[SkillPackage, ...]
    selected_references: tuple[str, ...]
    selected_loops: tuple[str, ...]
    precedence_policy: tuple[str, ...]
    context_budget: int
    validation_requirements: tuple[str, ...]
    rejected_candidates: tuple[str, ...] = field(default_factory=tuple)
    rationale: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class RunBundle:
    """Materialized Agent Harness-compliant bundle for a single run."""

    bundle_id: str
    objective_id: str
    plan_id: str
    path: str
    harness_file: str
    bundle_manifest: str
    primary_harness_id: str
    supporting_harness_ids: tuple[str, ...]
    selected_skill_ids: tuple[str, ...]
    validation_status: BundleValidationStatus
    validation_errors: tuple[str, ...] = field(default_factory=tuple)
    created_at: str | None = None


@dataclass(frozen=True, slots=True)
class MultiHarnessPipelineResult:
    """Result of selecting, composing, and validating a multi-harness bundle."""

    plan: HarnessCompositionPlan
    bundle: RunBundle


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
class RuntimeRequest:
    """Unified input contract for the runtime core."""

    brief: Brief
    brain_ids: tuple[str, ...]
    memory_snapshot: MemoryContextSnapshot | None = None
    evidence_readiness_score: float | None = None
    evidence_readiness_gate: str | None = None


@dataclass(frozen=True, slots=True)
class RuntimeSelection:
    """Deterministic runtime selection for a task."""

    task_profile: TaskProfile
    capability_set: CapabilitySet
    harnesses: tuple[HarnessDefinition, ...]
    loop_policy: LoopPolicy
    memory_snapshot: MemoryContextSnapshot | None = None
    rationale: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, slots=True)
class RuntimeExecutionResult:
    """Canonical runtime outcome produced by the harness core."""

    selection: RuntimeSelection
    base_envelope: ExecutionEnvelope
    verification_outcome: VerificationOutcome | None
    review_outcome: ReviewOutcome | None
    recovery_decision: RecoveryDecision | None
    execution_envelope: ExecutionEnvelope


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
