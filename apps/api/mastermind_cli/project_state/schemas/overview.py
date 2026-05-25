"""Overview response schema for the project state thin slice."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class CheckpointSummary(BaseModel):
    """Summary of the latest project checkpoint."""

    checkpoint_id: str = Field(..., description="Latest checkpoint ID")
    task_id: str = Field(..., description="Task associated with the checkpoint")
    next_step_summary: str = Field(..., description="Next step to resume from")
    created_at: datetime = Field(..., description="Checkpoint creation timestamp")


class DecisionSummary(BaseModel):
    """Summary of the latest project decision."""

    decision_id: str = Field(..., description="Latest decision ID")
    title: str = Field(..., description="Decision title")
    status: str = Field(..., description="Decision status")
    created_at: datetime = Field(..., description="Decision creation timestamp")


class ProjectOverviewResponse(BaseModel):
    """Read-side project overview for the dashboard and agent tools."""

    project_id: str = Field(..., description="Project identifier")
    name: str = Field(..., description="Project name")
    status: str = Field(..., description="Project status")
    adapter_id: str | None = Field(None, description="Project adapter identifier")
    total_tasks: int = Field(..., description="Total number of tasks")
    active_tasks: int = Field(..., description="Tasks currently in progress")
    blocked_tasks: int = Field(..., description="Tasks currently blocked")
    total_estimated_cost: float = Field(..., description="Aggregated estimated cost")
    latest_checkpoint: CheckpointSummary | None = Field(
        None,
        description="Most recent checkpoint summary",
    )
    latest_decision: DecisionSummary | None = Field(
        None,
        description="Most recent decision summary",
    )


class TaskDetailResponse(BaseModel):
    """Detailed read-side task representation for dashboard/task tools."""

    task_id: str = Field(..., description="Task identifier")
    project_id: str = Field(..., description="Owning project identifier")
    parent_task_id: str | None = Field(None, description="Parent task identifier")
    title: str = Field(..., description="Task title")
    status: str = Field(..., description="Task status")
    priority: str = Field(..., description="Task priority")
    owner_type: str | None = Field(None, description="Owner type")
    owner_id: str | None = Field(None, description="Owner identifier")
    metadata: dict[str, object] = Field(..., description="Task metadata")
    constraints: dict[str, object] = Field(..., description="Task constraints")
    completion_criteria: dict[str, object] = Field(
        ..., description="Task completion criteria"
    )
    created_at: datetime = Field(..., description="Task creation timestamp")
    updated_at: datetime = Field(..., description="Last task update timestamp")


class TaskDependencyResponse(BaseModel):
    """Dependency edge response for a task."""

    dependency_id: str = Field(..., description="Dependency edge identifier")
    task_id: str = Field(..., description="Task that has the dependency")
    depends_on_task_id: str = Field(
        ..., description="Task that must be completed first"
    )
    dependency_type: str = Field(..., description="Dependency type")
    created_at: datetime = Field(..., description="Dependency creation timestamp")


class TaskListResponse(BaseModel):
    """List of tasks for a project."""

    project_id: str = Field(..., description="Project identifier")
    tasks: list[TaskDetailResponse] = Field(
        default_factory=list, description="Tasks for the project"
    )


class TaskDependenciesResponse(BaseModel):
    """List of dependency edges for a task."""

    project_id: str = Field(..., description="Project identifier")
    task_id: str = Field(..., description="Task identifier")
    dependencies: list[TaskDependencyResponse] = Field(
        default_factory=list, description="Dependency edges for the task"
    )


class RunDetailResponse(BaseModel):
    """Detailed run representation for project execution visibility."""

    run_id: str = Field(..., description="Run identifier")
    project_id: str = Field(..., description="Owning project identifier")
    task_id: str = Field(..., description="Task identifier")
    task_title: str | None = Field(None, description="Associated task title")
    actor_type: str = Field(..., description="Actor type executing the run")
    actor_id: str = Field(..., description="Actor identifier executing the run")
    status: str = Field(..., description="Run status")
    started_at: datetime = Field(..., description="Run start timestamp")
    ended_at: datetime | None = Field(
        None, description="Run end timestamp if completed"
    )
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Run metadata"
    )


class ActiveRunsResponse(BaseModel):
    """List of active runs for a project."""

    project_id: str = Field(..., description="Project identifier")
    runs: list[RunDetailResponse] = Field(
        default_factory=list, description="Currently active runs for the project"
    )


class LatestCheckpointResponse(BaseModel):
    """Detailed latest checkpoint view for a project."""

    checkpoint_id: str = Field(..., description="Checkpoint identifier")
    project_id: str = Field(..., description="Owning project identifier")
    task_id: str = Field(..., description="Task identifier associated with checkpoint")
    run_id: str | None = Field(None, description="Run identifier")
    context_summary: dict[str, object] = Field(..., description="Context summary")
    resume_state: dict[str, object] = Field(..., description="Resume state snapshot")
    next_step_summary: str = Field(..., description="Next step summary")
    created_at: datetime = Field(..., description="Checkpoint creation timestamp")


class CreateCheckpointRequest(BaseModel):
    """Request payload to create a new task checkpoint."""

    run_id: str | None = Field(None, description="Associated run identifier")
    context_summary: dict[str, Any] = Field(
        default_factory=dict, description="Structured context summary"
    )
    resume_state: dict[str, Any] = Field(
        default_factory=dict, description="Structured resume state snapshot"
    )
    next_step_summary: str = Field(
        ..., min_length=1, max_length=4000, description="Next step summary"
    )


class ProviderCostSummary(BaseModel):
    """Aggregated token and cost summary for a provider within a project."""

    provider: str = Field(..., description="Provider identifier")
    total_prompt_tokens: int = Field(..., description="Summed prompt tokens")
    total_completion_tokens: int = Field(..., description="Summed completion tokens")
    total_estimated_cost: float = Field(..., description="Summed estimated cost")


class ProjectCostSummaryResponse(BaseModel):
    """Aggregated token and cost summary for a project."""

    project_id: str = Field(..., description="Project identifier")
    total_prompt_tokens: int = Field(..., description="Total prompt tokens")
    total_completion_tokens: int = Field(..., description="Total completion tokens")
    total_estimated_cost: float = Field(..., description="Total estimated cost")
    providers: list[ProviderCostSummary] = Field(
        default_factory=list,
        description="Per-provider token and cost totals",
    )


class ProjectTimeSummaryResponse(BaseModel):
    """Estimated time and ETA summary for a project."""

    project_id: str = Field(..., description="Project identifier")
    total_tasks: int = Field(..., description="Total number of tasks")
    completed_tasks: int = Field(..., description="Completed task count")
    remaining_tasks: int = Field(..., description="Remaining task count")
    active_run_count: int = Field(..., description="Currently active run count")
    estimated_total_minutes: int = Field(
        ..., description="Estimated total project effort in minutes"
    )
    estimated_remaining_minutes: int = Field(
        ..., description="Estimated remaining project effort in minutes"
    )
    active_run_elapsed_minutes: int = Field(
        ..., description="Wall clock minutes accumulated by active runs"
    )
    project_age_minutes: int = Field(
        ..., description="Elapsed minutes since project creation"
    )
    projected_completion_at: datetime | None = Field(
        None, description="Projected completion timestamp if estimate is available"
    )
    confidence: str = Field(
        ..., description="Estimate confidence: low, medium, or high"
    )
    estimation_basis: str = Field(
        ..., description="Explanation of how the ETA was estimated"
    )


class TokenUsageEventResponse(BaseModel):
    """Detailed token usage event for project telemetry drill-down."""

    usage_event_id: str = Field(..., description="Usage event identifier")
    project_id: str = Field(..., description="Project identifier")
    task_id: str | None = Field(None, description="Associated task identifier")
    run_id: str | None = Field(None, description="Associated run identifier")
    provider: str = Field(..., description="Provider identifier")
    model: str = Field(..., description="Model identifier")
    auth_mode: str = Field(..., description="Authentication mode")
    prompt_tokens: int = Field(..., description="Prompt tokens consumed")
    completion_tokens: int = Field(..., description="Completion tokens consumed")
    estimated_cost: float = Field(..., description="Estimated monetary cost")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Usage metadata"
    )
    created_at: datetime = Field(..., description="Usage event timestamp")


class TokenUsageListResponse(BaseModel):
    """List of detailed token usage events for a project."""

    project_id: str = Field(..., description="Project identifier")
    events: list[TokenUsageEventResponse] = Field(
        default_factory=list, description="Detailed token usage events"
    )


class RecordTokenUsageRequest(BaseModel):
    """Request body for recording a token usage event from an agent."""

    model: str = Field(..., description="Model identifier (e.g. claude-sonnet-4-6)")
    provider: str = Field("anthropic", description="Provider identifier")
    auth_mode: str = Field("api", description="Authentication mode")
    prompt_tokens: int = Field(..., ge=0, description="Prompt tokens consumed")
    completion_tokens: int = Field(..., ge=0, description="Completion tokens consumed")
    estimated_cost: float = Field(0.0, ge=0.0, description="Estimated cost in USD")
    run_id: str | None = Field(None, description="Associated run identifier")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Usage metadata"
    )


class ActivityFeedEventResponse(BaseModel):
    """Single activity feed event for a project timeline."""

    event_type: str = Field(..., description="Event type identifier")
    occurred_at: datetime = Field(..., description="Event timestamp")
    project_id: str = Field(..., description="Project identifier")
    task_id: str | None = Field(None, description="Associated task identifier")
    entity_id: str = Field(..., description="Primary entity identifier for the event")
    title: str = Field(..., description="Short human-readable event title")
    summary: str = Field(..., description="Short event summary")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Event metadata"
    )


class ActivityFeedResponse(BaseModel):
    """Project activity feed response."""

    project_id: str = Field(..., description="Project identifier")
    events: list[ActivityFeedEventResponse] = Field(
        default_factory=list, description="Recent activity feed events"
    )


class DecisionDetailResponse(BaseModel):
    """Detailed decision record representation."""

    decision_id: str = Field(..., description="Decision identifier")
    project_id: str = Field(..., description="Owning project identifier")
    task_id: str | None = Field(None, description="Associated task identifier")
    title: str = Field(..., description="Decision title")
    status: str = Field(..., description="Decision status")
    rationale_markdown: str = Field(..., description="Decision rationale markdown")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Decision metadata"
    )
    created_at: datetime = Field(..., description="Decision creation timestamp")


class CreateDecisionRequest(BaseModel):
    """Request payload to record a new decision for a project or task."""

    task_id: str | None = Field(None, description="Associated task identifier")
    title: str = Field(..., min_length=1, max_length=500, description="Decision title")
    status: str = Field(..., min_length=1, max_length=64, description="Decision status")
    rationale_markdown: str = Field(
        ..., min_length=1, max_length=20000, description="Decision rationale markdown"
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict, description="Decision metadata"
    )


class UpdateTaskStatusRequest(BaseModel):
    """Request payload to update a task's status."""

    status: str = Field(..., min_length=1, max_length=64, description="New task status")
    reason: str | None = Field(
        None, max_length=1000, description="Optional reason for the status change"
    )


