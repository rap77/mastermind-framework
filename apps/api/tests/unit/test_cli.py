"""
Tests for mastermind_cli.mm_flow.cli

TDD: verifies CLI lifecycle management — INSERT on --start, UPDATE on --complete,
runtime-state.json written with correct schema (C2), EXEC_ID handoff (C4).
"""

import json
import uuid
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from click.testing import CliRunner

from mastermind_cli.mm_flow.cli import cli


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_asyncpg_conn(
    execute_result: object = None,
    fetchrow_result: object = None,
) -> MagicMock:
    """Build a mock asyncpg connection for unit testing without a real DB.

    Args:
        execute_result: Value returned by ``conn.execute`` awaitable.
        fetchrow_result: Value returned by ``conn.fetchrow`` awaitable.

    Returns:
        AsyncMock configured with ``execute``, ``fetchrow``, and ``close``.
    """
    conn = AsyncMock()
    conn.execute = AsyncMock(return_value=execute_result)
    conn.fetchrow = AsyncMock(return_value=fetchrow_result)
    conn.close = AsyncMock()
    return conn


# ---------------------------------------------------------------------------
# Task 2.1 tests
# ---------------------------------------------------------------------------


class TestExecutePhaseStart:
    def test_start_creates_db_row(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--start issues INSERT into phase_executions with correct phase_number."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        # Override runtime-state path to tmp_path
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH",
            tmp_path / ".mm-flow" / "runtime-state.json",
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(cli, ["execute-phase", "--phase", "19", "--start"])

        assert result.exit_code == 0, result.output
        # Verify execute was called twice: SET LOCAL + INSERT (IMPORTANT #1 - RLS)
        assert conn.execute.await_count == 2
        # Second call should be the INSERT
        call_args = conn.execute.call_args_list[1]
        sql: str = call_args[0][0]
        assert "INSERT INTO phase_executions" in sql
        # phase_number arg is second positional
        assert call_args[0][2] == 19

    def test_execution_id_in_stdout(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--start echoes execution_id:<uuid> to stdout."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH",
            tmp_path / ".mm-flow" / "runtime-state.json",
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(cli, ["execute-phase", "--phase", "19", "--start"])

        assert result.exit_code == 0, result.output
        assert result.output.startswith("execution_id:")
        # The part after "execution_id:" must be a valid UUID
        raw_id = result.output.strip().split("execution_id:")[1]
        parsed = uuid.UUID(raw_id)  # raises if not valid UUID
        assert str(parsed) == raw_id

    def test_start_writes_runtime_state(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--start writes runtime-state.json with correct 7-field schema (C2)."""
        runtime_path = tmp_path / ".mm-flow" / "runtime-state.json"
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH", runtime_path
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(cli, ["execute-phase", "--phase", "19", "--start"])

        assert result.exit_code == 0, result.output
        assert runtime_path.exists(), "runtime-state.json must be created"

        state = json.loads(runtime_path.read_text())
        required_fields = {
            "execution_id",
            "phase",
            "current_moment",
            "active_brain",
            "brain_state",
            "backend",
            "updated_at",
        }
        assert required_fields == set(
            state.keys()
        ), f"Missing fields: {required_fields - set(state.keys())}"
        assert state["phase"] == 19
        assert state["brain_state"] == "ACTIVE"
        # execution_id must be a valid UUID
        uuid.UUID(state["execution_id"])


class TestExecutePhaseComplete:
    def test_complete_updates_db_row(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--complete issues UPDATE with status=completed."""
        runtime_path = tmp_path / ".mm-flow" / "runtime-state.json"
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH", runtime_path
        )

        # Pre-write a runtime state so --complete can read execution_id
        exec_id = str(uuid.uuid4())
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.write_text(
            json.dumps(
                {
                    "execution_id": exec_id,
                    "phase": 19,
                    "current_moment": "EXECUTION_WAVE",
                    "active_brain": 0,
                    "brain_state": "ACTIVE",
                    "backend": "claude",
                    "updated_at": "2026-04-14T00:00:00",
                }
            )
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(
                cli,
                [
                    "execute-phase",
                    "--phase",
                    "19",
                    "--complete",
                    "--commit",
                    "abc123",
                    "--tokens",
                    "500",
                    "--summary",
                    "test run",
                ],
            )

        assert result.exit_code == 0, result.output
        # Verify execute was called twice: SET LOCAL + UPDATE (IMPORTANT #1 - RLS)
        assert conn.execute.await_count == 2
        # Second call should be the UPDATE
        call_args = conn.execute.call_args_list[1]
        sql: str = call_args[0][0]
        assert "UPDATE phase_executions" in sql
        assert "status='completed'" in sql
        # execution_id is first positional arg
        assert call_args[0][1] == exec_id

    def test_complete_writes_runtime_state_idle(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """--complete writes runtime-state.json with brain_state=IDLE."""
        runtime_path = tmp_path / ".mm-flow" / "runtime-state.json"
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH", runtime_path
        )

        exec_id = str(uuid.uuid4())
        runtime_path.parent.mkdir(parents=True, exist_ok=True)
        runtime_path.write_text(
            json.dumps(
                {
                    "execution_id": exec_id,
                    "phase": 19,
                    "current_moment": "EXECUTION_WAVE",
                    "active_brain": 0,
                    "brain_state": "ACTIVE",
                    "backend": "claude",
                    "updated_at": "2026-04-14T00:00:00",
                }
            )
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(
                cli, ["execute-phase", "--phase", "19", "--complete"]
            )

        assert result.exit_code == 0, result.output
        state = json.loads(runtime_path.read_text())
        assert state["brain_state"] == "IDLE"
        assert state["current_moment"] == "COMPLETED"


class TestMutuallyExclusiveFlags:
    def test_start_and_complete_raises_usage_error(self) -> None:
        """--start and --complete together must raise UsageError with improved message."""
        runner = CliRunner()
        result = runner.invoke(
            cli, ["execute-phase", "--phase", "19", "--start", "--complete"]
        )
        assert result.exit_code != 0
        assert "mutually exclusive" in result.output.lower()
        # Check for improved error message (SUGGESTION #1)
        assert "example" in result.output.lower() or "--start" in result.output

    def test_neither_flag_raises_usage_error(self) -> None:
        """Calling without --start or --complete must raise UsageError with improved message."""
        runner = CliRunner()
        result = runner.invoke(cli, ["execute-phase", "--phase", "19"])
        assert result.exit_code != 0
        assert "required" in result.output.lower()
        # Check for improved error message with examples (SUGGESTION #1)
        assert "--start" in result.output and "--complete" in result.output


class TestEnvironmentValidation:
    """Tests for new environment variable validation (IMPORTANT #2)."""

    def test_missing_database_url_raises_usage_error(self) -> None:
        """DATABASE_URL environment variable must be set (no default)."""
        runner = CliRunner()
        # Ensure DATABASE_URL is not set
        result = runner.invoke(cli, ["execute-phase", "--phase", "19", "--start"])
        assert result.exit_code != 0
        assert "DATABASE_URL" in result.output
        assert "environment variable" in result.output.lower()
        # Check for helpful example (IMPORTANT #2)
        assert "export" in result.output or "postgresql://" in result.output

    def test_database_url_with_valid_value_succeeds(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Valid DATABASE_URL allows command to proceed."""
        monkeypatch.setenv("DATABASE_URL", "postgresql://fake/db")
        monkeypatch.setattr(
            "mastermind_cli.mm_flow.cli.RUNTIME_STATE_PATH",
            tmp_path / ".mm-flow" / "runtime-state.json",
        )

        conn = _make_asyncpg_conn()
        with patch("asyncpg.connect", new=AsyncMock(return_value=conn)):
            runner = CliRunner()
            result = runner.invoke(cli, ["execute-phase", "--phase", "19", "--start"])

        assert result.exit_code == 0, result.output
