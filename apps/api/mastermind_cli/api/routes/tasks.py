"""Task management REST endpoints.

This module provides CRUD operations for brain orchestration tasks.

Requirements: UI-06, UI-08, ARCH-03, PERF-02
Security: OWASP A03 (XSS) - Server-side brief sanitization
"""

import json
import time
import uuid
from datetime import datetime, timezone
from html import escape
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, func, select

from mastermind_cli.api.dependencies import get_db_path, get_project_state_db_url
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.api.services.graph_builder import build_niche_clustered_graph
from mastermind_cli.api.services.task_runner import run_brain_task
from mastermind_cli.project_state.database.session import (
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.models.project import Project
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from mastermind_cli.orchestration.distillation_service import (
    KnowledgeDistillationService,
    DistillationTask,
)
from mastermind_cli.orchestrator.flow_detector import FlowDetector
from mastermind_cli.state.database import DatabaseConnection
from mastermind_cli.types.pydantic import StrictRequestModel

# Router
router = APIRouter()


def _user_task_project_id(user_id: str) -> str:
    """Return the transitional project_state scope for legacy user tasks."""
    return f"user-tasks:{user_id}"


def _ensure_user_task_project(
    user_id: str,
    database_url: str,
) -> str:
    """Ensure the transitional project_state workspace exists for the user."""
    initialize_database(database_url)
    project_id = _user_task_project_id(user_id)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        project = session.get(Project, project_id)
        if project is None:
            session.add(
                Project(
                    project_id=project_id,
                    name="User task workspace",
                    status="active",
                    adapter_id="legacy-tasks",
                    metadata_json={"user_id": user_id},
                    created_at=now,
                    updated_at=now,
                )
            )
            session.commit()
    return project_id


def _persist_task_to_project_state(
    *,
    database_url: str,
    task_id: str,
    user_id: str,
    brief: str,
    status: str,
    flow_config: str,
) -> None:
    """Persist the transitional task/task_run records to project_state."""
    project_id = _ensure_user_task_project(user_id, database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        session.add(
            Task(
                task_id=task_id,
                project_id=project_id,
                title=brief[:500],
                status=status,
                priority="normal",
                owner_type="user",
                owner_id=user_id,
                metadata_json={
                    "brief": brief,
                    "flow_config": flow_config,
                    "user_id": user_id,
                },
                constraints={},
                completion_criteria={},
                created_at=now,
                updated_at=now,
            )
        )
        session.add(
            TaskRun(
                run_id=task_id,
                project_id=project_id,
                task_id=task_id,
                actor_type="user",
                actor_id=user_id,
                status=status,
                started_at=now,
                ended_at=None,
                metadata_json={"legacy_execution_id": task_id},
            )
        )
        session.commit()


def _read_task_brief(task: Task) -> str:
    """Return the legacy brief field from a project_state task record."""
    brief = task.metadata_json.get("brief")
    if isinstance(brief, str) and brief:
        return brief
    return task.title


def _read_task_flow_config(task: Task) -> str:
    """Return the legacy flow_config field from a project_state task record."""
    flow_config = task.metadata_json.get("flow_config")
    if isinstance(flow_config, str):
        return flow_config
    return "{}"


def _load_task_graph_source(
    *,
    database_url: str,
    user_id: str,
    task_id: str,
    db_path: str,
) -> tuple[str, str, str]:
    """Return flow_config, status, and brief for graph rendering.

    Prefers project_state as the transitional source of truth, but falls back
    to the legacy SQLite executions row for pre-migration records.
    """
    task = _get_project_state_task(
        database_url=database_url,
        user_id=user_id,
        task_id=task_id,
    )
    if task is not None:
        return (
            _read_task_flow_config(task),
            task.status,
            _read_task_brief(task),
        )

    import sqlite3

    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.execute(
            "SELECT flow_config, status, brief FROM executions WHERE id = ? AND user_id = ?",
            [task_id, user_id],
        )
        row = cursor.fetchone()
    finally:
        conn.close()

    if row is None:
        raise HTTPException(status_code=404, detail="Task not found")

    flow_config_value = row[0] if isinstance(row[0], str) else "{}"
    brief_value = row[2] if isinstance(row[2], str) else ""
    return (flow_config_value, row[1], brief_value)


def _get_project_state_task(
    *,
    database_url: str,
    user_id: str,
    task_id: str,
) -> Task | None:
    """Return a task from the transitional project_state namespace."""
    project_id = _ensure_user_task_project(user_id, database_url)
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        return session.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.task_id == task_id,
            )
        ).scalar_one_or_none()


