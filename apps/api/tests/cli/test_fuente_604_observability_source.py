"""Regression tests for FUENTE-604 observability source metadata and structure."""

from __future__ import annotations

from pathlib import Path

from mastermind_cli.utils.validation import validate_source_file
from mastermind_cli.utils.yaml import read_yaml_frontmatter


SOURCE_PATH = (
    Path(__file__).resolve().parents[4]
    / "docs"
    / "nichos"
    / "software-development"
    / "BRAIN-06-QA-DEVOPS"
    / "sources"
    / "FUENTE-604-observability-engineering-majors.md"
)


def test_fuente_604_has_expected_front_matter() -> None:
    """FUENTE-604 should keep the expected metadata contract."""
    metadata, content = read_yaml_frontmatter(str(SOURCE_PATH))

    assert metadata is not None
    assert metadata["source_id"] == "FUENTE-604"
    assert metadata["brain"] == "brain-software-06-qa-devops"
    assert (
        metadata["title"]
        == "Observability Engineering: Achieving Production Excellence"
    )
    assert metadata["author"] == "Charity Majors, Liz Fong-Jones, George Miranda"
    assert metadata["type"] == "book"
    assert metadata["isbn"] == "978-1492076445"
    assert metadata["distillation_quality"] == "complete"
    assert "### 1. Principios Fundamentales" in content
    assert "### 5. Anti-patrones" in content


def test_fuente_604_passes_framework_validation() -> None:
    """FUENTE-604 should pass the framework source validator without warnings."""
    result = validate_source_file(str(SOURCE_PATH))

    assert result.is_valid
    assert result.errors == []
    assert result.warnings == []
