"""Tests for project-specific adapter warnings."""

from __future__ import annotations

from pathlib import Path


from mastermind_cli.mm_flow.adapter_warnings import AdapterWarnings
from mastermind_cli.mm_flow.project_adapter import ProjectAdapter


def _write_planning_fixture(
    root: Path,
    *,
    project_name: str = "MasterMind Unified Harness + Memory",
    include_source_of_truth: bool = True,
    include_bridge_contract: bool = True,
) -> None:
    """Write the minimal aidlc-docs + .planning fixture used by the adapter."""
    (root / "aidlc-docs").mkdir(parents=True, exist_ok=True)
    (root / ".planning").mkdir(parents=True, exist_ok=True)
    lines = [
        "# AI-DLC State",
        "",
        "## Project Manifest",
        f"- project_name: {project_name}",
        "- canonical_scope: reusable harness core, memory core, and project adapters",
    ]
    if include_source_of_truth:
        lines.extend(
            [
                "- source_of_truth_ai_dlc: true",
                "- source_of_truth_planning: true",
            ]
        )
    else:
        lines.extend(
            [
                "- source_of_truth_ai_dlc: false",
                "- source_of_truth_planning: false",
            ]
        )
    lines.extend(
        [
            "- active_objective: harness-core-runtime-v1",
            "- active_uow: UOW-5",
            f"- project_root: {root}",
            "- operational_layer: .planning",
            "- design_layer: aidlc-docs",
            "- memory_layer: Engram persistent memory",
            "- harness_layer: apps/api/mastermind_cli and tools/mastermind-cli",
            "- adapter_name: mastermind-adapter",
        ]
    )
    if include_bridge_contract:
        lines.append(
            "- bridge_contract: aidlc-docs/inception/plans/planning-bridge-contract.md"
        )
    lines.append("")
    (root / "aidlc-docs" / "aidlc-state.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    (root / ".planning" / "HANDOFF-CURRENT.md").write_text(
        "\n".join(
            [
                "# Handoff",
                "",
                "## Next recommended objective",
                "- `harness-core-runtime-v1` — unified harness",
                "",
                "## Next command",
                "- Continue.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def test_collect_warnings_passes_on_healthy_repo(tmp_path: Path) -> None:
    """A fully populated repo should pass with only the optional info warnings."""
    _write_planning_fixture(tmp_path)
    adapter = ProjectAdapter.for_repo(tmp_path)

    warnings = adapter.collect_warnings()

    assert isinstance(warnings, AdapterWarnings)
    assert warnings.passed is True
    assert warnings.errors == ()
    codes = {item.code for item in warnings.items}
    assert "manifest_missing" not in codes
    assert "handoff_missing" not in codes


def test_collect_warnings_flags_missing_manifest(tmp_path: Path) -> None:
    """A repo without `aidlc-state.md` should report an error-severity warning."""
    (tmp_path / ".planning").mkdir(parents=True, exist_ok=True)
    adapter = ProjectAdapter.for_repo(tmp_path)

    warnings = adapter.collect_warnings()

    assert warnings.passed is False
    codes = {item.code for item in warnings.errors}
    assert "manifest_missing" in codes


def test_collect_warnings_flags_missing_handoff(tmp_path: Path) -> None:
    """A repo without `.planning/HANDOFF-CURRENT.md` should warn but still pass."""
    (tmp_path / "aidlc-docs").mkdir(parents=True, exist_ok=True)
    (tmp_path / "aidlc-docs" / "aidlc-state.md").write_text(
        "# AI-DLC State\n\n## Project Manifest\n- project_name: foo\n"
        "- canonical_scope: x\n- source_of_truth_ai_dlc: true\n"
        "- source_of_truth_planning: true\n- active_objective: a\n"
        "- active_uow: U1\n- project_root: /\n- operational_layer: .planning\n"
        "- design_layer: aidlc-docs\n- memory_layer: x\n- harness_layer: y\n",
        encoding="utf-8",
    )
    adapter = ProjectAdapter.for_repo(tmp_path)

    warnings = adapter.collect_warnings()

    codes = {item.code for item in warnings.warnings}
    assert "handoff_missing" in codes
    assert warnings.passed is True


def test_collect_warnings_flags_unclear_source_of_truth(tmp_path: Path) -> None:
    """Manifests missing source-of-truth flags should warn about ownership ambiguity."""
    _write_planning_fixture(tmp_path, include_source_of_truth=False)
    adapter = ProjectAdapter.for_repo(tmp_path)

    warnings = adapter.collect_warnings()

    codes = {item.code for item in warnings.warnings}
    assert "source_of_truth_split_unclear" in codes
