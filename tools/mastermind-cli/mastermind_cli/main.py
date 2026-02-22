"""MasterMind Framework CLI - Main entry point."""

import click
from rich.console import Console
from rich import print as rprint
from rich.panel import Panel

from . import __version__
from .commands.source import source
from .commands.brain import brain
from .commands.framework import framework

console = Console()


@click.group()
@click.version_option(version=__version__)
def cli():
    """
    MasterMind Framework - AI-powered expert brains.

    Manage sources, brains, and framework operations.
    """
    pass


# Register command groups
cli.add_command(source)
cli.add_command(brain)
cli.add_command(framework)


@cli.command()
def info():
    """Show framework information."""
    console.print(Panel.fit(
        """
[bold cyan]MasterMind Framework[/bold cyan]

[bold]Version:[/bold] 0.1.0
[bold]Description:[/bold] AI-powered expert brains

[bold]Quick Start:[/bold]

  mastermind source list           List all sources
  mastermind brain status <id>      Show brain status
  mastermind framework status       Show framework status

[bold]Documentation:[/bold]

  https://github.com/rap77/mastermind-framework
        """,
        title="MasterMind Framework",
        border_style="cyan"
    ))


if __name__ == "__main__":
    cli()
