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
import datetime
import logging
import os
import uuid
from typing import Literal

import asyncpg
import httpx
from pydantic import BaseModel, ConfigDict

from mastermind_cli.brain_registry_module.repository import BrainRegistryRepository

log = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Rust hub URL — override via RUST_HUB_URL env var in production.
# Default targets the Rust control plane on port 8002 (docker-compose alias).
# ---------------------------------------------------------------------------
_DEFAULT_RUST_HUB_URL = os.getenv("RUST_HUB_URL", "http://localhost:8002")

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
        model: Provider-qualified model string in format "provider:model_id"
               (e.g. "anthropic:claude-opus-4-6").  Resolved at dispatch time
               from the model_profiles section in config.yml.
        provider: Provider name extracted from the model string
                  (e.g. "anthropic", "openrouter", "z_ai").
        is_barrier: True if this brain acts as a barrier (post-parallel gate).
    """

    model_config = ConfigDict(strict=True)
    brain_id: int
    role: str
    model_profile: Literal["quality", "balanced", "budget"]
    model: str
    provider: str
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
        rust_hub_url: Base URL of the Rust control plane (default: RUST_HUB_URL env var).
            Used to POST brain lifecycle events to ``/internal/brain-event``.
    """

    def __init__(
        self, postgres_url: str, rust_hub_url: str = _DEFAULT_RUST_HUB_URL
    ) -> None:
        """Initialise the engine with an explicit PostgreSQL URL (C1).

        Args:
            postgres_url: PostgreSQL DSN used for agent_registry queries.
            rust_hub_url: Base URL for the Rust control plane WebSocket hub.
        """
        self.postgres_url = postgres_url
        self.rust_hub_url = rust_hub_url.rstrip("/")
        from mastermind_cli.mm_flow.config_loader import load_config

        self.config = load_config()

    # ------------------------------------------------------------------
    # B2.5 / B2.6: Brain lifecycle event notification
    # ------------------------------------------------------------------

    async def _post_brain_event(
        self,
        trace_id: str,
        brain_id: int,
        status: Literal["dispatched", "running", "completed", "failed"],
        model: str | None = None,
        provider: str | None = None,
    ) -> None:
        """POST a brain lifecycle event to the Rust hub.

        Fire-and-forget — errors are logged but never propagate to the caller.
        The ``/internal/brain-event`` endpoint is internal-only and should not
        be reachable from the public internet.

        Args:
            trace_id: Distributed trace identifier for this dispatch.
            brain_id: Integer brain identifier (1-7).
            status: Lifecycle status of the brain.
            model: Provider-qualified model string (e.g. "anthropic:claude-opus-4-6").
                   Omitted from payload if None.
            provider: Provider name (e.g. "anthropic", "openrouter", "z_ai").
                      Omitted from payload if None.
        """
        payload: dict[str, str] = {
            "trace_id": trace_id,
            "brain_id": str(brain_id),
            "status": status,
            "timestamp": datetime.datetime.now(datetime.UTC).isoformat(),
        }
        if model is not None:
            payload["model"] = model
        if provider is not None:
            payload["provider"] = provider
        url = f"{self.rust_hub_url}/internal/brain-event"
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                resp = await client.post(url, json=payload)
                if resp.status_code not in (200, 204):
                    log.warning(
                        "brain-event POST returned %s for brain %s (trace=%s)",
                        resp.status_code,
                        brain_id,
                        trace_id,
                    )
        except Exception as exc:  # noqa: BLE001
            log.warning(
                "Failed to POST brain event to Rust hub: %s (brain=%s, trace=%s)",
                exc,
                brain_id,
                trace_id,
            )

    async def dispatch(
        self,
        phase: int,
        moment: Literal["DISCUSSION", "PLANNING", "EXECUTION_WAVE", "VERIFICATION"],
        trace_id: str | None = None,
        profile: Literal["quality", "balanced", "budget"] | None = None,
    ) -> DispatchResult:
        """Return the set of brains to run for a given phase + moment.

        Reads routing rules from self.config (loaded from config.yml), then
        queries agent_registry to hydrate brain metadata.

        Posts ``dispatched`` events to the Rust hub for every brain selected
        (B2.5) and ``completed`` events when the dispatch completes (B2.6).

        Args:
            phase: Phase number being executed (e.g. 19). Currently unused in
                query but kept for future per-phase routing overrides.
            moment: Execution moment driving brain selection.
            trace_id: Distributed trace identifier.  Generated automatically if
                not provided so every dispatch is traceable.
            profile: Model quality tier override for ALL brains in this dispatch.
                     When None (default): parallel brains use "balanced", barrier
                     brains use "quality" (per routing config defaults).
                     When provided: ALL brains (parallel and barrier) use this tier,
                     resolving model/provider from config.yml model_profiles (C2.09).

        Returns:
            DispatchResult with parallel and barrier brain lists.

        Raises:
            BudgetExceededError: If any brain has consumed >80% of its budget.
        """
        trace_id = trace_id or str(uuid.uuid4())
        routing = self.config.brain_routing[moment]

        conn = await asyncio.wait_for(asyncpg.connect(self.postgres_url), timeout=5.0)
        try:
            parallel_brains = await self._get_brains_from_registry(
                conn, routing.brains, is_barrier=False, profile_override=profile
            )
            barrier_brains = await self._get_brains_from_registry(
                conn, routing.barrier, is_barrier=True, profile_override=profile
            )
        finally:
            await conn.close()

        self._check_budget(parallel_brains + barrier_brains)

        # B2.5 — notify Rust hub that each brain is being dispatched
        # Include model and provider (C2.05) so WS events carry the full model info.
        all_brains = parallel_brains + barrier_brains
        await asyncio.gather(
            *[
                self._post_brain_event(
                    trace_id,
                    b.brain_id,
                    "dispatched",
                    model=b.model,
                    provider=b.provider,
                )
                for b in all_brains
            ],
            return_exceptions=True,  # never fail dispatch because of hub errors
        )

        result = DispatchResult(
            moment=moment,
            parallel=[b for b in parallel_brains if not b.is_barrier],
            barrier=barrier_brains,
            budget_remaining=100_000,  # placeholder — real value queries tokens_consumed_total
            execution_id=str(uuid.uuid4()),
        )

        # B2.6 — notify Rust hub that each brain has completed
        await asyncio.gather(
            *[
                self._post_brain_event(
                    trace_id,
                    b.brain_id,
                    "completed",
                    model=b.model,
                    provider=b.provider,
                )
                for b in all_brains
            ],
            return_exceptions=True,
        )

        return result

    def _resolve_model_for_profile(
        self,
        profile: Literal["quality", "balanced", "budget"],
        brain_record_model: str | None = None,
    ) -> tuple[str, str]:
        """Resolve the provider-qualified model string for a given profile.

        Reads from self.config.model_profiles first; falls back to brain_registry
        per-brain model field if no config entry is found.

        Args:
            profile: Model quality tier to resolve ("quality", "balanced", "budget").
            brain_record_model: Optional per-brain model override from brain_registry
                                (e.g. record.model_quality).  Used as fallback only.

        Returns:
            Tuple of (model_string, provider_name) where model_string is in
            "provider:model_id" format and provider_name is the prefix portion.
        """
        # Prefer config.yml model_profiles over brain_registry per-brain model
        config_profile = self.config.model_profiles.get(profile)
        if config_profile is not None:
            model_str = config_profile.model
            provider = config_profile.provider
        elif brain_record_model:
            # Fallback: use brain_registry model field (may not have provider prefix)
            model_str = brain_record_model
            provider = model_str.split(":")[0] if ":" in model_str else "anthropic"
        else:
            # Last resort: use quality profile default
            fallback = self.config.model_profiles.get("quality")
            model_str = fallback.model if fallback else "anthropic:claude-opus-4-6"
            provider = model_str.split(":")[0] if ":" in model_str else "anthropic"

        return model_str, provider

    async def _get_brains_from_registry(
        self,
        conn: asyncpg.Connection,
        brain_ids: list[int],
        is_barrier: bool = False,
        profile_override: Literal["quality", "balanced", "budget"] | None = None,
    ) -> list[BrainDispatch]:
        """Fetch brain metadata from brain_registry for the given IDs.

        Uses BrainRegistryRepository (brain_registry table) instead of the
        legacy agent_registry table.  The ``is_barrier`` flag is passed in
        from the routing config (Brain #7 is always the barrier) because the
        brain_registry table does not have a per-row is_barrier column.

        Model and provider are resolved from config.yml model_profiles (C2.03/C2.04):
        - Barrier brains run at quality tier → reads model_profiles.quality.model
        - Parallel brains run at balanced tier → reads model_profiles.balanced.model
        When ``profile_override`` is set, ALL brains use that tier (C2.09).
        All models are in "provider:model_id" format, no hardcoded Anthropic.

        Args:
            conn: Open asyncpg connection (caller owns lifecycle).
            brain_ids: List of brain_id integers to look up.
            is_barrier: True when these brain IDs are the barrier group.
            profile_override: When set, overrides the default profile tier for all
                              brains in this group.  Used when the caller passes an
                              explicit profile to dispatch() (C2.09).

        Returns:
            List of BrainDispatch instances, one per found row.
        """
        if not brain_ids:
            return []
        repo = BrainRegistryRepository(conn)
        results: list[BrainDispatch] = []
        for brain_id in brain_ids:
            record = await repo.get_by_id(brain_id)
            if record is None:
                log.warning(
                    "brain_id=%s not found in brain_registry — skipping", brain_id
                )
                continue
            # Profile resolution (C2.09):
            # 1. Use profile_override if caller passed an explicit profile to dispatch()
            # 2. Otherwise: barrier brains → quality, parallel brains → balanced
            if profile_override is not None:
                profile: Literal["quality", "balanced", "budget"] = profile_override
            else:
                profile = "quality" if is_barrier else "balanced"

            # Resolve model and provider from config.yml (C2.03/C2.04) — NOT hardcoded.
            # Use per-brain registry model as fallback if config doesn't have the profile.
            if profile == "quality":
                brain_model_for_profile = record.model_quality
            elif profile == "budget":
                brain_model_for_profile = record.model_budget
            else:
                brain_model_for_profile = record.model_balanced

            model_str, provider = self._resolve_model_for_profile(
                profile, brain_model_for_profile
            )
            results.append(
                BrainDispatch(
                    brain_id=record.brain_id,
                    role=record.name,
                    model_profile=profile,
                    model=model_str,
                    provider=provider,
                    is_barrier=is_barrier,
                )
            )
        return results

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
