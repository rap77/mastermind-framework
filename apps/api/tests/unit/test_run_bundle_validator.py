"""Tests for structural validation of composed run bundles."""

from pathlib import Path

from mastermind_cli.orchestrator.runtime_contracts import RunBundle, RunBundleValidator


def _write_valid_bundle(root: Path) -> RunBundle:
    """Write a minimal structurally valid run bundle."""
    bundle_path = root / "plan-obj-001"
    (bundle_path / "skills" / "memory-retrieval").mkdir(parents=True)
    (bundle_path / "references").mkdir()
    (bundle_path / "HARNESS.md").write_text(
        "---\n"
        "name: Product Strategist RunBundle\n"
        "description: Test run bundle.\n"
        "---\n"
        "Primary harness: `product-strategist`\n",
        encoding="utf-8",
    )
    (bundle_path / ".leaf-detectors").write_text("skill=SKILL.md\n", encoding="utf-8")
    (bundle_path / "skills" / "SKILLS.md").write_text(
        "---\ndescription: Selected skills.\n---\n",
        encoding="utf-8",
    )
    (bundle_path / "skills" / "memory-retrieval" / "SKILL.md").write_text(
        "---\nname: Memory Retrieval\ndescription: Retrieve memory.\n---\n",
        encoding="utf-8",
    )
    (bundle_path / "references" / "REFERENCES.md").write_text(
        "---\ndescription: Selected references.\n---\n",
        encoding="utf-8",
    )
    (bundle_path / "bundle.yaml").write_text(
        "bundle_id: plan-obj-001\n"
        "objective_id: obj-001\n"
        "plan_id: plan-obj-001\n"
        "primary_harness: product-strategist\n"
        "supporting_harnesses: [evidence-readiness]\n"
        "selected_skills: [memory-retrieval]\n"
        "precedence: [project_policy, primary_harness, supporting_harnesses, selected_skills, selected_references]\n",
        encoding="utf-8",
    )
    return RunBundle(
        bundle_id="plan-obj-001",
        objective_id="obj-001",
        plan_id="plan-obj-001",
        path=str(bundle_path),
        harness_file=str(bundle_path / "HARNESS.md"),
        bundle_manifest=str(bundle_path / "bundle.yaml"),
        primary_harness_id="product-strategist",
        supporting_harness_ids=("evidence-readiness",),
        selected_skill_ids=("memory-retrieval",),
        validation_status="pending",
    )


def test_validator_marks_structurally_valid_bundle_as_passed(tmp_path: Path) -> None:
    """Valid bundles should be marked passed without errors."""
    bundle = _write_valid_bundle(tmp_path)

    validated = RunBundleValidator().validate(bundle)

    assert validated.validation_status == "passed"
    assert validated.validation_errors == ()


def test_validator_reports_missing_required_files(tmp_path: Path) -> None:
    """Missing required Agent Harness files should fail validation."""
    bundle = _write_valid_bundle(tmp_path)
    Path(bundle.harness_file).unlink()
    Path(bundle.path, ".leaf-detectors").unlink()

    validated = RunBundleValidator().validate(bundle)

    assert validated.validation_status == "failed"
    assert "missing HARNESS.md" in validated.validation_errors
    assert "missing .leaf-detectors" in validated.validation_errors


def test_validator_reports_manifest_mismatch_and_missing_skill_leaf(
    tmp_path: Path,
) -> None:
    """Manifest mismatches and missing selected skill leaves should fail validation."""
    bundle = _write_valid_bundle(tmp_path)
    Path(bundle.path, "bundle.yaml").write_text(
        "bundle_id: wrong\n"
        "objective_id: obj-001\n"
        "plan_id: plan-obj-001\n"
        "primary_harness: other\n"
        "selected_skills: [memory-retrieval]\n",
        encoding="utf-8",
    )
    Path(bundle.path, "skills", "memory-retrieval", "SKILL.md").unlink()

    validated = RunBundleValidator().validate(bundle)

    assert validated.validation_status == "failed"
    assert "bundle.yaml bundle_id mismatch" in validated.validation_errors
    assert "bundle.yaml primary_harness mismatch" in validated.validation_errors
    assert (
        "missing selected skill leaf: memory-retrieval/SKILL.md"
        in validated.validation_errors
    )
