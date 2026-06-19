"""CLI tests for manual source ingestion preview."""

from __future__ import annotations

import json
from pathlib import Path

from click.testing import CliRunner
import pytest

from mastermind_cli.commands.source import source


@pytest.fixture
def runner() -> CliRunner:
    """Return a Click runner for source CLI tests."""
    return CliRunner()


def _write_source_fixture(
    base_dir: Path, source_id: str = "FUENTE-999", filename_suffix: str = ""
) -> Path:
    """Create a minimal valid source fixture under docs/**/sources."""
    source_dir = (
        base_dir / "docs" / "universal" / "08-master-interviewer-brain" / "sources"
    )
    source_dir.mkdir(parents=True, exist_ok=True)
    suffix = f"_{filename_suffix}" if filename_suffix else ""
    source_file = source_dir / f"{source_id}{suffix}.md"
    source_file.write_text(
        f"""---
source_id: "{source_id}"
brain: "brain-universal-08-master-interviewer"
niche: "universal"
title: "Fixture Source"
author: "Test Author"
expert_id: "EXP-999"
type: "book"
language: "es"
year: 2026
isbn: "0000000000"
skills_covered: ["H1"]
distillation_quality: "complete"
---

# {source_id}: Fixture Source

## Conocimiento Destilado

### 1. Principios Fundamentales

> **P1: Listen for specifics**
> Ask for concrete past behavior instead of opinions.

### 2. Frameworks y Metodologías

#### FM1: Interview Ladder

Start with broad context, then move into a concrete last-time story.

#### FM2: Silence Probe

Use short silences to invite deeper detail from the interviewee.

### 4. Criterios de Decisión

- Priorizar preguntas sobre comportamientos reales recientes.

### 5. Anti-patrones

- Aceptar opiniones abstractas sin pedir ejemplos concretos.

## Notas de Destilación

- Fixture notes
""",
        encoding="utf-8",
    )
    return source_file


def test_ingest_preview_prints_json_report(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ingest-preview emits an auditable JSON report to stdout."""
    _write_source_fixture(tmp_path)
    monkeypatch.setattr(
        "mastermind_cli.commands.source.get_project_root", lambda: tmp_path
    )

    result = runner.invoke(source, ["ingest-preview", "FUENTE-999"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_id"] == "FUENTE-999"
    assert payload["brain_id"] == "brain-universal-08-master-interviewer"
    assert payload["collection_type"] == "domain_knowledge"
    assert payload["chunk_count"] == 5
    assert len(payload["chunks"]) == 5
    assert payload["chunks"][0]["source_ref"] == "FUENTE-999"
    assert payload["chunks"][0]["chunk_hash"]


def test_ingest_preview_writes_report_file(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ingest-preview writes the preview report to a requested JSON file."""
    _write_source_fixture(tmp_path, source_id="FUENTE-998")
    monkeypatch.setattr(
        "mastermind_cli.commands.source.get_project_root", lambda: tmp_path
    )
    output_path = tmp_path / "dist" / "preview.json"

    result = runner.invoke(
        source,
        ["ingest-preview", "FUENTE-998", "--output", str(output_path)],
    )

    assert result.exit_code == 0
    summary = json.loads(result.output)
    assert summary["status"] == "written"
    assert summary["output"] == str(output_path)
    report = json.loads(output_path.read_text(encoding="utf-8"))
    assert report["source_id"] == "FUENTE-998"
    assert report["chunk_count"] == 5


def test_ingest_preview_finds_suffixed_source_filenames(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ingest-preview resolves real-world FUENTE filenames with suffixes."""
    _write_source_fixture(
        tmp_path, source_id="FUENTE-805", filename_suffix="user-interviews_hall"
    )
    monkeypatch.setattr(
        "mastermind_cli.commands.source.get_project_root", lambda: tmp_path
    )

    result = runner.invoke(source, ["ingest-preview", "FUENTE-805"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_id"] == "FUENTE-805"


def test_ingest_preview_rejects_missing_source(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ingest-preview aborts cleanly when the source is missing."""
    monkeypatch.setattr(
        "mastermind_cli.commands.source.get_project_root", lambda: tmp_path
    )

    result = runner.invoke(source, ["ingest-preview", "FUENTE-404"])

    assert result.exit_code != 0
    assert "Source FUENTE-404 not found" in result.output


def test_ingest_preview_ignores_unrelated_invalid_yaml_sources(
    runner: CliRunner, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """ingest-preview should not fail on invalid YAML in unrelated source files."""
    source_file = _write_source_fixture(tmp_path, source_id="FUENTE-777")
    bad_file = source_file.parent / "FUENTE-BAD_broken.md"
    bad_file.write_text(
        '---\nsource_id: "FUENTE-BAD"\ntitle: "broken: [\n---\n', encoding="utf-8"
    )
    monkeypatch.setattr(
        "mastermind_cli.commands.source.get_project_root", lambda: tmp_path
    )

    result = runner.invoke(source, ["ingest-preview", "FUENTE-777"])

    assert result.exit_code == 0
    payload = json.loads(result.output)
    assert payload["source_id"] == "FUENTE-777"
