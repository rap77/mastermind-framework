"""Focused subprocess coverage for the objective refinement handoff."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]


class RefineObjectiveHandlerTest(unittest.TestCase):
    """Validate the agent-led refinement boundary in an isolated repository."""

    def setUp(self) -> None:
        """Create an isolated objective package and command symlink."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-refine-objective-"))
        subprocess.run(
            ["git", "init"], cwd=self.temp_dir, check=True, capture_output=True
        )
        commands_dir = self.temp_dir / ".claude" / "commands"
        commands_dir.parent.mkdir(parents=True)
        os.symlink(REPO_ROOT / ".mm-flow" / "commands", commands_dir)
        self.objective_dir = (
            self.temp_dir / ".planning" / "changes" / "sample-objective"
        )
        self.objective_dir.mkdir(parents=True)
        (self.temp_dir / "docs" / "canonical").mkdir(parents=True)
        (self.temp_dir / "docs" / "canonical" / "sample-objective.md").write_text(
            "# Sample Objective\n", encoding="utf-8"
        )
        for name in ("requirements.md", "design.md", "HANDOFF-CURRENT.md"):
            (self.objective_dir / name).write_text(f"# {name}\n", encoding="utf-8")
        self._write_tasks(scaffold=True)

    def tearDown(self) -> None:
        """Remove the isolated repository after each test."""
        shutil.rmtree(self.temp_dir)

    def _write_tasks(self, *, scaffold: bool = False, generic: bool = False) -> None:
        subtasks = (
            ""
            if scaffold
            else """
### Execution Subtasks
- T1.1: Map the package artifact contract and validation boundary

### Purpose
"""
        )
        if generic:
            subtasks = """
### Execution Subtasks
- T1.1: Review requirements and design context for T1

### Purpose
"""
        acceptance = (
            "### Acceptance Criteria\n- [ ] The task scope is verifiably complete\n"
        )
        (self.objective_dir / "tasks.md").write_text(
            "# Tasks\n\n"
            "## T1: Define artifact contract\n\n"
            "### Depends On\nNone\n\n"
            f"{subtasks}{acceptance}\n"
            "## T2: Validate package synchronization\n\n"
            "### Depends On\nT1\n\n"
            + (
                ""
                if scaffold
                else "### Execution Subtasks\n- T2.1: Assert the synchronized execution ledger matches refined root tasks\n\n### Purpose\n"
            )
            + acceptance
            + "## T3: Document operator handoff\n\n### Depends On\nT2\n\n"
            + (
                ""
                if scaffold
                else "### Execution Subtasks\n- T3.1: Document the validated execution entry point for operators\n\n### Purpose\n"
            )
            + acceptance,
            encoding="utf-8",
        )

    def run_handler(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the slash-command adapter from the temporary project root."""
        return subprocess.run(
            [
                "python3",
                ".claude/commands/mm/refine-objective-handler.py",
                "--objective",
                "sample-objective",
                *args,
            ],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_brief_accepts_scaffold_and_sync_requires_specific_topology(self) -> None:
        """Brief is read-only while sync rejects discovery scaffolds."""
        brief = self.run_handler("--brief")
        self.assertEqual(brief.returncode, 0, msg=brief.stderr)
        self.assertIn("MODEL_BRIEF_START", brief.stdout)
        self.assertIn("docs/canonical/sample-objective.md", brief.stdout)
        self.assertFalse((self.objective_dir / "execution-state.json").exists())

        sync = self.run_handler("--sync")
        self.assertNotEqual(sync.returncode, 0)
        self.assertIn("STATUS: FAILED", sync.stdout)
        self.assertIn("Execution Subtasks", sync.stdout)

    def test_sync_resyncs_specific_topology_and_rejects_generic_child(self) -> None:
        """Only specific explicit children can cross into execution."""
        self._write_tasks()
        sync = self.run_handler("--sync")
        self.assertEqual(sync.returncode, 0, msg=sync.stdout + sync.stderr)
        self.assertEqual(
            sync.stdout,
            "STATUS: PASSED\nOBJECTIVE: sample-objective\n"
            "NEXT_COMMAND: /mm:complete-task T1 --brief\n",
        )
        self.assertTrue((self.objective_dir / "execution-state.json").exists())

        self._write_tasks(generic=True)
        generic = self.run_handler("--sync")
        self.assertNotEqual(generic.returncode, 0)
        self.assertIn("generic placeholder", generic.stdout)


if __name__ == "__main__":
    unittest.main()
