"""Evaluation CLI commands."""

import click
from pathlib import Path
import yaml

from mastermind_cli.memory import EvaluationLogger


@click.group()
def evaluation():
    """Manage and search stored evaluations."""
    pass


@evaluation.command()
@click.option("--limit", default=10, help="Number of evaluations to show", type=int)
@click.option("--verbose", "-v", is_flag=True, help="Show detailed output")
def list(limit: int, verbose: bool):
    """List recent evaluations."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    evaluations = logger.find_recent(limit)

    if not evaluations:
        click.echo("No evaluations found.")
        return

    click.echo(f"\n📋 Recent evaluations (showing {len(evaluations)}):\n")

    for eval in evaluations:
        # Color based on verdict
        verdict_colors = {
            "APPROVE": "green",
            "CONDITIONAL": "yellow",
            "REJECT": "red",
            "ESCALATE": "blue",
        }
        color = verdict_colors.get(eval.verdict.value, "white")

        click.echo(f"📌 {eval.evaluation_id}")
        click.echo(f"   📅 {eval.timestamp.strftime('%Y-%m-%d %H:%M')}")
        click.echo(f"   📁 Project: {eval.project}")
        click.echo(f"   🔄 Flow: {eval.flow_type}")

        if verbose:
            click.echo(f"   Score: {eval.score}")
        else:
            click.secho("   Verdict: ", nl=False)
            click.secho(f"{eval.verdict.value}", fg=color)

        # Show tags if present
        if eval.tags:
            click.echo(f"   🏷️  Tags: {', '.join(eval.tags[:5])}")

        # Show brief preview
        brief_preview = eval.brief[:60] + "..." if len(eval.brief) > 60 else eval.brief
        click.echo(f"   💬 {brief_preview}")

        # Show issues count
        if eval.issues_found:
            severity_count = {}
            for issue in eval.issues_found:
                severity_count[issue.severity] = severity_count.get(issue.severity, 0) + 1
            if severity_count:
                issues_str = ", ".join([f"{k}:{v}" for k, v in severity_count.items()])
                click.echo(f"   ⚠️  Issues: {issues_str}")

        click.echo()


@evaluation.command()
@click.argument("evaluation_id")
def show(evaluation_id: str):
    """Show detailed evaluation."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    eval_entry = logger.find_by_id(evaluation_id)

    if not eval_entry:
        click.echo(f"Evaluation '{evaluation_id}' not found.", err=True)
        return

    # Header
    click.echo(f"\n{'='*60}")
    click.echo(f"📋 {eval_entry.evaluation_id}")
    click.echo(f"{'='*60}\n")

    # Metadata
    click.echo(f"📅 Date: {eval_entry.timestamp.strftime('%Y-%m-%d %H:%M:%S')} UTC")
    click.echo(f"📁 Project: {eval_entry.project}")
    click.echo(f"🔄 Flow Type: {eval_entry.flow_type}")
    click.echo(f"🧠 Brains Involved: {', '.join([f'#{b}' for b in eval_entry.brains_involved])}")

    # Verdict with color
    verdict_colors = {
        "APPROVE": "green",
        "CONDITIONAL": "yellow",
        "REJECT": "red",
        "ESCALATE": "blue",
    }
    color = verdict_colors.get(eval_entry.verdict.value, "white")

    click.echo("\n--- Verdict ---")
    click.secho(f"Verdict: {eval_entry.verdict.value}", fg=color, bold=True)
    click.echo(f"Score: {eval_entry.score}")

    # Brief
    click.echo("\n--- Brief ---")
    click.echo(eval_entry.brief)

    # Issues
    if eval_entry.issues_found:
        click.echo(f"\n--- Issues Found ({len(eval_entry.issues_found)}) ---")
        for i, issue in enumerate(eval_entry.issues_found, 1):
            severity_colors = {"high": "red", "medium": "yellow", "low": "blue"}
            sev_color = severity_colors.get(issue.severity, "white")

            click.echo(f"\n{i}. {issue.type}")
            click.secho(f"   [{issue.severity.upper()}]", fg=sev_color, nl=False)
            click.echo(f" {issue.description}")
            click.echo(f"   💡 {issue.recommendation}")

    # Strengths
    if eval_entry.strengths_found:
        click.echo(f"\n--- Strengths ({len(eval_entry.strengths_found)}) ---")
        for strength in eval_entry.strengths_found:
            click.echo(f"  ✓ {strength}")

    # Tags
    if eval_entry.tags:
        click.echo("\n--- Tags ---")
        click.echo(f"  {', '.join(eval_entry.tags)}")

    # Full output
    if eval_entry.full_output:
        click.echo("\n--- Full Evaluation Output ---")
        click.echo(eval_entry.full_output)

    click.echo()