def _cancel_project_state_task(
    *,
    database_url: str,
    user_id: str,
    task_id: str,
) -> bool:
    """Cancel a transitional project_state task and its active run."""
    project_id = _ensure_user_task_project(user_id, database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        task = session.execute(
            select(Task).where(
                Task.project_id == project_id,
                Task.task_id == task_id,
            )
        ).scalar_one_or_none()
        if task is None:
            return False

        task.status = "cancelled"
        task.updated_at = now

        run = session.execute(
            select(TaskRun).where(
                TaskRun.project_id == project_id,
                TaskRun.run_id == task_id,
            )
        ).scalar_one_or_none()
        if run is not None:
            run.status = "cancelled"
            run.ended_at = now

        session.commit()
    return True


# ===== Request/Response Models =====


class CreateTaskRequest(StrictRequestModel):
    """Request to create new orchestration task."""

    brief: str = Field(..., min_length=1, max_length=10000)
    flow: Optional[str] = None
    max_iterations: int = Field(default=3, ge=1, le=10)
    use_mcp: bool = False


class TaskResponse(BaseModel):
    """Task creation response."""

    task_id: str
    status: str
    created_at: datetime


class TaskListResponse(BaseModel):
    """Task list response."""

    tasks: list[dict[str, object]]
    total: int
    limit: int
    offset: int


class AutoTaskRequest(StrictRequestModel):
    """Request to create task with auto-detected flow."""

    brief: str = Field(..., min_length=1, max_length=10000)


class AutoTaskResponse(BaseModel):
    """Auto-task creation response with detected flow."""

    id: str
    status: str
    flow: str


# ===== Endpoints =====


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: CreateTaskRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskResponse:
    """Create new orchestration task.

    Validates brief length, sanitizes input (XSS prevention),
    calls Coordinator.orchestrate() with parallel=True,
    returns task_id and status.

    ARCH-03: Per-request orchestrator instances (no shared global state).
    Security: Server-side brief sanitization (defense in depth)
    """
    task_id = str(uuid.uuid4())

    # XSS Prevention: Server-side sanitization (defense in depth)
    # escape() converts HTML entities to prevent stored XSS
    brief_sanitized = escape(request.brief)

    async with DatabaseConnection(db_path) as db:
        # Create execution record
        await db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status, user_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                task_id,
                request.flow or "{}",
                brief_sanitized,
                datetime.utcnow(),
                "pending",
                user_id,
            ],
        )
        await db.conn.commit()

    _persist_task_to_project_state(
        database_url=database_url,
        task_id=task_id,
        user_id=user_id,
        brief=brief_sanitized,
        status="pending",
        flow_config=request.flow or "{}",
    )

    background_tasks.add_task(
        run_brain_task,
        task_id=task_id,
        brief=brief_sanitized,
        flow=request.flow if isinstance(request.flow, str) else None,
        db_path=db_path,
    )

    return TaskResponse(
        task_id=task_id,
        status="pending",
        created_at=datetime.utcnow(),
    )


