"""
Orchestrate command for mastermind-cli.

Updated for Pure Function Architecture (v2.0):
- Uses StatelessCoordinator (per-request instances, multi-user safe)
- API Key authentication via MM_API_KEY environment variable
- Type-safe Brief and BrainInput interfaces
"""

import asyncio
import click
import os
import sys
from typing import cast

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig,
)
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration
from mastermind_cli.brain_registry import BrainRegistry
from mastermind_cli.mm_flow.evidence_selector import (
    EvidenceClarity,
    EvidenceSelectionRequest,
    RiskLevel,
    UncertaintyLevel,
)
from pydantic import BaseModel, ValidationError


def validate_api_key(api_key: str, db_path: str) -> str | None:
    """Validate a CLI API key against the canonical `/api/keys` store."""
    from mastermind_cli.api.routes.keys import validate_api_key_v2

    return asyncio.run(validate_api_key_v2(api_key, db_path))


def execute_flow_sync(
    coordinator: StatelessCoordinator,
    brief_model: Brief,
    brain_ids: list[str],
    parallel_mode: bool,
    evidence_request: EvidenceSelectionRequest | None = None,
) -> dict[str, BaseModel]:
    """Execute the orchestration flow from synchronous CLI code."""

    async def _execute() -> dict[str, BaseModel]:
        if parallel_mode:
            return await coordinator.execute_flow(
                brief_model,
                brain_ids,
                evidence_request=evidence_request,
            )

        seq_results: dict[str, BaseModel] = {}
        for brain_id in brain_ids:
            brain_results = await coordinator.execute_flow(
                brief_model,
                [brain_id],
                evidence_request=evidence_request,
            )
            seq_results.update(brain_results)
        return seq_results

    return asyncio.run(_execute())


@click.group()
def orchestrate() -> None:
    """Orchestrate brains to process user briefs."""
    pass


