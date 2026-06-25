#!/usr/bin/env python3
"""Manage the MasterMind harness gap registry artifact."""

from __future__ import annotations

import argparse
import json
import logging
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from planning_paths import get_planning_dir, planning_relpath

OPEN_STATUSES = {"open", "deferred"}
READINESS_PRIORITY = {"ready": 3, "needs_more_evidence": 2, "blocked": 1}
IMPACT_PRIORITY = {"high": 3, "medium": 2, "low": 1}
URGENCY_PRIORITY = {"high": 3, "medium": 2, "low": 1}
logger = logging.getLogger(__name__)


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
REGISTRY_PATH = PLANNING_DIR / "gaps" / "gap-registry.json"
REGISTRY_RELATIVE_PATH = REGISTRY_PATH.relative_to(ROOT)
ARCHIVE_OBJECTIVES_PATH = PLANNING_DIR / "archive" / "objectives"
CHANGES_OBJECTIVES_PATH = PLANNING_DIR / "changes"


def parse_args() -> argparse.Namespace:
    """Parse CLI arguments."""
    parser = argparse.ArgumentParser(description="Manage the MM gap registry.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    register_parser = subparsers.add_parser("register", help="Register a new gap.")
    register_parser.add_argument("--id", dest="gap_id")
    register_parser.add_argument("--title", required=True)
    register_parser.add_argument("--detected-from", required=True)
    register_parser.add_argument("--objective-slug")
    register_parser.add_argument("--evidence", action="append", required=True)
    register_parser.add_argument(
        "--impact",
        choices=["low", "medium", "high"],
        default="medium",
    )
    register_parser.add_argument(
        "--urgency",
        choices=["low", "medium", "high"],
        default="medium",
    )
    register_parser.add_argument("--suggested-followup")
    register_parser.add_argument(
        "--promotion-readiness",
        choices=["ready", "needs_more_evidence", "blocked"],
        default="needs_more_evidence",
    )
    register_parser.add_argument(
        "--status",
        choices=["open", "deferred"],
        default="open",
    )

    list_parser = subparsers.add_parser("list", help="List gaps from the registry.")
    list_parser.add_argument(
        "--all",
        action="store_true",
        help="Include promoted and closed gaps.",
    )

    promote_parser = subparsers.add_parser(
        "promote", help="Mark a gap as promoted to an objective."
    )
    promote_parser.add_argument("--id", dest="gap_id", required=True)
    promote_parser.add_argument("--objective-slug", required=True)

    subparsers.add_parser(
        "duplicates",
        help="Show possible duplicate gaps using deterministic fingerprints.",
    )
    subparsers.add_parser(
        "next",
        help="Show the next recommended open gap using deterministic priority.",
    )
    sync_parser = subparsers.add_parser(
        "sync-objective",
        help="Synchronize a gap entry against exact objective artifact presence.",
    )
    sync_parser.add_argument("--objective-slug", required=True)
    prepare_parser = subparsers.add_parser(
        "prepare-promotion",
        help="Validate one gap and emit the next command to promote it safely.",
    )
    prepare_parser.add_argument("--id", dest="gap_id", required=True)

    return parser.parse_args()


def load_registry() -> dict[str, Any]:
    """Load the gap registry, creating a default shape when needed."""
    if not REGISTRY_PATH.exists():
        return {"version": 1, "gaps": []}
    try:
        data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise ValueError(f"Failed to read gap registry: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("Gap registry must be a JSON object.")
    gaps = data.get("gaps")
    if not isinstance(gaps, list):
        raise ValueError("Gap registry must contain a top-level 'gaps' list.")
    return data


def write_registry(data: dict[str, Any]) -> None:
    """Persist the registry artifact."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def utc_now() -> str:
    """Return an ISO8601 UTC timestamp."""
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_gap_text(value: Any) -> str:
    """Normalize free text into a deterministic comparison fingerprint."""
    if not isinstance(value, str):
        return ""
    collapsed = re.sub(r"[^a-z0-9]+", " ", value.lower())
    return " ".join(collapsed.split())


def open_gap_entries(data: dict[str, Any]) -> list[dict[str, Any]]:
    """Return open or deferred gap entries in registry order."""
    return [
        entry
        for entry in data.get("gaps", [])
        if isinstance(entry, dict) and entry.get("status") in OPEN_STATUSES
    ]


def gap_priority_sort_key(entry: dict[str, Any]) -> tuple[int, int, int, str, str]:
    """Build a deterministic sort key for open gaps."""
    return (
        -READINESS_PRIORITY.get(str(entry.get("promotion_readiness")), 0),
        -IMPACT_PRIORITY.get(str(entry.get("impact")), 0),
        -URGENCY_PRIORITY.get(str(entry.get("urgency")), 0),
        str(entry.get("created_at_utc") or ""),
        str(entry.get("id") or ""),
    )


def duplicate_suspects(gaps: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Compute read-only duplicate suspects for open gaps."""
    seen_pairs: set[tuple[str, str]] = set()
    suspects: list[dict[str, Any]] = []
    for index, left in enumerate(gaps):
        left_id = str(left.get("id") or "")
        left_title = normalize_gap_text(left.get("title"))
        left_followup = normalize_gap_text(left.get("suggested_followup"))
        for right in gaps[index + 1 :]:
            right_id = str(right.get("id") or "")
            right_title = normalize_gap_text(right.get("title"))
            right_followup = normalize_gap_text(right.get("suggested_followup"))
            reasons: list[str] = []
            if left_followup and left_followup == right_followup:
                reasons.append("same_suggested_followup")
            if left_title and left_title == right_title:
                reasons.append("same_normalized_title")
            if not reasons:
                continue
            pair_key = tuple(sorted((left_id, right_id)))
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)
            suspects.append(
                {
                    "gap_ids": [left_id, right_id],
                    "reasons": reasons,
                    "shared_suggested_followup": left.get("suggested_followup")
                    if "same_suggested_followup" in reasons
                    else None,
                    "shared_normalized_title": left_title
                    if "same_normalized_title" in reasons
                    else None,
                }
            )
    return suspects


def next_gap_id(data: dict[str, Any]) -> str:
    """Generate the next sequential gap ID."""
    max_value = 0
    for entry in data.get("gaps", []):
        gap_id = entry.get("id", "")
        if not isinstance(gap_id, str):
            continue
        if not gap_id.startswith("gap-"):
            continue
        suffix = gap_id.removeprefix("gap-")
        if suffix.isdigit():
            max_value = max(max_value, int(suffix))
    return f"gap-{max_value + 1:04d}"


def register_gap(args: argparse.Namespace) -> int:
    """Register a new gap entry."""
    data = load_registry()
    gap_id = args.gap_id or next_gap_id(data)
    gaps = data["gaps"]
    if any(entry.get("id") == gap_id for entry in gaps if isinstance(entry, dict)):
        sys.stdout.write("STATUS: FAILED\n")
        sys.stdout.write(f"- Gap ID already exists: {gap_id}\n")
        return 1

    entry: dict[str, Any] = {
        "id": gap_id,
        "title": args.title,
        "status": args.status,
        "detected_from": args.detected_from,
        "objective_slug": args.objective_slug,
        "evidence": args.evidence,
        "impact": args.impact,
        "urgency": args.urgency,
        "suggested_followup": args.suggested_followup,
        "promotion_readiness": args.promotion_readiness,
        "promoted_objective_slug": None,
        "created_at_utc": utc_now(),
        "updated_at_utc": utc_now(),
    }
    gaps.append(entry)
    write_registry(data)

    logger.info("STATUS: PASSED")
    logger.info("- Registered gap: %s", gap_id)
    logger.info("- Registry: %s", REGISTRY_RELATIVE_PATH)
    return 0


def list_gaps(args: argparse.Namespace) -> int:
    """List gap entries."""
    data = load_registry()
    gaps = [entry for entry in data["gaps"] if isinstance(entry, dict)]
    if not args.all:
        gaps = open_gap_entries(data)
    payload = {"version": data.get("version", 1), "gaps": gaps}
    logger.info("%s", json.dumps(payload, indent=2))
    return 0


def promote_gap(args: argparse.Namespace) -> int:
    """Mark a gap as promoted to an objective slug."""
    data = load_registry()
    for entry in data["gaps"]:
        if not isinstance(entry, dict):
            continue
        if entry.get("id") != args.gap_id:
            continue
        entry["status"] = "promoted"
        entry["promoted_objective_slug"] = args.objective_slug
        entry["updated_at_utc"] = utc_now()
        write_registry(data)
        logger.info("STATUS: PASSED")
        logger.info("- Promoted gap: %s", args.gap_id)
        logger.info("- Objective slug: %s", args.objective_slug)
        return 0

    logger.error("STATUS: FAILED")
    logger.error("- Gap ID not found: %s", args.gap_id)
    return 1


def list_duplicate_suspects() -> int:
    """Print duplicate-suspect relationships for open gaps."""
    data = load_registry()
    gaps = open_gap_entries(data)
    payload = {
        "version": data.get("version", 1),
        "suspects": duplicate_suspects(gaps),
    }
    logger.info("%s", json.dumps(payload, indent=2))
    return 0


def recommend_next_gap() -> int:
    """Print the next recommended open gap using deterministic priority."""
    data = load_registry()
    ranked = sorted(open_gap_entries(data), key=gap_priority_sort_key)
    payload = {
        "version": data.get("version", 1),
        "recommended_gap": ranked[0] if ranked else None,
        "ranked_open_gaps": ranked,
    }
    logger.info("%s", json.dumps(payload, indent=2))
    return 0


def objective_lifecycle_status(objective_slug: str) -> str | None:
    """Infer lifecycle status from exact objective artifact presence."""
    if (ARCHIVE_OBJECTIVES_PATH / objective_slug).exists():
        return "resolved"
    if (CHANGES_OBJECTIVES_PATH / objective_slug).exists():
        return "promoted"
    return None


def objective_display_name_from_gap(entry: dict[str, Any]) -> str:
    """Return a deterministic objective display name for discover commands."""
    title = entry.get("title")
    if isinstance(title, str) and title.strip():
        return title.strip()
    suggested_followup = str(entry.get("suggested_followup") or "")
    words = suggested_followup.replace("-", " ").replace("_", " ").split()
    return " ".join(word.capitalize() for word in words)


def sync_objective(args: argparse.Namespace) -> int:
    """Synchronize a matching gap entry against exact objective artifacts."""
    target_status = objective_lifecycle_status(args.objective_slug)
    if target_status is None:
        logger.error("STATUS: FAILED")
        logger.error(
            "- Objective artifacts not found for slug: %s", args.objective_slug
        )
        return 1

    data = load_registry()
    for entry in data["gaps"]:
        if not isinstance(entry, dict):
            continue
        if entry.get("suggested_followup") != args.objective_slug:
            continue
        entry["status"] = target_status
        entry["promoted_objective_slug"] = args.objective_slug
        entry["updated_at_utc"] = utc_now()
        write_registry(data)
        logger.info("STATUS: PASSED")
        logger.info("- Synchronized gap: %s", entry.get("id"))
        logger.info("- Objective slug: %s", args.objective_slug)
        logger.info("- New status: %s", target_status)
        return 0

    logger.error("STATUS: FAILED")
    logger.error("- No gap found for suggested_followup: %s", args.objective_slug)
    return 1


def prepare_promotion(args: argparse.Namespace) -> int:
    """Validate a gap and emit the exact next command for objective materialization."""
    data = load_registry()
    for entry in data["gaps"]:
        if not isinstance(entry, dict):
            continue
        if entry.get("id") != args.gap_id:
            continue

        if entry.get("status") not in OPEN_STATUSES:
            logger.error("STATUS: FAILED")
            logger.error(
                "- Gap is not promotion-eligible from status: %s", entry.get("status")
            )
            return 1

        if entry.get("promotion_readiness") != "ready":
            logger.error("STATUS: FAILED")
            logger.error(
                "- Gap is not promotion-ready: %s", entry.get("promotion_readiness")
            )
            return 1

        objective_slug = str(entry.get("suggested_followup") or "").strip()
        if not objective_slug:
            logger.error("STATUS: FAILED")
            logger.error("- Gap has no suggested_followup objective slug.")
            return 1

        lifecycle_status = objective_lifecycle_status(objective_slug)
        if lifecycle_status == "promoted":
            logger.error("STATUS: FAILED")
            logger.error("- Objective already exists in changes/: %s", objective_slug)
            return 1
        if lifecycle_status == "resolved":
            logger.error("STATUS: FAILED")
            logger.error("- Objective already exists in archive/: %s", objective_slug)
            return 1

        objective_name = objective_display_name_from_gap(entry)
        command = (
            f'/mm:discover --existing --objective {objective_slug} "{objective_name}"'
        )
        logger.info("STATUS: PASSED")
        logger.info("GAP_ID: %s", entry.get("id"))
        logger.info("OBJECTIVE_SLUG: %s", objective_slug)
        logger.info("OBJECTIVE_NAME: %s", objective_name)
        logger.info("NEXT_COMMAND: %s", command)
        return 0

    logger.error("STATUS: FAILED")
    logger.error("- Gap ID not found: %s", args.gap_id)
    return 1


def main() -> int:
    """Run the CLI."""
    args = parse_args()
    if args.command == "register":
        return register_gap(args)
    if args.command == "list":
        return list_gaps(args)
    if args.command == "promote":
        return promote_gap(args)
    if args.command == "duplicates":
        return list_duplicate_suspects()
    if args.command == "next":
        return recommend_next_gap()
    if args.command == "sync-objective":
        return sync_objective(args)
    if args.command == "prepare-promotion":
        return prepare_promotion(args)
    logger.error("STATUS: FAILED")
    logger.error("- Unsupported command: %s", args.command)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
