"""Tests for deterministic evidence harness routing."""

from __future__ import annotations

import unittest

from mastermind_cli.mm_flow.evidence_selector import (
    EvidenceHarnessSelector,
    EvidenceSelectionRequest,
)


class EvidenceHarnessSelectorTest(unittest.TestCase):
    """Verify evidence routing stays minimal and deterministic."""

    def test_routes_clear_sources_to_intake_only(self) -> None:
        """Clear, low-risk evidence should stay on the cheapest path."""
        selector = EvidenceHarnessSelector()
        payload = selector.select(
            EvidenceSelectionRequest(
                objective="Summarize this product page",
                source_clarity="clear",
                uncertainty="low",
                gap_count=0,
                token_budget=800,
            )
        )

        self.assertEqual(payload.selected_harness, "evidence-intake-only")
        self.assertEqual(payload.selected_loop, "tool-loop")
        self.assertIn("clear-source-minimum-path", payload.reasons)

    def test_routes_partial_evidence_to_canonization(self) -> None:
        """Partial evidence with controlled risk should canonize instead of escalating."""
        selector = EvidenceHarnessSelector()
        payload = selector.select(
            EvidenceSelectionRequest(
                objective="Canonize notes from a book chapter",
                source_clarity="partial",
                uncertainty="medium",
                gap_count=1,
                readiness_gate="conditionally_ready",
                readiness_score=72.0,
            )
        )

        self.assertEqual(payload.selected_harness, "evidence-intake-canonization")
        self.assertEqual(payload.selected_loop, "goal-loop")
        self.assertEqual(payload.next_actions, ("canonize_sources", "record_deltas"))

    def test_routes_ready_spec_work_to_ai_dlc(self) -> None:
        """Ready spec or implementation work should hand off to AI-DLC."""
        selector = EvidenceHarnessSelector()
        payload = selector.select(
            EvidenceSelectionRequest(
                objective="Write the implementation spec for the new harness",
                source_clarity="clear",
                uncertainty="low",
                gap_count=0,
                readiness_gate="ready",
                readiness_score=92.0,
            )
        )

        self.assertEqual(payload.selected_harness, "ai-dlc-harness")
        self.assertEqual(payload.selected_loop, "goal-loop")
        self.assertEqual(payload.next_actions, ("launch_ai_dlc_workflow",))


if __name__ == "__main__":
    unittest.main()
