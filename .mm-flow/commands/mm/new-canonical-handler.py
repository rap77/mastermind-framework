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

from planning_paths import get_planning_dir


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
APPS_API_DIR = ROOT / "apps" / "api"
if str(APPS_API_DIR) not in sys.path:
    sys.path.insert(0, str(APPS_API_DIR))

from mastermind_cli.mm_flow.evidence_registry_service import (  # noqa: E402
    EvidenceRegistryService,
)

EVIDENCE_REGISTRY = EvidenceRegistryService(
    get_planning_dir(ROOT) / "evidence" / "evidence-registry.json"
)
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
        choices=["prd", "brain", "update"],
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


def write_canonical_document(
    output: Path, content: str, *, allow_overwrite: bool = False
) -> None:
    """Write a canonical document, optionally allowing overwrite."""
    if output.exists() and not allow_overwrite:
        raise FileExistsError(f"File already exists: {output}")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content)


def create_prd(name: str, title: str, output: Path | None) -> int:
    """Create a new PRD document."""
    template = TEMPLATES_DIR / "00-PRD-Template.md"
    if not template.exists():
        logger.error("ERROR: Template not found at %s", template)
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"{slug}.md"

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    try:
        write_canonical_document(output, content)
    except FileExistsError as exc:
        logger.error("ERROR: %s", exc)
        return 1
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

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    try:
        write_canonical_document(output, content)
    except FileExistsError as exc:
        logger.error("ERROR: %s", exc)
        return 1
    register_canonical_as_evidence(output, "brain", name, title)
    logger.info("STATUS: created")
    logger.info("- File: %s", render_path(output))
    return 0


def update_prd(name: str, title: str, output: Path | None) -> int:
    """Update an existing PRD document from the template."""
    template = TEMPLATES_DIR / "00-PRD-Template.md"
    if not template.exists():
        logger.error("ERROR: Template not found at %s", template)
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"{slug}.md"

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    write_canonical_document(output, content, allow_overwrite=True)
    register_canonical_as_evidence(output, "prd", name, title)
    logger.info("STATUS: updated")
    logger.info("- File: %s", render_path(output))
    return 0


def update_brain(name: str, title: str, output: Path | None) -> int:
    """Update an existing Brain specification document from the template."""
    template = TEMPLATES_DIR / "02-Metodo-Seleccion-Expertos.md"
    if not template.exists():
        logger.error("ERROR: Brain template not found")
        return 1

    slug = name.lower().replace(" ", "-")
    if output is None:
        output = ROOT / "docs" / "PRD" / f"BRAIN-{slug}.md"

    content = template.read_text()
    content = content.replace("{{NAME}}", name)
    content = content.replace("{{TITLE}}", title)

    write_canonical_document(output, content, allow_overwrite=True)
    register_canonical_as_evidence(output, "brain", name, title)
    logger.info("STATUS: updated")
    logger.info("- File: %s", render_path(output))
    return 0


def register_canonical_as_evidence(
    output: Path, doc_type: str, name: str, title: str
) -> None:
    """Register a created canonical document as evidence."""
    version_hash = hashlib.sha256(output.read_bytes()).hexdigest()
    version_ref = render_path(output)
    source_id = f"canonical:{doc_type}:{name.lower().replace(' ', '-')}"
    EVIDENCE_REGISTRY.register_version(
        source_id=source_id,
        source_type="doc",
        name=title,
        uri=version_ref,
        version_ref=version_ref,
        version_hash=version_hash,
        summary=f"Canonical {doc_type} document created from template",
        confidence=1.0,
        coverage=1.0,
        user_answers_complete=True,
    )


def main() -> int:
    """Main entry point."""
    args = parse_args()

    if args.type is None:
        logger.info("Available canonical types:")
        logger.info("  prd       - Product Requirements Document")
        logger.info("  brain     - Brain specification")
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
    elif args.type == "update":
        if args.name.startswith("brain-"):
            return update_brain(args.name, args.title, output)
        return update_prd(args.name, args.title, output)
    else:
        logger.error("ERROR: Type '%s' not yet implemented", args.type)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
