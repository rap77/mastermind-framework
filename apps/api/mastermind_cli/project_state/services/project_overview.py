"""Project overview service for the project state thin slice."""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timedelta, timezone
import re
from typing import Any
import uuid

from sqlalchemy.orm import Session

from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository
from mastermind_cli.project_state.repositories.checkpoints import CheckpointsRepository
from mastermind_cli.project_state.repositories.decisions import DecisionsRepository
from mastermind_cli.project_state.repositories.projects import ProjectsRepository
from mastermind_cli.project_state.repositories.task_dependencies import (
    TaskDependenciesRepository,
)
from mastermind_cli.project_state.repositories.task_runs import TaskRunsRepository
from mastermind_cli.project_state.repositories.tasks import TasksRepository
from mastermind_cli.project_state.repositories.telemetry import TelemetryRepository
from mastermind_cli.project_state.schemas.overview import (
    ActiveRunsResponse,
    ActivityFeedEventResponse,
    ActivityFeedResponse,
    ArtifactLinkResponse,
    ArtifactLineageResponse,
    ArtifactVersionResponse,
    CheckpointSummary,
    ContextDecisionSummary,
    CreateCheckpointRequest,
    CreateDecisionRequest,
    DecisionDetailResponse,
    DecisionListResponse,
    DecisionSummary,
    DoctrineExceptionPolicyResponse,
    DoctrineMethodologyResponse,
    DoctrineProjectionResponse,
    DoctrineRuleResponse,
    DoctrineUpdateRequest,
    ProjectDoctrineResponse,
    LatestCheckpointResponse,
    ProjectCostSummaryResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectOverviewResponse,
    ProjectStateRealtimeEvent,
    ProjectTimeSummaryResponse,
    ProviderCostSummary,
    RunDetailResponse,
    TaskContextProjectionResponse,
    TaskDependenciesResponse,
    TaskDependencyResponse,
    TaskDetailResponse,
    TaskListResponse,
    RecordTokenUsageRequest,
    TokenUsageEventResponse,
    TokenUsageListResponse,
    UpdateTaskStatusRequest,
)


