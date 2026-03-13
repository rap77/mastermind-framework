"""
Orchestrate command for mastermind-cli.
"""

import click
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from mastermind_cli.orchestrator import Coordinator, OutputFormatter
from mastermind_cli.types import CoordinatorRequest
from pydantic import ValidationError


@click.group()
def orchestrate():
    """Orchestrate brains to process user briefs."""
    pass


@orchestrate.command()
@click.argument('brief', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read brief from file')
@click.option('--flow', type=click.Choice(['full_product', 'validation_only', 'design_sprint', 'build_feature', 'optimization', 'technical_review']), help='Force specific flow')
@click.option('--dry-run', is_flag=True, help='Generate plan without executing')
@click.option('--use-mcp', is_flag=True, help='Use MCP for real NotebookLM calls (requires Claude Code environment)')
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def run(brief, file, flow, dry_run, use_mcp, output, verbose):
    """Orchestrate brains to process user brief.

    Examples:

        \b
        # Simple validation (with mock responses)
        mm orchestrate run "validar idea de app de viajes"

        \b
        # Full product flow
        mm orchestrate run "quiero crear una app para encontrar compañeros de viaje"

        \b
        # Dry run to see plan
        mm orchestrate run --dry-run "mi idea de startup"

        \b
        # Use real NotebookLM calls (requires Claude Code + nlm CLI)
        mm orchestrate run --use-mcp "es buena idea esta app?"

        \b
        # Force specific flow
        mm orchestrate run --flow validation_only "validar mi idea"

        \b
        # Read brief from file
        mm orchestrate run --file brief.md

        \b
        # Save output to file
        mm orchestrate run -o output.yaml "mi idea"
    """
    # Get brief from file or argument
    if file:
        with open(file, 'r') as f:
            brief_text = f.read().strip()
    elif brief:
        brief_text = brief
    else:
        # Read from stdin
        brief_text = click.get_text_stream('stdin').read().strip()

    if not brief_text:
        click.echo("Error: No brief provided. Use --file, provide argument, or pipe via stdin.", err=True)
        click.echo("\nExamples:")
        click.echo("  mm orchestrate run 'your brief here'")
        click.echo("  mm orchestrate run --file brief.md")
        click.echo("  echo 'brief' | mm orchestrate run")
        raise click.Abort()

    # Change to project root directory
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    os.chdir(project_root)

    # Validate and create CoordinatorRequest (Pydantic validates constraints)
    try:
        request = CoordinatorRequest(
            brief=brief_text,
            flow=flow,
            dry_run=dry_run,
            output_file=output,
            use_mcp=use_mcp
        )
    except ValidationError as e:
        # Format validation error with context
        from mastermind_cli.utils.validation import format_validation_error_compact
        error_msg = format_validation_error_compact(e)
        click.echo(f"Validation Error: {error_msg}", err=True)
        click.echo("\nHint: Check parameter constraints (e.g., max_iterations must be 1-10)", err=True)
        raise click.Abort()

    # Show MCP status
    if request.use_mcp:
        click.echo("🔌 MCP mode enabled (requires nlm CLI)")
        if verbose:
            click.echo("   Install: https://github.com/automation-tools/nlm")
        click.echo("")

    # Create coordinator
    formatter = OutputFormatter()
    coordinator = Coordinator(formatter=formatter, use_mcp=request.use_mcp)

    # Show what we're doing
    if verbose:
        click.echo(f"📋 Brief: {request.brief[:80]}...")
        click.echo(f"🔄 Flow: {request.flow or 'auto-detect'}")
        click.echo(f"🔌 MCP: {'enabled' if request.use_mcp else 'disabled (mock mode)'}")
        click.echo("")

    try:
        # Run orchestration with validated request
        result = coordinator.orchestrate(
            brief=request.brief,
            flow=request.flow,
            dry_run=request.dry_run,
            output_file=request.output_file,
            max_iterations=request.max_iterations,
            use_mcp=request.use_mcp
        )

    except ValidationError as e:
        # Handle validation errors from @validate_call
        from mastermind_cli.utils.validation import format_validation_error_compact
        error_msg = format_validation_error_compact(e)
        click.echo(f"Runtime Validation Error: {error_msg}", err=True)
        sys.exit(1)

        # Handle result
        if result.get('status') == 'error':
            click.echo(formatter.format_error(result['error']), err=True)
            sys.exit(1)

        elif result.get('status') == 'dry_run_complete':
            # Print execution plan
            click.echo(result['output'])
            click.echo("")
            click.echo("ℹ️  Dry run complete. Use without --dry-run to execute.", err=True)

        elif result.get('status') == 'completed':
            # Results already printed during execution
            if output:
                click.echo(f"\n✅ Output saved to: {output}")

    except Exception as e:
        click.echo(formatter.format_error(f"Orchestration failed: {str(e)}"), err=True)
        if verbose:
            import traceback
            click.echo("\n" + traceback.format_exc(), err=True)
        sys.exit(1)


# Alias for shorter command
# Alias for shorter command
@orchestrate.command()
@click.argument('brief', required=False)
@click.option('--file', '-f', type=click.Path(exists=True), help='Read brief from file')
@click.option('--flow', type=click.Choice(['full_product', 'validation_only', 'design_sprint', 'build_feature', 'optimization', 'technical_review']), help='Force specific flow')
@click.option('--dry-run', is_flag=True, help='Generate plan without executing')
@click.option('--use-mcp', is_flag=True, help='Use MCP for real NotebookLM calls (requires Claude Code environment)')
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def go(brief, file, flow, dry_run, use_mcp, output, verbose):
    """Quick command to orchestrate (same as 'run')."""
    # Call the run command with the same arguments
    ctx = click.Context(run)
    run.invoke(brief, file=file, flow=flow, dry_run=dry_run, use_mcp=use_mcp, output=output, verbose=verbose)


@orchestrate.command()
@click.argument('plan_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Save output to file')
def continue_plan(plan_file, output):
    """Continue execution from a saved plan."""
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    os.chdir(project_root)

    coordinator = Coordinator()

    try:
        result = coordinator.continue_plan(
            plan_id="continued",
            plan_file=plan_file
        )

        if result.get('status') == 'error':
            click.echo(f"❌ Error: {result['error']}", err=True)
            sys.exit(1)

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)
