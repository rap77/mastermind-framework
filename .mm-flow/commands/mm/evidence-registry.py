#!/usr/bin/env python3
"""Manage the MasterMind evidence registry artifact."""

from __future__ import annotations

import argparse
import json
import logging
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from planning_paths import get_planning_dir, planning_relpath

logger = logging.getLogger(__name__)

SOURCE_TYPES = {"repo", "url", "book", "doc", "product", "system", "interview"}
VERSION_STATES = {"current", "superseded", "archived", "deprecated", "retracted"}
DELTA_TYPES = {"functional", "structural", "data", "nfr", "decision"}
DELTA_DECISIONS = {"adopted", "adapted", "rejected", "deprecated", "superseded"}


def project_root() -> Path:
    """Find the git project root, falling back to file-relative detection."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent.parent.parent


ROOT = project_root()
PLANNING_DIR = get_planning_dir(ROOT)
PLANNING_LABEL = planning_relpath(ROOT)
REGISTRY_PATH = PLANNING_DIR / "evidence" / "evidence-registry.json"
REGISTRY_RELATIVE_PATH = REGISTRY_PATH.relative_to(ROOT)

APPS_API_DIR = ROOT / "apps" / "api"
if str(APPS_API_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_API_DIR))

from mastermind_cli.mm_flow.evidence_registry_service import (  # noqa: E402
    EvidenceRegistryService,
)

SERVICE = EvidenceRegistryService(REGISTRY_PATH)


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Manage the MM evidence registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser(
        "register", help="Register a new evidence version."
    )
    register_parser.add_argument("--id", dest="version_id")
    register_parser.add_argument("--source-id")
    register_parser.add_argument(
        "--source-type", required=True, choices=sorted(SOURCE_TYPES)
    )
    register_parser.add_argument("--name", required=True)
    register_parser.add_argument("--uri", required=True)
    register_parser.add_argument("--version-ref", required=True)
    register_parser.add_argument("--version-hash", required=True)
    register_parser.add_argument("--summary", required=True)
    register_parser.add_argument(
        "--state", choices=sorted(VERSION_STATES), default="current"
    )
    register_parser.add_argument("--confidence", type=float, default=0.7)
    register_parser.add_argument("--coverage", type=float, default=0.7)
    register_parser.add_argument("--critical-gaps", type=int, default=0)
    register_parser.add_argument("--important-gaps", type=int, default=0)
    register_parser.add_argument("--optional-gaps", type=int, default=0)
    register_parser.add_argument("--contradictions", type=int, default=0)
    register_parser.add_argument("--user-answers-complete", action="store_true")

    subparsers.add_parser("list", help="List evidence versions.")

    list_deltas_parser = subparsers.add_parser(
        "list-deltas", help="List evidence deltas."
    )
    list_deltas_parser.add_argument("--source-id")
    list_deltas_parser.add_argument("--delta-type", choices=sorted(DELTA_TYPES))
    list_deltas_parser.add_argument("--decision", choices=sorted(DELTA_DECISIONS))

    readiness_parser = subparsers.add_parser(
        "readiness", help="Calculate readiness for a registered evidence version."
    )
    readiness_parser.add_argument("--id", dest="version_id", required=True)

    delta_parser = subparsers.add_parser(
        "delta", help="Record a delta between versions."
    )
    delta_parser.add_argument("--from-id", dest="from_version_id", required=True)
    delta_parser.add_argument("--to-id", dest="to_version_id", required=True)
    delta_parser.add_argument(
        "--delta-type", choices=sorted(DELTA_TYPES), required=True
    )
    delta_parser.add_argument("--summary", required=True)
    delta_parser.add_argument(
        "--impact", choices=["low", "medium", "high"], default="medium"
    )
    delta_parser.add_argument(
        "--risk", choices=["low", "medium", "high"], default="medium"
    )
    delta_parser.add_argument(
        "--decision", choices=sorted(DELTA_DECISIONS), default="adapted"
    )

    return parser.parse_args()


def utc_now() -> str:
    """Return an ISO8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def load_registry() -> dict[str, Any]:
    """Load the evidence registry, creating a default shape when needed."""
    return SERVICE.load_registry()


