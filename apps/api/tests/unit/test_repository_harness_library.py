"""Tests for the repository harness library fixture."""

from __future__ import annotations

from pathlib import Path

import yaml

from mastermind_cli.orchestrator.runtime_contracts import (
    BehavioralRoutingEvaluator,
    FileSystemHarnessCatalog,
    MultiHarnessPipeline,
    ObjectiveProfile,
    RunBundleComposer,
)


REPO_ROOT = Path(__file__).resolve().parents[4]
LIBRARY_ROOT = REPO_ROOT / ".mm-flow" / "harness-library"


def _word_count(path: Path) -> int:
    """Return a simple word count for context-budget guardrails."""
    return len(path.read_text(encoding="utf-8").split())


def _frontmatter(path: Path) -> dict[str, object]:
    """Read required YAML frontmatter from a harness library markdown file."""
    content = path.read_text(encoding="utf-8")
    assert content.startswith("---\n"), f"{path} missing YAML frontmatter"
    _, raw_metadata, _ = content.split("---\n", 2)
    metadata = yaml.safe_load(raw_metadata)
    assert isinstance(metadata, dict), f"{path} frontmatter must be a mapping"
    return metadata


def test_repository_harness_library_routing_cases_pass() -> None:
    """Repository harness library should satisfy its behavioral routing cases."""
    report = BehavioralRoutingEvaluator(
        FileSystemHarnessCatalog(LIBRARY_ROOT)
    ).evaluate_file(LIBRARY_ROOT / "routing-cases.yaml")

    failures = {
        result.case_id: result.errors
        for result in report.case_results
        if not result.passed
    }
    assert failures == {}


def test_repository_harness_library_builds_valid_run_bundle(tmp_path: Path) -> None:
    """Repository harness library should compose a valid Agent Harness RunBundle."""
    pipeline = MultiHarnessPipeline(
        catalog=FileSystemHarnessCatalog(LIBRARY_ROOT),
        composer=RunBundleComposer(
            output_root=tmp_path / "run-bundles",
            library_root=LIBRARY_ROOT,
        ),
    )

    result = pipeline.build(
        ObjectiveProfile(
            objective_id="repo-real-implementation-review",
            objective_text="Implement and verify a risky code change.",
            domain="software",
            phase="implementation",
            output_type="artifact",
            complexity="medium",
            risk_level="medium",
            verifiability="high",
            requires_write=True,
            requires_fresh_context=False,
            requires_memory=False,
            requires_mcp=False,
            requires_review=True,
            requires_recovery=False,
        )
    )

    assert result.bundle.validation_status == "passed"
    assert result.bundle.validation_errors == ()
    assert result.bundle.primary_harness_id == "implementation-lead"
    assert result.bundle.supporting_harness_ids == ("acceptance-verifier",)
    assert result.bundle.selected_skill_ids == (
        "codebase-scan",
        "safe-edit",
        "acceptance-check",
        "evidence-readiness",
    )
    assert Path(result.bundle.harness_file).is_file()


def test_repository_harness_library_respects_context_budget_guardrails() -> None:
    """Harness library markdown should stay compact and route by frontmatter."""
    markdown_files = tuple(
        path
        for path in LIBRARY_ROOT.rglob("*.md")
        if path.name in {"HARNESS.md", "SKILL.md"} or path.name.isupper()
    )

    assert markdown_files
    for path in markdown_files:
        metadata = _frontmatter(path)
        assert metadata.get("description"), f"{path} missing description"
        limit = 120 if path.name in {"HARNESS.md", "SKILL.md"} else 80
        assert _word_count(path) <= limit, f"{path} exceeds {limit} words"


def test_repository_harness_library_registry_references_exist() -> None:
    """Registry references should point to existing files for bundle lineage."""
    registry = yaml.safe_load(
        (LIBRARY_ROOT / "registry.yaml").read_text(encoding="utf-8")
    )
    assert isinstance(registry, dict)
    harnesses = registry.get("harnesses", [])
    assert isinstance(harnesses, list)

    for harness in harnesses:
        assert isinstance(harness, dict)
        for reference in harness.get("references", []):
            reference_path = LIBRARY_ROOT / reference
            assert reference_path.is_file(), f"missing reference {reference}"
