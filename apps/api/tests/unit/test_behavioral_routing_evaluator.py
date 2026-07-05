"""Tests for versioned multi-harness behavioral routing cases."""

from pathlib import Path

from mastermind_cli.orchestrator.runtime_contracts import (
    BehavioralRoutingEvaluator,
    FileSystemHarnessCatalog,
)


def _write_package(path: Path, filename: str, name: str, description: str) -> None:
    """Write a markdown package file with frontmatter."""
    path.mkdir(parents=True, exist_ok=True)
    (path / filename).write_text(
        "---\n" f"name: {name}\n" f"description: {description}\n" "---\n",
        encoding="utf-8",
    )


def _write_library(root: Path) -> None:
    """Write a minimal harness library for routing tests."""
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
        "Check evidence before generation.",
    )
    _write_package(
        root / "shared-skills" / "memory-retrieval",
        "SKILL.md",
        "Memory Retrieval",
        "Retrieve project memory.",
    )
    (root / "registry.yaml").write_text(
        "harnesses:\n"
        "  - id: product-strategist\n"
        "    path: roles/product-strategist\n"
        "    type: role\n"
        "    domains: [product]\n"
        "    phases: [discovery]\n"
        "    outputs: [prd]\n"
        "    supported_loops: [goal-loop]\n"
        "    skills: [memory-retrieval]\n"
        "  - id: evidence-readiness\n"
        "    path: verification/evidence-readiness\n"
        "    type: verification\n"
        "    domains: [product]\n"
        "    phases: [discovery]\n"
        "    outputs: [verdict]\n"
        "    supported_loops: [verification-loop]\n"
        "skills:\n"
        "  - id: memory-retrieval\n"
        "    path: shared-skills/memory-retrieval\n"
        "    domains: [product]\n"
        "    phases: [discovery]\n",
        encoding="utf-8",
    )


def test_behavioral_routing_evaluator_passes_expected_case(tmp_path: Path) -> None:
    """Evaluator should pass when selector output matches the case contract."""
    library_root = tmp_path / "harness-library"
    _write_library(library_root)
    cases_path = tmp_path / "routing-cases.yaml"
    cases_path.write_text(
        "schema_version: '1'\n"
        "routing_cases:\n"
        "  - case_id: product-prd-from-evidence\n"
        "    prompt: Create a PRD using existing evidence\n"
        "    objective_profile:\n"
        "      objective_id: obj-001\n"
        "      domain: product\n"
        "      phase: discovery\n"
        "      output_type: prd\n"
        "      complexity: medium\n"
        "      risk_level: medium\n"
        "      verifiability: high\n"
        "      requires_write: true\n"
        "      requires_fresh_context: false\n"
        "      requires_memory: true\n"
        "      requires_mcp: false\n"
        "      requires_review: true\n"
        "      requires_recovery: false\n"
        "    expected_primary_harness: product-strategist\n"
        "    expected_supporting_harnesses: [evidence-readiness]\n"
        "    expected_skills: [memory-retrieval]\n"
        "    forbidden_skills: [code-edit]\n"
        "    max_context_budget: 4000\n",
        encoding="utf-8",
    )

    report = BehavioralRoutingEvaluator(
        FileSystemHarnessCatalog(library_root)
    ).evaluate_file(cases_path)

    assert report.passed is True
    assert report.schema_version == "1"
    assert report.case_results[0].case_id == "product-prd-from-evidence"
    assert report.case_results[0].passed is True


def test_behavioral_routing_evaluator_reports_mismatch(tmp_path: Path) -> None:
    """Evaluator should produce actionable errors for failed routing cases."""
    library_root = tmp_path / "harness-library"
    _write_library(library_root)
    cases_path = tmp_path / "routing-cases.yaml"
    cases_path.write_text(
        "schema_version: '1'\n"
        "routing_cases:\n"
        "  - case_id: wrong-primary\n"
        "    prompt: Create a PRD using existing evidence\n"
        "    objective_profile:\n"
        "      objective_id: obj-001\n"
        "      domain: product\n"
        "      phase: discovery\n"
        "      output_type: prd\n"
        "      complexity: medium\n"
        "      risk_level: medium\n"
        "      verifiability: high\n"
        "      requires_write: true\n"
        "      requires_fresh_context: false\n"
        "      requires_memory: true\n"
        "      requires_mcp: false\n"
        "      requires_review: true\n"
        "      requires_recovery: false\n"
        "    expected_primary_harness: backend-architect\n"
        "    expected_supporting_harnesses: [evidence-readiness]\n"
        "    expected_skills: [memory-retrieval]\n"
        "    forbidden_skills: []\n"
        "    max_context_budget: 100\n",
        encoding="utf-8",
    )

    report = BehavioralRoutingEvaluator(
        FileSystemHarnessCatalog(library_root)
    ).evaluate_file(cases_path)

    assert report.passed is False
    assert report.case_results[0].passed is False
    assert "primary expected backend-architect got product-strategist" in (
        report.case_results[0].errors
    )
    assert "context_budget 4000 exceeds max 100" in report.case_results[0].errors
