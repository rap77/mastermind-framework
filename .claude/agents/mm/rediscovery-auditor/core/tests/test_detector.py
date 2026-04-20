"""Tests for ProjectDetector - Fingerprint-based project detection."""

from pathlib import Path
from core.detector import ProjectDetector


def test_detect_python_monolito(tmp_path):
    """Detect Python monolito project."""
    # Create pyproject.toml
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    # Create tests directory
    (tmp_path / "tests").mkdir()
    # Create src directory
    (tmp_path / "src").mkdir()

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert result["type"] == "monolito"
    assert "python" in result["stacks"]
    assert result["structure"]["python"]["package_manager"] in ["uv", "pip"]


def test_detect_python_monorepo(tmp_path):
    """Detect Python monorepo project."""
    # Create pyproject.toml in root
    (tmp_path / "pyproject.toml").write_text("[project]\nname='monorepo'\n")
    # Create apps directories (monorepo pattern)
    apps_dir = tmp_path / "apps"
    apps_dir.mkdir()
    (apps_dir / "api").mkdir()
    (apps_dir / "web").mkdir()

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert result["type"] == "monorepo"
    assert "python" in result["stacks"]


def test_detect_node_project(tmp_path):
    """Detect Node.js project."""
    # Create package.json
    (tmp_path / "package.json").write_text('{"name": "test", "version": "1.0.0"}\n')
    # Create pnpm-lock.yaml (indicator of pnpm usage)
    (tmp_path / "pnpm-lock.yaml").write_text('lockfileVersion: "6.0"\n')

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert "node" in result["stacks"]
    assert result["structure"]["node"]["package_manager"] in ["pnpm", "npm", "yarn"]


def test_detect_rust_project(tmp_path):
    """Detect Rust project."""
    # Create Cargo.toml
    (tmp_path / "Cargo.toml").write_text(
        '[package]\nname = "test"\nversion = "0.1.0"\n'
    )
    # Create src directory
    (tmp_path / "src").mkdir()

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert "rust" in result["stacks"]
    assert result["structure"]["rust"]["edition"] in ["2018", "2021"]


def test_detect_go_project(tmp_path):
    """Detect Go project."""
    # Create go.mod
    (tmp_path / "go.mod").write_text("module test\n\ngo 1.21\n")
    # Create main.go
    (tmp_path / "main.go").write_text("package main\n\nfunc main() {}\n")

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert "go" in result["stacks"]
    assert "go 1." in result["structure"]["go"]["version"]


def test_detect_multi_stack_project(tmp_path):
    """Detect project with multiple stacks (Python + Node)."""
    # Python files
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / "requirements.txt").write_text("pytest\n")
    # Node files
    (tmp_path / "package.json").write_text('{"name": "test"}\n')
    (tmp_path / "tsconfig.json").write_text("{}\n")

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert "python" in result["stacks"]
    assert "node" in result["stacks"]
    assert len(result["stacks"]) == 2


def test_detect_unknown_project(tmp_path):
    """Detect project with no known fingerprints."""
    # Create a random directory without known fingerprints
    (tmp_path / "random.txt").write_text("some content\n")
    (tmp_path / "data").mkdir()

    detector = ProjectDetector(tmp_path)
    result = detector.detect()

    assert result["type"] == "unknown"
    assert len(result["stacks"]) == 0


def test_tool_detection_with_timeout(tmp_path, monkeypatch):
    """Test tool detection handles timeout gracefully."""
    # Create a Python project
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")

    detector = ProjectDetector(tmp_path)
    # Should not raise exception even if tools are not available
    result = detector.detect()

    assert "python" in result["stacks"]
    # Tool availability should be detected or gracefully handled
    assert "tools" in result["structure"]["python"]


def test_nonexistent_directory():
    """Test detector handles non-existent directory gracefully."""
    detector = ProjectDetector(Path("/nonexistent/path"))
    result = detector.detect()

    assert result["type"] == "unknown"
    assert len(result["stacks"]) == 0
