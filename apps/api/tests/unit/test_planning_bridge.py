"""Tests for the planning bridge and repo adapter."""

from __future__ import annotations

from pathlib import Path

import pytest
from pytest import MonkeyPatch

from mastermind_cli.mm_flow.exceptions import PlanningManifestError
from mastermind_cli.mm_flow.planning_bridge import PlanningBridge, StructuredStatus
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter


def _write_planning_fixture(root: Path) -> None:
    (root / "aidlc-docs").mkdir(parents=True, exist_ok=True)
    (root / ".planning").mkdir(parents=True, exist_ok=True)
    (root / "aidlc-docs" / "aidlc-state.md").write_text(
        "\n".join(
            [
                "# AI-DLC State — Multi-Harness Architecture",
                "",
                "## Project Manifest",
                "- project_name: MasterMind Unified Harness + Memory",
                "- canonical_scope: reusable harness core, memory core, and project adapters",
                "- source_of_truth_ai_dlc: true",
                "- source_of_truth_planning: true",
                "- active_objective: manifest-contract-bridge-v1",
                "- active_uow: UOW-4",
                f"- project_root: {root}",
                "- operational_layer: .planning",
                "- design_layer: aidlc-docs",
                "- memory_layer: Engram persistent memory",
                "- harness_layer: apps/api/mastermind_cli and tools/mastermind-cli",
                "- adapter_name: mastermind-adapter",
                "- bridge_contract: aidlc-docs/inception/plans/planning-bridge-contract.md",
                "",
            ]
        ),
        encoding="utf-8",
    )
    (root / ".planning" / "HANDOFF-CURRENT.md").write_text(
        "\n".join(
            [
                "# Handoff — unified harness + memory kickoff",
                "",
                "## Last archived",
                "- `window-scheduler` — archived at 2026-06-21T19:23:46",
                "",
                "## Next recommended objective",
                "- `harness-memory-unification` — unified harness + memory platform",
                "- Build a reusable harness core plus memory layer, then bridge `.planning` into it through adapters.",
                "",
                "## Next command",
                "- Review `aidlc-docs/inception/plans/harness-memory-roadmap.md` and define the project manifest.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_planning_bridge_builds_normalized_harness_request(tmp_path: Path) -> None:
    """The bridge should normalize manifest + handoff into a harness request."""
    _write_planning_fixture(tmp_path)

    bridge = PlanningBridge(project_root=tmp_path)
    request = bridge.build_request()

    assert request.project_name == "MasterMind Unified Harness + Memory"
    assert request.design_objective == "manifest-contract-bridge-v1"
    assert request.operational_objective == "harness-memory-unification"
    assert request.active_uow == "UOW-4"
    assert (
        "next_command=Review `aidlc-docs/inception/plans/harness-memory-roadmap.md` and define the project manifest."
        in request.constraints
    )
    assert request.warnings == ("planning_objective_differs_from_design_objective",)


def test_planning_bridge_writes_structured_status(tmp_path: Path) -> None:
    """Structured bridge status should be written into the handoff file."""
    _write_planning_fixture(tmp_path)

    bridge = PlanningBridge(project_root=tmp_path)
    record = bridge.write_structured_status(
        StructuredStatus(
            status="in_progress",
            summary="Slice 3 bridge and adapter are being implemented.",
            next_action="continue_slice_3",
            verification_outcome="pending",
            recovery_notes=("bridge_wiring_in_progress",),
        ),
        objective="harness-memory-unification",
        uow="UOW-4",
    )

    content = (tmp_path / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )
    assert "## Bridge Status" in content
    assert "- objective: harness-memory-unification" in content
    assert "- uow: UOW-4" in content
    assert "- status: in_progress" in content
    assert "- next_action: continue_slice_3" in content
    assert "- verification_outcome: pending" in content
    assert record.objective == "harness-memory-unification"


def test_planning_bridge_raises_domain_error_for_missing_fields(tmp_path: Path) -> None:
    """Malformed manifests should fail with a planning-specific error."""
    (tmp_path / "aidlc-docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "aidlc-docs" / "aidlc-state.md").write_text(
        "\n".join(
            [
                "# AI-DLC State",
                "",
                "## Project Manifest",
                "- project_name: MasterMind",
                "- canonical_scope: reusable harness core",
                "",
            ]
        ),
        encoding="utf-8",
    )

    bridge = PlanningBridge(project_root=tmp_path)

    with pytest.raises(PlanningManifestError, match="Missing manifest fields"):
        bridge.load_manifest()


def test_project_adapter_exposes_repo_paths(tmp_path: Path) -> None:
    """The repo adapter should surface canonical paths and bridge behavior."""
    _write_planning_fixture(tmp_path)

    adapter = ProjectAdapter.for_repo(tmp_path)

    assert adapter.project_root == tmp_path
    assert adapter.manifest_path == tmp_path / "aidlc-docs" / "aidlc-state.md"
    assert adapter.handoff_path == tmp_path / ".planning" / "HANDOFF-CURRENT.md"
    assert adapter.state_path == tmp_path / ".planning" / "STATE.md"
    assert adapter.project_id == "mastermind-unified-harness-memory"


def test_project_adapter_project_id_prefers_explicit_env(
    tmp_path: Path, monkeypatch: MonkeyPatch
) -> None:
    """An explicit project-memory ID should override the manifest-derived slug."""
    _write_planning_fixture(tmp_path)
    monkeypatch.setenv("MM_MEMORY_PROJECT_ID", "proj-001")

    adapter = ProjectAdapter.for_repo(tmp_path)

    assert adapter.project_id == "proj-001"


def test_project_adapter_archives_completed_status(tmp_path: Path) -> None:
    """Completed status writes should replace the bridge block with an archive."""
    _write_planning_fixture(tmp_path)

    adapter = ProjectAdapter.for_repo(tmp_path)
    archive = adapter.write_structured_status(
        status="completed",
        summary="Slice 3 bridge landed.",
        next_action="activate_next_objective",
        verification_outcome="passed",
        objective="harness-memory-unification",
        uow="UOW-4",
        warnings=("traceable_archive",),
    )

    content = (tmp_path / ".planning" / "HANDOFF-CURRENT.md").read_text(
        encoding="utf-8"
    )
    assert "## Bridge Archive" in content
    assert "- objective: harness-memory-unification" in content
    assert "- archived_at:" in content
    assert archive is not None
    assert archive.objective == "harness-memory-unification"
