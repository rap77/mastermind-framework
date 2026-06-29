"""
Tests for the mm_flow CLI module — environment validation and runtime-state atomic writes.

Note: high-level lifecycle coverage (start/complete) lives in
`test_mm_flow_cli_bridge.py`. This file focuses on cross-cutting CLI
contracts that don't depend on the unified harness run executor.
"""

import json
import stat
from pathlib import Path

import pytest
from click.testing import CliRunner

from mastermind_cli.mm_flow.cli import cli
from mastermind_cli.mm_flow.config_loader import RuntimeState


# ---------------------------------------------------------------------------
# Environment validation
# ---------------------------------------------------------------------------


class TestEnvironmentValidation:
    """Tests for required environment variables (DATABASE_URL)."""

    def test_missing_database_url_raises_usage_error(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """DATABASE_URL environment variable must be set (no default)."""
        runner = CliRunner()
        monkeypatch.delenv("DATABASE_URL", raising=False)
        result = runner.invoke(
            cli,
            [
                "run-phase",
                "--phase",
                "19",
                "--brief",
                "x",
                "--brain-ids",
                "y",
            ],
        )
        assert result.exit_code != 0
        assert "DATABASE_URL" in str(result.exception)
        assert "environment variable" in str(result.exception).lower()
        assert "export" in str(result.exception) or "postgresql://" in str(
            result.exception
        )


# ---------------------------------------------------------------------------
# Atomic write guarantee (C2)
# ---------------------------------------------------------------------------


class TestAtomicWriteGuarantee:
    """Tests for atomic write behavior of RuntimeState."""

    def test_atomic_write_round_trips_state(self, tmp_path: Path) -> None:
        """`to_json_file` produces a readable file whose contents round-trip cleanly."""
        runtime_path = tmp_path / "runtime-state.json"
        state = RuntimeState(
            execution_id="test-id",
            phase=19,
            current_moment="EXECUTION_WAVE",
            active_brain=0,
            brain_state="ACTIVE",
            backend="claude",
            updated_at="2026-04-14T00:00:00",
        )

        state.to_json_file(runtime_path)

        assert runtime_path.exists()
        payload = json.loads(runtime_path.read_text())
        assert payload["execution_id"] == "test-id"
        assert payload["phase"] == 19
        assert payload["current_moment"] == "EXECUTION_WAVE"
        assert payload["backend"] == "claude"

    def test_atomic_write_creates_parent_directories(self, tmp_path: Path) -> None:
        """Atomic write creates parent directories when they don't exist."""
        runtime_path = tmp_path / "nested" / "dir" / "runtime-state.json"
        state = RuntimeState(
            execution_id="test-id",
            phase=19,
            current_moment="EXECUTION_WAVE",
            active_brain=0,
            brain_state="ACTIVE",
            backend="claude",
            updated_at="2026-04-14T00:00:00",
        )
        state.to_json_file(runtime_path)
        assert runtime_path.exists()
        assert runtime_path.parent.exists()

    def test_atomic_write_sets_explicit_permissions(self, tmp_path: Path) -> None:
        """Atomic write sets 0o644 permissions on the resulting file."""
        runtime_path = tmp_path / "runtime-state.json"
        state = RuntimeState(
            execution_id="test-id",
            phase=19,
            current_moment="EXECUTION_WAVE",
            active_brain=0,
            brain_state="ACTIVE",
            backend="claude",
            updated_at="2026-04-14T00:00:00",
        )
        state.to_json_file(runtime_path)
        file_mode = runtime_path.stat().st_mode
        assert stat.filemode(file_mode) == "-rw-r--r--"
        assert (file_mode & 0o777) == 0o644

    def test_atomic_write_rejects_path_traversal(self, tmp_path: Path) -> None:
        """Atomic write rejects paths containing '..'."""
        state = RuntimeState(
            execution_id="test-id",
            phase=19,
            current_moment="EXECUTION_WAVE",
            active_brain=0,
            brain_state="ACTIVE",
            backend="claude",
            updated_at="2026-04-14T00:00:00",
        )
        with pytest.raises(ValueError, match="path traversal"):
            state.to_json_file(tmp_path / ".." / "runtime-state.json")

        absolute_path = tmp_path / "absolute-runtime-state.json"
        state.to_json_file(absolute_path)
        assert absolute_path.exists()
