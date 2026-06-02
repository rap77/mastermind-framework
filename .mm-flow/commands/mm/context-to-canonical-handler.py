#!/usr/bin/env python3
"""MasterMind Context-to-Canonical Handler.

Scans an existing project, collects its context, and writes a canonical
document draft directly. It can also emit a payload for an external model-based
writer when richer synthesis is desired.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime
from pathlib import Path

MM_FLOW_ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_canonical_assets_root() -> Path:
    """Return the canonical assets root used by context-to-canonical.

    Preference order:
    1. Bundled assets inside `.mm-flow/assets/canonical`
    2. Repository docs/canonical (development fallback)
    """
    bundled = MM_FLOW_ROOT / "assets" / "canonical"
    if bundled.exists():
        return bundled

    repo_docs = REPO_ROOT / "docs" / "canonical"
    if repo_docs.exists():
        return repo_docs

    raise FileNotFoundError(
        "Canonical assets not found in .mm-flow/assets/canonical or docs/canonical"
    )


CANONICAL_DIR = resolve_canonical_assets_root()

SUPPORTED_TYPES = {
    "project-adapter": {
        "template": CANONICAL_DIR / "project-adapter" / "PROJECT-ADAPTER-TEMPLATE.md",
        "example": CANONICAL_DIR / "project-adapter" / "EXAMPLE-PROJECT-ADAPTER.md",
        "output_subdir": "docs/canonical/project-adapter",
        "filename_prefix": "",
    },
    "objective": {
        "template": CANONICAL_DIR / "templates" / "OBJECTIVE-SPEC-TEMPLATE.md",
        "example": CANONICAL_DIR / "examples" / "EXAMPLE-OBJECTIVE-SPEC.md",
        "output_subdir": "docs/canonical/objective-specs",
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
    parser.add_argument(
        "--name",
        default=None,
        metavar="NAME",
        help="Objective name/description (required when --type objective)",
    )
    parser.add_argument(
        "--intent",
        default="feature",
        choices=["feature", "bugfix", "capability", "refactor"],
        help="Objective intent (only used with --type objective, default: feature)",
    )
    parser.add_argument(
        "--payload-only",
        action="store_true",
        help="Emit a payload for an external writer instead of writing the file directly",
    )
    parser.add_argument(
        "--interview",
        action="store_true",
        help="Emit structured follow-up questions when repository evidence is insufficient",
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
    """Return a compact git log for the target project."""
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

    # Active planning context for the target project
    handoff = read_file_safe(target / ".planning" / "HANDOFF-CURRENT.md")
    if handoff:
        ctx["content"]["handoff"] = handoff
        ctx["files_found"].append(".planning/HANDOFF-CURRENT.md")

    # existing roadmap (for dependency context when writing objective specs)
    roadmap = read_file_safe(
        target / ".planning" / "roadmap" / "objectives.md", max_bytes=3000
    )
    if roadmap:
        ctx["content"]["roadmap"] = roadmap
        ctx["files_found"].append(".planning/roadmap/objectives.md")

    # list of existing canonical docs (for evidence and dependency hints)
    canonical_dir = target / "docs" / "canonical"
    if canonical_dir.exists():
        canonical_list = [
            f.name
            for f in sorted(canonical_dir.glob("*.md"))
            if not f.name.startswith("README")
        ]
        if canonical_list:
            ctx["content"]["canonical_index"] = "\n".join(canonical_list)
            ctx["files_found"].append("docs/canonical/ (index)")

    return ctx


def determine_output(target: Path, doc_type: str, output_arg: str | None) -> Path:
    """Return the output path for the generated canonical document."""
    if output_arg:
        return Path(output_arg)
    spec = SUPPORTED_TYPES[doc_type]
    out_dir = target / spec["output_subdir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = target.name.lower().replace(" ", "-").replace("_", "-")
    return out_dir / f"{spec['filename_prefix']}{slug}.md"


def determine_report_output(output_path: Path) -> Path:
    """Return the sidecar JSON report path for a generated canonical doc."""
    return output_path.with_suffix(".json")


def slugify(name: str) -> str:
    """Convert a human name into a filesystem-safe slug."""
    slug = name.strip().lower()
    slug = "".join(ch if ch.isalnum() else "-" for ch in slug)
    while "--" in slug:
        slug = slug.replace("--", "-")
    return slug.strip("-")


def build_intake_contract(args: argparse.Namespace, target: Path) -> dict[str, object]:
    """Build the normalized structured intake contract for canonical generation."""
    return {
        "schema_version": 1,
        "doc_type": args.type,
        "target": str(target),
        "name": args.name,
        "intent": args.intent if args.type == "objective" else None,
        "interview_requested": args.interview,
        "output_mode": "payload-only" if args.payload_only else "direct-write",
    }


def build_interview_questions(
    intake: dict[str, object], context: dict[str, object], gaps: list[str]
) -> list[dict[str, str]]:
    """Return structured interview questions for insufficient-context cases."""
    doc_type = str(intake.get("doc_type", "project-adapter"))
    intent = str(intake.get("intent") or "feature")
    content = context.get("content", {})
    assert isinstance(content, dict)

    questions: list[dict[str, str]] = []
    if doc_type == "objective":
        if not content.get("docs_prd"):
            questions.append(
                {
                    "id": "desired_behavior",
                    "question": "What exact behavior or outcome should this objective produce?",
                    "reason": "Repository evidence does not yet define the objective slice precisely.",
                }
            )
        if intent == "bugfix":
            questions.append(
                {
                    "id": "repro_steps",
                    "question": "What are the minimal reproduction steps and the expected behavior?",
                    "reason": "Bugfix objectives need repro evidence to avoid ambiguous scope.",
                }
            )
        elif intent == "refactor":
            questions.append(
                {
                    "id": "invariants",
                    "question": "Which invariants must stay unchanged while refactoring?",
                    "reason": "Refactor work needs explicit non-regression boundaries.",
                }
            )
        else:
            questions.append(
                {
                    "id": "out_of_scope",
                    "question": "What is explicitly out of scope for this objective?",
                    "reason": "Feature/capability work benefits from clear scope boundaries.",
                }
            )
    elif gaps:
        questions.append(
            {
                "id": "project_goal",
                "question": "What is the primary goal this project adapter should capture?",
                "reason": "Repository evidence is too sparse to infer a stable canonical summary.",
            }
        )

    deduped: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for question in questions:
        qid = question["id"]
        if qid in seen_ids:
            continue
        seen_ids.add(qid)
        deduped.append(question)
    return deduped


def _first_sentence(*values: str) -> str:
    """Return the first non-empty sentence from the provided values."""
    for value in values:
        text = " ".join(value.split()).strip()
        if not text:
            continue
        for separator in [". ", "\n", "! ", "? "]:
            if separator in text:
                return text.split(separator, 1)[0].strip().rstrip(".!?") + "."
        return text.rstrip(".") + "."
    return "(not documented — to be defined)"


def _stack_label(stack: list[str]) -> str:
    """Return a human-readable project type label."""
    if not stack or stack == ["unknown"]:
        return "unknown"
    return ", ".join(stack)


def _extract_brains(config_text: str | None) -> str:
    """Extract active brain identifiers from config text."""
    if not config_text:
        return "- (not documented — to be defined)"
    for line in config_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("active:"):
            return f"- Active brains: {stripped.split(':', 1)[1].strip()}"
    return "- (not documented — to be defined)"


def render_project_adapter(payload: dict[str, object]) -> str:
    """Render a project-adapter canonical document directly from payload data."""
    context = payload["context"]
    assert isinstance(context, dict)
    content = context.get("content", {})
    assert isinstance(content, dict)
    stack = context.get("stack", ["unknown"])
    assert isinstance(stack, list)
    files_found = context.get("files_found", [])
    assert isinstance(files_found, list)

    readme = str(content.get("readme", ""))
    claude_md = str(content.get("claude_md", ""))
    docs_prd = str(content.get("docs_prd", ""))
    config_text = str(content.get("mastermind_config", ""))

    project_name = str(context.get("project_name", "unknown-project"))
    primary_niche = "software-development"
    if "finance" in readme.lower() or "trading" in readme.lower():
        primary_niche = "finance"

    generated_at = datetime.now().strftime("%Y-%m-%d")
    sources = ", ".join(files_found) if files_found else "(no explicit sources found)"

    return f"""# Project Adapter: {project_name}

