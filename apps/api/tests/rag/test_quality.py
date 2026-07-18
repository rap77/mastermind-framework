"""Tests for the cold-vs-RAG quality comparison helper."""

from __future__ import annotations

import json
from pathlib import Path

from mastermind_cli.rag.quality import compare_cold_vs_rag


def test_compare_cold_vs_rag_passes_when_rag_is_richer(tmp_path: Path) -> None:
    """RAG should beat cold when its output is more substantive."""
    output_path = tmp_path / "quality.json"

    result = compare_cold_vs_rag(
        brain_id="brain-01-product-strategy",
        cold_output_json={},
        rag_output_json={
            "recommendation": "use RAG",
            "analysis": "better context",
            "strategy": "compare against baseline",
        },
        output_path=output_path,
    )

    assert result.passes is True
    assert result.delta > 0.0
    assert result.rag_quality_score > result.cold_quality_score
    assert output_path.exists()
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["passes"] is True
    assert payload["brain_id"] == "brain-01-product-strategy"


def test_compare_cold_vs_rag_fails_when_rag_is_worse(tmp_path: Path) -> None:
    """RAG should fail when it does not improve on the cold baseline."""
    result = compare_cold_vs_rag(
        brain_id="brain-01-product-strategy",
        cold_output_json={
            "recommendation": "good enough",
            "analysis": "baseline",
            "strategy": "keep cold",
        },
        rag_output_json={},
        output_path=tmp_path / "quality.json",
    )

    assert result.passes is False
    assert result.delta < 0.0
    assert result.cold_quality_score > result.rag_quality_score
