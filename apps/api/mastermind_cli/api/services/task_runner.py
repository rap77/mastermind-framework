"""Background task runner for brain orchestration — Fase 3 + Fase 4 + C3.

Executes StatelessCoordinator.execute_flow() as a FastAPI BackgroundTask,
writes experience records, updates execution status in SQLite, and integrates
brain-to-brain routing for sequential delegation.

Fase 4 integration:
- After flow completes, route_to_brain() checks if additional brains should run
- emit_brain_routing_event() sends WS events for frontend awareness
- Routed brain failures are isolated — parent task stays completed

C3 integration (Brain #7 post-session hook):
- After each brain completes, Brain7Evaluator scores the output
- quality_score + insights written to ExperienceLogger
- high_value flag set if duration > 5min OR score >= 0.75
- POST to Rust /internal/brain-event with type=session_evaluated
- model field included in custom_metadata for provider tracking

Phase 21 RAG integration:
- run_brain_task() opens an asyncpg connection before execute_flow()
- The connection is passed as conn= so Brain #1 calls RAGContextBuilder.build()
- rag_enabled = (rag_context != "") is tracked per-brain in custom_metadata
- LangSmith span metadata includes rag_enabled for observability (21.20)
- asyncpg failure → conn=None → RAG skipped gracefully, rag_enabled=False

Brain #5/#6 guidance:
- FastAPI BackgroundTasks (not asyncio.create_task) — avoids orphan tasks
- CancelledError caught explicitly (BaseException, not Exception) — uvicorn safe
- BRAIN_ID_MAP explicit lookup table (not f-string) — no silent mismatches
- DB path from MM_DB_PATH env var — consistent with brain_memory.py CLI
"""

import asyncio
import inspect
import hashlib
import json
import logging
import os
import sqlite3
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from typing import Any, Mapping, Protocol

import asyncpg
import httpx
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.memory_layer.exceptions import MemorySnapshotError
from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.memory_layer.runtime import build_memory_store_from_env
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.orchestrator import brain_router as _brain_router
from mastermind_cli.orchestrator.brain7_evaluator import evaluate_session
from mastermind_cli.orchestrator.flow_detector import FlowDetector
from mastermind_cli.orchestrator.governance import GovernanceInterceptor
from mastermind_cli.orchestrator.runtime_contracts.memory_runtime_adapter import (
    MemoryRuntimeAdapter,
)
from mastermind_cli.project_state.database.session import (
    get_session_factory,
    initialize_database,
)
from mastermind_cli.project_state.repositories.artifacts import ArtifactRepository
from mastermind_cli.project_state.models.task import Task
from mastermind_cli.project_state.models.task_run import TaskRun
from mastermind_cli.orchestrator.stateless_coordinator import (
    create_stateless_coordinator,
)
from mastermind_cli.state.database import DatabaseConnection
from mastermind_cli.types.interfaces import Brief

log = logging.getLogger(__name__)


class TaskShutdownWriteError(RuntimeError):
    """Raised when best-effort shutdown bookkeeping cannot be completed."""


_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "",
)

# Rust control plane URL for internal brain-event endpoint
_RUST_CONTROL_PLANE_URL = os.environ.get(
    "RUST_CONTROL_PLANE_URL", "http://localhost:3001"
)


class _ExecutionLogger(Protocol):
    """Minimal protocol for experience logging during task execution."""

    async def log_execution(
        self,
        *,
        brain_id: str,
        input_json: dict[str, object],
        output_json: dict[str, object],
        duration_ms: int,
        status: str,
        trace_context_id: str | None = None,
        quality_score: float | None = None,
        custom_metadata: dict[str, object] | None = None,
    ) -> object:
        """Persist one execution event for a brain run."""
        ...


ExperienceLoggerFactory = Callable[[DatabaseConnection], _ExecutionLogger]


