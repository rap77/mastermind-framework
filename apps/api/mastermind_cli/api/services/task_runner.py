"""Background task runner for brain orchestration — Fase 3 + Fase 4.

Executes StatelessCoordinator.execute_flow() as a FastAPI BackgroundTask,
writes experience records, updates execution status in SQLite, and integrates
brain-to-brain routing for sequential delegation.

Fase 4 integration:
- After flow completes, route_to_brain() checks if additional brains should run
- emit_brain_routing_event() sends WS events for frontend awareness
- Routed brain failures are isolated — parent task stays completed

Brain #5/#6 guidance:
- FastAPI BackgroundTasks (not asyncio.create_task) — avoids orphan tasks
- CancelledError caught explicitly (BaseException, not Exception) — uvicorn safe
- BRAIN_ID_MAP explicit lookup table (not f-string) — no silent mismatches
- DB path from MM_DB_PATH env var — consistent with brain_memory.py CLI
"""

import asyncio
import time
import uuid

from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.orchestrator import brain_router as _brain_router
from mastermind_cli.orchestrator.flow_detector import FlowDetector
from mastermind_cli.orchestrator.stateless_coordinator import (
    create_stateless_coordinator,
)
from mastermind_cli.state.database import DatabaseConnection
from mastermind_cli.types.interfaces import Brief


class _PassthroughMCPClient:
    """Minimal MCPClient adapter for background task context.

    StatelessCoordinator requires an MCPClient at construction time, but in a
    FastAPI background task the brain agents run as Claude Code subagents — they
    make their own NotebookLM calls via Bash. This stub satisfies the protocol
    without invoking MCP tools from Python.
    """

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        return ""  # Brain agents make their own MCP calls via Bash tool


# Explicit mapping — FlowDetector.get_flow_sequence() returns list[int]
# Brain #5: never f-string interpolate, prevents silent brain ID mismatches
BRAIN_ID_MAP: dict[int, str] = {
    1: "brain-01-product",
    2: "brain-02-ux",
    3: "brain-03-ui",
    4: "brain-04-frontend",
    5: "brain-05-backend",
    6: "brain-06-qa",
    7: "brain-07-growth",
}


async def run_brain_task(
    task_id: str,
    brief: str,
    flow: str | None,
    db_path: str,
) -> None:
    """Execute brain orchestration and persist results.

    Designed to run as a FastAPI BackgroundTask — do NOT call with
    asyncio.create_task() from a route handler (creates orphan tasks).

    Status transitions:
        pending → running → completed (success)
        pending → running → failed (exception or CancelledError)

    Args:
        task_id: Execution record ID (must exist in executions table)
        brief: Raw user brief text
        flow: Flow type name (e.g. 'validation_only') or None for auto-detect
        db_path: SQLite database path (use MM_DB_PATH env var)
    """
    async with DatabaseConnection(db_path) as db:
        await db.conn.execute(
            "UPDATE executions SET status = ? WHERE id = ?",
            ["running", task_id],
        )
        await db.conn.commit()

    detector = FlowDetector()
    flow_type = flow if flow else detector.detect(brief)
    brain_ints = detector.get_flow_sequence(flow_type)
    brain_ids = [BRAIN_ID_MAP[n] for n in brain_ints if n in BRAIN_ID_MAP]

    coordinator = create_stateless_coordinator(_PassthroughMCPClient())
    start_ms = int(time.time() * 1000)

    try:
        brief_obj = Brief(problem_statement=brief, context="", target_audience=None)
        results = await coordinator.execute_flow(brief_obj, brain_ids)
        elapsed_ms = int(time.time() * 1000) - start_ms

        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            logger = ExperienceLogger(db)
            for brain_id, output in results.items():
                await logger.log_execution(
                    brain_id=brain_id,
                    input_json={"brief": brief, "flow": flow_type},
                    output_json=output.model_dump()
                    if hasattr(output, "model_dump")
                    else {},
                    duration_ms=elapsed_ms,
                    status="success",
                    trace_context_id=task_id,
                )
            await db.conn.execute(
                "UPDATE executions SET status = ? WHERE id = ?",
                ["completed", task_id],
            )
            await db.conn.commit()

        # --- Fase 4: Brain-to-brain routing (sequential delegation) ---
        # After the main flow completes, check if any brain's brief should
        # be routed to an additional brain that wasn't in the original flow.
        for brain_id in list(results.keys()):
            target_brain = _brain_router.route_to_brain(brief_obj, brain_id)
            if target_brain is None or target_brain in results:
                continue  # No match or brain already ran in this flow

            sub_task_id = str(uuid.uuid4())

            # Emit WS event for frontend awareness (Opción A: parent task_id)
            await _brain_router.emit_brain_routing_event(
                task_id=task_id,
                from_brain=brain_id,
                to_brain=target_brain,
                sub_task_id=sub_task_id,
            )

            # Execute the routed brain — failures are isolated
            try:
                routed_results = await coordinator.execute_flow(
                    brief_obj, [target_brain]
                )
                routed_elapsed = int(time.time() * 1000) - start_ms

                # Log experience for routed brain
                async with DatabaseConnection(db_path) as db:
                    routed_logger = ExperienceLogger(db)
                    for rid, rout in routed_results.items():
                        await routed_logger.log_execution(
                            brain_id=rid,
                            input_json={
                                "brief": brief,
                                "flow": flow_type,
                                "routed_from": brain_id,
                            },
                            output_json=rout.model_dump()
                            if hasattr(rout, "model_dump")
                            else {},
                            duration_ms=routed_elapsed,
                            status="success",
                            trace_context_id=task_id,
                        )
            except Exception:
                pass  # Routed brain failure is isolated — parent stays completed

    except (Exception, asyncio.CancelledError):
        # CancelledError is BaseException — must be listed explicitly
        # Brain #6: status must be written even on shutdown signal
        elapsed_ms = int(time.time() * 1000) - start_ms
        try:
            async with DatabaseConnection(db_path) as db:
                await db.conn.execute(
                    "UPDATE executions SET status = ? WHERE id = ?",
                    ["failed", task_id],
                )
                await db.conn.commit()
        except Exception:
            pass  # DB write on shutdown — best-effort only
