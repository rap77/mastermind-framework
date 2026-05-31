"""Focused regressions for complete-task handler argument parsing and resume sync."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DISCOVER_HANDLER = REPO_ROOT / ".claude" / "commands" / "mm" / "discover-handler.py"
COMPLETE_TASK_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "complete-task-handler.py"
)


class CompleteTaskHandlerRegressionTest(unittest.TestCase):
    """Exercise focused complete-task regressions without relying on broader suite state."""

    def setUp(self) -> None:
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-complete-task-"))
        subprocess.run(
            ["git", "init"], cwd=self.temp_dir, check=True, capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.email", "test@example.com"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        (self.temp_dir / ".mm-flow" / "planning").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / "docs" / "canonical").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / ".mm-flow" / "planning" / "SOURCE-OF-TRUTH.md").write_text(
            "# Source of Truth\n",
            encoding="utf-8",
        )
        (self.temp_dir / "README.md").write_text("# Temp Repo\n", encoding="utf-8")
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "21-PROJECT-STATE-OPERATIONAL-MEMORY-ARCHITECTURE.md"
        ).write_text(
            "# Project State Operational Memory Architecture\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir)

    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["python3", *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def _materialize_project_state_objective(self) -> Path:
        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        return self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"

    def test_brief_mode_accepts_task_then_flag_order(self) -> None:
        """`<TASK_ID> --brief` must print the brief without starting execution."""
        self._materialize_project_state_objective()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--brief")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("MODEL_BRIEF_START", result.stdout)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertNotIn("INFO: Starting task PS1", result.stdout)

    def test_resume_task_persists_runtime_completion_into_objective_state(self) -> None:
        """`--continue` must promote completed runtime subtasks into execution-state.json."""
        objective_dir = self._materialize_project_state_objective()

        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )

        runtime_state = {
            "task_id": "PS1",
            "objective_slug": "project-state-mvp",
            "session_id": "resume-test-session",
            "started_at": "2026-05-31T10:00:00",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {
                    "description": "Review requirements and design context for PS1",
                    "status": "completed",
                    "started_at": "2026-05-31T10:00:00",
                    "completed_at": "2026-05-31T10:05:00",
                    "duration_seconds": 300,
                },
                "PS1.2": {
                    "description": "Implement PS1 end-to-end",
                    "status": "completed",
                    "started_at": "2026-05-31T10:06:00",
                    "completed_at": "2026-05-31T10:12:00",
                    "duration_seconds": 360,
                },
                "PS1.3": {
                    "description": "Run validation for PS1",
                    "status": "completed",
                    "started_at": "2026-05-31T10:13:00",
                    "completed_at": "2026-05-31T10:14:00",
                    "duration_seconds": 60,
                },
            },
            "last_checkpoint": "PS1.3",
        }
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state), encoding="utf-8"
        )

        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["status"] = "in_progress"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "completed"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]["status"] = "completed"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.3"]["status"] = "pending"
        objective_state_path.write_text(json.dumps(objective_state), encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("TASK COMPLETE", result.stdout)

        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(repaired_state["tasks"]["PS1"]["status"], "completed")
        self.assertEqual(
            repaired_state["tasks"]["PS1"]["subtasks"]["PS1.3"]["status"], "completed"
        )


if __name__ == "__main__":
    unittest.main()