def _project_state_db_url_from_path(db_path: str) -> str:
    """Resolve the transitional project_state database URL from the legacy DB path."""
    if db_path == ":memory:":
        return "sqlite:///:memory:"
    return f"sqlite:///{db_path}.project_state"


def _build_experience_logger(
    db: DatabaseConnection,
    factory: ExperienceLoggerFactory | None,
) -> _ExecutionLogger:
    """Build an execution logger, allowing tests to inject a seam."""
    if factory is not None:
        return factory(db)
    return ExperienceLogger(db)


def _load_task_project_id(db_path: str, task_id: str) -> str | None:
    """Load the project ID for a task from project_state."""
    database_url = _project_state_db_url_from_path(db_path)
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    with session_factory() as session:
        task = session.get(Task, task_id)
        return task.project_id if task is not None else None


def _update_project_state_status(
    db_path: str,
    task_id: str,
    status: str,
    *,
    mark_run_finished: bool,
) -> None:
    """Mirror task/run status to project_state during the migration window."""
    database_url = _project_state_db_url_from_path(db_path)
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    now = datetime.now(timezone.utc)
    with session_factory() as session:
        _apply_project_state_status(
            session=session,
            task_id=task_id,
            status=status,
            timestamp=now,
            mark_run_finished=mark_run_finished,
        )
        session.commit()


def _apply_project_state_status(
    *,
    session: Session,
    task_id: str,
    status: str,
    timestamp: datetime,
    mark_run_finished: bool,
) -> None:
    """Apply a status update to transitional project_state task/run records."""
    task = session.get(Task, task_id)
    if task is not None:
        task.status = status
        task.updated_at = timestamp

    run = session.get(TaskRun, task_id)
    if run is not None:
        run.status = status
        if mark_run_finished:
            run.ended_at = timestamp


def _persist_execution_output_artifact(
    db_path: str,
    *,
    run_id: str,
    task_id: str,
    brain_outputs: Mapping[str, Any],
) -> None:
    """Persist a transitional canonical execution output bundle artifact."""
    database_url = _project_state_db_url_from_path(db_path)
    initialize_database(database_url)
    session_factory = get_session_factory(database_url)
    created_at = datetime.now(timezone.utc)
    metadata_json: dict[str, object] = {
        "run_id": run_id,
        "task_id": task_id,
        "format_version": 1,
        "brain_outputs": brain_outputs,
    }
    content_hash = hashlib.sha256(
        json.dumps(metadata_json, sort_keys=True).encode("utf-8")
    ).hexdigest()
    with session_factory() as session:
        task = session.get(Task, task_id)
        if task is None:
            return
        repo = ArtifactRepository(session)
        repo.create_version(
            version_id=str(uuid.uuid4()),
            artifact_id=f"execution-output:{run_id}",
            project_id=task.project_id,
            artifact_type="execution_output_bundle",
            version=1,
            content_hash=content_hash,
            created_at=created_at,
            metadata_json=metadata_json,
        )


class _PassthroughMCPClient:
    """Minimal MCPClient adapter for background task context.

    StatelessCoordinator requires an MCPClient at construction time, but in a
    FastAPI background task the brain agents run as Claude Code subagents — they
    make their own NotebookLM calls via Bash. This stub satisfies the protocol
    without invoking MCP tools from Python.
    """

    def query_notebooklm(self, notebook_id: str, query: str) -> str:
        """Return an empty placeholder because subagents call MCP directly."""
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


