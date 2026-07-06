"""Tests for source command fallbacks."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.commands import source as source_cmd


def test_source_update_logs_git_commit_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    """Git commit failures should not abort the source update flow."""
    outputs: list[str] = []

    class _Console:
        def print(self, message: str) -> None:
            outputs.append(str(message))

    monkeypatch.setattr(source_cmd, "console", lambda: _Console())
    monkeypatch.setattr(source_cmd, "get_project_root", lambda: Path("/repo"))
    monkeypatch.setattr(
        source_cmd,
        "find_sources_by_id",
        lambda source_id, search_paths: ["/repo/docs/source.md"],
    )
    monkeypatch.setattr(
        source_cmd,
        "read_yaml_frontmatter",
        lambda source_file: (
            {"version": "1.0.0", "changelog": []},
            "# content",
        ),
    )
    monkeypatch.setattr(source_cmd, "update_yaml_metadata", lambda *args, **kwargs: {})
    monkeypatch.setattr(
        source_cmd,
        "git_commit",
        lambda *args, **kwargs: (_ for _ in ()).throw(ValueError("boom")),
    )

    source_cmd.source_update.callback("SOURCE-001", "fix docs")

    assert any("Could not create git commit" in line for line in outputs)
    assert any("Source updated" in line for line in outputs)
