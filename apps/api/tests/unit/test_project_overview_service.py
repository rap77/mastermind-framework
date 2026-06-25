"""Unit tests for the project overview service."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from mastermind_cli.project_state.database.session import (
    dispose_engines,
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.artifact import ArtifactLink, ArtifactVersion
from mastermind_cli.project_state.models.checkpoint import Checkpoint
from mastermind_cli.project_state.models.decision import DecisionRecord
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_dependency import TaskDependency
from mastermind_cli.project_state.models.task_run import TaskRun
from mastermind_cli.project_state.models.token_usage import TokenUsageEvent
from mastermind_cli.project_state.services.project_overview import (
    ProjectOverviewService,
)
from mastermind_cli.project_state.schemas.overview import (
    CreateCheckpointRequest,
    CreateDecisionRequest,
    DoctrineUpdateRequest,
    RecordTokenUsageRequest,
    UpdateTaskStatusRequest,
)


def test_project_overview_service_builds_expected_summary(tmp_path: Path) -> None:
    """Build a project overview from seeded project state records."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)

    project_id = "project-alpha"
    checkpoint_id = str(uuid.uuid4())
    decision_id = str(uuid.uuid4())

    with session_factory() as session:
        session.add(
            Project(
                project_id=project_id,
                name="Project Alpha",
                status="active",
                adapter_id="finance-trading-pilot",
                metadata_json={},
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-1",
                    project_id=project_id,
                    title="Active task",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-05",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                ),
                Task(
                    task_id="task-2",
                    project_id=project_id,
                    title="Blocked task",
                    status="blocked",
                    priority="normal",
                    owner_type="human",
                    owner_id="user-1",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                ),
            ]
        )
        session.add(
            Checkpoint(
                checkpoint_id=checkpoint_id,
                project_id=project_id,
                task_id="task-1",
                run_id="run-1",
                context_summary={"summary": "Checkpoint"},
                resume_state={"state": "resume"},
                next_step_summary="Continue implementation",
                created_at=datetime.now(timezone.utc),
            )
        )
        session.add(
            DecisionRecord(
                decision_id=decision_id,
                project_id=project_id,
                task_id="task-1",
                title="Adopt hybrid runtime",
                status="approved",
                rationale_markdown="Use hybrid mode by default.",
                metadata_json={},
                created_at=datetime.now(timezone.utc),
            )
        )
        session.add(
            TokenUsageEvent(
                usage_event_id=str(uuid.uuid4()),
                project_id=project_id,
                task_id="task-1",
                run_id="run-1",
                provider="anthropic",
                model="claude",
                auth_mode="subscription",
                prompt_tokens=100,
                completion_tokens=50,
                estimated_cost=1.25,
                metadata_json={},
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        overview = service.get_overview(project_id)

    assert overview is not None
    assert overview.project_id == project_id
    assert overview.name == "Project Alpha"
    assert overview.total_tasks == 2
    assert overview.active_tasks == 1
    assert overview.blocked_tasks == 1
    assert overview.total_estimated_cost == 1.25
    assert overview.latest_checkpoint is not None
    assert overview.latest_checkpoint.checkpoint_id == checkpoint_id
    assert overview.latest_decision is not None
    assert overview.latest_decision.decision_id == decision_id


def test_project_overview_service_returns_task_detail_and_latest_checkpoint(
    tmp_path: Path,
) -> None:
    """Return detailed task and checkpoint views from seeded records."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)

    created_at = datetime.now(timezone.utc)
    with session_factory() as session:
        session.add(
            Project(
                project_id="project-beta",
                name="Project Beta",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-42",
                project_id="project-beta",
                parent_task_id="task-parent",
                title="Implement dashboard projection",
                status="in_progress",
                priority="critical",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={"lane": "backend"},
                constraints={"must_use": ["sqlalchemy"]},
                completion_criteria={"done": True},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            Checkpoint(
                checkpoint_id="chk-1",
                project_id="project-beta",
                task_id="task-42",
                run_id="run-42",
                context_summary={"phase": "implementation"},
                resume_state={"cursor": 3},
                next_step_summary="Implement task detail endpoint",
                created_at=created_at,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        task = service.get_task_detail("project-beta", "task-42")
        checkpoint = service.get_latest_checkpoint("project-beta")

    assert task is not None
    assert task.task_id == "task-42"
    assert task.parent_task_id == "task-parent"
    assert task.priority == "critical"
    assert task.metadata == {"lane": "backend"}
    assert checkpoint is not None
    assert checkpoint.checkpoint_id == "chk-1"
    assert checkpoint.run_id == "run-42"
    assert checkpoint.context_summary == {"phase": "implementation"}


def test_project_overview_service_returns_project_cost_summary(tmp_path: Path) -> None:
    """Return aggregated token and cost totals for a project."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-costs",
                name="Project Costs",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            TokenUsageEvent(
                usage_event_id=str(uuid.uuid4()),
                project_id="project-costs",
                task_id=None,
                run_id="run-1",
                provider="anthropic",
                model="claude",
                auth_mode="subscription",
                prompt_tokens=12,
                completion_tokens=8,
                estimated_cost=0.5,
                metadata_json={},
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        summary = service.get_project_cost_summary("project-costs")

    assert summary is not None
    assert summary.project_id == "project-costs"
    assert summary.total_prompt_tokens == 12
    assert summary.total_completion_tokens == 8
    assert summary.total_estimated_cost == 0.5
    assert len(summary.providers) == 1
    assert summary.providers[0].provider == "anthropic"


def test_project_overview_service_returns_activity_feed(tmp_path: Path) -> None:
    """Return a recent mixed activity feed for a project."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-feed",
                name="Project Feed",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-feed",
                project_id="project-feed",
                title="Implement activity feed",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            TokenUsageEvent(
                usage_event_id=str(uuid.uuid4()),
                project_id="project-feed",
                task_id="task-feed",
                run_id="run-feed",
                provider="anthropic",
                model="claude",
                auth_mode="subscription",
                prompt_tokens=10,
                completion_tokens=5,
                estimated_cost=0.2,
                metadata_json={},
                created_at=now + timedelta(minutes=1),
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        feed = service.get_activity_feed("project-feed", limit=10)

    assert feed is not None
    assert feed.project_id == "project-feed"
    assert len(feed.events) == 2
    assert feed.events[0].event_type == "token_usage_recorded"
    assert feed.events[1].event_type == "task_updated"


def test_project_overview_service_returns_decision_views(tmp_path: Path) -> None:
    """Return decision list and detail views from seeded records."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-decisions",
                name="Project Decisions",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            DecisionRecord(
                decision_id="dec-1",
                project_id="project-decisions",
                task_id="task-1",
                title="Choose hybrid runtime",
                status="approved",
                rationale_markdown="Hybrid is the default.",
                metadata_json={"brain": "runtime"},
                created_at=created_at,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        decision = service.get_decision_detail("project-decisions", "dec-1")
        decisions = service.get_decision_list("project-decisions", limit=10)

    assert decision is not None
    assert decision.decision_id == "dec-1"
    assert decision.metadata == {"brain": "runtime"}
    assert decisions is not None
    assert len(decisions.decisions) == 1
    assert decisions.decisions[0].title == "Choose hybrid runtime"


def test_project_overview_service_returns_task_context_projection(
    tmp_path: Path,
) -> None:
    """Return a compact task context projection from seeded records."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-context",
                name="Project Context",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-context",
                project_id="project-context",
                title="Implement context projection",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={
                    "blockers": ["waiting for review"],
                    "dependencies": ["task-overview"],
                    "relevant_artifacts": ["SPEC.md"],
                },
                constraints={"must_use": ["postgres"]},
                completion_criteria={"done": True},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.add(
            Checkpoint(
                checkpoint_id="chk-context",
                project_id="project-context",
                task_id="task-context",
                run_id="run-context",
                context_summary={},
                resume_state={},
                next_step_summary="Continue implementation",
                created_at=created_at,
            )
        )
        session.add(
            DecisionRecord(
                decision_id="dec-context",
                project_id="project-context",
                task_id="task-context",
                title="Keep projections explicit",
                status="approved",
                rationale_markdown="Explicit routes improve traceability.",
                metadata_json={},
                created_at=created_at,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        projection = service.get_task_context_projection(
            "project-context", "task-context"
        )

    assert projection is not None
    assert projection.task_id == "task-context"
    assert projection.blockers == ["waiting for review"]
    assert projection.dependencies == ["task-overview"]
    assert projection.latest_checkpoint_id == "chk-context"
    assert projection.critical_decisions[0].decision_id == "dec-context"


def test_project_overview_service_returns_task_doctrine_projection(
    tmp_path: Path,
) -> None:
    """Return a doctrine projection for a task using seeded doctrine metadata."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-doctrine",
                name="Project Doctrine",
                status="active",
                adapter_id="default-adapter",
                metadata_json={"doctrine": {"methodology": "SDD"}},
            )
        )
        session.add(
            Task(
                task_id="task-doctrine",
                project_id="project-doctrine",
                title="Implement doctrine projection",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={
                    "doctrine": {
                        "mandatory_rules": [
                            "Projection must expose mandatory rules clearly"
                        ]
                    }
                },
                constraints={},
                completion_criteria={},
                created_at=created_at,
                updated_at=created_at,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        projection = service.get_task_doctrine_projection(
            "project-doctrine", "task-doctrine"
        )

    assert projection is not None
    assert projection.methodology.active == "SDD"
    assert (
        projection.mandatory_rules[0].summary
        == "Projection must expose mandatory rules clearly"
    )
    assert projection.exception_policy.pause_if_mandatory_rule_cannot_be_met is True


def test_project_overview_service_returns_project_list_and_detail(
    tmp_path: Path,
) -> None:
    """Return project list and detail views from seeded records."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add_all(
            [
                Project(
                    project_id="project-a",
                    name="Project A",
                    status="active",
                    adapter_id="adapter-a",
                    metadata_json={"tier": "gold"},
                    created_at=now,
                    updated_at=now,
                ),
                Project(
                    project_id="project-b",
                    name="Project B",
                    status="paused",
                    adapter_id="adapter-b",
                    metadata_json={},
                    created_at=now,
                    updated_at=now.replace(microsecond=0),
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        listing = service.get_project_list(limit=10)
        detail = service.get_project_detail("project-a")

    assert len(listing.projects) == 2
    assert listing.projects[0].project_id == "project-a"
    assert detail is not None
    assert detail.project_id == "project-a"
    assert detail.metadata == {"tier": "gold"}


def test_project_overview_service_returns_active_runs_and_run_detail(
    tmp_path: Path,
) -> None:
    """Return active run projections and individual run detail."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-runs",
                name="Project Runs",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-active",
                    project_id="project-runs",
                    title="Active execution",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-04",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-ended",
                    project_id="project-runs",
                    title="Ended execution",
                    status="done",
                    priority="normal",
                    owner_type="agent",
                    owner_id="brain-06",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.add_all(
            [
                TaskRun(
                    run_id="run-active",
                    project_id="project-runs",
                    task_id="task-active",
                    actor_type="agent",
                    actor_id="brain-04",
                    status="running",
                    started_at=now,
                    ended_at=None,
                    metadata_json={"mode": "automatic_cycle"},
                ),
                TaskRun(
                    run_id="run-ended",
                    project_id="project-runs",
                    task_id="task-ended",
                    actor_type="agent",
                    actor_id="brain-06",
                    status="completed",
                    started_at=now - timedelta(minutes=10),
                    ended_at=now - timedelta(minutes=1),
                    metadata_json={},
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        active_runs = service.get_active_runs("project-runs", limit=10)
        run_detail = service.get_run_detail("project-runs", "run-active")

    assert active_runs is not None
    assert active_runs.project_id == "project-runs"
    assert len(active_runs.runs) == 1
    assert active_runs.runs[0].run_id == "run-active"
    assert active_runs.runs[0].task_title == "Active execution"
    assert active_runs.runs[0].metadata == {"mode": "automatic_cycle"}
    assert run_detail is not None
    assert run_detail.run_id == "run-active"
    assert run_detail.task_title == "Active execution"


def test_project_overview_service_returns_task_list_and_dependencies(
    tmp_path: Path,
) -> None:
    """Return task list and dependency projections for a project."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-graph",
                name="Project Graph",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-a",
                    project_id="project-graph",
                    title="Task A",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-04",
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-b",
                    project_id="project-graph",
                    title="Task B",
                    status="pending",
                    priority="normal",
                    owner_type=None,
                    owner_id=None,
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now - timedelta(minutes=1),
                    updated_at=now - timedelta(minutes=1),
                ),
            ]
        )
        session.add(
            TaskDependency(
                dependency_id="dep-1",
                task_id="task-a",
                depends_on_task_id="task-b",
                dependency_type="blocks",
                created_at=now,
            )
        )
        session.add(
            TaskDependency(
                dependency_id="dep-invalid",
                task_id="task-a",
                depends_on_task_id="task-missing",
                dependency_type="relates_to",
                created_at=now,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        task_list = service.get_task_list("project-graph", limit=10)
        task_dependencies = service.get_task_dependencies("project-graph", "task-a")

    assert task_list is not None
    assert task_list.project_id == "project-graph"
    assert [item.task_id for item in task_list.tasks] == ["task-a", "task-b"]
    assert task_dependencies is not None
    assert task_dependencies.task_id == "task-a"
    assert len(task_dependencies.dependencies) == 1
    assert task_dependencies.dependencies[0].dependency_id == "dep-1"
    assert task_dependencies.dependencies[0].depends_on_task_id == "task-b"


def test_project_overview_service_returns_token_usage_list(tmp_path: Path) -> None:
    """Return recent token usage events for telemetry drill-down."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-telemetry",
                name="Project Telemetry",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add_all(
            [
                TokenUsageEvent(
                    usage_event_id="usage-new",
                    project_id="project-telemetry",
                    task_id="task-1",
                    run_id="run-1",
                    provider="anthropic",
                    model="claude",
                    auth_mode="subscription",
                    prompt_tokens=25,
                    completion_tokens=15,
                    estimated_cost=0.75,
                    metadata_json={"phase": "implementation"},
                    created_at=now,
                ),
                TokenUsageEvent(
                    usage_event_id="usage-old",
                    project_id="project-telemetry",
                    task_id="task-2",
                    run_id="run-2",
                    provider="openai",
                    model="gpt-5",
                    auth_mode="api_key",
                    prompt_tokens=10,
                    completion_tokens=5,
                    estimated_cost=0.2,
                    metadata_json={},
                    created_at=now - timedelta(minutes=5),
                ),
            ]
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        usage = service.get_token_usage_list("project-telemetry", limit=10)

    assert usage is not None
    assert usage.project_id == "project-telemetry"
    assert [item.usage_event_id for item in usage.events] == ["usage-new", "usage-old"]
    assert usage.events[0].metadata == {"phase": "implementation"}


def test_project_overview_service_returns_time_summary(tmp_path: Path) -> None:
    """Return a heuristic time summary with confidence and ETA."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-time",
                name="Project Time",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
                created_at=now - timedelta(hours=3),
                updated_at=now,
            )
        )
        session.add_all(
            [
                Task(
                    task_id="task-done",
                    project_id="project-time",
                    title="Done task",
                    status="done",
                    priority="normal",
                    owner_type="agent",
                    owner_id="brain-04",
                    metadata_json={"estimated_minutes": 30},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-active",
                    project_id="project-time",
                    title="Active task",
                    status="in_progress",
                    priority="high",
                    owner_type="agent",
                    owner_id="brain-05",
                    metadata_json={"estimated_effort": "2-3 hours"},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
                Task(
                    task_id="task-pending",
                    project_id="project-time",
                    title="Pending task",
                    status="pending",
                    priority="low",
                    owner_type=None,
                    owner_id=None,
                    metadata_json={},
                    constraints={},
                    completion_criteria={},
                    created_at=now,
                    updated_at=now,
                ),
            ]
        )
        session.add(
            TaskRun(
                run_id="run-time",
                project_id="project-time",
                task_id="task-active",
                actor_type="agent",
                actor_id="brain-05",
                status="running",
                started_at=now - timedelta(minutes=25),
                ended_at=None,
                metadata_json={},
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        summary = service.get_project_time_summary("project-time")

    assert summary is not None
    assert summary.project_id == "project-time"
    assert summary.total_tasks == 3
    assert summary.completed_tasks == 1
    assert summary.remaining_tasks == 2
    assert summary.active_run_count == 1
    assert summary.explicit_estimate_task_count == 2
    assert summary.fallback_estimate_task_count == 1
    assert summary.remaining_explicit_estimate_task_count == 1
    assert summary.remaining_fallback_estimate_task_count == 1
    assert summary.estimated_total_minutes == 210
    assert summary.estimated_remaining_minutes == 180
    assert summary.active_run_elapsed_minutes >= 25
    assert summary.project_age_minutes >= 180
    assert summary.confidence == "medium"
    assert summary.projected_completion_at is not None


def test_project_overview_service_creates_checkpoint_and_decision(
    tmp_path: Path,
) -> None:
    """Create checkpoint and decision records through the service layer."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-write",
                name="Project Write",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-write",
                project_id="project-write",
                title="Task Write",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        checkpoint = service.create_checkpoint(
            "project-write",
            "task-write",
            CreateCheckpointRequest(
                run_id="run-write",
                context_summary={"phase": "implementation"},
                resume_state={"cursor": 2},
                next_step_summary="Continue implementing the write-side endpoint",
            ),
            actor_user_id="test-user-id-001",
        )
        decision = service.create_decision(
            "project-write",
            CreateDecisionRequest(
                task_id="task-write",
                title="Record write-side decision",
                status="approved",
                rationale_markdown="Persist checkpoint and decision via project_state.",
                metadata={"brain": "backend"},
            ),
            actor_user_id="test-user-id-001",
        )

    assert checkpoint is not None
    assert checkpoint.run_id == "run-write"
    assert checkpoint.context_summary == {"phase": "implementation"}
    assert decision is not None
    assert decision.task_id == "task-write"
    assert decision.metadata["brain"] == "backend"
    assert decision.metadata["recorded_by"] == "test-user-id-001"


def test_project_overview_service_normalizes_invalid_task_metadata_on_checkpoint(
    tmp_path: Path,
) -> None:
    """Create a checkpoint even when task metadata is not a dict."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-bad-metadata",
                name="Project Bad Metadata",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-bad-metadata",
                project_id="project-bad-metadata",
                title="Task Bad Metadata",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json=["unexpected", "metadata"],
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        checkpoint = service.create_checkpoint(
            "project-bad-metadata",
            "task-bad-metadata",
            CreateCheckpointRequest(
                run_id="run-bad-metadata",
                context_summary={"phase": "implementation"},
                resume_state={"cursor": 2},
                next_step_summary="Continue despite legacy metadata",
            ),
            actor_user_id="test-user-id-001",
        )
        task = service.get_task_detail("project-bad-metadata", "task-bad-metadata")

    assert checkpoint is not None
    assert checkpoint.run_id == "run-bad-metadata"
    assert task is not None
    assert task.metadata["last_checkpoint_by"] == "test-user-id-001"
    assert task.metadata["last_checkpoint_at"].startswith(str(now.year))


def test_project_overview_service_returns_artifact_lineage(tmp_path: Path) -> None:
    """Return ordered artifact versions and causal links for one artifact."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-artifacts",
                name="Project Artifacts",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
            )
        )
        session.add(
            Task(
                task_id="task-artifact",
                project_id="project-artifacts",
                title="Track lineage",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add_all(
            [
                ArtifactVersion(
                    version_id="version-1",
                    artifact_id="artifact-1",
                    project_id="project-artifacts",
                    artifact_type="spec",
                    version=1,
                    content_hash="hash-1",
                    created_at=now,
                    metadata_json={"phase": "draft"},
                ),
                ArtifactVersion(
                    version_id="version-2",
                    artifact_id="artifact-1",
                    project_id="project-artifacts",
                    artifact_type="spec",
                    version=2,
                    content_hash="hash-2",
                    created_at=now + timedelta(minutes=1),
                    metadata_json={"phase": "approved"},
                ),
            ]
        )
        session.add(
            ArtifactLink(
                link_id="link-1",
                source_artifact_id="version-1",
                target_artifact_id="version-2",
                link_type="supersedes",
                task_id="task-artifact",
                decision_id=None,
                checkpoint_id=None,
                created_at=now + timedelta(minutes=2),
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        lineage = service.get_artifact_lineage("artifact-1")

    assert lineage is not None
    assert [item.version for item in lineage.versions] == [1, 2]
    assert lineage.links[0].link_id == "link-1"
    assert lineage.links[0].link_type == "supersedes"


def test_project_overview_service_updates_task_status_and_project_doctrine(
    tmp_path: Path,
) -> None:
    """Update task status metadata and persist doctrine changes."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-doctrine-write",
                name="Project Doctrine Write",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-doctrine-write",
                project_id="project-doctrine-write",
                title="Update doctrine",
                status="pending",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        updated_task = service.update_task_status(
            "project-doctrine-write",
            "task-doctrine-write",
            UpdateTaskStatusRequest(status="blocked", reason="waiting on security"),
            actor_user_id="user-42",
        )
        doctrine = service.update_project_doctrine(
            "project-doctrine-write",
            DoctrineUpdateRequest(
                methodology="SDD",
                methodology_reason="High coordination work",
                required_phases=["discover", "plan", "verify"],
                quality_gates=["gga", "uat"],
            ),
        )

    assert updated_task is not None
    assert updated_task.status == "blocked"
    assert updated_task.metadata["status_updated_by"] == "user-42"
    assert updated_task.metadata["status_reason"] == "waiting on security"
    assert doctrine is not None
    assert doctrine.project_id == "project-doctrine-write"
    assert doctrine.methodology == "SDD"
    assert doctrine.required_phases == ["discover", "plan", "verify"]
    assert doctrine.quality_gates == ["gga", "uat"]


def test_project_overview_service_records_usage_quality_and_realtime_events(
    tmp_path: Path,
) -> None:
    """Record token usage, derive quality summary, and expose realtime feed events."""
    database_url = f"sqlite:///{tmp_path / 'project_state.db'}"
    dispose_engines()
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)

    with session_factory() as session:
        session.add(
            Project(
                project_id="project-realtime",
                name="Project Realtime",
                status="active",
                adapter_id="default-adapter",
                metadata_json={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            Task(
                task_id="task-realtime",
                project_id="project-realtime",
                title="Emit realtime events",
                status="in_progress",
                priority="high",
                owner_type="agent",
                owner_id="brain-04",
                metadata_json={},
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.commit()

    with session_factory() as session:
        service = ProjectOverviewService(session)
        usage = service.record_token_usage(
            "project-realtime",
            "task-realtime",
            RecordTokenUsageRequest(
                model="claude-sonnet-4-6",
                provider="anthropic",
                auth_mode="subscription",
                prompt_tokens=120,
                completion_tokens=30,
                estimated_cost=1.5,
                metadata={"phase": "qa"},
                agent_id="brain-06",
                review_pass=True,
                verification_pass=False,
                rework_count=2,
            ),
        )
        quality = service.get_project_quality_summary("project-realtime")
        realtime_events = service.get_realtime_events("project-realtime", limit=10)

    assert usage is not None
    assert usage.metadata["agent_id"] == "brain-06"
    assert usage.metadata["review_pass"] is True
    assert quality is not None
    assert quality.total_events == 1
    assert quality.review_pass_count == 1
    assert quality.verification_fail_count == 1
    assert quality.avg_rework_count == 2.0
    assert realtime_events is not None
    assert any(event.event_type == "token_usage_recorded" for event in realtime_events)
