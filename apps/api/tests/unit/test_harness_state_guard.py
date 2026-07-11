"""Guard rails for the canonical harness state sources."""

from __future__ import annotations

from pathlib import Path

from mastermind_cli.mm_flow.planning_bridge import PlanningBridge
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter


def test_canonical_harness_state_sources_are_explicit() -> None:
    """The current harness state should be explicit and internally consistent."""
    repo_root = Path(__file__).resolve().parents[4]
    aidlc_state = (repo_root / "aidlc-docs" / "aidlc-state.md").read_text(
        encoding="utf-8"
    )
    planning_handoff = (repo_root / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )

    assert "- active_objective: manifest-contract-bridge-v1" in aidlc_state
    assert "- `harness-memory-unification` — unified harness + memory platform" in (
        planning_handoff
    )
    assert "## Next command" in planning_handoff

    bridge = PlanningBridge(project_root=repo_root)
    request = bridge.build_request()

    assert request.design_objective == "manifest-contract-bridge-v1"
    assert request.operational_objective == "harness-memory-unification"
    assert "planning_objective_differs_from_design_objective" in request.warnings

    adapter = ProjectAdapter.for_repo(repo_root)
    warnings = adapter.collect_warnings()
    warning_codes = {warning.code for warning in warnings}
    assert "source_of_truth_split_unclear" not in warning_codes