@orchestrate.command()
@click.argument("brief", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read brief from file")
@click.option(
    "--brains",
    "-b",
    help="Comma-separated list of brain IDs (e.g., brain-01-product-strategy,brain-02-ux-research)",
)
@click.option("--dry-run", is_flag=True, help="Generate plan without executing")
@click.option(
    "--use-mcp",
    is_flag=True,
    help="Use MCP for real NotebookLM calls (requires nlm CLI)",
)
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option(
    "--parallel/--no-parallel",
    default=True,
    help="Execute independent brains in parallel (default: True)",
)
@click.option(
    "--evidence-objective",
    default=None,
    help="Optional evidence objective to activate evidence routing",
)
@click.option(
    "--evidence-source-clarity",
    type=click.Choice(["clear", "partial", "ambiguous"]),
    default="partial",
    show_default=True,
)
@click.option(
    "--evidence-uncertainty",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    show_default=True,
)
@click.option("--evidence-gap-count", type=int, default=0, show_default=True)
@click.option("--evidence-needs-interview", is_flag=True)
@click.option(
    "--evidence-risk-level",
    type=click.Choice(["low", "medium", "high", "critical"]),
    default="medium",
    show_default=True,
)
@click.option("--evidence-readiness-gate", default=None)
@click.option("--evidence-readiness-score", type=float, default=None)
def run(
    brief: str | None,
    file: str | None,
    brains: str | None,
    dry_run: bool,
    use_mcp: bool,
    output: str | None,
    verbose: bool,
    parallel: bool,
    evidence_objective: str | None,
    evidence_source_clarity: str,
    evidence_uncertainty: str,
    evidence_gap_count: int,
    evidence_needs_interview: bool,
    evidence_risk_level: str,
    evidence_readiness_gate: str | None,
    evidence_readiness_score: float | None,
) -> None:
    """Orchestrate brains to process user brief (Pure Function Architecture v2.0).

    \b
    Examples:
        # Simple orchestration (auto-detect brains)
        mm orchestrate run "Build a CRM for small businesses"

        \b
        # Specific brains
        mm orchestrate run --brains brain-01-product-strategy "My startup idea"

        \b
        # Use MCP (real NotebookLM calls)
        mm orchestrate run --use-mcp "Validate my SaaS idea"

        \b
        # Read brief from file
        mm orchestrate run --file brief.md

        \b
        # Save output to file
        mm orchestrate run -o output.json "My idea"

    \b
    Environment Variables:
        MM_API_KEY  API key for authentication (required for CLI usage)
    """
    # ========================================================================
    # 1. VALIDATE API KEY
    # ========================================================================
    api_key = os.getenv("MM_API_KEY")
    if not api_key:
        raise ValueError(
            "MM_API_KEY environment variable not set.\n"
            "Set your API key:\n"
            "  export MM_API_KEY='your-api-key-here'\n"
            "Create a new key via the standard /api/keys flow."
        )

    # Validate API key
    db_path = os.getenv("MM_DB_PATH", "mastermind.db")
    validated_user_id = validate_api_key(api_key, db_path)
    if validated_user_id is None:
        raise ValueError(
            "Invalid API key.\n"
            "Your MM_API_KEY is not valid in the standard /api/keys flow."
        )

    # ========================================================================
    # 2. GET BRIEF TEXT
    # ========================================================================
    if file:
        with open(file, "r") as f:
            brief_text = f.read().strip()
    elif brief:
        brief_text = brief
    else:
        brief_text = click.get_text_stream("stdin").read().strip()

    if not brief_text:
        raise ValueError(
            "No brief provided. Use --file, provide argument, or pipe via stdin.\n"
            "Examples:\n"
            "  mm orchestrate run 'your brief here'\n"
            "  mm orchestrate run --file brief.md\n"
            "  echo 'brief' | mm orchestrate run"
        )

    # ========================================================================
    # 3. CREATE BRIEF MODEL (Pydantic validation)
    # ========================================================================
    try:
        brief_model = Brief(
            problem_statement=brief_text, context="", target_audience=None
        )
    except ValidationError as e:
        raise ValueError(
            f"Validation Error: {e}\n"
            "Hint: Brief must have at least 3 words and 10 characters"
        )

    # ========================================================================
    # 4. DETERMINE WHICH BRAINS TO EXECUTE
    # ========================================================================
    if brains:
        brain_ids = [b.strip() for b in brains.split(",")]
    else:
        # Auto-detect based on brief content (simple heuristic for now)
        # In production, Brain #8 (Master Interviewer) would determine this
        brain_ids = ["brain-01-product-strategy", "brain-02-ux-research"]
        if verbose:
            click.echo(f"ℹ️  Auto-detected brains: {', '.join(brain_ids)}")

    # ========================================================================
    # 5. CREATE STATELESS COORDINATOR (per-request instance)
    # ========================================================================
    # Change to project root directory
    project_root = os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    )
    os.chdir(project_root)

    # Create MCP client (MCPIntegration implements the MCPClient protocol)
    mcp_integration = MCPIntegration(use_mcp=use_mcp)

    # Wrap in TypeSafeMCPWrapper for protocol compliance
    from ..orchestrator.mcp_wrapper import TypeSafeMCPWrapper

    mcp_client = TypeSafeMCPWrapper(mcp_integration)

    # Create coordinator config
    config = CoordinatorConfig(
        mcp_client=mcp_client, enable_logging=verbose, brain_registry=BrainRegistry()
    )

    # Create NEW coordinator instance for this request (stateless)
    coordinator = StatelessCoordinator(config)

    # ========================================================================
    # 6. SHOW EXECUTION PLAN
    # ========================================================================
    if verbose:
        click.echo(f"📋 Brief: {brief_model.problem_statement[:80]}...")
        click.echo(f"🧠 Brains: {', '.join(brain_ids)}")
        click.echo(f"🔌 MCP: {'enabled' if use_mcp else 'disabled (mock mode)'}")
        click.echo(f"⚡ Parallel: {'enabled' if parallel else 'disabled (sequential)'}")
        click.echo(f"👤 Auth: {validated_user_id}")
        click.echo("")

    if dry_run:
        click.echo("📋 Execution Plan:")
        click.echo(f"  Brief: {brief_model.problem_statement[:60]}...")
        click.echo(f"  Brains ({len(brain_ids)}):")
        for brain_id in brain_ids:
            click.echo(f"    - {brain_id}")
        click.echo("")
        click.echo("ℹ️  Dry run complete. Use without --dry-run to execute.")
        return

    evidence_request = None
    if evidence_objective is not None:
        evidence_request = EvidenceSelectionRequest(
            objective=evidence_objective,
            source_clarity=cast(EvidenceClarity, evidence_source_clarity),
            uncertainty=cast(UncertaintyLevel, evidence_uncertainty),
            gap_count=evidence_gap_count,
            needs_interview=evidence_needs_interview,
            risk_level=cast(RiskLevel, evidence_risk_level),
            readiness_gate=evidence_readiness_gate,
            readiness_score=evidence_readiness_score,
        )

    try:
        results = execute_flow_sync(
            coordinator=coordinator,
            brief_model=brief_model,
            brain_ids=brain_ids,
            parallel_mode=parallel,
            evidence_request=evidence_request,
        )

        # ====================================================================
        # 8. DISPLAY RESULTS
        # ====================================================================
        click.echo("")
        click.echo("✅ Execution Complete")
        click.echo("=" * 60)

        for brain_id, brain_output in results.items():
            click.echo(f"\n🧠 {brain_id}")
            click.echo("-" * 60)
            # Pretty print the output
            if not isinstance(brain_output, BaseModel):
                click.echo(f"  {brain_output}")
                continue
            output_dict = brain_output.model_dump()
            for key, value in output_dict.items():
                if key == "generated_at":
                    continue  # Skip timestamp
                if isinstance(value, list):
                    click.echo(f"  {key}:")
                    for item in value:
                        click.echo(f"    - {item}")
                elif isinstance(value, dict):
                    click.echo(f"  {key}: {value}")
                else:
                    click.echo(f"  {key}: {value}")

        # Save to file if requested
        if output:
            import json
            from pathlib import Path

            # Convert results to dict
            results_dict = {
                brain_id: brain_output.model_dump()
                for brain_id, brain_output in results.items()
            }

            output_path = Path(output)
            if output_path.suffix == ".json":
                with open(output_path, "w") as f:
                    json.dump(results_dict, f, indent=2, default=str)
            elif output_path.suffix in [".yaml", ".yml"]:
                import yaml

                with open(output_path, "w") as f:
                    yaml.dump(results_dict, f, default_flow_style=False)
            else:
                # Default to JSON
                with open(output_path, "w") as f:
                    json.dump(results_dict, f, indent=2, default=str)

            click.echo(f"\n✅ Output saved to: {output}")

    except ValidationError as e:
        click.echo(f"❌ Runtime Validation Error: {e}", err=True)
        sys.exit(1)
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        if verbose:
            import traceback

            click.echo("\n" + traceback.format_exc(), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"❌ Orchestration failed: {str(e)}", err=True)
        if verbose:
            import traceback

            click.echo("\n" + traceback.format_exc(), err=True)
        sys.exit(1)


