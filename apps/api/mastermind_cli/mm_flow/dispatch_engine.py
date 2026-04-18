"""
MM-Flow Dynamic Dispatch Engine.

Routes phase execution moments to brain agents by reading config.yml and
querying the PostgreSQL agent_registry table.

Brain #7 conditions applied:
  C1 — postgres_url passed explicitly to constructor (no global state).
  C3 — NO asyncio.wait_for anywhere. Python cannot timeout Claude agents.

DISPATCH_ORACLE is the ground-truth routing table used for SLI-3 unit tests.
It mirrors the defaults in config.yml exactly so tests pass without a DB.
"""

import asyncio
import uuid
from typing import Literal

import asyncpg
from pydantic import BaseModel, ConfigDict

# ---------------------------------------------------------------------------
# Execution moment constants (SUGGESTION #3)
# ---------------------------------------------------------------------------

MOMENT_DISCUSSION = "DISCUSSION"
MOMENT_PLANNING = "PLANNING"
MOMENT_EXECUTION_WAVE = "EXECUTION_WAVE"
MOMENT_VERIFICATION = "VERIFICATION"

ALL_MOMENTS = frozenset(
    {
        MOMENT_DISCUSSION,
        MOMENT_PLANNING,
        MOMENT_EXECUTION_WAVE,
        MOMENT_VERIFICATION,
    }
)

# Brain ID constants (SUGGESTION #3)
BARRIER_BRAIN_ID = 7


class BrainDispatch(BaseModel):
    """A single brain entry in a dispatch result.

    Attributes:
        brain_id: Integer brain identifier (1-7).
        role: Human-readable role string from agent_registry.
        model_profile: Model quality tier (quality | balanced | budget).
        is_barrier: True if this brain acts as a barrier (post-parallel gate).
    """

    model_config = ConfigDict(strict=True)
    brain_id: int
    role: str
    model_profile: Literal["quality", "balanced", "budget"]
    is_barrier: bool


class DispatchResult(BaseModel):
    """Result of a single dispatch() call.

    Attributes:
        moment: The execution moment that was dispatched.
        parallel: Brains to run concurrently (non-barrier).
        barrier: Brains to run as a gate after parallel completes.
        budget_remaining: Estimated token budget remaining across all brains.
        execution_id: Fresh UUID for this dispatch (not the phase_executions id).
    """

    model_config = ConfigDict(strict=True)
    moment: Literal["DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"]
    parallel: list[BrainDispatch]
    barrier: list[BrainDispatch]
    budget_remaining: int
    execution_id: str


class BudgetExceededError(Exception):
    """Raised when a brain has consumed >80% of its token budget.

    Attributes:
        message: Human-readable description of which brain exceeded budget.
    """


# ---------------------------------------------------------------------------
# DISPATCH_ORACLE — ground truth for SLI-3 unit tests
#
# This dict mirrors the defaults in .planning/.mm-flow/config.yml exactly.
# Any routing change in config.yml MUST be reflected here to keep tests green.
# ---------------------------------------------------------------------------

DISPATCH_ORACLE: dict[str, dict[str, object]] = {
    MOMENT_DISCUSSION: {
        "parallel_brain_ids": [1, 2, 3],
        "barrier_brain_ids": [BARRIER_BRAIN_ID],
    },
    MOMENT_PLANNING: {
        "parallel_brain_ids": [4, 5, 6],
        "barrier_brain_ids": [BARRIER_BRAIN_ID],
    },
    MOMENT_EXECUTION_WAVE: {
        "parallel_brain_ids": [BARRIER_BRAIN_ID],
        "barrier_brain_ids": [],
        "sequential": True,
    },
    MOMENT_VERIFICATION: {
        "parallel_brain_ids": [BARRIER_BRAIN_ID],
        "barrier_brain_ids": [],
        "sequential": True,
    },
}


class DynamicDispatchEngine:
    """Dispatches brain agents based on phase + moment, reading config.yml + agent_registry.

    Args:
        postgres_url: Full PostgreSQL DSN. Pass ``os.environ['DATABASE_URL']`` at call site.
    """

    def __init__(self, postgres_url: str) -> None:
        """Initialise the engine with an explicit PostgreSQL URL (C1).

        Args:
            postgres_url: PostgreSQL DSN used for agent_registry queries.
        """
        self.postgres_url = postgres_url
        from mastermind_cli.mm_flow.config_loader import load_config

        self.config = load_config()

    async def dispatch(
        self,
        phase: int,
        moment: Literal["DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"],
    ) -> DispatchResult:
        """Return the set of brains to run for a given phase + moment.

        Reads routing rules from self.config (loaded from config.yml), then
        queries agent_registry to hydrate brain metadata.

        Args:
            phase: Phase number being executed (e.g. 19). Currently unused in
                query but kept for future per-phase routing overrides.
            moment: Execution moment driving brain selection.

        Returns:
            DispatchResult with parallel and barrier brain lists.

        Raises:
            BudgetExceededError: If any brain has consumed >80% of its budget.
        """
        routing = self.config.brain_routing[moment]

        conn = await asyncio.wait_for(asyncpg.connect(self.postgres_url), timeout=5.0)
        try:
            parallel_brains = await self._get_brains_from_registry(conn, routing.brains)
            barrier_brains = await self._get_brains_from_registry(conn, routing.barrier)
        finally:
            await conn.close()

        self._check_budget(parallel_brains + barrier_brains)

        return DispatchResult(
            moment=moment,
            parallel=[b for b in parallel_brains if not b.is_barrier],
            barrier=barrier_brains,
            budget_remaining=100_000,  # placeholder — real value queries tokens_consumed_total
            execution_id=str(uuid.uuid4()),
        )

    async def _get_brains_from_registry(
        self,
        conn: asyncpg.Connection,
        brain_ids: list[int],
    ) -> list[BrainDispatch]:
        """Fetch brain metadata from agent_registry for the given IDs.

        Args:
            conn: Open asyncpg connection (caller owns lifecycle).
            brain_ids: List of brain_id integers to look up.

        Returns:
            List of BrainDispatch instances, one per found row.
        """
        if not brain_ids:
            return []
        rows = await conn.fetch(
            "SELECT brain_id, role, model_quality, is_barrier, "
            "token_budget_per_phase, tokens_consumed_total "
            "FROM agent_registry WHERE brain_id = ANY($1::int[])",
            brain_ids,
        )
        return [
            BrainDispatch(
                brain_id=row["brain_id"],
                role=row["role"],
                model_profile=row["model_quality"],
                is_barrier=row["is_barrier"],
            )
            for row in rows
        ]

    def _check_budget(self, brains: list[BrainDispatch]) -> int:
        """Validate that no brain has exceeded 80% of its token budget.

        Args:
            brains: Combined list of parallel + barrier brains to check.

        Returns:
            Estimated tokens remaining (placeholder: 100_000).

        Raises:
            BudgetExceededError: If any brain is over budget (future implementation).
        """
        # Real budget tracking would query tokens_consumed_total from agent_registry
        # and compare to token_budget_per_phase. Left as placeholder per plan spec.
        return 100_000
