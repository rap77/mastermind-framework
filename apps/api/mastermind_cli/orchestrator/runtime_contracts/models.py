"""Typed runtime contract models for orchestrator control selection."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
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
    "policy",
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
StageResultStatus = Literal["passed", "failed", "blocked", "skipped", "needs_review"]
StageDecisionAction = Literal["execute", "skip", "block"]
EvidenceResult = Literal["pass", "fail", "inconclusive", "skipped"]
SecurityEnforcement = Literal["required", "mandatory"]
SecurityOverlayScope = Literal[
    "global", "domain", "jurisdiction", "project", "exception"
]


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
    stages: tuple[StageDefinition, ...] = field(default_factory=tuple)


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
    stage_graph: StageGraph | None = None
    content_hash: str | None = None


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
    policies: tuple[CapabilityDefinition, ...] = field(default_factory=tuple)


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


@dataclass(frozen=True, slots=True)
class StageDefinition:
    """Versioned executable stage declared by a run bundle."""

    stage_id: str
    name: str
    required: bool
    prerequisites: tuple[str, ...]
    capability_refs: tuple[str, ...]
    input_artifact_types: tuple[str, ...]
    output_artifact_types: tuple[str, ...]
    gate_policy: str
    approval_policy: str
    recovery_policy: str
    max_attempts: int

    def __post_init__(self) -> None:
        if not self.stage_id:
            raise ValueError("stage_id must not be empty")
        if not self.gate_policy:
            raise ValueError("gate_policy must not be empty")
        if self.max_attempts < 1:
            raise ValueError("max_attempts must be at least 1")


@dataclass(frozen=True, slots=True)
class StageNode:
    """A versioned stage graph node."""

    stage: StageDefinition
    version: str


@dataclass(frozen=True, slots=True)
class StageEdge:
    """A transition between stages for listed result statuses."""

    from_stage_id: str
    to_stage_id: str
    on_status: tuple[StageResultStatus, ...]
    version: str


@dataclass(frozen=True, slots=True)
class StageLoop:
    """Bounded loop metadata within a stage graph."""

    loop_id: str
    member_stage_ids: tuple[str, ...]
    entry_stage_id: str
    entry_condition_ref: str
    exit_condition_ref: str
    max_iterations: int
    checkpoint_each_iteration: bool
    exhausted_action: str
    version: str

    def __post_init__(self) -> None:
        if self.max_iterations < 1:
            raise ValueError("max_iterations must be at least 1")


@dataclass(frozen=True, slots=True)
class StageGraph:
    """Canonical versioned graph that defines one run's stage execution."""

    schema_version: str
    graph_id: str
    bundle_id: str
    profile_ref: str
    entry_stage_ids: tuple[str, ...]
    exit_stage_ids: tuple[str, ...]
    nodes: tuple[StageNode, ...]
    edges: tuple[StageEdge, ...]
    loops: tuple[StageLoop, ...]
    canonicalization_version: str
    content_hash: str

    def canonical_hash_input(self) -> dict[str, object]:
        """Return stable graph content excluding its computed digest."""
        return {
            "schema_version": self.schema_version,
            "graph_id": self.graph_id,
            "bundle_id": self.bundle_id,
            "profile_ref": self.profile_ref,
            "entry_stage_ids": tuple(sorted(self.entry_stage_ids)),
            "exit_stage_ids": tuple(sorted(self.exit_stage_ids)),
            "nodes": [
                asdict(node)
                for node in sorted(self.nodes, key=lambda node: node.stage.stage_id)
            ],
            "edges": [
                asdict(edge)
                for edge in sorted(
                    self.edges,
                    key=lambda edge: (edge.from_stage_id, edge.to_stage_id),
                )
            ],
            "loops": [
                {
                    **asdict(loop),
                    "member_stage_ids": tuple(sorted(loop.member_stage_ids)),
                }
                for loop in sorted(self.loops, key=lambda loop: loop.loop_id)
            ],
            "canonicalization_version": self.canonicalization_version,
        }


@dataclass(frozen=True, slots=True)
class StageDecision:
    """Explicit policy decision for one stage."""

    stage_id: str
    decision: StageDecisionAction
    rationale: str
    decided_by: str
    risk: RiskLevel
    affected_artifacts: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.decision not in {"execute", "skip", "block"}:
            raise ValueError(f"Unsupported stage decision: {self.decision}")