class DecisionListResponse(BaseModel):
    """List of recent decision records for a project."""

    project_id: str = Field(..., description="Project identifier")
    decisions: list[DecisionDetailResponse] = Field(
        default_factory=list, description="Recent decisions for the project"
    )


class ProjectStateRealtimeEvent(BaseModel):
    """Typed contract for a project-state realtime event emitted via SSE.

    This is the canonical event shape consumers (dashboard, agents) should
    subscribe to.  The ``event_type`` discriminates the payload so consumers
    can selectively act on relevant changes without polling the full feed.
    """

    event_type: str = Field(
        ...,
        description=(
            "Discriminator for the event kind.  Known values: "
            "task_updated | checkpoint_created | decision_recorded | "
            "token_usage_recorded | heartbeat"
        ),
    )
    project_id: str = Field(..., description="Project the event belongs to")
    entity_id: str = Field(
        ..., description="Primary entity identifier (task, checkpoint, decision, …)"
    )
    occurred_at: datetime = Field(
        ..., description="When the underlying change occurred"
    )
    summary: str = Field(..., description="Short human-readable event summary")
    metadata: dict[str, object] = Field(
        default_factory=dict,
        description="Additional event metadata (status, provider, model, …)",
    )


class ContextDecisionSummary(BaseModel):
    """Decision summary included in a task context projection."""

    decision_id: str = Field(..., description="Decision identifier")
    title: str = Field(..., description="Decision title")
    status: str = Field(..., description="Decision status")
    created_at: datetime = Field(..., description="Decision creation timestamp")


