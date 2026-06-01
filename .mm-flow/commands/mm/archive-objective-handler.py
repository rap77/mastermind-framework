#!/usr/bin/env python3
"""Archive a completed objective package from .mm-flow/planning/changes to archive/objectives."""

from __future__ import annotations

import json
import shutil
import subprocess
from argparse import ArgumentParser, Namespace
from datetime import datetime
from pathlib import Path


def project_root() -> Path:
    """Find project root via git, fallback to file-relative path."""
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
PLANNING_DIR = ROOT / ".mm-flow" / "planning"
CHANGES_DIR = PLANNING_DIR / "changes"
ARCHIVE_OBJECTIVES_DIR = PLANNING_DIR / "archive" / "objectives"
GLOBAL_HANDOFF = PLANNING_DIR / "HANDOFF-CURRENT.md"
RUNTIME_STATE_PATH = PLANNING_DIR / "task-progress.json"
REQUIRED_OBJECTIVE_FILES = (
    "requirements.md",
    "design.md",
    "tasks.md",
    "todo.md",
    "HANDOFF-CURRENT.md",
    "execution-state.json",
)


def parse_args() -> Namespace:
    """Parse CLI args."""
    parser = ArgumentParser(description="Archive a completed objective package.")
    parser.add_argument(
        "--objective",
        default=None,
        help="Objective slug under .mm-flow/planning/changes/<objective>.",
    )
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Only print the archive decision/result without moving files.",
    )
    return parser.parse_args()


def infer_objective() -> str | None:
    """Infer the active objective, preferring the current changes directory state.

    Resolution order:
    1. If exactly one objective exists under `.mm-flow/planning/changes/`, use it.
    2. Otherwise, if global handoff points at an objective that still exists in
       `.mm-flow/planning/changes/`, use that.
    3. Otherwise return None and require explicit `--objective`.
    """
    if CHANGES_DIR.exists():
        dirs = sorted(path.name for path in CHANGES_DIR.iterdir() if path.is_dir())
        if len(dirs) == 1:
            return dirs[0]

    if GLOBAL_HANDOFF.exists():
        text = GLOBAL_HANDOFF.read_text(encoding="utf-8")
        import re

        match = re.search(r"`([^`]+)`", text)
        if match:
            candidate = match.group(1).strip()
            if (CHANGES_DIR / candidate).exists():
                return candidate

    return None