@dataclass(frozen=True, slots=True)
class StageResult:
    """Immutable result from one stage execution attempt."""

    stage_id: str
    status: StageResultStatus
    attempt: int
    artifact_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    finding_refs: tuple[str, ...]
    started_at: str
    completed_at: str
    next_stage_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        if self.status not in {
            "passed",
            "failed",
            "blocked",
            "skipped",
            "needs_review",
        }:
            raise ValueError(f"Unsupported stage result status: {self.status}")


@dataclass(frozen=True, slots=True)
class EvidenceTool:
    """Tool identity used to collect execution evidence."""

    id: str
    version: str


@dataclass(frozen=True, slots=True)
class EvidenceEnvironment:
    """Environment identity used to collect execution evidence."""

    name: str
    configuration_refs: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class EvidenceMetric:
    """One measured value associated with execution evidence."""

    name: str
    actual: int | float | str
    expected: int | float | str
    unit: str
    passed: bool


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    """Typed, reference-only evidence emitted by a stage capability."""

    evidence_id: str
    check_id: str
    performed: bool
    method: str
    result: EvidenceResult
    summary: str
    command_or_procedure: str | None
    tool: EvidenceTool | None
    environment: EvidenceEnvironment | None
    exit_status: int | None
    artifact_refs: tuple[str, ...]
    metrics: tuple[EvidenceMetric, ...]
    detail_schema_ref: str | None
    details_ref: str | None
    limitations: tuple[str, ...]
    recorded_at: str

    def __post_init__(self) -> None:
        if not self.performed and self.result == "pass":
            raise ValueError("Unperformed evidence cannot pass")

    @property
    def passed(self) -> bool:
        """Return true only for a performed passing check."""
        return self.performed and self.result == "pass"


@dataclass(frozen=True, slots=True)
class ApprovalRecord:
    """Explicit approval decision retained for downstream acceptance."""

    approval_id: str
    scope: str
    decision: str
    actor: str
    rationale: str
    artifact_versions: tuple[str, ...]
    decided_at: str
    expires_at: str | None


@dataclass(frozen=True, slots=True)
class RunCheckpoint:
    """Authoritative, attempt-aware resume state for a stage execution run."""

    checkpoint_id: str
    version: int
    run_id: str
    bundle_id: str
    objective_id: str
    bundle_content_hash: str
    active_stage_id: str | None
    active_attempt: int
    completed_stage_ids: tuple[str, ...]
    skipped_stage_ids: tuple[str, ...]
    blocked_stage_ids: tuple[str, ...]
    artifact_refs: tuple[str, ...]
    evidence_refs: tuple[str, ...]
    pending_approval_ids: tuple[str, ...]
    budget_consumed: int
    budget_remaining: int
    recovery_state: str | None
    replan_state: str | None
    next_eligible_stage_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class ReplanRecord:
    """Append-only record of invalidation caused by a bounded replan."""

    replan_id: str
    run_id: str
    requested_change: str
    reason: str
    dependency_impacts: tuple[str, ...]
    invalidated_artifact_refs: tuple[str, ...]
    archived_artifact_refs: tuple[str, ...]
    invalidated_approval_ids: tuple[str, ...]
    new_bundle_id: str
    new_bundle_version: str
    confirmation_required: bool
    safe_resume_stage_id: str | None
    requested_at: str
    invalidated_evidence_refs: tuple[str, ...] = ()
    invalidated_acceptance: bool = False


@dataclass(frozen=True, slots=True)
class SecurityControl:
    """One versioned control selected by an applied security overlay."""

    control_id: str
    enforcement: SecurityEnforcement
    source_version: str


@dataclass(frozen=True, slots=True)
class ApprovedSecurityException:
    """Approved and expiring exception that can weaken one control."""

    exception_id: str
    control_ids: tuple[str, ...]
    rationale: str
    approved_by: str
    approved_at: str
    expires_at: str


@dataclass(frozen=True, slots=True)
class SecurityOverlay:
    """Layered security controls for a global or contextual scope."""

    overlay_id: str
    version: str
    scope: SecurityOverlayScope
    controls: tuple[SecurityControl, ...]
    domain: str | None = None
    jurisdiction: str | None = None
    project_id: str | None = None
    approved_exception: ApprovedSecurityException | None = None

    def __post_init__(self) -> None:
        if self.scope == "domain" and not self.domain:
            raise ValueError("domain overlay requires domain")
        if self.scope == "jurisdiction" and not self.jurisdiction:
            raise ValueError("jurisdiction overlay requires jurisdiction")
        if self.scope == "project" and not self.project_id:
            raise ValueError("project overlay requires project_id")
        if self.scope == "exception" and self.approved_exception is None:
            raise ValueError("exception overlay requires approved_exception")


