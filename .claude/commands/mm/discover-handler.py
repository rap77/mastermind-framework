#!/usr/bin/env python3
"""
MasterMind Discovery Handler

Analyzes ideas or audits existing projects to generate SPEC.md, plan.md, and todo.md.
"""

import argparse
import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def parse_args():
    parser = argparse.ArgumentParser(
        description="Discover and plan: from idea to actionable tasks"
    )
    parser.add_argument(
        "idea", nargs="?", help="Project idea (for new projects)", default=None
    )
    parser.add_argument(
        "--existing",
        action="store_true",
        help="Audit existing project instead of new idea",
    )
    parser.add_argument(
        "--mode",
        choices=["fast", "deep"],
        default="fast",
        help="Discovery mode: fast (15min) or deep (60min)",
    )
    parser.add_argument(
        "--health", action="store_true", help="Health check only (existing mode)"
    )
    parser.add_argument(
        "--gaps", action="store_true", help="Gap analysis only (existing mode)"
    )
    parser.add_argument(
        "--replan",
        action="store_true",
        help="Re-plan with current gaps (existing mode)",
    )

    return parser.parse_args()


def read_context_files(root_dir: Path) -> dict:
    """Read context files for existing projects."""
    context = {
        "root": str(root_dir),
        "has_readme": False,
        "has_claude_md": False,
        "has_plan": False,
        "has_todo": False,
        "has_planning": False,
        "has_spec": False,
        "git_status": None,
    }

    # Check files
    files_to_check = {
        "README.md": "has_readme",
        "CLAUDE.md": "has_claude_md",
        "tasks/plan.md": "has_plan",
        "tasks/todo.md": "has_todo",
        "SPEC.md": "has_spec",
    }

    for file_path, key in files_to_check.items():
        full_path = root_dir / file_path
        if full_path.exists():
            context[key] = True

    # Check .planning directory
    planning_dir = root_dir / ".planning"
    if planning_dir.exists() and any(planning_dir.iterdir()):
        context["has_planning"] = True

    # Get git status
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        context["git_status"] = result.stdout.strip()
    except Exception:
        pass

    # Get recent commits
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", "-10"],
            cwd=root_dir,
            capture_output=True,
            text=True,
            timeout=10,
        )
        context["recent_commits"] = result.stdout.strip()
    except Exception:
        context["recent_commits"] = ""

    return context


def generate_new_project_payload(idea: str, mode: str) -> dict:
    """Generate payload for new project discovery."""
    return {
        "mode": "new",
        "idea": idea,
        "discovery_mode": mode,
        "working_dir": "/home/rpadron/proy/mastermind",
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-new-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def generate_existing_project_payload(context: dict, options: dict) -> dict:
    """Generate payload for existing project audit."""
    return {
        "mode": "existing",
        "context": context,
        "options": options,
        "working_dir": "/home/rpadron/proy/mastermind",
        "timestamp": datetime.now().isoformat(),
        "session_id": f"discover-existing-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
    }


def main():
    args = parse_args()
    root_dir = Path.cwd()

    # Validate: --existing requires existing files
    if args.existing:
        context = read_context_files(root_dir)
        if not any(
            [context["has_readme"], context["has_claude_md"], context["has_plan"]]
        ):
            print(
                "ERROR: No project context found (README.md, CLAUDE.md, or tasks/plan.md required for --existing mode)"
            )
            sys.exit(1)

        # Determine agent type based on options
        if args.health:
            agent_type = "health-checker"
        elif args.gaps:
            agent_type = "gap-analyzer"
        elif args.replan:
            agent_type = "re-planner"
        else:
            agent_type = "rediscovery-auditor"

        payload = generate_existing_project_payload(
            context,
            {
                "health": args.health,
                "gaps": args.gaps,
                "replan": args.replan,
                "mode": args.mode,
            },
        )

        print("MODE: existing")
        print(f"TASK: {agent_type}")
        print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
        print("LAUNCH: discover-agent")
        print()
        print("INFO: Auditing existing project...")
        print(f"INFO: Session ID: {payload['session_id']}")

    else:
        # New project mode
        if not args.idea:
            print("ERROR: Idea required for new project mode")
            print('Usage: /mm:discover "<your idea>"')
            sys.exit(1)

        payload = generate_new_project_payload(args.idea, args.mode)

        print("MODE: new")
        print("TASK: discover-planner")
        print(f"PAYLOAD: {json.dumps(payload, indent=2)}")
        print("LAUNCH: discover-agent")
        print()
        print("INFO: Discovering new project idea...")
        print(f"INFO: Idea: {args.idea[:100]}...")
        print(f"INFO: Mode: {args.mode}")
        print(f"INFO: Session ID: {payload['session_id']}")


if __name__ == "__main__":
    main()
