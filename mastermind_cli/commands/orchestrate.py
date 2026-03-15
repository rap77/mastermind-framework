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

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mastermind_cli.types.interfaces import Brief
from mastermind_cli.orchestrator.stateless_coordinator import (
    StatelessCoordinator,
    CoordinatorConfig,
)
from mastermind_cli.orchestrator.mcp_integration import MCPIntegration
from mastermind_cli.auth.api_keys import validate_api_key
from mastermind_cli.brain_registry import BrainRegistry
from pydantic import BaseModel, ValidationError


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
def run(
    brief: str | None,
    file: str | None,
    brains: str | None,
    dry_run: bool,
    use_mcp: bool,
    output: str | None,
    verbose: bool,
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
        click.echo("❌ Error: MM_API_KEY environment variable not set", err=True)
        click.echo("\nSet your API key:", err=True)
        click.echo("  export MM_API_KEY='your-api-key-here'", err=True)
        click.echo("\nGenerate a new key:", err=True)
        click.echo("  mm auth create-key", err=True)
        raise click.Abort()

    # Validate API key
    validated_key = validate_api_key(api_key)
    if not validated_key:
        click.echo("❌ Error: Invalid API key", err=True)
        click.echo("\nYour MM_API_KEY is not valid. Generate a new key:", err=True)
        click.echo("  mm auth create-key", err=True)
        raise click.Abort()

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
        click.echo(
            "❌ Error: No brief provided. Use --file, provide argument, or pipe via stdin.",
            err=True,
        )
        click.echo("\nExamples:")
        click.echo("  mm orchestrate run 'your brief here'")
        click.echo("  mm orchestrate run --file brief.md")
        click.echo("  echo 'brief' | mm orchestrate run")
        raise click.Abort()

    # ========================================================================
    # 3. CREATE BRIEF MODEL (Pydantic validation)
    # ========================================================================
    try:
        brief_model = Brief(
            problem_statement=brief_text, context="", target_audience=None
        )
    except ValidationError as e:
        click.echo(f"❌ Validation Error: {e}", err=True)
        click.echo(
            "\nHint: Brief must have at least 3 words and 10 characters", err=True
        )
        raise click.Abort()

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
        click.echo(f"👤 Auth: {validated_key.owner}")
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

    # ========================================================================
    # 7. EXECUTE FLOW (async - run in event loop)
    # ========================================================================
    try:
        results = asyncio.run(coordinator.execute_flow(brief_model, brain_ids))

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
def go(
    brief: str | None,
    file: str | None,
    brains: str | None,
    dry_run: bool,
    use_mcp: bool,
    output: str | None,
    verbose: bool,
) -> None:
    """Quick command to orchestrate (alias for 'run')."""
    # Forward all arguments to the run command
    args_list: list[str | None] = [
        brief or None,
        "--file" if file else None,
        file or None,
        "--brains" if brains else None,
        brains or None,
        "--dry-run" if dry_run else None,
        "--use-mcp" if use_mcp else None,
        "--output" if output else None,
        output or None,
        "--verbose" if verbose else None,
    ]
    # Flatten arguments and filter out None values
    filtered_args: list[str] = [arg for arg in args_list if arg is not None]
    # Remove flags that don't need values
    filtered_args = [
        arg for arg in filtered_args if arg not in ("--file", "--brains", "--output")
    ]
    # Invoke with context
    ctx = run.make_context("run", filtered_args)
    run.invoke(ctx)
