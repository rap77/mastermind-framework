"""Tests for materializing Agent Harness run bundles."""

from pathlib import Path

import yaml

from mastermind_cli.orchestrator.runtime_contracts import (
    HarnessCompositionPlan,
    HarnessPackage,
    ObjectiveProfile,
    RunBundleComposer,
    SkillPackage,
)


def _build_plan() -> HarnessCompositionPlan:
    """Build a minimal composition plan for bundle tests."""
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
    primary = HarnessPackage(
        package_id="product-strategist",
        name="Product Strategist",
        package_type="role",
        path="roles/product-strategist",
        description="Turn product goals into PRDs.",
        domains=("product",),
        phases=("discovery",),
        outputs=("prd",),
        supported_loops=("goal-loop",),
        skills=("memory-retrieval",),
        references=("roles/product-strategist/references/strategy.md",),
    )
    supporting = HarnessPackage(
        package_id="evidence-readiness",
        name="Evidence Readiness",
        package_type="verification",
        path="verification/evidence-readiness",
        description="Check evidence readiness before generation.",
        domains=("product", "evidence"),
        phases=("discovery",),
        outputs=("verdict",),
        supported_loops=("verification-loop",),
    )
    skill = SkillPackage(
        skill_id="memory-retrieval",
        name="Memory Retrieval",
        path="shared-skills/memory-retrieval",
        description="Retrieve relevant project memory.",
        domains=("memory", "product"),
        phases=("discovery",),
    )
    return HarnessCompositionPlan(
        plan_id="plan-obj-001",
        objective_profile=profile,
        primary_harness=primary,
        supporting_harnesses=(supporting,),
        selected_skills=(skill,),
        selected_references=("roles/product-strategist/references/strategy.md",),
        selected_loops=("goal-loop", "verification-loop"),
        precedence_policy=(
            "project_policy",
            "primary_harness",
            "supporting_harnesses",
            "selected_skills",
            "selected_references",
        ),
        context_budget=4_000,
        validation_requirements=("structural", "behavioral"),
        rejected_candidates=("backend-architect",),
        rationale=("domain=product",),
    )


def test_composer_writes_agent_harness_bundle_files(tmp_path: Path) -> None:
    """Composer should create a valid bundle skeleton with lineage metadata."""
    plan = _build_plan()
    library_root = tmp_path / "harness-library"
    skill_dir = library_root / "shared-skills" / "memory-retrieval"
    skill_dir.mkdir(parents=True)
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: Memory Retrieval\n"
        "description: Retrieve relevant project memory.\n"
        "---\n"
        "Use this skill to retrieve memory.\n",
        encoding="utf-8",
    )
    composer = RunBundleComposer(
        output_root=tmp_path / ".run-bundles",
        library_root=library_root,
    )

    bundle = composer.compose(plan)

    bundle_path = Path(bundle.path)
    assert bundle.validation_status == "pending"
    assert (bundle_path / "HARNESS.md").is_file()
    assert (bundle_path / ".leaf-detectors").read_text(encoding="utf-8") == (
        "skill=SKILL.md\n"
    )
    assert (bundle_path / "skills" / "SKILLS.md").is_file()
    assert (bundle_path / "skills" / "memory-retrieval" / "SKILL.md").is_file()
    assert (bundle_path / "references" / "REFERENCES.md").is_file()

    manifest = yaml.safe_load((bundle_path / "bundle.yaml").read_text(encoding="utf-8"))
    assert manifest["bundle_id"] == "plan-obj-001"
    assert manifest["objective_id"] == "obj-001"
    assert manifest["primary_harness"] == "product-strategist"
    assert manifest["supporting_harnesses"] == ["evidence-readiness"]
    assert manifest["selected_skills"] == ["memory-retrieval"]
    assert manifest["precedence"] == list(plan.precedence_policy)


def test_composer_harness_file_documents_precedence_and_selected_harnesses(
    tmp_path: Path,
) -> None:
    """Generated HARNESS.md should explain the primary/supporting split."""
    plan = _build_plan()
    composer = RunBundleComposer(output_root=tmp_path / ".run-bundles")

    bundle = composer.compose(plan)

    harness_text = Path(bundle.harness_file).read_text(encoding="utf-8")
    assert "name: Product Strategist RunBundle" in harness_text
    assert "Primary harness: `product-strategist`" in harness_text
    assert "Supporting harnesses:" in harness_text
    assert "`evidence-readiness`" in harness_text
    assert "project_policy" in harness_text
    assert "selected_references" in harness_text