@dataclass(frozen=True, slots=True)
class SecurityProfile:
    """Deterministically composed security controls and their source lineage."""

    security_profile_id: str
    profile_version: str
    project_id: str
    domain: str
    jurisdictions: tuple[str, ...]
    controls: tuple[SecurityControl, ...]
    applied_overlays: tuple[SecurityOverlay, ...]
    source_versions: tuple[str, ...]
    schema_version: str = "1.0"
    data_classes: tuple[str, ...] = ()
    critical_assets: tuple[str, ...] = ()
    actors: tuple[str, ...] = ()
    trust_boundaries: tuple[str, ...] = ()
    threat_categories: tuple[str, ...] = ()
    control_sets: tuple[str, ...] = ()
    approval_policy: str | None = None
    risk_thresholds: tuple[tuple[str, str], ...] = ()
    approved_exception_ids: tuple[str, ...] = ()

    @property
    def applied_overlay_ids(self) -> tuple[str, ...]:
        """Return overlay identities in their deterministic precedence order."""
        return tuple(overlay.overlay_id for overlay in self.applied_overlays)

    @classmethod
    def compose(
        cls,
        *,
        security_profile_id: str,
        profile_version: str,
        project_id: str,
        domain: str,
        jurisdictions: tuple[str, ...],
        global_baseline: SecurityOverlay,
        domain_overlay: SecurityOverlay | None = None,
        jurisdiction_overlays: tuple[SecurityOverlay, ...] = (),
        project_overlay: SecurityOverlay | None = None,
        approved_exceptions: tuple[SecurityOverlay, ...] = (),
        data_classes: tuple[str, ...] = (),
        critical_assets: tuple[str, ...] = (),
        actors: tuple[str, ...] = (),
        trust_boundaries: tuple[str, ...] = (),
        threat_categories: tuple[str, ...] = (),
        control_sets: tuple[str, ...] = (),
        approval_policy: str | None = None,
        risk_thresholds: tuple[tuple[str, str], ...] = (),
    ) -> SecurityProfile:
        """Compose controls in global, domain, jurisdiction, project, exception order."""
        overlays = [global_baseline]
        if domain_overlay is not None:
            overlays.append(domain_overlay)
        overlays.extend(
            sorted(
                jurisdiction_overlays, key=lambda overlay: overlay.jurisdiction or ""
            )
        )
        if project_overlay is not None:
            overlays.append(project_overlay)
        overlays.extend(approved_exceptions)
        controls: dict[str, SecurityControl] = {}
        exceptions: list[str] = []
        for overlay in overlays:
            for control in overlay.controls:
                existing = controls.get(control.control_id)
                if (
                    existing is not None
                    and existing.enforcement == "mandatory"
                    and control.enforcement == "required"
                    and (
                        overlay.approved_exception is None
                        or control.control_id
                        not in overlay.approved_exception.control_ids
                    )
                ):
                    raise ValueError(
                        f"Overlay '{overlay.overlay_id}' cannot weaken control "
                        f"'{control.control_id}' without an approved exception"
                    )
                controls[control.control_id] = control
            if overlay.approved_exception is not None:
                exceptions.append(overlay.approved_exception.exception_id)
        return cls(
            security_profile_id=security_profile_id,
            profile_version=profile_version,
            project_id=project_id,
            domain=domain,
            jurisdictions=jurisdictions,
            controls=tuple(controls[key] for key in sorted(controls)),
            applied_overlays=tuple(overlays),
            source_versions=tuple(
                dict.fromkeys(
                    control.source_version
                    for overlay in overlays
                    for control in overlay.controls
                )
            ),
            data_classes=data_classes,
            critical_assets=critical_assets,
            actors=actors,
            trust_boundaries=trust_boundaries,
            threat_categories=threat_categories,
            control_sets=control_sets,
            approval_policy=approval_policy,
            risk_thresholds=risk_thresholds,
            approved_exception_ids=tuple(exceptions),
        )
