"""Tests for orchestrate export payloads."""

from __future__ import annotations

import unittest
from types import SimpleNamespace

from mastermind_cli.mm_flow.evidence_export import build_execution_export


class OrchestrateExportTest(unittest.TestCase):
    """Verify execution exports preserve routing metadata."""

    def test_export_includes_evidence_routing_summary(self) -> None:
        """Evidence routing should be included in exported top-level metadata."""
        results = {
            "brain-01-product-strategy": SimpleNamespace(
                model_dump=lambda: {"positioning": "Positioning", "generated_at": "x"}
            )
        }
        coordinator = SimpleNamespace(
            runtime_evidence_selection=SimpleNamespace(
                selected_harness="evidence-intake-canonization",
                selected_loop="goal-loop",
                selected_brain=None,
                reasons=("partial-evidence-with-controlled-risk",),
                risks=("canonization_may_need_followup",),
                next_actions=("canonize_sources", "record_deltas"),
                readiness_gate="conditionally_ready",
                readiness_score=72.0,
            )
        )

        payload = build_execution_export(
            results, coordinator.runtime_evidence_selection
        )

        self.assertIn("results", payload)
        self.assertIn("execution_summary", payload)
        routing = payload["execution_summary"]["evidence_routing"]
        self.assertEqual(routing["selected_harness"], "evidence-intake-canonization")
        self.assertEqual(routing["readiness_score"], 72.0)


if __name__ == "__main__":
    unittest.main()
