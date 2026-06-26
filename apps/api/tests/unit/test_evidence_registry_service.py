"""Tests for the evidence registry service."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from mastermind_cli.mm_flow.evidence_registry_service import EvidenceRegistryService


class EvidenceRegistryServiceTest(unittest.TestCase):
    """Exercise the canonical evidence registry runtime service."""

    def setUp(self) -> None:
        """Create a temporary registry path for each test."""
        self._tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmpdir.cleanup)
        self.registry_path = Path(self._tmpdir.name) / "evidence-registry.json"
        self.service = EvidenceRegistryService(self.registry_path)

    def test_register_version_creates_registry_and_source_entry(self) -> None:
        """Registering a first evidence version should persist source and version rows."""
        result = self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-1",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )

        self.assertEqual(result["version"]["id"], "ev-0001")
        self.assertIsNone(result["delta"])

        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.assertEqual(data["sources"][0]["source_id"], "canonical:prd:alpha")
        self.assertEqual(data["versions"][0]["state"], "current")
        self.assertEqual(data["deltas"], [])

    def test_register_version_supersedes_previous_hash_change(self) -> None:
        """A new hash for the same source should supersede the prior version."""
        first = self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-1",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )
        second = self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-2",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )

        self.assertEqual(first["version"]["id"], "ev-0001")
        self.assertEqual(second["version"]["id"], "ev-0002")
        self.assertEqual(second["delta"]["decision"], "superseded")

        data = json.loads(self.registry_path.read_text(encoding="utf-8"))
        self.assertEqual(data["versions"][0]["state"], "superseded")
        self.assertEqual(data["versions"][1]["state"], "current")
        self.assertEqual(data["deltas"][0]["from_version_id"], "ev-0001")
        self.assertEqual(data["deltas"][0]["to_version_id"], "ev-0002")

    def test_record_explicit_delta_validates_version_ids(self) -> None:
        """Recording a delta should fail until both version IDs exist."""
        self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-1",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )

        with self.assertRaisesRegex(ValueError, "Both version IDs"):
            self.service.record_explicit_delta(
                from_version_id="ev-0001",
                to_version_id="ev-0002",
                delta_type="decision",
                summary="Updated after review",
            )

    def test_list_deltas_supports_filters(self) -> None:
        """Delta listing should filter by source, type, and decision."""
        self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-1",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )
        self.service.register_version(
            source_id="canonical:prd:alpha",
            source_type="doc",
            name="Alpha",
            uri="docs/alpha.md",
            version_ref="docs/alpha.md",
            version_hash="hash-2",
            summary="Canonical alpha doc",
            confidence=1.0,
            coverage=1.0,
            user_answers_complete=True,
        )
        data = self.service.load_registry()
        self.service.record_delta(
            data,
            from_version_id="ev-0001",
            to_version_id="ev-0002",
            delta_type="functional",
            summary="Functional gap closed",
            impact="high",
            risk="medium",
            decision="adapted",
            source_id="canonical:prd:alpha",
        )
        self.service.write_registry(data)

        filtered = self.service.list_deltas(
            source_id="canonical:prd:alpha",
            delta_type="functional",
            decision="adapted",
        )

        self.assertEqual(len(filtered["deltas"]), 1)
        self.assertEqual(filtered["deltas"][0]["summary"], "Functional gap closed")

    def test_readiness_matches_completion_criteria(self) -> None:
        """Readiness should reuse the deterministic completion rubric."""
        version = self.service.register_version(
            source_id="canonical:prd:beta",
            source_type="doc",
            name="Beta",
            uri="docs/beta.md",
            version_ref="docs/beta.md",
            version_hash="hash-1",
            summary="Canonical beta doc",
            confidence=0.9,
            coverage=0.9,
            user_answers_complete=True,
        )
        readiness = self.service.readiness(version["version"]["id"])

        self.assertEqual(readiness["readiness"]["verdict"], "ready")
        self.assertEqual(
            readiness["readiness"]["reason"], "high_confidence_high_coverage"
        )
        self.assertGreaterEqual(readiness["score"]["score"], 80.0)
        self.assertEqual(readiness["score"]["gate"], "ready")

    def test_readiness_score_penalizes_gaps_and_contradictions(self) -> None:
        """Critical gaps and contradictions should push the score down."""
        version = self.service.register_version(
            source_id="canonical:prd:gamma",
            source_type="doc",
            name="Gamma",
            uri="docs/gamma.md",
            version_ref="docs/gamma.md",
            version_hash="hash-1",
            summary="Canonical gamma doc",
            confidence=0.9,
            coverage=0.9,
            critical_gaps=2,
            important_gaps=1,
            contradictions=1,
            user_answers_complete=False,
        )
        readiness = self.service.readiness(version["version"]["id"])

        self.assertLess(readiness["score"]["score"], 65.0)
        self.assertIn(readiness["score"]["gate"], {"blocked", "not_ready"})


if __name__ == "__main__":
    unittest.main()
