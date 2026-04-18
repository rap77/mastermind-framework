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
import os
import uuid
from datetime import datetime
from pathlib import Path

import asyncpg
import click

from mastermind_cli.mm_flow.config_loader import RuntimeState

RUNTIME_STATE_PATH = Path(".planning/.mm-flow/runtime-state.json")


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
        raise click.UsageError(
            "--start and --complete are mutually exclusive.\n"
            "Example: --start creates a new execution, --complete finishes it."
        )
    if not start and not complete:
        raise click.UsageError(
            "Either --start or --complete is required.\n"
            "To start: execute-phase --phase 19 --start\n"
            "To complete: execute-phase --phase 19 --complete --commit abc123"
        )

    postgres_url = os.environ.get("DATABASE_URL")
    if not postgres_url:
        raise click.UsageError(
            "DATABASE_URL environment variable must be set.\n"
            "Example: export DATABASE_URL=postgresql://user:pass@host:port/db"
        )

    async def _run() -> None:
        conn = await asyncio.wait_for(asyncpg.connect(postgres_url), timeout=5.0)
        try:
            # Set org_id for RLS policies (required for audit tables - IMPORTANT #1)
            org_id = os.environ.get("MM_FLOW_ORG_ID", "default-org-id")
            await conn.execute("SET LOCAL mm_flow.org_id = $1", org_id)

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
                click.echo(f"execution_id:{execution_id}")

            elif complete:
                # Read execution_id from runtime-state.json (C4 — EXEC_ID handoff)
                execution_id = ""
                if RUNTIME_STATE_PATH.exists():
                    state_data = json.loads(RUNTIME_STATE_PATH.read_text())
                    execution_id = state_data.get("execution_id", "")

                if execution_id:
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
                backend = os.environ.get("MM_FLOW_BACKEND", "claude")
                _write_runtime_state(
                    execution_id or "", phase, "COMPLETED", 0, "IDLE", backend
                )
                click.echo(f"Phase {phase} marked complete")

        finally:
            await conn.close()

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
