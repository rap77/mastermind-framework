"""
BackendScheduler: token tracking, reset detection, and usage accounting.

Maintains per-backend token budgets and detects when reset cycles have elapsed.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, cast

import psycopg2
import psycopg2.extras

from config import BACKENDS

logger = logging.getLogger(__name__)


class BackendScheduler:
    """Tracks token usage per backend and manages reset cycle detection."""

    def __init__(self, org_id: str, project_id: str, db_url: str) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def track_token_usage(self, backend: str, tokens_used: int) -> None:
        """
        Increment tokens_used for the active session of the given backend.

        Args:
            backend: Backend key ('claude', 'openrouter', 'z_ai').
            tokens_used: Number of tokens consumed in this call.
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE backend_sessions
                    SET tokens_used = tokens_used + %s, updated_at = NOW()
                    WHERE project_id = %s AND backend = %s AND is_active = TRUE
                    """,
                    (tokens_used, self.project_id, backend),
                )
                if cur.rowcount == 0:
                    logger.warning(
                        "No active session found for backend '%s' — creating one.",
                        backend,
                    )
                    self._create_session(conn, backend)
                    cur.execute(
                        """
                        UPDATE backend_sessions
                        SET tokens_used = tokens_used + %s, updated_at = NOW()
                        WHERE project_id = %s AND backend = %s AND is_active = TRUE
                        """,
                        (tokens_used, self.project_id, backend),
                    )
            conn.commit()
        logger.debug("Tracked %d tokens for backend '%s'", tokens_used, backend)

    def get_available_tokens(self, backend: str) -> int:
        """
        Return available tokens for a backend, applying reset if cycle elapsed.

        Args:
            backend: Backend key.

        Returns:
            Number of tokens available.
        """
        with self._connect() as conn:
            session = self._fetch_session(conn, backend)

        if session is None:
            cfg = BACKENDS.get(backend)
            return cfg.token_limit if cfg else 0

        if self._reset_cycle_completed(session):
            self._apply_reset(session)
            return session["tokens_limit"]

        return max(0, session["tokens_limit"] - session["tokens_used"])

    def detect_reset_cycles(self) -> Dict[str, float]:
        """
        Return reset_cycle_hours for each configured backend.

        Returns:
            Dict mapping backend key → reset_cycle_hours.
        """
        return {name: cfg.reset_cycle_hours for name, cfg in BACKENDS.items()}

    def time_until_next_reset(self, backend: str) -> Dict[str, Any]:
        """
        Return countdown info for the next token reset of a backend.

        Prefers next_reset_time from DB (set at depletion), falls back to
        calculating from last_reset + reset_cycle_hours.

        Returns:
            Dict with keys:
              - hours (int): full hours remaining
              - minutes (int): remaining minutes after hours
              - seconds (int): remaining seconds after minutes
              - next_reset_iso (str): ISO-8601 timestamp of next reset
              - is_depleted (bool): True when tokens were exhausted
              - status (str): human-readable like "4h 48m 30s" or "AVAILABLE NOW"
              - total_seconds (int): total seconds remaining (useful for sorting)
        """
        with self._connect() as conn:
            session = self._fetch_session(conn, backend)

        now = datetime.now(timezone.utc)

        if session is None:
            # No DB record — backend is fully fresh
            cfg = BACKENDS.get(backend)
            if cfg:
                next_reset = now + timedelta(hours=cfg.reset_cycle_hours)
            else:
                next_reset = now
            return self._build_countdown(next_reset, is_depleted=False)

        # Prefer explicitly tracked next_reset_time (set when depletion occurs)
        next_reset: Optional[datetime] = session.get("next_reset_time")

        if next_reset is None:
            # Fall back: calculate from last_reset
            last_reset: datetime = session["last_reset"]
            if last_reset.tzinfo is None:
                last_reset = last_reset.replace(tzinfo=timezone.utc)
            next_reset = last_reset + timedelta(hours=session["reset_cycle_hours"])

        is_depleted: bool = session.get("depletion_timestamp") is not None
        return self._build_countdown(next_reset, is_depleted=is_depleted)

    def _build_countdown(
        self, next_reset: datetime, is_depleted: bool
    ) -> Dict[str, Any]:
        """Compute countdown fields from a target reset datetime."""
        now = datetime.now(timezone.utc)
        if next_reset.tzinfo is None:
            next_reset = next_reset.replace(tzinfo=timezone.utc)

        if next_reset <= now:
            return {
                "hours": 0,
                "minutes": 0,
                "seconds": 0,
                "total_seconds": 0,
                "next_reset_iso": next_reset.isoformat(),
                "is_depleted": is_depleted,
                "status": "AVAILABLE NOW",
            }

        delta = next_reset - now
        total_seconds = int(delta.total_seconds())
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60

        return {
            "hours": hours,
            "minutes": minutes,
            "seconds": seconds,
            "total_seconds": total_seconds,
            "next_reset_iso": next_reset.isoformat(),
            "is_depleted": is_depleted,
            "status": f"{hours}h {minutes}m {seconds}s",
        }

    def get_all_usage_summary(self) -> list[Dict]:
        """
        Return token usage summary for all backends of this project.

        Returns:
            List of dicts: backend, tokens_used, tokens_limit, pct_available,
            hours_to_reset, is_active.
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT backend, tokens_used, tokens_limit,
                           reset_cycle_hours, last_reset, is_active,
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
                rows: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cur.fetchall())

        summary = []
        for row_tuple in rows:
            row = cast(Dict[str, Any], row_tuple)
            available = max(0, row["tokens_limit"] - row["tokens_used"])
            if self._reset_cycle_completed(row):
                available = row["tokens_limit"]
            pct = (
                round(available / row["tokens_limit"] * 100, 1)
                if row["tokens_limit"]
                else 0
            )
            countdown = self.time_until_next_reset(row["backend"])
            summary.append(
                {
                    "backend": row["backend"],
                    "tokens_used": row["tokens_used"],
                    "tokens_limit": row["tokens_limit"],
                    "tokens_available": available,
                    "pct_available": pct,
                    "pct_used": round(row["tokens_used"] / row["tokens_limit"] * 100, 1)
                    if row["tokens_limit"]
                    else 0,
                    "countdown": countdown,
                    # Legacy scalar kept for compatibility with callers that used hours_to_reset
                    "hours_to_reset": countdown["hours"]
                    + countdown["minutes"] / 60
                    + countdown["seconds"] / 3600,
                    "is_active": row["is_active"],
                }
            )
        return summary

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def _fetch_session(
        self, conn: psycopg2.extensions.connection, backend: str
    ) -> Optional[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, backend, tokens_used, tokens_limit,
                       reset_cycle_hours, last_reset, is_active,
                       next_reset_time, depletion_timestamp
                FROM backend_sessions
                WHERE project_id = %s AND backend = %s
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (self.project_id, backend),
            )
            row = cur.fetchone()
            return cast(Dict[str, Any], row) if row else None

    def _reset_cycle_completed(self, session: Dict) -> bool:
        last_reset: datetime = session["last_reset"]
        if last_reset.tzinfo is None:
            last_reset = last_reset.replace(tzinfo=timezone.utc)
        elapsed = (datetime.now(timezone.utc) - last_reset).total_seconds() / 3600
        return elapsed >= session["reset_cycle_hours"]

    def _apply_reset(self, session: Dict) -> None:
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
        logger.info("Token reset applied for backend '%s'", session["backend"])

    def _create_session(self, conn, backend: str) -> None:
        cfg = BACKENDS.get(backend)
        if not cfg:
            logger.error("Unknown backend '%s' — cannot create session.", backend)
            return
        with conn.cursor() as cur:
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
                    backend,
                    cfg.token_limit,
                    cfg.reset_cycle_hours,
                ),
            )
        conn.commit()
