#!/usr/bin/env python3
"""
MasterMind New Canonical Handler

Creates new canonical documents (PRD, brain specifications, etc.)
from templates following the MasterMind framework conventions.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


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
TEMPLATES_DIR = ROOT / "docs" / "canonical" / "templates"


def parse_args() -> argparse.Namespace:
    """Parse new-canonical command arguments."""
    parser = argparse.ArgumentParser(
        description="Create new canonical document from MasterMind templates"
    )
    parser.add_argument(
        "type",
        nargs="?",
        choices=["prd", "brain", "source", "task", "objective"],
        help="Type of canonical document to create",
    )
    parser.add_argument(
        "--name",
        help="Name/slug for the document (e.g., '05-Cerebro-01')",
    )
    parser.add_argument(
        "--title",
        help="Human-readable title for the document",
    )
    parser.add_argument(
        "--output",
        help="Output path (default: auto-generated based on type)",
    )
    return parser.parse_args()


def list_templates() -> list[str]:
    """List available canonical templates."""
    if not TEMPLATES_DIR.exists():
        return []
    return [f.stem for f in TEMPLATES_DIR.glob("*.md")]


def create_prd(name: str, title: str, output: Path | None) -> int:
    """Create a new PRD document."""
    template = TEMPLATES_DIR / "00-PRD-Template.md"
    if not template.exists():
        print(f"ERROR: Template not found at {template}")
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"{slug}.md"

    # Check if file exists
    if output.exists():
        print(f"ERROR: File already exists: {output}")
        return 1

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    print("STATUS: created")
    print(f"- File: {output.relative_to(ROOT)}")
    return 0


def create_brain(name: str, title: str, output: Path | None) -> int:
    """Create a new Brain specification document."""
    template = TEMPLATES_DIR / "02-Metodo-Seleccion-Expertos.md"  # Use brain template
    if not template.exists():
        print("ERROR: Brain template not found")
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"BRAIN-{slug}.md"

    if output.exists():
        print(f"ERROR: File already exists: {output}")
        return 1

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    print("STATUS: created")
    print(f"- File: {output.relative_to(ROOT)}")
    return 0


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.type is None:
        print("Available canonical types:")
        print("  prd       - Product Requirements Document")
        print("  brain     - Brain specification")
        print("  source    - Source master document")
        print("  task      - Task specification")
        print("  objective - Objective specification")
        print("")
        print(
            "Usage: python3 new-canonical-handler.py <type> --name <slug> --title <title>"
        )
        return 0

    if not args.name:
        print("ERROR: --name is required")
        return 1

    if not args.title:
        args.title = args.name.replace("-", " ").title()

    output = Path(args.output) if args.output else None

    if args.type == "prd":
        return create_prd(args.name, args.title, output)
    elif args.type == "brain":
        return create_brain(args.name, args.title, output)
    else:
        print(f"ERROR: Type '{args.type}' not yet implemented")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
