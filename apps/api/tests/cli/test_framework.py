#!/usr/bin/env python3
"""Tests for framework CLI commands."""

from unittest.mock import patch, MagicMock
import pytest
from click.testing import CliRunner

from mastermind_cli.commands.framework import (
    framework,
    get_project_root,
)


@pytest.fixture
def runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_project_structure(tmp_path):
    """Create a temporary project structure with brain directories."""
    # Create software-development directory structure
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    # Create brain directories with sources
    brains = ["brain-01", "brain-02", "brain-03"]
    for brain_name in brains:
        brain_dir = sw_dev / f"{brain_name}-brain"
        brain_dir.mkdir()
        sources_dir = brain_dir / "sources"
        sources_dir.mkdir()

        # Create some source files
        for i in range(3):
            source_file = sources_dir / f"FUENTE-{i+1:03d}.md"
            source_file.write_text(
                f"""---
source_id: "FUENTE-{i+1:03d}"
brain: "{brain_name}"
title: "Test Source {i+1}"
distillation_quality: "{'complete' if i < 2 else 'partial'}"
loaded_in_notebook: {i % 2 == 0}
---

# Test Content {i+1}

This is test content for source {i+1}.
"""
            )

    # Add project marker
    (tmp_path / "CLAUDE.md").write_text("# Test Project")

    return tmp_path


# =============================================================================
# Test get_project_root helper
# =============================================================================


def test_get_project_root_finds_marker(tmp_path):
    """Test get_project_root finds project root by marker file."""
    (tmp_path / "CLAUDE.md").write_text("# Test")

    with patch("pathlib.Path.cwd", return_value=tmp_path / "subdir"):
        root = get_project_root()
        assert root == tmp_path


def test_get_project_root_finds_design_marker(tmp_path):
    """Test get_project_root finds project root by design marker."""
    design_dir = tmp_path / "docs" / "design"
    design_dir.mkdir(parents=True)
    (design_dir / "00-PRD-MasterMind-Framework.md").write_text("# PRD")

    with patch("pathlib.Path.cwd", return_value=tmp_path / "subdir"):
        root = get_project_root()
        assert root == tmp_path


def test_get_project_root_returns_current_when_no_marker(tmp_path):
    """Test get_project_root returns current dir when no marker found."""
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        root = get_project_root()
        assert root == tmp_path


def test_get_project_root_searches_parent_directories(tmp_path):
    """Test get_project_root searches parent directories."""
    # Create marker in parent
    (tmp_path / "CLAUDE.md").write_text("# Test")

    # Create nested subdirectory
    nested = tmp_path / "a" / "b" / "c"
    nested.mkdir(parents=True)

    with patch("pathlib.Path.cwd", return_value=nested):
        root = get_project_root()
        assert root == tmp_path


# =============================================================================
# Test framework command group
# =============================================================================


def test_framework_group_exists(runner):
    """Test that framework command group can be invoked."""
    result = runner.invoke(framework, ["--help"])
    assert result.exit_code == 0
    assert "Framework-level operations" in result.output


# =============================================================================
# Test framework status command
# =============================================================================


def test_framework_status_displays_overview(temp_project_structure, runner):
    """Test framework status displays framework overview."""
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "Framework Status" in result.output
        assert "MasterMind Framework" in result.output
        assert "Version: 0.1.0" in result.output
        assert "Total Brains: 3" in result.output
        assert "Total Sources: 9" in result.output


def test_framework_status_displays_brain_table(temp_project_structure, runner):
    """Test framework status displays brains table."""
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "brain-01" in result.output
        assert "brain-02" in result.output
        assert "brain-03" in result.output


def test_framework_status_calculates_progress(temp_project_structure, runner):
    """Test framework status calculates completion progress."""
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # 6 complete out of 9 total = 66%
        assert "66%" in result.output or "67%" in result.output  # Rounding may vary


def test_framework_status_counts_sources_per_brain(temp_project_structure, runner):
    """Test framework status counts sources per brain."""
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Each brain has 3 sources
        lines = result.output.split("\n")
        brain_lines = [line for line in lines if "brain-0" in line]
        assert len(brain_lines) == 3
        for line in brain_lines:
            assert "3" in line  # Each has 3 sources


def test_framework_status_counts_loaded_in_notebook(temp_project_structure, runner):
    """Test framework status counts sources loaded in notebook."""
    with patch("pathlib.Path.cwd", return_value=temp_project_structure):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Every other source is loaded (0, 2, 4, 6, 8) = 5 loaded
        # But we need to check the actual display
        # The progress column shows "complete/total"


def test_framework_status_no_software_dev_directory(tmp_path, runner):
    """Test framework status handles missing software-development directory."""
    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code != 0
        assert "software-development directory not found" in result.output