## 1. Project Identity

- **Project name:** {project_name}
- **Project type:** {_stack_label(stack)}
- **Primary niche:** {primary_niche}
- **Secondary niches:** (not documented — to be defined)
- **Owner/team:** (not documented — to be defined)
- **Start date:** {generated_at}

## 2. Project Goal

{_first_sentence(readme, claude_md, docs_prd)}

## 3. Why MasterMind Is Being Used Here

MasterMind is being used to structure discovery, planning, execution, and archival around objective packages derived from the real project context.

## 4. Project Constraints

- Technical constraints: {_first_sentence(claude_md, docs_prd)}
- Business constraints: (not documented — to be defined)
- Regulatory constraints: (not documented — to be defined)
- Timeline constraints: (not documented — to be defined)
- Risk constraints: Existing repository context may be incomplete or partially stale; generated canonicals should be reviewed before execution.

## 5. Selected Brains

### Core/meta-brains involved

{_extract_brains(config_text)}

### Niche brains involved

- Brain 1: Product / planning
- Brain 2: Architecture / implementation
- Brain 3: QA / review

## 6. Project-Specific Knowledge

What knowledge is specific to this project and should not automatically be promoted to core?

- Local rule 1: Respect project-local instructions from CLAUDE.md/README before proposing workflow changes.
- Local assumption 2: Generated planning should reconcile repository state before execution.
- Local integration 3: Existing docs/PRD and canonical docs are higher-trust discovery sources than chat memory.