def write_registry(data: dict[str, Any]) -> None:
    """Persist the registry artifact."""
    SERVICE.write_registry(data)


def next_version_id(data: dict[str, Any]) -> str:
    """Generate the next sequential evidence version ID."""
    return SERVICE._next_version_id(data)


def next_delta_id(data: dict[str, Any]) -> str:
    """Generate the next sequential evidence delta ID."""
    return SERVICE._next_delta_id(data)


def append_delta(
    data: dict[str, Any],
    *,
    from_version_id: str,
    to_version_id: str,
    delta_type: str,
    summary: str,
    impact: str,
    risk: str,
    decision: str,
    source_id: str | None,
) -> dict[str, Any]:
    """Append a delta entry and return it."""
    return SERVICE.record_delta(
        data,
        from_version_id=from_version_id,
        to_version_id=to_version_id,
        delta_type=delta_type,
        summary=summary,
        impact=impact,
        risk=risk,
        decision=decision,
        source_id=source_id,
    )


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value to the given range."""
    return SERVICE._clamp(value, minimum, maximum)


def calculate_readiness(entry: dict[str, Any]) -> dict[str, Any]:
    """Compute a deterministic readiness verdict for an evidence version."""
    return SERVICE.calculate_readiness(entry)


def register_version(args: argparse.Namespace) -> int:
    """Register a new evidence version entry."""
    try:
        result = SERVICE.register_version(
            source_id=args.source_id,
            source_type=args.source_type,
            name=args.name,
            uri=args.uri,
            version_ref=args.version_ref,
            version_hash=args.version_hash,
            summary=args.summary,
            state=args.state,
            confidence=args.confidence,
            coverage=args.coverage,
            critical_gaps=args.critical_gaps,
            important_gaps=args.important_gaps,
            optional_gaps=args.optional_gaps,
            contradictions=args.contradictions,
            user_answers_complete=args.user_answers_complete,
            version_id=args.version_id,
        )
    except ValueError as exc:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- {exc}\n")
        return 1
    logger.info("STATUS: PASSED")
    logger.info("- Registered evidence version: %s", result["version"]["id"])
    logger.info("- Registry: %s", result["registry_path"])
    return 0


def list_versions() -> int:
    """List evidence versions as JSON."""
    sys.stdout.write(json.dumps(SERVICE.list_versions(), indent=2) + "\n")
    return 0


def list_deltas(args: argparse.Namespace) -> int:
    """List evidence deltas as JSON."""
    sys.stdout.write(
        json.dumps(
            SERVICE.list_deltas(
                source_id=args.source_id,
                delta_type=args.delta_type,
                decision=args.decision,
            ),
            indent=2,
        )
        + "\n"
    )
    return 0


def record_delta(args: argparse.Namespace) -> int:
    """Record a delta between two evidence versions."""
    try:
        payload = SERVICE.record_explicit_delta(
            from_version_id=args.from_version_id,
            to_version_id=args.to_version_id,
            delta_type=args.delta_type,
            summary=args.summary,
            impact=args.impact,
            risk=args.risk,
            decision=args.decision,
        )
    except ValueError as exc:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- {exc}\n")
        return 1

    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


def readiness(args: argparse.Namespace) -> int:
    """Compute readiness for an evidence version."""
    try:
        payload = SERVICE.readiness(args.version_id)
    except ValueError as exc:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- {exc}\n")
        return 1
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.command == "register":
        return register_version(args)
    if args.command == "list":
        return list_versions()
    if args.command == "list-deltas":
        return list_deltas(args)
    if args.command == "readiness":
        return readiness(args)
    if args.command == "delta":
        return record_delta(args)
    sys.stdout.write("STATUS: FAILED\n")
    sys.stdout.write(f"- Unsupported command: {args.command}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
