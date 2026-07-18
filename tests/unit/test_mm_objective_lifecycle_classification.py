"""Regression tests for planned-versus-active objective classification."""

from __future__ import annotations

import importlib.util
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
COMMANDS_DIR = REPO_ROOT / ".mm-flow" / "commands" / "mm"
sys.path.insert(0, str(COMMANDS_DIR))


def load_module(name: str, filename: str) -> object:
    """Load one MM command module from its filesystem path."""
    module_path = COMMANDS_DIR / filename
    spec = importlib.util.spec_from_file_location(name, module_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


ACTIVE_STATE = load_module(
    "test_mm_active_objective_state", "active-objective-state.py"
)
DISCOVER = load_module("test_mm_discover_handler", "discover-handler.py")


class ObjectiveLifecycleClassificationTest(unittest.TestCase):
    """Prove that package lifecycle derives from durable state, not directory presence."""

    def setUp(self) -> None:
        """Create an isolated planning workspace."""
        self.root = Path(tempfile.mkdtemp(prefix="mm-objective-lifecycle-"))
        self.planning_dir = self.root / ".mm-flow" / "planning"
        self.changes_dir = self.planning_dir / "changes"
        self.changes_dir.mkdir(parents=True)

    def tearDown(self) -> None:
        """Remove the isolated workspace."""
        shutil.rmtree(self.root)

    def write_package(
        self,
        slug: str,
        *,
        status: str = "planned",
        active_task: str | None = None,
        task_statuses: dict[str, str] | None = None,
    ) -> Path:
        """Write a minimal objective package with a durable root-task ledger."""
        statuses = task_statuses or {"T1": "pending", "T2": "pending"}
        objective_dir = self.changes_dir / slug
        objective_dir.mkdir(parents=True)
        (objective_dir / "tasks.md").write_text(
            "# Tasks\n\n"
            + "\n".join(f"## {task_id}: Task {task_id}" for task_id in statuses)
            + "\n",
            encoding="utf-8",
        )
        (objective_dir / "execution-state.json").write_text(
            json.dumps(
                {
                    "objective_slug": slug,
                    "status": status,
                    "active_task": active_task,
                    "tasks": {
                        task_id: {"status": task_status}
                        for task_id, task_status in statuses.items()
                    },
                }
            ),
            encoding="utf-8",
        )
        return objective_dir

    def candidate_statuses(self) -> dict[str, str]:
        """Return statuses discovered solely from planning package directories."""
        return {
            candidate.slug: candidate.status
            for candidate in DISCOVER.collect_change_directory_candidates(self.root)
        }

    def test_six_planned_packages_are_non_blocking_and_discovered_as_planned(
        self,
    ) -> None:
        """Preplanned packages may coexist without becoming active by directory presence."""
        slugs = [f"planned-{index}" for index in range(1, 7)]
        for slug in slugs:
            self.write_package(slug)

        self.assertEqual(ACTIVE_STATE.active_objective_dirs(self.root), [])
        self.assertEqual(self.candidate_statuses(), {slug: "planned" for slug in slugs})

    def test_matching_runtime_activates_only_its_planned_objective(self) -> None:
        """Runtime authority overrides a stale planned top-level status for one slug."""
        self.write_package("planned-one")
        self.write_package("planned-two")
        (self.planning_dir / "task-progress.json").write_text(
            json.dumps({"objective_slug": "planned-two", "task_id": "T1"}),
            encoding="utf-8",
        )

        self.assertEqual(
            [path.name for path in ACTIVE_STATE.active_objective_dirs(self.root)],
            ["planned-two"],
        )
        self.assertEqual(
            self.candidate_statuses(),
            {"planned-one": "planned", "planned-two": "active"},
        )

    def test_planned_ledger_with_active_task_or_progressed_root_blocks(self) -> None:
        """Any execution evidence promotes a stale planned ledger to active."""
        self.write_package("has-active-task", active_task="T1")
        progressed_slugs = []
        for task_status in ("in_progress", "completed", "failed", "skipped"):
            slug = f"has-{task_status.replace('_', '-')}"
            progressed_slugs.append(slug)
            self.write_package(
                slug,
                task_statuses={"T1": task_status, "T2": "pending"},
            )
        self.write_package("top-level-active", status="active")

        self.assertEqual(
            [path.name for path in ACTIVE_STATE.active_objective_dirs(self.root)],
            sorted(["has-active-task", "top-level-active", *progressed_slugs]),
        )
        self.assertEqual(
            self.candidate_statuses(),
            {
                "has-active-task": "active",
                "top-level-active": "active",
                **{slug: "active" for slug in progressed_slugs},
            },
        )

    def test_missing_or_malformed_execution_state_blocks_fail_safe(self) -> None:
        """Unknown durable state cannot silently unblock objective activation."""
        missing = self.changes_dir / "missing-state"
        missing.mkdir()
        malformed = self.changes_dir / "malformed-state"
        malformed.mkdir()
        (malformed / "execution-state.json").write_text("{broken", encoding="utf-8")
        malformed_shape = self.changes_dir / "malformed-shape"
        malformed_shape.mkdir()
        (malformed_shape / "execution-state.json").write_text(
            json.dumps(
                {
                    "status": "planned",
                    "active_task": None,
                    "tasks": {"T1": "pending"},
                }
            ),
            encoding="utf-8",
        )

        self.assertEqual(
            [path.name for path in ACTIVE_STATE.active_objective_dirs(self.root)],
            ["malformed-shape", "malformed-state", "missing-state"],
        )
        self.assertEqual(
            self.candidate_statuses(),
            {
                "malformed-shape": "active",
                "malformed-state": "active",
                "missing-state": "active",
            },
        )

    def test_completed_exact_planned_root_set_is_discovered_done(self) -> None:
        """A complete durable ledger remains done when it matches tasks.md exactly."""
        self.write_package(
            "completed-objective",
            status="active",
            task_statuses={"T1": "completed", "T2": "completed"},
        )

        self.assertEqual(self.candidate_statuses(), {"completed-objective": "done"})

    def test_archived_package_remains_done(self) -> None:
        """Archive location remains authoritative for completed lifecycle state."""
        archived = self.planning_dir / "archive" / "objectives" / "archived-objective"
        archived.mkdir(parents=True)

        self.assertEqual(self.candidate_statuses(), {"archived-objective": "done"})

    def test_stale_bootstrapped_done_ghost_remains_non_blocking(self) -> None:
        """A roadmap-done bootstrapped ghost retains its legacy non-blocking behavior."""
        objective_dir = self.write_package("stale-ghost")
        state_path = objective_dir / "execution-state.json"
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state.pop("status")
        state.pop("active_task")
        state["bootstrapped_from_artifacts"] = True
        state_path.write_text(json.dumps(state), encoding="utf-8")
        roadmap_dir = self.planning_dir / "roadmap"
        roadmap_dir.mkdir(parents=True)
        (roadmap_dir / "objectives.json").write_text(
            json.dumps([{"slug": "stale-ghost", "status": "done"}]),
            encoding="utf-8",
        )

        self.assertEqual(ACTIVE_STATE.active_objective_dirs(self.root), [])
        self.assertEqual(self.candidate_statuses(), {"stale-ghost": "done"})

    def test_roadmap_output_does_not_emit_preplanned_packages_as_active(self) -> None:
        """Roadmap serialization preserves planned status for every preplanned package."""
        slugs = [f"roadmap-planned-{index}" for index in range(1, 7)]
        for slug in slugs:
            self.write_package(slug)
        roadmap_dir = self.planning_dir / "roadmap"

        DISCOVER.write_roadmap_files(
            self.root,
            {"roadmap_dir": str(roadmap_dir)},
        )

        objectives = json.loads(
            (roadmap_dir / "objectives.json").read_text(encoding="utf-8")
        )
        statuses = {
            objective["slug"]: objective["status"]
            for objective in objectives
            if objective["slug"] in slugs
        }
        self.assertEqual(statuses, {slug: "planned" for slug in slugs})


if __name__ == "__main__":
    unittest.main()