@router.post("/auto", response_model=AutoTaskResponse, status_code=202)
async def create_auto_task(
    request: AutoTaskRequest,
    background_tasks: BackgroundTasks,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> AutoTaskResponse:
    """Create task with auto-detected flow.

    Accepts only a brief (no explicit flow), auto-detects the appropriate
    flow using FlowDetector, creates an execution record, and dispatches
    the brain orchestration via BackgroundTasks.

    Returns 202 Accepted immediately — execution happens asynchronously.
    """
    task_id = str(uuid.uuid4())

    # XSS Prevention: Server-side sanitization
    brief_sanitized = escape(request.brief)

    # Auto-detect flow from brief content
    detector = FlowDetector()
    detected_flow = detector.detect(brief_sanitized)

    async with DatabaseConnection(db_path) as db:
        await db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status, user_id)
               VALUES (?, ?, ?, ?, ?, ?)""",
            [
                task_id,
                detected_flow,
                brief_sanitized,
                datetime.utcnow(),
                "pending",
                user_id,
            ],
        )
        await db.conn.commit()

    _persist_task_to_project_state(
        database_url=database_url,
        task_id=task_id,
        user_id=user_id,
        brief=brief_sanitized,
        status="pending",
        flow_config=detected_flow,
    )

    background_tasks.add_task(
        run_brain_task,
        task_id=task_id,
        brief=brief_sanitized,
        flow=detected_flow,
        db_path=db_path,
    )

    # NEW: Hook distillation after orchestration completes
    execution_start_ms = int(time.time() * 1000)

    distillation_service = KnowledgeDistillationService(db_path=db_path)
    distillation_task = DistillationTask(
        session_id=task_id,
        brain_ids=[detected_flow] if isinstance(detected_flow, str) else [],
        brief_summary=brief_sanitized[:200],  # Truncate for storage
        execution_start_ms=execution_start_ms,
        execution_end_ms=execution_start_ms,  # Placeholder; will update in AgentRunner
        invocation_method="mm:execute-phase",  # Detect from request context if needed
        user_id=user_id,
    )

    # Fire-and-forget: Non-blocking, executes AFTER user receives 202 response
    background_tasks.add_task(
        distillation_service.trigger_evaluation_and_distillation,
        distillation_task,
    )

    return AutoTaskResponse(
        id=task_id,
        status="pending",
        flow=detected_flow,
    )


@router.get("")
async def list_tasks(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskListResponse:
    """List user's tasks with pagination.

    Session isolation: WHERE user_id = current_user.id (UI-08 requirement).
    """
    project_id = _ensure_user_task_project(user_id, database_url)
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        rows = list(
            session.execute(
                select(Task)
                .where(Task.project_id == project_id)
                .order_by(desc(Task.created_at))
                .limit(limit)
                .offset(offset)
            ).scalars()
        )
        total = int(
            session.execute(
                select(func.count())
                .select_from(Task)
                .where(Task.project_id == project_id)
            ).scalar_one()
        )

    return TaskListResponse(
        tasks=[
            {
                "id": task.task_id,
                "brief": _read_task_brief(task),
                "created_at": task.created_at,
                "status": task.status,
            }
            for task in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> dict[str, object]:
    """Get task state.

    Returns 404 if not found or doesn't belong to user.
    """
    task = _get_project_state_task(
        database_url=database_url,
        user_id=user_id,
        task_id=task_id,
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": task.task_id,
        "flow_config": _read_task_flow_config(task),
        "brief": _read_task_brief(task),
        "created_at": task.created_at,
        "status": task.status,
    }


@router.get("/{task_id}/state")
async def get_task_state(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    database_url: str = Depends(get_project_state_db_url),
) -> dict[str, object]:
    """Get current task state (optimized for <100ms queries - PERF-02)."""
    # Same as get_task for now (will add brain_states in Task 2)
    return await get_task(task_id, user_id, database_url)


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> dict[str, str]:
    """Cancel running task.

    Requires ownership. Logged to audit (automatic via middleware).
    """
    task_found = _cancel_project_state_task(
        database_url=database_url,
        user_id=user_id,
        task_id=task_id,
    )
    if not task_found:
        raise HTTPException(status_code=404, detail="Task not found")

    async with DatabaseConnection(db_path) as db:
        await db.conn.execute(
            "UPDATE executions SET status = 'cancelled' WHERE id = ? AND user_id = ?",
            [task_id, user_id],
        )
        await db.conn.commit()

    return {"message": "Task cancelled", "task_id": task_id}


# ===== Graph Models =====


class GraphNode(BaseModel):
    """Node in the execution graph."""

    id: str = Field(..., description="Brain ID")
    label: str = Field(..., description="Display label")
    level: int = Field(..., ge=0, description="Execution level (wave number)")
    state: str = Field(
        ...,
        description="Current state (pending, running, completed, failed, cancelled)",
    )


class GraphEdge(BaseModel):
    """Edge in the execution graph — React Flow compatible field names."""

    source: str = Field(..., description="Source brain ID")
    target: str = Field(..., description="Target brain ID")
    data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Edge metadata (e.g. execution_mode for Phase 08 sub-graphs)",
    )


class TaskGraphResponse(BaseModel):
    """Task graph response with nodes and edges.

    Phase 08 enhancement: optional `subgraph` field with niche-clustered
    DAG structure (parentId, execution_mode). When present, frontend can
    render the enhanced React Flow graph with niche container nodes.
    Backward compat: nodes/edges/max_level/max_parallelism/layout_positions
    remain unchanged for existing Phase 07 NexusCanvas.
    """

    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    max_level: int = Field(..., ge=0, description="Maximum execution level")
    max_parallelism: int = Field(..., ge=0, description="Maximum concurrent brains")
    layout_positions: dict[str, dict[str, float]] | None = Field(
        default=None,
        description="Optional server-computed node positions. None = client computes dagre layout.",
    )
    subgraph: Optional[dict[str, Any]] = Field(
        default=None,
        description="Phase 08: niche-clustered DAG with parentId + execution_mode."
        " None when no brains have executed.",
    )


# ===== Graph Endpoint =====


@router.get("/{task_id}/graph", response_model=TaskGraphResponse)
async def get_task_graph(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
    database_url: str = Depends(get_project_state_db_url),
) -> TaskGraphResponse:
    """Get task execution graph for visualization.

    Returns node/edge structure for React Flow rendering.
    Phase 08 enhancement: also returns `subgraph` with niche-clustered
    DAG when `brain_execution_log` data is available in flow_config.

    Nodes are ordered by execution level (topological sort).

    Performance: Completes in <100ms (PERF-02 requirement).
    Backward compat: nodes/edges/max_level/max_parallelism unchanged.
    """
    flow_config_json, task_status, brief = _load_task_graph_source(
        database_url=database_url,
        user_id=user_id,
        task_id=task_id,
        db_path=db_path,
    )

    # Parse flow_config
    try:
        if flow_config_json:
            flow_config = (
                json.loads(flow_config_json)
                if isinstance(flow_config_json, str)
                else flow_config_json
            )
        else:
            flow_config = {}
    except json.JSONDecodeError:
        flow_config = {}

    # ===== Phase 08: Build niche-clustered subgraph =====
    # brain_execution_log is populated by execution_writer when task completes
    brain_execution_log: list[dict[str, Any]] = flow_config.get(
        "brain_execution_log", []
    )
    subgraph: dict[str, Any] | None = None
    if brain_execution_log:
        subgraph = build_niche_clustered_graph(
            task_id=task_id,
            brief=brief or "",
            brains=brain_execution_log,
        )

    # Handle empty flow_config (Phase 07 backward compat)
    if not flow_config or not flow_config.get("nodes"):
        return TaskGraphResponse(
            nodes=[],
            edges=[],
            max_level=0,
            max_parallelism=0,
            layout_positions=None,
            subgraph=subgraph,
        )

    # Build nodes from flow_config
    nodes_raw = flow_config.get("nodes", {})
    edges_raw = flow_config.get("edges", {})

    # Calculate level (dependency depth) for each node
    node_levels: Dict[str, int] = {}
    for node_id, dependencies in nodes_raw.items():
        if not dependencies:
            node_levels[node_id] = 0
        else:
            max_dep_level = max(node_levels.get(dep, 0) for dep in dependencies)
            node_levels[node_id] = max_dep_level + 1

    # Build node list with states (default to task_status for now)
    nodes = [
        GraphNode(
            id=node_id,
            label=node_id.replace("brain-", "Brain #").replace("_", " ").title(),
            level=level,
            state=task_status,  # All nodes share task status until brain_states are implemented
        )
        for node_id, level in sorted(node_levels.items(), key=lambda x: x[1])
    ]

    # Build edge list — React Flow compatible: source/target field names
    edges = []
    for target_node, dependencies in edges_raw.items():
        for source_node in dependencies:
            edges.append(GraphEdge(source=source_node, target=target_node))

    # Calculate metrics
    max_level = max(node_levels.values(), default=0)
    max_parallelism = (
        max(
            sum(1 for level in node_levels.values() if level == lvl)
            for lvl in range(max_level + 1)
        )
        if nodes
        else 0
    )

    return TaskGraphResponse(
        nodes=nodes,
        edges=edges,
        max_level=max_level,
        max_parallelism=max_parallelism,
        layout_positions=None,
        subgraph=subgraph,
    )
