"""Integration tests for full rediscovery flow."""

from core.detector import ProjectDetector
from core.orchestrator import Orchestrator


def test_full_integration_python_project(tmp_path):
    """Test full flow with Python project."""
    # Setup test project
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_example.py").write_text("def test_true(): assert True")

    # Detect
    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()

    assert fingerprint["type"] == "monolito"
    assert "python" in fingerprint["stacks"]

    # Execute
    orchestrator = Orchestrator(tmp_path, fingerprint)
    results = orchestrator.execute_all()

    assert "python" in results
    # Tests might be skipped if tooling unavailable
    assert results["python"]["status"] in ["success", "skipped"]


def test_generate_health_report(tmp_path):
    """Test health report generation."""
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / "tests").mkdir()

    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()
    orchestrator = Orchestrator(tmp_path, fingerprint)

    report = orchestrator.format_health_report()

    assert "# Project Health Check" in report
    assert "## Python Stack" in report


def test_multi_stack_detection(tmp_path):
    """Test detection of multi-stack project."""
    # Create Python + Node project
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    (tmp_path / "package.json").write_text('{"name": "test"}')

    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()

    assert "python" in fingerprint["stacks"]
    assert "node" in fingerprint["stacks"]

    # Orchestrator should load both strategies
    orchestrator = Orchestrator(tmp_path, fingerprint)
    assert len(orchestrator.strategies) == 2


def test_orchestrator_with_unknown_stack(tmp_path):
    """Test orchestrator handles unknown stacks gracefully."""
    # Create fingerprint with unknown stack
    fingerprint = {
        "type": "monolito",
        "stacks": ["python", "unknown_stack"],
        "structure": {"python": {"tests": [], "package_manager": "pip"}},
    }

    orchestrator = Orchestrator(tmp_path, fingerprint)

    # Should only load python strategy (unknown_stack ignored)
    assert len(orchestrator.strategies) == 1
    assert orchestrator.strategies[0].name == "python"


def test_health_report_with_skipped_stack(tmp_path):
    """Test health report shows skipped stacks."""
    # Create project with Node but no npm
    (tmp_path / "package.json").write_text('{"name": "test"}')

    detector = ProjectDetector(tmp_path)
    fingerprint = detector.detect()
    orchestrator = Orchestrator(tmp_path, fingerprint)

    report = orchestrator.format_health_report()

    # Report should mention Node stack
    assert "## Node Stack" in report
