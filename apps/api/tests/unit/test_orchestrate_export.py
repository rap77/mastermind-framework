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
            ),
            runtime_task_profile=SimpleNamespace(
                task_id="runtime-abc123",
                complexity="medium",
                risk_level="medium",
                requires_checker=True,
            ),
            runtime_loop_policy=SimpleNamespace(
                base_loop="execute+verify-light",
                additional_loops=("verify-light",),
                requires_review=False,
                requires_verification=True,
            ),
        )

        payload = build_execution_export(
            results,
            runtime_contracts={
                "task_profile": {
                    "task_id": coordinator.runtime_task_profile.task_id,
                    "complexity": coordinator.runtime_task_profile.complexity,
                    "risk_level": coordinator.runtime_task_profile.risk_level,
                    "requires_checker": coordinator.runtime_task_profile.requires_checker,
                },
                "loop_policy": {
                    "base_loop": coordinator.runtime_loop_policy.base_loop,
                    "additional_loops": list(
                        coordinator.runtime_loop_policy.additional_loops
                    ),
                    "requires_review": coordinator.runtime_loop_policy.requires_review,
                    "requires_verification": coordinator.runtime_loop_policy.requires_verification,
                },
            },
            evidence_routing=coordinator.runtime_evidence_selection,
        )

        self.assertIn("results", payload)
        self.assertIn("execution_summary", payload)
        routing = payload["execution_summary"]["evidence_routing"]
        self.assertEqual(routing["selected_harness"], "evidence-intake-canonization")
        self.assertEqual(routing["readiness_score"], 72.0)
        contracts = payload["execution_summary"]["runtime_contracts"]
        self.assertEqual(contracts["task_profile"]["task_id"], "runtime-abc123")


if __name__ == "__main__":
    unittest.main()