# Alias for shorter command
@orchestrate.command()
@click.argument("brief", required=False)
@click.option("--file", "-f", type=click.Path(exists=True), help="Read brief from file")
@click.option("--brains", "-b", help="Comma-separated list of brain IDs")
@click.option("--dry-run", is_flag=True, help="Generate plan without executing")
@click.option("--use-mcp", is_flag=True, help="Use MCP for real NotebookLM calls")
@click.option("--output", "-o", type=click.Path(), help="Save output to file")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option(
    "--parallel/--no-parallel",
    default=True,
    help="Execute brains in parallel (default: True)",
)
def go(
    brief: str | None,
    file: str | None,
    brains: str | None,
    dry_run: bool,
    use_mcp: bool,
    output: str | None,
    verbose: bool,
    parallel: bool,
) -> None:
    """Quick command to orchestrate (alias for 'run')."""
    run_callback = run.callback
    if run_callback is None:
        raise RuntimeError("run callback is unavailable")
    run_callback(
        brief=brief,
        file=file,
        brains=brains,
        dry_run=dry_run,
        use_mcp=use_mcp,
        output=output,
        verbose=verbose,
        parallel=parallel,
        evidence_objective=None,
        evidence_source_clarity="partial",
        evidence_uncertainty="medium",
        evidence_gap_count=0,
        evidence_needs_interview=False,
        evidence_risk_level="medium",
        evidence_readiness_gate=None,
        evidence_readiness_score=None,
    )
