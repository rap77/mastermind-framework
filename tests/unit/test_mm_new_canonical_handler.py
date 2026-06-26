"""Tests for the MM new canonical handler."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
NEW_CANONICAL_HELPER = (
    REPO_ROOT / ".mm-flow" / "commands" / "mm" / "new-canonical-handler.py"
)


class NewCanonicalHandlerTest(unittest.TestCase):
    """Exercise canonical creation and automatic evidence registration."""

    def setUp(self) -> None:
        """Create a temporary git workspace."""
        self.temp_dir = Path(tempfile.mkdtemp(prefix="mm-new-canonical-"))
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
        template_dir = self.temp_dir / "docs" / "canonical" / "templates"
        template_dir.mkdir(parents=True, exist_ok=True)
        (template_dir / "00-PRD-Template.md").write_text(
            "# {{TITLE}}\n\nName: {{NAME}}\n",
            encoding="utf-8",
        )
        (template_dir / "02-Metodo-Seleccion-Expertos.md").write_text(
            "# {{TITLE}}\n\nBrain: {{NAME}}\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        """Remove the temporary workspace."""
        shutil.rmtree(self.temp_dir)

    def run_helper(self, *args: str) -> subprocess.CompletedProcess[str]:
        """Run the canonical handler in the temp workspace."""
        return subprocess.run(
            ["python3", str(NEW_CANONICAL_HELPER), *args],
            cwd=self.temp_dir,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_prd_creation_registers_evidence_version(self) -> None:
        """Creating a PRD should write the doc and register it in evidence."""
        result = self.run_helper(
            "prd",
            "--name",
            "launch-plan",
            "--title",
            "Launch Plan",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        created_doc = self.temp_dir / "docs" / "PRD" / "launch-plan.md"
        self.assertTrue(created_doc.exists())

        registry_path = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "evidence"
            / "evidence-registry.json"
        )
        self.assertTrue(registry_path.exists())

        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(
            registry["sources"][0]["source_id"], "canonical:prd:launch-plan"
        )
        self.assertEqual(registry["versions"][0]["source_type"], "doc")
        self.assertEqual(registry["versions"][0]["name"], "Launch Plan")
        self.assertEqual(registry["versions"][0]["state"], "current")

    def test_brain_creation_uses_custom_output_and_registers_evidence(self) -> None:
        """Creating a brain should honor --output and register evidence."""
        custom_output = self.temp_dir / "canonical" / "brain-spec.md"
        result = self.run_helper(
            "brain",
            "--name",
            "brain-01",
            "--title",
            "Strategy Brain",
            "--output",
            str(custom_output),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        self.assertTrue(custom_output.exists())

        registry_path = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "evidence"
            / "evidence-registry.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(
            registry["sources"][0]["source_id"],
            "canonical:brain:brain-01",
        )
        self.assertEqual(registry["versions"][0]["uri"], "canonical/brain-spec.md")
        self.assertEqual(registry["versions"][0]["name"], "Strategy Brain")

    def test_prd_creation_supports_output_outside_repo_root(self) -> None:
        """Creating a PRD should work even when --output points outside the repo."""
        external_output = Path(tempfile.gettempdir()) / "mm-external-prd.md"
        if external_output.exists():
            external_output.unlink()

        result = self.run_helper(
            "prd",
            "--name",
            "external-launch",
            "--title",
            "External Launch",
            "--output",
            str(external_output),
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(external_output.exists())

        registry_path = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "evidence"
            / "evidence-registry.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(
            registry["versions"][0]["uri"], external_output.resolve().as_posix()
        )
        self.assertEqual(
            registry["versions"][0]["version_ref"], external_output.resolve().as_posix()
        )

    def test_update_prd_overwrites_doc_and_supersedes_previous_version(self) -> None:
        """Updating a PRD should overwrite it and supersede the previous evidence."""
        result = self.run_helper(
            "prd", "--name", "launch-plan", "--title", "Launch Plan"
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        update_result = self.run_helper(
            "update",
            "--name",
            "launch-plan",
            "--title",
            "Launch Plan v2",
        )
        self.assertEqual(update_result.returncode, 0, msg=update_result.stderr)

        created_doc = self.temp_dir / "docs" / "PRD" / "launch-plan.md"
        self.assertIn("Launch Plan v2", created_doc.read_text(encoding="utf-8"))

        registry_path = (
            self.temp_dir
            / ".mm-flow"
            / "planning"
            / "evidence"
            / "evidence-registry.json"
        )
        registry = json.loads(registry_path.read_text(encoding="utf-8"))
        self.assertEqual(len(registry["versions"]), 2)
        self.assertEqual(len(registry["deltas"]), 1)
        self.assertEqual(registry["versions"][0]["state"], "superseded")
        self.assertEqual(registry["versions"][1]["state"], "current")
        self.assertEqual(registry["deltas"][0]["decision"], "superseded")


if __name__ == "__main__":
    unittest.main()
