"""Framework commands for MasterMind CLI."""

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
def framework():
    """Framework-level operations."""
    pass


@framework.command("status")
def framework_status():
    """Show global framework status."""
    project_root = get_project_root()
    software_dev_path = project_root / "docs" / "software-development"

    if not software_dev_path.exists():
        console.print("[red]Error: software-development directory not found[/red]")
        raise click.Abort()

    # Collect all brain data
    brains_data = []
    total_sources = 0
    total_complete = 0

    for brain_dir in sorted(software_dev_path.iterdir()):
        if not brain_dir.is_dir() or not brain_dir.name.endswith("-brain"):
            continue

        brain_name = brain_dir.name.replace("-brain", "")
        sources_dir = brain_dir / "sources"
        sources = list(sources_dir.glob("FUENTE-*.md")) if sources_dir.exists() else []

        complete_count = 0
        loaded_count = 0

        for source_file in sources:
            try:
                metadata, _ = read_yaml_frontmatter(str(source_file))
                if metadata:
                    if metadata.get("distillation_quality") == "complete":
                        complete_count += 1
                    if metadata.get("loaded_in_notebook"):
                        loaded_count += 1
            except Exception:
                pass

        brains_data.append({
            "name": brain_name,
            "sources": len(sources),
            "complete": complete_count,
            "loaded": loaded_count,
        })

        total_sources += len(sources)
        total_complete += complete_count

    # Display dashboard
    console.print(Panel.fit(
        f"[bold]MasterMind Framework[/bold]\n\n"
        f"Version: 0.1.0\n"
        f"Total Brains: {len(brains_data)}\n"
        f"Total Sources: {total_sources}\n"
        f"Complete: [green]{total_complete}[/green] ({total_complete * 100 // total_sources if total_sources > 0 else 0}%)\n"
        f"Niche: Software Development",
        title="Framework Status",
        border_style="blue"
    ))

    # Brains table
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Brain")
    table.add_column("Sources")
    table.add_column("Complete")
    table.add_column("Progress")

    for brain in brains_data:
        sources = brain["sources"]
        complete = brain["complete"]
        progress = f"[green]{complete}[/green]/{sources}" if sources > 0 else "—"

        table.add_row(
            brain["name"],
            str(sources),
            str(complete),
            progress,
        )

    console.print("\n")
    console.print(table)


@framework.command("release")
@click.option("--version", required=True, help="Version number (e.g., 0.2.0)")
@click.option("--message", default="", help="Release message")
def framework_release(version: str, message: str):
    """Create release with git tag and changelog."""
    try:
        from ..utils.git import get_repo
        from git import GitCommandError

        repo = get_repo()

        # Create annotated tag
        tag_message = f"Release {version}\n\n{message}" if message else f"Release {version}"
        repo.create_tag(version, message=tag_message)

        console.print(Panel.fit(
            f"[green]✓[/green] Release [bold]{version}[/bold] created\n\n"
            f"Tag: {version}\n"
            f"Message: {tag_message}",
            title="Release Created",
            border_style="green"
        ))

    except Exception as e:
        console.print(f"[red]Error creating release: {e}[/red]")
        raise click.Abort()
