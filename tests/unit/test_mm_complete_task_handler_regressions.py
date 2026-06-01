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

    def _materialize_generic_objective(self, slug: str, title: str) -> Path:
        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            slug,
            title,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        return self.temp_dir / ".mm-flow" / "planning" / "changes" / slug

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
        self._materialize_generic_objective("beta-objective", "Beta Objective")

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--brief", "T1")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("ambiguous across active objectives", result.stderr)
        self.assertIn("Use <objective>/T1", result.stderr)

    def test_brief_accepts_explicit_objective_scoped_task_ref(self) -> None:
        """Objective-scoped task refs should work when multiple active objectives exist."""
        self._materialize_generic_objective("alpha-objective", "Alpha Objective")
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
        final_done = self.run_command(
            str(COMPLETE_TASK_HANDLER), "--mark-done", "PS1.3"
        )
        self.assertEqual(
            final_done.returncode, 0, msg=final_done.stdout + final_done.stderr
        )

        self.assertTrue(core_marker.exists(), "core notifier should be used")
        self.assertFalse(
            adapter_marker.exists(), "Claude adapter notifier should not be preferred"
        )

    def test_git_recovery_marks_committed_subtasks_done_on_resume(self) -> None:
        """resume_task must auto-complete subtasks that have git commits even if --mark-done failed.

        Regression: get_git_commits_for_task had two bugs — broken parsing (always returned
        empty set) and wrong scope (filtered by planning path, not commit subject). Even when
        fixed, git results were 'informative only' and never used to update state. This caused
        re-execution of already-committed subtasks when the handler broke mid-task.
        """
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

        # Git-recovered subtasks must NOT appear in the pending list sent to executor
        self.assertIn(
            "git-recovered",
            result.stdout.lower(),
            msg="Expected git-recovery log message",
        )
        # PS1.3 is the only truly pending subtask — executor should only see that
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
        self.assertNotIn(
            "PS1.1", pending_ids, "PS1.1 was committed — must not be re-executed"
        )
        self.assertNotIn(
            "PS1.2", pending_ids, "PS1.2 was committed — must not be re-executed"
        )
        self.assertIn(
            "PS1.3", pending_ids, "PS1.3 has no commit — must still be pending"
        )

    def test_git_recovery_ignores_commits_from_other_objective_scopes(self) -> None:
        """Generic T2 commits from other objective scopes must not auto-complete current subtasks."""
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
