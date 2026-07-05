"""Tests for standard Agent Harness content loading."""

from pathlib import Path

import pytest

from mastermind_cli.orchestrator.runtime_contracts import AgentHarnessLoader


def _write_bundle(root: Path) -> Path:
    """Write a minimal Agent Harness bundle for loader tests."""
    bundle_path = root / "bundle"
    (bundle_path / "skills" / "memory-retrieval").mkdir(parents=True)
    (bundle_path / "references").mkdir()
    (bundle_path / "HARNESS.md").write_text("root harness\n", encoding="utf-8")
    (bundle_path / ".leaf-detectors").write_text("skill=SKILL.md\n", encoding="utf-8")
    (bundle_path / "skills" / "SKILLS.md").write_text(
        "skills routing\n", encoding="utf-8"
    )
    (bundle_path / "skills" / "memory-retrieval" / "SKILL.md").write_text(
        "skill leaf\n",
        encoding="utf-8",
    )
    (bundle_path / "references" / "REFERENCES.md").write_text(
        "references routing\n",
        encoding="utf-8",
    )
    return bundle_path


def test_loader_returns_root_harness_and_routing_files(tmp_path: Path) -> None:
    """Directories with standard routing files should load only their route map."""
    bundle_path = _write_bundle(tmp_path)
    loader = AgentHarnessLoader(bundle_path)

    assert loader.load_content(".") == "root harness\n"
    assert loader.load_content("skills") == "skills routing\n"
    assert loader.load_content("references") == "references routing\n"


def test_loader_returns_leaf_primary_file_from_detector(tmp_path: Path) -> None:
    """Leaf directories should resolve through `.leaf-detectors`."""
    bundle_path = _write_bundle(tmp_path)
    loader = AgentHarnessLoader(bundle_path)

    assert loader.load_content("skills/memory-retrieval") == "skill leaf\n"


def test_loader_blocks_paths_outside_bundle_root(tmp_path: Path) -> None:
    """Path traversal outside the harness root should be rejected."""
    bundle_path = _write_bundle(tmp_path)
    loader = AgentHarnessLoader(bundle_path)

    with pytest.raises(ValueError, match="outside harness root"):
        loader.load_content("../outside.md")
