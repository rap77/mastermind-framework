"""Tests for runtime state writer fallback behavior."""

from __future__ import annotations

from pathlib import Path

import pytest

from mastermind_cli.mm_flow.runtime_state_writer import extract_state_from_state_md


def test_extract_state_logs_invalid_phase_and_defaults_to_zero(
    tmp_path: Path, caplog: pytest.LogCaptureFixture
) -> None:
    """Invalid numeric fields should be logged and defaulted."""
    caplog.set_level("DEBUG")
    state_md = tmp_path / "STATE.md"
    state_md.write_text(
        "\n".join(
            [
                "current_phase: not-a-number",
                "milestone: Alpha",
                "overall_status: OK",
                "plan_abc: WIP",
            ]
        ),
        encoding="utf-8",
    )

    state = extract_state_from_state_md(state_md)

    assert state["current_phase"] == 0
    assert state["active_plan"] == 0
    assert "Invalid current_phase in STATE.md" in caplog.text
