"""Tests for deterministic multi-harness selection."""

from pathlib import Path

import pytest

from mastermind_cli.orchestrator.runtime_contracts import (
    FileSystemHarnessCatalog,
    MultiHarnessSelector,
    ObjectiveProfile,
)


def _write_package(path: Path, filename: str, name: str, description: str) -> None:
    """Write a minimal Agent Harness/Skill markdown package file."""
    path.mkdir(parents=True, exist_ok=True)
    (path / filename).write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n{description}\n",
        encoding="utf-8",
    )


def _write_catalog_fixture(root: Path) -> None:
    """Write a small multi-harness library fixture."""
    _write_package(
        root / "roles" / "product-strategist",
        "HARNESS.md",
        "Product Strategist",
        "Turn product goals into PRDs.",
    )
    (root / "roles" / "product-strategist" / ".leaf-detectors").write_text(
        "skill=SKILL.md\n",
        encoding="utf-8",
    )
    _write_package(
        root / "roles" / "backend-architect",
        "HARNESS.md",
        "Backend Architect",
        "Design backend architecture and contracts.",
    )
    _write_package(
        root / "verification" / "evidence-readiness",
        "HARNESS.md",
        "Evidence Readiness",
        "Check whether evidence is ready for generation.",
    )
    _write_package(
        root / "recovery" / "bounded-recovery",
        "HARNESS.md",
        "Bounded Recovery",
        "Choose retry, patch, replan, or escalation.",
    )
    _write_package(
        root / "shared-skills" / "memory-retrieval",
        "SKILL.md",
        "Memory Retrieval",
        "Retrieve relevant project memory.",
    )
    (root / "registry.yaml").write_text(
        "harnesses:\n"
        "  - id: product-strategist\n"
        "    path: roles/product-strategist\n"
        "    type: role\n"
        "    domains: [product, strategy]\n"
        "    phases: [discovery, planning]\n"
        "    outputs: [prd]\n"
        "    supported_loops: [goal-loop]\n"
        "    skills: [memory-retrieval]\n"
        "  - id: backend-architect\n"
        "    path: roles/backend-architect\n"
        "    type: role\n"
        "    domains: [backend, architecture]\n"
        "    phases: [design]\n"
        "    outputs: [architecture]\n"
        "    supported_loops: [reflection-loop]\n"
        "  - id: evidence-readiness\n"
        "    path: verification/evidence-readiness\n"
        "    type: verification\n"
        "    domains: [product, evidence]\n"
        "    phases: [discovery, verification]\n"
        "    outputs: [verdict]\n"
        "    supported_loops: [verification-loop]\n"
        "  - id: bounded-recovery\n"
        "    path: recovery/bounded-recovery\n"
        "    type: recovery\n"
        "    domains: [runtime]\n"
        "    phases: [recovery]\n"
        "    outputs: [recovery-plan]\n"
        "    supported_loops: [recovery-loop]\n"
        "skills:\n"
        "  - id: memory-retrieval\n"
        "    path: shared-skills/memory-retrieval\n"
        "    domains: [memory, product]\n"
        "    phases: [discovery]\n",
        encoding="utf-8",
    )


def test_selector_builds_plan_with_primary_supporting_and_skills(
    tmp_path: Path,
) -> None:
    """Product discovery objectives should compose the product role plus evidence."""
    _write_catalog_fixture(tmp_path)
    selector = MultiHarnessSelector(FileSystemHarnessCatalog(tmp_path))
    profile = ObjectiveProfile(
        objective_id="obj-001",
        objective_text="Create a PRD from existing evidence",
        domain="product",
        phase="discovery",
        output_type="prd",
        complexity="medium",
        risk_level="medium",
        verifiability="high",
        requires_write=True,
        requires_fresh_context=False,
        requires_memory=True,
        requires_mcp=False,
        requires_review=True,
        requires_recovery=False,
    )

    plan = selector.select(profile)

    assert plan.primary_harness.package_id == "product-strategist"
    assert [h.package_id for h in plan.supporting_harnesses] == ["evidence-readiness"]
    assert [skill.skill_id for skill in plan.selected_skills] == ["memory-retrieval"]
    assert plan.selected_loops == ("goal-loop", "verification-loop")
    assert plan.precedence_policy == (
        "project_policy",
        "primary_harness",
        "supporting_harnesses",
        "selected_skills",
        "selected_references",
    )
    assert "backend-architect" in plan.rejected_candidates


def test_selector_adds_recovery_harness_only_when_required(tmp_path: Path) -> None:
    """Recovery harnesses should be opt-in based on objective risk state."""
    _write_catalog_fixture(tmp_path)
    selector = MultiHarnessSelector(FileSystemHarnessCatalog(tmp_path))
    profile = ObjectiveProfile(
        objective_id="obj-002",
        objective_text="Recover a failed PRD generation run",
        domain="product",
        phase="discovery",
        output_type="prd",
        complexity="medium",
        risk_level="high",
        verifiability="high",
        requires_write=True,
        requires_fresh_context=False,
        requires_memory=True,
        requires_mcp=False,
        requires_review=True,
        requires_recovery=True,
    )

    plan = selector.select(profile)

    assert [h.package_id for h in plan.supporting_harnesses] == [
        "evidence-readiness",
        "bounded-recovery",
    ]
    assert plan.selected_loops == ("goal-loop", "verification-loop", "recovery-loop")


def test_selector_fails_when_no_primary_role_matches(tmp_path: Path) -> None:
    """Selector should fail loudly when no role harness can own the run."""
    _write_catalog_fixture(tmp_path)
    selector = MultiHarnessSelector(FileSystemHarnessCatalog(tmp_path))
    profile = ObjectiveProfile(
        objective_id="obj-003",
        objective_text="Create a finance risk model",
        domain="finance",
        phase="research",
        output_type="risk-model",
        complexity="complex",
        risk_level="high",
        verifiability="medium",
        requires_write=True,
        requires_fresh_context=True,
        requires_memory=False,
        requires_mcp=True,
        requires_review=True,
        requires_recovery=False,
    )

    with pytest.raises(ValueError, match="No primary harness"):
        selector.select(profile)
