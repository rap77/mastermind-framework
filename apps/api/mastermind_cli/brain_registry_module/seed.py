"""
Brain Registry seed script.

Inserts the 8 default MasterMind brain agents into brain_registry.
Reads capabilities and trigger conditions from the agent definition files
under .claude/agents/mm/.

Usage:
    uv run python -m mastermind_cli.brain_registry_module.seed
    DATABASE_URL=postgresql://... uv run python -m mastermind_cli.brain_registry_module.seed
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys

import asyncpg

log = logging.getLogger(__name__)

_DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres@localhost:5434/mastermind_bd",
)

# ---------------------------------------------------------------------------
# Brain definitions extracted from the canonical brain registry config.
# ---------------------------------------------------------------------------
#
# Fields per row:
#   brain_id        : int  (1-8, matches agent numbering)
#   name            : str  (human-readable)
#   model_quality   : str  (claude-opus-4-6 — used for critical decisions)
#   model_balanced  : str  (claude-sonnet-4-6 — standard domain brains)
#   model_budget    : str  (claude-haiku-4-5 — context checks)
#   capabilities    : list[str] (domain expertise areas)
#   trigger_conditions: list[str] (when to activate this brain)
#   enabled         : bool

BRAIN_SEED_DATA: list[dict[str, object]] = [
    {
        "brain_id": 1,
        "name": "Product Strategy",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "product-discovery",
            "feature-evaluation",
            "roadmap-strategy",
            "outcome-metrics",
            "user-pain-validation",
            "okr-definition",
            "opportunity-mapping",
        ],
        "trigger_conditions": [
            "should we build",
            "feature request",
            "product decision",
            "milestone planning",
            "user pain",
            "what to build",
            "product strategy",
            "roadmap",
        ],
        "enabled": True,
    },
    {
        "brain_id": 2,
        "name": "UX Research",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "user-flow-design",
            "usability-evaluation",
            "interaction-patterns",
            "cognitive-load-reduction",
            "heuristic-evaluation",
            "mental-model-mapping",
            "friction-analysis",
        ],
        "trigger_conditions": [
            "user flow",
            "navigation",
            "usability",
            "interaction design",
            "ux",
            "user experience",
            "3 clicks",
            "findability",
        ],
        "enabled": True,
    },
    {
        "brain_id": 3,
        "name": "UI Design",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "visual-design",
            "component-aesthetics",
            "animation-patterns",
            "interaction-polish",
            "design-systems",
            "minimalist-design",
            "typography",
            "color-theory",
        ],
        "trigger_conditions": [
            "visual design",
            "component design",
            "animation",
            "look and feel",
            "ui",
            "aesthetics",
            "design system",
            "how should it look",
        ],
        "enabled": True,
    },
    {
        "brain_id": 4,
        "name": "Frontend",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "frontend-architecture",
            "component-composition",
            "performance-optimization",
            "state-management",
            "websocket-integration",
            "react-flow",
            "bundle-optimization",
            "render-performance",
        ],
        "trigger_conditions": [
            "frontend",
            "react",
            "component architecture",
            "state management",
            "websocket",
            "renders",
            "bundle",
            "performance",
            "react flow",
        ],
        "enabled": True,
    },
    {
        "brain_id": 5,
        "name": "Backend",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "api-design",
            "data-modeling",
            "async-patterns",
            "domain-driven-design",
            "event-sourcing",
            "type-safety",
            "service-boundaries",
            "database-design",
        ],
        "trigger_conditions": [
            "api design",
            "backend",
            "database",
            "async",
            "service",
            "domain model",
            "type safety",
            "architecture",
        ],
        "enabled": True,
    },
    {
        "brain_id": 6,
        "name": "QA/DevOps",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "test-strategy",
            "ci-cd-design",
            "reliability-engineering",
            "change-risk-evaluation",
            "deployment-strategy",
            "observability",
            "incident-response",
        ],
        "trigger_conditions": [
            "testing",
            "ci/cd",
            "deployment",
            "reliability",
            "risk",
            "qa",
            "devops",
            "monitoring",
            "observability",
        ],
        "enabled": True,
    },
    {
        "brain_id": 7,
        "name": "Growth/Data",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "cross-domain-synthesis",
            "second-order-effects",
            "systems-thinking",
            "metrics-evaluation",
            "experimentation-design",
            "barrier-validation",
            "consensus-evaluation",
        ],
        "trigger_conditions": [
            "barrier",
            "verification",
            "cross-domain",
            "synthesis",
            "second order",
            "metrics",
            "evaluation",
            "approve",
            "reject",
        ],
        "enabled": True,
    },
    {
        "brain_id": 8,
        "name": "Master Interviewer",
        "model_quality": "claude-opus-4-6",
        "model_balanced": "claude-sonnet-4-6",
        "model_budget": "claude-haiku-4-5",
        "capabilities": [
            "discovery",
            "requirements-clarification",
            "problem-definition",
            "socratic-questioning",
            "gap-detection",
            "interview-methodology",
            "brief-analysis",
        ],
        "trigger_conditions": [
            "brief",
            "vago",
            "ambiguo",
            "no sé qué necesito",
            "descubrimiento",
            "discovery",
            "requirements",
            "clarify",
        ],
        "enabled": True,
    },
]


async def seed_brain_registry(database_url: str = _DEFAULT_DATABASE_URL) -> int:
    """Insert the 8 default brain rows into brain_registry.

    Uses ON CONFLICT DO NOTHING so re-runs are safe (idempotent).

    Args:
        database_url: PostgreSQL DSN to connect to.

    Returns:
        Number of rows inserted (0 if all already existed).

    Raises:
        asyncpg.PostgresError: If any INSERT fails.
    """
    conn: asyncpg.Connection = await asyncpg.connect(database_url)
    try:
        inserted = 0
        for brain in BRAIN_SEED_DATA:
            result = await conn.execute(
                """
                INSERT INTO brain_registry
                    (brain_id, name, model_quality, model_balanced, model_budget,
                     capabilities, trigger_conditions, enabled)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
                ON CONFLICT (brain_id) DO NOTHING
                """,
                brain["brain_id"],
                brain["name"],
                brain["model_quality"],
                brain["model_balanced"],
                brain["model_budget"],
                brain["capabilities"],
                brain["trigger_conditions"],
                brain["enabled"],
            )
            # asyncpg returns "INSERT 0 N" or "INSERT 0 0"
            if result.endswith(" 1"):
                inserted += 1
                log.info("Inserted brain_id=%s (%s)", brain["brain_id"], brain["name"])
            else:
                log.info(
                    "Skipped brain_id=%s (%s) — already exists",
                    brain["brain_id"],
                    brain["name"],
                )

        # Verify final count
        count = await conn.fetchval("SELECT COUNT(*) FROM brain_registry")
        log.info("brain_registry row count: %s", count)
        return inserted
    finally:
        await conn.close()


def main() -> None:
    """Entry point for running seed from the CLI."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    url = _DEFAULT_DATABASE_URL
    inserted = asyncio.run(seed_brain_registry(url))
    sys.stdout.write(f"Seed complete: {inserted} new brain(s) inserted.\n")


if __name__ == "__main__":
    main()
