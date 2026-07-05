"""Tests for the end-to-end multi-harness bundle pipeline."""

from pathlib import Path

from mastermind_cli.orchestrator.runtime_contracts import (
    FileSystemHarnessCatalog,
    MultiHarnessPipeline,
    ObjectiveProfile,
    RunBundleComposer,
)


def _write_package(path: Path, filename: str, name: str, description: str) -> None:
    """Write a minimal markdown package file with YAML frontmatter."""
    path.mkdir(parents=True, exist_ok=True)
    (path / filename).write_text(
        "---\n"
        f"name: {name}\n"
        f"description: {description}\n"
        "---\n"
        f"{description}\n",
        encoding="utf-8",
    )


def _write_library(root: Path) -> None:
    """Write a small harness library used by the pipeline test."""
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
        root / "verification" / "evidence-readiness",
        "HARNESS.md",
        "Evidence Readiness",
        "Check whether evidence is ready for generation.",
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
        "  - id: evidence-readiness\n"
        "    path: verification/evidence-readiness\n"
        "    type: verification\n"
        "    domains: [product, evidence]\n"
        "    phases: [discovery, verification]\n"
        "    outputs: [verdict]\n"
        "    supported_loops: [verification-loop]\n"
        "skills:\n"
        "  - id: memory-retrieval\n"
        "    path: shared-skills/memory-retrieval\n"
        "    domains: [memory, product]\n"
        "    phases: [discovery]\n",
        encoding="utf-8",
    )


def test_pipeline_selects_composes_and_validates_bundle(tmp_path: Path) -> None:
    """Pipeline should return both the composition plan and a validated bundle."""
    library_root = tmp_path / "harness-library"
    _write_library(library_root)
    pipeline = MultiHarnessPipeline(
        catalog=FileSystemHarnessCatalog(library_root),
        composer=RunBundleComposer(
            output_root=tmp_path / ".run-bundles",
            library_root=library_root,
        ),
    )
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

    result = pipeline.build(profile)

    assert result.plan.primary_harness.package_id == "product-strategist"
    assert result.plan.supporting_harnesses[0].package_id == "evidence-readiness"
    assert result.bundle.validation_status == "passed"
    assert result.bundle.validation_errors == ()
    assert Path(result.bundle.path, "HARNESS.md").is_file()
