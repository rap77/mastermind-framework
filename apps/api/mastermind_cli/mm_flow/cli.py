"""
MM-Flow CLI — lifecycle management for phase execution.

Registers phase executions in PostgreSQL phase_executions table.
Writes runtime-state.json atomically for EXEC_ID handoff (C4).

Usage:
    uv run python -m mastermind_cli.mm_flow.cli execute-phase --phase 19 --start
    uv run python -m mastermind_cli.mm_flow.cli execute-phase --phase 19 --complete --commit abc123
"""

import asyncio
import json
import logging
import os
import uuid
import subprocess
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import cast

import asyncpg
import click

from mastermind_cli.memory_layer.runtime import build_memory_store_from_env
from mastermind_cli.memory_layer.service import MemoryService
from mastermind_cli.mm_flow.evidence_selector import (
    EvidenceHarnessSelector,
    EvidenceSelectionRequest,
    EvidenceClarity,
    RiskLevel,
    UncertaintyLevel,
)
from mastermind_cli.mm_flow.evidence_registry_service import EvidenceRegistryService
from mastermind_cli.mm_flow.config_loader import RuntimeState
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter

RUNTIME_STATE_PATH = Path(".planning/.mm-flow/runtime-state.json")
logger = logging.getLogger(__name__)


def _project_root() -> Path:
    """Resolve the repository root from git."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path.cwd()


def _registry_path() -> Path:
    """Return the active file registry path."""
    return _project_root() / ".planning" / "evidence" / "evidence-registry.json"


def _build_memory_service(database_url: str) -> MemoryService:
    """Build the first-party memory service for MM-Flow persistence."""
    return MemoryService(
        build_memory_store_from_env(
            database_url,
            enable_vector=False,
            enable_index=True,
        )
    )


def _build_project_adapter() -> ProjectAdapter:
    """Build the repo-specific planning bridge adapter."""
    return ProjectAdapter.for_repo(_project_root())


def _write_runtime_state(
    execution_id: str,
    phase: int,
    moment: str,
    brain: int,
    state: str,
    backend: str,
) -> None:
    """Write runtime-state.json atomically via temp file + rename (C2).

    Args:
        execution_id: UUID string matching phase_executions.id (C4).
        phase: Phase number being executed.
        moment: Current execution moment (e.g. EXECUTION_WAVE, COMPLETED).
        brain: Active brain ID; 0 means orchestrator.
        state: Brain lifecycle state (ACTIVE | IDLE | BARRIER | OFFLINE).
        backend: Execution backend identifier (e.g. "claude").
    """
    state_obj = RuntimeState(
        execution_id=execution_id,
        phase=phase,
        current_moment=moment,
        active_brain=brain,
        brain_state=state,
        backend=backend,
        updated_at=datetime.now().isoformat(),
    )
    state_obj.to_json_file(RUNTIME_STATE_PATH)


@click.group()
def cli() -> None:
    """MM-Flow CLI for phase execution lifecycle management.

    Provides commands to register phase start/completion in the PostgreSQL
    audit trail and maintain the runtime-state.json checkpoint file.
    """


@cli.command("execute-phase")
@click.option("--phase", type=int, required=True, help="Phase number")
@click.option("--start", is_flag=True, help="Mark phase as started")
@click.option("--complete", is_flag=True, help="Mark phase as completed")
@click.option("--commit", default=None, help="Git commit hash at completion")
@click.option("--tokens", type=int, default=0, help="Tokens consumed")
@click.option("--summary", default="", help="Execution summary")
def execute_phase(
    phase: int,
    start: bool,
    complete: bool,
    commit: str | None,
    tokens: int,
    summary: str,
) -> None:
    """Manage the lifecycle of a single phase execution.

    Args:
        phase: Phase number to track (e.g. 19).
        start: When True, inserts a new in_progress row and echoes execution_id.
        complete: When True, updates the row to completed using the stored UUID.
        commit: Git commit hash to attach at completion.
        tokens: Tokens consumed during execution (default 0).
        summary: Human-readable summary written to output_summary column.
    """
    if start and complete:
        raise ValueError(
            "--start and --complete are mutually exclusive.\n"
            "Example: --start creates a new execution, --complete finishes it."
        )
    if not start and not complete:
        raise ValueError(
            "Either --start or --complete is required.\n"
            "To start: execute-phase --phase 19 --start\n"
            "To complete: execute-phase --phase 19 --complete --commit abc123"
        )

    postgres_url = os.environ.get("DATABASE_URL")
    if not postgres_url:
        raise ValueError(
            "DATABASE_URL environment variable must be set.\n"
            "Example: export DATABASE_URL=postgresql://user:pass@host:port/db"
        )

    async def _run() -> None:
        conn = await asyncio.wait_for(asyncpg.connect(postgres_url), timeout=5.0)
        try:
            async with conn.transaction():
                # Set org_id for RLS policies (required for audit tables - IMPORTANT #1)
                org_id = os.environ.get("MM_FLOW_ORG_ID", "default-org-id")
                await conn.execute(
                    "SELECT set_config('mm_flow.org_id', $1, true)",
                    org_id,
                )

                if start:
                    execution_id = str(uuid.uuid4())
                    await conn.execute(
                        """INSERT INTO phase_executions
                               (id, phase_number, status, started_at, triggered_by)
                           VALUES ($1, $2, 'in_progress', NOW(), 'skill')
                           ON CONFLICT DO NOTHING""",
                        execution_id,
                        phase,
                    )
                    backend = os.environ.get("MM_FLOW_BACKEND", "claude")
                    _write_runtime_state(
                        execution_id, phase, "EXECUTION_WAVE", 0, "ACTIVE", backend
                    )
                    try:
                        adapter = _build_project_adapter()
                        request = adapter.load_harness_request()
                        adapter.write_structured_status(
                            status="in_progress",
                            summary=f"Phase {phase} execution started.",
                            next_action="continue_phase_execution",
                            verification_outcome="pending",
                            objective=request.operational_objective,
                            uow=request.active_uow,
                            warnings=request.warnings,
                        )
                    except Exception:
                        logger.warning(
                            "execute-phase planning bridge write failed",
                            exc_info=True,
                        )
                    project_id = os.environ.get("MM_MEMORY_PROJECT_ID")
                    if project_id:
                        try:
                            memory_service = _build_memory_service(postgres_url)
                            await memory_service.record_preference(
                                key="preferred_backend",
                                value={"backend_id": backend},
                                scope="project",
                                project_id=project_id,
                            )
                        except Exception:
                            logger.warning(
                                "execute-phase start preference persistence failed",
                                exc_info=True,
                            )
                    click.echo(f"execution_id:{execution_id}")

                elif complete:
                    # Read execution_id from runtime-state.json (C4 — EXEC_ID handoff)
                    execution_id = ""
                    if RUNTIME_STATE_PATH.exists():
                        try:
                            state_data = json.loads(RUNTIME_STATE_PATH.read_text())
                        except json.JSONDecodeError as exc:
                            raise ValueError(
                                "runtime-state.json is malformed; cannot complete phase."
                            ) from exc
                        execution_id = state_data.get("execution_id", "")

                    if not execution_id:
                        raise ValueError(
                            "runtime-state.json is missing execution_id; cannot complete phase."
                        )

                    await conn.execute(
                        """UPDATE phase_executions
                           SET status='completed', completed_at=NOW(),
                               git_commit_hash=$2, tokens_consumed=$3, output_summary=$4
                           WHERE id=$1""",
                        execution_id,
                        commit,
                        tokens,
                        summary,
                    )
                    project_id = os.environ.get("MM_MEMORY_PROJECT_ID")
                    if summary and project_id:
                        try:
                            memory_service = _build_memory_service(postgres_url)
                        except Exception:
                            logger.warning(
                                "execute-phase memory service construction failed",
                                exc_info=True,
                            )
                        else:
                            try:
                                await memory_service.record_session_summary(
                                    session_id=execution_id,
                                    summary=summary,
                                    project_id=project_id,
                                    metadata={
                                        "phase": phase,
                                        "git_commit_hash": commit,
                                        "tokens_consumed": tokens,
                                        "invocation_method": "mm:execute-phase",
                                    },
                                )
                            except Exception:
                                logger.warning(
                                    "execute-phase session summary persistence failed",
                                    exc_info=True,
                                )
                            try:
                                related_context = (
                                    await memory_service.fetch_project_context(
                                        project_id=project_id,
                                        query=summary,
                                        limit=3,
                                    )
                                )
                                related_memory_ids = [
                                    result.memory_id
                                    for result in related_context
                                    if result.memory_id
                                    and result.memory_id != execution_id
                                ]
                                await memory_service.record_learning(
                                    title=f"Session summary: {execution_id}",
                                    content=summary,
                                    project_id=project_id,
                                    memory_type="session_summary",
                                    visibility="project",
                                    source_kind="mm_flow",
                                    source_ref=f"session_summary:{execution_id}",
                                    tags=["session_summary", f"phase-{phase}"],
                                    related_memory_ids=related_memory_ids or None,
                                    metadata={
                                        "phase": phase,
                                        "git_commit_hash": commit,
                                        "tokens_consumed": tokens,
                                        "invocation_method": "mm:execute-phase",
                                    },
                                )
                            except Exception:
                                logger.warning(
                                    "execute-phase memory enrichment failed",
                                    exc_info=True,
                                )
                    backend = os.environ.get("MM_FLOW_BACKEND", "claude")
                    _write_runtime_state(
                        execution_id, phase, "COMPLETED", 0, "IDLE", backend
                    )
                    try:
                        adapter = _build_project_adapter()
                        request = adapter.load_harness_request()
                        adapter.write_structured_status(
                            status="completed",
                            summary=summary or f"Phase {phase} completed.",
                            next_action="archive_objective",
                            verification_outcome="passed",
                            objective=request.operational_objective,
                            uow=request.active_uow,
                            warnings=request.warnings,
                        )
                    except Exception:
                        logger.warning(
                            "execute-phase planning bridge archive failed",
                            exc_info=True,
                        )
                    click.echo(f"Phase {phase} marked complete")

        finally:
            await conn.close()

    asyncio.run(_run())


@cli.command("sync-evidence-registry")
@click.option(
    "--database-url",
    default=None,
    help="PostgreSQL DSN (defaults to DATABASE_URL env var)",
)
@click.option(
    "--registry-key",
    default="default",
    help="Logical registry key stored in Postgres",
)
def sync_evidence_registry(database_url: str | None, registry_key: str) -> None:
    """Sync the local evidence registry snapshot to PostgreSQL."""
    resolved_database_url = database_url or os.environ.get("DATABASE_URL")
    if not resolved_database_url:
        raise ValueError(
            "DATABASE_URL environment variable must be set or passed via --database-url."
        )

    service = EvidenceRegistryService(_registry_path())
    payload = asyncio.run(
        service.sync_to_postgres(
            resolved_database_url,
            registry_key=registry_key,
        )
    )
    click.echo(json.dumps(payload, indent=2))


@cli.command("evidence-readiness-score")
@click.option(
    "--registry-path",
    default=None,
    help="Path to evidence registry JSON (defaults to active planning registry)",
)
@click.option("--version-id", required=True, help="Registry version ID")
def evidence_readiness_score(registry_path: str | None, version_id: str) -> None:
    """Show the readiness score and gate for a registry version."""
    path = Path(registry_path) if registry_path else _registry_path()
    service = EvidenceRegistryService(path)
    payload = service.readiness(version_id)
    click.echo(json.dumps(payload, indent=2))


@cli.command("evidence-route")
@click.option("--objective", required=True, help="Objective or task description")
@click.option(
    "--source-clarity",
    type=click.Choice(["clear", "partial", "ambiguous"]),
    default="partial",
    show_default=True,
)
@click.option(
    "--uncertainty",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    show_default=True,
)
@click.option("--gap-count", type=int, default=0, show_default=True)
@click.option("--needs-interview", is_flag=True, help="Force interview-aware routing")
@click.option(
    "--risk-level",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    show_default=True,
)
@click.option("--token-budget", type=int, default=2000, show_default=True)
@click.option("--readiness-gate", default=None, help="Optional readiness gate")
@click.option(
    "--readiness-score", type=float, default=None, help="Optional readiness score"
)
def evidence_route(
    objective: str,
    source_clarity: str,
    uncertainty: str,
    gap_count: int,
    needs_interview: bool,
    risk_level: str,
    token_budget: int,
    readiness_gate: str | None,
    readiness_score: float | None,
) -> None:
    """Route an evidence task to the minimum sufficient harness."""
    selector = EvidenceHarnessSelector()
    payload = selector.select(
        EvidenceSelectionRequest(
            objective=objective,
            source_clarity=cast(EvidenceClarity, source_clarity),
            uncertainty=cast(UncertaintyLevel, uncertainty),
            gap_count=gap_count,
            needs_interview=needs_interview,
            risk_level=cast(RiskLevel, risk_level),
            token_budget=token_budget,
            readiness_gate=readiness_gate,
            readiness_score=readiness_score,
        )
    )
    click.echo(json.dumps(asdict(payload), indent=2))


if __name__ == "__main__":
    cli()
