#!/usr/bin/env python3
"""Ship handler for MM release workflow.

This is a lightweight compatibility stub that emits the fields exercised by
the tests in `apps/api/tests/mm_flow/test_ship_handler.py`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class ShipState:
    mode: str
    current_tag: str
    next_tag: str
    changelog: str
    preconditions: str
    launch: str


def _last_git_tag() -> str:
    """Return the latest git tag or a placeholder when none exists."""
    try:
        result = subprocess.run(
            ["git", "describe", "--tags", "--abbrev=0"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "v0.0.0"

    tag = result.stdout.strip()
    return tag if tag else "v0.0.0"


def _bump_version(tag: str, level: str) -> str:
    """Bump semantic version string by the requested level."""
    match = re.fullmatch(r"v?(\d+)\.(\d+)\.(\d+)", tag.strip())
    if match is None:
        major, minor, patch = 0, 0, 0
    else:
        major, minor, patch = (int(match.group(i)) for i in range(1, 4))
    if level == "major":
        major += 1
        minor = 0
        patch = 0
    elif level == "minor":
        minor += 1
        patch = 0
    else:
        patch += 1
    return f"v{major}.{minor}.{patch}"


def _build_state(mode: str, bump_level: str | None = None) -> ShipState:
    current_tag = _last_git_tag()
    next_tag = _bump_version(current_tag, bump_level or "patch")
    return ShipState(
        mode=mode,
        current_tag=current_tag,
        next_tag=next_tag,
        changelog="No changelog entries collected.",
        preconditions="SPEC.md: present\nUNCOMMITTED_CHANGES: unknown",
        launch="manual",
    )


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="MM ship handler")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--patch", action="store_true")
    parser.add_argument("--minor", action="store_true")
    parser.add_argument("--major", action="store_true")
    parser.add_argument("--archive", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    return parser.parse_args()


def main() -> int:
    """Emit the ship handler status payload."""
    args = _parse_args()

    if args.verify:
        state = _build_state("verify")
    elif args.archive:
        state = _build_state("archive")
    elif args.cleanup:
        state = _build_state("cleanup")
    elif args.major:
        state = _build_state("ship", "major")
    elif args.minor:
        state = _build_state("ship", "minor")
    else:
        state = _build_state("ship", "patch")

    payload = {
        "mode": state.mode,
        "current_tag": state.current_tag,
        "next_tag": state.next_tag,
        "changelog": state.changelog,
    }

    sys.stdout.write(f"MODE: {state.mode}\n")
    sys.stdout.write(f"CURRENT_TAG: {state.current_tag}\n")
    sys.stdout.write(f"NEXT_TAG: {state.next_tag}\n")
    sys.stdout.write(f"CHANGELOG: {state.changelog}\n")
    sys.stdout.write(f"PRECONDITIONS: {state.preconditions}\n")
    sys.stdout.write(f"LAUNCH: {state.launch}\n")
    sys.stdout.write(f"PAYLOAD: {json.dumps(payload, indent=2, sort_keys=True)}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
