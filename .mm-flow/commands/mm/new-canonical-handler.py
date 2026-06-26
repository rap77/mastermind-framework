#!/usr/bin/env python3
"""
MasterMind New Canonical Handler

Creates new canonical documents (PRD, brain specifications, etc.)
from templates following the MasterMind framework conventions.
"""

from __future__ import annotations

import argparse
import hashlib
import logging
import subprocess
import sys
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
EVIDENCE_REGISTRY_HELPER = Path(__file__).resolve().parent / "evidence-registry.py"
logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
logger = logging.getLogger(__name__)


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


def render_path(path: Path) -> str:
    """Render a path relative to ROOT when possible, otherwise absolute."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def create_prd(name: str, title: str, output: Path | None) -> int:
    """Create a new PRD document."""
    template = TEMPLATES_DIR / "00-PRD-Template.md"
    if not template.exists():
        logger.error("ERROR: Template not found at %s", template)
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"{slug}.md"

    # Check if file exists
    if output.exists():
        logger.error("ERROR: File already exists: %s", output)
        return 1

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    register_canonical_as_evidence(output, "prd", name, title)
    logger.info("STATUS: created")
    logger.info("- File: %s", render_path(output))
    return 0


def create_brain(name: str, title: str, output: Path | None) -> int:
    """Create a new Brain specification document."""
    template = TEMPLATES_DIR / "02-Metodo-Seleccion-Expertos.md"  # Use brain template
    if not template.exists():
        logger.error("ERROR: Brain template not found")
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"BRAIN-{slug}.md"

    if output.exists():
        logger.error("ERROR: File already exists: %s", output)
        return 1

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)
    register_canonical_as_evidence(output, "brain", name, title)
    logger.info("STATUS: created")
    logger.info("- File: %s", render_path(output))
    return 0


def register_canonical_as_evidence(
    output: Path, doc_type: str, name: str, title: str
) -> None:
    """Register a created canonical document as evidence."""
    if not EVIDENCE_REGISTRY_HELPER.exists():
        return

    version_hash = hashlib.sha256(output.read_bytes()).hexdigest()
    version_ref = render_path(output)
    source_id = f"canonical:{doc_type}:{name.lower().replace(' ', '-')}"

    subprocess.run(
        [
            "python3",
            str(EVIDENCE_REGISTRY_HELPER),
            "register",
            "--source-id",
            source_id,
            "--source-type",
            "doc",
            "--name",
            title,
            "--uri",
            version_ref,
            "--version-ref",
            version_ref,
            "--version-hash",
            version_hash,
            "--summary",
            f"Canonical {doc_type} document created from template",
            "--confidence",
            "1.0",
            "--coverage",
            "1.0",
            "--user-answers-complete",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.type is None:
        logger.info("Available canonical types:")
        logger.info("  prd       - Product Requirements Document")
        logger.info("  brain     - Brain specification")
        logger.info("  source    - Source master document")
        logger.info("  task      - Task specification")
        logger.info("  objective - Objective specification")
        logger.info("")
        logger.info(
            "Usage: python3 new-canonical-handler.py <type> --name <slug> --title <title>"
        )
        return 0

    if not args.name:
        logger.error("ERROR: --name is required")
        return 1

    if not args.title:
        args.title = args.name.replace("-", " ").title()

    output = Path(args.output) if args.output else None

    if args.type == "prd":
        return create_prd(args.name, args.title, output)
    elif args.type == "brain":
        return create_brain(args.name, args.title, output)
    else:
        logger.error("ERROR: Type '%s' not yet implemented", args.type)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