def load_execution_state(objective_dir: Path) -> dict | None:
    """Load objective execution-state.json if present."""
    path = objective_dir / "execution-state.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def load_runtime_state() -> dict | None:
    """Load active runtime state when present."""
    if not RUNTIME_STATE_PATH.exists():
        return None
    try:
        return json.loads(RUNTIME_STATE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def required_files_present(objective_dir: Path) -> tuple[bool, list[str]]:
    """Return whether the required objective artifacts are present."""
    missing = [
        filename
        for filename in REQUIRED_OBJECTIVE_FILES
        if not (objective_dir / filename).exists()
    ]
    return not missing, missing


def runtime_allows_archive(objective: str) -> tuple[bool, str]:
    """Ensure the active runtime session is not still open for this objective."""
    runtime_state = load_runtime_state()
    if runtime_state is None:
        return True, "no active runtime state found"

    runtime_slug = runtime_state.get("objective_slug")
    if runtime_slug != objective:
        return True, "runtime state belongs to another objective"

    subtasks = runtime_state.get("subtasks", {})
    if subtasks and all(
        subtask.get("status") == "completed" for subtask in subtasks.values()
    ):
        return True, "runtime subtasks are fully completed"

    runtime_task = runtime_state.get("task_id", "unknown")
    return False, f"runtime task {runtime_task} is still incomplete"


def is_completed(objective_dir: Path) -> tuple[bool, str]:
    """Return completion status and reason."""
    state = load_execution_state(objective_dir)
    if state and state.get("tasks"):
        statuses = [task.get("status", "pending") for task in state["tasks"].values()]
        if statuses and all(status == "completed" for status in statuses):
            return True, "execution-state.json shows all root tasks completed"
        return False, "execution-state.json still has pending/in-progress root tasks"

    handoff_path = objective_dir / "HANDOFF-CURRENT.md"
    if handoff_path.exists():
        text = handoff_path.read_text(encoding="utf-8")
        if (
            "**COMPLETE**" in text
            or "objective package has no pending root tasks" in text
        ):
            return True, "handoff indicates objective complete"
    return False, "objective completion could not be proven"


def archive_safety(objective: str, objective_dir: Path) -> tuple[bool, str]:
    """Run full archive safety validation for an objective package."""
    files_ok, missing = required_files_present(objective_dir)
    if not files_ok:
        return False, f"missing required objective files: {', '.join(missing)}"

    completed, completion_reason = is_completed(objective_dir)
    if not completed:
        return False, completion_reason

    runtime_ok, runtime_reason = runtime_allows_archive(objective)
    if not runtime_ok:
        return False, runtime_reason

    return True, completion_reason


def mark_objective_done_in_roadmap(objective: str) -> None:
    """Update objectives.json to reflect the objective is now done."""
    import re as _re

    objectives_json = PLANNING_DIR / "roadmap" / "objectives.json"
    if objectives_json.exists():
        try:
            data = json.loads(objectives_json.read_text(encoding="utf-8"))
            # Support both formats: bare list OR {"objectives": [...], ...} dict
            entries: list = (
                data if isinstance(data, list) else data.get("objectives", [])
            )
            changed = False
            for entry in entries:
                if (
                    entry.get("stable_id") == objective
                    or entry.get("slug") == objective
                    or entry.get("id") == objective
                ):
                    entry["status"] = "done"
                    entry["ready_now"] = False
                    entry["recommended_next"] = False
                    changed = True
                    break
            if changed:
                # Promote the highest-priority planned+ready objective as recommended_next
                candidates = [
                    o
                    for o in entries
                    if o.get("status") == "planned" and o.get("ready_now", False)
                ]
                if candidates:
                    next_obj = min(candidates, key=lambda o: o.get("rank", 9999))
                    next_obj["recommended_next"] = True
                objectives_json.write_text(
                    json.dumps(data, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8",
                )
        except (json.JSONDecodeError, OSError, AttributeError):
            pass

    objectives_md = PLANNING_DIR / "roadmap" / "objectives.md"
    if objectives_md.exists():
        try:
            text = objectives_md.read_text(encoding="utf-8")
            text = _re.sub(
                rf"(\| \d+ \| `{_re.escape(objective)}` \| )planned(\b)",
                r"\1done\2",
                text,
            )
            objectives_md.write_text(text, encoding="utf-8")
        except OSError:
            pass


def find_next_objective() -> dict | None:
    """Return the highest-priority planned+ready objective from objectives.json."""
    objectives_json = PLANNING_DIR / "roadmap" / "objectives.json"
    if not objectives_json.exists():
        return None
    try:
        data = json.loads(objectives_json.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
    candidates = [
        o for o in data if o.get("status") == "planned" and o.get("ready_now", False)
    ]
    if not candidates:
        return None
    return min(candidates, key=lambda o: o.get("rank", 9999))


def update_global_handoff(archived_objective: str) -> None:
    """Rewrite root HANDOFF-CURRENT.md after archiving an objective."""
    next_obj = find_next_objective()
    if next_obj:
        slug = next_obj.get("slug") or next_obj.get("stable_id", "unknown")
        name = next_obj.get("name", slug)
        summary = next_obj.get("summary", "")
        content = "\n".join(
            [
                "# Handoff — no active objective",
                "",
                "## Last archived",
                f"- `{archived_objective}` — archived at {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Next recommended objective",
                f"- `{slug}` — {name}",
                f"- {summary}",
                "",
                "## Next command",
                "- `/mm:activate-next-objective`",
                "",
            ]
        )
    else:
        content = "\n".join(
            [
                "# Handoff — no active objective",
                "",
                "## Last archived",
                f"- `{archived_objective}` — archived at {datetime.now().isoformat(timespec='seconds')}",
                "",
                "## Next command",
                "- No planned objectives remaining. Review roadmap.",
                "",
            ]
        )
    GLOBAL_HANDOFF.write_text(content, encoding="utf-8")


def write_completion_summary(
    objective_dir: Path, archive_dir: Path, reason: str
) -> None:
    """Write completion summary into the archived objective package."""
    handoff_path = archive_dir / "HANDOFF-CURRENT.md"
    summary_path = archive_dir / "COMPLETION-SUMMARY.md"
    handoff_excerpt = ""
    if handoff_path.exists():
        handoff_excerpt = handoff_path.read_text(encoding="utf-8").strip()
    summary = "\n".join(
        [
            f"# Completion Summary — {archive_dir.name}",
            "",
            f"- Archived at: {datetime.now().isoformat(timespec='seconds')}",
            f"- Completion basis: {reason}",
            f"- Source moved from: {objective_dir}",
            "",
            "## Handoff Snapshot",
            handoff_excerpt or "- No handoff snapshot available.",
            "",
        ]
    )
    summary_path.write_text(summary, encoding="utf-8")


def main() -> int:
    """Archive a completed objective package."""
    args = parse_args()
    objective = args.objective or infer_objective()
    if not objective:
        print("STATUS: FAILED")
        print("- Could not infer objective. Pass --objective <slug>.")
        return 1

    objective_dir = CHANGES_DIR / objective
    if not objective_dir.exists():
        print("STATUS: FAILED")
        print(f"- Active objective package missing: {objective_dir}")
        return 1

    completed, reason = archive_safety(objective, objective_dir)
    if not completed:
        print("STATUS: FAILED")
        print(f"- Objective `{objective}` is not archive-safe: {reason}")
        return 1

    archive_dir = ARCHIVE_OBJECTIVES_DIR / objective
    if archive_dir.exists():
        print("STATUS: FAILED")
        print(f"- Archive destination already exists: {archive_dir}")
        return 1

    print("STATUS: PASSED")
    print(f"- Objective `{objective}` is archive-safe: {reason}")
    if args.summary_only:
        return 0

    ARCHIVE_OBJECTIVES_DIR.mkdir(parents=True, exist_ok=True)
    shutil.move(str(objective_dir), str(archive_dir))
    write_completion_summary(objective_dir, archive_dir, reason)
    mark_objective_done_in_roadmap(objective)
    update_global_handoff(objective)
    print(f"- Archived to: {archive_dir}")

    next_obj = find_next_objective()
    if next_obj:
        slug = next_obj.get("slug") or next_obj.get("stable_id", "unknown")
        print(f"NEXT_COMMAND: /mm:activate-next-objective  # next: {slug}")
    else:
        print("NEXT_COMMAND: none — no planned objectives remaining")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
