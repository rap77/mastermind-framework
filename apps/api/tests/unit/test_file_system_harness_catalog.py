"""Tests for filesystem-backed harness library discovery."""

from pathlib import Path

import pytest

from mastermind_cli.orchestrator.runtime_contracts import FileSystemHarnessCatalog


def test_catalog_loads_harness_and_shared_skill_from_registry(tmp_path: Path) -> None:
    """Catalog should read registry entries and validate standard files exist."""
    root = tmp_path / "harness-library"
    harness_dir = root / "roles" / "product-strategist"
    skill_dir = root / "shared-skills" / "memory-retrieval"
    harness_dir.mkdir(parents=True)
    skill_dir.mkdir(parents=True)
    (harness_dir / "HARNESS.md").write_text(
        "---\n"
        "name: Product Strategist\n"
        "description: Turn product goals into PRDs.\n"
        "---\n"
        "Use this harness for product strategy.\n",
        encoding="utf-8",
    )
    (harness_dir / ".leaf-detectors").write_text("skill=SKILL.md\n", encoding="utf-8")
    (skill_dir / "SKILL.md").write_text(
        "---\n"
        "name: Memory Retrieval\n"
        "description: Retrieve relevant project memory.\n"
        "---\n"
        "Use this skill to retrieve memory.\n",
        encoding="utf-8",
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
        "skills:\n"
        "  - id: memory-retrieval\n"
        "    path: shared-skills/memory-retrieval\n"
        "    domains: [memory]\n"
        "    phases: [discovery]\n",
        encoding="utf-8",
    )

    catalog = FileSystemHarnessCatalog(root)

    harnesses = catalog.list_harnesses()
    skills = catalog.list_skills()

    assert harnesses[0].package_id == "product-strategist"
    assert harnesses[0].name == "Product Strategist"
    assert harnesses[0].description == "Turn product goals into PRDs."
    assert harnesses[0].skills == ("memory-retrieval",)
    assert skills[0].skill_id == "memory-retrieval"
    assert skills[0].description == "Retrieve relevant project memory."


def test_catalog_fails_when_harness_file_is_missing(tmp_path: Path) -> None:
    """Invalid harness packages should fail loudly instead of silently loading."""
    root = tmp_path / "harness-library"
    (root / "roles" / "product-strategist").mkdir(parents=True)
    (root / "registry.yaml").write_text(
        "harnesses:\n"
        "  - id: product-strategist\n"
        "    path: roles/product-strategist\n"
        "    type: role\n"
        "    domains: [product]\n"
        "    phases: [discovery]\n"
        "    outputs: [prd]\n"
        "    supported_loops: [goal-loop]\n",
        encoding="utf-8",
    )

    catalog = FileSystemHarnessCatalog(root)

    with pytest.raises(ValueError, match="HARNESS.md"):
        catalog.list_harnesses()


def test_catalog_fails_when_leaf_detector_is_missing_for_harness_with_skills(
    tmp_path: Path,
) -> None:
    """Harnesses that declare skills should include .leaf-detectors."""
    root = tmp_path / "harness-library"
    harness_dir = root / "roles" / "product-strategist"
    harness_dir.mkdir(parents=True)
    (harness_dir / "HARNESS.md").write_text(
        "---\n"
        "name: Product Strategist\n"
        "description: Turn product goals into PRDs.\n"
        "---\n"
        "Use this harness for product strategy.\n",
        encoding="utf-8",
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
        "    skills: [memory-retrieval]\n",
        encoding="utf-8",
    )

    catalog = FileSystemHarnessCatalog(root)

    with pytest.raises(ValueError, match=".leaf-detectors"):
        catalog.list_harnesses()