class TaskContextProjectionResponse(BaseModel):
    """Minimal task context projection for agent and human execution."""

    project_id: str = Field(..., description="Owning project identifier")
    task_id: str = Field(..., description="Task identifier")
    generated_at: datetime = Field(..., description="Projection generation timestamp")
    objective: str = Field(..., description="Current task objective")
    status: str = Field(..., description="Current task status")
    priority: str = Field(..., description="Task priority")
    blockers: list[str] = Field(default_factory=list, description="Active blockers")
    dependencies: list[str] = Field(
        default_factory=list, description="Referenced dependency task identifiers"
    )
    constraints: dict[str, object] = Field(..., description="Task constraints")
    completion_criteria: dict[str, object] = Field(
        ..., description="Task completion criteria"
    )
    critical_decisions: list[ContextDecisionSummary] = Field(
        default_factory=list, description="Recent critical decisions for the task scope"
    )
    latest_checkpoint_id: str | None = Field(
        None, description="Latest checkpoint identifier for the task"
    )
    next_step: str | None = Field(None, description="Next step to resume or continue")
    relevant_artifacts: list[str] = Field(
        default_factory=list, description="Relevant artifact identifiers or names"
    )


class DoctrineRuleResponse(BaseModel):
    """Single doctrine rule included in a doctrine projection."""

    rule_id: str = Field(..., description="Rule identifier")
    summary: str = Field(..., description="Rule summary")
    severity: str = Field(..., description="Rule severity")
    check: str | None = Field(None, description="Validation or compliance check")