## 7. Local Integrations

- API / service 1: {_first_sentence(readme)}
- API / service 2: {_first_sentence(docs_prd)}
- Broker / provider / platform: {_stack_label(stack)}

## 8. Decision Model

- Which decisions are project-local? Objective scope, touched modules, and implementation sequencing.
- Which decisions should go through framework-level meta-brains? Reusable lifecycle rules, archive rules, and canonical/template changes.

## 9. Memory Boundaries

### Keep local to project

- Local heuristics: Project-specific command conventions and touched-module assumptions.
- Local data assumptions: Stack and integration details discovered from repo files.
- Local workflow decisions: Which objective is active, archived, or next.

### Candidate for promotion to core

- Reusable protocol improvements: Better objective lifecycle gates and model-agnostic writer patterns.
- Reusable template improvements: Canonical templates and roadmap ranking heuristics.
- Reusable doctrinal improvements: Context collection and archive safety rules.

## 10. Success Criteria

- Generated canonical docs reflect real repository evidence.
- `/mm:discover` can use the canonical context as a strong planning source.
- Another model can resume from artifacts without relying on chat memory alone.

## 11. Notes

This document was generated directly from repository context and should be treated as a first-pass canonical adapter.

---
*Generated by MasterMind context-to-canonical on {generated_at}.*
*Sources: {sources}*
"""


def render_objective_spec(payload: dict[str, object]) -> str:
    """Render an objective-spec canonical document directly from payload data."""
    context = payload["context"]
    assert isinstance(context, dict)
    content = context.get("content", {})
    assert isinstance(content, dict)
    files_found = context.get("files_found", [])
    assert isinstance(files_found, list)
    stack = context.get("stack", ["unknown"])
    assert isinstance(stack, list)

    objective_name = str(context.get("objective_name", "Unnamed objective"))
    objective_slug = str(context.get("objective_slug", "unnamed-objective"))
    objective_intent = str(context.get("objective_intent", "feature"))
    project_name = str(context.get("project_name", "unknown-project"))
    readme = str(content.get("readme", ""))
    claude_md = str(content.get("claude_md", ""))
    docs_prd = str(content.get("docs_prd", ""))
    roadmap = str(content.get("roadmap", ""))
    canonical_index = str(content.get("canonical_index", ""))

    dependencies = "none"
    if roadmap:
        lowered = roadmap.lower()
        if "project-state-mvp" in lowered and objective_slug != "project-state-mvp":
            dependencies = "project-state-mvp"

    generated_at = datetime.now().strftime("%Y-%m-%d")
    sources = ", ".join(files_found) if files_found else "(no explicit sources found)"

    return f"""# Objective Spec: {objective_name}

<!-- mm:objective-spec | slug: {objective_slug} | intent: {objective_intent} | status: draft -->

## 1. Objective Identity

- **Slug:** {objective_slug}
- **Name:** {objective_name}
- **Intent:** {objective_intent}
- **Project:** {project_name}
- **Status:** draft

## 2. Summary

{_first_sentence(objective_name, readme, claude_md)}

## 3. Why It Matters

- **Product reason:** {_first_sentence(readme, docs_prd)}
- **Technical reason:** {_first_sentence(claude_md, docs_prd)}
- **User impact:** {_first_sentence(readme)}

## 4. Scope

### In scope

- Define the smallest coherent implementation slice for `{objective_name}`.
- Touch only the modules justified by the current project context.
- Produce acceptance criteria that can be validated by targeted tests.

### Out of scope

- Unrelated refactors outside the touched slice.
- New platform abstractions not evidenced by current repository needs.

## 5. Acceptance Criteria

- [ ] The objective is described in terms of observable behavior or repository structure changes.
- [ ] Dependencies and touched modules are explicit enough for `/mm:discover` to package the work.
- [ ] The resulting objective can be validated with concrete tests or checks.

## 6. MVP Relevance

- **Included in MVP:** yes
- **Reason:** The objective is being introduced as an actionable planning artifact for the active roadmap.

## 7. Dependencies

- **Depends on:** {dependencies}
- **Unlocks:** To be determined during roadmap reconciliation using current canonical evidence ({canonical_index[:160] or "not documented"}).

## 8. Technical Context

- **Affected modules:** {_stack_label(stack)}
- **Approach:** Derive implementation from current repository evidence, then let `/mm:discover` convert it into an objective package.
- **Known constraints:** {_first_sentence(claude_md, docs_prd)}

## 9. Evidence

- {sources}

