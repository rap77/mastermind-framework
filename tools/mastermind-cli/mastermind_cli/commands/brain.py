"""Brain commands for MasterMind CLI."""

from pathlib import Path
from typing import Dict, List

import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import print as rprint

from ..utils.yaml import read_yaml_frontmatter

console = Console()


def get_project_root() -> Path:
    """Get the MasterMind project root directory."""
    current = Path.cwd()
    markers = ["CLAUDE.md", "docs/design/00-PRD-MasterMind-Framework.md"]
    for parent in [current] + list(current.parents):
        for marker in markers:
            if (parent / marker).exists():
                return parent
    return current


@click.group()
def brain():
    """Manage brain configuration."""
    pass


@brain.command("status")
@click.argument("brain_id")
def brain_status(brain_id: str):
    """Show complete brain status."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        console.print(f"\n[yellow]Available brains:[/yellow]")
        for d in (project_root / "docs" / "software-development").iterdir():
            if d.is_dir() and d.name.endswith("-brain"):
                console.print(f"  • {d.name.replace('-brain', '')}")
        raise click.Abort()

    sources_dir = brain_path / "sources"
    sources = list(sources_dir.glob("FUENTE-*.md")) if sources_dir.exists() else []

    # Collect metadata from sources
    all_skills = set()
    quality_stats = {"complete": 0, "partial": 0, "pending": 0}
    loaded_count = 0
    experts = set()

    for source_file in sources:
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                skills = metadata.get("skills_covered", [])
                all_skills.update(skills)

                quality = metadata.get("distillation_quality", "pending")
                if quality in quality_stats:
                    quality_stats[quality] += 1

                if metadata.get("loaded_in_notebook"):
                    loaded_count += 1

                expert_id = metadata.get("expert_id")
                if expert_id:
                    experts.add(expert_id)
        except Exception:
            pass

    # Display status
    console.print(Panel.fit(
        f"[bold]{brain_id}[/bold]\n\n"
        f"Sources: {len(sources)}\n"
        f"Experts: {len(experts)}\n"
        f"Skills Covered: {len(all_skills)}\n"
        f"Loaded in Notebook: {loaded_count}/{len(sources)}",
        title=f"Brain Status: {brain_id}",
        border_style="blue"
    ))

    # Sources table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Source ID")
    table.add_column("Title")
    table.add_column("Author")
    table.add_column("Quality")

    for source_file in sources:
        try:
            metadata, _ = read_yaml_frontmatter(str(source_file))
            if metadata:
                quality = metadata.get("distillation_quality", "pending")
                quality_color = "green" if quality == "complete" else "yellow"

                table.add_row(
                    metadata.get("source_id", "—"),
                    metadata.get("title", "—")[:30],
                    metadata.get("author", "—"),
                    f"[{quality_color}]{quality}[/{quality_color}]",
                )
        except Exception:
            pass

    console.print("\n")
    console.print(table)


@brain.command("validate")
@click.argument("brain_id")
def brain_validate(brain_id: str):
    """Validate brain for gaps and completeness."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        raise click.Abort()

    from ..utils.validation import validate_brain_sources

    results = validate_brain_sources(str(brain_path))

    if not results:
        console.print(f"[yellow]No sources found to validate[/yellow]")
        return

    # Count issues
    total_errors = sum(len(r.errors) for r in results.values())
    total_warnings = sum(len(r.warnings) for r in results.values())
    valid_count = sum(1 for r in results.values() if r.is_valid)

    console.print(Panel.fit(
        f"Total Sources: {len(results)}\n"
        f"Valid: [green]{valid_count}[/green]\n"
        f"Errors: [red]{total_errors}[/red]\n"
        f"Warnings: [yellow]{total_warnings}[/yellow]",
        title=f"Validation: {brain_id}",
        border_style="green" if total_errors == 0 else "red"
    ))

    if total_errors > 0:
        console.print("\n[red]Sources with errors:[/red]")
        for filename, result in results.items():
            if result.errors:
                console.print(f"  • {filename}: {len(result.errors)} errors")


@brain.command("package")
@click.argument("brain_id")
@click.option("--output", default="dist/packages", help="Output directory")
def brain_package(brain_id: str, output: str):
    """Package brain for distribution."""
    project_root = get_project_root()
    brain_path = project_root / "docs" / "software-development" / f"{brain_id}-brain"
    output_dir = project_root / output

    if not brain_path.exists():
        console.print(f"[red]Error: Brain not found: {brain_id}[/red]")
        raise click.Abort()

    output_dir.mkdir(parents=True, exist_ok=True)

    # For now, just count files (full packaging in future PRP)
    sources_dir = brain_path / "sources"
    sources = list(sources_dir.glob("FUENTE-*.md")) if sources_dir.exists() else []

    console.print(Panel.fit(
        f"[bold]{brain_id}[/bold]\n\n"
        f"Sources: {len(sources)}\n"
        f"Output: {output_dir}\n\n"
        f"[dim](Full packaging coming in future PRP)[/dim]",
        title="Brain Package",
        border_style="blue"
    ))
