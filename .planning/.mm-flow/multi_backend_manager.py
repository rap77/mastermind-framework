"""
MultiBackendManager: smart backend selection and token tracking.

Selects the best available backend for a project, switches when tokens are low,
and checkpoints context before every switch.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

import psycopg2
import psycopg2.extras

from config import BACKENDS, BACKEND_PRIORITY, MIN_TOKENS_FOR_SWITCH

logger = logging.getLogger(__name__)


class MultiBackendManager:
    """Manages backend selection and token-aware switching for a project."""

    def __init__(self, org_id: str, project_id: str, db_url: str) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_best_available_backend(self) -> Dict[str, Any]:
        """
        Return the backend with the most available tokens for this project.

        Checks active backend_sessions, resets depleted sessions whose reset
        cycle has elapsed, then ranks by available tokens.

        Returns:
            Dict with keys: backend, tokens_available, tokens_limit,
            tokens_used, reset_cycle_hours, session_id
        """
        with self._connect() as conn:
            sessions = self._fetch_active_sessions(conn)

        ranked = []
        for s in sessions:
            available = self._compute_available_tokens(s)
            ranked.append(
                {
                    "backend": s["backend"],
                    "tokens_available": available,
                    "tokens_limit": s["tokens_limit"],
                    "tokens_used": s["tokens_used"],
                    "reset_cycle_hours": s["reset_cycle_hours"],
                    "session_id": str(s["id"]),
                }
            )

        ranked.sort(key=lambda x: x["tokens_available"], reverse=True)

        if not ranked:
            # Fallback to first priority backend with full tokens
            default = BACKENDS[BACKEND_PRIORITY[0]]
            return {
                "backend": BACKEND_PRIORITY[0],
                "tokens_available": default.token_limit,
                "tokens_limit": default.token_limit,
                "tokens_used": 0,
                "reset_cycle_hours": default.reset_cycle_hours,
                "session_id": None,
            }

        best = ranked[0]
        if best["tokens_available"] < MIN_TOKENS_FOR_SWITCH and len(ranked) > 1:
            logger.warning(
                "Best backend '%s' has only %d tokens — triggering switch.",
                best["backend"],
                best["tokens_available"],
            )
            self.track_token_depletion(best["backend"], best["tokens_available"])  # type: ignore[attr-defined]
            next_best = ranked[1]
            self.switch_backend(best["backend"], next_best["backend"])
            return next_best

        return best

    def switch_backend(self, from_backend: str, to_backend: str) -> Dict[str, Any]:
        """
        Switch from one backend to another.

        1. Save a context checkpoint with reason='backend_switch'.
        2. Mark old session as ended.
        3. Activate new session (or create one if missing).

        Returns:
            Dict with switch metadata.
        """
        logger.info("Switching backend: %s → %s", from_backend, to_backend)
        self.checkpoint_before_switch(from_backend, to_backend)

        with self._connect() as conn:
            with conn.cursor() as cur:
                # End old session
                cur.execute(
                    """
                    UPDATE backend_sessions
                    SET is_active = FALSE, session_ended = NOW(), updated_at = NOW()
                    WHERE project_id = %s AND backend = %s AND is_active = TRUE
                    """,
                    (self.project_id, from_backend),
                )
                # Activate or create new session
                cur.execute(
                    """
                    UPDATE backend_sessions
                    SET is_active = TRUE, session_started = NOW(),
                        session_ended = NULL, updated_at = NOW()
                    WHERE project_id = %s AND backend = %s AND is_active = FALSE
                    """,
                    (self.project_id, to_backend),
                )
                if cur.rowcount == 0:
                    cfg = BACKENDS[to_backend]
                    cur.execute(
                        """
                        INSERT INTO backend_sessions
                            (org_id, project_id, backend, tokens_used, tokens_limit,
                             reset_cycle_hours, is_active)
                        VALUES (%s, %s, %s, 0, %s, %s, TRUE)
                        """,
                        (
                            self.org_id,
                            self.project_id,
                            to_backend,
                            cfg.token_limit,
                            cfg.reset_cycle_hours,
                        ),
                    )
            conn.commit()

        logger.info("Switch complete: now using '%s'", to_backend)
        return {
            "from": from_backend,
            "to": to_backend,
            "switched_at": datetime.now(timezone.utc).isoformat(),
        }

    def track_token_depletion(self, backend: str, tokens_remaining: int) -> None:
        """
        Record depletion event when tokens fall below MIN_TOKENS_FOR_SWITCH.

        Sets depletion_timestamp and calculates next_reset_time so the countdown
        can be displayed in mm-flow status.

        Args:
            backend: Backend key that was depleted.
            tokens_remaining: Tokens left at depletion time.
        """
        if tokens_remaining >= MIN_TOKENS_FOR_SWITCH:
            return  # Not actually depleted yet

        now = datetime.now(timezone.utc)
        next_reset = self._calculate_next_reset_time(backend, now)

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE backend_sessions
                    SET depletion_timestamp = %s,
                        next_reset_time = %s,
                        updated_at = NOW()
                    WHERE project_id = %s AND backend = %s AND is_active = TRUE
                    """,
                    (now, next_reset, self.project_id, backend),
                )
            conn.commit()

        logger.warning(
            "Backend '%s' depleted (%d tokens remaining). Next reset: %s",
            backend,
            tokens_remaining,
            next_reset.isoformat(),
        )

    def _calculate_next_reset_time(self, backend: str, from_time: datetime) -> datetime:
        """
        Calculate when this backend will reset next.

        Args:
            backend: Backend key.
            from_time: Reference timestamp (usually now or depletion time).

        Returns:
            UTC datetime of the next reset.
        """
        config = BACKENDS[backend]
        return from_time + timedelta(hours=config.reset_cycle_hours)

    def checkpoint_before_switch(
        self,
        from_backend: str,
        to_backend: str,
        state_data: Optional[Dict[str, Any]] = None,
        conversation_history: Optional[list] = None,
    ) -> None:
        """
        Save a context_checkpoints row with reason='backend_switch'.

        Reads current mm_flow_state for this project to capture phase + state_data.
        """
        state_data = state_data or {}
        conversation_history = conversation_history or []

        with self._connect() as conn:
            current_state = self._fetch_current_state(conn)
            workspace_id = self._fetch_workspace_id(conn)

            phase = current_state.get("phase", 1) if current_state else 1
            if current_state and not state_data:
                state_data = current_state.get("state_data", {})
            tokens_at = current_state.get("tokens_consumed", 0) if current_state else 0

            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO context_checkpoints
                        (org_id, project_id, workspace_id, phase, reason,
                         state_data, conversation_history, from_backend, to_backend,
                         tokens_at_checkpoint)
                    VALUES (%s, %s, %s, %s, 'backend_switch',
                            %s, %s, %s, %s, %s)
                    """,
                    (
                        self.org_id,
                        self.project_id,
                        workspace_id,
                        phase,
                        psycopg2.extras.Json(state_data),
                        psycopg2.extras.Json(conversation_history),
                        from_backend,
                        to_backend,
                        tokens_at,
                    ),
                )
            conn.commit()

        logger.debug("Checkpoint saved before switch %s → %s", from_backend, to_backend)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> psycopg2.extensions.connection:
        """Return a psycopg2 connection with dict cursor factory."""
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def _fetch_active_sessions(
        self, conn: psycopg2.extensions.connection
    ) -> List[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, backend, tokens_used, tokens_limit,
                       reset_cycle_hours, last_reset, session_started,
                       next_reset_time, depletion_timestamp
                FROM backend_sessions
                WHERE project_id = %s
                ORDER BY
                    CASE backend
                        WHEN 'z_ai'       THEN 1
                        WHEN 'openrouter' THEN 2
                        WHEN 'claude'     THEN 3
                        ELSE 99
                    END
                """,
                (self.project_id,),
            )
            return cast(List[Dict[str, Any]], cur.fetchall())

    def _fetch_current_state(
        self, conn: psycopg2.extensions.connection
    ) -> Optional[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT phase, status, state_data, tokens_consumed
                FROM mm_flow_state
                WHERE project_id = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (self.project_id,),
            )
            row = cur.fetchone()
            return cast(Dict[str, Any], row) if row else None

    def _fetch_workspace_id(self, conn: psycopg2.extensions.connection) -> str:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM workspaces WHERE project_id = %s LIMIT 1",
                (self.project_id,),
            )
            _raw = cur.fetchone()
            row: Optional[Dict[str, Any]] = cast(Dict[str, Any], _raw) if _raw else None
            return str(row["id"]) if row else "00000000-0000-0000-0000-000000000000"

    def _compute_available_tokens(self, session: Dict[str, Any]) -> int:
        """
        Available tokens = limit - used, unless reset cycle has elapsed.
        If cycle elapsed, reset tokens_used to 0 in DB and return full limit.
        """
        if self._reset_cycle_completed(session):
            self._reset_session_tokens(session)
            return session["tokens_limit"]
        return max(0, session["tokens_limit"] - session["tokens_used"])

    def _reset_cycle_completed(self, session: Dict[str, Any]) -> bool:
        """Return True if reset_cycle_hours have passed since last_reset."""
        last_reset: datetime = session["last_reset"]
        if last_reset.tzinfo is None:
            last_reset = last_reset.replace(tzinfo=timezone.utc)
        elapsed_hours = (datetime.now(timezone.utc) - last_reset).total_seconds() / 3600
        return elapsed_hours >= session["reset_cycle_hours"]

    def _reset_session_tokens(self, session: Dict[str, Any]) -> None:
        """Zero out tokens_used and update last_reset in the DB."""
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE backend_sessions
                    SET tokens_used = 0, last_reset = NOW(), updated_at = NOW()
                    WHERE id = %s
                    """,
                    (session["id"],),
                )
            conn.commit()
        logger.info(
            "Reset cycle completed for backend '%s' — tokens reset.", session["backend"]
        )
