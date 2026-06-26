"""Tests for the MM evidence registry helper."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
EVIDENCE_REGISTRY_HELPER = (
    REPO_ROOT / ".mm-flow" / "commands" / "mm" / "evidence-registry.py"
)


class EvidenceRegistryHelperTest(unittest.TestCase):
    """Exercise evidence registry register/list/readiness behavior."""

    def setUp(self) -> None:
        """Create a temporary git workspace."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-evidence-registry-"))
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
        """Run the evidence registry helper in the temp workspace."""
        return subprocess.run(
            ["python3", str(EVIDENCE_REGISTRY_HELPER), *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def registry_path(self) -> Path:
        """Return the registry path inside the temp workspace."""
        return (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "evidence"
            / "evidence-registry.json"
        )

    def test_register_creates_registry_and_persists_version(self) -> None:
        """Register should create the artifact and store the requested version."""
        result = self.run_helper(
            "register",
            "--source-id",
            "source-hermes",
            "--source-type",
            "repo",
            "--name",
            "Hermes Agent",
            "--uri",
            "https://github.com/nousresearch/hermes-agent",
            "--version-ref",
            "v1.0.0",
            "--version-hash",
            "abc123",
            "--summary",
            "Persistent memory and skill-based procedural flow",
            "--confidence",
            "0.92",
            "--coverage",
            "0.9",
            "--user-answers-complete",
        )

        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(self.registry_path().exists())

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        self.assertEqual(registry["version"], 1)
        self.assertEqual(len(registry["sources"]), 1)
        self.assertEqual(len(registry["versions"]), 1)
        self.assertEqual(registry["versions"][0]["id"], "ev-0001")

    def test_readiness_returns_ready_for_high_confidence_high_coverage(self) -> None:
        """Readiness should return ready when the evidence is strong."""
        self.run_helper(
            "register",
            "--id",
            "ev-ready",
            "--source-id",
            "source-ready",
            "--source-type",
            "doc",
            "--name",
            "Evidence Doc",
            "--uri",
            "file:///tmp/evidence.md",
            "--version-ref",
            "r1",
            "--version-hash",
            "hash-ready",
            "--summary",
            "Strong evidence",
            "--confidence",
            "0.95",
            "--coverage",
            "0.95",
            "--user-answers-complete",
        )

        result = self.run_helper("readiness", "--id", "ev-ready")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["readiness"]["verdict"], "ready")
        self.assertEqual(
            payload["readiness"]["reason"], "high_confidence_high_coverage"
        )

    def test_readiness_blocks_when_critical_gaps_exist(self) -> None:
        """Readiness should block when critical gaps remain open."""
        self.run_helper(
            "register",
            "--id",
            "ev-gap",
            "--source-type",
            "book",
            "--name",
            "Spec Book",
            "--uri",
            "file:///tmp/spec-book.pdf",
            "--version-ref",
            "chap-1",
            "--version-hash",
            "hash-gap",
            "--summary",
            "Useful but incomplete",
            "--confidence",
            "0.85",
            "--coverage",
            "0.6",
            "--critical-gaps",
            "2",
        )

        result = self.run_helper("readiness", "--id", "ev-gap")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["readiness"]["verdict"], "not_ready")
        self.assertEqual(payload["readiness"]["reason"], "critical_gaps_open")

    def test_delta_records_change_between_versions(self) -> None:
        """Delta should record a version-to-version change."""
        self.run_helper(
            "register",
            "--id",
            "ev-old",
            "--source-id",
            "source-delta-a",
            "--source-type",
            "doc",
            "--name",
            "Delta Doc",
            "--uri",
            "docs/old.md",
            "--version-ref",
            "old",
            "--version-hash",
            "hash-old",
            "--summary",
            "Old evidence",
            "--confidence",
            "0.8",
            "--coverage",
            "0.8",
            "--user-answers-complete",
        )
        self.run_helper(
            "register",
            "--id",
            "ev-new",
            "--source-id",
            "source-delta-b",
            "--source-type",
            "doc",
            "--name",
            "Delta Doc",
            "--uri",
            "docs/new.md",
            "--version-ref",
            "new",
            "--version-hash",
            "hash-new",
            "--summary",
            "New evidence",
            "--confidence",
            "0.9",
            "--coverage",
            "0.9",
            "--user-answers-complete",
        )

        result = self.run_helper(
            "delta",
            "--from-id",
            "ev-old",
            "--to-id",
            "ev-new",
            "--delta-type",
            "decision",
            "--summary",
            "Canonical doc refined with newer evidence",
            "--impact",
            "medium",
            "--risk",
            "low",
            "--decision",
            "adapted",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["delta"]["id"], "ed-0001")
        self.assertEqual(payload["delta"]["from_version_id"], "ev-old")
        self.assertEqual(payload["delta"]["to_version_id"], "ev-new")
        self.assertEqual(payload["delta"]["delta_type"], "decision")
        self.assertEqual(payload["delta"]["decision"], "adapted")

    def test_list_deltas_returns_registered_deltas(self) -> None:
        """List-deltas should expose the recorded delta entries."""
        self.run_helper(
            "register",
            "--id",
            "ev-a",
            "--source-id",
            "source-list-a",
            "--source-type",
            "doc",
            "--name",
            "Doc A",
            "--uri",
            "docs/a.md",
            "--version-ref",
            "a",
            "--version-hash",
            "hash-a",
            "--summary",
            "A",
            "--user-answers-complete",
        )
        self.run_helper(
            "register",
            "--id",
            "ev-b",
            "--source-id",
            "source-list-b",
            "--source-type",
            "doc",
            "--name",
            "Doc B",
            "--uri",
            "docs/b.md",
            "--version-ref",
            "b",
            "--version-hash",
            "hash-b",
            "--summary",
            "B",
            "--user-answers-complete",
        )
        self.run_helper(
            "delta",
            "--from-id",
            "ev-a",
            "--to-id",
            "ev-b",
            "--delta-type",
            "functional",
            "--summary",
            "Added new behavior",
            "--impact",
            "high",
            "--risk",
            "medium",
            "--decision",
            "adopted",
        )

        result = self.run_helper("list-deltas")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["deltas"]), 1)
        self.assertEqual(payload["deltas"][0]["id"], "ed-0001")
        self.assertEqual(payload["deltas"][0]["delta_type"], "functional")

    def test_list_deltas_filters_by_source_id(self) -> None:
        """List-deltas should filter by source ID."""
        self.run_helper(
            "register",
            "--id",
            "ev-src-a",
            "--source-id",
            "source-filter-a",
            "--source-type",
            "doc",
            "--name",
            "Doc A",
            "--uri",
            "docs/a.md",
            "--version-ref",
            "a",
            "--version-hash",
            "hash-a",
            "--summary",
            "A",
            "--user-answers-complete",
        )
        self.run_helper(
            "register",
            "--id",
            "ev-src-b",
            "--source-id",
            "source-filter-b",
            "--source-type",
            "doc",
            "--name",
            "Doc B",
            "--uri",
            "docs/b.md",
            "--version-ref",
            "b",
            "--version-hash",
            "hash-b",
            "--summary",
            "B",
            "--user-answers-complete",
        )
        self.run_helper(
            "delta",
            "--from-id",
            "ev-src-a",
            "--to-id",
            "ev-src-b",
            "--delta-type",
            "decision",
            "--summary",
            "Changed",
            "--impact",
            "medium",
            "--risk",
            "low",
            "--decision",
            "adapted",
        )

        result = self.run_helper(
            "list-deltas",
            "--source-id",
            "source-filter-b",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(len(payload["deltas"]), 1)
        self.assertEqual(payload["deltas"][0]["source_id"], "source-filter-b")

    def test_register_adds_auto_delta_for_same_source_update(self) -> None:
        """Registering a newer version for the same source should create a delta."""
        self.run_helper(
            "register",
            "--id",
            "ev-old",
            "--source-id",
            "source-auto-delta",
            "--source-type",
            "doc",
            "--name",
            "Auto Delta Doc",
            "--uri",
            "docs/auto-old.md",
            "--version-ref",
            "old",
            "--version-hash",
            "hash-old",
            "--summary",
            "Old canonical content",
            "--user-answers-complete",
        )
        self.run_helper(
            "register",
            "--id",
            "ev-new",
            "--source-id",
            "source-auto-delta",
            "--source-type",
            "doc",
            "--name",
            "Auto Delta Doc",
            "--uri",
            "docs/auto-new.md",
            "--version-ref",
            "new",
            "--version-hash",
            "hash-new",
            "--summary",
            "Updated canonical content",
            "--user-answers-complete",
        )

        registry = json.loads(self.registry_path().read_text(encoding="utf-8"))
        self.assertEqual(len(registry["versions"]), 2)
        self.assertEqual(len(registry["deltas"]), 1)
        delta = registry["deltas"][0]
        self.assertEqual(delta["from_version_id"], "ev-old")
        self.assertEqual(delta["to_version_id"], "ev-new")
        self.assertEqual(delta["decision"], "superseded")


if __name__ == "__main__":
    unittest.main()