@evaluation.command()
@click.argument("project")
@click.option("--limit", default=20, help="Max evaluations to show", type=int)
def find(project: str, limit: int):
    """Find evaluations by project."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    evaluations = logger.find_by_project(project)

    if not evaluations:
        click.echo(f"No evaluations found for project '{project}'.")
        return

    # Apply limit
    evaluations = evaluations[:limit]

    click.echo(f"\n📋 Found {len(evaluations)} evaluations for '{project}':\n")

    for eval in evaluations:
        verdict_colors = {
            "APPROVE": "green",
            "CONDITIONAL": "yellow",
            "REJECT": "red",
            "ESCALATE": "blue",
        }
        color = verdict_colors.get(eval.verdict.value, "white")

        click.echo(f"  {eval.evaluation_id} | ", nl=False)
        click.secho(f"{eval.verdict.value}", fg=color, nl=False)
        click.echo(f" | {eval.timestamp.strftime('%Y-%m-%d')} | {eval.score}")

        # Show brief preview
        brief_preview = eval.brief[:50] + "..." if len(eval.brief) > 50 else eval.brief
        click.echo(f"  💬 {brief_preview}")
        click.echo()


@evaluation.command()
@click.argument("query")
@click.option("--limit", default=10, help="Max results to show", type=int)
def search(query: str, limit: int):
    """Search evaluations by keyword."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    evaluations = logger.search(query)

    if not evaluations:
        click.echo(f"No evaluations found matching '{query}'.")
        return

    # Apply limit
    evaluations = evaluations[:limit]

    click.echo(f"\n📋 Found {len(evaluations)} evaluations matching '{query}':\n")

    for eval in evaluations:
        verdict_colors = {
            "APPROVE": "green",
            "CONDITIONAL": "yellow",
            "REJECT": "red",
            "ESCALATE": "blue",
        }
        color = verdict_colors.get(eval.verdict.value, "white")

        click.echo(f"  {eval.evaluation_id} | ", nl=False)
        click.secho(f"{eval.verdict.value}", fg=color, nl=False)
        click.echo(f" | {eval.project}")
        click.echo(f"  💬 {eval.brief[:80]}...")
        click.echo()


@evaluation.command()
@click.option("--verdict", "-v", help="Filter by verdict", type=click.Choice(["APPROVE", "CONDITIONAL", "REJECT", "ESCALATE"]))
def stats(verdict: str):
    """Show evaluation statistics."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    stats = logger.get_stats()

    click.echo("\n📊 Evaluation Statistics\n")
    click.echo(f"{'='*40}")

    if stats.get("total_evaluations", 0) == 0:
        click.echo("No evaluations recorded yet.")
        return

    click.echo(f"Total Evaluations: {stats['total_evaluations']}")
    click.echo(f"Storage Path: {stats.get('storage_path', 'N/A')}")

    # Verdict breakdown
    verdict_breakdown = stats.get("verdict_breakdown", {})
    if verdict_breakdown:
        click.echo("\nVerdict Breakdown:")
        for v, count in verdict_breakdown.items():
            color = {
                "APPROVE": "green",
                "CONDITIONAL": "yellow",
                "REJECT": "red",
                "ESCALATE": "blue",
            }.get(v, "white")
            click.secho(f"  {v}: {count}", fg=color)

    # Top projects
    top_projects = stats.get("top_projects", {})
    if top_projects:
        click.echo("\nTop Projects:")
        for project, count in list(top_projects.items())[:5]:
            click.echo(f"  {project}: {count}")

    click.echo()


@evaluation.command()
@click.argument("evaluation_id")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def export(evaluation_id: str, output: str):
    """Export evaluation to YAML file."""
    logger = EvaluationLogger()

    if not logger.enabled:
        click.echo("Evaluation logging is not enabled.", err=True)
        return

    eval_entry = logger.find_by_id(evaluation_id)

    if not eval_entry:
        click.echo(f"Evaluation '{evaluation_id}' not found.", err=True)
        return

    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = Path(f"{evaluation_id}.yaml")

    # Export
    with open(output_path, "w", encoding="utf-8") as f:
        yaml.dump(eval_entry.to_dict(), f, default_flow_style=False, allow_unicode=True)

    click.echo(f"✅ Exported to {output_path}")
