#!/usr/bin/env python3
"""Handler for /mm:execute-milestone.

THIN handler — reads project state, emits ONE LAUNCH payload.
The milestone-executor agent handles ALL phases in background:
  discover → brains → spec → plan → execute

No polling. No sleep(). No multiple launches. Just state → payload.
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def find_project_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return Path(result.stdout.strip())
    except Exception:
        pass
    return Path(__file__).resolve().parent.parent.parent.parent


PROJECT_ROOT = find_project_root()


def mm_info(msg: str) -> None:
    print(f"INFO: {msg}", flush=True)


def mm_error(msg: str) -> None:
    print(f"ERROR: {msg}", flush=True, file=sys.stderr)


def mm_launch(agent: str, payload: dict) -> None:
    print(f"LAUNCH: {agent}", flush=True)
    print(f"PAYLOAD: {json.dumps(payload)}", flush=True)


def read_file_safe(path: Path, max_chars: int = 4000) -> str:
    if not path.exists():
        return ""
    try:
        content = path.read_text()
        if len(content) > max_chars:
            return content[:max_chars] + f"\n... [truncated at {max_chars} chars]"
        return content
    except Exception:
        return ""


def get_git_log(root: Path, n: int = 30) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def discover_project_context(root: Path) -> dict:
    """Read all relevant project files for the agent payload."""
    paths = {
        "readme": root / "README.md",
        "claude_md": root / "CLAUDE.md",
        "spec": root / "tasks" / "SPEC.md",
        "plan": root / "tasks" / "plan.md",
        "todo": root / "tasks" / "todo.md",
        "state": root / ".planning" / "STATE.md",
        "roadmap": root / ".planning" / "ROADMAP.md",
    }

    context: dict = {}
    for key, path in paths.items():
        context[f"has_{key}"] = path.exists()
        context[key] = read_file_safe(path)

    context["git_log"] = get_git_log(root)
    context["is_new_project"] = not any(
        [
            context["has_spec"],
            context["has_plan"],
            context["has_state"],
        ]
    )

    return context


def read_stack_from_config(root: Path) -> list[str]:
    config = root / ".mastermind" / "config.yaml"
    if not config.exists():
        return []
    in_stack = False
    stack: list[str] = []
    for line in config.read_text().splitlines():
        stripped = line.strip()
        if stripped == "stack:":
            in_stack = True
            continue
        if in_stack:
            if stripped.startswith("- "):
                stack.append(stripped[2:].strip())
            elif stripped and not line[0].isspace():
                break
    return stack


def main() -> None:
    if len(sys.argv) < 2:
        mm_error('Usage: execute-milestone-handler.py "<description>" [--task-id <ID>]')
        sys.exit(1)

    args = list(sys.argv[1:])

    task_id = None
    if "--task-id" in args:
        idx = args.index("--task-id")
        if idx + 1 < len(args):
            task_id = args[idx + 1]
            args = [a for i, a in enumerate(args) if i != idx and i != idx + 1]

    description = " ".join(args)

    mm_info(f"Project: {PROJECT_ROOT}")
    mm_info(f"Milestone: {description}")

    mm_info("Reading project context...")
    context = discover_project_context(PROJECT_ROOT)

    mode = "new" if context["is_new_project"] else "existing"

    if mode == "new":
        mm_info("Mode: NEW PROJECT — spec + plan + execute from scratch")
    else:
        mm_info("Mode: EXISTING PROJECT — audit gaps, update plan, execute")
        for key in ("spec", "plan", "state", "roadmap"):
            if context[f"has_{key}"]:
                mm_info(f"  ✓ {key} found")

    payload = {
        "description": description,
        "task_id": task_id,
        "mode": mode,
        "working_directory": str(PROJECT_ROOT),
        "stack": read_stack_from_config(PROJECT_ROOT),
        "project_context": context,
        "session_id": f"ms-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }

    mm_launch("milestone-executor", payload)


if __name__ == "__main__":
    main()
