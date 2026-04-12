"""
TokenLimiter: enforce safeguards — minimum tokens, checkpoint intervals, iteration caps.

Used by night_mode and the state machine to decide whether to continue or pause.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, cast

import psycopg2
import psycopg2.extras

from .config import (
    BACKENDS,
    BACKEND_PRIORITY,
    CONTEXT_CHECKPOINT_INTERVAL,
    MAX_ITERATIONS_PER_PHASE,
)

logger = logging.getLogger(__name__)

# Additional safeguard for night mode: never continue if all backends < this
MIN_TOKENS_SAFETY = 10_000


class TokenLimiter:
    """Enforces token budgets and decides when to switch, checkpoint, or stop."""

    def __init__(self, org_id: str, project_id: str, db_url: str) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def check_token_availability(self, required_tokens: int) -> bool:
        """
        Return True if any backend has at least required_tokens available.

        Args:
            required_tokens: Tokens needed for the next operation.

        Returns:
            True if at least one backend can service the request.
        """
        best = self._best_available()
        if best is None:
            return False
        available = best["tokens_available"]
        if available < required_tokens:
            logger.warning(
                "Best backend '%s' has %d tokens — need %d.",
                best["backend"],
                available,
                required_tokens,
            )
            return False
        return True

    def should_checkpoint(self, tokens_used_since_last: int) -> bool:
        """
        Return True if it's time to save a context checkpoint.

        Args:
            tokens_used_since_last: Tokens consumed since last checkpoint.

        Returns:
            True when the checkpoint interval threshold is reached.
        """
        return tokens_used_since_last >= CONTEXT_CHECKPOINT_INTERVAL

    def can_continue_phase(self, iteration_count: int) -> bool:
        """
        Return True if the phase hasn't exceeded the max retry limit.

        Args:
            iteration_count: Number of iterations attempted so far.

        Returns:
            False when iteration_count >= MAX_ITERATIONS_PER_PHASE.
        """
        if iteration_count >= MAX_ITERATIONS_PER_PHASE:
            logger.warning(
                "Phase reached max iterations (%d). Escalating to human.",
                MAX_ITERATIONS_PER_PHASE,
            )
            return False
        return True

    def is_safe_for_night_mode(self) -> bool:
        """
        Return True if any backend has at least MIN_TOKENS_SAFETY tokens.

        Night mode should pause entirely if this returns False.
        """
        return self.check_token_availability(MIN_TOKENS_SAFETY)

    def get_best_backend_info(self) -> Optional[Dict]:
        """
        Return info on the backend with the most tokens.

        Returns:
            Dict with keys: backend, tokens_available, tokens_limit, tokens_used.
            None if no sessions found.
        """
        return self._best_available()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def _best_available(self) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT backend, tokens_used, tokens_limit,
                           reset_cycle_hours, last_reset
                    FROM backend_sessions
                    WHERE project_id = %s
                    """,
                    (self.project_id,),
                )
                rows: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cur.fetchall())

        if not rows:
            # Fallback: return first priority backend with full limit
            name = BACKEND_PRIORITY[0]
            cfg = BACKENDS[name]
            return {
                "backend": name,
                "tokens_available": cfg.token_limit,
                "tokens_limit": cfg.token_limit,
                "tokens_used": 0,
            }

        best = None
        best_tokens = -1

        for row_tuple in rows:
            from datetime import datetime, timezone

            row = cast(Dict[str, Any], row_tuple)
            last_reset = row["last_reset"]
            if last_reset.tzinfo is None:
                last_reset = last_reset.replace(tzinfo=timezone.utc)
            elapsed = (datetime.now(timezone.utc) - last_reset).total_seconds() / 3600
            if elapsed >= row["reset_cycle_hours"]:
                available = row["tokens_limit"]
            else:
                available = max(0, row["tokens_limit"] - row["tokens_used"])

            if available > best_tokens:
                best_tokens = available
                best = {
                    "backend": row["backend"],
                    "tokens_available": available,
                    "tokens_limit": row["tokens_limit"],
                    "tokens_used": row["tokens_used"],
                }

        return best