class ProjectOverviewService:
    """Build a project overview from project state repositories."""

    _ESTIMATE_PATTERN = re.compile(
        r"(?P<min>\d+)\s*min|(?P<hours>\d+)(?:\s*-\s*(?P<hours_hi>\d+))?\s*h(?:ours?)?",
        re.IGNORECASE,
    )

    @staticmethod
    def _occurred_at(value: datetime) -> datetime:
        """Normalize event timestamps for sorting."""
        return value

    @staticmethod
    def _as_utc(value: datetime) -> datetime:
        """Normalize potentially naive datetimes to UTC-aware datetimes."""
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @staticmethod
    def _estimate_minutes_from_metadata(
        metadata: dict[str, object], priority: str
    ) -> tuple[int, bool]:
        """Derive a best-effort estimate in minutes from task metadata."""
        explicit_numeric_keys = ("estimated_minutes", "estimated_duration_minutes")
        for key in explicit_numeric_keys:
            value = metadata.get(key)
            if isinstance(value, (int, float)) and value > 0:
                return int(value), True

        effort = metadata.get("estimated_effort")
        if isinstance(effort, str):
            effort_lower = effort.lower()
            if match := ProjectOverviewService._ESTIMATE_PATTERN.search(effort_lower):
                if match.group("min"):
                    return int(match.group("min")), True

                if match.group("hours"):
                    low = int(match.group("hours"))
                    high = (
                        int(match.group("hours_hi")) if match.group("hours_hi") else low
                    )
                    return int(((low + high) / 2) * 60), True

        fallback_by_priority = {
            "critical": 180,
            "high": 120,
            "normal": 60,
            "low": 30,
        }
        return fallback_by_priority.get(priority, 60), False

    def get_project_time_summary(
        self, project_id: str
    ) -> ProjectTimeSummaryResponse | None:
        """Return an ETA-oriented time summary for a project using simple heuristics."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        tasks = self.tasks.list_by_project(project_id, limit=1000)
        active_runs = self.task_runs.list_active_by_project(project_id, limit=500)
        now = datetime.now(timezone.utc)

        completed_statuses = {"done", "completed", "complete", "approved"}
        remaining_statuses = {"cancelled", "canceled"}

        estimated_total_minutes = 0
        estimated_remaining_minutes = 0
        explicit_estimate_count = 0

        completed_tasks = 0
        remaining_tasks = 0

        for task in tasks:
            estimate_minutes, explicit = self._estimate_minutes_from_metadata(
                task.metadata_json,
                task.priority,
            )
            estimated_total_minutes += estimate_minutes
            if explicit:
                explicit_estimate_count += 1

            if task.status in completed_statuses:
                completed_tasks += 1
                continue

            if task.status in remaining_statuses:
                continue

            remaining_tasks += 1
            estimated_remaining_minutes += estimate_minutes

        active_run_elapsed_minutes = 0
        for run in active_runs:
            elapsed = now - self._as_utc(run.started_at)
            active_run_elapsed_minutes += max(int(elapsed.total_seconds() // 60), 0)

        project_age_minutes = max(
            int((now - self._as_utc(project.created_at)).total_seconds() // 60),
            0,
        )

        estimate_ratio = explicit_estimate_count / len(tasks) if tasks else 0.0
        if estimate_ratio >= 0.7:
            confidence = "high"
        elif estimate_ratio >= 0.3:
            confidence = "medium"
        else:
            confidence = "low"

        projected_completion_at = (
            now.replace(microsecond=0) if estimated_remaining_minutes == 0 else None
        )
        if estimated_remaining_minutes > 0:
            projected_completion_at = now.replace(microsecond=0) + timedelta(
                minutes=estimated_remaining_minutes
            )

        return ProjectTimeSummaryResponse(
            project_id=project_id,
            total_tasks=len(tasks),
            completed_tasks=completed_tasks,
            remaining_tasks=remaining_tasks,
            active_run_count=len(active_runs),
            estimated_total_minutes=estimated_total_minutes,
            estimated_remaining_minutes=estimated_remaining_minutes,
            active_run_elapsed_minutes=active_run_elapsed_minutes,
            project_age_minutes=project_age_minutes,
            projected_completion_at=projected_completion_at,
            confidence=confidence,
            estimation_basis=(
                "Heuristic ETA based on task metadata estimates when available; "
                "falls back to priority-based defaults otherwise."
            ),
        )

    def create_checkpoint(
        self,
        project_id: str,
        task_id: str,
        request: CreateCheckpointRequest,
        actor_user_id: str,
    ) -> LatestCheckpointResponse | None:
        """Create a new checkpoint for a task in a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        created_at = datetime.now(timezone.utc)
        checkpoint = self.checkpoints.create_checkpoint(
            checkpoint_id=str(uuid.uuid4()),
            project_id=project_id,
            task_id=task_id,
            run_id=request.run_id,
            context_summary=deepcopy(request.context_summary),
            resume_state=deepcopy(request.resume_state),
            next_step_summary=request.next_step_summary,
            created_at=created_at,
        )

        task_metadata = deepcopy(task.metadata_json)
        task_metadata["last_checkpoint_by"] = actor_user_id
        task_metadata["last_checkpoint_at"] = created_at.isoformat()
        task.metadata_json = task_metadata
        task.updated_at = created_at
        self.session.commit()

        return LatestCheckpointResponse(
            checkpoint_id=checkpoint.checkpoint_id,
            project_id=checkpoint.project_id,
            task_id=checkpoint.task_id,
            run_id=checkpoint.run_id,
            context_summary=checkpoint.context_summary,
            resume_state=checkpoint.resume_state,
            next_step_summary=checkpoint.next_step_summary,
            created_at=checkpoint.created_at,
        )

    def create_decision(
        self,
        project_id: str,
        request: CreateDecisionRequest,
        actor_user_id: str,
    ) -> DecisionDetailResponse | None:
        """Create a new decision record for a project and optional task."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        if request.task_id is not None:
            task = self.tasks.get_by_id(project_id, request.task_id)
            if task is None:
                return None

        created_at = datetime.now(timezone.utc)
        metadata = deepcopy(request.metadata)
        metadata["recorded_by"] = actor_user_id
        metadata["recorded_at"] = created_at.isoformat()

        decision = self.decisions.create_decision(
            decision_id=str(uuid.uuid4()),
            project_id=project_id,
            task_id=request.task_id,
            title=request.title,
            status=request.status,
            rationale_markdown=request.rationale_markdown,
            metadata_json=metadata,
            created_at=created_at,
        )

        return DecisionDetailResponse(
            decision_id=decision.decision_id,
            project_id=decision.project_id,
            task_id=decision.task_id,
            title=decision.title,
            status=decision.status,
            rationale_markdown=decision.rationale_markdown,
            metadata=decision.metadata_json,
            created_at=decision.created_at,
        )

    def update_task_status(
        self,
        project_id: str,
        task_id: str,
        request: UpdateTaskStatusRequest,
        actor_user_id: str,
    ) -> TaskDetailResponse | None:
        """Update the status of a task and persist audit metadata."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        task = self.tasks.update_status(project_id, task_id, request.status)
        if task is None:
            return None

        updated_at = datetime.now(timezone.utc)
        task_metadata = deepcopy(task.metadata_json)
        task_metadata["status_updated_by"] = actor_user_id
        task_metadata["status_updated_at"] = updated_at.isoformat()
        if request.reason:
            task_metadata["status_reason"] = request.reason
        task.metadata_json = task_metadata
        task.updated_at = updated_at
        self.session.commit()

        return TaskDetailResponse(
            task_id=task.task_id,
            project_id=task.project_id,
            parent_task_id=task.parent_task_id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            owner_type=task.owner_type,
            owner_id=task.owner_id,
            metadata=task.metadata_json,
            constraints=task.constraints,
            completion_criteria=task.completion_criteria,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def update_project_doctrine(
        self, project_id: str, request: DoctrineUpdateRequest
    ) -> ProjectDoctrineResponse | None:
        """Merge doctrine fields into project.metadata_json["doctrine"]."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        metadata: dict[str, Any] = deepcopy(
            project.metadata_json if isinstance(project.metadata_json, dict) else {}
        )
        raw_doctrine = metadata.get("doctrine", {})
        doctrine: dict[str, Any] = (
            raw_doctrine if isinstance(raw_doctrine, dict) else {}
        )

        if request.methodology is not None:
            doctrine["methodology"] = request.methodology
        if request.methodology_reason is not None:
            doctrine["methodology_reason"] = request.methodology_reason
        if request.required_phases is not None:
            doctrine["required_phases"] = request.required_phases
        if request.mandatory_rules is not None:
            doctrine["mandatory_rules"] = [
                r.model_dump(exclude_none=True) for r in request.mandatory_rules
            ]
        if request.recommended_rules is not None:
            doctrine["recommended_rules"] = [
                r.model_dump(exclude_none=True) for r in request.recommended_rules
            ]
        if request.architecture_constraints is not None:
            doctrine["architecture_constraints"] = request.architecture_constraints
        if request.quality_gates is not None:
            doctrine["quality_gates"] = request.quality_gates
        if request.exception_policy is not None:
            doctrine["exception_policy"] = request.exception_policy

        metadata["doctrine"] = doctrine
        project.metadata_json = metadata
        project.updated_at = datetime.now(timezone.utc)
        self.session.commit()

        def _to_rule(raw: object) -> DoctrineRuleResponse:
            d = raw if isinstance(raw, dict) else {}
            return DoctrineRuleResponse(
                rule_id=str(d.get("rule_id", "")),
                summary=str(d.get("summary", "")),
                severity=str(d.get("severity", "mandatory")),
                check=str(d["check"]) if "check" in d else None,
            )

        mandatory = [
            _to_rule(r)
            for r in (doctrine.get("mandatory_rules") or [])
            if isinstance(r, dict)
        ]
        recommended = [
            _to_rule(r)
            for r in (doctrine.get("recommended_rules") or [])
            if isinstance(r, dict)
        ]
        return ProjectDoctrineResponse(
            project_id=project_id,
            methodology=str(doctrine.get("methodology", "SDD")),
            methodology_reason=str(
                doctrine.get(
                    "methodology_reason", "cross-cutting project-state implementation"
                )
            ),
            required_phases=[
                str(p)
                for p in (doctrine.get("required_phases") or [])
                if isinstance(p, str)
            ],
            mandatory_rules=mandatory,
            recommended_rules=recommended,
            architecture_constraints=[
                str(c)
                for c in (doctrine.get("architecture_constraints") or [])
                if isinstance(c, str)
            ],
            quality_gates=[
                str(g)
                for g in (doctrine.get("quality_gates") or [])
                if isinstance(g, str)
            ],
        )

    def __init__(self, session: Session) -> None:
        """Initialize service repositories from a shared session."""
        self.session = session
        self.projects = ProjectsRepository(session)
        self.tasks = TasksRepository(session)
        self.task_dependencies = TaskDependenciesRepository(session)
        self.task_runs = TaskRunsRepository(session)
        self.checkpoints = CheckpointsRepository(session)
        self.decisions = DecisionsRepository(session)
        self.telemetry = TelemetryRepository(session)
        self.artifacts = ArtifactRepository(session)

    def get_artifact_lineage(self, artifact_id: str) -> ArtifactLineageResponse | None:
        """Return the causal lineage graph for a logical artifact.

        Returns None if no versions exist for the given artifact_id.
        The response includes all versions (ordered ascending) and all causal
        links where any of those versions appears as source or target.
        """
        versions = self.artifacts.get_versions_by_artifact_id(artifact_id)
        if not versions:
            return None

        version_ids = [v.version_id for v in versions]
        links = self.artifacts.get_links_by_version_ids(version_ids)

        return ArtifactLineageResponse(
            artifact_id=artifact_id,
            versions=[
                ArtifactVersionResponse(
                    version_id=v.version_id,
                    artifact_id=v.artifact_id,
                    artifact_type=v.artifact_type,
                    version=v.version,
                    content_hash=v.content_hash,
                    created_at=v.created_at,
                    metadata=v.metadata_json,
                )
                for v in versions
            ],
            links=[
                ArtifactLinkResponse(
                    link_id=lnk.link_id,
                    source_artifact_id=lnk.source_artifact_id,
                    target_artifact_id=lnk.target_artifact_id,
                    link_type=lnk.link_type,
                    task_id=lnk.task_id,
                    decision_id=lnk.decision_id,
                    checkpoint_id=lnk.checkpoint_id,
                    created_at=lnk.created_at,
                )
                for lnk in links
            ],
        )

    def get_task_list(
        self, project_id: str, limit: int = 200
    ) -> TaskListResponse | None:
        """Return tasks for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        effective_limit = max(1, min(limit, 500))
        tasks = [
            TaskDetailResponse(
                task_id=item.task_id,
                project_id=item.project_id,
                parent_task_id=item.parent_task_id,
                title=item.title,
                status=item.status,
                priority=item.priority,
                owner_type=item.owner_type,
                owner_id=item.owner_id,
                metadata=item.metadata_json,
                constraints=item.constraints,
                completion_criteria=item.completion_criteria,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in self.tasks.list_by_project(project_id, limit=effective_limit)
        ]
        return TaskListResponse(project_id=project_id, tasks=tasks)

    def get_token_usage_list(
        self, project_id: str, limit: int = 100
    ) -> TokenUsageListResponse | None:
        """Return recent token usage events for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        effective_limit = max(1, min(limit, 500))
        events = [
            TokenUsageEventResponse(
                usage_event_id=item.usage_event_id,
                project_id=item.project_id,
                task_id=item.task_id,
                run_id=item.run_id,
                provider=item.provider,
                model=item.model,
                auth_mode=item.auth_mode,
                prompt_tokens=item.prompt_tokens,
                completion_tokens=item.completion_tokens,
                estimated_cost=item.estimated_cost,
                metadata=item.metadata_json,
                created_at=item.created_at,
            )
            for item in self.telemetry.list_recent_by_project(
                project_id, limit=effective_limit
            )
        ]
        return TokenUsageListResponse(project_id=project_id, events=events)

    def record_token_usage(
        self,
        project_id: str,
        task_id: str,
        request: RecordTokenUsageRequest,
    ) -> TokenUsageEventResponse | None:
        """Record a token usage event for a task via the service layer.

        Returns None if the task does not exist or belongs to a different project.
        """
        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        event = self.telemetry.create_event(
            usage_event_id=str(uuid.uuid4()),
            project_id=project_id,
            task_id=task_id,
            model=request.model,
            provider=request.provider,
            auth_mode=request.auth_mode,
            prompt_tokens=request.prompt_tokens,
            completion_tokens=request.completion_tokens,
            estimated_cost=request.estimated_cost,
            run_id=request.run_id,
            metadata_json=request.metadata,
        )
        return TokenUsageEventResponse(
            usage_event_id=event.usage_event_id,
            project_id=event.project_id,
            task_id=event.task_id,
            run_id=event.run_id,
            provider=event.provider,
            model=event.model,
            auth_mode=event.auth_mode,
            prompt_tokens=event.prompt_tokens,
            completion_tokens=event.completion_tokens,
            estimated_cost=event.estimated_cost,
            metadata=event.metadata_json,
            created_at=event.created_at,
        )

    def get_task_dependencies(
        self, project_id: str, task_id: str
    ) -> TaskDependenciesResponse | None:
        """Return dependency edges for a task in a project."""
        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        dependencies = [
            TaskDependencyResponse(
                dependency_id=item.dependency_id,
                task_id=item.task_id,
                depends_on_task_id=item.depends_on_task_id,
                dependency_type=item.dependency_type,
                created_at=item.created_at,
            )
            for item in self.task_dependencies.list_by_task(task_id)
        ]
        return TaskDependenciesResponse(
            project_id=project_id,
            task_id=task_id,
            dependencies=dependencies,
        )

    def get_run_detail(self, project_id: str, run_id: str) -> RunDetailResponse | None:
        """Return a detailed run view for the given project and run ID."""
        run = self.task_runs.get_by_id(project_id, run_id)
        if run is None:
            return None

        task = self.tasks.get_by_id(project_id, run.task_id)
        return RunDetailResponse(
            run_id=run.run_id,
            project_id=run.project_id,
            task_id=run.task_id,
            task_title=task.title if task is not None else None,
            actor_type=run.actor_type,
            actor_id=run.actor_id,
            status=run.status,
            started_at=run.started_at,
            ended_at=run.ended_at,
            metadata=run.metadata_json,
        )

    def get_active_runs(
        self, project_id: str, limit: int = 50
    ) -> ActiveRunsResponse | None:
        """Return currently active runs for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        effective_limit = max(1, min(limit, 200))
        runs = self.task_runs.list_active_by_project(project_id, limit=effective_limit)
        task_ids = [run.task_id for run in runs]
        tasks_by_id = {
            task.task_id: task
            for task in self.tasks.list_recent_by_project(
                project_id, limit=max(len(task_ids), 1) * 5
            )
            if task.task_id in task_ids
        }

        return ActiveRunsResponse(
            project_id=project_id,
            runs=[
                RunDetailResponse(
                    run_id=run.run_id,
                    project_id=run.project_id,
                    task_id=run.task_id,
                    task_title=tasks_by_id[run.task_id].title
                    if run.task_id in tasks_by_id
                    else None,
                    actor_type=run.actor_type,
                    actor_id=run.actor_id,
                    status=run.status,
                    started_at=run.started_at,
                    ended_at=run.ended_at,
                    metadata=run.metadata_json,
                )
                for run in runs
            ],
        )

    def get_project_detail(self, project_id: str) -> ProjectDetailResponse | None:
        """Return a detailed project view, or None if missing."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        return ProjectDetailResponse(
            project_id=project.project_id,
            name=project.name,
            status=project.status,
            adapter_id=project.adapter_id,
            metadata=project.metadata_json,
            created_at=project.created_at,
            updated_at=project.updated_at,
        )

    def get_project_list(self, limit: int = 100) -> ProjectListResponse:
        """Return a recent project list for dashboard navigation."""
        effective_limit = max(1, min(limit, 200))
        projects = [
            ProjectDetailResponse(
                project_id=item.project_id,
                name=item.name,
                status=item.status,
                adapter_id=item.adapter_id,
                metadata=item.metadata_json,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in self.projects.list_projects(limit=effective_limit)
        ]
        return ProjectListResponse(projects=projects)

    def get_task_doctrine_projection(
        self, project_id: str, task_id: str
    ) -> DoctrineProjectionResponse | None:
        """Return a task-level doctrine projection for execution."""
        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        project_meta = (
            project.metadata_json if isinstance(project.metadata_json, dict) else {}
        )
        task_meta = task.metadata_json if isinstance(task.metadata_json, dict) else {}
        doctrine_meta = task_meta.get("doctrine", {})
        project_doctrine_meta = project_meta.get("doctrine", {})
        if not isinstance(doctrine_meta, dict):
            doctrine_meta = {}
        if not isinstance(project_doctrine_meta, dict):
            project_doctrine_meta = {}

        methodology_name = str(
            doctrine_meta.get(
                "methodology",
                project_doctrine_meta.get("methodology", "SDD"),
            )
        )
        methodology_reason = str(
            doctrine_meta.get(
                "methodology_reason",
                project_doctrine_meta.get(
                    "methodology_reason", "cross-cutting project-state implementation"
                ),
            )
        )
        required_phases_raw = doctrine_meta.get(
            "required_phases",
            project_doctrine_meta.get(
                "required_phases", ["spec", "design", "implementation", "review"]
            ),
        )
        required_phases = (
            [str(item) for item in required_phases_raw]
            if isinstance(required_phases_raw, list)
            else ["implementation", "review"]
        )

        mandatory_rules_raw = doctrine_meta.get(
            "mandatory_rules",
            project_doctrine_meta.get(
                "mandatory_rules",
                [
                    {
                        "rule_id": "state-structured-source-of-truth",
                        "summary": "Use structured project state as source of truth",
                        "severity": "mandatory",
                        "check": "Projection must derive from project state records",
                    },
                    {
                        "rule_id": "explicit-read-models",
                        "summary": "Expose explicit read-side projections for UI and agents",
                        "severity": "mandatory",
                        "check": "Endpoints return typed projection payloads",
                    },
                ],
            ),
        )
        recommended_rules_raw = doctrine_meta.get(
            "recommended_rules",
            project_doctrine_meta.get(
                "recommended_rules",
                [
                    {
                        "rule_id": "artifact-first-context",
                        "summary": "Prefer structured artifacts over transcript history",
                        "severity": "recommended",
                        "check": "Include checkpoints/decisions before logs",
                    }
                ],
            ),
        )

        def _normalize_rules(
            raw: object, default_severity: str
        ) -> list[DoctrineRuleResponse]:
            if not isinstance(raw, list):
                return []
            rules: list[DoctrineRuleResponse] = []
            for idx, item in enumerate(raw):
                if isinstance(item, dict):
                    rules.append(
                        DoctrineRuleResponse(
                            rule_id=str(item.get("rule_id", f"rule-{idx+1}")),
                            summary=str(item.get("summary", "")),
                            severity=str(item.get("severity", default_severity)),
                            check=(
                                str(item.get("check"))
                                if item.get("check") is not None
                                else None
                            ),
                        )
                    )
                else:
                    rules.append(
                        DoctrineRuleResponse(
                            rule_id=f"rule-{idx+1}",
                            summary=str(item),
                            severity=default_severity,
                            check=None,
                        )
                    )
            return rules

        architecture_constraints_raw = doctrine_meta.get(
            "architecture_constraints",
            project_doctrine_meta.get(
                "architecture_constraints",
                [
                    "Keep project_state isolated from legacy runtime state modules",
                    "Return projection-oriented schemas instead of ORM payloads",
                ],
            ),
        )
        architecture_constraints = (
            [str(item) for item in architecture_constraints_raw]
            if isinstance(architecture_constraints_raw, list)
            else []
        )

        quality_gates_raw = doctrine_meta.get(
            "quality_gates",
            project_doctrine_meta.get(
                "quality_gates",
                [
                    "Unit tests added for service projections",
                    "API tests added for public route behavior",
                    "Projection remains compatible with explicit backend-service boundary",
                ],
            ),
        )
        quality_gates = (
            [str(item) for item in quality_gates_raw]
            if isinstance(quality_gates_raw, list)
            else []
        )

        exception_policy_raw = doctrine_meta.get(
            "exception_policy", project_doctrine_meta.get("exception_policy", {})
        )
        if not isinstance(exception_policy_raw, dict):
            exception_policy_raw = {}

        return DoctrineProjectionResponse(
            project_id=project_id,
            task_id=task_id,
            scope="task",
            generated_at=datetime.now(timezone.utc),
            methodology=DoctrineMethodologyResponse(
                active=methodology_name,
                reason=methodology_reason,
                required_phases=required_phases,
            ),
            mandatory_rules=_normalize_rules(mandatory_rules_raw, "mandatory"),
            recommended_rules=_normalize_rules(recommended_rules_raw, "recommended"),
            architecture_constraints=architecture_constraints,
            quality_gates=quality_gates,
            exception_policy=DoctrineExceptionPolicyResponse(
                human_approval_required_for_overrides=bool(
                    exception_policy_raw.get(
                        "human_approval_required_for_overrides", True
                    )
                ),
                pause_if_mandatory_rule_cannot_be_met=bool(
                    exception_policy_raw.get(
                        "pause_if_mandatory_rule_cannot_be_met", True
                    )
                ),
            ),
        )

    def get_task_context_projection(
        self, project_id: str, task_id: str
    ) -> TaskContextProjectionResponse | None:
        """Return a minimal task context projection for execution continuity."""
        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        latest_checkpoint = self.checkpoints.get_latest_by_task(project_id, task_id)
        decisions = self.decisions.list_recent_by_task(project_id, task_id, limit=5)
        if not decisions:
            decisions = self.decisions.list_recent_by_project(project_id, limit=5)

        blockers_raw = task.metadata_json.get("blockers", [])
        blockers = (
            [str(item) for item in blockers_raw]
            if isinstance(blockers_raw, list)
            else []
        )

        dependencies_raw = task.metadata_json.get("dependencies", [])
        dependencies = (
            [str(item) for item in dependencies_raw]
            if isinstance(dependencies_raw, list)
            else []
        )

        artifacts_raw = task.metadata_json.get("relevant_artifacts", [])
        relevant_artifacts = (
            [str(item) for item in artifacts_raw]
            if isinstance(artifacts_raw, list)
            else []
        )

        return TaskContextProjectionResponse(
            project_id=project_id,
            task_id=task_id,
            generated_at=datetime.now(timezone.utc),
            objective=task.title,
            status=task.status,
            priority=task.priority,
            blockers=blockers,
            dependencies=dependencies,
            constraints=task.constraints,
            completion_criteria=task.completion_criteria,
            critical_decisions=[
                ContextDecisionSummary(
                    decision_id=item.decision_id,
                    title=item.title,
                    status=item.status,
                    created_at=item.created_at,
                )
                for item in decisions
            ],
            latest_checkpoint_id=(
                latest_checkpoint.checkpoint_id
                if latest_checkpoint is not None
                else None
            ),
            next_step=(
                latest_checkpoint.next_step_summary
                if latest_checkpoint is not None
                else None
            ),
            relevant_artifacts=relevant_artifacts,
        )

    def get_decision_detail(
        self, project_id: str, decision_id: str
    ) -> DecisionDetailResponse | None:
        """Return a detailed decision view, or None if missing."""
        decision = self.decisions.get_by_id(project_id, decision_id)
        if decision is None:
            return None

        return DecisionDetailResponse(
            decision_id=decision.decision_id,
            project_id=decision.project_id,
            task_id=decision.task_id,
            title=decision.title,
            status=decision.status,
            rationale_markdown=decision.rationale_markdown,
            metadata=decision.metadata_json,
            created_at=decision.created_at,
        )

    def get_decision_list(
        self, project_id: str, limit: int = 20
    ) -> DecisionListResponse | None:
        """Return a recent decision list for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        effective_limit = max(1, min(limit, 100))
        decisions = [
            DecisionDetailResponse(
                decision_id=item.decision_id,
                project_id=item.project_id,
                task_id=item.task_id,
                title=item.title,
                status=item.status,
                rationale_markdown=item.rationale_markdown,
                metadata=item.metadata_json,
                created_at=item.created_at,
            )
            for item in self.decisions.list_recent_by_project(
                project_id, effective_limit
            )
        ]
        return DecisionListResponse(project_id=project_id, decisions=decisions)

    def get_activity_feed(
        self, project_id: str, limit: int = 20
    ) -> ActivityFeedResponse | None:
        """Return a recent activity feed for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        effective_limit = max(1, min(limit, 100))
        events: list[ActivityFeedEventResponse] = []

        for task in self.tasks.list_recent_by_project(project_id, effective_limit):
            events.append(
                ActivityFeedEventResponse(
                    event_type="task_updated",
                    occurred_at=task.updated_at,
                    project_id=project_id,
                    task_id=task.task_id,
                    entity_id=task.task_id,
                    title=task.title,
                    summary=f"Task status is {task.status}",
                    metadata={
                        "status": task.status,
                        "priority": task.priority,
                        "owner_type": task.owner_type or "",
                        "owner_id": task.owner_id or "",
                    },
                )
            )

        for checkpoint in self.checkpoints.list_recent_by_project(
            project_id, effective_limit
        ):
            events.append(
                ActivityFeedEventResponse(
                    event_type="checkpoint_created",
                    occurred_at=checkpoint.created_at,
                    project_id=project_id,
                    task_id=checkpoint.task_id,
                    entity_id=checkpoint.checkpoint_id,
                    title="Checkpoint created",
                    summary=checkpoint.next_step_summary,
                    metadata={"run_id": checkpoint.run_id or ""},
                )
            )

        for decision in self.decisions.list_recent_by_project(
            project_id, effective_limit
        ):
            events.append(
                ActivityFeedEventResponse(
                    event_type="decision_recorded",
                    occurred_at=decision.created_at,
                    project_id=project_id,
                    task_id=decision.task_id,
                    entity_id=decision.decision_id,
                    title=decision.title,
                    summary=f"Decision status is {decision.status}",
                    metadata={"status": decision.status},
                )
            )

        for usage in self.telemetry.list_recent_by_project(project_id, effective_limit):
            events.append(
                ActivityFeedEventResponse(
                    event_type="token_usage_recorded",
                    occurred_at=usage.created_at,
                    project_id=project_id,
                    task_id=usage.task_id,
                    entity_id=usage.usage_event_id,
                    title=f"{usage.provider} / {usage.model}",
                    summary=(
                        f"Recorded {usage.prompt_tokens} prompt and "
                        f"{usage.completion_tokens} completion tokens"
                    ),
                    metadata={
                        "provider": usage.provider,
                        "model": usage.model,
                        "auth_mode": usage.auth_mode,
                        "estimated_cost": usage.estimated_cost,
                    },
                )
            )

        sorted_events = sorted(
            events, key=lambda item: self._occurred_at(item.occurred_at), reverse=True
        )[:effective_limit]
        return ActivityFeedResponse(project_id=project_id, events=sorted_events)

    def get_realtime_events(
        self, project_id: str, limit: int = 20
    ) -> list[ProjectStateRealtimeEvent] | None:
        """Return recent project-state events as a typed realtime event list.

        Returns ``None`` if the project does not exist.  Consumers subscribe to
        the SSE stream and use these events to decide whether a refresh is needed
        — the event shape is the explicit contract between backend and UI.
        """
        feed = self.get_activity_feed(project_id, limit=limit)
        if feed is None:
            return None

        return [
            ProjectStateRealtimeEvent(
                event_type=item.event_type,
                project_id=item.project_id,
                entity_id=item.entity_id,
                occurred_at=item.occurred_at,
                summary=item.summary,
                metadata=dict(item.metadata),
            )
            for item in feed.events
        ]

    def get_project_cost_summary(
        self, project_id: str
    ) -> ProjectCostSummaryResponse | None:
        """Return aggregated token and cost totals for a project."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        aggregate = self.telemetry.get_project_cost_aggregate(project_id)
        return ProjectCostSummaryResponse(
            project_id=project_id,
            total_prompt_tokens=aggregate.total_prompt_tokens,
            total_completion_tokens=aggregate.total_completion_tokens,
            total_estimated_cost=aggregate.total_estimated_cost,
            providers=[
                ProviderCostSummary(
                    provider=item.provider,
                    total_prompt_tokens=item.total_prompt_tokens,
                    total_completion_tokens=item.total_completion_tokens,
                    total_estimated_cost=item.total_estimated_cost,
                )
                for item in aggregate.providers
            ],
        )

    def get_task_detail(
        self, project_id: str, task_id: str
    ) -> TaskDetailResponse | None:
        """Return a task detail view, or None if the task does not exist."""
        task = self.tasks.get_by_id(project_id, task_id)
        if task is None:
            return None

        return TaskDetailResponse(
            task_id=task.task_id,
            project_id=task.project_id,
            parent_task_id=task.parent_task_id,
            title=task.title,
            status=task.status,
            priority=task.priority,
            owner_type=task.owner_type,
            owner_id=task.owner_id,
            metadata=task.metadata_json,
            constraints=task.constraints,
            completion_criteria=task.completion_criteria,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )

    def get_latest_checkpoint(self, project_id: str) -> LatestCheckpointResponse | None:
        """Return the latest checkpoint for a project, or None if none exists."""
        checkpoint = self.checkpoints.get_latest_by_project(project_id)
        if checkpoint is None:
            return None

        return LatestCheckpointResponse(
            checkpoint_id=checkpoint.checkpoint_id,
            project_id=checkpoint.project_id,
            task_id=checkpoint.task_id,
            run_id=checkpoint.run_id,
            context_summary=checkpoint.context_summary,
            resume_state=checkpoint.resume_state,
            next_step_summary=checkpoint.next_step_summary,
            created_at=checkpoint.created_at,
        )

    def get_overview(self, project_id: str) -> ProjectOverviewResponse | None:
        """Return the project overview, or None if the project does not exist."""
        project = self.projects.get_by_id(project_id)
        if project is None:
            return None

        total_tasks = self.tasks.count_by_project(project_id)
        active_tasks = self.tasks.count_by_project_and_status(project_id, "in_progress")
        blocked_tasks = self.tasks.count_by_project_and_status(project_id, "blocked")
        latest_checkpoint = self.checkpoints.get_latest_by_project(project_id)
        latest_decision = self.decisions.get_latest_by_project(project_id)
        total_estimated_cost = self.telemetry.get_project_cost_total(project_id)

        checkpoint_summary = None
        if latest_checkpoint is not None:
            checkpoint_summary = CheckpointSummary(
                checkpoint_id=latest_checkpoint.checkpoint_id,
                task_id=latest_checkpoint.task_id,
                next_step_summary=latest_checkpoint.next_step_summary,
                created_at=latest_checkpoint.created_at,
            )

        decision_summary = None
        if latest_decision is not None:
            decision_summary = DecisionSummary(
                decision_id=latest_decision.decision_id,
                title=latest_decision.title,
                status=latest_decision.status,
                created_at=latest_decision.created_at,
            )

        return ProjectOverviewResponse(
            project_id=project.project_id,
            name=project.name,
            status=project.status,
            adapter_id=project.adapter_id,
            total_tasks=total_tasks,
            active_tasks=active_tasks,
            blocked_tasks=blocked_tasks,
            total_estimated_cost=total_estimated_cost,
            latest_checkpoint=checkpoint_summary,
            latest_decision=decision_summary,
        )