async def _post_session_evaluated_event(
    task_id: str,
    brain_ids: list[str],
    quality_scores: dict[str, float],
) -> None:
    """POST a session_evaluated brain-event to the Rust control plane.

    This fires-and-forgets — failures are silently swallowed so a Rust
    outage never blocks brain execution results from being persisted.

    The Rust /internal/brain-event endpoint fans out to all /ws/events
    WebSocket subscribers, which is how the frontend receives the badge update.

    Args:
        task_id: The task (trace) ID for the evaluated session.
        brain_ids: List of brain IDs that ran in this session.
        quality_scores: Mapping of brain_id → quality_score (0.0–1.0).
    """
    if not brain_ids:
        return

    avg_score = (
        sum(quality_scores.values()) / len(quality_scores) if quality_scores else 0.0
    )

    payload = {
        "trace_id": task_id,
        "brain_id": brain_ids[-1],  # Last brain = session representative
        "status": "session_evaluated",
        "quality_score": round(avg_score, 4),
        "brain_ids": brain_ids,
        "scores": quality_scores,
    }

    try:
        async with httpx.AsyncClient(timeout=2.0) as client:
            await client.post(
                f"{_RUST_CONTROL_PLANE_URL}/internal/brain-event",
                json=payload,
            )
    except httpx.HTTPError as exc:
        log.debug(
            "session_evaluated event delivery failed for task_id=%s: %s",
            task_id,
            exc,
            exc_info=True,
        )
        # Non-fatal — Rust may be down; Python side is already persisted