class DoctrineRuleRequest(BaseModel):
    """Single doctrine rule for a write request."""

    rule_id: str
    summary: str
    severity: str = "mandatory"
    check: str | None = None


class DoctrineUpdateRequest(BaseModel):
    """Request body for setting project-level doctrine (partial update)."""

    methodology: str | None = None
    methodology_reason: str | None = None
    required_phases: list[str] | None = None
    mandatory_rules: list[DoctrineRuleRequest] | None = None
    recommended_rules: list[DoctrineRuleRequest] | None = None
    architecture_constraints: list[str] | None = None
    quality_gates: list[str] | None = None
    exception_policy: dict[str, bool] | None = None


class ProjectDoctrineResponse(BaseModel):
    """Project-level doctrine state returned after a write."""

    project_id: str
    methodology: str
    methodology_reason: str
    required_phases: list[str]
    mandatory_rules: list[DoctrineRuleResponse]
    recommended_rules: list[DoctrineRuleResponse]
    architecture_constraints: list[str]
    quality_gates: list[str]


class DoctrineMethodologyResponse(BaseModel):
    """Active methodology selection for a doctrine projection."""

    active: str = Field(..., description="Active methodology name")
    reason: str = Field(..., description="Why this methodology applies")
    required_phases: list[str] = Field(
        default_factory=list, description="Required workflow phases"
    )


