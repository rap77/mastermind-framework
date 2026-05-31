#!/usr/bin/env python3
"""
MasterMind Context-to-Canonical Handler

Scans an existing project, collects its context, and produces a PAYLOAD
for the canonical-writer agent to fill in the appropriate template.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parent.parent.parent.parent
TEMPLATE_DIR = FRAMEWORK_ROOT / "docs" / "canonical" / "project-adapter"

SUPPORTED_TYPES = {
    "project-adapter": {
        "template": TEMPLATE_DIR / "PROJECT-ADAPTER-TEMPLATE.md",
        "example": TEMPLATE_DIR / "EXAMPLE-PROJECT-ADAPTER.md",
        "output_subdir": "docs/canonical/project-adapter",
        "filename_prefix": "",
    },
}

MAX_FILE_BYTES = 6_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate a canonical document from an existing project's context",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python3 context-to-canonical-handler.py\n"
            "  python3 context-to-canonical-handler.py --type project-adapter\n"
            "  python3 context-to-canonical-handler.py --target /path/to/project\n"
        ),
    )
    parser.add_argument(
        "--type",
        default="project-adapter",
        choices=list(SUPPORTED_TYPES.keys()),
        help="Type of canonical document to generate (default: project-adapter)",
    )
    parser.add_argument(
        "--target",
        default=None,
        metavar="PATH",
        help="Target project directory (default: current working directory)",
    )
    parser.add_argument(
        "--output",
        default=None,
        metavar="PATH",
        help="Output file path (default: auto-generated inside target)",
    )
    return parser.parse_args()


def read_file_safe(path: Path, max_bytes: int = MAX_FILE_BYTES) -> str | None:
    """Read a file, truncating at max_bytes. Returns None if not found."""
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
        if len(text) > max_bytes:
            return text[:max_bytes] + "\n... [truncated]"
        return text
    except OSError:
        return None


def git_log(target: Path, n: int = 20) -> str:
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"-{n}"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=target,
        )
        return result.stdout.strip() if result.returncode == 0 else ""
    except Exception:
        return ""


def collect_context(target: Path) -> dict:
    """Collect all available context from the target project."""
    ctx: dict = {
        "project_name": target.name,
        "project_path": str(target),
        "files_found": [],
        "content": {},
    }

    # Priority sources — read content
    priority_files = [
        ("CLAUDE.md", "claude_md"),
        ("README.md", "readme"),
        ("PROJECT.md", "project_md"),
        (".mastermind/config.yaml", "mastermind_config"),
    ]
    for rel, key in priority_files:
        text = read_file_safe(target / rel)
        if text:
            ctx["content"][key] = text
            ctx["files_found"].append(rel)

    # docs/PRD — collect all .md files (first 4, truncated)
    prd_dir = target / "docs" / "PRD"
    if prd_dir.exists():
        prd_files = sorted(prd_dir.glob("*.md"))[:4]
        prd_texts = []
        for f in prd_files:
            t = read_file_safe(f, max_bytes=2000)
            if t:
                prd_texts.append(f"### {f.name}\n{t}")
                ctx["files_found"].append(f"docs/PRD/{f.name}")
        if prd_texts:
            ctx["content"]["docs_prd"] = "\n\n".join(prd_texts)

    # package.json — stack signals
    pkg = read_file_safe(target / "package.json", max_bytes=2000)
    if pkg:
        ctx["content"]["package_json"] = pkg
        ctx["files_found"].append("package.json")

    # pyproject.toml
    py_proj = read_file_safe(target / "pyproject.toml", max_bytes=1000)
    if py_proj:
        ctx["content"]["pyproject_toml"] = py_proj
        ctx["files_found"].append("pyproject.toml")

    # Detect stack
    stack = []
    if (target / "package.json").exists():
        stack.append("nodejs")
        try:
            pkg_data = json.loads((target / "package.json").read_text())
            deps = {
                **pkg_data.get("dependencies", {}),
                **pkg_data.get("devDependencies", {}),
            }
            if "next" in deps:
                stack = ["nextjs"] + stack
            elif "react" in deps:
                stack = ["react"] + stack
        except Exception:
            pass
    if (target / "pyproject.toml").exists() or (target / "requirements.txt").exists():
        stack.append("python")
    if (target / "Cargo.toml").exists():
        stack.append("rust")
    if (target / "go.mod").exists():
        stack.append("go")
    ctx["stack"] = stack or ["unknown"]

    # git log
    log = git_log(target)
    if log:
        ctx["content"]["git_log"] = log
        ctx["files_found"].append("git log")

    # existing .mm-flow planning context
    handoff = read_file_safe(target / ".mm-flow" / "planning" / "HANDOFF-CURRENT.md")
    if handoff:
        ctx["content"]["handoff"] = handoff
        ctx["files_found"].append(".mm-flow/planning/HANDOFF-CURRENT.md")

    return ctx


def determine_output(target: Path, doc_type: str, output_arg: str | None) -> Path:
    if output_arg:
        return Path(output_arg)
    spec = SUPPORTED_TYPES[doc_type]
    out_dir = target / spec["output_subdir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = target.name.lower().replace(" ", "-").replace("_", "-")
    return out_dir / f"{spec['filename_prefix']}{slug}.md"


def main() -> None:
    args = parse_args()
    target = Path(args.target).resolve() if args.target else Path.cwd()

    if not target.is_dir():
        print(f"ERROR: Target is not a directory: {target}")
        raise SystemExit(1)

    spec = SUPPORTED_TYPES[args.type]
    template_path = spec["template"]
    example_path = spec["example"]

    if not template_path.exists():
        print(f"ERROR: Template not found: {template_path}")
        raise SystemExit(1)

    template_content = template_path.read_text(encoding="utf-8")
    example_content = read_file_safe(example_path) or ""

    print(f"INFO: Scanning project: {target}")
    context = collect_context(target)
    print(f"INFO: Context sources found: {', '.join(context['files_found']) or 'none'}")
    print(f"INFO: Detected stack: {context['stack']}")

    output_path = determine_output(target, args.type, args.output)
    print(f"INFO: Output will be written to: {output_path}")

    payload = {
        "doc_type": args.type,
        "target": str(target),
        "output_path": str(output_path),
        "template_content": template_content,
        "example_content": example_content,
        "context": context,
    }

    print(f"PAYLOAD: {json.dumps(payload)}")
    print("LAUNCH: canonical-writer")
    print()
    print(f"INFO: Ready to generate {args.type} canonical doc for: {target.name}")


if __name__ == "__main__":
    main()