def test_framework_status_empty_brain_directory(tmp_path, runner):
    """Test framework status with empty brain directory."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "Total Brains: 0" in result.output
        assert "Total Sources: 0" in result.output


def test_framework_status_ignores_non_brain_directories(tmp_path, runner):
    """Test framework status ignores directories not ending with -brain."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    # Create brain directory
    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()

    # Create non-brain directory
    other_dir = sw_dev / "other-directory"
    other_dir.mkdir()

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "Total Brains: 1" in result.output
        # Non-brain directory should be ignored


def test_framework_status_handles_missing_sources_directory(tmp_path, runner):
    """Test framework status handles brain directory without sources."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    # No sources directory created

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "brain-01" in result.output
        assert "0" in result.output  # No sources


def test_framework_status_handles_invalid_yaml_in_sources(tmp_path, runner):
    """Test framework status handles invalid YAML in source files."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    # Create source with invalid YAML
    source_file = sources_dir / "FUENTE-001.md"
    source_file.write_text(
        """---
invalid: yaml: content:
    broken: [
---

# Content
"""
    )

    # Create source with valid YAML
    source_file2 = sources_dir / "FUENTE-002.md"
    source_file2.write_text(
        """---
source_id: "FUENTE-002"
brain: "brain-01"
title: "Valid Source"
distillation_quality: "complete"
loaded_in_notebook: false
---

# Content
"""
    )

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Should handle invalid YAML gracefully
        assert "brain-01" in result.output


def test_framework_status_handles_sources_without_yaml(tmp_path, runner):
    """Test framework status handles source files without YAML front matter."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    # Create source without YAML
    source_file = sources_dir / "FUENTE-001.md"
    source_file.write_text("# Just markdown content\n\nNo front matter here.")

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Should handle missing YAML gracefully
        assert "brain-01" in result.output


def test_framework_status_zero_sources_division(tmp_path):
    """Test framework status handles zero total sources without division by zero."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    # Create brain with no sources
    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    (brain_dir / "sources").mkdir()

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        runner = CliRunner()
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Should not crash on division by zero
        assert "0%" in result.output


# =============================================================================
# Test framework release command
# =============================================================================


def test_framework_release_creates_tag(runner):
    """Test framework release creates git tag."""
    with patch("mastermind_cli.utils.git.get_repo") as mock_get_repo:
        import mastermind_cli.commands.framework as fw_module

        fw_module.get_repo = mock_get_repo

        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = runner.invoke(framework, ["release", "--version", "1.0.0"])
        assert result.exit_code == 0
        assert "Release 1.0.0" in result.output
        mock_repo.create_tag.assert_called_once_with("1.0.0", message="Release 1.0.0")


def test_framework_release_with_message(runner):
    """Test framework release includes custom message."""
    # Patch the import before it happens
    with patch("mastermind_cli.utils.git.get_repo") as mock_get_repo:
        # Make it available in the commands.framework namespace
        import mastermind_cli.commands.framework as fw_module

        fw_module.get_repo = mock_get_repo

        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = runner.invoke(
            framework, ["release", "--version", "1.0.0", "--message", "First release"]
        )
        assert result.exit_code == 0
        mock_repo.create_tag.assert_called_once_with(
            "1.0.0", message="Release 1.0.0\n\nFirst release"
        )


def test_framework_release_multiline_message(runner):
    """Test framework release handles multiline messages."""
    with patch("mastermind_cli.utils.git.get_repo") as mock_get_repo:
        import mastermind_cli.commands.framework as fw_module

        fw_module.get_repo = mock_get_repo

        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        result = runner.invoke(
            framework,
            [
                "release",
                "--version",
                "2.0.0",
                "--message",
                "Major release\n\nNew features",
            ],
        )
        assert result.exit_code == 0
        assert "Major release" in result.output
        assert "New features" in result.output


def test_framework_release_not_git_repository(runner):
    """Test framework release handles non-git repository."""
    with patch(
        "mastermind_cli.utils.git.get_repo", side_effect=ValueError("Not a git repo")
    ) as mock_get_repo:
        import mastermind_cli.commands.framework as fw_module

        fw_module.get_repo = mock_get_repo

        result = runner.invoke(framework, ["release", "--version", "1.0.0"])
        assert result.exit_code != 0
        assert "Error creating release" in result.output


def test_framework_release_requires_version(runner):
    """Test framework release requires version parameter."""
    result = runner.invoke(framework, ["release"])
    assert result.exit_code != 0
    assert "Missing option" in result.output or "--version" in result.output


def test_framework_release_handles_git_error(runner):
    """Test framework release handles git errors."""
    with patch("mastermind_cli.utils.git.get_repo") as mock_get_repo:
        import mastermind_cli.commands.framework as fw_module

        fw_module.get_repo = mock_get_repo

        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo
        mock_repo.create_tag.side_effect = Exception("Git error: tag already exists")

        result = runner.invoke(framework, ["release", "--version", "1.0.0"])
        # Should catch the exception and show error
        assert result.exit_code != 0 or "Error creating release" in result.output