class DoctrineExceptionPolicyResponse(BaseModel):
    """Exception handling policy for doctrine projection."""

    human_approval_required_for_overrides: bool = Field(
        ..., description="Whether overrides need human approval"
    )
    pause_if_mandatory_rule_cannot_be_met: bool = Field(
        ...,
        description="Whether execution should pause if a mandatory rule cannot be met",
    )


class DoctrineProjectionResponse(BaseModel):
    """Task-level doctrine projection for agent and human execution."""

    project_id: str = Field(..., description="Owning project identifier")
    task_id: str = Field(..., description="Task identifier")
    scope: str = Field(..., description="Projection scope")
    generated_at: datetime = Field(..., description="Projection generation timestamp")
    methodology: DoctrineMethodologyResponse = Field(
        ..., description="Active methodology"
    )
    mandatory_rules: list[DoctrineRuleResponse] = Field(
        default_factory=list, description="Mandatory doctrine rules"
    )
    recommended_rules: list[DoctrineRuleResponse] = Field(
        default_factory=list, description="Recommended doctrine rules"
    )
    architecture_constraints: list[str] = Field(
        default_factory=list, description="Architecture constraints"
    )
    quality_gates: list[str] = Field(
        default_factory=list, description="Quality gates before completion"
    )
    exception_policy: DoctrineExceptionPolicyResponse = Field(
        ..., description="Exception handling policy"
    )


class ProjectDetailResponse(BaseModel):
    """Detailed project representation for dashboard navigation."""

    project_id: str = Field(..., description="Project identifier")
    name: str = Field(..., description="Project name")
    status: str = Field(..., description="Project status")
    adapter_id: str | None = Field(None, description="Adapter identifier")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Project metadata"
    )
    created_at: datetime = Field(..., description="Project creation timestamp")
    updated_at: datetime = Field(..., description="Last project update timestamp")


class ProjectListResponse(BaseModel):
    """List of projects available in project_state."""

    projects: list[ProjectDetailResponse] = Field(
        default_factory=list, description="Projects ordered by recent activity"
    )


class ArtifactVersionResponse(BaseModel):
    """Single artifact version included in a lineage response."""

    version_id: str = Field(..., description="Unique version identifier")
    artifact_id: str = Field(..., description="Logical artifact group identifier")
    artifact_type: str = Field(..., description="Artifact type (spec, plan, decision…)")
    version: int = Field(..., description="Monotonically increasing version number")
    content_hash: str = Field(
        ..., description="Content fingerprint (SHA-256 or similar)"
    )
    created_at: datetime = Field(..., description="Version creation timestamp")
    metadata: dict[str, object] = Field(
        default_factory=dict, description="Artifact version metadata"
    )


class ArtifactLinkResponse(BaseModel):
    """Causal link between two artifact versions included in a lineage response."""

    link_id: str = Field(..., description="Unique link identifier")
    source_artifact_id: str = Field(..., description="Source version_id")
    target_artifact_id: str = Field(..., description="Target version_id")
    link_type: str = Field(..., description="Link type (derived_from, supersedes…)")
    task_id: str | None = Field(None, description="Associated task identifier")
    decision_id: str | None = Field(None, description="Associated decision identifier")
    checkpoint_id: str | None = Field(
        None, description="Associated checkpoint identifier"
    )
    created_at: datetime = Field(..., description="Link creation timestamp")


class ArtifactLineageResponse(BaseModel):
    """Causal lineage graph for a logical artifact."""

    artifact_id: str = Field(..., description="Logical artifact group identifier")
    versions: list[ArtifactVersionResponse] = Field(
        default_factory=list,
        description="All versions for the artifact, ordered ascending by version",
    )
    links: list[ArtifactLinkResponse] = Field(
        default_factory=list,
        description="Causal links connecting version nodes (source or target in this artifact)",
    )
