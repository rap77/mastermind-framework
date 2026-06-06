#!/usr/bin/env python3
"""Validate whether a canonical objective is ready for discover packaging."""

from __future__ import annotations

import json
from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path.cwd()
OBJECTIVE_SPECS_DIR = PROJECT_ROOT / "docs" / "canonical" / "objective-specs"
REQUIRED_REPORT_KEYS = {
    "schema_version",
    "doc_type",
    "intent",
    "context_sources",
    "evidence",
    "assumptions",
    "gaps_detected",
    "questions_asked",
    "questions_unanswered",
    "confidence",
    "generated_files",
}


def parse_args() -> Namespace:
    """Parse command arguments for the objective context gate."""
    parser = ArgumentParser(
        description="Validate a canonical objective before discover materializes it."
    )
    parser.add_argument(
        "--objective",
        default=None,
        help="Objective slug under docs/canonical/objective-specs/<slug>.md",
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Explicit path to a canonical objective markdown file.",
    )
    return parser.parse_args()


def resolve_markdown_path(args: Namespace) -> Path:
    """Resolve the canonical objective markdown path from slug or explicit path."""
    if args.path:
        return Path(args.path).resolve()
    if args.objective:
        return (OBJECTIVE_SPECS_DIR / f"{args.objective}.md").resolve()
    raise ValueError("Pass --objective <slug> or --path <canonical-markdown-path>.")


def load_report(report_path: Path) -> dict[str, object]:
    """Load and parse the sidecar intake report JSON."""
    return json.loads(report_path.read_text(encoding="utf-8"))


def gate_status_path(markdown_path: Path) -> Path:
    """Return the persisted gate-status artifact path for a canonical objective."""
    return markdown_path.with_suffix(".gate.json")


def validate_report_shape(report: dict[str, object]) -> list[str]:
    """Return missing or malformed report contract issues."""
    issues: list[str] = []
    missing_keys = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing_keys:
        issues.append(f"Missing report keys: {', '.join(missing_keys)}")
    if report.get("doc_type") != "objective":
        issues.append("Report doc_type must be 'objective'")
    return issues


def build_next_command(markdown_path: Path, status: str) -> str:
    """Return the next recommended command for a gate outcome."""
    objective_slug = markdown_path.stem
    if status == "PASSED":
        return f"/mm:discover --existing --objective {objective_slug}"
    return f"/mm:objective-context-check --objective {objective_slug}"


def write_gate_status(
    markdown_path: Path,
    report_path: Path,
    status: str,
    *,
    issues: list[str] | None = None,
) -> None:
    """Persist a deterministic gate-status artifact next to the canonical objective."""
    artifact: dict[str, Any] = {
        "schema_version": 1,
        "objective_slug": markdown_path.stem,
        "canonical_markdown": str(markdown_path),
        "intake_report": str(report_path),
        "status": status,
        "next_command": build_next_command(markdown_path, status),
    }
    if issues:
        artifact["issues"] = issues
    gate_status_path(markdown_path).write_text(
        json.dumps(artifact, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    """Run the gate and print a structured readiness verdict."""
    try:
        args = parse_args()
        markdown_path = resolve_markdown_path(args)
    except ValueError as exc:
        print("STATUS: FAILED")
        print(f"- {exc}")
        return 1

    report_path = markdown_path.with_suffix(".json")
    issues: list[str] = []

    if not markdown_path.exists():
        issues.append(f"Canonical markdown missing: {markdown_path}")
    if not report_path.exists():
        issues.append(f"Canonical intake report missing: {report_path}")
    if issues:
        if markdown_path.exists():
            write_gate_status(markdown_path, report_path, "FAILED", issues=issues)
        print("STATUS: FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    markdown_text = markdown_path.read_text(encoding="utf-8")
    if "<!-- mm:objective-spec" not in markdown_text:
        write_gate_status(
            markdown_path,
            report_path,
            "FAILED",
            issues=["Canonical markdown is missing the mm:objective-spec marker"],
        )
        print("STATUS: FAILED")
        print("- Canonical markdown is missing the mm:objective-spec marker")
        return 1

    try:
        report = load_report(report_path)
    except json.JSONDecodeError as exc:
        write_gate_status(
            markdown_path,
            report_path,
            "FAILED",
            issues=[f"Canonical intake report is invalid JSON: {exc}"],
        )
        print("STATUS: FAILED")
        print(f"- Canonical intake report is invalid JSON: {exc}")
        return 1

    issues.extend(validate_report_shape(report))
    if issues:
        write_gate_status(markdown_path, report_path, "FAILED", issues=issues)
        print("STATUS: FAILED")
        for issue in issues:
            print(f"- {issue}")
        return 1

    questions_unanswered = report.get("questions_unanswered", [])
    gaps_detected = report.get("gaps_detected", [])
    confidence = str(report.get("confidence", "unknown"))

    print(f"CANONICAL: {markdown_path}")
    print(f"REPORT: {report_path}")

    if questions_unanswered:
        write_gate_status(
            markdown_path,
            report_path,
            "NEEDS_INPUT",
            issues=[
                f"Outstanding questions: {', '.join(str(q) for q in questions_unanswered)}"
            ],
        )
        print("STATUS: NEEDS_INPUT")
        print(
            f"- Outstanding questions: {', '.join(str(q) for q in questions_unanswered)}"
        )
        if gaps_detected:
            print(f"- Gaps detected: {', '.join(str(g) for g in gaps_detected)}")
        print("- Next: answer the interview questions before running discover")
        return 2

    write_gate_status(markdown_path, report_path, "PASSED")
    print("STATUS: PASSED")
    print(f"- Confidence: {confidence}")
    if gaps_detected:
        print(f"- Non-blocking gaps: {', '.join(str(g) for g in gaps_detected)}")
    print(f"- Next: {build_next_command(markdown_path, 'PASSED')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
