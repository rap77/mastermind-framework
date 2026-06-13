"""Tests for the MM gap registry helper."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
GAP_REGISTRY_HELPER = REPO_ROOT / ".mm-flow" / "commands" / "mm" / "gap-registry.py"


class GapRegistryHelperTest(unittest.TestCase):
    """Exercise gap registry register/list/promote behavior."""

    def setUp(self) -> None:
        """Create a temporary git workspace."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-gap-registry-"))
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

    def tearDown(self) -> None:
        """Remove the temporary workspace."""
        shutil.rmtree(self.temp_dir)

    def run_helper(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the gap registry helper in the temp workspace."""
        return subprocess.run(
            ["python3", str(GAP_REGISTRY_HELPER), *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def registry_path(self) -> Path:
        """Return the registry path inside the temp workspace."""
        return self.temp_dir / ".mm-flow" / "planning" / "gaps" / "gap-registry.json"

    def create_objective_artifact(self, slug: str, archived: bool = False) -> None:
        """Create a minimal objective artifact directory for lifecycle sync tests."""
        base = "archive/objectives" if archived else "changes"
        (self.temp_dir / ".mm-flow" / "planning" / base / slug).mkdir(parents=True)

    def test_register_creates_registry_and_persists_gap(self) -> None:
        """Register should create the artifact and store the requested gap."""
        result = self.run_helper(
            "register",
            "--title",
            "Task runner validation isolation",
            "--detected-from",
            "rag-scale-out-brains-2-7",
            "--objective-slug",
            "rag-scale-out-brains-2-7",
            "--evidence",
            "task_runner tests still hang under focused patches",
            "--impact",
            "medium",
            "--urgency",
            "medium",
            "--suggested-followup",
            "task-runner-test-isolation",
            "--promotion-readiness",
            "ready",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(self.registry_path().exists())

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        self.assertEqual(registry["version"], 1)
        self.assertEqual(len(registry["gaps"]), 1)
        self.assertEqual(registry["gaps"][0]["id"], "gap-0001")
        self.assertEqual(registry["gaps"][0]["status"], "open")

    def test_list_defaults_to_open_and_deferred_gaps(self) -> None:
        """List without --all should omit promoted gaps."""
        self.run_helper(
            "register",
            "--id",
            "gap-open",
            "--title",
            "Open gap",
            "--detected-from",
            "objective-a",
            "--evidence",
            "open evidence",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-deferred",
            "--title",
            "Deferred gap",
            "--detected-from",
            "objective-b",
            "--evidence",
            "deferred evidence",
            "--status",
            "deferred",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-promoted",
            "--title",
            "Promoted gap",
            "--detected-from",
            "objective-c",
            "--evidence",
            "promoted evidence",
        )
        self.run_helper(
            "promote",
            "--id",
            "gap-promoted",
            "--objective-slug",
            "objective-promoted",
        )

        result = self.run_helper("list")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        gap_ids = [entry["id"] for entry in payload["gaps"]]

        self.assertEqual(gap_ids, ["gap-open", "gap-deferred"])

    def test_promote_marks_existing_gap_without_creating_objective(self) -> None:
        """Promote should only mutate the registry entry state."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Codegen restoration",
            "--detected-from",
            "vertical-slice",
            "--evidence",
            "ts-proto shim still manual",
        )

        result = self.run_helper(
            "promote",
            "--id",
            "gap-1234",
            "--objective-slug",
            "vertical-slice-codegen-restoration",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        entry = registry["gaps"][0]
        self.assertEqual(entry["status"], "promoted")
        self.assertEqual(
            entry["promoted_objective_slug"],
            "vertical-slice-codegen-restoration",
        )

    def test_duplicates_reports_same_suggested_followup(self) -> None:
        """Duplicate suspects should surface gaps sharing a follow-up slug."""
        self.run_helper(
            "register",
            "--id",
            "gap-a",
            "--title",
            "Worker runtime follow-up",
            "--detected-from",
            "rust-control-plane",
            "--evidence",
            "runtime seam follow-up",
            "--suggested-followup",
            "worker-runtime-followup",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-b",
            "--title",
            "Rust worker seam cleanup",
            "--detected-from",
            "rust-control-plane",
            "--evidence",
            "same follow-up different wording",
            "--suggested-followup",
            "worker-runtime-followup",
        )

        result = self.run_helper("duplicates")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(len(payload["suspects"]), 1)
        suspect = payload["suspects"][0]
        self.assertEqual(suspect["gap_ids"], ["gap-a", "gap-b"])
        self.assertEqual(suspect["reasons"], ["same_suggested_followup"])

    def test_duplicates_reports_same_normalized_title(self) -> None:
        """Duplicate suspects should surface gaps sharing a normalized title."""
        self.run_helper(
            "register",
            "--id",
            "gap-a",
            "--title",
            "Gap registry dedupe and prioritization",
            "--detected-from",
            "objective-a",
            "--evidence",
            "first phrasing",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-b",
            "--title",
            "gap registry: dedupe and prioritization",
            "--detected-from",
            "objective-b",
            "--evidence",
            "second phrasing",
        )

        result = self.run_helper("duplicates")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(len(payload["suspects"]), 1)
        suspect = payload["suspects"][0]
        self.assertEqual(suspect["gap_ids"], ["gap-a", "gap-b"])
        self.assertEqual(suspect["reasons"], ["same_normalized_title"])

    def test_next_prefers_ready_then_impact_then_urgency(self) -> None:
        """Next should rank by readiness, then impact, then urgency."""
        self.run_helper(
            "register",
            "--id",
            "gap-low-readiness",
            "--title",
            "Needs more evidence",
            "--detected-from",
            "objective-a",
            "--evidence",
            "not ready",
            "--impact",
            "high",
            "--urgency",
            "high",
            "--promotion-readiness",
            "needs_more_evidence",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-medium",
            "--title",
            "Ready but lower impact",
            "--detected-from",
            "objective-b",
            "--evidence",
            "ready medium impact",
            "--impact",
            "medium",
            "--urgency",
            "high",
            "--promotion-readiness",
            "ready",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-top",
            "--title",
            "Ready high impact high urgency",
            "--detected-from",
            "objective-c",
            "--evidence",
            "top candidate",
            "--impact",
            "high",
            "--urgency",
            "high",
            "--promotion-readiness",
            "ready",
        )

        result = self.run_helper("next")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["recommended_gap"]["id"], "gap-top")
        ranked_ids = [entry["id"] for entry in payload["ranked_open_gaps"]]
        self.assertEqual(
            ranked_ids,
            ["gap-top", "gap-medium", "gap-low-readiness"],
        )

    def test_next_uses_creation_order_as_stable_tie_break(self) -> None:
        """Next should keep earlier gaps first when all priority fields tie."""
        self.run_helper(
            "register",
            "--id",
            "gap-early",
            "--title",
            "Early gap",
            "--detected-from",
            "objective-a",
            "--evidence",
            "first gap",
            "--impact",
            "medium",
            "--urgency",
            "medium",
            "--promotion-readiness",
            "ready",
        )
        self.run_helper(
            "register",
            "--id",
            "gap-late",
            "--title",
            "Late gap",
            "--detected-from",
            "objective-b",
            "--evidence",
            "second gap",
            "--impact",
            "medium",
            "--urgency",
            "medium",
            "--promotion-readiness",
            "ready",
        )

        result = self.run_helper("next")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)

        ranked_ids = [entry["id"] for entry in payload["ranked_open_gaps"]]
        self.assertEqual(ranked_ids, ["gap-early", "gap-late"])

    def test_sync_objective_marks_gap_promoted_when_change_exists(self) -> None:
        """Sync should mark a matching gap as promoted when the objective is active."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Gap promotion workflow",
            "--detected-from",
            "mm-harness-gap-dedupe-and-priority",
            "--evidence",
            "registry drift after opening an objective",
            "--suggested-followup",
            "mm-harness-gap-objective-lifecycle-sync",
        )
        self.create_objective_artifact("mm-harness-gap-objective-lifecycle-sync")

        result = self.run_helper(
            "sync-objective",
            "--objective-slug",
            "mm-harness-gap-objective-lifecycle-sync",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        entry = registry["gaps"][0]
        self.assertEqual(entry["status"], "promoted")
        self.assertEqual(
            entry["promoted_objective_slug"],
            "mm-harness-gap-objective-lifecycle-sync",
        )

    def test_sync_objective_marks_gap_resolved_when_archive_exists(self) -> None:
        """Sync should mark a matching gap as resolved when the objective is archived."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Gap promotion workflow",
            "--detected-from",
            "mm-harness-gap-dedupe-and-priority",
            "--evidence",
            "registry drift after archiving an objective",
            "--suggested-followup",
            "mm-harness-gap-objective-lifecycle-sync",
        )
        self.create_objective_artifact(
            "mm-harness-gap-objective-lifecycle-sync",
            archived=True,
        )

        result = self.run_helper(
            "sync-objective",
            "--objective-slug",
            "mm-harness-gap-objective-lifecycle-sync",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        entry = registry["gaps"][0]
        self.assertEqual(entry["status"], "resolved")
        self.assertEqual(
            entry["promoted_objective_slug"],
            "mm-harness-gap-objective-lifecycle-sync",
        )

    def test_prepare_promotion_emits_next_discover_command_for_ready_gap(self) -> None:
        """Prepare-promotion should emit the exact discover command for a ready open gap."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Gap promotion assistant",
            "--detected-from",
            "mm-harness-gap-registry-ui-triage",
            "--evidence",
            "operators still need a bridge from gap to objective",
            "--suggested-followup",
            "mm-harness-gap-promotion-assistant",
            "--promotion-readiness",
            "ready",
        )

        result = self.run_helper("prepare-promotion", "--id", "gap-1234")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn(
            "OBJECTIVE_SLUG: mm-harness-gap-promotion-assistant", result.stdout
        )
        self.assertIn(
            'NEXT_COMMAND: /mm:discover --existing --objective mm-harness-gap-promotion-assistant "Gap promotion assistant"',
            result.stdout,
        )

    def test_prepare_promotion_fails_when_gap_not_ready(self) -> None:
        """Prepare-promotion should fail for non-ready gaps."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Gap promotion assistant",
            "--detected-from",
            "mm-harness-gap-registry-ui-triage",
            "--evidence",
            "still needs evidence",
            "--suggested-followup",
            "mm-harness-gap-promotion-assistant",
            "--promotion-readiness",
            "needs_more_evidence",
        )

        result = self.run_helper("prepare-promotion", "--id", "gap-1234")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Gap is not promotion-ready", result.stdout)

    def test_prepare_promotion_fails_when_objective_already_exists(self) -> None:
        """Prepare-promotion should fail when the suggested objective already exists."""
        self.run_helper(
            "register",
            "--id",
            "gap-1234",
            "--title",
            "Gap promotion assistant",
            "--detected-from",
            "mm-harness-gap-registry-ui-triage",
            "--evidence",
            "objective already active",
            "--suggested-followup",
            "mm-harness-gap-promotion-assistant",
            "--promotion-readiness",
            "ready",
        )
        self.create_objective_artifact("mm-harness-gap-promotion-assistant")

        result = self.run_helper("prepare-promotion", "--id", "gap-1234")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Objective already exists in changes/", result.stdout)


if __name__ == "__main__":
    unittest.main()
