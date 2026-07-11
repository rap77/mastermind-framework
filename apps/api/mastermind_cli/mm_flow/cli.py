"""
MM-Flow CLI — harness execution lifecycle management.

Runs a phase through `HarnessRunExecutor` end-to-end, registers the execution
in the PostgreSQL phase_executions audit trail, and writes the
`runtime-state.json` handoff for EXEC_ID continuity between `--start` and
`--complete`.

Usage:
    uv run python -m mastermind_cli.mm_flow.cli run-phase \\
        --phase 19 --brief "..." --brain-ids brain-01-product-strategy \\
        --status in_progress
    uv run python -m mastermind_cli.mm_flow.cli run-phase \\
        --phase 19 --brief "..." --brain-ids brain-01-product-strategy \\
        --status completed --commit abc123
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
from typing import Any, cast

import asyncpg
import click

from mastermind_cli.memory_layer.runtime import build_memory_service_from_env
from mastermind_cli.mm_flow.evidence_selector import (
    EvidenceHarnessSelector,
    EvidenceSelectionRequest,
    EvidenceClarity,
    RiskLevel,
    UncertaintyLevel,
)
from mastermind_cli.mm_flow.evidence_registry_service import EvidenceRegistryService
from mastermind_cli.mm_flow.config_loader import MMFlowConfig, RuntimeState, load_config
from mastermind_cli.mm_flow.exceptions import PlanningBridgeError
from mastermind_cli.mm_flow.harness_run_executor import HarnessRunExecutor
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter
from mastermind_cli.orchestrator.runtime_contracts import (
    BehavioralRoutingEvaluator,
    BehavioralRoutingReport,
    FileSystemHarnessCatalog,
    MemoryRuntimeAdapter,
    MultiHarnessPipeline,
    RunBundleComposer,
)
from mastermind_cli.orchestrator.stateless_coordinator import (
    CoordinatorConfig,
    StatelessCoordinator,
)
from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration

logger = logging.getLogger(__name__)


def _bridge_click_exception(
    adapter: ProjectAdapter, exc: PlanningBridgeError
) -> click.ClickException:
    """Wrap bridge failures with the handoff path for user-facing CLI errors."""
    return click.ClickException(f"{exc} (handoff: {adapter.handoff_path})")


def _project_root() -> Path:
    """Resolve the repository root from git when possible."""
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
    except (subprocess.SubprocessError, OSError) as exc:
        logger.debug("git rev-parse failed; falling back to cwd", exc_info=exc)
    return Path.cwd()


def _registry_path() -> Path:
    """Return the active file registry path."""
    return _project_root() / ".planning" / "evidence" / "evidence-registry.json"


def _runtime_state_path(project_root: Path | None = None) -> Path:
    """Return the resolved runtime-state.json path under the repo root."""
    root = project_root or _project_root()
    return root / ".planning" / ".mm-flow" / "runtime-state.json"


def _validate_completed_runtime_state(project_root: Path) -> str:
    """Load and validate the runtime-state before closing a completed phase."""
    runtime_state_path = _runtime_state_path(project_root)
    if not runtime_state_path.exists():
        raise ValueError(
            "runtime-state.json is missing execution_id; cannot complete phase."
        )
    try:
        state_data = json.loads(runtime_state_path.read_text())
    except json.JSONDecodeError as exc:
        raise ValueError(
            "runtime-state.json is malformed; cannot complete phase."
        ) from exc
    if state_data.get("current_moment") == "COMPLETED":
        raise ValueError(
            "runtime-state.json already marked COMPLETED; "
            "cannot complete phase again."
        )
    execution_id = str(state_data.get("execution_id", ""))
    if not execution_id:
        raise ValueError(
            "runtime-state.json is missing execution_id; cannot complete phase."
        )
    return execution_id


def _build_harness_executor(
    project_root: Path,
    postgres_url: str,
) -> tuple[ProjectAdapter, HarnessRunExecutor]:
    """Build the shared runtime wiring for MM-Flow phase execution."""
    config = load_config(str(_config_path(project_root)))
    adapter = ProjectAdapter.for_repo(project_root)
    memory_service = build_memory_service_from_env(
        postgres_url,
        enable_vector=False,
        enable_index=True,
    )
    executor = HarnessRunExecutor(
        adapter=adapter,
        mcp_client=cast(Any, MCPIntegration(use_mcp=False)),
        coordinator_factory=lambda **kwargs: StatelessCoordinator(
            CoordinatorConfig(**kwargs)
        ),
        memory_service=memory_service,
        memory_runtime_writer=MemoryRuntimeAdapter(memory_service=memory_service),
        multi_harness_pipeline=_build_multi_harness_pipeline(
            project_root,
            config,
        ),
    )
    return adapter, executor


def _config_path(project_root: Path) -> Path:
    """Return the resolved MM-Flow config path for a project root."""
    return project_root / ".planning" / ".mm-flow" / "config.yml"


def _build_multi_harness_pipeline(
    project_root: Path,
    config: MMFlowConfig,
) -> MultiHarnessPipeline | None:
    """Build the optional multi-harness pipeline from MM-Flow config."""
    if not config.harness_library.enabled:
        return None
    library_root = project_root / config.harness_library.path
    if not (library_root / "registry.yaml").is_file():
        raise ValueError(
            "harness_library.enabled=true but registry.yaml is missing at "
            f"{library_root / 'registry.yaml'}"
        )
    return MultiHarnessPipeline(
        catalog=FileSystemHarnessCatalog(library_root),
        composer=RunBundleComposer(
            output_root=project_root / config.harness_library.bundle_output_path,
            library_root=library_root,
        ),
    )


def _evaluate_harness_routing_cases(
    project_root: Path,
    config: MMFlowConfig,
    cases_path: str | None,
) -> BehavioralRoutingReport:
    """Evaluate declarative routing cases against the configured harness library."""
    if not config.harness_library.enabled:
        raise ValueError(
            "harness_library.enabled must be true to evaluate routing cases"
        )
    library_root = project_root / config.harness_library.path
    if not (library_root / "registry.yaml").is_file():
        raise ValueError(
            "harness_library.enabled=true but registry.yaml is missing at "
            f"{library_root / 'registry.yaml'}"
        )
    resolved_cases = (
        Path(cases_path) if cases_path else library_root / "routing-cases.yaml"
    )
    if not resolved_cases.is_file():
        raise ValueError(f"routing cases file is missing at {resolved_cases}")
    evaluator = BehavioralRoutingEvaluator(FileSystemHarnessCatalog(library_root))
    return evaluator.evaluate_file(resolved_cases)


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
    state_obj.to_json_file(_runtime_state_path())


@click.group()
def cli() -> None:
    """MM-Flow CLI for phase execution lifecycle management.

    Provides commands to register phase start/completion in the PostgreSQL
    audit trail and maintain the runtime-state.json checkpoint file.
    """


@cli.command("run-phase")
@click.option("--phase", type=int, required=True, help="Phase number")
@click.option(
    "--brief",
    required=True,
    help="Problem statement handed to the harness runtime.",
)
@click.option(
    "--brain-ids",
    required=True,
    help="Comma-separated brain IDs to execute (e.g. brain-01-product-strategy,brain-03-ui-design).",
)
@click.option(
    "--status",
    type=click.Choice(["in_progress", "completed"]),
    default="in_progress",
    show_default=True,
)
@click.option("--summary", default="", help="Human-readable summary for the run.")
@click.option(
    "--tokens", type=int, default=0, help="Tokens consumed (recorded on completion)."
)
@click.option("--commit", default=None, help="Git commit hash at completion.")
def run_phase(
    phase: int,
    brief: str,
    brain_ids: str,
    status: str,
    summary: str,
    tokens: int,
    commit: str | None,
) -> None:
    """Run the harness end-to-end via `HarnessRunExecutor` and record phase audit."""
    parsed_brain_ids = tuple(
        brain_id.strip() for brain_id in brain_ids.split(",") if brain_id.strip()
    )
    if not parsed_brain_ids:
        raise ValueError("--brain-ids must contain at least one brain ID")

    resolved_summary = summary or f"Phase {phase} {status}."
    project_root = _project_root()
    completed_execution_id = (
        _validate_completed_runtime_state(project_root) if status == "completed" else ""
    )
    postgres_url = os.environ.get("DATABASE_URL")
    if not postgres_url:
        raise ValueError(
            "DATABASE_URL environment variable must be set.\n"
            "Example: export DATABASE_URL=postgresql://user:pass@host:port/db"
        )

    async def _run() -> None:
        conn: Any = await asyncio.wait_for(asyncpg.connect(postgres_url), timeout=5.0)
        try:
            async with conn.transaction():
                org_id = os.environ.get("MM_FLOW_ORG_ID", "default-org-id")
                await conn.execute(
                    "SELECT set_config('mm_flow.org_id', $1, true)",
                    org_id,
                )

                execution_id = str(uuid.uuid4())
                if status == "in_progress":
                    adapter, executor = _build_harness_executor(
                        project_root, postgres_url
                    )
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
                        execution_id,
                        phase,
                        "EXECUTION_WAVE",
                        0,
                        "ACTIVE",
                        backend,
                    )
                    try:
                        run = await executor.execute_harness_run(
                            brief=Brief(
                                problem_statement=brief,
                                context="",
                                constraints=[],
                                target_audience="",
                            ),
                            brain_ids=parsed_brain_ids,
                            status="in_progress",
                            summary=resolved_summary,
                            verification_outcome="pending",
                        )
                    except PlanningBridgeError as exc:
                        raise _bridge_click_exception(adapter, exc) from exc
                    click.echo(
                        f"execution_id:{execution_id} project_id:{run.project_id} "
                        f"validation_passed:{run.validation.passed}"
                    )
                else:
                    execution_id = completed_execution_id
                    adapter, executor = _build_harness_executor(
                        project_root, postgres_url
                    )
                    try:
                        run = await executor.execute_harness_run(
                            brief=Brief(
                                problem_statement=brief,
                                context="",
                                constraints=[],
                                target_audience="",
                            ),
                            brain_ids=parsed_brain_ids,
                            status="completed",
                            summary=resolved_summary,
                            verification_outcome="passed",
                        )
                    except PlanningBridgeError as exc:
                        raise _bridge_click_exception(adapter, exc) from exc
                    update_result = await conn.execute(
                        """UPDATE phase_executions
                           SET status='completed', completed_at=NOW(),
                               git_commit_hash=$2, tokens_consumed=$3, output_summary=$4
                           WHERE id=$1 AND status='in_progress'""",
                        execution_id,
                        commit,
                        tokens,
                        resolved_summary,
                    )
                    if update_result.endswith("0"):
                        raise ValueError(
                            f"No in_progress phase_executions row matched id={execution_id}; "
                            "cannot complete phase."
                        )
                    memory_service = getattr(executor, "memory_service", None)
                    if memory_service is not None:
                        record_session_summary = getattr(
                            memory_service, "record_session_summary", None
                        )
                        if record_session_summary is not None:
                            await record_session_summary(
                                session_id=execution_id,
                                summary=resolved_summary,
                                project_id=run.project_id,
                                metadata={
                                    "phase": phase,
                                    "status": status,
                                    "tokens": tokens,
                                    "commit": commit,
                                },
                            )
                    backend = os.environ.get("MM_FLOW_BACKEND", "claude")
                    _write_runtime_state(
                        execution_id,
                        phase,
                        "COMPLETED",
                        0,
                        "IDLE",
                        backend,
                    )
                    archived = (
                        "archived" if run.archive_record is not None else "no_archive"
                    )
                    click.echo(
                        f"Phase {phase} marked complete execution_id:{execution_id} "
                        f"project_id:{run.project_id} "
                        f"validation_passed:{run.validation.passed} {archived}"
                    )
        finally:
            await conn.close()

    asyncio.run(_run())


@cli.command("harness-routing-check")
@click.option(
    "--config-path",
    default=None,
    help="Path to MM-Flow config (defaults to .planning/.mm-flow/config.yml)",
)
@click.option(
    "--cases-path",
    default=None,
    help="Path to routing cases YAML (defaults to harness library routing-cases.yaml)",
)
def harness_routing_check(config_path: str | None, cases_path: str | None) -> None:
    """Evaluate behavioral routing cases for the configured harness library."""
    project_root = _project_root()
    config = load_config(config_path or str(_config_path(project_root)))
    report = _evaluate_harness_routing_cases(project_root, config, cases_path)
    click.echo(json.dumps(asdict(report), indent=2))
    if not report.passed:
        raise click.ClickException("behavioral routing cases failed")


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
