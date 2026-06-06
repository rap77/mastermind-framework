#!/usr/bin/env python3
"""Shared helpers for canonical objective gate-status inference."""

from __future__ import annotations

import json
from pathlib import Path


def objective_canonical_markdown_path(root_dir: Path, objective_slug: str) -> Path:
    """Return the canonical objective markdown path for a slug."""
    return root_dir / "docs" / "canonical" / "objective-specs" / f"{objective_slug}.md"


def objective_gate_status_path(markdown_path: Path) -> Path:
    """Return the persisted gate-status artifact path for a canonical objective."""
    return markdown_path.with_suffix(".gate.json")


def infer_objective_gate_status(
    root_dir: Path, objective_slug: str
) -> tuple[str, str, str | None]:
    """Infer gate status for a canonical objective from persisted artifacts.

    Returns:
        (status, guidance, artifact_path)
    """
    markdown_path = objective_canonical_markdown_path(root_dir, objective_slug)
    if not markdown_path.exists():
        return ("NO_CANONICAL", "", None)

    report_path = markdown_path.with_suffix(".json")
    gate_path = objective_gate_status_path(markdown_path)
    if not gate_path.exists():
        return (
            "NOT_RUN",
            f"Run /mm:objective-context-check --objective {objective_slug} before discover materializes this canonical objective.",
            str(markdown_path),
        )

    if not report_path.exists():
        return (
            "FAILED",
            "Canonical intake report is missing. Rebuild or repair the canonical objective, then rerun /mm:objective-context-check --objective "
            f"{objective_slug}.",
            str(gate_path),
        )

    gate_mtime = gate_path.stat().st_mtime
    if (
        markdown_path.stat().st_mtime > gate_mtime
        or report_path.stat().st_mtime > gate_mtime
    ):
        return (
            "NOT_RUN",
            f"Canonical objective changed after the last gate run. Rerun /mm:objective-context-check --objective {objective_slug}.",
            str(gate_path),
        )

    try:
        gate_data = json.loads(gate_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return (
            "FAILED",
            f"Gate status artifact is invalid JSON. Rerun /mm:objective-context-check --objective {objective_slug}.",
            str(gate_path),
        )

    status = str(gate_data.get("status", "FAILED")).upper()
    if status == "PASSED":
        return ("PASSED", "", str(gate_path))
    if status == "NEEDS_INPUT":
        return (
            "NEEDS_INPUT",
            f"Objective gate still needs input. Answer the open questions, then rerun /mm:objective-context-check --objective {objective_slug}.",
            str(gate_path),
        )
    return (
        "FAILED",
        f"Objective gate did not pass. Inspect the gate output/artifact and rerun /mm:objective-context-check --objective {objective_slug}.",
        str(gate_path),
    )
