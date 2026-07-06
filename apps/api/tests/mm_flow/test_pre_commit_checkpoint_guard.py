"""Tests for pre_commit_checkpoint_guard.py.

These tests cover the checkpoint barrier that blocks commits when the active
objective has not advanced its staged execution-state artifacts.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

# Add guard directory to path for imports BEFORE importing the guard.
GUARD_DIR = (
    Path(__file__).parent.parent.parent.parent.parent / ".claude" / "commands" / "mm"
)
sys.path.insert(0, str(GUARD_DIR))

try:
    import pre_commit_checkpoint_guard as guard
except ImportError:
    pytest.skip("pre_commit_checkpoint_guard.py not found", allow_module_level=True)


class TestStatusRank:
    """Tests for status ordering."""

    def test_known_statuses(self) -> None:
        """Ranks known statuses in ascending progress order."""
        assert guard.status_rank("pending") == 0
        assert guard.status_rank("in_progress") == 1
        assert guard.status_rank("completed") == 2

    def test_unknown_statuses(self) -> None:
        """Returns -1 for statuses the guard does not understand."""
        assert guard.status_rank("blocked") == -1


class TestPathClassification:
    """Tests for code-path classification."""

    def test_ignores_planning_paths(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        """Ignores planning files inside the active objective tree."""
        monkeypatch.setattr(guard, "PLANNING_LABEL", ".planning")
        assert guard.is_code_like_path(".planning/changes/x/todo.md") is False

    def test_ignores_gitignore(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Ignores the top-level .gitignore file."""
        monkeypatch.setattr(guard, "PLANNING_LABEL", ".planning")
        assert guard.is_code_like_path(".gitignore") is False

    def test_accepts_code_paths(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Allows ordinary code paths to trigger the checkpoint barrier."""
        monkeypatch.setattr(guard, "PLANNING_LABEL", ".planning")
        assert guard.is_code_like_path("apps/api/main.py") is True


class TestMain:
    """Tests for the checkpoint barrier entrypoint."""

    def _configure_runtime(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        runtime: dict[str, object],
    ) -> Path:
        runtime_path = tmp_path / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime), encoding="utf-8")
        monkeypatch.setattr(guard, "RUNTIME_STATE", runtime_path)
        monkeypatch.setattr(guard, "PLANNING_LABEL", ".planning")
        monkeypatch.setattr(guard, "logger", MagicMock())
        return runtime_path

    def test_main_allows_missing_runtime_state(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Allows commits when no active task progress file exists."""
        monkeypatch.setattr(guard, "load_json_path", lambda path: None)
        monkeypatch.setattr(guard, "RUNTIME_STATE", tmp_path / "missing.json")

        assert guard.main() == 0

    def test_main_rejects_missing_checkpoint_artifacts(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
        capsys: pytest.CaptureFixture[str],
    ) -> None:
        """Blocks commits when required checkpoint artifacts are absent."""
        runtime = {
            "task_id": "task-1",
            "objective_slug": "objective-1",
            "subtasks": {"step-1": {"status": "in_progress"}},
        }
        self._configure_runtime(monkeypatch, tmp_path, runtime)
        monkeypatch.setattr(guard, "staged_files", lambda: ["apps/api/main.py"])

        assert guard.main() == 1
        assert "missing required checkpoint artifacts" in capsys.readouterr().err

    def test_main_rejects_when_no_progress_advancement(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Blocks commits when staged state does not advance task progress."""
        runtime = {
            "task_id": "task-1",
            "objective_slug": "objective-1",
            "subtasks": {"step-1": {"status": "in_progress"}},
        }
        self._configure_runtime(monkeypatch, tmp_path, runtime)
        monkeypatch.setattr(
            guard,
            "staged_files",
            lambda: [
                ".planning/changes/objective-1/execution-state.json",
                ".planning/changes/objective-1/todo.md",
                ".planning/changes/objective-1/HANDOFF-CURRENT.md",
                "apps/api/main.py",
            ],
        )
        monkeypatch.setattr(
            guard,
            "load_json_from_git",
            lambda rev_spec, repo_path: {
                "tasks": {
                    "task-1": {
                        "status": "pending",
                        "subtasks": {"step-1": {"status": "in_progress"}},
                    }
                }
            },
        )
        monkeypatch.setattr(
            guard,
            "load_json_from_index",
            lambda repo_path: {
                "tasks": {
                    "task-1": {
                        "status": "pending",
                        "subtasks": {"step-1": {"status": "in_progress"}},
                    }
                }
            },
        )

        assert guard.main() == 1
        assert guard.logger.error.called

    def test_main_allows_progress_advancement(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        """Allows commits when staged state advances task progress."""
        runtime = {
            "task_id": "task-1",
            "objective_slug": "objective-1",
            "subtasks": {"step-1": {"status": "in_progress"}},
        }
        self._configure_runtime(monkeypatch, tmp_path, runtime)
        monkeypatch.setattr(
            guard,
            "staged_files",
            lambda: [
                ".planning/changes/objective-1/execution-state.json",
                ".planning/changes/objective-1/todo.md",
                ".planning/changes/objective-1/HANDOFF-CURRENT.md",
                "apps/api/main.py",
            ],
        )
        monkeypatch.setattr(
            guard,
            "load_json_from_git",
            lambda rev_spec, repo_path: {
                "tasks": {
                    "task-1": {
                        "status": "pending",
                        "subtasks": {"step-1": {"status": "pending"}},
                    }
                }
            },
        )
        monkeypatch.setattr(
            guard,
            "load_json_from_index",
            lambda repo_path: {
                "tasks": {
                    "task-1": {
                        "status": "in_progress",
                        "subtasks": {"step-1": {"status": "in_progress"}},
                    }
                }
            },
        )

        assert guard.main() == 0
