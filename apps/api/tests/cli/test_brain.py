"""Tests for brain CLI commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from mastermind_cli.commands.brain import brain_status


def test_brain_status_logs_source_parse_failures(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """brain status should warn when a source file cannot be parsed."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    source_file = sources_dir / "FUENTE-001.md"
    source_file.write_text(
        """---
invalid: yaml: content:
    broken: [
---

# Content
"""
    )

    caplog.set_level("WARNING")

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        brain_status.callback("brain-01")

    assert str(source_file) in caplog.text
