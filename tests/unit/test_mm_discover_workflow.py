"""Tests for the adapted MasterMind discover workflow."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DISCOVER_HANDLER = REPO_ROOT / ".claude" / "commands" / "mm" / "discover-handler.py"
CONTRACT_CHECK = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "discover-contract-check.py"
)
COMPLETE_TASK_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "complete-task-handler.py"
)
UPDATE_TODO_TIMES = REPO_ROOT / ".claude" / "commands" / "mm" / "update-todo-times.py"


class DiscoverWorkflowTest(unittest.TestCase):
    """Exercise roadmap and objective package materialization."""

    def setUp(self) -> None:
        """Create a temporary repository-like workspace with minimal intent docs."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-discover-"))
        subprocess.run(
            ["git", "init"], cwd=self.temp_dir, check=True, capture_output=True
        )
        (self.temp_dir / ".planning").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / "docs" / "canonical").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / ".planning" / "SOURCE-OF-TRUTH.md").write_text(
            "# Source of Truth\n\n## Roadmap\n\n### Phase 21: Project State Realtime\n\n**Goal:** Add realtime updates to the project-state dashboard.\n",
            encoding="utf-8",
        )
        (
            self.temp_dir / ".planning" / "HANDOFF-PROJECT-STATE-2026-05-24.md"
        ).write_text(
            "# Project State Handoff\n\n## Goal\nContinue the Project State MVP.\n\n## Best next steps\n1. Add realtime events\n",
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
        (
            self.temp_dir / "docs" / "canonical" / "33-DASHBOARD-REALTIME-EVENTS.md"
        ).write_text(
            "# Dashboard Realtime Events\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """Remove the temporary workspace."""
        shutil.rmtree(self.temp_dir)

    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run a Python command in the temporary workspace."""
        return subprocess.run(
            ["python3", *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_roadmap_mode_materializes_outputs(self) -> None:
        """Roadmap mode should write roadmap files and the current handoff."""
        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        roadmap_dir = self.temp_dir / ".planning" / "roadmap"
        objectives_path = roadmap_dir / "objectives.md"
        dependency_path = roadmap_dir / "dependency-graph.md"
        self.assertTrue(objectives_path.exists())
        self.assertTrue(dependency_path.exists())
        self.assertIn("project-state", objectives_path.read_text(encoding="utf-8"))
        self.assertIn(
            "Project State",
            (self.temp_dir / ".planning" / "HANDOFF-CURRENT.md").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn("WRITTEN:", result.stdout)

    def test_objective_mode_materializes_package_and_validates(self) -> None:
        """Objective mode should write the package and pass the objective validator."""
        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        for filename in (
            "requirements.md",
            "design.md",
            "tasks.md",
            "todo.md",
            "HANDOFF-CURRENT.md",
        ):
            self.assertTrue((objective_dir / filename).exists(), msg=filename)

        tasks_text = (objective_dir / "tasks.md").read_text(encoding="utf-8")
        self.assertIn("### Purpose", tasks_text)
        self.assertIn("### Validation Commands", tasks_text)
        self.assertIn("### Files / Areas Likely Touched", tasks_text)

        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn("depends_on:", todo_text)
        self.assertIn("validation:", todo_text)

        check_result = self.run_command(
            str(CONTRACT_CHECK), "--objective", "project-state-mvp"
        )
        self.assertEqual(
            check_result.returncode, 0, msg=check_result.stdout + check_result.stderr
        )
        self.assertIn("STATUS: PASSED", check_result.stdout)

    def test_complete_task_handler_resolves_objective_package(self) -> None:
        """complete-task should execute against an objective package source."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Planning source: objective", result.stdout)
        self.assertIn("LAUNCH: task-executor", result.stdout)
        self.assertIn('"planning_mode": "objective"', result.stdout)
        self.assertIn('"objective_slug": "project-state-mvp"', result.stdout)

    def test_update_todo_times_uses_objective_todo_path(self) -> None:
        """update-todo-times should update the active objective todo.md from runtime state."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        runtime_state = {
            "task_id": "PS1",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {"status": "completed", "duration_seconds": 30},
                "PS1.2": {"status": "in_progress", "duration_seconds": 0},
                "PS1.3": {"status": "pending", "duration_seconds": 0},
            },
        }
        (self.temp_dir / ".planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        update_result = self.run_command(str(UPDATE_TODO_TIMES), "PS1")
        self.assertEqual(update_result.returncode, 0, msg=update_result.stderr)
        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn("⏱️ **Estimate**:", todo_text)
        self.assertIn("📊 **Avg/subtask**:", todo_text)

    def test_reconcile_repairs_todo_and_handoff_from_runtime_truth(self) -> None:
        """Reconcile mode should restore todo/handoff from runtime state truth."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        runtime_state = {
            "task_id": "PS1",
            "objective_slug": "project-state-mvp",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {"status": "completed", "duration_seconds": 30},
                "PS1.2": {"status": "pending", "duration_seconds": 0},
                "PS1.3": {"status": "pending", "duration_seconds": 0},
            },
        }
        (self.temp_dir / ".planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        todo_path = objective_dir / "todo.md"
        todo_text = todo_path.read_text(encoding="utf-8").replace(
            "- [ ] PS1:", "- [x] PS1:"
        )
        todo_text = todo_text.replace("- [ ] PS1.2:", "- [x] PS1.2:")
        todo_text = todo_text.replace("- [ ] PS1.3:", "- [x] PS1.3:")
        todo_path.write_text(todo_text, encoding="utf-8")

        handoff_path = objective_dir / "HANDOFF-CURRENT.md"
        handoff_text = handoff_path.read_text(encoding="utf-8")
        handoff_text = handoff_text.replace(
            "- [ ] The objective has an execution-ready package with requirements, design, tasks, and handoff.",
            "- [x] PS1: Realtime events for project_state — incorrectly advanced.",
        )
        handoff_text = handoff_text.replace(
            "- `PS1` from `tasks.md`.",
            "- `PS2` from `tasks.md` — incorrectly advanced.",
        )
        handoff_path.write_text(handoff_text, encoding="utf-8")

        reconcile_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--reconcile", "PS1"
        )
        self.assertEqual(
            reconcile_result.returncode,
            0,
            msg=reconcile_result.stdout + reconcile_result.stderr,
        )

        repaired_todo = todo_path.read_text(encoding="utf-8")
        self.assertIn("- [~] PS1:", repaired_todo)
        self.assertIn("- [x] PS1.1:", repaired_todo)
        self.assertIn("- [ ] PS1.2:", repaired_todo)
        self.assertIn("- [ ] PS1.3:", repaired_todo)

        repaired_handoff = handoff_path.read_text(encoding="utf-8")
        self.assertNotIn("incorrectly advanced", repaired_handoff)
        self.assertIn("## Exact next recommended task", repaired_handoff)
        self.assertIn("`PS1` from `tasks.md`", repaired_handoff)

    def test_starting_new_task_is_blocked_if_previous_runtime_task_incomplete(
        self,
    ) -> None:
        """A different task must not start while previous runtime task is incomplete."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        runtime_state = {
            "task_id": "PS2",
            "objective_slug": "project-state-mvp",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS2.1": {"status": "completed"},
                "PS2.2": {"status": "pending"},
                "PS2.3": {"status": "pending"},
            },
        }
        (self.temp_dir / ".planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS3")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("previous runtime task PS2 is incomplete", result.stderr)


if __name__ == "__main__":
    unittest.main()
