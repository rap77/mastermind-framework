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
ACTIVATE_NEXT_OBJECTIVE_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "activate-next-objective-handler.py"
)
CONTEXT_TO_CANONICAL_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "context-to-canonical-handler.py"
)
OBJECTIVE_CONTEXT_CHECK_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "objective-context-check-handler.py"
)
INIT_HANDLER = REPO_ROOT / ".claude" / "commands" / "mm" / "init-handler.py"
UPDATE_TODO_TIMES = REPO_ROOT / ".claude" / "commands" / "mm" / "update-todo-times.py"
CHECKPOINT_GUARD = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "pre_commit_checkpoint_guard.py"
)
VERIFY_CRITERIA_HANDLER = (
    REPO_ROOT / ".claude" / "commands" / "mm" / "verify-criteria-handler.py"
)
RENDER_ACTIVE_OBJECTIVE_EXCEPTION = (
    REPO_ROOT / ".mm-flow" / "commands" / "mm" / "render-active-objective-exception.py"
)
REPLACE_ACTIVE_OBJECTIVE_EXCEPTION = (
    REPO_ROOT / ".mm-flow" / "commands" / "mm" / "replace-active-objective-exception.py"
)
BIN_MM = REPO_ROOT / "bin" / "mm"


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
        (self.temp_dir / ".mm-flow" / "planning").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / "docs" / "canonical").mkdir(parents=True, exist_ok=True)
        (self.temp_dir / ".mm-flow" / "planning" / "SOURCE-OF-TRUTH.md").write_text(
            "# Source of Truth\n\n## Roadmap\n\n### Phase 21: Project State Realtime\n\n**Goal:** Add realtime updates to the project-state dashboard.\n",
            encoding="utf-8",
        )
        (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "HANDOFF-PROJECT-STATE-2026-05-24.md"
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

    def run_neutral_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the neutral `mm` entrypoint in the temporary workspace."""
        self._link_framework_commands()
        return subprocess.run(
            ["python3", str(BIN_MM), *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def _link_framework_commands(self) -> None:
        """Expose the shared MM command tree inside the temporary repo."""
        commands_link = self.temp_dir / ".mm-flow" / "commands"
        if commands_link.exists() or commands_link.is_symlink():
            return
        commands_link.parent.mkdir(parents=True, exist_ok=True)
        commands_link.symlink_to(
            REPO_ROOT / ".mm-flow" / "commands", target_is_directory=True
        )

    def _write_objective_canonical(
        self,
        slug: str,
        report: dict[str, object],
        *,
        title: str = "Add OAuth Login",
    ) -> Path:
        """Create a canonical objective markdown/json pair in the temp repo."""
        output_dir = self.temp_dir / "docs" / "canonical" / "objective-specs"
        output_dir.mkdir(parents=True, exist_ok=True)
        markdown_path = output_dir / f"{slug}.md"
        markdown_path.write_text(
            (
                f"# Objective Spec: {title}\n\n"
                f"<!-- mm:objective-spec | slug: {slug} | intent: feature | status: draft -->\n\n"
                "## 1. Objective Identity\n"
            ),
            encoding="utf-8",
        )
        report_path = markdown_path.with_suffix(".json")
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return markdown_path

    def _write_gate_artifact(
        self,
        slug: str,
        status: str,
        *,
        next_command: str | None = None,
        issues: list[str] | None = None,
    ) -> Path:
        """Create a persisted gate-status artifact for a canonical objective."""
        markdown_path = (
            self.temp_dir / "docs" / "canonical" / "objective-specs" / f"{slug}.md"
        )
        gate_path = markdown_path.with_suffix(".gate.json")
        payload: dict[str, object] = {
            "schema_version": 1,
            "objective_slug": slug,
            "canonical_markdown": str(markdown_path),
            "intake_report": str(markdown_path.with_suffix(".json")),
            "status": status,
            "next_command": next_command
            or f"/mm:objective-context-check --objective {slug}",
        }
        if issues:
            payload["issues"] = issues
        gate_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return gate_path

    def _write_active_objective_exceptions_artifact(
        self, payload: dict[str, object]
    ) -> Path:
        """Create the active-objective exceptions artifact in the temp repo."""
        artifact_path = (
            self.temp_dir / ".mm-flow" / "planning" / "active-objective-exceptions.json"
        )
        artifact_path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
        return artifact_path

    def _write_active_objective_command_bundles_artifact(
        self, payload: dict[str, object]
    ) -> Path:
        """Create the active-objective command bundles artifact in the temp repo."""
        artifact_path = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "active-objective-command-bundles.json"
        )
        artifact_path.write_text(
            json.dumps(payload, indent=2) + "\n",
            encoding="utf-8",
        )
        return artifact_path

    def _write_temp_json_object(
        self, filename: str, payload: dict[str, object]
    ) -> Path:
        """Write one JSON object file inside the temp workspace."""
        path = self.temp_dir / filename
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        return path

    def _write_default_named_bundle_artifact(self) -> Path:
        """Create the default named bundle artifact used in delegation tests."""
        return self._write_active_objective_command_bundles_artifact(
            {
                "version": 1,
                "bundles": [
                    {
                        "name": "activate-next-objective-default",
                        "parent_command": "activate-next-objective",
                        "delegated_commands": ["discover --existing --objective"],
                        "reason": "activate delegates materialization to discover.",
                    }
                ],
            }
        )

    def _with_default_exception_expiry(
        self,
        payload: dict[str, object],
        *,
        expires_at_utc: str = "2099-12-31T23:59:59Z",
    ) -> dict[str, object]:
        """Fill missing machine expiry fields in test exception payloads."""
        data = json.loads(json.dumps(payload))
        exceptions = data.get("exceptions", [])
        if isinstance(exceptions, list):
            for entry in exceptions:
                if isinstance(entry, dict) and "expires_at_utc" not in entry:
                    entry["expires_at_utc"] = expires_at_utc
        return data

    def test_roadmap_mode_materializes_outputs(self) -> None:
        """Roadmap mode should write roadmap files and the current handoff."""
        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        objectives_path = roadmap_dir / "objectives.md"
        dependency_path = roadmap_dir / "dependency-graph.md"
        self.assertTrue(objectives_path.exists())
        self.assertTrue(dependency_path.exists())
        self.assertIn("project-state", objectives_path.read_text(encoding="utf-8"))
        current_handoff = (
            self.temp_dir / ".mm-flow" / "planning" / "HANDOFF-CURRENT.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Current objective", current_handoff)
        self.assertIn("/mm:discover --existing --objective", current_handoff)
        self.assertIn("WRITTEN:", result.stdout)

    def test_roadmap_merges_project_state_aliases_and_marks_completed_package_done(
        self,
    ) -> None:
        """Roadmap discovery should not split project-state and project-state-mvp into separate active tracks."""
        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
            (
                self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
            ).read_text(encoding="utf-8")
        )
        project_state_entries = [
            item
            for item in objectives
            if item["slug"] in {"project-state", "project-state-mvp"}
        ]
        self.assertEqual(len(project_state_entries), 1)
        self.assertEqual(project_state_entries[0]["slug"], "project-state-mvp")
        self.assertEqual(project_state_entries[0]["status"], "done")
        self.assertIn("rank", project_state_entries[0])
        self.assertEqual(project_state_entries[0]["stable_id"], "project-state-mvp")

    def test_roadmap_marks_archived_objective_done_and_sets_recommended_next(
        self,
    ) -> None:
        """Archived objectives should remain done and roadmap should emit a deterministic recommendation."""
        archived_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "artifact-versioning-and-lineage"
        )
        archived_dir.mkdir(parents=True, exist_ok=True)
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_dir / "tasks.md").write_text(
            "# Tasks — artifact-versioning-and-lineage\n\n## AV1: Foundation\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_dir / "todo.md").write_text(
            "# Todo — artifact-versioning-and-lineage\n\n## Execution Checklist\n\n- [x] AV1: Foundation\n  - [x] AV1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "artifact-versioning-and-lineage",
                    "tasks": {"AV1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")

        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        objectives = json.loads(
            (
                self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
            ).read_text(encoding="utf-8")
        )
        artifact = next(
            item
            for item in objectives
            if item["slug"] == "artifact-versioning-and-lineage"
        )
        self.assertEqual(artifact["status"], "done")
        backend = next(
            item
            for item in objectives
            if item["slug"] == "backend-service-boundary-for-agents"
        )
        self.assertTrue(backend["ready_now"])
        self.assertTrue(backend["recommended_next"])
        self.assertEqual(backend["stable_id"], "backend-service-boundary-for-agents")

        objectives_md = (
            self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.md"
        ).read_text(encoding="utf-8")
        self.assertIn("## Recommended next objective", objectives_md)
        self.assertIn("| Rank | Objective |", objectives_md)
        self.assertIn("`backend-service-boundary-for-agents`", objectives_md)

    def test_activate_next_objective_materializes_recommended_package(self) -> None:
        """activate-next-objective should create the package for the roadmap recommendation."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")

        roadmap_result = self.run_command(
            str(DISCOVER_HANDLER), "--roadmap", "--existing"
        )
        self.assertEqual(roadmap_result.returncode, 0, msg=roadmap_result.stderr)

        # Simulate a stale roadmap snapshot that disagrees with the canonical JSON.
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        (roadmap_dir / "objectives.md").write_text(
            "# Objective Roadmap\n\n## Recommended next objective\n\n"
            "- `token-cost-quality-telemetry`\n"
            "- Why: stale snapshot that should be regenerated\n",
            encoding="utf-8",
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        self.assertIn("backend-service-boundary-for-agents", result.stdout)

        refreshed_objectives_md = (roadmap_dir / "objectives.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("`backend-service-boundary-for-agents`", refreshed_objectives_md)
        self.assertNotIn("`token-cost-quality-telemetry`", refreshed_objectives_md)

        objective_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "changes"
            / "backend-service-boundary-for-agents"
        )
        self.assertTrue((objective_dir / "requirements.md").exists())
        self.assertTrue((objective_dir / "design.md").exists())
        self.assertTrue((objective_dir / "tasks.md").exists())

    def test_activate_next_objective_blocks_when_exception_artifact_omits_command(
        self,
    ) -> None:
        """activate-next-objective should keep the single-active block when not explicitly allowed."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "discover-only-pair",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Test exception that should not apply to activation.",
                            "commands": ["discover --existing --objective"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn(active_slug, result.stdout)
        self.assertNotIn("ACTIVE_OBJECTIVE_EXCEPTION", result.stdout)

    def test_activate_next_objective_blocks_when_bundle_artifact_is_missing(
        self,
    ) -> None:
        """activate-next-objective should fail closed when delegated bundle metadata is missing."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "activate-pair-no-bundle",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Missing bundle artifact should keep activation fail-closed.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("bundle metadata", result.stdout)
        self.assertNotIn("ACTIVE_OBJECTIVE_EXCEPTION", result.stdout)

    def test_activate_next_objective_blocks_when_bundle_artifact_is_invalid(
        self,
    ) -> None:
        """activate-next-objective should fail closed when bundle metadata is invalid."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "activate-pair-invalid-bundle",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Invalid bundle artifact should keep activation fail-closed.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )
        self._write_active_objective_command_bundles_artifact(
            {
                "version": 1,
                "bundles": [
                    {
                        "name": "activate-next-objective-default",
                        "parent_command": "activate-next-objective",
                        "delegated_commands": [],
                        "reason": "Invalid because delegated_commands is empty.",
                    }
                ],
            }
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("bundle metadata", result.stdout)
        self.assertNotIn("ACTIVE_OBJECTIVE_EXCEPTION", result.stdout)

    def test_activate_next_objective_allows_valid_matching_active_exception(
        self,
    ) -> None:
        """activate-next-objective should honor a valid matching multi-active exception."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "activate-pair",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Allow coordinated activation for these two objectives.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Archive either objective after the coordination window closes.",
                        }
                    ],
                }
            )
        )
        self._write_default_named_bundle_artifact()

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        self.assertIn("ACTIVE_OBJECTIVE_EXCEPTION: activate-pair", result.stdout)
        self.assertIn(recommended_slug, result.stdout)
        self.assertIn(active_slug, result.stdout)
        self.assertIn("Allow coordinated activation", result.stdout)
        self.assertIn("Expires when:", result.stdout)

    def test_activate_next_objective_allows_named_bundle_reference_exception(
        self,
    ) -> None:
        """activate-next-objective should resolve named bundle refs deterministically."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "activate-pair-bundle-ref",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Allow activation via named bundle ref.",
                            "command_bundle_refs": ["activate-next-objective-default"],
                            "expires_when": "Archive either objective after the coordination window closes.",
                        }
                    ],
                }
            )
        )
        self._write_default_named_bundle_artifact()

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        self.assertIn(
            "ACTIVE_OBJECTIVE_EXCEPTION: activate-pair-bundle-ref", result.stdout
        )

    def test_activate_next_objective_blocks_on_unknown_named_bundle_reference(
        self,
    ) -> None:
        """Unknown named bundle refs should fail closed."""
        active_slug = "parallel-helper-objective"
        (self.temp_dir / ".mm-flow" / "planning" / "changes" / active_slug).mkdir(
            parents=True, exist_ok=True
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        recommended_slug = "backend-service-boundary-for-agents"
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": recommended_slug,
                        "title": "Backend Service Boundary For Agents",
                        "recommended_next": True,
                    }
                ],
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "activate-pair-unknown-bundle-ref",
                            "objective_slugs": [
                                recommended_slug,
                                active_slug,
                            ],
                            "reason": "Unknown bundle ref should fail closed.",
                            "command_bundle_refs": ["missing-bundle"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )
        self._write_default_named_bundle_artifact()

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn(active_slug, result.stdout)

    def test_render_active_objective_exception_fails_when_artifact_is_missing(
        self,
    ) -> None:
        """Render helper should fail clearly when the exceptions artifact is absent."""
        result = self.run_command(
            str(RENDER_ACTIVE_OBJECTIVE_EXCEPTION), "--id", "missing-entry"
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Missing exception artifact", result.stdout)

    def test_render_active_objective_exception_fails_for_unknown_id(self) -> None:
        """Render helper should fail clearly when the id does not exist."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "known-entry",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Known entry for render tests.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — test window.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(
            str(RENDER_ACTIVE_OBJECTIVE_EXCEPTION), "--id", "unknown-entry"
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Unknown exception id: unknown-entry", result.stdout)

    def test_render_active_objective_exception_renders_existing_entry_by_id(
        self,
    ) -> None:
        """Render helper should print the normalized existing entry without mutation."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "render-me",
                            "objective_slugs": ["beta", "alpha", "alpha"],
                            "reason": "Render the current entry.",
                            "commands": [
                                "activate-next-objective",
                                "activate-next-objective",
                            ],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — render window.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(
            str(RENDER_ACTIVE_OBJECTIVE_EXCEPTION), "--id", "render-me"
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        rendered = json.loads(result.stdout.split("\n", 2)[2])
        self.assertEqual(rendered["id"], "render-me")
        self.assertEqual(rendered["objective_slugs"], ["alpha", "beta"])
        self.assertEqual(rendered["commands"], ["activate-next-objective"])
        self.assertEqual(rendered["expires_at_utc"], "2099-12-31T23:59:59Z")

    def test_render_active_objective_exception_applies_narrow_overrides(
        self,
    ) -> None:
        """Render helper should support narrow override-based updates before paste/replace."""
        self._write_default_named_bundle_artifact()
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "update-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Old reason.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — old window.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(
            str(RENDER_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "update-me",
            "--objective-slug",
            "alpha",
            "--objective-slug",
            "gamma",
            "--reason",
            "Updated reason.",
            "--command-bundle-ref",
            "activate-next-objective-default",
            "--expires-at-utc",
            "2099-11-30T12:00:00Z",
            "--expires-context",
            "updated window",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        rendered = json.loads(result.stdout.split("\n", 2)[2])
        self.assertEqual(rendered["objective_slugs"], ["alpha", "gamma"])
        self.assertEqual(rendered["reason"], "Updated reason.")
        self.assertEqual(
            rendered["command_bundle_refs"], ["activate-next-objective-default"]
        )
        self.assertEqual(rendered["commands"], ["activate-next-objective"])
        self.assertEqual(rendered["expires_at_utc"], "2099-11-30T12:00:00Z")
        self.assertEqual(
            rendered["expires_when"],
            "Expires at 2099-11-30T12:00:00Z — updated window",
        )

    def test_replace_active_objective_exception_fails_when_artifact_is_missing(
        self,
    ) -> None:
        """Replace helper should fail clearly when the exceptions artifact is absent."""
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "missing-entry",
                "objective_slugs": ["alpha", "beta"],
                "reason": "Replacement object.",
                "commands": ["activate-next-objective"],
                "expires_at_utc": "2099-12-31T23:59:59Z",
                "expires_when": "Expires at 2099-12-31T23:59:59Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "missing-entry",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Missing exception artifact", result.stdout)

    def test_replace_active_objective_exception_fails_when_entry_file_is_missing(
        self,
    ) -> None:
        """Replace helper should fail clearly when the replacement file is absent."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        }
                    ],
                }
            )
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "replace-me",
            "--entry-file",
            str(self.temp_dir / "does-not-exist.json"),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Missing entry file", result.stdout)

    def test_replace_active_objective_exception_fails_for_duplicate_id(
        self,
    ) -> None:
        """Replace helper should fail closed when the target id is duplicated."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry A.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window A.",
                        },
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "gamma"],
                            "reason": "Original entry B.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window B.",
                        },
                    ],
                }
            )
        )
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "replace-me",
                "objective_slugs": ["alpha", "delta"],
                "reason": "Replacement object.",
                "commands": ["activate-next-objective"],
                "expires_at_utc": "2099-12-31T23:59:59Z",
                "expires_when": "Expires at 2099-12-31T23:59:59Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "replace-me",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Duplicate exception id: replace-me", result.stdout)

    def test_replace_active_objective_exception_fails_on_id_mismatch(
        self,
    ) -> None:
        """Replace helper should reject replacement objects whose id mismatches --id."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        }
                    ],
                }
            )
        )
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "different-id",
                "objective_slugs": ["alpha", "delta"],
                "reason": "Replacement object.",
                "commands": ["activate-next-objective"],
                "expires_at_utc": "2099-12-31T23:59:59Z",
                "expires_when": "Expires at 2099-12-31T23:59:59Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "replace-me",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Replacement entry `id` must match --id", result.stdout)

    def test_replace_active_objective_exception_replaces_exactly_one_entry_by_id(
        self,
    ) -> None:
        """Replace helper should rewrite exactly one matching entry and preserve the rest."""
        self._write_default_named_bundle_artifact()
        artifact_path = self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        },
                        {
                            "id": "keep-me",
                            "objective_slugs": ["beta", "gamma"],
                            "reason": "Unchanged entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — keep window.",
                        },
                    ],
                }
            )
        )
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "replace-me",
                "objective_slugs": ["alpha", "delta"],
                "reason": "Replacement object.",
                "command_bundle_refs": ["activate-next-objective-default"],
                "expires_at_utc": "2099-11-30T12:00:00Z",
                "expires_when": "Expires at 2099-11-30T12:00:00Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--id",
            "replace-me",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        self.assertIn("validate-active-objective-exceptions.py", result.stdout)

        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        self.assertEqual(artifact["version"], 1)
        self.assertEqual(len(artifact["exceptions"]), 2)
        updated = next(
            entry for entry in artifact["exceptions"] if entry["id"] == "replace-me"
        )
        untouched = next(
            entry for entry in artifact["exceptions"] if entry["id"] == "keep-me"
        )
        self.assertEqual(updated["objective_slugs"], ["alpha", "delta"])
        self.assertEqual(updated["reason"], "Replacement object.")
        self.assertEqual(
            updated["command_bundle_refs"], ["activate-next-objective-default"]
        )
        self.assertEqual(updated["commands"], [])
        self.assertEqual(updated["expires_at_utc"], "2099-11-30T12:00:00Z")
        self.assertEqual(untouched["reason"], "Unchanged entry.")

    def test_replace_active_objective_exception_dry_run_fails_for_unknown_id(
        self,
    ) -> None:
        """Dry-run should reuse the same fail-closed id checks as the write path."""
        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "known-entry",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        }
                    ],
                }
            )
        )
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "unknown-entry",
                "objective_slugs": ["alpha", "delta"],
                "reason": "Replacement object.",
                "commands": ["activate-next-objective"],
                "expires_at_utc": "2099-12-31T23:59:59Z",
                "expires_when": "Expires at 2099-12-31T23:59:59Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--dry-run",
            "--id",
            "unknown-entry",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("Unknown exception id: unknown-entry", result.stdout)

    def test_replace_active_objective_exception_dry_run_fails_for_invalid_replacement(
        self,
    ) -> None:
        """Dry-run should reject invalid replacement objects without mutating the artifact."""
        artifact_path = self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        }
                    ],
                }
            )
        )
        before = artifact_path.read_text(encoding="utf-8")
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "replace-me",
                "objective_slugs": ["alpha"],
                "reason": "Invalid replacement object.",
                "commands": ["activate-next-objective"],
                "expires_at_utc": "2099-12-31T23:59:59Z",
                "expires_when": "Expires at 2099-12-31T23:59:59Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--dry-run",
            "--id",
            "replace-me",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn(
            "Replacement entry is invalid after normalization.", result.stdout
        )
        self.assertEqual(artifact_path.read_text(encoding="utf-8"), before)

    def test_replace_active_objective_exception_dry_run_previews_without_mutating(
        self,
    ) -> None:
        """Dry-run should show current/replacement preview and leave the artifact untouched."""
        self._write_default_named_bundle_artifact()
        artifact_path = self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "replace-me",
                            "objective_slugs": ["alpha", "beta"],
                            "reason": "Original entry.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Expires at 2099-12-31T23:59:59Z — original window.",
                        }
                    ],
                }
            )
        )
        before = artifact_path.read_text(encoding="utf-8")
        replacement_path = self._write_temp_json_object(
            "replacement.json",
            {
                "id": "replace-me",
                "objective_slugs": ["alpha", "delta"],
                "reason": "Replacement object.",
                "command_bundle_refs": ["activate-next-objective-default"],
                "expires_at_utc": "2099-11-30T12:00:00Z",
                "expires_when": "Expires at 2099-11-30T12:00:00Z — replacement window.",
            },
        )

        result = self.run_command(
            str(REPLACE_ACTIVE_OBJECTIVE_EXCEPTION),
            "--dry-run",
            "--id",
            "replace-me",
            "--entry-file",
            str(replacement_path),
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        self.assertIn("DRY_RUN: true", result.stdout)
        self.assertIn("CHANGED_FIELDS:", result.stdout)
        self.assertIn('"reason": "Original entry."', result.stdout)
        self.assertIn('"reason": "Replacement object."', result.stdout)
        self.assertEqual(artifact_path.read_text(encoding="utf-8"), before)

    def test_roadmap_surfaces_gate_status_for_recommended_objective(self) -> None:
        """Roadmap outputs should expose gate status when the recommended objective has a canonical objective."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        objectives = json.loads(
            (
                self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
            ).read_text(encoding="utf-8")
        )
        backend = next(
            item
            for item in objectives
            if item["slug"] == "backend-service-boundary-for-agents"
        )
        self.assertEqual(backend["gate_status"], "NOT_RUN")
        self.assertIn("gate_guidance", backend)
        objectives_md = (
            self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.md"
        ).read_text(encoding="utf-8")
        self.assertIn("not_run", objectives_md)

    def test_roadmap_reranks_to_gate_ready_objective_when_higher_priority_one_is_blocked(
        self,
    ) -> None:
        """Roadmap should recommend a gate-ready objective over a higher-priority candidate blocked by gate status."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )
        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        objectives = json.loads(
            (
                self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
            ).read_text(encoding="utf-8")
        )
        recommended = next(item for item in objectives if item["recommended_next"])
        self.assertEqual(recommended["slug"], "dashboard-realtime")

    def test_activate_next_objective_uses_gate_ready_reranked_recommendation(
        self,
    ) -> None:
        """Activation should follow the reranked gate-ready recommendation."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )
        roadmap_result = self.run_command(
            str(DISCOVER_HANDLER), "--roadmap", "--existing"
        )
        self.assertEqual(
            roadmap_result.returncode,
            0,
            msg=roadmap_result.stdout + roadmap_result.stderr,
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("dashboard-realtime", result.stdout)

    def test_roadmap_marks_blocked_fallback_when_all_ready_candidates_are_gate_blocked(
        self,
    ) -> None:
        """Roadmap should still recommend one candidate when all ready candidates are gate-blocked, but mark it as a blocked fallback."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir / "docs" / "canonical" / "33-DASHBOARD-REALTIME-EVENTS.md"
        ).write_text("# Dashboard Realtime Events\n", encoding="utf-8")
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        self._write_objective_canonical(
            "dashboard-realtime",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "dashboard-realtime",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        result = self.run_command(str(DISCOVER_HANDLER), "--roadmap", "--existing")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

        objectives = json.loads(
            (
                self.temp_dir / ".mm-flow" / "planning" / "roadmap" / "objectives.json"
            ).read_text(encoding="utf-8")
        )
        recommended = next(item for item in objectives if item["recommended_next"])
        self.assertEqual(recommended["slug"], "backend-service-boundary-for-agents")
        self.assertTrue(recommended["recommended_blocked_fallback"])
        self.assertIn("unblock_priority_reason", recommended)
        self.assertIn("highest priority", recommended["unblock_priority_reason"])
        self.assertIn("gate status", recommended["unblock_priority_reason"])

        handoff = (
            self.temp_dir / ".mm-flow" / "planning" / "HANDOFF-CURRENT.md"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "All dependency-ready objectives are currently gate-blocked", handoff
        )
        self.assertIn("Unblock priority reason", handoff)

    def test_activate_next_objective_remains_blocked_on_blocked_fallback_recommendation(
        self,
    ) -> None:
        """Activation should still block when roadmap falls back to a gate-blocked recommendation."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir / "docs" / "canonical" / "33-DASHBOARD-REALTIME-EVENTS.md"
        ).write_text("# Dashboard Realtime Events\n", encoding="utf-8")
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        self._write_objective_canonical(
            "dashboard-realtime",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "dashboard-realtime",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        roadmap_result = self.run_command(
            str(DISCOVER_HANDLER), "--roadmap", "--existing"
        )
        self.assertEqual(
            roadmap_result.returncode,
            0,
            msg=roadmap_result.stdout + roadmap_result.stderr,
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertIn("backend-service-boundary-for-agents", result.stdout)

    def test_activate_next_objective_blocks_when_recommended_gate_not_run(self) -> None:
        """activate-next-objective should stop early when the recommended objective has not passed the gate yet."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        (
            self.temp_dir / "docs" / "canonical" / "33-DASHBOARD-REALTIME-EVENTS.md"
        ).unlink()
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        roadmap_result = self.run_command(
            str(DISCOVER_HANDLER), "--roadmap", "--existing"
        )
        self.assertEqual(
            roadmap_result.returncode,
            0,
            msg=roadmap_result.stdout + roadmap_result.stderr,
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertIn("GATE_STATUS: NOT_RUN", result.stdout)
        self.assertIn(
            "/mm:objective-context-check --objective backend-service-boundary-for-agents",
            result.stdout,
        )

    def test_activate_next_objective_blocks_when_recommended_gate_needs_input(
        self,
    ) -> None:
        """activate-next-objective should stop with actionable guidance when the recommended objective still needs input."""
        archived_project_state_dir = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        archived_project_state_dir.mkdir(parents=True, exist_ok=True)
        (archived_project_state_dir / "tasks.md").write_text(
            "# Tasks — project-state-mvp\n\n## PS1: Realtime\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "todo.md").write_text(
            "# Todo — project-state-mvp\n\n## Execution Checklist\n\n- [x] PS1: Realtime\n  - [x] PS1.1: Done\n",
            encoding="utf-8",
        )
        (archived_project_state_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {"PS1": {"status": "completed", "subtasks": {}}},
                }
            ),
            encoding="utf-8",
        )
        (
            self.temp_dir
            / "docs"
            / "canonical"
            / "34-BACKEND-SERVICE-BOUNDARY-FOR-AGENTS.md"
        ).write_text("# Backend Service Boundary For Agents\n", encoding="utf-8")
        (
            self.temp_dir / "docs" / "canonical" / "33-DASHBOARD-REALTIME-EVENTS.md"
        ).unlink()
        self._write_objective_canonical(
            "backend-service-boundary-for-agents",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "backend-service-boundary-for-agents",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": ["README-only evidence"],
                "questions_asked": [
                    {
                        "id": "desired_behavior",
                        "question": "?",
                        "reason": "Sparse context",
                    }
                ],
                "questions_unanswered": ["desired_behavior"],
                "confidence": "medium",
                "generated_files": [],
            },
        )
        self._write_gate_artifact(
            "backend-service-boundary-for-agents",
            "NEEDS_INPUT",
            issues=["Outstanding questions: desired_behavior"],
        )

        roadmap_result = self.run_command(
            str(DISCOVER_HANDLER), "--roadmap", "--existing"
        )
        self.assertEqual(
            roadmap_result.returncode,
            0,
            msg=roadmap_result.stdout + roadmap_result.stderr,
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertIn("GATE_STATUS: NEEDS_INPUT", result.stdout)
        self.assertIn("Answer the open questions", result.stdout)

    def test_discover_objective_blocks_when_another_active_objective_exists(
        self,
    ) -> None:
        """Discover should not materialize a second active objective package by default."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 2, msg=second.stdout + second.stderr)
        self.assertIn("STATUS: BLOCKED", second.stdout)
        self.assertIn("project-state-mvp", second.stdout)
        self.assertIn("complete/archive/resume", second.stdout)

    def test_discover_objective_allows_refreshing_the_same_active_objective(
        self,
    ) -> None:
        """Discover may refresh the existing active objective package when targeting the same slug."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        original_tasks = (objective_dir / "tasks.md").read_text(encoding="utf-8")

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(second.returncode, 0, msg=second.stdout + second.stderr)
        self.assertIn("MODE: objective", second.stdout)
        self.assertEqual(
            original_tasks, (objective_dir / "tasks.md").read_text(encoding="utf-8")
        )

    def test_discover_objective_blocks_when_exception_artifact_omits_command(
        self,
    ) -> None:
        """Discover should keep blocking when the exception does not list the discover command."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)

        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-activate-only",
                            "objective_slugs": [
                                "artifact-versioning-and-lineage",
                                "project-state-mvp",
                            ],
                            "reason": "Test exception that should not apply to discover.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 2, msg=second.stdout + second.stderr)
        self.assertIn("STATUS: BLOCKED", second.stdout)
        self.assertIn("project-state-mvp", second.stdout)
        self.assertNotIn("ACTIVE_OBJECTIVE_EXCEPTION", second.stdout)

    def test_discover_objective_blocks_on_unsupported_delegated_scope(self) -> None:
        """Discover should fail closed when the delegation marker is unsupported."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)

        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-activate-only",
                            "objective_slugs": [
                                "artifact-versioning-and-lineage",
                                "project-state-mvp",
                            ],
                            "reason": "Only the documented activate delegation may inherit this scope.",
                            "commands": ["activate-next-objective"],
                            "expires_when": "Remove after test.",
                        }
                    ],
                }
            )
        )

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--delegated-from",
            "unknown-parent-command",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 2, msg=second.stdout + second.stderr)
        self.assertIn("STATUS: BLOCKED", second.stdout)
        self.assertNotIn("ACTIVE_OBJECTIVE_EXCEPTION", second.stdout)

    def test_discover_objective_allows_valid_matching_active_exception(self) -> None:
        """Discover should honor a valid matching multi-active exception."""
        first = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(first.returncode, 0, msg=first.stdout + first.stderr)

        self._write_active_objective_exceptions_artifact(
            self._with_default_exception_expiry(
                {
                    "version": 1,
                    "exceptions": [
                        {
                            "id": "allow-discover-pair",
                            "objective_slugs": [
                                "artifact-versioning-and-lineage",
                                "project-state-mvp",
                            ],
                            "reason": "These two objective packages may coexist for coordinated harness work.",
                            "commands": ["discover --existing --objective"],
                            "expires_when": "Archive either objective after the coordination window closes.",
                        }
                    ],
                }
            )
        )

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 0, msg=second.stdout + second.stderr)
        self.assertIn("ACTIVE_OBJECTIVE_EXCEPTION: allow-discover-pair", second.stdout)
        self.assertIn(
            "ALLOWED_OBJECTIVES: artifact-versioning-and-lineage, project-state-mvp",
            second.stdout,
        )
        self.assertIn("These two objective packages may coexist", second.stdout)
        self.assertIn("Expires when:", second.stdout)
        self.assertTrue(
            (
                self.temp_dir
                / ".mm-flow"
                / "planning"
                / "changes"
                / "artifact-versioning-and-lineage"
            ).exists()
        )

    def test_discover_objective_ignores_stale_bootstrapped_done_active_objective(
        self,
    ) -> None:
        """Discover should ignore a bootstrapped ghost objective when roadmap already marks it done."""
        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        objective_dir.mkdir(parents=True, exist_ok=True)
        for name in (
            "requirements.md",
            "design.md",
            "tasks.md",
            "todo.md",
            "HANDOFF-CURRENT.md",
        ):
            (objective_dir / name).write_text(f"# {name}\n", encoding="utf-8")
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "bootstrapped_from_artifacts": True,
                    "tasks": {
                        "PS1": {"status": "pending"},
                        "PS2": {"status": "pending"},
                    },
                }
            ),
            encoding="utf-8",
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": "project-state-mvp",
                        "status": "done",
                        "ready_now": False,
                        "recommended_next": False,
                    }
                ]
            ),
            encoding="utf-8",
        )

        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_activate_next_objective_ignores_stale_bootstrapped_done_active_objective(
        self,
    ) -> None:
        """Activation should ignore a bootstrapped ghost objective when roadmap already marks it done."""
        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        objective_dir.mkdir(parents=True, exist_ok=True)
        for name in (
            "requirements.md",
            "design.md",
            "tasks.md",
            "todo.md",
            "HANDOFF-CURRENT.md",
        ):
            (objective_dir / name).write_text(f"# {name}\n", encoding="utf-8")
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "bootstrapped_from_artifacts": True,
                    "tasks": {
                        "PS1": {"status": "pending"},
                        "PS2": {"status": "pending"},
                    },
                }
            ),
            encoding="utf-8",
        )
        roadmap_dir = self.temp_dir / ".mm-flow" / "planning" / "roadmap"
        roadmap_dir.mkdir(parents=True, exist_ok=True)
        (roadmap_dir / "objectives.json").write_text(
            json.dumps(
                [
                    {
                        "slug": "project-state-mvp",
                        "status": "done",
                        "ready_now": False,
                        "recommended_next": False,
                    },
                    {
                        "slug": "backend-service-boundary-for-agents",
                        "name": "Backend Service Boundary For Agents",
                        "status": "planned",
                        "ready_now": True,
                        "recommended_next": True,
                    },
                ]
            ),
            encoding="utf-8",
        )

        result = self.run_command(str(ACTIVATE_NEXT_OBJECTIVE_HANDLER))
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("backend-service-boundary-for-agents", result.stdout)

    def test_context_to_canonical_writes_project_adapter_directly(self) -> None:
        """context-to-canonical should write a project-adapter doc without agent help."""
        result = self.run_command(
            str(CONTEXT_TO_CANONICAL_HANDLER),
            "--target",
            str(self.temp_dir),
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)

        output_dir = self.temp_dir / "docs" / "canonical" / "project-adapter"
        output_candidates = list(output_dir.glob("*.md"))
        self.assertEqual(len(output_candidates), 1, msg=result.stdout + result.stderr)
        output_path = output_candidates[0]
        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("# Project Adapter:", content)
        self.assertIn("## 10. Success Criteria", content)
        report_path = output_path.with_suffix(".json")
        self.assertTrue(report_path.exists())
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["schema_version"], 1)
        self.assertEqual(report["doc_type"], "project-adapter")
        self.assertIn("context_sources", report)
        self.assertIn("confidence", report)

    def test_context_to_canonical_writes_objective_spec_directly(self) -> None:
        """context-to-canonical objective mode should write a discoverable canonical spec."""
        result = self.run_command(
            str(CONTEXT_TO_CANONICAL_HANDLER),
            "--type",
            "objective",
            "--target",
            str(self.temp_dir),
            "--name",
            "Add OAuth Login",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)

        output_dir = self.temp_dir / "docs" / "canonical" / "objective-specs"
        output_candidates = list(output_dir.glob("*.md"))
        self.assertEqual(len(output_candidates), 1, msg=result.stdout + result.stderr)
        output_path = output_candidates[0]
        self.assertTrue(output_path.exists())
        content = output_path.read_text(encoding="utf-8")
        self.assertIn("<!-- mm:objective-spec | slug: add-oauth-login", content)
        self.assertIn("## 5. Acceptance Criteria", content)
        report = json.loads(
            output_path.with_suffix(".json").read_text(encoding="utf-8")
        )
        self.assertEqual(report["doc_type"], "objective")
        self.assertEqual(report["intent"], "feature")
        self.assertEqual(report["objective_slug"], "add-oauth-login")
        self.assertIn("evidence", report)
        self.assertIn("gaps_detected", report)
        self.assertIn(
            "NEXT_COMMAND: /mm:objective-context-check --objective add-oauth-login",
            result.stdout,
        )

    def test_context_to_canonical_payload_includes_normalized_intake_contract(
        self,
    ) -> None:
        """Payload mode should expose the normalized intake contract for downstream tools."""
        result = self.run_command(
            str(CONTEXT_TO_CANONICAL_HANDLER),
            "--type",
            "objective",
            "--target",
            str(self.temp_dir),
            "--name",
            "Add OAuth Login",
            "--payload-only",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        payload_line = next(
            line for line in result.stdout.splitlines() if line.startswith("PAYLOAD:")
        )
        payload = json.loads(payload_line[len("PAYLOAD: ") :])
        self.assertEqual(payload["intake"]["schema_version"], 1)
        self.assertEqual(payload["intake"]["doc_type"], "objective")
        self.assertEqual(payload["intake"]["intent"], "feature")
        self.assertEqual(
            payload["report_output_path"],
            str(Path(payload["output_path"]).with_suffix(".json")),
        )

    def test_context_to_canonical_report_emits_structured_interview_questions(
        self,
    ) -> None:
        """Objective report should surface structured interview questions when context is sparse."""
        target = self.temp_dir / "sparse-project"
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text("# Sparse Project\n", encoding="utf-8")

        result = self.run_command(
            str(CONTEXT_TO_CANONICAL_HANDLER),
            "--type",
            "objective",
            "--target",
            str(target),
            "--name",
            "Add OAuth Login",
            "--interview",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("INTERVIEW_REQUIRED: yes", result.stdout)

        report_path = (
            target / "docs" / "canonical" / "objective-specs" / "add-oauth-login.json"
        )
        report = json.loads(report_path.read_text(encoding="utf-8"))
        self.assertTrue(report["questions_asked"])
        self.assertIn("desired_behavior", report["questions_unanswered"])

    def test_objective_context_check_passes_when_canonical_is_ready(self) -> None:
        """The new gate should pass when the canonical markdown/report are ready."""
        self._write_objective_canonical(
            "add-oauth-login",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "add-oauth-login",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md", "CLAUDE.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        result = self.run_command(
            str(OBJECTIVE_CONTEXT_CHECK_HANDLER),
            "--objective",
            "add-oauth-login",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        gate_artifact = (
            self.temp_dir
            / "docs"
            / "canonical"
            / "objective-specs"
            / "add-oauth-login.gate.json"
        )
        self.assertTrue(gate_artifact.exists())
        gate_data = json.loads(gate_artifact.read_text(encoding="utf-8"))
        self.assertEqual(gate_data["status"], "PASSED")
        self.assertEqual(
            gate_data["next_command"],
            "/mm:discover --existing --objective add-oauth-login",
        )

    def test_objective_context_check_fails_when_report_is_missing(self) -> None:
        """The gate should fail deterministically when the sidecar report is missing."""
        output_dir = self.temp_dir / "docs" / "canonical" / "objective-specs"
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "add-oauth-login.md").write_text(
            (
                "# Objective Spec: Add OAuth Login\n\n"
                "<!-- mm:objective-spec | slug: add-oauth-login | intent: feature | status: draft -->\n"
            ),
            encoding="utf-8",
        )

        result = self.run_command(
            str(OBJECTIVE_CONTEXT_CHECK_HANDLER),
            "--objective",
            "add-oauth-login",
        )
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: FAILED", result.stdout)
        self.assertIn("report", result.stdout.lower())

    def test_objective_context_check_needs_input_when_questions_remain(self) -> None:
        """The gate should request input when structured interview questions remain unanswered."""
        self._write_objective_canonical(
            "add-oauth-login",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "add-oauth-login",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": ["README-only evidence"],
                "questions_asked": [
                    {
                        "id": "desired_behavior",
                        "question": "What exact behavior should this objective produce?",
                        "reason": "Sparse context",
                    }
                ],
                "questions_unanswered": ["desired_behavior"],
                "confidence": "medium",
                "generated_files": [],
            },
        )

        result = self.run_command(
            str(OBJECTIVE_CONTEXT_CHECK_HANDLER),
            "--objective",
            "add-oauth-login",
        )
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: NEEDS_INPUT", result.stdout)
        self.assertIn("desired_behavior", result.stdout)

    def test_discover_objective_blocks_when_gate_has_not_run(self) -> None:
        """Discover should stop instead of bypassing the gate when a canonical objective exists but was not checked."""
        self._write_objective_canonical(
            "add-oauth-login",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "add-oauth-login",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )

        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "add-oauth-login",
            "Add OAuth Login",
        )
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertIn("GATE_STATUS: NOT_RUN", result.stdout)
        self.assertIn(
            "/mm:objective-context-check --objective add-oauth-login", result.stdout
        )

    def test_discover_objective_blocks_when_gate_needs_input(self) -> None:
        """Discover should stop with actionable guidance when the gate still needs input."""
        self._write_objective_canonical(
            "add-oauth-login",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "add-oauth-login",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": ["README-only evidence"],
                "questions_asked": [
                    {
                        "id": "desired_behavior",
                        "question": "?",
                        "reason": "Sparse context",
                    }
                ],
                "questions_unanswered": ["desired_behavior"],
                "confidence": "medium",
                "generated_files": [],
            },
        )
        self._write_gate_artifact(
            "add-oauth-login",
            "NEEDS_INPUT",
            issues=["Outstanding questions: desired_behavior"],
        )

        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "add-oauth-login",
            "Add OAuth Login",
        )
        self.assertEqual(result.returncode, 2, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: BLOCKED", result.stdout)
        self.assertIn("GATE_STATUS: NEEDS_INPUT", result.stdout)
        self.assertIn("Answer the open questions", result.stdout)

    def test_discover_objective_allows_materialization_after_gate_passes(self) -> None:
        """Discover should proceed once the canonical objective has a passing gate artifact."""
        self._write_objective_canonical(
            "add-oauth-login",
            {
                "schema_version": 1,
                "doc_type": "objective",
                "intent": "feature",
                "objective_slug": "add-oauth-login",
                "project_name": self.temp_dir.name,
                "context_sources": ["README.md", "CLAUDE.md"],
                "evidence": [{"source": "README.md", "kind": "repo"}],
                "assumptions": [],
                "gaps_detected": [],
                "questions_asked": [],
                "questions_unanswered": [],
                "confidence": "high",
                "generated_files": [],
            },
        )
        self._write_gate_artifact(
            "add-oauth-login",
            "PASSED",
            next_command="/mm:discover --existing --objective add-oauth-login",
        )

        result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "add-oauth-login",
            "Add OAuth Login",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("MODE: objective", result.stdout)

    def test_init_handler_symlinks_to_mm_flow_source(self) -> None:
        """init-handler should install symlinks pointing at .mm-flow sources, not .claude wrappers."""
        target = self.temp_dir / "installed-project"
        target.mkdir(parents=True, exist_ok=True)

        result = self.run_command(
            str(INIT_HANDLER),
            "--target",
            str(target),
            "--skip-postgres-check",
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        commands_link = target / ".claude" / "commands" / "mm"
        agents_link = target / ".claude" / "agents" / "mm"
        skills_link = target / ".claude" / "skills" / "mm"
        framework_commands = target / ".mm-flow" / "commands"
        framework_agents = target / ".mm-flow" / "agents"
        framework_skills = target / ".mm-flow" / "skills"
        framework_config = target / ".mm-flow" / "config"
        framework_assets = target / ".mm-flow" / "assets"
        neutral_cli = target / "bin" / "mm"
        self.assertTrue(commands_link.is_symlink())
        self.assertTrue(agents_link.is_symlink())
        self.assertTrue(skills_link.is_symlink())
        self.assertTrue(framework_commands.is_symlink())
        self.assertTrue(framework_agents.is_symlink())
        self.assertTrue(framework_skills.is_symlink())
        self.assertTrue(framework_config.is_symlink())
        self.assertTrue(framework_assets.is_symlink())
        self.assertTrue(neutral_cli.is_symlink())
        self.assertEqual(
            commands_link.resolve(), REPO_ROOT / ".mm-flow" / "commands" / "mm"
        )
        self.assertEqual(
            agents_link.resolve(), REPO_ROOT / ".mm-flow" / "agents" / "mm"
        )
        self.assertEqual(
            skills_link.resolve(), REPO_ROOT / ".mm-flow" / "skills" / "mm"
        )
        self.assertEqual(
            framework_commands.resolve(), REPO_ROOT / ".mm-flow" / "commands"
        )
        self.assertEqual(framework_agents.resolve(), REPO_ROOT / ".mm-flow" / "agents")
        self.assertEqual(framework_skills.resolve(), REPO_ROOT / ".mm-flow" / "skills")
        self.assertEqual(framework_config.resolve(), REPO_ROOT / ".mm-flow" / "config")
        self.assertEqual(framework_assets.resolve(), REPO_ROOT / ".mm-flow" / "assets")
        self.assertEqual(neutral_cli.resolve(), REPO_ROOT / "bin" / "mm")

    def test_installed_project_can_run_context_to_canonical_via_symlink(self) -> None:
        """An installed project should be able to run context-to-canonical through .claude symlinks."""
        target = self.temp_dir / "installed-project"
        target.mkdir(parents=True, exist_ok=True)
        (target / "README.md").write_text(
            "# Installed Demo\n\nBuild a scheduler.\n", encoding="utf-8"
        )

        init_result = self.run_command(
            str(INIT_HANDLER),
            "--target",
            str(target),
            "--skip-postgres-check",
        )
        self.assertEqual(
            init_result.returncode, 0, msg=init_result.stdout + init_result.stderr
        )

        result = subprocess.run(
            [
                "python3",
                str(
                    target
                    / ".claude"
                    / "commands"
                    / "mm"
                    / "context-to-canonical-handler.py"
                ),
                "--type",
                "objective",
                "--name",
                "Add Scheduler API",
            ],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("STATUS: PASSED", result.stdout)
        output_path = (
            target / "docs" / "canonical" / "objective-specs" / "add-scheduler-api.md"
        )
        self.assertTrue(output_path.exists())

    def test_installed_project_can_run_neutral_mm_cli(self) -> None:
        """An installed project should expose the neutral `mm` CLI via bin/mm."""
        target = self.temp_dir / "installed-project"
        target.mkdir(parents=True, exist_ok=True)

        init_result = self.run_command(
            str(INIT_HANDLER),
            "--target",
            str(target),
            "--skip-postgres-check",
        )
        self.assertEqual(
            init_result.returncode, 0, msg=init_result.stdout + init_result.stderr
        )

        result = subprocess.run(
            ["python3", str(target / "bin" / "mm"), "complete-task", "--help"],
            cwd=target,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Usage: mm-complete-task", result.stdout)

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
        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
            / ".mm-flow"
            / "planning"
            / "changes"
            / "project-state-mvp"
            / "execution-state.json"
        )
        self.assertTrue(objective_state_path.exists())
        objective_state = json.loads(objective_state_path.read_text(encoding="utf-8"))
        self.assertEqual(objective_state["objective_slug"], "project-state-mvp")
        self.assertIn("PS1", objective_state["tasks"])

    def test_complete_task_brief_mode_emits_model_handoff(self) -> None:
        """Brief mode should print a ready-to-use model handoff summary."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--brief", "PS1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("MODEL_BRIEF_START", result.stdout)
        self.assertIn("Objective: project-state-mvp", result.stdout)
        self.assertIn(
            ".mm-flow/planning/changes/project-state-mvp/execution-state.json",
            result.stdout,
        )
        self.assertIn(
            "python3 .claude/commands/mm/discover-contract-check.py --objective project-state-mvp",
            result.stdout,
        )

    def test_complete_task_brief_mode_accepts_task_then_flag_order(self) -> None:
        """Brief mode must work even when Claude passes `<TASK_ID> --brief`."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1", "--brief")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("MODEL_BRIEF_START", result.stdout)
        self.assertNotIn("LAUNCH: task-executor", result.stdout)
        self.assertNotIn("INFO: Starting task PS1", result.stdout)

    def test_complete_task_handler_help_exits_cleanly(self) -> None:
        """Help flags should print usage instead of being treated as a task id."""
        result = self.run_command(str(COMPLETE_TASK_HANDLER), "--help")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Usage: mm-complete-task", result.stdout)
        self.assertNotIn("Starting task --HELP", result.stdout)

    def test_neutral_cli_help_exits_cleanly(self) -> None:
        """The neutral CLI should advertise the canonical shell entrypoint."""
        result = self.run_neutral_cli("--help")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Usage: mm <command> [args]", result.stdout)
        self.assertIn("continue-task", result.stdout)

    def test_neutral_cli_dispatches_complete_task_help(self) -> None:
        """The neutral CLI should dispatch help requests to the core handler."""
        result = self.run_neutral_cli("complete-task", "--help")
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)
        self.assertIn("Usage: mm-complete-task", result.stdout)

    def test_neutral_cli_preserves_handler_exit_codes(self) -> None:
        """Invalid args should preserve the underlying handler's non-zero exit code."""
        direct = self.run_command(str(DISCOVER_HANDLER), "--not-a-real-flag")
        via_cli = self.run_neutral_cli("discover", "--not-a-real-flag")
        self.assertEqual(direct.returncode, 2)
        self.assertEqual(via_cli.returncode, direct.returncode)

    def test_active_mm_flow_has_no_verify_criteria_handler_dependency(self) -> None:
        """The active complete-task flow should not depend on the legacy verify-criteria handler."""
        self.assertFalse(VERIFY_CRITERIA_HANDLER.exists())
        handler_source = COMPLETE_TASK_HANDLER.read_text(encoding="utf-8")
        self.assertNotIn("verify-criteria-handler.py", handler_source)

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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        update_result = self.run_command(str(UPDATE_TODO_TIMES), "PS1")
        self.assertEqual(update_result.returncode, 0, msg=update_result.stderr)
        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        self.assertIn("⏱️ **Estimate**:", todo_text)
        self.assertIn("📊 **Avg/subtask**:", todo_text)

    def test_update_todo_times_replaces_metrics_without_duplication(self) -> None:
        """Repeated updates should keep a single metrics block per root task."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        runtime_state = {
            "task_id": "PS1",
            "plan_path": str(objective_dir / "tasks.md"),
            "todo_path": str(objective_dir / "todo.md"),
            "subtasks": {
                "PS1.1": {"status": "completed", "duration_seconds": 30},
                "PS1.2": {"status": "completed", "duration_seconds": 60},
                "PS1.3": {"status": "pending", "duration_seconds": 0},
            },
        }
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        first = self.run_command(str(UPDATE_TODO_TIMES), "PS1")
        second = self.run_command(str(UPDATE_TODO_TIMES), "PS1")
        self.assertEqual(first.returncode, 0, msg=first.stderr)
        self.assertEqual(second.returncode, 0, msg=second.stderr)

        todo_text = (objective_dir / "todo.md").read_text(encoding="utf-8")
        ps1_section = todo_text.split("- [ ] PS2:", 1)[0]
        self.assertEqual(ps1_section.count("⏱️ **Estimate**:"), 1)
        self.assertEqual(ps1_section.count("📊 **Avg/subtask**:"), 1)

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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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

    def test_resume_task_persists_runtime_completion_into_objective_state(self) -> None:
        """Resume should reconcile completed runtime subtasks back into execution-state.json."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        start_result = self.run_command(str(COMPLETE_TASK_HANDLER), "PS1")
        self.assertEqual(start_result.returncode, 0, msg=start_result.stderr)
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
            json.dumps(runtime_state),
            encoding="utf-8",
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

        todo_path = objective_dir / "todo.md"
        todo_text = todo_path.read_text(encoding="utf-8")
        self.assertIn("- [x] PS1: Realtime events for project_state", todo_text)
        self.assertIn("- [x] PS1.3: Run validation for PS1", todo_text)

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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
        first_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        (first_dir / "execution-state.json").write_text(
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
        self.assertEqual(
            archive_result.returncode,
            0,
            msg=archive_result.stdout + archive_result.stderr,
        )

        second = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "artifact-versioning-and-lineage",
            "Artifact Versioning and Lineage",
        )
        self.assertEqual(second.returncode, 0, msg=second.stderr)

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
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(runtime_state),
            encoding="utf-8",
        )

        result = self.run_command(str(COMPLETE_TASK_HANDLER), "T1")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(
            ".mm-flow/planning/changes/artifact-versioning-and-lineage/tasks.md",
            result.stdout,
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "archive"
            / "objectives"
            / "project-state-mvp"
        )
        self.assertTrue(archived_dir.exists())
        self.assertTrue((archived_dir / "COMPLETION-SUMMARY.md").exists())

    def test_archive_objective_infers_single_active_objective_by_default(self) -> None:
        """archive-objective should default to the sole active objective without requiring --objective."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {
                        "PS1": {"status": "completed"},
                    },
                }
            ),
            encoding="utf-8",
        )
        (self.temp_dir / ".mm-flow" / "planning" / "HANDOFF-CURRENT.md").write_text(
            "# Handoff — wrong-objective\n\n## Current objective\n- `wrong-objective`\n",
            encoding="utf-8",
        )

        archive_result = self.run_command(str(ARCHIVE_OBJECTIVE_HANDLER))
        self.assertEqual(
            archive_result.returncode,
            0,
            msg=archive_result.stdout + archive_result.stderr,
        )
        self.assertIn("project-state-mvp", archive_result.stdout)

    def test_archive_objective_allows_completed_todo_without_execution_state(
        self,
    ) -> None:
        """archive-objective should accept a fully completed package even when execution-state.json was never created."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        todo_path = objective_dir / "todo.md"
        todo_text = todo_path.read_text(encoding="utf-8")
        todo_text = todo_text.replace("- [ ] PS1:", "- [x] PS1:")
        todo_text = todo_text.replace("- [ ] PS1.1:", "- [x] PS1.1:")
        todo_text = todo_text.replace("- [ ] PS1.2:", "- [x] PS1.2:")
        todo_text = todo_text.replace("- [ ] PS1.3:", "- [x] PS1.3:")
        todo_text = todo_text.replace("- [ ] PS2:", "- [x] PS2:")
        todo_text = todo_text.replace("- [ ] PS2.1:", "- [x] PS2.1:")
        todo_text = todo_text.replace("- [ ] PS2.2:", "- [x] PS2.2:")
        todo_text = todo_text.replace("- [ ] PS2.3:", "- [x] PS2.3:")
        todo_path.write_text(todo_text, encoding="utf-8")
        (objective_dir / "HANDOFF-CURRENT.md").write_text(
            "# Handoff — project-state-mvp\n\n## Current objective\n- `project-state-mvp` — **COMPLETE**\n",
            encoding="utf-8",
        )

        archive_result = self.run_command(
            str(ARCHIVE_OBJECTIVE_HANDLER), "--objective", "project-state-mvp"
        )
        self.assertEqual(
            archive_result.returncode,
            0,
            msg=archive_result.stdout + archive_result.stderr,
        )
        self.assertIn("archive-safe", archive_result.stdout)

    def test_archive_objective_blocks_when_runtime_task_is_incomplete(self) -> None:
        """archive-objective should fail if runtime state still shows an incomplete task for the objective."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": "project-state-mvp",
                    "tasks": {
                        "PS1": {"status": "completed"},
                    },
                }
            ),
            encoding="utf-8",
        )
        (self.temp_dir / ".mm-flow" / "planning" / "task-progress.json").write_text(
            json.dumps(
                {
                    "task_id": "PS1",
                    "objective_slug": "project-state-mvp",
                    "subtasks": {
                        "PS1.1": {"status": "completed"},
                        "PS1.2": {"status": "in_progress"},
                    },
                }
            ),
            encoding="utf-8",
        )

        archive_result = self.run_command(str(ARCHIVE_OBJECTIVE_HANDLER))
        self.assertNotEqual(archive_result.returncode, 0)
        self.assertIn("runtime task PS1 is still incomplete", archive_result.stdout)

    def test_archive_objective_auto_syncs_matching_gap_registry_entry(self) -> None:
        """archive-objective should resolve a matching gap entry after a successful archive."""
        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(discover_result.returncode, 0, msg=discover_result.stderr)

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
        todo_path = objective_dir / "todo.md"
        todo_text = todo_path.read_text(encoding="utf-8")
        todo_text = todo_text.replace("- [ ] PS1:", "- [x] PS1:")
        todo_text = todo_text.replace("- [ ] PS1.1:", "- [x] PS1.1:")
        todo_text = todo_text.replace("- [ ] PS1.2:", "- [x] PS1.2:")
        todo_text = todo_text.replace("- [ ] PS1.3:", "- [x] PS1.3:")
        todo_text = todo_text.replace("- [ ] PS2:", "- [x] PS2:")
        todo_text = todo_text.replace("- [ ] PS2.1:", "- [x] PS2.1:")
        todo_text = todo_text.replace("- [ ] PS2.2:", "- [x] PS2.2:")
        todo_text = todo_text.replace("- [ ] PS2.3:", "- [x] PS2.3:")
        todo_path.write_text(todo_text, encoding="utf-8")
        (objective_dir / "HANDOFF-CURRENT.md").write_text(
            "# Handoff — project-state-mvp\n\n## Current objective\n- `project-state-mvp` — **COMPLETE**\n",
            encoding="utf-8",
        )
        gap_registry_path = (
            self.temp_dir / ".mm-flow" / "planning" / "gaps" / "gap-registry.json"
        )
        gap_registry_path.parent.mkdir(parents=True, exist_ok=True)
        gap_registry_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "gaps": [
                        {
                            "id": "gap-1234",
                            "title": "Project state follow-up",
                            "status": "open",
                            "detected_from": "some-objective",
                            "objective_slug": "some-objective",
                            "evidence": ["follow-up became a real objective"],
                            "impact": "medium",
                            "urgency": "medium",
                            "suggested_followup": "project-state-mvp",
                            "promotion_readiness": "ready",
                            "promoted_objective_slug": None,
                            "created_at_utc": "2026-06-08T00:00:00Z",
                            "updated_at_utc": "2026-06-08T00:00:00Z",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        archive_result = self.run_command(
            str(ARCHIVE_OBJECTIVE_HANDLER), "--objective", "project-state-mvp"
        )
        self.assertEqual(
            archive_result.returncode,
            0,
            msg=archive_result.stdout + archive_result.stderr,
        )
        self.assertIn("Gap registry sync", archive_result.stdout)

        registry = json.loads(gap_registry_path.read_text(encoding="utf-8"))
        entry = registry["gaps"][0]
        self.assertEqual(entry["status"], "resolved")
        self.assertEqual(entry["promoted_objective_slug"], "project-state-mvp")

    def test_discover_objective_auto_syncs_matching_gap_registry_entry(self) -> None:
        """discover objective mode should promote a matching gap entry after package creation."""
        gap_registry_path = (
            self.temp_dir / ".mm-flow" / "planning" / "gaps" / "gap-registry.json"
        )
        gap_registry_path.parent.mkdir(parents=True, exist_ok=True)
        gap_registry_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "gaps": [
                        {
                            "id": "gap-1234",
                            "title": "Project state follow-up",
                            "status": "open",
                            "detected_from": "some-objective",
                            "objective_slug": "some-objective",
                            "evidence": ["follow-up became a real objective"],
                            "impact": "medium",
                            "urgency": "medium",
                            "suggested_followup": "project-state-mvp",
                            "promotion_readiness": "ready",
                            "promoted_objective_slug": None,
                            "created_at_utc": "2026-06-08T00:00:00Z",
                            "updated_at_utc": "2026-06-08T00:00:00Z",
                        }
                    ],
                }
            ),
            encoding="utf-8",
        )

        discover_result = self.run_command(
            str(DISCOVER_HANDLER),
            "--existing",
            "--objective",
            "project-state-mvp",
            "Project State MVP",
        )
        self.assertEqual(
            discover_result.returncode,
            0,
            msg=discover_result.stdout + discover_result.stderr,
        )
        self.assertIn("GAP_REGISTRY_SYNC", discover_result.stdout)

        registry = json.loads(gap_registry_path.read_text(encoding="utf-8"))
        entry = registry["gaps"][0]
        self.assertEqual(entry["status"], "promoted")
        self.assertEqual(entry["promoted_objective_slug"], "project-state-mvp")

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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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

        objective_dir = (
            self.temp_dir / ".mm-flow" / "planning" / "changes" / "project-state-mvp"
        )
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
