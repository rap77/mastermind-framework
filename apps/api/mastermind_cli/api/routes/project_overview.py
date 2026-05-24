"""Project overview REST endpoints for the project state thin slice."""

from __future__ import annotations

import asyncio
import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from mastermind_cli.api.dependencies import get_project_state_db_url
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.project_state.database.session import get_session_factory
from mastermind_cli.project_state.schemas.overview import (
    ActiveRunsResponse,
    ActivityFeedResponse,
    CreateCheckpointRequest,
    CreateDecisionRequest,
    DecisionDetailResponse,
    DecisionListResponse,
    DoctrineProjectionResponse,
    LatestCheckpointResponse,
    ProjectCostSummaryResponse,
    ProjectDetailResponse,
    ProjectListResponse,
    ProjectOverviewResponse,
    ProjectTimeSummaryResponse,
    RunDetailResponse,
    TaskContextProjectionResponse,
    TaskDependenciesResponse,
    TaskDetailResponse,
    TaskListResponse,
    TokenUsageListResponse,
    UpdateTaskStatusRequest,
)
from mastermind_cli.project_state.services.project_overview import (
    ProjectOverviewService,
)

router = APIRouter()


@router.get("", response_model=ProjectListResponse)
async def list_projects(
    limit: int = Query(default=100, ge=1, le=200),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ProjectListResponse:
    """Return recent projects for dashboard navigation."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        projects = service.get_project_list(limit=limit)
    return projects


@router.get("/{project_id}", response_model=ProjectDetailResponse)
async def get_project_detail(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ProjectDetailResponse:
    """Return a detailed project view for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        project = service.get_project_detail(project_id)
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/{project_id}/overview", response_model=ProjectOverviewResponse)
async def get_project_overview(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ProjectOverviewResponse:
    """Return the read-side project overview for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        overview = service.get_overview(project_id)
    if overview is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return overview


@router.get("/{project_id}/tasks/{task_id}", response_model=TaskDetailResponse)
async def get_project_task_detail(
    project_id: str,
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskDetailResponse:
    """Return the task detail view for the given project and task ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        task = service.get_task_detail(project_id, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch(
    "/{project_id}/tasks/{task_id}/status",
    response_model=TaskDetailResponse,
)
async def update_project_task_status(
    project_id: str,
    task_id: str,
    request: UpdateTaskStatusRequest,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskDetailResponse:
    """Update the status of a task within a project."""
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        task = service.update_task_status(project_id, task_id, request, user_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.get("/{project_id}/tasks", response_model=TaskListResponse)
async def list_project_tasks(
    project_id: str,
    limit: int = Query(default=200, ge=1, le=500),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskListResponse:
    """Return task list for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        tasks = service.get_task_list(project_id, limit=limit)
    if tasks is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return tasks


@router.get(
    "/{project_id}/tasks/{task_id}/dependencies",
    response_model=TaskDependenciesResponse,
)
async def get_project_task_dependencies(
    project_id: str,
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskDependenciesResponse:
    """Return dependency edges for the given project and task."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        dependencies = service.get_task_dependencies(project_id, task_id)
    if dependencies is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dependencies


@router.get("/{project_id}/runs/active", response_model=ActiveRunsResponse)
async def get_project_active_runs(
    project_id: str,
    limit: int = Query(default=50, ge=1, le=200),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ActiveRunsResponse:
    """Return currently active runs for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        runs = service.get_active_runs(project_id, limit=limit)
    if runs is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return runs


@router.get("/{project_id}/runs/{run_id}", response_model=RunDetailResponse)
async def get_project_run_detail(
    project_id: str,
    run_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> RunDetailResponse:
    """Return the run detail view for the given project and run ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        run = service.get_run_detail(project_id, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run


@router.post(
    "/{project_id}/tasks/{task_id}/checkpoints",
    response_model=LatestCheckpointResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_task_checkpoint(
    project_id: str,
    task_id: str,
    request: CreateCheckpointRequest,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> LatestCheckpointResponse:
    """Create a new checkpoint for the given project task."""
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        checkpoint = service.create_checkpoint(project_id, task_id, request, user_id)
    if checkpoint is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return checkpoint


@router.get("/{project_id}/checkpoints/latest", response_model=LatestCheckpointResponse)
async def get_latest_project_checkpoint(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> LatestCheckpointResponse:
    """Return the latest checkpoint for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        checkpoint = service.get_latest_checkpoint(project_id)
    if checkpoint is None:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    return checkpoint


@router.get("/{project_id}/costs/summary", response_model=ProjectCostSummaryResponse)
async def get_project_cost_summary(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ProjectCostSummaryResponse:
    """Return aggregated token and cost totals for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        summary = service.get_project_cost_summary(project_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return summary


@router.get("/{project_id}/time-summary", response_model=ProjectTimeSummaryResponse)
async def get_project_time_summary(
    project_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ProjectTimeSummaryResponse:
    """Return heuristic time and ETA summary for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        summary = service.get_project_time_summary(project_id)
    if summary is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return summary


@router.get("/{project_id}/token-usage", response_model=TokenUsageListResponse)
async def get_project_token_usage(
    project_id: str,
    limit: int = Query(default=100, ge=1, le=500),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TokenUsageListResponse:
    """Return recent token usage events for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        events = service.get_token_usage_list(project_id, limit=limit)
    if events is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return events


@router.get("/{project_id}/activity", response_model=ActivityFeedResponse)
async def get_project_activity_feed(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> ActivityFeedResponse:
    """Return the recent activity feed for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        feed = service.get_activity_feed(project_id, limit=limit)
    if feed is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return feed


@router.get("/{project_id}/decisions", response_model=DecisionListResponse)
async def get_project_decisions(
    project_id: str,
    limit: int = Query(default=20, ge=1, le=100),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> DecisionListResponse:
    """Return recent decisions for the given project ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        decisions = service.get_decision_list(project_id, limit=limit)
    if decisions is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return decisions


@router.post(
    "/{project_id}/decisions",
    response_model=DecisionDetailResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_project_decision(
    project_id: str,
    request: CreateDecisionRequest,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> DecisionDetailResponse:
    """Create a new decision record for the given project."""
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        decision = service.create_decision(project_id, request, user_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Project or task not found")
    return decision


@router.get(
    "/{project_id}/decisions/{decision_id}", response_model=DecisionDetailResponse
)
async def get_project_decision_detail(
    project_id: str,
    decision_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> DecisionDetailResponse:
    """Return a detailed decision record for the given project and decision ID."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        decision = service.get_decision_detail(project_id, decision_id)
    if decision is None:
        raise HTTPException(status_code=404, detail="Decision not found")
    return decision


@router.get(
    "/{project_id}/tasks/{task_id}/context-projection",
    response_model=TaskContextProjectionResponse,
)
async def get_project_task_context_projection(
    project_id: str,
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskContextProjectionResponse:
    """Return a task context projection for the given project and task."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        projection = service.get_task_context_projection(project_id, task_id)
    if projection is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return projection


@router.get(
    "/{project_id}/tasks/{task_id}/doctrine-projection",
    response_model=DoctrineProjectionResponse,
)
async def get_project_task_doctrine_projection(
    project_id: str,
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> DoctrineProjectionResponse:
    """Return a task doctrine projection for the given project and task."""
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        projection = service.get_task_doctrine_projection(project_id, task_id)
    if projection is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return projection


_SSE_HEARTBEAT_INTERVAL_SECONDS = 20
_SSE_MAX_EVENTS_PER_POLL = 20
_SSE_TOTAL_DURATION_SECONDS = 300  # Close after 5 min; client reconnects automatically.


@router.get("/{project_id}/events")
async def stream_project_state_events(
    project_id: str,
    once: bool = Query(
        default=False,
        description=(
            "If true, emit the initial realtime event batch once and close the "
            "stream immediately. Intended for tests and one-shot consumers."
        ),
    ),
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> StreamingResponse:
    """Stream project-state realtime events as Server-Sent Events (SSE).

    The endpoint yields ``ProjectStateRealtimeEvent`` objects serialised as
    SSE ``data:`` lines.  Clients should subscribe with ``EventSource`` and
    call ``router.refresh()`` (or equivalent) on receipt of any event whose
    ``event_type`` is not ``"heartbeat"``.

    The stream closes after ``_SSE_TOTAL_DURATION_SECONDS`` seconds; browsers
    reconnect automatically via the ``EventSource`` reconnect protocol.
    A 404 is returned immediately if the project does not exist.
    """
    del user_id  # Reserved for future RBAC/ownership checks in the thin slice.

    # Validate project exists before opening the stream.
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        service = ProjectOverviewService(session)
        events = service.get_realtime_events(project_id, limit=_SSE_MAX_EVENTS_PER_POLL)
    if events is None:
        raise HTTPException(status_code=404, detail="Project not found")

    async def _event_generator() -> AsyncGenerator[str, None]:
        """Yield SSE-formatted lines for each project-state event then heartbeats."""
        # Emit current recent events on connect so the UI can paint immediately.
        with session_factory() as _session:
            _service = ProjectOverviewService(_session)
            initial_events = _service.get_realtime_events(
                project_id, limit=_SSE_MAX_EVENTS_PER_POLL
            )
        if initial_events:
            for event in initial_events:
                payload = event.model_dump(mode="json")
                yield f"event: project_state_event\ndata: {json.dumps(payload)}\n\n"

        if once:
            return

        deadline = asyncio.get_event_loop().time() + _SSE_TOTAL_DURATION_SECONDS
        while asyncio.get_event_loop().time() < deadline:
            await asyncio.sleep(_SSE_HEARTBEAT_INTERVAL_SECONDS)
            yield "event: heartbeat\ndata: {}\n\n"

    return StreamingResponse(
        _event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
