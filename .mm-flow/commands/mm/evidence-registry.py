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
    if not REGISTRY_PATH.exists():
        return {"version": 1, "sources": [], "versions": [], "deltas": []}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Failed to read evidence registry: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Evidence registry must be a JSON object.")
    for key in ("sources", "versions", "deltas"):
        if not isinstance(data.get(key), list):
            raise ValueError(f"Evidence registry must contain top-level '{key}' list.")
    return data


def write_registry(data: dict[str, Any]) -> None:
    """Persist the registry artifact."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def next_version_id(data: dict[str, Any]) -> str:
    """Generate the next sequential evidence version ID."""
    max_value = 0
    for entry in data.get("versions", []):
        version_id = entry.get("id", "")
        if not isinstance(version_id, str) or not version_id.startswith("ev-"):
            continue
        suffix = version_id.removeprefix("ev-")
        if suffix.isdigit():
            max_value = max(max_value, int(suffix))
    return f"ev-{max_value + 1:04d}"


def next_delta_id(data: dict[str, Any]) -> str:
    """Generate the next sequential evidence delta ID."""
    max_value = 0
    for entry in data.get("deltas", []):
        delta_id = entry.get("id", "")
        if not isinstance(delta_id, str) or not delta_id.startswith("ed-"):
            continue
        suffix = delta_id.removeprefix("ed-")
        if suffix.isdigit():
            max_value = max(max_value, int(suffix))
    return f"ed-{max_value + 1:04d}"


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Clamp a numeric value to the given range."""
    return max(minimum, min(maximum, value))


def calculate_readiness(entry: dict[str, Any]) -> dict[str, Any]:
    """Compute a deterministic readiness verdict for an evidence version."""
    confidence = float(entry.get("confidence") or 0.0)
    coverage = float(entry.get("coverage") or 0.0)
    critical_gaps = int(entry.get("critical_gaps") or 0)
    contradictions = int(entry.get("contradictions") or 0)
    user_answers_complete = bool(entry.get("user_answers_complete"))

    if contradictions > 0:
        verdict = "blocked"
        reason = "contradictions_present"
    elif critical_gaps > 0:
        verdict = "not_ready"
        reason = "critical_gaps_open"
    elif not user_answers_complete and coverage < 0.8:
        verdict = "blocked"
        reason = "missing_user_answers"
    elif confidence >= 0.8 and coverage >= 0.8:
        verdict = "ready"
        reason = "high_confidence_high_coverage"
    elif confidence >= 0.7 and coverage >= 0.7:
        verdict = "conditionally_ready"
        reason = "good_enough_with_caution"
    else:
        verdict = "not_ready"
        reason = "insufficient_confidence_or_coverage"

    return {
        "verdict": verdict,
        "reason": reason,
        "confidence": confidence,
        "coverage": coverage,
        "critical_gaps": critical_gaps,
        "contradictions": contradictions,
        "user_answers_complete": user_answers_complete,
    }


def register_version(args: argparse.Namespace) -> int:
    """Register a new evidence version entry."""
    data = load_registry()
    version_id = args.version_id or next_version_id(data)
    versions = data["versions"]
    if any(
        entry.get("id") == version_id for entry in versions if isinstance(entry, dict)
    ):
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- Version ID already exists: {version_id}\n")
        return 1

    confidence = clamp(args.confidence, 0.0, 1.0)
    coverage = clamp(args.coverage, 0.0, 1.0)
    entry: dict[str, Any] = {
        "id": version_id,
        "source_id": args.source_id,
        "source_type": args.source_type,
        "name": args.name,
        "uri": args.uri,
        "version_ref": args.version_ref,
        "version_hash": args.version_hash,
        "summary": args.summary,
        "state": args.state,
        "confidence": confidence,
        "coverage": coverage,
        "critical_gaps": args.critical_gaps,
        "important_gaps": args.important_gaps,
        "optional_gaps": args.optional_gaps,
        "contradictions": args.contradictions,
        "user_answers_complete": args.user_answers_complete,
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
    }
    versions.append(entry)
    if args.source_id and not any(
        source.get("source_id") == args.source_id
        for source in data["sources"]
        if isinstance(source, dict)
    ):
        data["sources"].append(
            {
                "source_id": args.source_id,
                "source_type": args.source_type,
                "name": args.name,
                "uri": args.uri,
                "created_at_utc": utc_now(),
                "updated_at_utc": utc_now(),
            }
        )
    write_registry(data)

    logger.info("STATUS: PASSED")
    logger.info("- Registered evidence version: %s", version_id)
    logger.info("- Registry: %s", REGISTRY_RELATIVE_PATH)
    return 0


def list_versions() -> int:
    """List evidence versions as JSON."""
    data = load_registry()
    payload = {
        "registry_path": str(REGISTRY_RELATIVE_PATH),
        "versions": data.get("versions", []),
    }
    sys.stdout.write(json.dumps(payload, indent=2) + "\n")
    return 0


def record_delta(args: argparse.Namespace) -> int:
    """Record a delta between two evidence versions."""
    data = load_registry()
    from_version = next(
        (
            entry
            for entry in data.get("versions", [])
            if isinstance(entry, dict) and entry.get("id") == args.from_version_id
        ),
        None,
    )
    to_version = next(
        (
            entry
            for entry in data.get("versions", [])
            if isinstance(entry, dict) and entry.get("id") == args.to_version_id
        ),
        None,
    )
    if from_version is None or to_version is None:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write("- Both version IDs must exist before recording a delta\n")
        return 1

    delta = {
        "id": next_delta_id(data),
        "from_version_id": args.from_version_id,
        "to_version_id": args.to_version_id,
        "delta_type": args.delta_type,
        "summary": args.summary,
        "impact": args.impact,
        "risk": args.risk,
        "decision": args.decision,
        "source_id": to_version.get("source_id") or from_version.get("source_id"),
        "created_at_utc": utc_now(),
    }
    data["deltas"].append(delta)
    write_registry(data)

    sys.stdout.write(
        json.dumps(
            {
                "registry_path": str(REGISTRY_RELATIVE_PATH),
                "delta": delta,
            },
            indent=2,
        )
        + "\n"
    )
    return 0


def readiness(args: argparse.Namespace) -> int:
    """Compute readiness for an evidence version."""
    data = load_registry()
    version = next(
        (
            entry
            for entry in data.get("versions", [])
            if isinstance(entry, dict) and entry.get("id") == args.version_id
        ),
        None,
    )
    if version is None:
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- Unknown version ID: {args.version_id}\n")
        return 1

    verdict = calculate_readiness(version)
    sys.stdout.write(
        json.dumps(
            {
                "version_id": args.version_id,
                "registry_path": str(REGISTRY_RELATIVE_PATH),
                "readiness": verdict,
            },
            indent=2,
        )
        + "\n"
    )
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.command == "register":
        return register_version(args)
    if args.command == "list":
        return list_versions()
    if args.command == "readiness":
        return readiness(args)
    if args.command == "delta":
        return record_delta(args)
    sys.stdout.write("STATUS: FAILED\n")
    sys.stdout.write(f"- Unsupported command: {args.command}\n")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