async def run_brain_task(
    task_id: str,
    brief: str,
    flow: str | None,
    db_path: str,
    *,
    experience_logger_factory: ExperienceLoggerFactory | None = None,
    governance: GovernanceInterceptor | None = None,
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
        experience_logger_factory: Optional seam for injecting an execution logger
            during tests or storage transitions.
    """
    async with DatabaseConnection(db_path) as db:
        await db.conn.execute(
            "UPDATE executions SET status = ? WHERE id = ?",
            ["running", task_id],
        )
        await db.conn.commit()
    try:
        _update_project_state_status(
            db_path,
            task_id,
            "running",
            mark_run_finished=False,
        )
    except (OSError, RuntimeError, TypeError, ValueError, SQLAlchemyError) as exc:
        log.warning(
            "project_state running status update failed for task_id=%s: %s",
            task_id,
            exc,
            exc_info=True,
        )

    detector = FlowDetector()
    flow_type = flow if flow else detector.detect(brief)
    brain_ints = detector.get_flow_sequence(flow_type)
    brain_ids = [BRAIN_ID_MAP[n] for n in brain_ints if n in BRAIN_ID_MAP]

    project_id = _load_task_project_id(db_path, task_id)
    memory_context_provider: (
        Callable[[str, str | None], ContextSnapshot | None] | None
    ) = None
    memory_runtime_writer: MemoryRuntimeAdapter | None = None
    memory_service: MemoryService | None = None
    memory_snapshot: ContextSnapshot | None = None

    if project_id is not None:
        memory_database_url = os.environ.get(
            "MM_MEMORY_DATABASE_URL"
        ) or os.environ.get("DATABASE_URL")
        if memory_database_url:
            try:
                memory_service = MemoryService(
                    build_memory_store_from_env(
                        memory_database_url,
                        enable_vector=False,
                        enable_index=True,
                    )
                )
                memory_snapshot = await memory_service.build_context_snapshot(
                    project_id
                )
                memory_runtime_writer = MemoryRuntimeAdapter(
                    memory_service=memory_service
                )

                def _snapshot_provider(
                    _project_id: str, _task_id: str | None
                ) -> ContextSnapshot | None:
                    return memory_snapshot

                memory_context_provider = _snapshot_provider
            except (MemorySnapshotError, OSError, ValueError) as exc:
                log.warning(
                    "memory snapshot load failed for task_id=%s project_id=%s: %s",
                    task_id,
                    project_id,
                    exc,
                    exc_info=True,
                )
                if memory_service is not None:
                    memory_runtime_writer = MemoryRuntimeAdapter(
                        memory_service=memory_service
                    )

    coordinator = create_stateless_coordinator(
        _PassthroughMCPClient(),
        governance=governance,
        project_id=project_id,
        memory_context_provider=memory_context_provider,
        memory_runtime_writer=memory_runtime_writer,
    )
    start_ms = int(time.time() * 1000)

    async def _mark_execution_failed_during_shutdown() -> None:
        """Best-effort shutdown bookkeeping for failed executions."""
        failures: list[str] = []
        try:
            async with DatabaseConnection(db_path) as db:
                await db.conn.execute(
                    "UPDATE executions SET status = ? WHERE id = ?",
                    ["failed", task_id],
                )
                await db.conn.commit()
        except sqlite3.Error as exc:
            failures.append(f"execution status update failed during shutdown: {exc}")
        try:
            _update_project_state_status(
                db_path,
                task_id,
                "failed",
                mark_run_finished=True,
            )
        except (OSError, RuntimeError, TypeError, ValueError, SQLAlchemyError) as exc:
            failures.append(f"project_state failed status update failed: {exc}")
        if failures:
            raise TaskShutdownWriteError("; ".join(failures))

    # Phase 21: open asyncpg connection for RAG retrieval.
    # If PostgreSQL is unavailable, conn stays None and RAG is skipped gracefully.
    pg_conn: asyncpg.Connection | None = None
    if _DEFAULT_DATABASE_URL:
        try:
            pg_conn = await asyncpg.connect(_DEFAULT_DATABASE_URL)
        except (
            OSError,
            RuntimeError,
            TimeoutError,
            ValueError,
            asyncpg.PostgresError,
        ) as exc:  # noqa: BLE001
            log.warning("RAG skipped — asyncpg connect failed: %s", exc)

    try:
        brief_obj = Brief(problem_statement=brief, context="", target_audience=None)
        execute_flow = coordinator.execute_flow
        signature = inspect.signature(execute_flow)
        if "conn" in signature.parameters or any(
            param.kind == inspect.Parameter.VAR_KEYWORD
            for param in signature.parameters.values()
        ):
            results = await execute_flow(brief_obj, brain_ids, conn=pg_conn)
        else:
            results = await execute_flow(brief_obj, brain_ids)
        elapsed_ms = int(time.time() * 1000) - start_ms

        # 21.19: rag_enabled = True only if Brain #1 retrieved real context.
        # We detect this by asking RAGContextBuilder.build() again with the same
        # connection — build() is idempotent (read-only) so calling twice is safe.
        # Alternatively, build() could return a flag, but that would change its
        # public API.  The re-call pattern keeps the API stable.
        rag_context_per_brain: dict[str, bool] = {}
        if pg_conn is not None:
            from mastermind_cli.rag.context_builder import RAGContextBuilder

            for bid in results:
                if bid in {"brain-01-product", "brain-01-product-strategy"}:
                    ctx = await RAGContextBuilder(pg_conn).build(bid, brief)
                    rag_context_per_brain[bid] = ctx != ""
                else:
                    rag_context_per_brain[bid] = False
        else:
            rag_context_per_brain = {bid: False for bid in results}

        # C3: Evaluate all brain outputs with Brain #7 before persisting
        eval_scores: dict[str, float] = {}
        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            logger = _build_experience_logger(db, experience_logger_factory)
            for brain_id, output in results.items():
                output_dict = (
                    output.model_dump() if hasattr(output, "model_dump") else {}
                )

                # C3.02/C3.03: Brain #7 post-session evaluation
                eval_result = evaluate_session(
                    brain_id=brain_id,
                    output_json=output_dict,
                    duration_ms=elapsed_ms,
                    status="success",
                )
                eval_scores[brain_id] = eval_result.quality_score

                # 21.19: rag_enabled = True only when RAG returned real context.
                rag_enabled: bool = rag_context_per_brain.get(brain_id, False)

                # C3.04/C3.05: quality_score + model + high_value in custom_metadata
                # 21.18: rag_enabled added to custom_metadata
                custom_meta: dict[str, object] = {
                    "model": os.environ.get("MM_MODEL", "unknown"),
                    "high_value": eval_result.high_value,
                    "insights": eval_result.insights,
                    "task_id": task_id,
                    "flow_type": flow_type,
                    "rag_enabled": rag_enabled,
                }

                # 21.20: include rag_enabled in LangSmith span metadata (non-blocking)
                try:
                    from langsmith import get_current_run_tree

                    rt = get_current_run_tree()
                    if rt is not None:
                        rt.metadata.update({"rag_enabled": rag_enabled})
                except (
                    AttributeError,
                    RuntimeError,
                    TypeError,
                    ValueError,
                ) as exc:  # noqa: BLE001
                    log.debug(
                        "LangSmith metadata update failed for task_id=%s brain_id=%s: %s",
                        task_id,
                        brain_id,
                        exc,
                        exc_info=True,
                    )  # LangSmith optional — never fail brain execution

                await logger.log_execution(
                    brain_id=brain_id,
                    input_json={"brief": brief, "flow": flow_type},
                    output_json=output_dict,
                    duration_ms=elapsed_ms,
                    status="success",
                    trace_context_id=task_id,
                    quality_score=eval_result.quality_score,
                    custom_metadata=custom_meta,
                )

            await db.conn.execute(
                "UPDATE executions SET status = ? WHERE id = ?",
                ["completed", task_id],
            )
            await db.conn.commit()
        try:
            _update_project_state_status(
                db_path,
                task_id,
                "completed",
                mark_run_finished=True,
            )
        except (OSError, RuntimeError, TypeError, ValueError, SQLAlchemyError) as exc:
            log.warning(
                "project_state completed status update failed for task_id=%s: %s",
                task_id,
                exc,
                exc_info=True,
            )
        try:
            canonical_outputs = {
                brain_id: (output.model_dump() if hasattr(output, "model_dump") else {})
                for brain_id, output in results.items()
            }
            _persist_execution_output_artifact(
                db_path,
                run_id=task_id,
                task_id=task_id,
                brain_outputs=canonical_outputs,
            )
        except (OSError, RuntimeError, TypeError, ValueError, SQLAlchemyError) as exc:
            log.warning(
                "execution output artifact persistence failed for task_id=%s: %s",
                task_id,
                exc,
                exc_info=True,
            )

        # C3.06: POST session_evaluated event to Rust control plane (outside DB ctx)
        await _post_session_evaluated_event(
            task_id=task_id,
            brain_ids=list(results.keys()),
            quality_scores=eval_scores,
        )

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
                    routed_logger = _build_experience_logger(
                        db,
                        experience_logger_factory,
                    )
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
            except (
                ConnectionError,
                OSError,
                RuntimeError,
                TimeoutError,
                TypeError,
                ValueError,
            ) as exc:
                log.warning(
                    "routed brain execution failed for task_id=%s from=%s to=%s: %s",
                    task_id,
                    brain_id,
                    target_brain,
                    exc,
                    exc_info=True,
                )  # Routed brain failure is isolated — parent stays completed

    except asyncio.CancelledError:
        # CancelledError is BaseException — must be handled explicitly
        # Brain #6: status must be written even on shutdown signal
        elapsed_ms = int(time.time() * 1000) - start_ms
        try:
            await _mark_execution_failed_during_shutdown()
        except TaskShutdownWriteError:
            log.warning(
                "shutdown bookkeeping failed for task_id=%s",
                task_id,
                exc_info=True,
            )
    except (OSError, RuntimeError, TypeError, ValueError, SQLAlchemyError):
        elapsed_ms = int(time.time() * 1000) - start_ms
        try:
            await _mark_execution_failed_during_shutdown()
        except TaskShutdownWriteError:
            log.warning(
                "shutdown bookkeeping failed for task_id=%s",
                task_id,
                exc_info=True,
            )
    finally:
        # Phase 21: always close the asyncpg RAG connection (if opened)
        if pg_conn is not None:
            try:
                await pg_conn.close()
            except (
                ConnectionError,
                OSError,
                RuntimeError,
                TimeoutError,
                ValueError,
            ) as exc:  # noqa: BLE001
                log.debug(
                    "failed to close asyncpg RAG connection for task_id=%s: %s",
                    task_id,
                    exc,
                    exc_info=True,
                )
