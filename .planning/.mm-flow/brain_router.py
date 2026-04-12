"""
BrainRouter: phase-aware brain dispatch and consultation logging.

Maps phase types to brain IDs, logs every consultation, and aggregates
outputs for cross-brain synthesis.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, cast

import psycopg2
import psycopg2.extras

from config import PHASE_BRAIN_ROUTING

logger = logging.getLogger(__name__)


class BrainRouter:
    """Routes tasks to the correct brain set and logs all consultations."""

    def __init__(self, org_id: str, project_id: str, db_url: str) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_brains_for_phase(self, phase_type: str) -> List[int]:
        """
        Return brain IDs for a given phase type.

        Args:
            phase_type: One of DISCUSSION | PLANNING | EXECUTION | VERIFICATION.

        Returns:
            List of brain IDs (ints 1-7).

        Raises:
            ValueError: If phase_type is not in PHASE_BRAIN_ROUTING.
        """
        key = phase_type.upper()
        if key not in PHASE_BRAIN_ROUTING:
            raise ValueError(
                f"Unknown phase_type '{phase_type}'. "
                f"Valid types: {list(PHASE_BRAIN_ROUTING.keys())}"
            )
        return PHASE_BRAIN_ROUTING[key]

    def log_consultation(
        self,
        brain_id: int,
        input_text: str,
        output_text: str,
        confidence: float,
        phase: int = 0,
        backend_used: Optional[str] = None,
        tokens_used: int = 0,
        validated: bool = False,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Insert a brain_consultations row and return its UUID.

        Args:
            brain_id: Brain number (1-7).
            input_text: Text sent to the brain.
            output_text: Text received from the brain.
            confidence: Quality score 0.0-1.0.
            phase: Phase number (optional, for audit).
            backend_used: Backend that ran the consultation.
            tokens_used: Tokens consumed.
            validated: Whether Brain #7 approved this output.
            metadata: Extra key/value data.

        Returns:
            UUID of the inserted row as a string.
        """
        if not 1 <= brain_id <= 7:
            raise ValueError(f"brain_id must be 1-7, got {brain_id}")
        if not 0.0 <= confidence <= 1.0:
            raise ValueError(f"confidence must be 0.0-1.0, got {confidence}")

        meta = metadata or {}
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO brain_consultations
                        (org_id, project_id, phase, brain_id,
                         consultation_input, consultation_output,
                         confidence, validated, backend_used, tokens_used, metadata)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        self.org_id,
                        self.project_id,
                        phase,
                        brain_id,
                        input_text,
                        output_text,
                        confidence,
                        validated,
                        backend_used,
                        tokens_used,
                        psycopg2.extras.Json(meta),
                    ),
                )
                _raw = cur.fetchone()
                row: Optional[Dict[str, Any]] = (
                    cast(Dict[str, Any], _raw) if _raw else None
                )
            conn.commit()

        consultation_id = str(row["id"]) if row else ""
        logger.debug(
            "Logged consultation: brain=%d phase=%d confidence=%.2f id=%s",
            brain_id,
            phase,
            confidence,
            consultation_id,
        )
        return consultation_id

    def get_brain_outputs(
        self,
        phase: int,
        brain_ids: List[int],
        limit_per_brain: int = 5,
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Fetch recent brain outputs for a given phase, grouped by brain_id.

        Args:
            phase: Phase number to filter by.
            brain_ids: Brain IDs to include.
            limit_per_brain: Max rows per brain (most recent first).

        Returns:
            Dict mapping brain_id → list of consultation dicts.
        """
        if not brain_ids:
            return {}

        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT brain_id, consultation_input, consultation_output,
                           confidence, validated, backend_used, created_at
                    FROM brain_consultations
                    WHERE project_id = %s
                      AND phase = %s
                      AND brain_id = ANY(%s)
                    ORDER BY brain_id, created_at DESC
                    """,
                    (self.project_id, phase, brain_ids),
                )
                rows: List[Dict[str, Any]] = cast(List[Dict[str, Any]], cur.fetchall())

        result: Dict[int, List[Dict[str, Any]]] = {bid: [] for bid in brain_ids}
        counts: Dict[int, int] = {bid: 0 for bid in brain_ids}

        for row in rows:
            bid = row["brain_id"]
            if counts[bid] < limit_per_brain:
                result[bid].append(dict(row))
                counts[bid] += 1

        return result

    def get_latest_brain7_verdict(self, phase: int) -> Optional[Dict[str, Any]]:
        """
        Return the most recent Brain #7 verdict for a phase.

        Returns:
            Consultation dict or None.
        """
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT consultation_output, confidence, validated, created_at
                    FROM brain_consultations
                    WHERE project_id = %s AND phase = %s AND brain_id = 7
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (self.project_id, phase),
                )
                row = cur.fetchone()
        return dict(row) if row else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self):
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
