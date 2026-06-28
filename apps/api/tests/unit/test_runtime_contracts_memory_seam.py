"""Tests for the memory snapshot seam in the harness core."""

from mastermind_cli.memory_layer.models import ContextSnapshot
from mastermind_cli.orchestrator.runtime_contracts import HarnessCore, RuntimeRequest
from mastermind_cli.types.interfaces import Brief


def test_harness_core_uses_injected_memory_snapshot() -> None:
    """The core should carry an injected memory snapshot through selection."""
    snapshot = ContextSnapshot(
        project_id="proj-001",
        summary="Resume from the last safe checkpoint.",
        open_gaps=["No decision available"],
    )
    core = HarnessCore()

    selection = core.select_runtime(
        RuntimeRequest(
            brief=Brief(problem_statement="Build a CRM for small businesses"),
            brain_ids=("brain-01-product-strategy",),
            memory_snapshot=snapshot,
        )
    )

    assert selection.memory_snapshot == snapshot
    assert "memory_gap=No decision available" in selection.rationale
