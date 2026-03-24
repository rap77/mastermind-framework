"""Task management REST endpoints.

This module provides CRUD operations for brain orchestration tasks.

Requirements: UI-06, UI-08, ARCH-03, PERF-02
Security: OWASP A03 (XSS) - Server-side brief sanitization
"""

import json
import uuid
from datetime import datetime
from html import escape
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.api.services.graph_builder import build_niche_clustered_graph
from mastermind_cli.state.database import DatabaseConnection

# Router
router = APIRouter()


# ===== Request/Response Models =====


class CreateTaskRequest(BaseModel):
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


# ===== Endpoints =====


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: CreateTaskRequest,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
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

        # Note: Actual orchestration happens in background
        # For now, just create the record
        # TODO: Integrate with Coordinator.orchestrate() in Task 2

    return TaskResponse(
        task_id=task_id,
        status="pending",
        created_at=datetime.utcnow(),
    )


@router.get("")
async def list_tasks(
    limit: int = 50,
    offset: int = 0,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> TaskListResponse:
    """List user's tasks with pagination.

    Session isolation: WHERE user_id = current_user.id (UI-08 requirement).
    """
    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            """SELECT id, brief, created_at, status FROM executions
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            [user_id, limit, offset],
        )
        rows = await cursor.fetchall()

        count_cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM executions WHERE user_id = ?", [user_id]
        )
        count_row = await count_cursor.fetchone()
        total = count_row[0] if count_row else 0

    return TaskListResponse(
        tasks=[
            {"id": row[0], "brief": row[1], "created_at": row[2], "status": row[3]}
            for row in rows
        ],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> dict[str, object]:
    """Get task state.

    Returns 404 if not found or doesn't belong to user.
    """
    async with DatabaseConnection(db_path) as db:
        cursor = await db.conn.execute(
            "SELECT * FROM executions WHERE id = ? AND user_id = ?",
            [task_id, user_id],
        )
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

    return {
        "id": row[0],
        "flow_config": row[1],
        "brief": row[2],
        "created_at": row[3],
        "status": row[4],
    }


@router.get("/{task_id}/state")
async def get_task_state(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> dict[str, object]:
    """Get current task state (optimized for <100ms queries - PERF-02)."""
    # Same as get_task for now (will add brain_states in Task 2)
    return await get_task(task_id, user_id, db_path)


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> dict[str, str]:
    """Cancel running task.

    Requires ownership. Logged to audit (automatic via middleware).
    """
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
) -> TaskGraphResponse:
    """Get task execution graph for visualization.

    Returns node/edge structure for React Flow rendering.
    Phase 08 enhancement: also returns `subgraph` with niche-clustered
    DAG when `brain_execution_log` data is available in flow_config.

    Nodes are ordered by execution level (topological sort).

    Performance: Completes in <100ms (PERF-02 requirement).
    Backward compat: nodes/edges/max_level/max_parallelism unchanged.
    """
    async with DatabaseConnection(db_path) as db:
        # Fetch execution record (also get brief for subgraph master node)
        cursor = await db.conn.execute(
            "SELECT flow_config, status, brief FROM executions WHERE id = ? AND user_id = ?",
            [task_id, user_id],
        )
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        flow_config_json, task_status, brief = row

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
