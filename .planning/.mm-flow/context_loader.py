"""
EngramContextLoader: Automatic context recovery from Engram persistent memory.

This module queries Engram for prior decisions, warnings, and learnings
associated with a specific phase, then generates a CONTEXT.md file
that can be injected into phase planning.

Architecture:
1. Query Engram: mem_search "phase N" → get decisions, warnings, learnings
2. Parse observations: extract type, title, content
3. Categorize: UX decisions, backend warnings, test gaps, security, etc.
4. Generate CONTEXT.md: write to .planning/phases/0N-*/CONTEXT.md

Usage:
    loader = EngramContextLoader(project="mastermind", phase_num=19)
    context_md = loader.generate_context_md()
    # context_md written to .planning/phases/19-*/CONTEXT.md
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


# ============================================================================
# DOMAIN MODELS
# ============================================================================


@dataclass
class EngramObservation:
    """Parsed observation from Engram."""

    id: int
    title: str
    content: str
    observation_type: str  # decision, architecture, bugfix, discovery, pattern, etc.
    project: str
    scope: str  # project or personal
    created_at: Optional[str] = None
    topic_key: Optional[str] = None

    def category(self) -> str:
        """Infer category from title and type (keywords > type fallback)."""
        title_lower = self.title.lower()

        # Performance (check before Backend/API since query is backend-ish)
        if any(
            kw in title_lower
            for kw in [
                "performance",
                "optimization",
                "cache",
                "speed",
                "latency",
                "efficient",
            ]
        ):
            return "Performance"

        # UX/Design (check before general "design")
        if any(
            kw in title_lower
            for kw in [
                "button",
                "alignment",
                "padding",
                "ui ",
                "ux ",
                "header",
                "layout",
                "component visual",
                "interface",
            ]
        ):
            return "UX/Design"

        # Backend/API
        if any(
            kw in title_lower
            for kw in ["backend", "api", "database", "schema", "orm", "query"]
        ):
            return "Backend/API"

        # Testing
        if any(
            kw in title_lower
            for kw in ["test", "qa", "validation", "verification", "coverage"]
        ):
            return "Testing/QA"

        # Security
        if any(
            kw in title_lower
            for kw in [
                "security",
                "auth",
                "encryption",
                "vulnerability",
                "access",
                "token",
            ]
        ):
            return "Security"

        # Architecture/Patterns (check after specific categories)
        if any(
            kw in title_lower
            for kw in [
                "architecture",
                "pattern",
                "refactor",
                "structure",
                "state management",
            ]
        ):
            return "Architecture"

        # DevOps/Deployment
        if any(
            kw in title_lower
            for kw in [
                "deploy",
                "devops",
                "docker",
                "kubernetes",
                "ci/cd",
                "infra",
                "pipeline",
            ]
        ):
            return "DevOps/Deployment"

        # Default to type
        return self.observation_type.title()


# ============================================================================
# ENGRAM CONTEXT LOADER
# ============================================================================


class EngramContextLoader:
    """
    Loads historical context from Engram for a specific phase.

    Queries Engram via subprocess (mm-flow CLI would call these tools),
    then generates a CONTEXT.md file with sections:
    - Prior Decisions
    - Warnings from History
    - Learnings & Precedents
    - Cross-Phase Contracts
    """

    def __init__(self, project: str, phase_num: int) -> None:
        """
        Initialize loader.

        Args:
            project: Project name (e.g. "mastermind-framework")
            phase_num: Phase number (e.g. 19)
        """
        self.project = project
        self.phase_num = phase_num
        self.phase_str = f"{phase_num:02d}"

        # Root of codebase
        self.repo_root = Path(__file__).parent.parent.parent
        self.phase_dir = self.repo_root / ".planning" / "phases" / f"{self.phase_str}-*"

        self.observations: List[EngramObservation] = []
        self.logger = logging.getLogger(__name__)

    # ========================================================================
    # MAIN API
    # ========================================================================

    def generate_context_md(self) -> Optional[Path]:
        """
        Main entry point: query Engram, parse, generate CONTEXT.md.

        Returns:
            Path to generated CONTEXT.md, or None if no context found.
        """
        self.logger.info(
            f"Generating context for phase {self.phase_num} (project: {self.project})"
        )

        # Step 1: Query Engram
        if not self._query_engram():
            self.logger.warning(
                f"No observations found in Engram for phase {self.phase_num}"
            )
            return None

        # Step 2: Find phase directory
        phase_folders = list(
            self.repo_root.glob(f".planning/phases/{self.phase_str}-*")
        )
        if not phase_folders:
            self.logger.warning(
                f"No phase folder found matching {self.phase_str}-* in .planning/phases"
            )
            return None

        phase_dir = phase_folders[0]
        context_file = phase_dir / "CONTEXT.md"

        # Step 4: Render and write CONTEXT.md
        context_md = self._render_context_md()
        context_file.write_text(context_md, encoding="utf-8")

        self.logger.info(f"✅ Context generated: {context_file}")
        return context_file

    # ========================================================================
    # PRIVATE: QUERY ENGRAM
    # ========================================================================

    def _query_engram(self) -> bool:
        """
        Query Engram via subprocess: mem_search for "phase {N}" observations.

        Since we're in CLI (not async), we call engram tools via subprocess.
        This is a fallback; in production, use HTTP or gRPC.

        Returns:
            True if observations found, False otherwise.
        """
        # Query pattern: "phase 19" → get all observations mentioning this phase
        search_query = f"phase {self.phase_num}"

        try:
            # For now, this is a placeholder. In real implementation,
            # we'd call something like:
            #   mm-flow engram-query --search "phase 19" --project mastermind --output json
            #
            # For this implementation, we'll try to import engram tools if available
            observations = self._try_engram_api_query(search_query)

            if observations:
                self.observations = observations
                self.logger.info(
                    f"Found {len(observations)} observations in Engram for phase {self.phase_num}"
                )
                return True

            return False

        except Exception as e:
            self.logger.error(f"Failed to query Engram: {e}")
            return False

    def _try_engram_api_query(self, _search_query: str) -> List[EngramObservation]:
        """
        Attempt to query Engram using Python SDK or subprocess.

        Since Engram tools are available via Claude Code agents, this is stubbed
        for the current implementation. In a real deployment, this would:

        1. Call engram tools via HTTP/gRPC (if running in agent context)
        2. Or use subprocess to query via CLI wrapper
        3. Or read from a cached JSON file (development mode)

        For now: returns empty list, allowing graceful degradation.
        Context recovery is OPTIONAL — phases can execute without it.

        Returns:
            List of EngramObservation objects (empty if Engram unavailable).
        """
        # NOTE: In production, this would call:
        #
        #   results = mem_search(
        #       query=search_query,
        #       project=self.project,
        #       scope="project"
        #   )
        #   for obs in results:
        #       full = mem_get_observation(id=obs['id'])
        #       observations.append(EngramObservation(
        #           id=full['id'],
        #           title=full['title'],
        #           content=full['content'],
        #           observation_type=full['type'],
        #           project=self.project,
        #           scope=full.get('scope', 'project'),
        #           created_at=full.get('created_at'),
        #           topic_key=full.get('topic_key')
        #       ))
        #
        # Since we're in CLI context (not async Claude Code agent),
        # context recovery is OPTIONAL. The phase can execute without it.
        return []

    # ========================================================================
    # PRIVATE: CATEGORIZE & RENDER
    # ========================================================================

    def _categorize_observations(self) -> Dict[str, List[EngramObservation]]:
        """
        Categorize observations by type and domain.

        Returns:
            Dict mapping category -> list of observations.
        """
        categorized: Dict[str, List[EngramObservation]] = {}

        for obs in self.observations:
            cat = obs.category()
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(obs)

        return categorized

    def _render_context_md(self) -> str:
        """
        Render CONTEXT.md with all sections.

        Structure:
        ```
        # Phase {N} Context Recovery

        Auto-generated from Engram persistent memory.
        Last updated: {timestamp}

        ## Prior Decisions
        ...

        ## Warnings from History
        ...

        ## Learnings & Precedents
        ...

        ## Cross-Phase Contracts
        ...
        ```

        Returns:
            Markdown string ready to write to file.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sections = [
            f"# Phase {self.phase_num} Context Recovery",
            "",
            f"Auto-generated from Engram persistent memory on {now}.",
            "",
            "This context helps prevent reinventing wheels and ensures continuity across phases.",
            "",
        ]

        # ====================================================================
        # SECTION 1: PRIOR DECISIONS
        # ====================================================================

        decisions = [
            obs
            for obs in self.observations
            if obs.observation_type in ["decision", "architectural"]
        ]
        if decisions:
            sections.append("## Prior Decisions")
            sections.append("")
            sections.append(
                "Architectural, technical, and product decisions from prior phases."
            )
            sections.append("")

            for obs in decisions:
                sections.append(f"### {obs.title}")
                sections.append("")
                sections.append(f"**Category**: {obs.category()}")
                sections.append("")
                sections.append(f"**Decision**:\n{obs.content}")
                sections.append("")
                if obs.created_at:
                    sections.append(f"*From session {obs.created_at}*")
                sections.append("")

        # ====================================================================
        # SECTION 2: WARNINGS FROM HISTORY
        # ====================================================================

        warnings = [
            obs
            for obs in self.observations
            if obs.observation_type in ["bugfix", "discovery"]
            and "warning" in obs.title.lower()
            or "risk" in obs.title.lower()
            or "issue" in obs.title.lower()
        ]
        if warnings:
            sections.append("## Warnings from History")
            sections.append("")
            sections.append(
                "Issues, gotchas, and edge cases discovered in prior phases."
            )
            sections.append("")

            for obs in warnings:
                sections.append(f"### ⚠️ {obs.title}")
                sections.append("")
                sections.append(obs.content)
                sections.append("")

        # ====================================================================
        # SECTION 3: LEARNINGS & PRECEDENTS
        # ====================================================================

        learnings = [
            obs
            for obs in self.observations
            if obs.observation_type in ["pattern", "discovery", "learning"]
        ]
        if learnings:
            sections.append("## Learnings & Precedents")
            sections.append("")
            sections.append(
                "Patterns, conventions, and technical insights from prior work."
            )
            sections.append("")

            # Group by category
            by_cat: Dict[str, List[EngramObservation]] = {}
            for obs in learnings:
                cat = obs.category()
                if cat not in by_cat:
                    by_cat[cat] = []
                by_cat[cat].append(obs)

            for cat in sorted(by_cat.keys()):
                sections.append(f"### {cat}")
                sections.append("")
                for obs in by_cat[cat]:
                    sections.append(f"- **{obs.title}**: {obs.content[:100]}...")
                sections.append("")

        # ====================================================================
        # SECTION 4: CROSS-PHASE CONTRACTS
        # ====================================================================

        sections.append("## Cross-Phase Contracts")
        sections.append("")
        sections.append("Agreements and invariants that span multiple phases:")
        sections.append("")

        sections.append(
            "- Phases must not contradict prior decisions without Brain #7 approval"
        )
        sections.append(
            "- All PRs must reference the phase they're completing (git commit trailer)"
        )
        sections.append("- Test suite must pass before marking phase complete")
        sections.append("- Documentation must be updated alongside code changes")
        sections.append("")

        # ====================================================================
        # FOOTER
        # ====================================================================

        sections.append("---")
        sections.append("")
        sections.append(
            f"*Context generated by EngramContextLoader for phase {self.phase_num}*"
        )
        sections.append(
            "*To update this context, save observations to Engram with type=decision, type=discovery, etc.*"
        )

        return "\n".join(sections)


# ============================================================================
# CLI INTEGRATION (called from commands.py)
# ============================================================================


def generate_context_for_phase(
    project: str,
    phase_num: int,
) -> Optional[Path]:
    """
    Convenience function: generate context for a phase.

    Called by `mm-flow context --phase N` command.

    Args:
        project: Project name
        phase_num: Phase number

    Returns:
        Path to generated CONTEXT.md, or None if failed.
    """
    loader = EngramContextLoader(project=project, phase_num=phase_num)
    return loader.generate_context_md()


__all__ = [
    "EngramContextLoader",
    "EngramObservation",
    "generate_context_for_phase",
]
