"""Execution writer service — persists task execution data to DB.

Hooked into WebSocket task_completed events. Runs as a FastAPI
BackgroundTask to avoid blocking the WS response.

Strategy Vault is an audit trail (non-mission-critical). If the DB
write fails, it is logged but never re-raised — WS flow is unaffected.

Concurrency: UNIQUE constraint on task_id + INSERT OR IGNORE ensures
only the first write wins when multiple brains complete simultaneously.

Requirements: SV-01, SV-02
"""

import json
import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from mastermind_cli.state.database import DatabaseConnection

logger = logging.getLogger("execution_writer")


def _compute_milestones(
    brain_outputs: dict[str, Any],
    max_milestones: int = 7,
) -> list[dict[str, Any]]:
    """Compute evenly-spaced milestones from brain outputs.

    Milestones represent key moments during task execution:
    - Index 0: "Task started"
    - Intermediate: "{brain_name} complete"
    - Last: "Task complete"

    Args:
        brain_outputs: Dict of {brain_id: output_data} ordered by timestamp
        max_milestones: Maximum number of milestones to return (default=7)

    Returns:
        List of milestone dicts (at most max_milestones entries)
    """
    if not brain_outputs:
        return []

    # Sort outputs by timestamp
    sorted_outputs = sorted(
        brain_outputs.items(),
        key=lambda item: item[1].get("timestamp", 0)
        if isinstance(item[1], dict)
        else 0,
    )

    # Build full milestone list
    all_milestones: list[dict[str, Any]] = []

    # First: "Task started"
    if sorted_outputs:
        first_ts = sorted_outputs[0][1].get("timestamp", 0) if sorted_outputs else 0
        all_milestones.append(
            {
                "index": 0,
                "timestamp": int(first_ts),
                "label": "Task started",
                "brain_count": 0,
            }
        )

    # Middle: brain completions
    for i, (brain_id, output_data) in enumerate(sorted_outputs):
        if isinstance(output_data, dict):
            ts = output_data.get("timestamp", 0)
            brain_name = brain_id.replace("brain-", "Brain #").replace("_", " ").title()
            all_milestones.append(
                {
                    "index": i + 1,
                    "timestamp": int(ts),
                    "label": f"{brain_name} complete",
                    "brain_count": i + 1,
                }
            )

    # Last: "Task complete" (if more than 1 brain)
    if len(sorted_outputs) > 0:
        last_ts = (
            sorted_outputs[-1][1].get("timestamp", 0)
            if isinstance(sorted_outputs[-1][1], dict)
            else 0
        )
        all_milestones.append(
            {
                "index": len(all_milestones),
                "timestamp": int(last_ts) + 1,
                "label": "Task complete",
                "brain_count": len(sorted_outputs),
            }
        )

    # Evenly sample to max_milestones
    if len(all_milestones) <= max_milestones:
        # Re-index
        for i, m in enumerate(all_milestones):
            m["index"] = i
        return all_milestones

    # Sample evenly: always include first and last
    step = (len(all_milestones) - 1) / (max_milestones - 1)
    sampled = [all_milestones[round(i * step)] for i in range(max_milestones)]

    # Re-index
    for i, m in enumerate(sampled):
        m = dict(m)
        m["index"] = i
        sampled[i] = m

    return sampled


async def write_execution(
    task_id: str,
    brief: str,
    brain_outputs: dict[str, Any],
    graph_snapshot: dict[str, Any],
    db_path: str,
    duration_ms: int = 0,
    status: str = "success",
) -> str | None:
    """Persist execution data to execution_history table.

    Called as a BackgroundTask when WS task_completed event fires.
    Never raises — logs errors and returns None on failure.

    Concurrency safety: Uses INSERT OR IGNORE (SQLite equivalent of
    INSERT ... ON CONFLICT DO NOTHING) to handle simultaneous writes
    from multiple brain completions.

    Args:
        task_id: Task UUID (FK to executions table)
        brief: First 100 chars of brief text
        brain_outputs: Dict {brain_id: output_dict} from orchestrator
        graph_snapshot: Final DAG state dict for replay
        db_path: SQLite database path
        duration_ms: Total execution duration in milliseconds
        status: "success", "error", or "running"

    Returns:
        Created execution UUID, or None if write failed or was skipped
        (i.e., another writer already created the record for this task_id)
    """
    exec_id = str(uuid.uuid4())
    brain_count = len(brain_outputs) if brain_outputs else 1
    milestones = _compute_milestones(brain_outputs)

    try:
        async with DatabaseConnection(db_path) as db:
            await db.create_execution_history_schema()

            # INSERT OR IGNORE: first writer wins, subsequent silently skip
            cursor = await db.conn.execute(
                """INSERT OR IGNORE INTO execution_history
                   (id, task_id, brief, status, duration_ms, brain_count,
                    created_at, milestones_json, brain_outputs_json, graph_snapshot_json)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                [
                    exec_id,
                    task_id,
                    brief[:200],
                    status if status in {"success", "error", "running"} else "success",
                    duration_ms,
                    brain_count,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(milestones),
                    json.dumps(brain_outputs),
                    json.dumps(graph_snapshot),
                ],
            )
            await db.conn.commit()

            if cursor.rowcount == 0:
                # Silently skipped (another writer won the race)
                logger.info(
                    "execution_write_skipped",
                    extra={"task_id": task_id, "reason": "already_written"},
                )
                return None

            return exec_id

    except Exception as e:
        # Structured error log — never re-raise (WS flow must not be blocked)
        logger.error(
            "execution_write_failed",
            extra={
                "task_id": task_id,
                "error": str(e),
                "brain_count": brain_count,
            },
        )
        return None
