"""Tests for memory CLI commands."""

from __future__ import annotations

from click.testing import CliRunner
import pytest

from mastermind_cli.commands.memory import memory
from mastermind_cli.main import cli


def test_memory_migrate_invokes_upgrade_and_reports_result(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The memory migrate command should call the migration helper."""
    captured: dict[str, object] = {}

    def fake_upgrade_to_head(database_url: str = "postgresql://fallback") -> list[str]:
        captured["database_url"] = database_url
        return ["0001_create_memory_tables"]

    monkeypatch.setattr(
        "mastermind_cli.commands.memory.upgrade_to_head",
        fake_upgrade_to_head,
    )

    result = CliRunner().invoke(memory, ["migrate"])

    assert result.exit_code == 0
    assert "Applied 1 migration(s): 0001_create_memory_tables" in result.output
    assert captured["database_url"] == "postgresql://fallback"


def test_memory_group_is_registered_on_root_cli(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The root CLI should expose the memory migrate command."""
    monkeypatch.setattr(
        "mastermind_cli.commands.memory.upgrade_to_head",
        lambda database_url="postgresql://fallback": [],
    )

    result = CliRunner().invoke(cli, ["memory", "migrate"])

    assert result.exit_code == 0
    assert "No new migrations to apply." in result.output