---
*Generated by MasterMind context-to-canonical on {generated_at}.*
*Sources: {sources}*
"""


def build_intake_report(payload: dict[str, object]) -> dict[str, object]:
    """Build the machine-readable intake report for downstream tooling."""
    context = payload["context"]
    assert isinstance(context, dict)
    content = context.get("content", {})
    assert isinstance(content, dict)
    files_found = context.get("files_found", [])
    assert isinstance(files_found, list)
    intake = payload["intake"]
    assert isinstance(intake, dict)

    evidence = [{"source": source, "kind": "repo"} for source in files_found]
    assumptions: list[str] = []
    gaps: list[str] = []
    questions_unanswered: list[str] = []

    if not content.get("readme"):
        gaps.append("README.md missing or unreadable")
    if intake.get("doc_type") == "objective" and not content.get("docs_prd"):
        assumptions.append(
            "Objective scope is inferred from repository context without dedicated PRD evidence"
        )
    if not content.get("claude_md"):
        assumptions.append("Runtime/operator guidance is inferred without CLAUDE.md")
    if intake.get("doc_type") == "objective":
        questions_unanswered.append(
            "Should objective-context-check request additional structured user input before discover?"
        )

    questions_asked = build_interview_questions(intake, context, gaps)
    if gaps:
        confidence = "medium" if evidence else "low"
    else:
        confidence = "high" if len(evidence) >= 3 else "medium"

    report = {
        "schema_version": 1,
        "doc_type": intake.get("doc_type"),
        "intent": intake.get("intent"),
        "objective_slug": context.get("objective_slug"),
        "project_name": context.get("project_name"),
        "context_sources": files_found,
        "evidence": evidence,
        "assumptions": assumptions,
        "gaps_detected": gaps,
        "questions_asked": questions_asked,
        "questions_unanswered": [q["id"] for q in questions_asked]
        + questions_unanswered,
        "confidence": confidence,
        "generated_files": [
            payload["output_path"],
            payload["report_output_path"],
        ],
    }
    return report


def write_document(payload: dict[str, object]) -> tuple[Path, Path]:
    """Write the canonical document and sidecar report, returning both paths."""
    output_path = Path(str(payload["output_path"]))
    report_output_path = Path(str(payload["report_output_path"]))
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_output_path.parent.mkdir(parents=True, exist_ok=True)
    doc_type = str(payload["doc_type"])
    if doc_type == "project-adapter":
        content = render_project_adapter(payload)
    elif doc_type == "objective":
        content = render_objective_spec(payload)
    else:
        raise ValueError(f"Unsupported doc_type: {doc_type}")
    output_path.write_text(content, encoding="utf-8")
    report_output_path.write_text(
        json.dumps(build_intake_report(payload), indent=2) + "\n",
        encoding="utf-8",
    )
    return output_path, report_output_path


def main() -> None:
    args = parse_args()
    target = Path(args.target).resolve() if args.target else Path.cwd()

    if not target.is_dir():
        print(f"ERROR: Target is not a directory: {target}")
        raise SystemExit(1)

    if args.type == "objective" and not args.name:
        print("ERROR: --name is required when --type objective")
        print(
            "  Example: context-to-canonical-handler.py --type objective --name 'Add OAuth login'"
        )
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

    # Objective-specific fields
    if args.type == "objective":
        context["objective_name"] = args.name
        context["objective_slug"] = slugify(args.name)
        context["objective_intent"] = args.intent

        # Override output path to use slug as filename
        if not args.output:
            out_dir = target / spec["output_subdir"]
            out_dir.mkdir(parents=True, exist_ok=True)
            args.output = str(out_dir / f"{context['objective_slug']}.md")

    output_path = determine_output(target, args.type, args.output)
    print(f"INFO: Output will be written to: {output_path}")

    payload = {
        "doc_type": args.type,
        "target": str(target),
        "output_path": str(output_path),
        "report_output_path": str(determine_report_output(output_path)),
        "template_content": template_content,
        "example_content": example_content,
        "context": context,
        "intake": build_intake_contract(args, target),
    }

    if args.payload_only:
        print(f"PAYLOAD: {json.dumps(payload)}")
        print("LAUNCH: canonical-writer")
        print()
        print(f"INFO: Ready to generate {args.type} canonical doc for: {target.name}")
        return

    output_file, report_file = write_document(payload)
    report_data = json.loads(report_file.read_text(encoding="utf-8"))
    print("STATUS: PASSED")
    print(f"FILE: {output_file}")
    print(f"REPORT: {report_file}")
    if report_data.get("questions_asked"):
        print("INTERVIEW_REQUIRED: yes")
    else:
        print("INTERVIEW_REQUIRED: no")
    print(f"MODE: direct-write ({args.type})")
    print("NEXT_COMMAND: /mm:discover --roadmap --existing")


if __name__ == "__main__":
    main()
