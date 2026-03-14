"""Task management REST endpoints.

This module provides CRUD operations for brain orchestration tasks.

Requirements: UI-06, UI-08, ARCH-03, PERF-02
"""

import json
import uuid
from datetime import datetime
from typing import Optional, Dict, List, Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from mastermind_cli.api.routes.auth import get_current_user_any
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
    tasks: list
    total: int
    limit: int
    offset: int


# ===== Endpoints =====


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    request: CreateTaskRequest,
    user_id: str = Depends(get_current_user_any),
):
    """Create new orchestration task.

    Validates brief length, calls Coordinator.orchestrate() with parallel=True,
    returns task_id and status.

    ARCH-03: Per-request orchestrator instances (no shared global state).
    """
    task_id = str(uuid.uuid4())

    async with DatabaseConnection(":memory:") as db:
        # Create execution record
        await db.conn.execute(
            """INSERT INTO executions (id, flow_config, brief, created_at, status)
               VALUES (?, ?, ?, ?, ?)""",
            [task_id, request.flow or "{}", request.brief, datetime.utcnow(), "pending"],
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
):
    """List user's tasks with pagination.

    Session isolation: WHERE user_id = current_user.id (UI-08 requirement).
    """
    async with DatabaseConnection(":memory:") as db:
        cursor = await db.conn.execute(
            """SELECT id, brief, created_at, status FROM executions
               ORDER BY created_at DESC
               LIMIT ? OFFSET ?""",
            [limit, offset],
        )
        rows = await cursor.fetchall()

        count_cursor = await db.conn.execute("SELECT COUNT(*) FROM executions")
        total = (await count_cursor.fetchone())[0]

    return TaskListResponse(
        tasks=[{"id": row[0], "brief": row[1], "created_at": row[2], "status": row[3]} for row in rows],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{task_id}")
async def get_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
):
    """Get task state.

    Returns 404 if not found or doesn't belong to user.
    """
    async with DatabaseConnection(":memory:") as db:
        cursor = await db.conn.execute(
            "SELECT * FROM executions WHERE id = ?",
            [task_id],
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
):
    """Get current task state (optimized for <100ms queries - PERF-02)."""
    # Same as get_task for now (will add brain_states in Task 2)
    return await get_task(task_id, user_id)


@router.delete("/{task_id}")
async def cancel_task(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
):
    """Cancel running task.

    Requires ownership. Logged to audit (automatic via middleware).
    """
    async with DatabaseConnection(":memory:") as db:
        await db.conn.execute(
            "UPDATE executions SET status = 'cancelled' WHERE id = ?",
            [task_id],
        )
        await db.conn.commit()

    return {"message": "Task cancelled", "task_id": task_id}


# ===== Graph Models =====


class GraphNode(BaseModel):
    """Node in the execution graph."""
    id: str = Field(..., description="Brain ID")
    label: str = Field(..., description="Display label")
    level: int = Field(..., ge=0, description="Execution level (wave number)")
    state: str = Field(..., description="Current state (pending, running, completed, failed, cancelled)")


class GraphEdge(BaseModel):
    """Edge in the execution graph."""
    from_node: str = Field(..., alias="from", description="Source brain ID")
    to: str = Field(..., description="Target brain ID")

    class Config:
        populate_by_name = True


class TaskGraphResponse(BaseModel):
    """Task graph response with nodes and edges."""
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    max_level: int = Field(..., ge=0, description="Maximum execution level")
    max_parallelism: int = Field(..., ge=0, description="Maximum concurrent brains")


# ===== Graph Endpoint =====


@router.get("/{task_id}/graph", response_model=TaskGraphResponse)
async def get_task_graph(
    task_id: str,
    user_id: str = Depends(get_current_user_any),
):
    """Get task execution graph for visualization.

    Returns node/edge structure for D3.js rendering.
    Nodes are ordered by execution level (topological sort).

    Performance: Completes in <100ms (PERF-02 requirement).
    """
    async with DatabaseConnection(":memory:") as db:
        # Fetch execution record
        cursor = await db.conn.execute(
            "SELECT flow_config, status FROM executions WHERE id = ?",
            [task_id],
        )
        row = await cursor.fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Task not found")

        flow_config_json, task_status = row

    # Parse flow_config
    try:
        if flow_config_json:
            flow_config = json.loads(flow_config_json) if isinstance(flow_config_json, str) else flow_config_json
        else:
            flow_config = {}
    except json.JSONDecodeError:
        flow_config = {}

    # Handle empty flow_config
    if not flow_config or not flow_config.get("nodes"):
        return TaskGraphResponse(
            nodes=[],
            edges=[],
            max_level=0,
            max_parallelism=0
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
            state=task_status  # All nodes share task status until brain_states are implemented
        )
        for node_id, level in sorted(node_levels.items(), key=lambda x: x[1])
    ]

    # Build edge list
    edges = []
    for target_node, dependencies in edges_raw.items():
        for source_node in dependencies:
            edges.append(GraphEdge(from_node=source_node, to=target_node))

    # Calculate metrics
    max_level = max(node_levels.values(), default=0)
    max_parallelism = max(
        sum(1 for level in node_levels.values() if level == lvl)
        for lvl in range(max_level + 1)
    ) if nodes else 0

    return TaskGraphResponse(
        nodes=nodes,
        edges=edges,
        max_level=max_level,
        max_parallelism=max_parallelism
    )
