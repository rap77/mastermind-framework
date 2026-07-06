"""Memory commands for MasterMind CLI."""

from __future__ import annotations

import click

from mastermind_cli.memory_layer.migrate import upgrade_to_head


@click.group()
def memory() -> None:
    """Manage memory-layer operations."""
    pass


@memory.command("migrate")
def memory_migrate() -> None:
    """Apply memory-layer database migrations."""
    applied = upgrade_to_head()
    if applied:
        click.echo(f"Applied {len(applied)} migration(s): {', '.join(applied)}")
    else:
        click.echo("No new migrations to apply.")