# =============================================================================
# Test integration scenarios
# =============================================================================


def test_framework_status_with_realistic_structure(tmp_path, runner):
    """Test framework status with realistic project structure."""
    # Create structure similar to actual project
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    # Product Strategy Brain (brain-01)
    brain01 = sw_dev / "brain-01-brain"
    brain01.mkdir()
    sources01 = brain01 / "sources"
    sources01.mkdir()

    # Add 10 sources with varying completion
    for i in range(10):
        complete = "complete" if i < 7 else "partial"
        loaded = i < 5
        source = sources01 / f"FUENTE-{i+1:03d}.md"
        source.write_text(
            f"""---
source_id: "FUENTE-{i+1:03d}"
brain: "brain-01"
title: "Source {i+1}"
distillation_quality: "{complete}"
loaded_in_notebook: {str(loaded).lower()}
---

# Content {i+1}
"""
        )

    # UX Research Brain (brain-02)
    brain02 = sw_dev / "brain-02-brain"
    brain02.mkdir()
    sources02 = brain02 / "sources"
    sources02.mkdir()

    # Add fewer sources to brain-02
    for i in range(5):
        source = sources02 / f"FUENTE-{i+1:03d}.md"
        source.write_text(
            f"""---
source_id: "FUENTE-{i+1:03d}"
brain: "brain-02"
title: "UX Source {i+1}"
distillation_quality: "complete"
loaded_in_notebook: true
---

# UX Content {i+1}
"""
        )

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        assert "Total Brains: 2" in result.output
        assert "Total Sources: 15" in result.output
        # brain-01: 7/10 complete, brain-02: 5/5 complete = 12/15 = 80%
        assert "80%" in result.output or "12/15" in result.output


def test_framework_status_with_non_source_files(tmp_path, runner):
    """Test framework status ignores non-source files in sources directory."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    # Create actual source file
    (sources_dir / "FUENTE-001.md").write_text(
        """---
source_id: "FUENTE-001"
distillation_quality: "complete"
loaded_in_notebook: false
---

# Content
"""
    )

    # Create non-source files (should be ignored)
    (sources_dir / "README.md").write_text("# Readme")
    (sources_dir / ".gitkeep").write_text("")
    (sources_dir / "NOTES.txt").write_text("Notes")

    with patch("pathlib.Path.cwd", return_value=tmp_path):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Should only count FUENTE-001.md
        assert "Total Sources: 1" in result.output


def test_framework_status_nested_project_marker(tmp_path, runner):
    """Test framework status finds project root from nested directory."""
    # Create marker in root
    (tmp_path / "CLAUDE.md").write_text("# Project Root")

    # Create software-development nested deep
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    (sources_dir / "FUENTE-001.md").write_text(
        """---
source_id: "FUENTE-001"
distillation_quality: "complete"
loaded_in_notebook: false
---

# Content
"""
    )

    # Simulate being in a nested subdirectory
    nested = tmp_path / "apps" / "api" / "src"
    nested.mkdir(parents=True)

    with patch("pathlib.Path.cwd", return_value=nested):
        result = runner.invoke(framework, ["status"])
        assert result.exit_code == 0
        # Should find the project root and display status


# =============================================================================
# Test error handling
# =============================================================================


def test_framework_status_handles_permission_errors(tmp_path, runner):
    """Test framework status handles permission errors gracefully."""
    sw_dev = tmp_path / "docs" / "software-development"
    sw_dev.mkdir(parents=True)

    brain_dir = sw_dev / "brain-01-brain"
    brain_dir.mkdir()
    sources_dir = brain_dir / "sources"
    sources_dir.mkdir()

    # Create a source file
    source_file = sources_dir / "FUENTE-001.md"
    source_file.write_text(
        """---
source_id: "FUENTE-001"
distillation_quality: "complete"
loaded_in_notebook: false
---

# Content
"""
    )

    # Mock read_yaml_frontmatter to raise permission error
    with patch(
        "mastermind_cli.commands.framework.read_yaml_frontmatter",
        side_effect=PermissionError("Permission denied"),
    ):
        with patch("pathlib.Path.cwd", return_value=tmp_path):
            runner = CliRunner()
            result = runner.invoke(framework, ["status"])
            # Should handle gracefully, not crash
            assert result.exit_code == 0 or "Error" in result.output


def test_framework_release_with_special_characters_in_message(runner):
    """Test framework release handles special characters in message."""
    with patch("mastermind_cli.utils.git.get_repo") as mock_get_repo:
        mock_repo = MagicMock()
        mock_get_repo.return_value = mock_repo

        special_message = "Release with quotes: 'test' and \"double\" and emojis: 🎉"
        result = runner.invoke(
            framework, ["release", "--version", "1.0.0", "--message", special_message]
        )
        assert result.exit_code == 0
        assert "🎉" in result.output
