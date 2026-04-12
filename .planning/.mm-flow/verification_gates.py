"""
VerificationGates: Brain #7 quality validation and cross-phase contract checking.

Simulates Brain #7 (Evaluador Crítico) with heuristic checks and logs every
validation result for audit.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, Optional

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

# Minimum confidence to pass Brain #7 gate
DEFAULT_CONFIDENCE_THRESHOLD = 0.7

# Heuristics: penalise these patterns
_VAGUE_PATTERNS = [
    r"\bTODO\b",
    r"\bFIXME\b",
    r"\bplaceholder\b",
    r"\bTBD\b",
    r"\bN/A\b",
]
_compiled_vague = [re.compile(p, re.IGNORECASE) for p in _VAGUE_PATTERNS]


class VerificationGates:
    """Validates AI outputs and cross-phase contracts using Brain #7 logic."""

    def __init__(self, db_url: str) -> None:
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def validate_output(
        self,
        output_text: str,
        phase: int,
        org_id: str,
        project_id: str,
        confidence_threshold: float = DEFAULT_CONFIDENCE_THRESHOLD,
        backend_used: Optional[str] = None,
    ) -> bool:
        """
        Run heuristic Brain #7 validation on an output.

        Scoring:
        - Starts at 1.0.
        - Empty output → 0.0.
        - Each vague pattern found → -0.15.
        - Output shorter than 50 chars → -0.3.

        Logs result to brain_consultations (brain_id=7).

        Args:
            output_text: Text to validate.
            phase: Phase number (for logging).
            org_id: Organization UUID.
            project_id: Project UUID.
            confidence_threshold: Minimum score to pass (default 0.7).
            backend_used: Backend that produced the output.

        Returns:
            True if confidence >= threshold.
        """
        confidence = self._score_output(output_text)
        passed = confidence >= confidence_threshold

        self._log_validation(
            org_id=org_id,
            project_id=project_id,
            phase=phase,
            input_text=f"[validate_output phase={phase}]",
            output_text=output_text,
            confidence=confidence,
            validated=passed,
            backend_used=backend_used,
            metadata={"threshold": confidence_threshold, "passed": passed},
        )

        if passed:
            logger.info(
                "Brain #7: phase %d APPROVED (confidence=%.2f)", phase, confidence
            )
        else:
            logger.warning(
                "Brain #7: phase %d REJECTED (confidence=%.2f < threshold=%.2f)",
                phase,
                confidence,
                confidence_threshold,
            )
        return passed

    def check_cross_phase_contract(
        self,
        from_phase: int,
        to_phase: int,
        from_output: str,
        to_input: str,
        org_id: str,
        project_id: str,
    ) -> bool:
        """
        Check that from_output satisfies the contract for the from→to transition.

        Also validates to_input is non-empty (ready to receive).

        Args:
            from_phase: Completed phase.
            to_phase: Incoming phase.
            from_output: Output of the completed phase.
            to_input: Input prepared for the new phase.
            org_id: Organization UUID.
            project_id: Project UUID.

        Returns:
            True if contract is satisfied.
        """
        contract = self._fetch_contract(from_phase, to_phase)

        if contract is None:
            logger.debug(
                "No contract found for %d→%d — allowing transition.",
                from_phase,
                to_phase,
            )
            return True

        # Heuristic: both sides must be non-empty meaningful text
        from_ok = bool(from_output and len(from_output.strip()) >= 10)
        to_ok = bool(to_input and len(to_input.strip()) >= 5)
        satisfied = from_ok and to_ok

        self._log_validation(
            org_id=org_id,
            project_id=project_id,
            phase=from_phase,
            input_text=f"contract_check {from_phase}→{to_phase}: {from_output[:200]}",
            output_text=f"to_input: {to_input[:200]}",
            confidence=1.0 if satisfied else 0.0,
            validated=satisfied,
            backend_used=None,
            metadata={
                "contract": contract["contract_text"],
                "from_phase": from_phase,
                "to_phase": to_phase,
                "satisfied": satisfied,
            },
        )

        if satisfied:
            logger.info("Contract %d→%d SATISFIED.", from_phase, to_phase)
        else:
            logger.warning(
                "Contract %d→%d NOT SATISFIED. from_ok=%s to_ok=%s",
                from_phase,
                to_phase,
                from_ok,
                to_ok,
            )
        return satisfied

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _score_output(self, text: str) -> float:
        if not text or not text.strip():
            return 0.0

        score = 1.0

        if len(text.strip()) < 50:
            score -= 0.3

        for pattern in _compiled_vague:
            if pattern.search(text):
                score -= 0.15

        return max(0.0, round(score, 2))

    def _fetch_contract(
        self, from_phase: int, to_phase: int
    ) -> Optional[Dict[str, Any]]:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT contract_text, is_required
                    FROM cross_phase_contracts
                    WHERE from_phase = %s AND to_phase = %s
                    """,
                    (from_phase, to_phase),
                )
                row = cur.fetchone()
        return dict(row) if row else None

    def _log_validation(
        self,
        org_id: str,
        project_id: str,
        phase: int,
        input_text: str,
        output_text: str,
        confidence: float,
        validated: bool,
        backend_used: Optional[str],
        metadata: Dict[str, Any],
    ) -> None:
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO brain_consultations
                            (org_id, project_id, phase, brain_id,
                             consultation_input, consultation_output,
                             confidence, validated, backend_used, metadata)
                        VALUES (%s, %s, %s, 7, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            org_id,
                            project_id,
                            phase,
                            input_text[:2000],
                            output_text[:2000],
                            confidence,
                            validated,
                            backend_used,
                            psycopg2.extras.Json(metadata),
                        ),
                    )
                conn.commit()
        except Exception as exc:
            logger.error("Failed to log Brain #7 validation: %s", exc)

    def _connect(self):
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
