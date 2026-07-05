"""Tests for multi-harness composition data contracts."""

from mastermind_cli.orchestrator.runtime_contracts import (
    HarnessCompositionPlan,
    HarnessPackage,
    ObjectiveProfile,
    RunBundle,
    SkillPackage,
)


def test_objective_profile_captures_selection_signals() -> None:
    """Objective profiles should preserve the signals used by the selector."""
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
        evidence_readiness_gate="ready",
        evidence_readiness_score=82.0,
    )

    assert profile.domain == "product"
    assert profile.requires_memory is True
    assert profile.evidence_readiness_score == 82.0


def test_harness_composition_plan_keeps_primary_harness_and_supporting_context() -> (
    None
):
    """Composition plans should separate the primary role from supporting harnesses."""
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
        path=".mm-flow/harness-library/roles/product-strategist",
        description="Turn product goals and evidence into strategy artifacts.",
        domains=("product", "strategy"),
        phases=("discovery", "planning"),
        outputs=("prd",),
        supported_loops=("goal-loop",),
    )
    evidence = HarnessPackage(
        package_id="evidence-readiness",
        name="Evidence Readiness",
        package_type="verification",
        path=".mm-flow/harness-library/verification/evidence-readiness",
        description="Check whether evidence is sufficient before generation.",
        domains=("evidence",),
        phases=("discovery", "verification"),
        outputs=("verdict",),
        supported_loops=("verification-loop",),
    )
    skill = SkillPackage(
        skill_id="memory-retrieval",
        name="Memory Retrieval",
        path=".mm-flow/harness-library/shared-skills/memory-retrieval",
        description="Retrieve relevant project memory for the objective.",
        domains=("memory",),
        phases=("discovery",),
    )

    plan = HarnessCompositionPlan(
        plan_id="run-product-discovery-001",
        objective_profile=profile,
        primary_harness=primary,
        supporting_harnesses=(evidence,),
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
        rationale=("domain=product", "requires_review=True"),
    )

    assert plan.primary_harness.package_id == "product-strategist"
    assert plan.supporting_harnesses[0].package_id == "evidence-readiness"
    assert plan.selected_skills[0].skill_id == "memory-retrieval"
    assert plan.precedence_policy[0] == "project_policy"


def test_run_bundle_preserves_lineage_to_composition_plan() -> None:
    """Run bundles should point back to the plan and materialized bundle path."""
    bundle = RunBundle(
        bundle_id="run-product-discovery-001",
        objective_id="obj-001",
        plan_id="run-product-discovery-001",
        path=".run-bundles/run-product-discovery-001",
        harness_file=".run-bundles/run-product-discovery-001/HARNESS.md",
        bundle_manifest=".run-bundles/run-product-discovery-001/bundle.yaml",
        primary_harness_id="product-strategist",
        supporting_harness_ids=("evidence-readiness",),
        selected_skill_ids=("memory-retrieval",),
        validation_status="pending",
    )

    assert bundle.plan_id == "run-product-discovery-001"
    assert bundle.primary_harness_id == "product-strategist"
    assert bundle.validation_status == "pending"
