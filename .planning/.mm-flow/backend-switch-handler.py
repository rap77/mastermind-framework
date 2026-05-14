#!/usr/bin/env python3
"""
backend-switch-handler.py — Automatic backend switch on token depletion.

C2.14: Called at startup of complete-task-handler.py (or by task-executor).
       Reads BACKEND-SWITCH-REQUIRED.json — if it exists:
       - Updates ACTIVE_BACKEND in ACTIVE-BACKEND.json to the next provider
       - Deletes the BACKEND-SWITCH-REQUIRED.json signal file

C2.15: Writes/updates ACTIVE-BACKEND.json with the current active backend.
       This file is the single source of truth for the JS hooks.

Usage:
    python3 .planning/.mm-flow/backend-switch-handler.py [--check] [--status]

Exit codes:
    0 — no switch needed or switch applied successfully
    1 — error reading/writing files
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_SCRIPT_DIR = Path(__file__).resolve().parent
_REPO_ROOT = _SCRIPT_DIR.parent.parent
_PLANNING_DIR = _REPO_ROOT / ".planning"

BACKEND_SWITCH_REQUIRED_PATH = _PLANNING_DIR / "BACKEND-SWITCH-REQUIRED.json"
ACTIVE_BACKEND_PATH = _PLANNING_DIR / "ACTIVE-BACKEND.json"

# Priority order: try z_ai first (cheapest), then openrouter, then claude (most expensive)
# C2.14 spec: "z_ai → openrouter → claude"
_PRIORITY_ORDER = ["z_ai", "openrouter", "claude"]


# ---------------------------------------------------------------------------
# Core logic
# ---------------------------------------------------------------------------


def read_active_backend() -> str:
    """Read active backend from ACTIVE-BACKEND.json. Default: 'claude'."""
    try:
        data = json.loads(ACTIVE_BACKEND_PATH.read_text())
        return data.get("active_backend", "claude")
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return "claude"


def write_active_backend(backend: str, reason: str = "startup") -> None:
    """Write ACTIVE-BACKEND.json with the given backend name (C2.15).

    This file is the single source of truth for the JS hooks and Python handlers.
    Written atomically via temp file + rename on POSIX systems.

    Args:
        backend: Active backend identifier (e.g. "claude", "openrouter", "z_ai").
        reason: Human-readable reason for the update (for audit trail).
    """
    data = {
        "active_backend": backend,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
    }
    _PLANNING_DIR.mkdir(parents=True, exist_ok=True)
    tmp = ACTIVE_BACKEND_PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(data, indent=2) + "\n")
    tmp.rename(ACTIVE_BACKEND_PATH)
    print(f"INFO: ACTIVE-BACKEND.json updated → {backend} (reason: {reason})")


def get_next_backend(current: str) -> str | None:
    """Return next backend in priority order, or None if at end of list.

    C2.14 spec: z_ai → openrouter → claude
    """
    try:
        idx = _PRIORITY_ORDER.index(current)
        if idx < len(_PRIORITY_ORDER) - 1:
            return _PRIORITY_ORDER[idx + 1]
    except ValueError:
        pass
    return None


def check_and_apply_switch() -> bool:
    """Check for BACKEND-SWITCH-REQUIRED.json and apply switch if present.

    C2.14 spec:
    - If BACKEND-SWITCH-REQUIRED.json exists:
        1. Read next_backend from the file
        2. Update ACTIVE-BACKEND.json to next_backend
        3. Delete BACKEND-SWITCH-REQUIRED.json signal
    - If not present: ensure ACTIVE-BACKEND.json exists (C2.15 invariant)

    Returns:
        True if a switch was applied, False otherwise.
    """
    if not BACKEND_SWITCH_REQUIRED_PATH.exists():
        # Ensure ACTIVE-BACKEND.json exists (C2.15 invariant)
        if not ACTIVE_BACKEND_PATH.exists():
            write_active_backend("claude", "initial_setup")
        return False

    # Read the switch signal
    try:
        signal = json.loads(BACKEND_SWITCH_REQUIRED_PATH.read_text())
    except (json.JSONDecodeError, OSError) as exc:
        print(
            f"ERROR: Failed to read BACKEND-SWITCH-REQUIRED.json: {exc}",
            file=sys.stderr,
        )
        return False

    current_backend = signal.get("current_backend", "claude")
    next_backend = signal.get("next_backend") or get_next_backend(current_backend)
    signal_reason = signal.get("reason", "token_depletion")

    if not next_backend:
        print(
            f"WARNING: No next backend available after '{current_backend}' — staying on current",
            file=sys.stderr,
        )
        # Still clean up the signal file to avoid looping
        BACKEND_SWITCH_REQUIRED_PATH.unlink(missing_ok=True)
        return False

    # Apply the switch
    print(
        f"INFO: Backend switch triggered: {current_backend} → {next_backend} ({signal_reason})"
    )
    write_active_backend(next_backend, f"switch_from_{current_backend}_{signal_reason}")

    # Delete the signal file (C2.14: "borra el archivo signal")
    try:
        BACKEND_SWITCH_REQUIRED_PATH.unlink()
        print("INFO: BACKEND-SWITCH-REQUIRED.json deleted")
    except OSError as exc:
        print(f"WARNING: Could not delete signal file: {exc}", file=sys.stderr)

    return True


def show_status() -> None:
    """Print current backend status."""
    active = read_active_backend()
    switch_pending = BACKEND_SWITCH_REQUIRED_PATH.exists()
    print(f"STATUS: active_backend={active}")
    print(f"STATUS: switch_pending={switch_pending}")
    if ACTIVE_BACKEND_PATH.exists():
        try:
            data = json.loads(ACTIVE_BACKEND_PATH.read_text())
            print(f"STATUS: updated_at={data.get('updated_at', 'unknown')}")
            print(f"STATUS: reason={data.get('reason', 'unknown')}")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 = success, 1 = error).
    """
    args = sys.argv[1:]

    if "--status" in args:
        show_status()
        return 0

    if "--check" in args:
        # Just check, don't apply
        if BACKEND_SWITCH_REQUIRED_PATH.exists():
            signal = json.loads(BACKEND_SWITCH_REQUIRED_PATH.read_text())
            print(
                f"INFO: Switch pending: {signal.get('current_backend')} → {signal.get('next_backend')}"
            )
        else:
            print("INFO: No backend switch pending")
        return 0

    # Default: check and apply
    check_and_apply_switch()
    return 0


if __name__ == "__main__":
    sys.exit(main())
