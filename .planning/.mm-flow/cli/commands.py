"""
MM-Flow CLI: multi-project workflow orchestrator commands.

Usage:
    python -m planning.mm_flow.cli.commands --help
    mm-flow init --org acme-corp --project mastermind
    mm-flow status
    mm-flow execute-phase --phase 19
    mm-flow night-run --project mastermind --phase 19 --max-hours 8
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, cast

# Setup Python path to find .mm-flow modules
_MM_FLOW_PATH = Path(__file__).parent.parent
if str(_MM_FLOW_PATH) not in sys.path:
    sys.path.insert(0, str(_MM_FLOW_PATH))

import click  # noqa: E402
import psycopg2  # noqa: E402
import psycopg2.extras  # noqa: E402

# Context file location
CONTEXT_FILE = Path.home() / ".mm-flow" / ".context.json"


def _load_context() -> dict:
    if not CONTEXT_FILE.exists():
        raise click.ClickException(
            f"No context found at {CONTEXT_FILE}. Run 'mm-flow init' first."
        )
    with CONTEXT_FILE.open() as fh:
        return json.load(fh)


def _save_context(ctx: dict) -> None:
    CONTEXT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with CONTEXT_FILE.open("w") as fh:
        json.dump(ctx, fh, indent=2)


def _db_url() -> str:
    import sys
    from pathlib import Path

    mm_flow_path = Path(__file__).parent.parent
    if str(mm_flow_path) not in sys.path:
        sys.path.insert(0, str(mm_flow_path))
    from config import POSTGRES_LOCAL  # type: ignore[import]

    return POSTGRES_LOCAL.connection_string


# ---------------------------------------------------------------------------
# CLI group
# ---------------------------------------------------------------------------


@click.group()
def cli():
    """MM-Flow: Multi-project workflow orchestrator with intelligent backend management."""
    pass


# ---------------------------------------------------------------------------
# mm-flow init
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--org", required=True, help="Organization slug (e.g. acme-corp)")
@click.option("--project", required=True, help="Project slug (e.g. mastermind)")
@click.option(
    "--backend",
    default="z_ai",
    type=click.Choice(["claude", "openrouter", "z_ai"], case_sensitive=False),
    help="Initial backend to use (default: z_ai)",
)
def init(org: str, project: str, backend: str) -> None:
    """Initialize project context. Saves to ~/.mm-flow/.context.json"""
    db = _db_url()
    try:
        conn = psycopg2.connect(db, cursor_factory=psycopg2.extras.RealDictCursor)
    except Exception as exc:
        raise click.ClickException(f"Cannot connect to PostgreSQL: {exc}")

    with conn:
        with conn.cursor() as cur:
            # Resolve org
            cur.execute("SELECT id, name FROM organizations WHERE slug = %s", (org,))
            _org = cur.fetchone()
            org_row: Optional[Dict[str, Any]] = (
                cast(Dict[str, Any], _org) if _org else None
            )
            if not org_row:
                raise click.ClickException(
                    f"Organization '{org}' not found in database."
                )

            # Resolve project
            cur.execute(
                "SELECT id, name FROM projects WHERE org_id = %s AND slug = %s",
                (org_row["id"], project),
            )
            _proj = cur.fetchone()
            proj_row: Optional[Dict[str, Any]] = (
                cast(Dict[str, Any], _proj) if _proj else None
            )
            if not proj_row:
                raise click.ClickException(
                    f"Project '{project}' not found under org '{org}'."
                )

            # Resolve workspace
            cur.execute(
                "SELECT id, current_phase FROM workspaces WHERE project_id = %s LIMIT 1",
                (proj_row["id"],),
            )
            _ws = cur.fetchone()
            ws_row: Optional[Dict[str, Any]] = (
                cast(Dict[str, Any], _ws) if _ws else None
            )
            if not ws_row:
                raise click.ClickException(
                    f"No workspace found for project '{project}'. "
                    "Run the seed script first."
                )

    context = {
        "org": org,
        "project": project,
        "org_id": str(org_row["id"]) if org_row else "",
        "project_id": str(proj_row["id"]) if proj_row else "",
        "workspace_id": str(ws_row["id"]) if ws_row else "",
        "backend": backend,
        "phase": ws_row["current_phase"] if ws_row else 1,
        "last_checkpoint": None,
    }
    _save_context(context)
    click.echo(
        f"✅ Initialized {org}/{project} "
        f"(phase={context['phase']}, backend={backend})"
    )
    click.echo(f"   Context saved to: {CONTEXT_FILE}")


# ---------------------------------------------------------------------------
# mm-flow status
# ---------------------------------------------------------------------------


def _fmt_tokens(n: int) -> str:
    """Format token count as compact string: 100000 → '100K'."""
    if n >= 1_000:
        return f"{n // 1_000}K"
    return str(n)


def _status_cell(row: dict) -> str:
    """
    Build the Status column content for a backend row.

    Examples:
        "❌ DEPLETED ⏳ 18h 30m 45s"
        "✅ READY (108K available)"
    """
    countdown = row["countdown"]
    if countdown["is_depleted"] and countdown["total_seconds"] > 0:
        return f"❌ DEPLETED ⏳ {countdown['status']}"
    available_fmt = _fmt_tokens(row["tokens_available"])
    return f"✅ READY ({available_fmt} available)"


@cli.command()
def status() -> None:
    """Show MM-Flow status with reset countdown per backend."""
    ctx = _load_context()

    from backend_scheduler import BackendScheduler  # type: ignore[import]
    from multi_backend_manager import MultiBackendManager  # type: ignore[import]

    db = _db_url()
    scheduler = BackendScheduler(
        org_id=ctx["org_id"],
        project_id=ctx["project_id"],
        db_url=db,
    )
    mgr = MultiBackendManager(
        org_id=ctx["org_id"],
        project_id=ctx["project_id"],
        db_url=db,
    )
    summary = scheduler.get_all_usage_summary()

    # Determine best available backend
    try:
        best = mgr.get_best_available_backend()
        current_backend = best["backend"]
    except Exception:
        current_backend = ctx.get("backend", "unknown")

    click.echo(f"\nProject: {ctx['project']} ({ctx['org']})")
    click.echo()

    # Table dimensions
    col_backend = 10
    col_used = 13
    col_pct = 7
    col_status = 32

    border_top = f"┌{'─'*col_backend}┬{'─'*col_used}┬{'─'*col_pct}┬{'─'*col_status}┐"
    border_header = f"├{'─'*col_backend}┼{'─'*col_used}┼{'─'*col_pct}┼{'─'*col_status}┤"
    border_bottom = f"└{'─'*col_backend}┴{'─'*col_used}┴{'─'*col_pct}┴{'─'*col_status}┘"

    header = (
        f"│ {'Backend':<{col_backend - 2}} "
        f"│ {'Used/Limit':^{col_used - 2}} "
        f"│ {'%Used':^{col_pct - 2}} "
        f"│ {'Status':<{col_status - 2}} │"
    )

    click.echo(border_top)
    click.echo(header)
    click.echo(border_header)

    for row in summary:
        used_fmt = _fmt_tokens(row["tokens_used"])
        limit_fmt = _fmt_tokens(row["tokens_limit"])
        used_limit = f"{used_fmt}/{limit_fmt}"
        pct_used = f"{row['pct_used']:.0f}%"
        status_text = _status_cell(row)

        # Truncate status to fit column
        max_status_width = col_status - 2
        if len(status_text) > max_status_width:
            status_text = status_text[: max_status_width - 1] + "…"

        click.echo(
            f"│ {row['backend']:<{col_backend - 2}} "
            f"│ {used_limit:^{col_used - 2}} "
            f"│ {pct_used:^{col_pct - 2}} "
            f"│ {status_text:<{max_status_width}} │"
        )

    click.echo(border_bottom)

    # Footer: current backend and next switch suggestion
    click.echo(f"\nCurrent  : {current_backend} (phase {ctx['phase']})")

    # Find best fallback
    ready_rows = [
        r
        for r in summary
        if not r["countdown"]["is_depleted"] or r["countdown"]["total_seconds"] == 0
    ]
    ready_rows.sort(key=lambda r: r["tokens_available"], reverse=True)
    if len(ready_rows) >= 2:
        fallback = ready_rows[1]
        click.echo(
            f"Next switch: If {current_backend} < 5K → will use "
            f"{fallback['backend']} ({_fmt_tokens(fallback['tokens_available'])} available)"
        )
    click.echo()


# ---------------------------------------------------------------------------
# mm-flow execute-phase
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--phase", type=int, required=True, help="Phase number to execute")
def execute_phase(phase: int) -> None:
    """Execute a phase using current context from ~/.mm-flow/.context.json"""
    ctx = _load_context()

    from multi_backend_manager import MultiBackendManager  # type: ignore[import]
    from state_machine import StateMachine  # type: ignore[import]

    db = _db_url()
    mgr = MultiBackendManager(ctx["org_id"], ctx["project_id"], db)
    sm = StateMachine(ctx["org_id"], ctx["project_id"], ctx["workspace_id"], db)

    best = mgr.get_best_available_backend()
    click.echo(
        f"Using backend: {best['backend']} "
        f"({best['tokens_available']:,} tokens available)"
    )

    sm.set_phase_context(
        phase=phase,
        status="in_progress",
        state_data={"started_via": "cli"},
        backend_used=best["backend"],
    )
    click.echo(f"Phase {phase} → in_progress")

    # Placeholder: actual execution delegated to brain pipeline
    click.echo(f"[Placeholder] Executing phase {phase} logic…")

    sm.set_phase_context(
        phase=phase,
        status="completed",
        state_data={"completed_via": "cli", "output": "placeholder output"},
        backend_used=best["backend"],
    )

    # Update context file
    ctx["phase"] = phase
    ctx["backend"] = best["backend"]
    _save_context(ctx)

    click.echo(f"✅ Phase {phase} complete.")


# ---------------------------------------------------------------------------
# mm-flow night-run
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--project", required=True, help="Project slug")
@click.option("--phase", type=int, required=True, help="Phase number to run")
@click.option(
    "--max-hours", default=8, type=float, help="Maximum runtime hours (default: 8)"
)
def night_run(project: str, phase: int, max_hours: float) -> None:
    """Run phase autonomously for max_hours (overnight mode)."""
    ctx = _load_context()

    if ctx["project"] != project:
        raise click.ClickException(
            f"Context project is '{ctx['project']}', but --project='{project}'. "
            "Run 'mm-flow init' with the correct project first."
        )

    from night_mode import NightModeExecutor  # type: ignore[import]

    executor = NightModeExecutor(
        org_id=ctx["org_id"],
        project_id=ctx["project_id"],
        phase=phase,
        max_hours=max_hours,
        db_url=_db_url(),
    )

    click.echo(
        f"Starting night run: {project}/phase={phase} " f"max_hours={max_hours} …"
    )
    result = executor.run()

    click.echo(f"\n{'='*50}")
    click.echo("Night run complete.")
    click.echo(f"  Status   : {result['status']}")
    click.echo(f"  Progress : {result['progress_pct']}%")
    click.echo(f"  Completed: {', '.join(result['completed_subtasks']) or 'none'}")
    if result["paused_reason"]:
        click.echo(f"  Paused   : {result['paused_reason']}")
    click.echo(f"  Started  : {result['started_at']}")
    click.echo(f"  Ended    : {result['ended_at']}")


# ---------------------------------------------------------------------------
# mm-flow context
# ---------------------------------------------------------------------------


@cli.command()
@click.option(
    "--phase", type=int, required=True, help="Phase number to recover context for"
)
@click.option(
    "--project",
    default="mastermind",
    help="Project name (default: mastermind)",
)
@click.option(
    "--output",
    type=click.Path(),
    help="Override output file path (optional)",
)
def context(phase: int, project: str, output: Optional[str]) -> None:
    """
    Generate CONTEXT.md for a phase by querying Engram.

    Recovers prior decisions, warnings, and learnings from Engram persistent memory.
    Writes to .planning/phases/0N-*/CONTEXT.md by default.

    Usage:
        mm-flow context --phase 19
        mm-flow context --phase 19 --project mastermind
        mm-flow context --phase 19 --output /tmp/context.md
    """
    from context_loader import generate_context_for_phase  # type: ignore[import]

    output_path = Path(output) if output else None

    try:
        result_path = generate_context_for_phase(
            project=project,
            phase_num=phase,
            output_path=output_path,
        )

        if result_path:
            click.echo(f"✅ Context generated: {result_path}")
            click.echo(f"   Use this context when planning phase {phase}.")
        else:
            click.echo(
                f"⚠️  No context found in Engram for phase {phase}. "
                f"This is OK — proceeding without prior context."
            )

    except Exception as e:
        raise click.ClickException(f"Failed to generate context: {e}")


# ---------------------------------------------------------------------------
# mm-flow plan-phase (wrapper)
# ---------------------------------------------------------------------------


@cli.command()
@click.option("--phase", type=int, required=True, help="Phase number to plan")
@click.option(
    "--project",
    default="mastermind",
    help="Project name (default: mastermind)",
)
def plan_phase(phase: int, project: str) -> None:
    """
    Plan a phase with automatic Engram context injection.

    This is a wrapper that:
    1. Generates CONTEXT.md from Engram (automatically)
    2. Calls /mm:plan-phase N with context auto-injected
    3. Returns PLAN.md with context references

    The context injection is transparent — the user just sees one command.

    Usage:
        mm-flow plan-phase --phase 19
        mm-flow plan-phase --phase 19 --project mastermind
    """
    from context_loader import generate_context_for_phase  # type: ignore[import]

    click.echo(f"Planning phase {phase} for {project}…")
    click.echo()

    # Step 1: Auto-generate context from Engram
    click.echo("1️⃣  Recovering context from Engram…")
    context_path = generate_context_for_phase(
        project=project,
        phase_num=phase,
        output_path=None,
    )

    if context_path:
        click.echo(f"   ✅ Context found: {context_path}")
    else:
        click.echo("   ⚠️  No prior context (OK, will proceed without)")

    click.echo()

    # Step 2: Invoke /mm:plan-phase N
    # NOTE: This would normally delegate to the /mm:plan-phase skill
    # For now, we just indicate what would happen
    click.echo(f"2️⃣  Would invoke: /mm:plan-phase {phase} --context <auto>")
    click.echo()
    click.echo(
        "   (In production: this delegates to the MasterMind brain planning skill)"
    )
    click.echo()

    # Step 3: Summary
    click.echo(f"✅ Phase {phase} planning would proceed with context auto-injected.")
    click.echo("   PLAN.md will reference prior decisions and learnings.")
    click.echo()
    click.echo(f"   Next: Review .planning/phases/{phase:02d}-*/PLAN.md")
    click.echo(f"   Then: Run `mm-flow execute-phase --phase {phase}`")


if __name__ == "__main__":
    cli()
