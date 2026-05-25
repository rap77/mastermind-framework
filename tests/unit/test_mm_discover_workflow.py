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
ARCHIVE_OBJECTIVE_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "archive-objective-handler.py"
)
UPDATE_TODO_TIMES = REPO_ROOT / ".claude" / "commands" / "mm" / "update-todo-times.py"
CHECKPOINT_GUARD = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "pre_commit_checkpoint_guard.py"
)


class DiscoverWorkflowTest(unittest.TestCase):
    """Exercise roadmap and objective package materialization."""

    def setUp(self) -> None:
        """Create a temporary repository-like workspace with minimal intent docs."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-discover-"))
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
        current_handoff = (
            self.temp_dir / ".planning" / "HANDOFF-CURRENT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Current objective", current_handoff)
        self.assertIn("/mm:discover --existing --objective", current_handoff)
        self.assertIn("WRITTEN:", result.stdout)

    def test_roadmap_merges_project_state_aliases_and_marks_completed_package_done(
        self,
    ) -> None:
        """Roadmap discovery should not split project-state and project-state-mvp into separate active tracks."""
        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        objective_dir.mkdir(parents=True, exist_ok=True)
        (objective_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime events\n",
            encoding="utf-8",
        )
        (objective_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime events\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (objective_dir / "HANDOFF-CURRENT.md").write_text(
            "# Handoff — project-state-mvp\n\n## Current objective\n- `project-state-mvp` — **COMPLETE**\n",
            encoding="utf-8",
        )
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )

        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        objectives = json.loads(
            (self.temp_dir / ".planning" / "roadmap" / "objectives.json").read_text(
                encoding="utf-8"
            )
        )
        project_state_entries = [
            item
            for item in objectives
            if item["slug"] in {"project-state", "project-state-mvp"}
        ]
        self.assertEqual(len(project_state_entries), 1)
        self.assertEqual(project_state_entries[0]["slug"], "project-state-mvp")
        self.assertEqual(project_state_entries[0]["status"], "done")

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

        objective_state_path = (
            self.temp_dir
            / ".planning"
            / "changes"
            / "project-state-mvp"
            / "execution-state.json"
        )
        self.assertTrue(objective_state_path.exists())
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(objective_state["objective_slug"], "project-state-mvp")
        self.assertIn("PS1", objective_state["tasks"])

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

    def test_mark_commands_update_durable_objective_state_and_todo_projection(
        self,
    ) -> None:
        """Handler mark commands should be the single writer for progress state."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)

        mark_progress = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
        )
        self.assertEqual(mark_progress.returncode, 0, msg=mark_progress.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"],
            "in_progress",
        )
        self.assertEqual(objective_state["tasks"]["PS1"]["status"], "in_progress")

        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn("- [~] PS1: Realtime events for project_state", todo_text)
        self.assertIn(
            "- [~] PS1.1: Review requirements and design context for PS1", todo_text
        )

        mark_done = self.run_command(str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.1")
        self.assertEqual(mark_done.returncode, 0, msg=mark_done.stderr)

        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"],
            "completed",
        )
        self.assertEqual(objective_state["tasks"]["PS1"]["status"], "in_progress")

        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn(
            "- [x] PS1.1: Review requirements and design context for PS1", todo_text
        )

    def test_start_task_reprojects_manual_todo_drift_from_objective_state(self) -> None:
        """Manual todo edits must be overwritten from durable objective state before execution."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["status"] = "in_progress"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "completed"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]["status"] = "pending"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.3"]["status"] = "pending"
        objective_state_path.write_text(json.dumps(objective_state), encoding="utf-8")

        todo_path = objective_dir / "todo.md"
        drifted = todo_path.read_text(encoding="utf-8")
        drifted = drifted.replace("- [ ] PS1:", "- [x] PS1:")
        drifted = drifted.replace("- [ ] PS1.2:", "- [x] PS1.2:")
        drifted = drifted.replace("- [ ] PS1.3:", "- [x] PS1.3:")
        todo_path.write_text(drifted, encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        repaired_todo = todo_path.read_text(encoding="utf-8")
        self.assertIn("- [~] PS1: Realtime events for project_state", repaired_todo)
        self.assertIn(
            "- [x] PS1.1: Review requirements and design context for PS1", repaired_todo
        )
        self.assertIn("- [ ] PS1.2: Implement PS1 end-to-end", repaired_todo)
        self.assertIn("- [ ] PS1.3: Run validation for PS1", repaired_todo)
        self.assertIn("PENDING: 2 subtasks to execute", result.stdout)

    def test_show_status_uses_durable_state_not_manual_todo_checkboxes(self) -> None:
        """Status output must reflect execution-state truth even if todo.md was manually advanced."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["status"] = "in_progress"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "completed"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]["status"] = "pending"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.3"]["status"] = "pending"
        objective_state_path.write_text(json.dumps(objective_state), encoding="utf-8")

        todo_path = objective_dir / "todo.md"
        drifted = todo_path.read_text(encoding="utf-8")
        drifted = drifted.replace("- [ ] PS1:", "- [x] PS1:")
        drifted = drifted.replace("- [ ] PS1.2:", "- [x] PS1.2:")
        drifted = drifted.replace("- [ ] PS1.3:", "- [x] PS1.3:")
        todo_path.write_text(drifted, encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("PS1 [~] 1/3", result.stdout)

    def test_starting_new_root_task_preserves_previous_objective_history(self) -> None:
        """Starting the next root task must not erase durable status of the previous one."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        objective_state_path = objective_dir / "execution-state.json"

        start_ps1 = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_ps1.returncode, 0, msg=start_ps1.stderr)
        for subtask_id in ("PS1.1", "PS1.2", "PS1.3"):
            in_progress = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-in-progress", subtask_id
            )
            self.assertEqual(in_progress.returncode, 0, msg=in_progress.stderr)
            done = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", subtask_id
            )
            self.assertEqual(done.returncode, 0, msg=done.stderr)

        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(objective_state["tasks"]["PS1"]["status"], "completed")

        start_ps2 = self.run_command(str(COMPLETE_TASK_HANDLER), "PS2")
        self.assertEqual(start_ps2.returncode, 0, msg=start_ps2.stderr)

        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(objective_state["tasks"]["PS1"]["status"], "completed")
        self.assertIn("PS2", objective_state["tasks"])

    def test_task_resolution_prefers_explicit_task_objective_over_stale_runtime(
        self,
    ) -> None:
        """Explicit task IDs must resolve against their own objective package, not stale runtime paths."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stderr)
        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 0, msg=second.stderr)

        first_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        runtime_state = {
            "task_id": "PS1",
            "objective_slug": "project-state-mvp",
            "plan_path": str(first_dir / "tasks.md"),
            "todo_path": str(first_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {"status": "completed"},
                "PS1.2": {"status": "completed"},
                "PS1.3": {"status": "completed"},
            },
        }
        (self.temp_dir / ".planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "T1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(
            ".planning/changes/artifact-versioning-and-lineage/tasks.md", result.stdout
        )
        self.assertIn(
            '"objective_slug": "artifact-versioning-and-lineage"', result.stdout
        )

    def test_archive_objective_moves_completed_package_to_archive_objectives(
        self,
    ) -> None:
        """Completed objective packages should archive into archive/objectives, not legacy roots."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {
                        "PS1": {"status": "completed"},
                        "PS2": {"status": "completed"},
                    },
                }
            ),
            encoding="utf-8",
        )

        archive_result = self.run_command(
            str(ARCHIVE_OBJECTIVE_HANDLER), "--objective", "project-state-mvp"
        )
        self.assertEqual(archive_result.returncode, 0, msg=archive_result.stderr)
        self.assertFalse(objective_dir.exists())
        archived_dir = (
            self.temp_dir / ".planning" / "archive" / "objectives" / "project-state-mvp"
        )
        self.assertTrue(archived_dir.exists())
        self.assertTrue((archived_dir / "COMPLETION-SUMMARY.md").exists())

    def test_checkpoint_guard_blocks_code_commit_without_execution_state_advance(
        self,
    ) -> None:
        """Pre-commit guard must reject staged code when objective state did not advance."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        code_path = self.temp_dir / "README.md"
        code_path.write_text("# Temp Repo\nchanged\n", encoding="utf-8")

        subprocess.run(
            [
                "git",
                "add",
                "README.md",
                str(
                    (objective_dir / "execution-state.json").relative_to(self.temp_dir)
                ),
                str((objective_dir / "todo.md").relative_to(self.temp_dir)),
                str((objective_dir / "HANDOFF-CURRENT.md").relative_to(self.temp_dir)),
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )

        result = self.run_command(str(CHECKPOINT_GUARD))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no durable task progress advancement", result.stdout)

    def test_checkpoint_guard_allows_commit_when_execution_state_advances(
        self,
    ) -> None:
        """Pre-commit guard should pass when staged execution-state advances active subtask status."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)

        objective_dir = self.temp_dir / ".planning" / "changes" / "project-state-mvp"
        execution_state_path = objective_dir / "execution-state.json"
        execution_state = json.loads(execution_state_path.read_text(encoding="utf-8"))
        execution_state["tasks"]["PS1"]["status"] = "in_progress"
        execution_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "completed"
        execution_state_path.write_text(json.dumps(execution_state), encoding="utf-8")

        todo_path = objective_dir / "todo.md"
        todo_text = todo_path.read_text(encoding="utf-8")
        todo_text = todo_text.replace("- [ ] PS1:", "- [~] PS1:")
        todo_text = todo_text.replace("- [ ] PS1.1:", "- [x] PS1.1:")
        todo_path.write_text(todo_text, encoding="utf-8")

        code_path = self.temp_dir / "README.md"
        code_path.write_text("# Temp Repo\nchanged\n", encoding="utf-8")

        subprocess.run(
            [
                "git",
                "add",
                "README.md",
                str(execution_state_path.relative_to(self.temp_dir)),
                str(todo_path.relative_to(self.temp_dir)),
                str((objective_dir / "HANDOFF-CURRENT.md").relative_to(self.temp_dir)),
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )

        result = self.run_command(str(CHECKPOINT_GUARD))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
