"""Focused regressions for complete-task handler argument parsing and resume sync."""

from __future__ import annotations

import json
import fcntl
import re
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
        """Create an isolated planning repository for each regression test."""
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
        """Remove the isolated planning repository after each regression test."""
        shutil.rmtree(self.temp_dir)

    def run_command(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run a command inside the isolated repository."""
        return subprocess.run(
            ["python3", *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def _write_active_objective_exceptions_artifact(
        self, payload: dict[str, object]
    ) -> Path:
        path = (
            self.temp_dir / ".mm-flow" / "planning" / "active-objective-exceptions.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def _with_default_exception_expiry(
        self, payload: dict[str, object]
    ) -> dict[str, object]:
        exceptions = payload.get("exceptions", [])
        if not isinstance(exceptions, list):
            return payload
        normalized: list[dict[str, object]] = []
        for entry in exceptions:
            if not isinstance(entry, dict):
                continue
            enriched = dict(entry)
            enriched.setdefault("expires_at_utc", "2099-01-01T00:00:00Z")
            normalized.append(enriched)
        updated = dict(payload)
        updated["exceptions"] = normalized
        return updated

    def _materialize_project_state_objective(self) -> Path:
        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        for task_id in ("PS1", "PS2", "PS3"):
            self._set_task_topology(
                objective_dir,
                task_id,
                [
                    (
                        f"{task_id}.1",
                        f"Review requirements and design context for {task_id}",
                    ),
                    (f"{task_id}.2", f"Implement {task_id} end-to-end"),
                    (f"{task_id}.3", f"Run validation for {task_id}"),
                ],
            )
        return objective_dir

    def _materialize_generic_objective(self, slug: str, title: str) -> Path:
        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            slug,
            title,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        objective_dir = self.temp_dir / ".mm-flow" / "planning" / "changes" / slug
        for task_id in ("T1", "T2", "T3"):
            self._set_task_topology(
                objective_dir,
                task_id,
                [
                    (
                        f"{task_id}.1",
                        f"Review requirements and design context for {task_id}",
                    ),
                    (f"{task_id}.2", f"Implement {task_id} end-to-end"),
                    (f"{task_id}.3", f"Run validation for {task_id}"),
                ],
            )
        return objective_dir

    def _set_task_topology(
        self, objective_dir: Path, task_id: str, entries: list[tuple[str, str]]
    ) -> None:
        """Replace one task's explicit topology block in a test plan."""
        tasks_path = objective_dir / "tasks.md"
        content = tasks_path.read_text(encoding="utf-8")
        body = "".join(
            f"- {subtask_id}: {description}\n" for subtask_id, description in entries
        )
        updated, count = re.subn(
            rf"(^## {re.escape(task_id)}:.*?^### Execution Subtasks\n).*?(?=^### )",
            rf"\g<1>{body}\n",
            content,
            count=1,
            flags=re.MULTILINE | re.DOTALL,
        )
        if count == 0:
            updated, count = re.subn(
                rf"(^## {re.escape(task_id)}:.*?\n\n)(?=### Purpose)",
                rf"\g<1>### Execution Subtasks\n{body}\n",
                content,
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            )
        self.assertEqual(count, 1)
        tasks_path.write_text(updated, encoding="utf-8")

    def _set_legacy_todo_topology(
        self,
        objective_dir: Path,
        task_id: str,
        entries: list[tuple[str, str, str]],
    ) -> None:
        """Inject explicit unmarked legacy children under one todo root."""
        todo_path = objective_dir / "todo.md"
        content = todo_path.read_text(encoding="utf-8").replace(
            "<!-- topology-source: tasks.md -->\n\n", "", 1
        )
        children = "\n".join(
            f"  - [{status}] {subtask_id}: {description}"
            for status, subtask_id, description in entries
        )
        updated, count = re.subn(
            rf"(^- \[ \] {re.escape(task_id)}:.*$)",
            rf"\g<1>\n{children}",
            content,
            count=1,
            flags=re.MULTILINE,
        )
        self.assertEqual(count, 1)
        todo_path.write_text(updated, encoding="utf-8")

    def _materialize_two_generic_objectives(self) -> tuple[Path, Path]:
        """Create two concurrently active objectives for scoped-resolution tests."""
        alpha_dir = self._materialize_generic_objective(
            "alpha-objective", "Alpha Objective"
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-alpha-beta-regressions",
                            "objective_slugs": ["alpha-objective", "beta-objective"],
                            "reason": "Allow scoped complete-task regression coverage.",
                            "commands": ["discover --existing --objective"],
                            "expires_when": "Remove after regression test completes.",
                        }
                    ],
                }
            )
        )
        beta_dir = self._materialize_generic_objective(
            "beta-objective", "Beta Objective"
        )
        return alpha_dir, beta_dir

    def test_brief_mode_accepts_task_then_flag_order(self) -> None:
        """`<TASK_ID> --brief` must print the brief without starting execution."""
        self._materialize_project_state_objective()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--brief")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("MODEL_BRIEF_START", result.stdout)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertNotIn("INFO: Starting task PS1", result.stdout)

    def test_brief_includes_matching_objective_canonical_doc(self) -> None:
        """Brief should surface the primary canonical doc when one matches the objective slug."""
        (self.temp_dir / "docs" / "canonical" / "21-project-state-mvp.md").write_text(
            "# Project State MVP\n",
            encoding="utf-8",
        )
        self._materialize_project_state_objective()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--brief", "PS1")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("docs/canonical/21-project-state-mvp.md", result.stdout)

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

    def test_resync_preserves_existing_execution_metadata(self) -> None:
        """Resync must not erase durable timestamps or task metadata."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        task_state = objective_state["tasks"]["PS1"]
        subtask_state = task_state["subtasks"]["PS1.1"]
        objective_state["status"] = "active"
        objective_state["active_task"] = "PS2"
        objective_state["tasks"]["REMOVED"] = {"status": "completed"}
        task_state["depends_on"] = ["PS0"]
        task_state["subtasks"]["PS1.REMOVED"] = {"status": "completed"}
        task_state["started_at"] = "2026-05-31T10:00:00"
        task_state["completed_at"] = "2026-05-31T10:05:00"
        subtask_state["started_at"] = "2026-05-31T10:00:00"
        subtask_state["completed_at"] = "2026-05-31T10:05:00"
        subtask_state["duration_seconds"] = 300
        subtask_state["updated_at"] = "2026-05-31T10:05:00"
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        repaired_task = repaired_state["tasks"]["PS1"]
        repaired_subtask = repaired_task["subtasks"]["PS1.1"]
        self.assertEqual(repaired_state["status"], "active")
        self.assertEqual(repaired_state["active_task"], "PS2")
        self.assertNotIn("REMOVED", repaired_state["tasks"])
        self.assertEqual(repaired_task["depends_on"], ["PS0"])
        self.assertNotIn("PS1.REMOVED", repaired_task["subtasks"])
        self.assertEqual(repaired_task["started_at"], "2026-05-31T10:00:00")
        self.assertEqual(repaired_task["completed_at"], "2026-05-31T10:05:00")
        self.assertEqual(repaired_subtask["started_at"], "2026-05-31T10:00:00")
        self.assertEqual(repaired_subtask["completed_at"], "2026-05-31T10:05:00")
        self.assertEqual(repaired_subtask["duration_seconds"], 300)
        self.assertEqual(repaired_subtask["updated_at"], "2026-05-31T10:05:00")

    def test_resync_rebuilds_invalid_state_shapes(self) -> None:
        """Resync must recover when valid JSON has a non-object ledger shape."""
        objective_dir = self._materialize_project_state_objective()
        objective_state_path = objective_dir / "execution-state.json"

        for invalid_state in (None, [], {"tasks": []}, {"tasks": {"PS1": []}}):
            with self.subTest(invalid_state=invalid_state):
                objective_state_path.write_text(
                    json.dumps(invalid_state), encoding="utf-8"
                )
                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    "project-state-mvp",
                )
                self.assertEqual(
                    result.returncode, 0, msg=result.stdout + result.stderr
                )
                repaired_state = json.loads(
                    objective_state_path.read_text(encoding="utf-8")
                )
                self.assertIsInstance(repaired_state, dict)
                self.assertIsInstance(repaired_state["tasks"], dict)
                self.assertIsInstance(repaired_state["tasks"]["PS1"], dict)

    def test_resync_prefers_non_empty_runtime_metadata(self) -> None:
        """Valid runtime checkpoints must override older durable metadata."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        durable_subtask = objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]
        durable_subtask["started_at"] = "2026-05-31T09:00:00"
        durable_subtask["duration_seconds"] = 60
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime_subtask = runtime_state["subtasks"]["PS1.2"]
        runtime_subtask["status"] = "completed"
        runtime_subtask["started_at"] = "2026-05-31T10:00:00"
        runtime_subtask["completed_at"] = "2026-05-31T10:02:00"
        runtime_subtask["duration_seconds"] = 120
        runtime_subtask["updated_at"] = "2026-05-31T10:02:00"
        runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        repaired_subtask = repaired_state["tasks"]["PS1"]["subtasks"]["PS1.2"]
        self.assertEqual(repaired_subtask["status"], "completed")
        self.assertEqual(repaired_subtask["started_at"], "2026-05-31T10:00:00")
        self.assertEqual(repaired_subtask["completed_at"], "2026-05-31T10:02:00")
        self.assertEqual(repaired_subtask["duration_seconds"], 120)
        self.assertEqual(repaired_subtask["updated_at"], "2026-05-31T10:02:00")

    def test_resync_clears_active_task_removed_from_plan(self) -> None:
        """Resync must not retain an active task absent from the current plan."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["active_task"] = "REMOVED"
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertNotIn("active_task", repaired_state)

    def test_resync_ignores_runtime_with_invalid_subtask_shapes(self) -> None:
        """Malformed nested runtime state must not crash objective resync."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        valid_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

        for invalid_subtasks in ([], {"PS1.1": []}, {"PS1.1": {}}):
            with self.subTest(invalid_subtasks=invalid_subtasks):
                malformed_runtime = {**valid_runtime, "subtasks": invalid_subtasks}
                runtime_path.write_text(json.dumps(malformed_runtime), encoding="utf-8")
                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    "project-state-mvp",
                )
                self.assertEqual(
                    result.returncode, 0, msg=result.stdout + result.stderr
                )
                self.assertFalse(runtime_path.exists())

    def test_resync_preserves_runtime_owned_by_another_objective(self) -> None:
        """Resync never deletes or normalizes cross-objective runtime."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(
            json.dumps(
                {
                    "task_id": "T1",
                    "objective_slug": "beta-objective",
                    "session_id": "beta-runtime",
                    "plan_path": str(beta_dir / "tasks.md"),
                    "todo_path": str(beta_dir / "todo.md"),
                    "subtasks": {"T1.1": []},
                }
            ),
            encoding="utf-8",
        )
        before = runtime_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", alpha_dir.name
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertEqual(runtime_path.read_bytes(), before)

    def test_resync_rolls_back_all_artifacts_on_late_acceptance_failure(self) -> None:
        """Late acceptance failure restores local, runtime, and global artifacts."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace("- [ ]", "- [z]", 1),
            encoding="utf-8",
        )
        tracked = (
            self.temp_dir / ".mm-flow" / "planning" / "task-progress.json",
            objective_dir / "execution-state.json",
            tasks_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
            self.temp_dir / ".mm-flow" / "planning" / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance", result.stderr.lower())
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_resync_reads_subtasks_from_the_explicit_objective(self) -> None:
        """Duplicate task IDs must not make resync consume another objective's plan."""
        alpha_dir, _beta_dir = self._materialize_two_generic_objectives()
        self._set_task_topology(
            alpha_dir,
            "T1",
            [
                ("T1.1", "Alpha-only requirements review"),
                ("T1.2", "Implement T1 end-to-end"),
                ("T1.3", "Run validation for T1"),
            ],
        )

        beta_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "beta-objective"
        )
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "beta-objective",
            "plan_path": str(beta_dir / "tasks.md"),
            "todo_path": str(beta_dir / "todo.md"),
            "session_id": "beta-runtime",
            "started_at": "2026-06-01T09:00:00",
            "subtasks": {
                "T1.1": {
                    "description": "Review requirements and design context for T1",
                    "status": "pending",
                }
            },
        }
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state), encoding="utf-8"
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "alpha-objective"
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        alpha_state = json.loads(
            (alpha_dir / "execution-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            alpha_state["tasks"]["T1"]["subtasks"]["T1.1"]["description"],
            "Alpha-only requirements review",
        )

    def test_resync_validates_root_tasks_before_rewriting_ledger(self) -> None:
        """An empty tasks.md must fail without erasing the existing durable ledger."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        original_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        original_state["durable_marker"] = "must-survive"
        objective_state_path.write_text(
            json.dumps(original_state, indent=2), encoding="utf-8"
        )
        original_bytes = objective_state_path.read_bytes()
        (objective_dir / "tasks.md").write_text(
            "# Malformed plan without root tasks\n", encoding="utf-8"
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("has no root tasks", result.stderr)
        self.assertEqual(objective_state_path.read_bytes(), original_bytes)

    def test_continue_rejects_runtime_with_list_subtasks_without_traceback(
        self,
    ) -> None:
        """Resume must use validated runtime state instead of iterating raw JSON shapes."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime_state["subtasks"] = []
        runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runtime state is invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_fresh_start_rejects_invalid_objective_state_shape(self) -> None:
        """Normal start must fail closed without rewriting a malformed ledger."""
        objective_dir = self._materialize_project_state_objective()
        objective_state_path = objective_dir / "execution-state.json"
        objective_state_path.write_text('{"tasks": []}', encoding="utf-8")
        invalid_bytes = objective_state_path.read_bytes()
        todo_path = objective_dir / "todo.md"
        todo_bytes = todo_path.read_bytes()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Objective state is invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(objective_state_path.read_bytes(), invalid_bytes)
        self.assertEqual(todo_path.read_bytes(), todo_bytes)

    def test_resync_invalid_runtime_does_not_regress_valid_durable_status(self) -> None:
        """Malformed lower-authority runtime cannot downgrade valid durable state."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        base_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

        for invalid_status in ("", "unknown-status"):
            with self.subTest(invalid_status=invalid_status):
                objective_state = json.loads(
                    objective_state_path.read_text(encoding="utf-8")
                )
                durable = objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]
                durable["status"] = "in_progress"
                durable["started_at"] = "2026-06-01T09:00:00"
                objective_state_path.write_text(
                    json.dumps(objective_state, indent=2), encoding="utf-8"
                )
                runtime_state = json.loads(json.dumps(base_runtime))
                runtime_state["subtasks"]["PS1.1"]["status"] = invalid_status
                runtime_state["subtasks"]["PS1.1"]["started_at"] = "2026-06-01T10:00:00"
                runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    "project-state-mvp",
                )
                self.assertEqual(
                    result.returncode, 0, msg=result.stdout + result.stderr
                )
                repaired_state = json.loads(
                    objective_state_path.read_text(encoding="utf-8")
                )
                repaired = repaired_state["tasks"]["PS1"]["subtasks"]["PS1.1"]
                self.assertEqual(repaired["status"], "in_progress")
                self.assertNotEqual(repaired["status"], invalid_status)
                self.assertEqual(repaired["started_at"], "2026-06-01T09:00:00")

    def test_resync_rejects_runtime_with_empty_required_timestamps(self) -> None:
        """Resync must not consume runtime rejected by the primary loader."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        durable = objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]
        durable["started_at"] = "2026-06-01T09:00:00"
        durable["completed_at"] = "2026-06-01T09:05:00"
        durable["updated_at"] = "2026-06-01T09:05:00"
        durable["duration_seconds"] = 300
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime_subtask = runtime_state["subtasks"]["PS1.1"]
        runtime_subtask.update(
            {
                "status": "completed",
                "started_at": "",
                "completed_at": "",
                "updated_at": "",
                "duration_seconds": 0,
            }
        )
        runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        repaired = repaired_state["tasks"]["PS1"]["subtasks"]["PS1.1"]
        self.assertEqual(repaired["status"], "pending")
        self.assertEqual(repaired["started_at"], "2026-06-01T09:00:00")
        self.assertEqual(repaired["completed_at"], "2026-06-01T09:05:00")
        self.assertEqual(repaired["updated_at"], "2026-06-01T09:05:00")
        self.assertEqual(repaired["duration_seconds"], 300)
        self.assertFalse(runtime_path.exists())

    def test_resume_reconcile_ignores_stale_runtime_subtasks_and_null_timing(
        self,
    ) -> None:
        """Runtime reconciliation must be plan-scoped and preserve durable timings."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        durable = objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]
        durable["started_at"] = "2026-06-01T09:00:00"
        durable["completed_at"] = "2026-06-01T09:05:00"
        durable["updated_at"] = "2026-06-01T09:05:00"
        durable["duration_seconds"] = 300
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        for runtime_subtask in runtime_state["subtasks"].values():
            runtime_subtask["status"] = "completed"
        runtime_state["subtasks"]["PS1.1"].update(
            {
                "started_at": None,
                "completed_at": None,
                "updated_at": None,
                "duration_seconds": 0,
            }
        )
        runtime_state["subtasks"]["PS1.99"] = {
            "description": "Removed stale subtask",
            "status": "completed",
            "started_at": None,
            "completed_at": None,
            "updated_at": None,
            "duration_seconds": 0,
        }
        runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("TASK COMPLETE", result.stdout)
        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        repaired_subtasks = repaired_state["tasks"]["PS1"]["subtasks"]
        self.assertNotIn("PS1.99", repaired_subtasks)
        normalized_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertNotIn("PS1.99", normalized_runtime["subtasks"])
        self.assertEqual(
            set(normalized_runtime["subtasks"]), {"PS1.1", "PS1.2", "PS1.3"}
        )
        repaired = repaired_subtasks["PS1.1"]
        self.assertEqual(repaired["started_at"], "2026-06-01T09:00:00")
        self.assertEqual(repaired["completed_at"], "2026-06-01T09:05:00")
        self.assertEqual(repaired["updated_at"], "2026-06-01T09:05:00")
        self.assertEqual(repaired["duration_seconds"], 300)

    def test_resume_requires_every_expected_subtask_to_be_completed(self) -> None:
        """Incomplete, invalid, or missing expected runtime entries must not complete a task."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        base_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

        scenarios: tuple[str, str | None] = (
            ("in_progress", "in_progress"),
            ("failed", "failed"),
            ("skipped", "skipped"),
            ("unknown", "unknown-status"),
            ("missing", None),
        )
        for label, status in scenarios:
            with self.subTest(status=label):
                runtime_state = json.loads(json.dumps(base_runtime))
                for runtime_subtask in runtime_state["subtasks"].values():
                    runtime_subtask["status"] = "completed"
                if status is None:
                    runtime_state["subtasks"].pop("PS1.3")
                else:
                    runtime_state["subtasks"]["PS1.3"]["status"] = status
                runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "PS1", "--continue"
                )
                self.assertNotIn("TASK COMPLETE", result.stdout)
                self.assertNotIn("Traceback", result.stderr)

    def test_objective_slug_rejects_unsafe_path_components(self) -> None:
        """Objective paths must reject traversal, separators, absolute paths, and empties."""
        self._materialize_project_state_objective()

        unsafe_slugs = (
            "",
            "..",
            "../project-state-mvp",
            "alpha/objective",
            str(self.temp_dir),
        )
        for unsafe_slug in unsafe_slugs:
            with self.subTest(unsafe_slug=unsafe_slug):
                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    unsafe_slug,
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("safe single path component", result.stderr)

        scoped_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--brief", "../project-state-mvp/PS1"
        )
        self.assertNotEqual(scoped_result.returncode, 0)
        self.assertIn("safe single path component", scoped_result.stderr)

    def test_explicit_resume_rejects_runtime_from_another_objective(self) -> None:
        """Scoped resume must not consume same-ID runtime or ledger state from another objective."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        alpha_state_path = alpha_dir / "execution-state.json"
        beta_state_path = beta_dir / "execution-state.json"
        alpha_bytes = alpha_state_path.read_bytes()
        beta_state = json.loads(beta_state_path.read_text(encoding="utf-8"))
        beta_task = beta_state["tasks"]["T1"]
        beta_task["status"] = "completed"
        for subtask in beta_task["subtasks"].values():
            subtask["status"] = "completed"
        beta_state_path.write_text(json.dumps(beta_state, indent=2), encoding="utf-8")
        beta_bytes = beta_state_path.read_bytes()

        runtime_state = {
            "task_id": "T1",
            "objective_slug": "beta-objective",
            "session_id": "beta-resume-session",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(beta_dir / "tasks.md"),
            "todo_path": str(beta_dir / "todo.md"),
            "subtasks": {
                subtask_id: {
                    "description": subtask["description"],
                    "status": "completed",
                }
                for subtask_id, subtask in beta_task["subtasks"].items()
            },
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")
        runtime_bytes = runtime_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "alpha-objective/T1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("belongs to objective `beta-objective`", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(alpha_state_path.read_bytes(), alpha_bytes)
        self.assertEqual(beta_state_path.read_bytes(), beta_bytes)
        self.assertEqual(runtime_path.read_bytes(), runtime_bytes)

    def test_explicit_resume_rejects_mismatched_durable_objective_slug(self) -> None:
        """Scoped resume must not trust a ledger whose embedded slug names another objective."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        alpha_state_path = alpha_dir / "execution-state.json"
        beta_state_path = beta_dir / "execution-state.json"
        alpha_state = json.loads(alpha_state_path.read_text(encoding="utf-8"))
        alpha_state["objective_slug"] = "beta-objective"
        alpha_state_path.write_text(json.dumps(alpha_state, indent=2), encoding="utf-8")
        alpha_bytes = alpha_state_path.read_bytes()
        beta_bytes = beta_state_path.read_bytes()
        alpha_task = alpha_state["tasks"]["T1"]
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "alpha-objective",
            "session_id": "alpha-resume-session",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(alpha_dir / "tasks.md"),
            "todo_path": str(alpha_dir / "todo.md"),
            "subtasks": {
                subtask_id: {
                    "description": subtask["description"],
                    "status": "completed",
                }
                for subtask_id, subtask in alpha_task["subtasks"].items()
            },
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "alpha-objective/T1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Cannot complete T1", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(alpha_state_path.read_bytes(), alpha_bytes)
        self.assertEqual(beta_state_path.read_bytes(), beta_bytes)

    def test_resume_rejects_malformed_ledger_without_runtime_mutation(self) -> None:
        """Only explicit resync may salvage a malformed durable ledger."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        objective_state_path = objective_dir / "execution-state.json"
        base_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        for subtask in base_runtime["subtasks"].values():
            subtask["status"] = "completed"

        for runtime_state in (
            {**base_runtime, "subtasks": {**base_runtime["subtasks"]}},
            {
                **base_runtime,
                "subtasks": {
                    subtask_id: subtask
                    for subtask_id, subtask in base_runtime["subtasks"].items()
                    if subtask_id != "PS1.3"
                },
            },
        ):
            with self.subTest(runtime_ids=sorted(runtime_state["subtasks"])):
                runtime_path.write_text(
                    json.dumps(runtime_state, indent=2), encoding="utf-8"
                )
                objective_state_path.write_text('{"tasks": []}', encoding="utf-8")
                runtime_bytes = runtime_path.read_bytes()
                durable_bytes = objective_state_path.read_bytes()

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "project-state-mvp/PS1",
                    "--continue",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Objective state is invalid", result.stderr)
                self.assertNotIn("TASK COMPLETE", result.stdout)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), runtime_bytes)
                self.assertEqual(objective_state_path.read_bytes(), durable_bytes)

    def test_continue_rejects_missing_or_invalid_session_id(self) -> None:
        """Runtime session_id is required because resume reports and rotates it."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        base_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

        for invalid_session_id in (None, "", []):
            with self.subTest(session_id=invalid_session_id):
                runtime_state = json.loads(json.dumps(base_runtime))
                if invalid_session_id is None:
                    runtime_state.pop("session_id")
                else:
                    runtime_state["session_id"] = invalid_session_id
                runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")
                original_bytes = runtime_path.read_bytes()

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "PS1", "--continue"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Runtime state is invalid", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), original_bytes)

    def test_reconcile_rejects_runtime_missing_primary_required_shape(self) -> None:
        """Reconcile uses the same strict runtime loader as resume and checkpoints."""
        objective_dir = self._materialize_project_state_objective()
        resync = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )
        self.assertEqual(resync.returncode, 0, msg=resync.stdout + resync.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = {
            "task_id": "PS1",
            "objective_slug": "project-state-mvp",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                f"PS1.{index}": {
                    "description": description,
                    "status": "pending",
                }
                for index, description in enumerate(
                    (
                        "Review requirements and design context for PS1",
                        "Implement PS1 end-to-end",
                        "Run validation for PS1",
                    ),
                    start=1,
                )
            },
        }
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        runtime_bytes = runtime_path.read_bytes()
        state_bytes = (objective_dir / "execution-state.json").read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--reconcile", "project-state-mvp/PS1"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runtime state is invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(runtime_path.read_bytes(), runtime_bytes)
        self.assertEqual(
            (objective_dir / "execution-state.json").read_bytes(), state_bytes
        )

    def test_initialization_durable_write_failure_leaves_no_runtime(self) -> None:
        """Runtime is not persisted or launched when durable seeding fails."""
        objective_dir = self._materialize_project_state_objective()
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        objective_dir.chmod(0o500)

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1")
        objective_dir.chmod(0o700)

        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(runtime_path.exists())
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_runtime_commands_reject_invalid_nested_state_without_mutation(
        self,
    ) -> None:
        """All runtime-reading CLI routes must reject malformed nested state safely."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        valid_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        commands = (
            ("--reconcile", "PS1"),
            ("PS1", "--reset-stale"),
            ("--mark-done", "PS1.1"),
            ("--mark-in-progress", "PS1.1"),
        )

        for command in commands:
            with self.subTest(command=command):
                invalid_runtime = {**valid_runtime, "subtasks": []}
                runtime_path.write_text(
                    json.dumps(invalid_runtime, indent=2), encoding="utf-8"
                )
                original_bytes = runtime_path.read_bytes()

                result = self.run_command(str(COMPLETE_TASK_HANDLER), *command)

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Runtime state is invalid", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), original_bytes)

        runtime_path.write_text(
            json.dumps({**valid_runtime, "subtasks": []}, indent=2), encoding="utf-8"
        )
        status_result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")
        self.assertEqual(
            status_result.returncode,
            0,
            msg=status_result.stdout + status_result.stderr,
        )
        self.assertNotIn("Traceback", status_result.stderr)

    def test_continue_accepts_every_supported_runtime_status(self) -> None:
        """Validation must retain all statuses genuinely supported by the handler."""
        self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        base_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))

        for supported_status in (
            "pending",
            "in_progress",
            "completed",
            "failed",
            "skipped",
        ):
            with self.subTest(status=supported_status):
                runtime_state = json.loads(json.dumps(base_runtime))
                runtime_state["subtasks"]["PS1.1"]["status"] = supported_status
                runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "PS1", "--continue"
                )

                self.assertEqual(
                    result.returncode, 0, msg=result.stdout + result.stderr
                )
                self.assertNotIn("Runtime state is invalid", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

        for invalid_status in ("", "unknown-status"):
            with self.subTest(status=invalid_status):
                runtime_state = json.loads(json.dumps(base_runtime))
                runtime_state["subtasks"]["PS1.1"]["status"] = invalid_status
                runtime_path.write_text(json.dumps(runtime_state), encoding="utf-8")

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "PS1", "--continue"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Runtime state is invalid", result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_runtime_rejects_noncanonical_objective_paths(self) -> None:
        """Runtime plan/todo paths must be the canonical files for its objective slug."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        runtime_state = {
            "task_id": "T1",
            "objective_slug": "alpha-objective",
            "session_id": "wrong-path-session",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(beta_dir / "tasks.md"),
            "todo_path": str(beta_dir / "todo.md"),
            "subtasks": {
                f"T1.{index}": {
                    "description": f"Alpha subtask {index}",
                    "status": "pending",
                }
                for index in range(1, 4)
            },
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")
        original_bytes = runtime_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "alpha-objective/T1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Runtime state is invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(runtime_path.read_bytes(), original_bytes)
        self.assertTrue((alpha_dir / "tasks.md").exists())

    def test_fresh_scoped_start_ignores_other_objective_runtime_and_ledger(
        self,
    ) -> None:
        """Fresh alpha/T1 must not project or consume completed beta/T1 state."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        beta_state_path = beta_dir / "execution-state.json"
        beta_state = json.loads(beta_state_path.read_text(encoding="utf-8"))
        beta_task = beta_state["tasks"]["T1"]
        beta_task["status"] = "completed"
        for subtask in beta_task["subtasks"].values():
            subtask["status"] = "completed"
        beta_state_path.write_text(json.dumps(beta_state, indent=2), encoding="utf-8")
        beta_state_bytes = beta_state_path.read_bytes()
        beta_tasks_bytes = (beta_dir / "tasks.md").read_bytes()
        beta_todo_bytes = (beta_dir / "todo.md").read_bytes()
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "beta-objective",
            "session_id": "completed-beta-session",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(beta_dir / "tasks.md"),
            "todo_path": str(beta_dir / "todo.md"),
            "subtasks": {
                subtask_id: {
                    "description": subtask["description"],
                    "status": "completed",
                }
                for subtask_id, subtask in beta_task["subtasks"].items()
            },
        }
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "alpha-objective/T1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        payload_line = next(
            line for line in result.stdout.splitlines() if line.startswith("PAYLOAD:")
        )
        payload = json.loads(payload_line.removeprefix("PAYLOAD:").strip())
        self.assertEqual(payload["objective_slug"], "alpha-objective")
        self.assertEqual(
            [entry["id"] for entry in payload["subtasks"]],
            ["T1.1", "T1.2", "T1.3"],
        )
        self.assertEqual(beta_state_path.read_bytes(), beta_state_bytes)
        self.assertEqual((beta_dir / "tasks.md").read_bytes(), beta_tasks_bytes)
        self.assertEqual((beta_dir / "todo.md").read_bytes(), beta_todo_bytes)
        self.assertTrue((alpha_dir / "execution-state.json").exists())

    def test_resume_normalizes_stale_extra_durable_subtasks(self) -> None:
        """Authorized resume reconciliation must prune stale durable topology."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.STALE"] = {
            "description": "Removed durable subtask",
            "status": "pending",
        }
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        for subtask in runtime_state["subtasks"].values():
            subtask["status"] = "completed"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--continue"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        repaired = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(
            set(repaired["tasks"]["PS1"]["subtasks"]),
            {"PS1.1", "PS1.2", "PS1.3"},
        )

    def test_git_history_is_informational_only_on_fresh_start(self) -> None:
        """Exact-looking commits never promote runtime or durable execution state."""
        objective_dir = self._materialize_generic_objective(
            "alpha-objective", "Alpha Objective"
        )
        resync_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "alpha-objective"
        )
        self.assertEqual(
            resync_result.returncode,
            0,
            msg=resync_result.stdout + resync_result.stderr,
        )
        dummy_path = self.temp_dir / "git-recovery.txt"
        for index in range(1, 4):
            dummy_path.write_text(f"version {index}\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "git-recovery.txt"],
                cwd=self.temp_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"feat(alpha-objective): T1.{index} recovered work",
                ],
                cwd=self.temp_dir,
                check=True,
                capture_output=True,
            )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "alpha-objective/T1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("GIT_INFO: 3/3", result.stdout)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertIn("LAUNCH: task-executor", result.stdout)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        self.assertTrue(runtime_path.exists())
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertTrue(
            all(
                subtask["status"] == "pending"
                for subtask in runtime_state["subtasks"].values()
            )
        )
        objective_state = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(objective_state["tasks"]["T1"]["status"], "pending")
        self.assertTrue(
            all(
                subtask["status"] == "pending"
                for subtask in objective_state["tasks"]["T1"]["subtasks"].values()
            )
        )

    def test_git_history_does_not_project_or_complete_malformed_acceptance(
        self,
    ) -> None:
        """Informational commits do not touch execution or acceptance state."""
        objective_dir = self._materialize_generic_objective(
            "alpha-objective", "Alpha Objective"
        )
        resync = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "alpha-objective"
        )
        self.assertEqual(resync.returncode, 0, msg=resync.stdout + resync.stderr)
        tasks_path = objective_dir / "tasks.md"
        tasks_text = tasks_path.read_text(encoding="utf-8")
        t1_start = tasks_text.index("## T1:")
        t1_end = tasks_text.index("## T2:")
        t1_section = tasks_text[t1_start:t1_end].replace("- [ ]", "- [x]")
        t1_section = t1_section.replace("- [x]", "- [z]", 1)
        tasks_path.write_text(
            tasks_text[:t1_start] + t1_section + tasks_text[t1_end:],
            encoding="utf-8",
        )
        for index in range(1, 4):
            marker = self.temp_dir / "git-advisory.txt"
            marker.write_text(f"version {index}\n", encoding="utf-8")
            subprocess.run(
                ["git", "add", "git-advisory.txt"],
                cwd=self.temp_dir,
                check=True,
                capture_output=True,
            )
            subprocess.run(
                [
                    "git",
                    "commit",
                    "-m",
                    f"feat(alpha-objective): T1.{index} recovered work",
                ],
                cwd=self.temp_dir,
                check=True,
                capture_output=True,
            )

        malformed_tasks = tasks_path.read_bytes()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "alpha-objective/T1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("GIT_INFO: 3/3", result.stdout)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(tasks_path.read_bytes(), malformed_tasks)
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["T1"]
        self.assertTrue(
            all(child["status"] == "pending" for child in durable["subtasks"].values())
        )

    def test_fresh_git_recovery_rolls_back_on_late_prerequisite_failure(self) -> None:
        """Late prerequisite failure rolls back even when Git history is present."""
        objective_dir = self._materialize_generic_objective(
            "late-git-failure", "Late Git Failure"
        )
        resync = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "late-git-failure"
        )
        self.assertEqual(resync.returncode, 0, msg=resync.stdout + resync.stderr)
        marker = self.temp_dir / "late-git-recovery.txt"
        marker.write_text("recovered\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", marker.name],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "feat(late-git-failure): T1.1 recovered work",
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        commands_dir = self.temp_dir / ".claude" / "commands" / "mm"
        commands_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / "complete-task-handler.py").write_text(
            "# present\n", encoding="utf-8"
        )
        tracked = (
            self.temp_dir / ".mm-flow" / "planning" / "task-progress.json",
            objective_dir / "execution-state.json",
            objective_dir / "tasks.md",
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {
            path: path.read_bytes() if path.exists() else None for path in tracked
        }

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "late-git-failure/T1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FLOW BLOCKED", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        for path, original in before.items():
            if original is None:
                self.assertFalse(path.exists())
            else:
                self.assertEqual(path.read_bytes(), original)

    def test_objective_artifact_symlink_escapes_are_rejected(self) -> None:
        """Every objective artifact must resolve inside its objective directory."""
        objective_dir = self._materialize_generic_objective(
            "escape-artifacts", "Escape Artifacts"
        )
        initial = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "escape-artifacts"
        )
        self.assertEqual(initial.returncode, 0, msg=initial.stdout + initial.stderr)
        for artifact_name in (
            "tasks.md",
            "todo.md",
            "execution-state.json",
            "HANDOFF-CURRENT.md",
        ):
            with self.subTest(artifact=artifact_name):
                external = self.temp_dir / f"external-{artifact_name}"
                local = objective_dir / artifact_name
                local_bytes = local.read_bytes()
                external.write_bytes(local_bytes)
                local.unlink()
                local.symlink_to(external)
                external_bytes = external.read_bytes()

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    "escape-artifacts",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must stay within objective", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(external.read_bytes(), external_bytes)
                local.unlink()
                local.write_bytes(local_bytes)

    def test_plan_topology_rejects_missing_malformed_and_duplicate_ids(self) -> None:
        """Plan topology is explicit, unique, and fail-closed."""
        objective_dir = self._materialize_generic_objective(
            "topology-invalid", "Topology Invalid"
        )
        tasks_path = objective_dir / "tasks.md"
        valid_tasks = tasks_path.read_text(encoding="utf-8")
        mutations = {
            "malformed": lambda text: text.replace(
                "- T1.1: Review requirements and design context for T1",
                "- malformed execution child",
                1,
            ),
            "duplicate-subtask": lambda text: text.replace(
                "- T1.2: Implement T1 end-to-end",
                "- T1.1: Duplicate child",
                1,
            ),
            "duplicate-root": lambda text: text
            + "\n## T1: Duplicate root\n### Execution Subtasks\n- T1.9: Duplicate root child\n\n",
        }
        for label, mutate in mutations.items():
            with self.subTest(case=label):
                tasks_path.write_text(mutate(valid_tasks), encoding="utf-8")
                before = {
                    path: path.read_bytes()
                    for path in (
                        tasks_path,
                        objective_dir / "todo.md",
                        objective_dir / "HANDOFF-CURRENT.md",
                    )
                }

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER),
                    "--resync-objective",
                    "topology-invalid",
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("topology", result.stderr.lower())
                self.assertNotIn("Traceback", result.stderr)
                for path, original in before.items():
                    self.assertEqual(path.read_bytes(), original)
                tasks_path.write_text(valid_tasks, encoding="utf-8")

    def test_legacy_todo_topology_is_used_only_when_plan_topology_is_absent(
        self,
    ) -> None:
        """Legacy packages may derive exact scoped children from todo.md."""
        objective_dir = self._materialize_generic_objective(
            "legacy-topology", "Legacy Topology"
        )
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            re.sub(
                r"^### Execution Subtasks\n.*?(?=^### )",
                "",
                tasks_path.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            ),
            encoding="utf-8",
        )
        self._set_legacy_todo_topology(
            objective_dir,
            "T1",
            [
                (" ", "T1.1", "Inspect the legacy objective boundary"),
                (" ", "T1.2", "Implement the legacy objective slice"),
                (" ", "T1.3", "Validate the legacy objective slice"),
            ],
        )
        for task_id in ("T2", "T3"):
            entries = [
                (f"{task_id}.1", f"Inspect legacy requirements for {task_id}"),
                (f"{task_id}.2", f"Implement legacy behavior for {task_id}"),
                (f"{task_id}.3", f"Validate legacy behavior for {task_id}"),
            ]
            self._set_task_topology(objective_dir, task_id, entries)
            self._set_legacy_todo_topology(
                objective_dir,
                task_id,
                [(" ", subtask_id, description) for subtask_id, description in entries],
            )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "legacy-topology/T1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("LAUNCH: task-executor", result.stdout)

    def test_checked_legacy_todo_children_seed_pending_durable_state(self) -> None:
        """Legacy checkboxes contribute topology, never completion truth."""
        objective_dir = self._materialize_generic_objective(
            "checked-legacy", "Checked Legacy"
        )
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            re.sub(
                r"^### Execution Subtasks\n.*?(?=^### )",
                "",
                tasks_path.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            ),
            encoding="utf-8",
        )
        self._set_legacy_todo_topology(
            objective_dir,
            "T1",
            [
                ("x", "T1.1", "Inspect checked legacy requirements"),
                ("x", "T1.2", "Implement checked legacy behavior"),
                ("x", "T1.3", "Validate checked legacy behavior"),
            ],
        )
        for task_id in ("T2", "T3"):
            entries = [
                (f"{task_id}.1", f"Inspect checked requirements for {task_id}"),
                (f"{task_id}.2", f"Implement checked behavior for {task_id}"),
                (f"{task_id}.3", f"Validate checked behavior for {task_id}"),
            ]
            self._set_task_topology(objective_dir, task_id, entries)
            self._set_legacy_todo_topology(
                objective_dir,
                task_id,
                [(" ", subtask_id, description) for subtask_id, description in entries],
            )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "checked-legacy"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )
        self.assertTrue(
            all(
                child["status"] == "pending"
                for child in durable["tasks"]["T1"]["subtasks"].values()
            )
        )

    def test_legacy_todo_topology_rejects_mixed_valid_and_malformed_children(
        self,
    ) -> None:
        """One valid legacy child cannot hide a malformed child-like sibling."""
        objective_dir = self._materialize_generic_objective(
            "malformed-legacy-topology", "Malformed Legacy Topology"
        )
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            re.sub(
                r"^### Execution Subtasks\n.*?(?=^### )",
                "",
                tasks_path.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            ),
            encoding="utf-8",
        )
        self._set_legacy_todo_topology(
            objective_dir,
            "T1",
            [
                (" ", "T1.1", "Inspect malformed legacy requirements"),
                (" ", "T1.two", "malformed child"),
            ],
        )
        todo_path = objective_dir / "todo.md"
        before = todo_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "malformed-legacy-topology/T1"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Malformed todo topology", result.stderr)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertEqual(todo_path.read_bytes(), before)

    def test_topology_conflict_between_plan_and_todo_fails_before_mutation(
        self,
    ) -> None:
        """Two explicit topology sources must agree exactly."""
        objective_dir = self._materialize_generic_objective(
            "conflicting-topology", "Conflicting Topology"
        )
        self._set_task_topology(
            objective_dir,
            "T1",
            [
                ("T1.1", "Inspect conflict requirements"),
                ("T1.2", "Implement conflict behavior"),
                ("T1.3", "Validate conflict behavior"),
            ],
        )
        self._set_legacy_todo_topology(
            objective_dir,
            "T1",
            [
                (" ", "T1.1", "Conflicting legacy description"),
                (" ", "T1.2", "Implement conflict behavior"),
                (" ", "T1.3", "Validate conflict behavior"),
            ],
        )
        todo_path = objective_dir / "todo.md"
        before = todo_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "conflicting-topology"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conflict", result.stderr.lower())
        self.assertEqual(todo_path.read_bytes(), before)

    def test_missing_plan_and_legacy_todo_topology_fails_closed(self) -> None:
        """The migration path never synthesizes generic child work."""
        objective_dir = self._materialize_generic_objective(
            "missing-topology", "Missing Topology"
        )
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            re.sub(
                r"^### Execution Subtasks\n.*?(?=^### )",
                "",
                tasks_path.read_text(encoding="utf-8"),
                count=1,
                flags=re.MULTILINE | re.DOTALL,
            ),
            encoding="utf-8",
        )
        todo_path = objective_dir / "todo.md"
        todo_path.write_text(
            re.sub(
                r"^  - \[[ x~]\] T1\.\d+:.*$",
                "",
                todo_path.read_text(encoding="utf-8").replace(
                    "<!-- topology-source: tasks.md -->\n\n", "", 1
                ),
                flags=re.MULTILINE,
            ),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "missing-topology/T1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("only a scaffold", result.stderr)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)

    def test_later_task_cannot_bootstrap_without_prior_durable_evidence(self) -> None:
        """A later root task requires durable proof for every predecessor."""
        objective_dir = self._materialize_project_state_objective()
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        before = (objective_dir / "todo.md").read_bytes()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS2")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("no durable completion evidence", result.stderr)
        self.assertFalse(runtime_path.exists())
        self.assertEqual((objective_dir / "todo.md").read_bytes(), before)

    def test_duplicate_execution_checklists_fail_before_resync_mutation(self) -> None:
        """Ambiguous duplicate projected sections are rejected fail-closed."""
        objective_dir = self._materialize_generic_objective(
            "duplicate-checklist", "Duplicate Checklist"
        )
        todo_path = objective_dir / "todo.md"
        todo_path.write_text(
            todo_path.read_text(encoding="utf-8")
            + "\n## Execution Checklist\n\n- [ ] T1: Duplicate\n",
            encoding="utf-8",
        )
        tracked = (
            todo_path,
            objective_dir / "tasks.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "duplicate-checklist"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate Execution Checklist", result.stderr)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_reconcile_rolls_back_when_acceptance_projection_fails(self) -> None:
        """Reconcile is one transaction across runtime, ledger, and projections."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        for subtask in runtime["subtasks"].values():
            subtask["status"] = "completed"
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace("- [ ]", "- [z]", 1),
            encoding="utf-8",
        )
        tracked = (
            runtime_path,
            objective_dir / "execution-state.json",
            tasks_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--reconcile", "PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("RECONCILED", result.stdout)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_prior_task_gate_requires_exact_durable_children(self) -> None:
        """A completed parent cannot satisfy acceptance with a pending planned child."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.unlink()
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["tasks"]["PS1"]["status"] = "completed"
        state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "pending"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace("- [ ]", "- [x]"),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS2")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance criteria are not satisfied", result.stderr)
        self.assertFalse(runtime_path.exists())
        self.assertNotIn("Traceback", result.stderr)

    def test_mark_done_rolls_back_state_and_projection_on_acceptance_failure(
        self,
    ) -> None:
        """A failed final projection must leave checkpoint artifacts byte-identical."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        for subtask_id in ("PS1.1", "PS1.2"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", subtask_id
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace("- [ ]", "- [z]", 1),
            encoding="utf-8",
        )
        tracked = (
            self.temp_dir / ".mm-flow" / "planning" / "task-progress.json",
            objective_dir / "execution-state.json",
            tasks_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.3")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_objective_symlink_escape_is_rejected_without_writes(self) -> None:
        """A safe-named objective symlink must not escape the resolved changes directory."""
        source_dir = self._materialize_generic_objective(
            "source-objective", "Source Objective"
        )
        external_root = Path(tempfile.mkdtemp(prefix="mm-objective-external-"))
        self.addCleanup(shutil.rmtree, external_root)
        external_objective = external_root / "escape-objective"
        shutil.copytree(source_dir, external_objective)
        escape_path = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "escape-objective"
        )
        escape_path.symlink_to(external_objective, target_is_directory=True)
        self.assertFalse((external_objective / "execution-state.json").exists())

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "escape-objective"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("canonical directory", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse((external_objective / "execution-state.json").exists())

    def test_resync_preserves_durable_completed_status_over_stale_todo(self) -> None:
        """Unchecked projected todo state must not regress durable completion evidence."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        task_state = objective_state["tasks"]["PS1"]
        task_state["status"] = "completed"
        task_state["completed_at"] = "2026-06-01T10:00:00"
        for subtask in task_state["subtasks"].values():
            subtask["status"] = "completed"
            subtask["completed_at"] = "2026-06-01T10:00:00"
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "--resync-objective",
            "project-state-mvp",
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        repaired_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        repaired_task = repaired_state["tasks"]["PS1"]
        self.assertEqual(repaired_task["status"], "completed")
        self.assertEqual(repaired_task["completed_at"], "2026-06-01T10:00:00")
        self.assertTrue(
            all(
                subtask["status"] == "completed"
                for subtask in repaired_task["subtasks"].values()
            )
        )

    def test_resync_write_failure_is_controlled_and_does_not_project(self) -> None:
        """Resync cannot emit success after durable persistence fails."""
        objective_dir = self._materialize_project_state_objective()
        tracked = (objective_dir / "todo.md", objective_dir / "HANDOFF-CURRENT.md")
        before = {path: path.read_bytes() for path in tracked}
        objective_dir.chmod(0o500)

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )
        objective_dir.chmod(0o700)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("persist", result.stderr.lower())
        self.assertNotIn("RESYNCED", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_resync_normalizes_active_runtime_to_exact_plan(self) -> None:
        """Successful resync persists exact active runtime topology."""
        self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["subtasks"].pop("PS1.3")
        runtime["subtasks"]["PS1.99"] = {
            "description": "Removed child",
            "status": "pending",
        }
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertEqual(set(normalized["subtasks"]), {"PS1.1", "PS1.2", "PS1.3"})
        self.assertEqual(normalized["subtasks"]["PS1.3"]["status"], "pending")

    def test_resync_projects_exact_added_and_removed_todo_topology(self) -> None:
        """Todo projection exactly follows plan additions and removals."""
        objective_dir = self._materialize_project_state_objective()
        first = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)
        self._set_task_topology(
            objective_dir,
            "PS1",
            [
                ("PS1.1", "Review requirements and design context for PS1"),
                ("PS1.2", "Implement PS1 end-to-end"),
                ("PS1.4", "New exact projected child"),
            ],
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        todo = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn("PS1.4: New exact projected child", todo)
        self.assertNotIn("PS1.3:", todo)

    def test_reset_stale_normalizes_runtime_and_durable_then_projects(self) -> None:
        """Reset-stale updates both authoritative stores and the todo projection."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        progress = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
        )
        self.assertEqual(progress.returncode, 0, msg=progress.stdout + progress.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["subtasks"]["PS1.1"]["started_at"] = "2020-01-01T00:00:00"
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--reset-stale"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["PS1"]
        self.assertEqual(runtime["subtasks"]["PS1.1"]["status"], "pending")
        self.assertEqual(durable["subtasks"]["PS1.1"]["status"], "pending")
        self.assertEqual(durable["status"], "pending")
        self.assertIn(
            "- [ ] PS1.1:", (objective_dir / "todo.md").read_text(encoding="utf-8")
        )

    def test_reset_stale_rolls_back_when_projection_fails(self) -> None:
        """Any reset-stale projection failure restores every artifact and fails."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        progress = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
        )
        self.assertEqual(progress.returncode, 0, msg=progress.stdout + progress.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["subtasks"]["PS1.1"]["started_at"] = "2020-01-01T00:00:00"
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        todo_path = objective_dir / "todo.md"
        todo_path.write_text(
            todo_path.read_text(encoding="utf-8")
            + "\n## Execution Checklist\n\n- [ ] PS1: Duplicate\n",
            encoding="utf-8",
        )
        tracked = (
            runtime_path,
            objective_dir / "execution-state.json",
            objective_dir / "tasks.md",
            todo_path,
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--reset-stale"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("duplicate Execution Checklist", result.stderr)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_reset_stale_without_stale_children_is_byte_identical(self) -> None:
        """The no-stale reset branch is a read-only observation."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        tracked = (
            self.temp_dir / ".mm-flow" / "planning" / "task-progress.json",
            objective_dir / "execution-state.json",
            objective_dir / "tasks.md",
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--reset-stale"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("No stale subtasks found", result.stdout)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_reset_stale_safely_ignores_child_removed_by_normalization(self) -> None:
        """A stale runtime child removed from the plan cannot crash reset."""
        self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["subtasks"]["PS1.99"] = {
            "description": "Removed stale child",
            "status": "in_progress",
            "started_at": "2020-01-01T00:00:00",
            "completed_at": None,
            "duration_seconds": 0,
        }
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--reset-stale"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        normalized = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertNotIn("PS1.99", normalized["subtasks"])

    def test_status_scopes_duplicate_task_ids_per_objective(self) -> None:
        """Status must render duplicate task IDs independently and deterministically."""
        self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertLess(
            result.stdout.index("[alpha-objective]"),
            result.stdout.index("[beta-objective]"),
        )
        self.assertEqual(result.stdout.count("    T1 "), 2)

    def test_status_rejects_malformed_durable_state_before_projection(self) -> None:
        """Status must validate every ledger before creating or syncing projections."""
        objective_dir = self._materialize_project_state_objective()
        state_path = objective_dir / "execution-state.json"
        state_path.write_text('{"tasks": []}', encoding="utf-8")
        tracked_paths = (
            state_path,
            objective_dir / "tasks.md",
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked_paths}

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Objective state is invalid", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_status_accepts_planned_ledger_without_subtasks_read_only(self) -> None:
        """Pre-execution planned ledgers render pending without projection writes."""
        objective_dir = self._materialize_generic_objective(
            "planned-ledger", "Planned Ledger"
        )
        state_path = objective_dir / "execution-state.json"
        state_path.write_text(
            json.dumps(
                {
                    "objective_slug": "planned-ledger",
                    "status": "planned",
                    "tasks": {
                        "T1": {"status": "pending", "depends_on": []},
                        "T2": {"status": "pending", "depends_on": ["T1"]},
                        "T3": {"status": "pending", "depends_on": ["T2"]},
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        tracked = (
            state_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("T1 [ ] 0/0", result.stdout)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_no_subtasks_shape_is_rejected_outside_planned_pending_scope(self) -> None:
        """Loose task entries never validate as active or completed durable progress."""
        objective_dir = self._materialize_generic_objective(
            "strict-ledger", "Strict Ledger"
        )
        state_path = objective_dir / "execution-state.json"
        cases = (
            ("active", {"status": "pending", "depends_on": []}),
            ("planned", {"status": "completed", "depends_on": []}),
            (None, {"status": "pending", "depends_on": []}),
            ("planned", {"status": "pending", "depends_on": [""]}),
            ("planned", {"status": "pending", "depends_on": "T0"}),
        )
        for objective_status, task_entry in cases:
            with self.subTest(
                objective_status=objective_status, task_status=task_entry["status"]
            ):
                state = {
                    "objective_slug": "strict-ledger",
                    "tasks": {"T1": task_entry},
                }
                if objective_status is not None:
                    state["status"] = objective_status
                state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                before = state_path.read_bytes()

                result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Objective state is invalid", result.stderr)
                self.assertEqual(state_path.read_bytes(), before)

    def test_first_start_materializes_strict_task_from_planned_ledger(self) -> None:
        """Execution seeding upgrades the selected planned root before launch."""
        objective_dir = self._materialize_generic_objective(
            "planned-start", "Planned Start"
        )
        state_path = objective_dir / "execution-state.json"
        state_path.write_text(
            json.dumps(
                {
                    "objective_slug": "planned-start",
                    "status": "planned",
                    "tasks": {
                        "T1": {"status": "pending", "depends_on": []},
                        "T2": {"status": "pending", "depends_on": ["T1"]},
                        "T3": {"status": "pending", "depends_on": ["T2"]},
                    },
                },
                indent=2,
            ),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "planned-start/T1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("LAUNCH: task-executor", result.stdout)
        seeded = json.loads(state_path.read_text(encoding="utf-8"))
        self.assertEqual(seeded["status"], "active")
        for task_id in ("T1", "T2", "T3"):
            task = seeded["tasks"][task_id]
            self.assertEqual(
                set(task["subtasks"]),
                {f"{task_id}.1", f"{task_id}.2", f"{task_id}.3"},
            )
            self.assertIn("started_at", task)
            self.assertIn("completed_at", task)
        status = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")
        self.assertEqual(status.returncode, 0, msg=status.stdout + status.stderr)

    def test_status_rolls_back_all_objective_projections_on_late_failure(self) -> None:
        """Status projection is one transaction across all validated objectives."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for slug in ("alpha-objective", "beta-objective"):
            resync = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", slug
            )
            self.assertEqual(resync.returncode, 0, msg=resync.stdout + resync.stderr)
        alpha_todo = alpha_dir / "todo.md"
        alpha_todo.write_text(
            alpha_todo.read_text(encoding="utf-8").replace("- [ ] T1:", "- [x] T1:", 1),
            encoding="utf-8",
        )
        beta_todo = beta_dir / "todo.md"
        beta_todo.write_text(
            beta_todo.read_text(encoding="utf-8")
            + "\n## Execution Checklist\n\n- [ ] T1: Duplicate\n",
            encoding="utf-8",
        )
        tracked = (
            alpha_todo,
            alpha_dir / "HANDOFF-CURRENT.md",
            beta_todo,
            beta_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("Traceback", result.stderr)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_status_never_uses_todo_checkbox_as_completion_authority(self) -> None:
        """Without a durable task entry, checked todo remains pending/unknown."""
        objective_dir = self._materialize_generic_objective(
            "status-authority", "Status Authority"
        )
        todo_path = objective_dir / "todo.md"
        todo_path.write_text(
            todo_path.read_text(encoding="utf-8").replace("- [ ] T1:", "- [x] T1:", 1),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--status")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("T1 [ ] 0/0", result.stdout)
        self.assertNotIn("T1 ✅", result.stdout)

    def test_scoped_reconcile_and_reset_reject_other_objective_runtime(self) -> None:
        """Scoped mutators must reject same-ID runtime from another objective before writes."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "beta-objective",
            "session_id": "beta-mutator-session",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(beta_dir / "tasks.md"),
            "todo_path": str(beta_dir / "todo.md"),
            "subtasks": {
                "T1.1": {
                    "description": "Review requirements and design context for T1",
                    "status": "in_progress",
                    "started_at": "2020-01-01T00:00:00",
                    "retries": 0,
                },
                "T1.2": {
                    "description": "Implement T1 end-to-end",
                    "status": "pending",
                },
                "T1.3": {
                    "description": "Run validation for T1",
                    "status": "pending",
                },
            },
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        for command in (
            ("--reconcile", "alpha-objective/T1"),
            ("alpha-objective/T1", "--reset-stale"),
        ):
            with self.subTest(command=command):
                before = {
                    "runtime": runtime_path.read_bytes(),
                    "alpha_todo": (alpha_dir / "todo.md").read_bytes(),
                    "beta_todo": (beta_dir / "todo.md").read_bytes(),
                }
                result = self.run_command(str(COMPLETE_TASK_HANDLER), *command)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("belongs to objective `beta-objective`", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), before["runtime"])
                self.assertEqual(
                    (alpha_dir / "todo.md").read_bytes(), before["alpha_todo"]
                )
                self.assertEqual(
                    (beta_dir / "todo.md").read_bytes(), before["beta_todo"]
                )

    def test_bare_reset_stale_rejects_duplicate_task_before_mutation(self) -> None:
        """Bare reset must resolve duplicate task IDs before changing runtime."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "alpha-objective",
            "session_id": "ambiguous-reset",
            "started_at": "2020-01-01T00:00:00",
            "plan_path": str(alpha_dir / "tasks.md"),
            "todo_path": str(alpha_dir / "todo.md"),
            "subtasks": {
                "T1.1": {
                    "description": "Review requirements and design context for T1",
                    "status": "in_progress",
                    "started_at": "2020-01-01T00:00:00",
                    "retries": 0,
                },
                "T1.2": {"description": "Implement T1 end-to-end", "status": "pending"},
                "T1.3": {"description": "Run validation for T1", "status": "pending"},
            },
        }
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")
        before = {
            "runtime": runtime_path.read_bytes(),
            "alpha_todo": (alpha_dir / "todo.md").read_bytes(),
            "beta_todo": (beta_dir / "todo.md").read_bytes(),
        }

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--reset-stale", "T1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ambiguous across active objectives", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(runtime_path.read_bytes(), before["runtime"])
        self.assertEqual((alpha_dir / "todo.md").read_bytes(), before["alpha_todo"])
        self.assertEqual((beta_dir / "todo.md").read_bytes(), before["beta_todo"])

    def test_runtime_normalization_prunes_pending_extra_and_materializes_missing(
        self,
    ) -> None:
        """Runtime topology must normalize exactly to the current planned contract."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_state = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime_state["subtasks"]["PS1.1"]["status"] = "completed"
        runtime_state["subtasks"]["PS1.2"]["status"] = "completed"
        runtime_state["subtasks"].pop("PS1.3")
        runtime_state["subtasks"]["PS1.99"] = {
            "description": "Stale pending runtime entry",
            "status": "pending",
        }
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--continue"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        normalized = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertEqual(set(normalized["subtasks"]), {"PS1.1", "PS1.2", "PS1.3"})
        self.assertEqual(normalized["subtasks"]["PS1.3"]["status"], "pending")
        self.assertEqual(
            normalized["subtasks"]["PS1.3"]["description"],
            "Run validation for PS1",
        )
        payload_line = next(
            line for line in result.stdout.splitlines() if line.startswith("PAYLOAD:")
        )
        payload = json.loads(payload_line.removeprefix("PAYLOAD:").strip())
        self.assertEqual([entry["id"] for entry in payload["subtasks"]], ["PS1.3"])
        objective_state = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            set(objective_state["tasks"]["PS1"]["subtasks"]),
            {"PS1.1", "PS1.2", "PS1.3"},
        )

    def test_mark_done_normalizes_expanded_plan_before_parent_completion(self) -> None:
        """Mark-done must add a new planned child before aggregating its parent."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        for subtask_id in ("PS1.1", "PS1.2"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", subtask_id
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self._set_task_topology(
            objective_dir,
            "PS1",
            [
                ("PS1.1", "Review requirements and design context for PS1"),
                ("PS1.2", "Implement PS1 end-to-end"),
                ("PS1.3", "Run validation for PS1"),
                ("PS1.4", "Validate expanded plan contract"),
            ],
        )
        tasks_path = objective_dir / "tasks.md"

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.3")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime = json.loads(
            (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").read_text(
                encoding="utf-8"
            )
        )
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["PS1"]
        self.assertEqual(set(runtime["subtasks"]), {"PS1.1", "PS1.2", "PS1.3", "PS1.4"})
        self.assertEqual(set(durable["subtasks"]), set(runtime["subtasks"]))
        self.assertEqual(runtime["subtasks"]["PS1.4"]["status"], "pending")
        self.assertNotEqual(durable["status"], "completed")
        ps1_section = (
            tasks_path.read_text(encoding="utf-8")
            .split("## PS1:", 1)[1]
            .split("## PS2:", 1)[0]
        )
        self.assertIn("- [ ]", ps1_section)

    def test_mark_in_progress_materializes_new_planned_child(self) -> None:
        """Mark-in-progress must normalize new plan children into both state stores."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        self._set_task_topology(
            objective_dir,
            "PS1",
            [
                ("PS1.1", "Review requirements and design context for PS1"),
                ("PS1.2", "Implement PS1 end-to-end"),
                ("PS1.3", "Run validation for PS1"),
                ("PS1.4", "Validate expanded plan contract"),
            ],
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.4"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime = json.loads(
            (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").read_text(
                encoding="utf-8"
            )
        )
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["PS1"]
        self.assertEqual(runtime["subtasks"]["PS1.4"]["status"], "in_progress")
        self.assertEqual(durable["subtasks"]["PS1.4"]["status"], "in_progress")
        self.assertEqual(set(durable["subtasks"]), set(runtime["subtasks"]))
        self.assertEqual(durable["status"], "in_progress")

    def test_reconcile_normalizes_exact_state_then_projects_from_durable(self) -> None:
        """Reconcile must persist exact plan-scoped durable truth before projections."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["subtasks"]["PS1.1"]["status"] = "completed"
        runtime["subtasks"].pop("PS1.3")
        runtime["subtasks"]["PS1.99"] = {
            "description": "Removed runtime child",
            "status": "completed",
        }
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]["status"] = "completed"
        state_path.write_text(json.dumps(objective_state, indent=2), encoding="utf-8")
        todo_path = objective_dir / "todo.md"
        todo_path.write_text(
            todo_path.read_text(encoding="utf-8").replace("- [ ] PS1", "- [x] PS1"),
            encoding="utf-8",
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--reconcile", "project-state-mvp/PS1"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        normalized_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["PS1"]
        expected = {"PS1.1", "PS1.2", "PS1.3"}
        self.assertEqual(set(normalized_runtime["subtasks"]), expected)
        self.assertEqual(set(durable["subtasks"]), expected)
        self.assertEqual(durable["subtasks"]["PS1.1"]["status"], "completed")
        self.assertEqual(normalized_runtime["subtasks"]["PS1.2"]["status"], "completed")
        self.assertEqual(durable["subtasks"]["PS1.2"]["status"], "completed")
        self.assertEqual(durable["subtasks"]["PS1.3"]["status"], "pending")
        todo = todo_path.read_text(encoding="utf-8")
        self.assertIn("- [~] PS1:", todo)
        self.assertIn("- [x] PS1.1:", todo)
        self.assertIn("- [ ] PS1.3:", todo)
        self.assertNotIn("PS1.99", todo)

    def test_resync_preserves_valid_noncompleted_statuses_and_metadata(self) -> None:
        """Resync must salvage valid durable fields without todo-driven regression."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.unlink()
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        statuses = {
            "PS1.1": "in_progress",
            "PS1.2": "failed",
            "PS1.3": "skipped",
        }
        for index, (subtask_id, status) in enumerate(statuses.items(), start=1):
            subtask = task["subtasks"][subtask_id]
            subtask["status"] = status
            subtask["started_at"] = f"2026-06-01T09:0{index}:00"
            subtask["duration_seconds"] = index * 10
        task["status"] = "failed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        repaired = json.loads(state_path.read_text(encoding="utf-8"))
        repaired_task = repaired["tasks"]["PS1"]
        self.assertEqual(repaired_task["status"], "failed")
        for index, (subtask_id, status) in enumerate(statuses.items(), start=1):
            self.assertEqual(repaired_task["subtasks"][subtask_id]["status"], status)
            self.assertEqual(
                repaired_task["subtasks"][subtask_id]["started_at"],
                f"2026-06-01T09:0{index}:00",
            )
            self.assertEqual(
                repaired_task["subtasks"][subtask_id]["duration_seconds"],
                index * 10,
            )

    def test_new_planned_child_reopens_completed_parent_and_acceptance(self) -> None:
        """Completed parent is sticky only while every current planned child is completed."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        task["status"] = "completed"
        for subtask in task["subtasks"].values():
            subtask["status"] = "completed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self._set_task_topology(
            objective_dir,
            "PS1",
            [
                ("PS1.1", "Review requirements and design context for PS1"),
                ("PS1.2", "Implement PS1 end-to-end"),
                ("PS1.3", "Run validation for PS1"),
                ("PS1.4", "Validate newly added contract"),
            ],
        )
        tasks_path = objective_dir / "tasks.md"

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        repaired = json.loads(state_path.read_text(encoding="utf-8"))
        repaired_task = repaired["tasks"]["PS1"]
        self.assertEqual(
            set(repaired_task["subtasks"]), {"PS1.1", "PS1.2", "PS1.3", "PS1.4"}
        )
        self.assertEqual(repaired_task["subtasks"]["PS1.4"]["status"], "pending")
        self.assertNotEqual(repaired_task["status"], "completed")
        ps1_section = tasks_path.read_text(encoding="utf-8").split("## PS1:", 1)[1]
        self.assertIn("- [ ]", ps1_section.split("## PS2:", 1)[0])

    def test_fresh_start_reopens_parent_when_plan_adds_pending_child(self) -> None:
        """Fresh seeding recomputes the parent before acceptance projection."""
        objective_dir = self._materialize_project_state_objective()
        first = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.unlink()
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        task["status"] = "completed"
        for child in task["subtasks"].values():
            child["status"] = "completed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        self._set_task_topology(
            objective_dir,
            "PS1",
            [
                ("PS1.1", "Review requirements and design context for PS1"),
                ("PS1.2", "Implement PS1 end-to-end"),
                ("PS1.3", "Run validation for PS1"),
                ("PS1.4", "New pending contract child"),
            ],
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("PS1.4", result.stdout)
        repaired = json.loads(state_path.read_text(encoding="utf-8"))["tasks"]["PS1"]
        self.assertEqual(repaired["status"], "in_progress")
        tasks_text = (objective_dir / "tasks.md").read_text(encoding="utf-8")
        ps1 = tasks_text.split("## PS1:", 1)[1].split("## PS2:", 1)[0]
        self.assertIn("- [ ]", ps1)

    def test_bare_ambiguous_start_is_read_only_before_resolution(self) -> None:
        """Bare duplicate task resolution must fail before runtime/todo reconciliation."""
        alpha_dir, beta_dir = self._materialize_two_generic_objectives()
        for objective_slug in ("alpha-objective", "beta-objective"):
            result = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--resync-objective", objective_slug
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        runtime_state = {
            "task_id": "T1",
            "objective_slug": "alpha-objective",
            "session_id": "ambiguous-runtime",
            "started_at": "2026-06-01T09:00:00",
            "plan_path": str(alpha_dir / "tasks.md"),
            "todo_path": str(alpha_dir / "todo.md"),
            "subtasks": {
                f"T1.{index}": {
                    "description": description,
                    "status": "completed",
                }
                for index, description in enumerate(
                    (
                        "Review requirements and design context for T1",
                        "Implement T1 end-to-end",
                        "Run validation for T1",
                    ),
                    start=1,
                )
            },
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")
        before = {
            "runtime": runtime_path.read_bytes(),
            "alpha_todo": (alpha_dir / "todo.md").read_bytes(),
            "beta_todo": (beta_dir / "todo.md").read_bytes(),
        }

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "T1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ambiguous across active objectives", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(runtime_path.read_bytes(), before["runtime"])
        self.assertEqual((alpha_dir / "todo.md").read_bytes(), before["alpha_todo"])
        self.assertEqual((beta_dir / "todo.md").read_bytes(), before["beta_todo"])

    def test_normal_flow_rejects_malformed_durable_fields_and_resync_salvages(
        self,
    ) -> None:
        """Normal reads reject malformed durable fields; resync salvages fields independently."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.unlink()
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        subtasks = state["tasks"]["PS1"]["subtasks"]
        subtasks["PS1.1"].update(
            {
                "status": "completed",
                "description": ["invalid"],
                "started_at": "2026-06-01T09:00:00",
                "duration_seconds": -5,
                "poison": {"must": "not survive"},
            }
        )
        subtasks["PS1.2"]["status"] = "unknown"
        subtasks["PS1.3"].update(
            {
                "status": "failed",
                "description": "Run validation for PS1",
                "duration_seconds": 30,
            }
        )
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        malformed_bytes = state_path.read_bytes()

        normal_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--brief", "project-state-mvp/PS1"
        )
        self.assertNotEqual(normal_result.returncode, 0)
        self.assertIn("Objective state is invalid", normal_result.stderr)
        self.assertNotIn("Traceback", normal_result.stderr)
        self.assertEqual(state_path.read_bytes(), malformed_bytes)

        resync_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--resync-objective", "project-state-mvp"
        )
        self.assertEqual(
            resync_result.returncode,
            0,
            msg=resync_result.stdout + resync_result.stderr,
        )
        repaired = json.loads(state_path.read_text(encoding="utf-8"))
        repaired_subtasks = repaired["tasks"]["PS1"]["subtasks"]
        self.assertEqual(repaired_subtasks["PS1.1"]["status"], "completed")
        self.assertEqual(
            repaired_subtasks["PS1.1"]["description"],
            "Review requirements and design context for PS1",
        )
        self.assertEqual(repaired_subtasks["PS1.1"]["duration_seconds"], 0)
        self.assertEqual(
            repaired_subtasks["PS1.1"]["started_at"], "2026-06-01T09:00:00"
        )
        self.assertNotIn("poison", repaired_subtasks["PS1.1"])
        self.assertEqual(repaired_subtasks["PS1.2"]["status"], "pending")
        self.assertEqual(repaired_subtasks["PS1.3"]["status"], "failed")
        self.assertEqual(repaired_subtasks["PS1.3"]["duration_seconds"], 30)

    def test_malformed_scoped_start_and_resume_are_controlled_and_read_only(
        self,
    ) -> None:
        """Unsafe scoped paths must fail before normal start/resume side effects."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        state_path = objective_dir / "execution-state.json"
        for args in (
            ("../project-state-mvp/PS1",),
            ("../project-state-mvp/PS1", "--continue"),
        ):
            with self.subTest(args=args):
                before_runtime = runtime_path.read_bytes()
                before_state = state_path.read_bytes()
                result = self.run_command(str(COMPLETE_TASK_HANDLER), *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("safe single path component", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), before_runtime)
                self.assertEqual(state_path.read_bytes(), before_state)

    def test_completion_requires_verified_acceptance_projection(self) -> None:
        """Durable completion must not emit TASK COMPLETE without verifiable acceptance."""
        objective_dir = self._materialize_project_state_objective()
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        task["status"] = "completed"
        for subtask in task["subtasks"].values():
            subtask["status"] = "completed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_text = tasks_path.read_text(encoding="utf-8")
        ps1_start = tasks_text.index("## PS1:")
        ps1_end = tasks_text.index("## PS2:")
        ps1_section = tasks_text[ps1_start:ps1_end].replace("- [ ]", "- criterion:")
        tasks_path.write_text(
            tasks_text[:ps1_start] + ps1_section + tasks_text[ps1_end:],
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_resume_completion_rolls_back_on_acceptance_failure(self) -> None:
        """Resume completion restores runtime, ledger, and projections on failure."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        for subtask in runtime["subtasks"].values():
            subtask["status"] = "completed"
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_path.write_text(
            tasks_path.read_text(encoding="utf-8").replace("- [ ]", "- [z]", 1),
            encoding="utf-8",
        )
        tracked = (
            runtime_path,
            objective_dir / "execution-state.json",
            tasks_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        for path, original in before.items():
            self.assertEqual(path.read_bytes(), original)

    def test_resume_without_durable_ledger_fails_read_only_with_resync_instruction(
        self,
    ) -> None:
        """Runtime alone cannot authorize resume when the durable ledger is missing."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        state_path = objective_dir / "execution-state.json"
        state_path.unlink()
        runtime_before = runtime_path.read_bytes()

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--resync-objective project-state-mvp", result.stderr)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(runtime_path.read_bytes(), runtime_before)
        self.assertFalse(state_path.exists())

    def test_runtime_rejects_invalid_and_mixed_timezone_timestamps_before_writes(
        self,
    ) -> None:
        """Runtime timestamps must be valid ISO values with compatible awareness."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        valid = json.loads(runtime_path.read_text(encoding="utf-8"))
        for label, mutate in (
            (
                "invalid",
                lambda state: state["subtasks"]["PS1.1"].update(
                    {"started_at": "not-a-datetime"}
                ),
            ),
            (
                "mixed",
                lambda state: state["subtasks"]["PS1.1"].update(
                    {"started_at": "2026-01-01T00:00:00+00:00"}
                ),
            ),
        ):
            with self.subTest(label=label):
                state = json.loads(json.dumps(valid))
                mutate(state)
                runtime_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                before_runtime = runtime_path.read_bytes()
                before_state = (objective_dir / "execution-state.json").read_bytes()

                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.1"
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Runtime state is invalid", result.stderr)
                self.assertNotIn("Traceback", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), before_runtime)
                self.assertEqual(
                    (objective_dir / "execution-state.json").read_bytes(), before_state
                )

    def test_aware_runtime_preserves_awareness_across_resume_and_checkpoints(
        self,
    ) -> None:
        """Generated resume/checkpoint timestamps match aware runtime semantics."""
        self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        runtime["started_at"] = "2099-01-01T00:00:00+00:00"
        runtime_path.write_text(json.dumps(runtime, indent=2), encoding="utf-8")

        resumed = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")
        self.assertEqual(resumed.returncode, 0, msg=resumed.stdout + resumed.stderr)
        progressed = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
        )
        self.assertEqual(
            progressed.returncode, 0, msg=progressed.stdout + progressed.stderr
        )
        completed = self.run_command(str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.1")
        self.assertEqual(
            completed.returncode, 0, msg=completed.stdout + completed.stderr
        )
        persisted = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertTrue(persisted["resumed_at"].endswith("+00:00"))
        self.assertTrue(persisted["subtasks"]["PS1.1"]["updated_at"].endswith("+00:00"))

    def test_continue_without_runtime_fails_read_only(self) -> None:
        """Explicit continue never silently routes to fresh start."""
        objective_dir = self._materialize_project_state_objective()
        tracked = (
            objective_dir / "tasks.md",
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1", "--continue"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("start without --continue", result.stderr)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertFalse(
            (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").exists()
        )
        self.assertFalse((objective_dir / "execution-state.json").exists())
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_duplicate_acceptance_blocks_fail_before_mutation(self) -> None:
        """Acceptance projection requires exactly one block per root task."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        tasks_path = objective_dir / "tasks.md"
        tasks_text = tasks_path.read_text(encoding="utf-8")
        ps1 = tasks_text.split("## PS1:", 1)[1].split("## PS2:", 1)[0]
        duplicate = "\n### Acceptance Criteria\n- [ ] Duplicate criterion\n"
        tasks_path.write_text(
            tasks_text.replace(ps1, ps1 + duplicate, 1), encoding="utf-8"
        )
        tracked = (
            self.temp_dir / ".mm-flow" / "planning" / "task-progress.json",
            objective_dir / "execution-state.json",
            tasks_path,
            objective_dir / "todo.md",
            objective_dir / "HANDOFF-CURRENT.md",
        )
        before = {path: path.read_bytes() for path in tracked}

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_runtime_rejects_boolean_and_negative_retries(self) -> None:
        """Retries are nonnegative integers, never booleans."""
        self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        valid = json.loads(runtime_path.read_text(encoding="utf-8"))
        for retries in (True, -1):
            with self.subTest(retries=retries):
                state = json.loads(json.dumps(valid))
                state["subtasks"]["PS1.1"]["retries"] = retries
                runtime_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
                before = runtime_path.read_bytes()
                result = self.run_command(
                    str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.1"
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("Runtime state is invalid", result.stderr)
                self.assertEqual(runtime_path.read_bytes(), before)

    def test_mutation_lock_contention_fails_without_state_changes(self) -> None:
        """A second mutator fails controlled while the planning lock is held."""
        objective_dir = self._materialize_project_state_objective()
        lock_path = self.temp_dir / ".mm-flow" / "planning" / ".complete-task.lock"
        lock_path.touch()
        tracked = (objective_dir / "tasks.md", objective_dir / "todo.md")
        before = {path: path.read_bytes() for path in tracked}
        with lock_path.open("a+", encoding="utf-8") as lock_file:
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("another complete-task mutation is active", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        self.assertFalse(
            (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").exists()
        )
        for path, content in before.items():
            self.assertEqual(path.read_bytes(), content)

    def test_completion_rejects_mixed_malformed_acceptance_checkbox(self) -> None:
        """Unknown acceptance checkbox tokens must fail before any partial rewrite."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        task["status"] = "completed"
        for subtask in task["subtasks"].values():
            subtask["status"] = "completed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_text = tasks_path.read_text(encoding="utf-8")
        ps1_start = tasks_text.index("## PS1:")
        ps1_end = tasks_text.index("## PS2:")
        ps1_section = tasks_text[ps1_start:ps1_end]
        ps1_section = ps1_section.replace("- [ ]", "- [x]", 1)
        ps1_section = ps1_section.replace("- [ ]", "- [z]", 1)
        tasks_path.write_text(
            tasks_text[:ps1_start] + ps1_section + tasks_text[ps1_end:],
            encoding="utf-8",
        )
        malformed_bytes = tasks_path.read_bytes()

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)
        self.assertEqual(tasks_path.read_bytes(), malformed_bytes)

    def test_completion_rejects_acceptance_write_readback_mismatch(self) -> None:
        """Completion fails when a recognized criterion is not persisted as requested."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        task = state["tasks"]["PS1"]
        task["status"] = "completed"
        for subtask in task["subtasks"].values():
            subtask["status"] = "completed"
        state_path.write_text(json.dumps(state, indent=2), encoding="utf-8")
        tasks_path = objective_dir / "tasks.md"
        tasks_text = tasks_path.read_text(encoding="utf-8")
        ps1_start = tasks_text.index("## PS1:")
        ps1_end = tasks_text.index("## PS2:")
        ps1_section = tasks_text[ps1_start:ps1_end].replace("- [ ]", "- [x]")
        ps1_section = ps1_section.replace("- [x]", "  - [ ]", 1)
        tasks_path.write_text(
            tasks_text[:ps1_start] + ps1_section + tasks_text[ps1_end:],
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "project-state-mvp/PS1")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("acceptance projection failed", result.stderr)
        self.assertNotIn("TASK COMPLETE", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_completed_task_syncs_acceptance_criteria_checkboxes(self) -> None:
        """A completed root task must project its acceptance criteria to [x] in tasks.md."""
        objective_dir = self._materialize_project_state_objective()
        commands_dir = self.temp_dir / ".claude" / "commands" / "mm"
        skills_dir = self.temp_dir / ".claude" / "skills" / "mm" / "safe-commit"
        commands_dir.mkdir(parents=True, exist_ok=True)
        skills_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / "complete-task-handler.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        (commands_dir / "update-todo-times.py").write_text("# stub\n", encoding="utf-8")
        (commands_dir / "safe-commit-handler.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        (skills_dir / "SKILL.md").write_text("# Safe Commit\n", encoding="utf-8")

        bootstrap_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            bootstrap_result.returncode,
            0,
            msg=bootstrap_result.stdout + bootstrap_result.stderr,
        )

        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))

        objective_state["tasks"]["PS1"]["status"] = "completed"
        for subtask_id in objective_state["tasks"]["PS1"]["subtasks"]:
            objective_state["tasks"]["PS1"]["subtasks"][subtask_id]["status"] = (
                "completed"
            )
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("TASK COMPLETE", result.stdout)

        tasks_text = (objective_dir / "tasks.md").read_text(encoding="utf-8")
        ps1_section = tasks_text.split("## PS1:", 1)[1].split("## PS2:", 1)[0]
        self.assertIn("- [x]", ps1_section)
        self.assertNotIn("- [ ]", ps1_section)

    def test_resume_reconciles_in_progress_subtask_from_ledger(self) -> None:
        """--continue must reconcile runtime in_progress subtasks that the ledger marks completed.

        Regression: when an agent exits before calling --mark-done, the runtime keeps a subtask
        as in_progress while the ledger already has it as completed (e.g. marked done in a previous
        session). On resume, the runtime must trust the ledger and promote the subtask to completed
        so it's not treated as stale or invisible by the task-executor.
        """
        objective_dir = self._materialize_project_state_objective()

        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )

        # Runtime: PS1.1 stuck in_progress (agent was interrupted), PS1.2 and PS1.3 pending
        runtime_state = {
            "task_id": "PS1",
            "source_mode": "objective",
            "objective_slug": "project-state-mvp",
            "session_id": "stale-session-001",
            "started_at": "2026-05-31T09:00:00",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {
                    "description": "Review requirements and design context for PS1",
                    "status": "in_progress",
                    "retries": 0,
                    "started_at": "2026-05-31T09:01:00",
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "PS1.2": {
                    "description": "Implement PS1 end-to-end",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "PS1.3": {
                    "description": "Run validation for PS1",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
            },
            "last_checkpoint": "PS1.1",
            "context_budget_exit": None,
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        # Ledger: PS1.1 is already completed (marked done in a previous session)
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        objective_state["tasks"]["PS1"]["status"] = "in_progress"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"] = "completed"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.1"]["completed_at"] = (
            "2026-05-31T09:20:00"
        )
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.2"]["status"] = "pending"
        objective_state["tasks"]["PS1"]["subtasks"]["PS1.3"]["status"] = "pending"
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        # Verify: runtime was reconciled — PS1.1 must now be completed
        updated_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        self.assertEqual(
            updated_runtime["subtasks"]["PS1.1"]["status"],
            "completed",
            "PS1.1 must be promoted from in_progress to completed after ledger reconciliation",
        )
        # And PS1.2/PS1.3 remain pending (still need to be executed)
        self.assertEqual(updated_runtime["subtasks"]["PS1.2"]["status"], "pending")
        self.assertEqual(updated_runtime["subtasks"]["PS1.3"]["status"], "pending")
        # Reconciliation message should be visible
        self.assertIn("Reconciled from ledger", result.stdout)

    def test_objective_slug_prefix_stripped_from_task_id(self) -> None:
        """Handler must accept 'slug/TASK_ID' and strip the prefix before processing.

        Regression: agent sometimes passes 'bulk-upload-csv-import/T4' instead of 'T4'
        causing the handler to crash with 'Task not found' on the mangled task ID.
        """
        self._materialize_project_state_objective()

        # Both forms must produce the same --brief output
        result_plain = self.run_command(str(COMPLETE_TASK_HANDLER), "--brief", "PS1")
        result_prefixed = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--brief", "project-state-mvp/PS1"
        )

        self.assertEqual(
            result_plain.returncode, 0, msg=result_plain.stdout + result_plain.stderr
        )
        self.assertEqual(
            result_prefixed.returncode,
            0,
            msg=result_prefixed.stdout + result_prefixed.stderr,
        )
        self.assertIn("MODEL_BRIEF_START", result_prefixed.stdout)
        self.assertIn("PS1", result_prefixed.stdout)

    def test_brief_blocks_ambiguous_task_ids_across_multiple_active_objectives(
        self,
    ) -> None:
        """Bare `T1` must fail clearly when more than one active objective defines it."""
        self._materialize_generic_objective("alpha-objective", "Alpha Objective")
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-alpha-beta-discover",
                            "objective_slugs": [
                                "alpha-objective",
                                "beta-objective",
                            ],
                            "reason": "Allow coordinated regression coverage for two active objectives.",
                            "commands": ["discover --existing --objective"],
                            "expires_when": "Remove after regression test completes.",
                        }
                    ],
                }
            )
        )
        self._materialize_generic_objective("beta-objective", "Beta Objective")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--brief", "T1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ambiguous across active objectives", result.stderr)
        self.assertIn("Use <objective>/T1", result.stderr)

    def test_brief_accepts_explicit_objective_scoped_task_ref(self) -> None:
        """Objective-scoped task refs should work when multiple active objectives exist."""
        self._materialize_generic_objective("alpha-objective", "Alpha Objective")
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-alpha-beta-discover",
                            "objective_slugs": [
                                "alpha-objective",
                                "beta-objective",
                            ],
                            "reason": "Allow coordinated regression coverage for two active objectives.",
                            "commands": ["discover --existing --objective"],
                            "expires_when": "Remove after regression test completes.",
                        }
                    ],
                }
            )
        )
        self._materialize_generic_objective("beta-objective", "Beta Objective")

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--brief", "alpha-objective/T1"
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("MODEL_BRIEF_START", result.stdout)
        self.assertIn("Objective: alpha-objective", result.stdout)

    def test_start_task_blocks_immediately_when_safe_commit_adapter_is_missing(
        self,
    ) -> None:
        """Execution must abort before launch if critical Claude adapter files are missing."""
        self._materialize_project_state_objective()
        commands_dir = self.temp_dir / ".claude" / "commands" / "mm"
        skills_dir = self.temp_dir / ".claude" / "skills" / "mm" / "safe-commit"
        commands_dir.mkdir(parents=True, exist_ok=True)
        skills_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / "complete-task-handler.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        (commands_dir / "update-todo-times.py").write_text("# stub\n", encoding="utf-8")
        (skills_dir / "SKILL.md").write_text("# Safe Commit\n", encoding="utf-8")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("FLOW BLOCKED: missing safe-commit handler", result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)

    def test_completion_notification_prefers_mm_flow_notifier_over_claude_adapter(
        self,
    ) -> None:
        """Completion notification should resolve through `.mm-flow` before `.claude`."""
        self._materialize_project_state_objective()
        commands_dir = self.temp_dir / ".claude" / "commands" / "mm"
        skills_dir = self.temp_dir / ".claude" / "skills" / "mm" / "safe-commit"
        commands_dir.mkdir(parents=True, exist_ok=True)
        skills_dir.mkdir(parents=True, exist_ok=True)
        (commands_dir / "complete-task-handler.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        (commands_dir / "update-todo-times.py").write_text("# stub\n", encoding="utf-8")
        (commands_dir / "safe-commit-handler.py").write_text(
            "# stub\n", encoding="utf-8"
        )
        (skills_dir / "SKILL.md").write_text("# Safe Commit\n", encoding="utf-8")

        core_marker = self.temp_dir / "core-notify.txt"
        adapter_marker = self.temp_dir / "adapter-notify.txt"
        mm_flow_notify = (
            self.temp_dir / ".mm-flow" / "commands" / "mm" / "notify-complete.py"
        )
        claude_notify = commands_dir / "notify-complete.py"
        mm_flow_notify.parent.mkdir(parents=True, exist_ok=True)
        claude_notify.parent.mkdir(parents=True, exist_ok=True)
        mm_flow_notify.write_text(
            "from pathlib import Path\nPath('core-notify.txt').write_text('core', encoding='utf-8')\n",
            encoding="utf-8",
        )
        claude_notify.write_text(
            "from pathlib import Path\nPath('adapter-notify.txt').write_text('adapter', encoding='utf-8')\n",
            encoding="utf-8",
        )

        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )

        self.assertEqual(
            self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.1"
            ).returncode,
            0,
        )
        self.assertEqual(
            self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.1"
            ).returncode,
            0,
        )
        self.assertEqual(
            self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.2"
            ).returncode,
            0,
        )
        self.assertEqual(
            self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.2"
            ).returncode,
            0,
        )
        self.assertEqual(
            self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-in-progress", "PS1.3"
            ).returncode,
            0,
        )
        planning_dir = self.temp_dir / ".mm-flow" / "planning"
        planning_dir.chmod(0o500)
        try:
            final_done = self.run_command(
                str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.3"
            )
        finally:
            planning_dir.chmod(0o700)
        self.assertEqual(
            final_done.returncode, 0, msg=final_done.stdout + final_done.stderr
        )
        self.assertNotIn("Traceback", final_done.stderr)
        self.assertIn("metadata was not saved", final_done.stderr)
        runtime = json.loads(
            (planning_dir / "task-progress.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("completion_notified_at", runtime)
        self.assertTrue(
            all(
                child["status"] == "completed" for child in runtime["subtasks"].values()
            )
        )

        self.assertTrue(core_marker.exists(), "core notifier should be used")
        self.assertFalse(
            adapter_marker.exists(), "Claude adapter notifier should not be preferred"
        )

    def test_git_history_is_informational_only_on_resume(self) -> None:
        """Resume reports matching commits but never promotes execution state."""
        objective_dir = self._materialize_project_state_objective()

        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )

        # Simulate: PS1.1 was committed but --mark-done failed (in_progress stuck)
        # PS1.2 was also committed but never started in state (pending)
        runtime_state = {
            "task_id": "PS1",
            "source_mode": "objective",
            "objective_slug": "project-state-mvp",
            "session_id": "git-recovery-test",
            "started_at": "2026-05-01T09:00:00",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {
                    "description": "Review requirements and design context for PS1",
                    "status": "in_progress",
                    "retries": 0,
                    "started_at": "2026-05-01T09:01:00",
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "PS1.2": {
                    "description": "Implement PS1 end-to-end",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "PS1.3": {
                    "description": "Run validation for PS1",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
            },
            "last_checkpoint": "PS1.1",
            "context_budget_exit": None,
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        # Create git commits for PS1.1 and PS1.2 in the temp repo
        dummy_file = self.temp_dir / "dummy.txt"
        dummy_file.write_text("v1\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "dummy.txt"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "feat(project-state-mvp): PS1.1 — review requirements",
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        dummy_file.write_text("v2\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "dummy.txt"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "feat(project-state-mvp): PS1.2 — implement PS1"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        self.assertIn("GIT_INFO: 2/3", result.stdout)
        self.assertNotIn("git-recovered", result.stdout.lower())
        payload_line = next(
            (
                line
                for line in result.stdout.splitlines()
                if line.startswith("PAYLOAD:")
            ),
            None,
        )
        self.assertIsNotNone(payload_line, "Expected PAYLOAD: line in output")
        payload = json.loads(payload_line[len("PAYLOAD:") :].strip())
        pending_ids = [st["id"] for st in payload.get("subtasks", [])]
        self.assertEqual(pending_ids, ["PS1.1", "PS1.2", "PS1.3"])
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )["tasks"]["PS1"]["subtasks"]
        self.assertTrue(
            all(child["status"] != "completed" for child in durable.values())
        )

    def test_git_info_rejects_embedded_subtask_token_false_positive(self) -> None:
        """Informational Git reporting requires an exact scoped subtask token."""
        objective_dir = self._materialize_project_state_objective()
        start = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start.returncode, 0, msg=start.stdout + start.stderr)
        marker = self.temp_dir / "false-positive.txt"
        marker.write_text("not task evidence\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "false-positive.txt"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "feat(project-state-mvp): NOTPS1.1 unrelated token",
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--continue")

        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload_line = next(
            line for line in result.stdout.splitlines() if line.startswith("PAYLOAD:")
        )
        payload = json.loads(payload_line.removeprefix("PAYLOAD:").strip())
        self.assertIn("PS1.1", [subtask["id"] for subtask in payload["subtasks"]])
        durable = json.loads(
            (objective_dir / "execution-state.json").read_text(encoding="utf-8")
        )
        self.assertEqual(
            durable["tasks"]["PS1"]["subtasks"]["PS1.1"]["status"], "pending"
        )

    def test_git_info_ignores_commits_from_other_objective_scopes(self) -> None:
        """Other objective scopes are excluded from informational Git reporting."""
        objective_dir = self._materialize_generic_objective(
            "mm-harness-runtime-entrypoint-and-adapters",
            "MM Harness Runtime Entrypoint And Adapters",
        )
        objective_state_path = objective_dir / "execution-state.json"
        objective_state = {
            "objective_slug": "mm-harness-runtime-entrypoint-and-adapters",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "tasks": {
                "T1": {
                    "status": "completed",
                    "subtasks": {
                        "T1.1": {"status": "completed"},
                        "T1.2": {"status": "completed"},
                        "T1.3": {"status": "completed"},
                    },
                },
                "T2": {"status": "pending", "subtasks": {}},
                "T3": {"status": "pending", "subtasks": {}},
            },
        }
        objective_state_path.write_text(
            json.dumps(objective_state, indent=2), encoding="utf-8"
        )

        start_result = self.run_command(
            str(COMPLETE_TASK_HANDLER), "mm-harness-runtime-entrypoint-and-adapters/T2"
        )
        self.assertEqual(
            start_result.returncode, 0, msg=start_result.stdout + start_result.stderr
        )

        runtime_state = {
            "task_id": "T2",
            "source_mode": "objective",
            "objective_slug": "mm-harness-runtime-entrypoint-and-adapters",
            "session_id": "scope-recovery-test",
            "started_at": "2026-06-01T12:00:00",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "T2.1": {
                    "description": "Create the neutral CLI entrypoint and dispatch contract",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "T2.2": {
                    "description": "Wire the supported subcommands to core handlers",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
                "T2.3": {
                    "description": "Validate help/dispatch behavior and targeted tests",
                    "status": "pending",
                    "retries": 0,
                    "started_at": None,
                    "completed_at": None,
                    "duration_seconds": 0,
                },
            },
            "last_checkpoint": None,
            "context_budget_exit": None,
        }
        runtime_path = self.temp_dir / ".mm-flow" / "planning" / "task-progress.json"
        runtime_path.write_text(json.dumps(runtime_state, indent=2), encoding="utf-8")

        dummy_file = self.temp_dir / "dummy.txt"
        dummy_file.write_text("v1\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "dummy.txt"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "commit", "-m", "feat(other-objective): T2.2 — unrelated work"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        dummy_file.write_text("v2\n", encoding="utf-8")
        subprocess.run(
            ["git", "add", "dummy.txt"],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [
                "git",
                "commit",
                "-m",
                "feat(other-objective): T2.3 — unrelated validation",
            ],
            cwd=self.temp_dir,
            check=True,
            capture_output=True,
        )

        result = self.run_command(
            str(COMPLETE_TASK_HANDLER),
            "mm-harness-runtime-entrypoint-and-adapters/T2",
            "--continue",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertNotIn("Git-recovered completed subtasks", result.stdout)

        payload_line = next(
            (
                line
                for line in result.stdout.splitlines()
                if line.startswith("PAYLOAD:")
            ),
            None,
        )
        self.assertIsNotNone(payload_line, "Expected PAYLOAD: line in output")
        payload = json.loads(payload_line[len("PAYLOAD:") :].strip())
        pending_ids = [st["id"] for st in payload.get("subtasks", [])]
        self.assertEqual(pending_ids, ["T2.1", "T2.2", "T2.3"])


if __name__ == "__main__":
    unittest.main()
