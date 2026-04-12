"""
StateMachine: phase lifecycle management with RLS-enforced PostgreSQL state.

Handles phase transitions, state persistence, and cross-phase contract validation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional, cast

import psycopg2
import psycopg2.extras

logger = logging.getLogger(__name__)

# Valid status transitions
VALID_TRANSITIONS = {
    "pending": {"in_progress"},
    "in_progress": {"completed", "failed", "paused"},
    "paused": {"in_progress"},
    "failed": {"pending"},  # allow retry
    "completed": set(),  # terminal
}


class StateMachine:
    """Manages phase state lifecycle for a project workspace."""

    def __init__(
        self,
        org_id: str,
        project_id: str,
        workspace_id: str,
        db_url: str,
    ) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.workspace_id = workspace_id
        self.db_url = db_url

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_phase_context(
        self,
        phase: int,
        status: str,
        state_data: Dict[str, Any],
        backend_used: Optional[str] = None,
        tokens_consumed: int = 0,
    ) -> None:
        """
        Upsert the current phase state into mm_flow_state.

        Sets the RLS session variable before writing.

        Args:
            phase: Phase number (1-N).
            status: One of pending | in_progress | completed | failed | paused.
            state_data: Arbitrary phase-specific state dict.
            backend_used: Backend that processed this phase step.
            tokens_consumed: Tokens used so far in this phase.
        """
        if status not in VALID_TRANSITIONS and status not in (
            "pending",
            "in_progress",
            "completed",
            "failed",
            "paused",
        ):
            raise ValueError(f"Invalid status: {status!r}")

        with self._connect() as conn:
            self._set_rls_context(conn)
            with conn.cursor() as cur:
                # Check if a row already exists for this phase
                cur.execute(
                    """
                    SELECT id, status FROM mm_flow_state
                    WHERE project_id = %s AND phase = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (self.project_id, phase),
                )
                _row = cur.fetchone()
                existing: Optional[Dict[str, Any]] = (
                    cast(Dict[str, Any], _row) if _row else None
                )

                if existing:
                    existing_dict = cast(Dict[str, Any], existing)
                    cur.execute(
                        """
                        UPDATE mm_flow_state
                        SET status = %s, state_data = %s,
                            backend_used = %s, tokens_consumed = %s,
                            updated_at = NOW()
                        WHERE id = %s
                        """,
                        (
                            status,
                            psycopg2.extras.Json(state_data),
                            backend_used,
                            tokens_consumed,
                            existing_dict["id"],
                        ),
                    )
                    logger.debug("Updated phase %d state → %s", phase, status)
                else:
                    cur.execute(
                        """
                        INSERT INTO mm_flow_state
                            (org_id, project_id, workspace_id, phase, status,
                             state_data, backend_used, tokens_consumed)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            self.org_id,
                            self.project_id,
                            self.workspace_id,
                            phase,
                            status,
                            psycopg2.extras.Json(state_data),
                            backend_used,
                            tokens_consumed,
                        ),
                    )
                    logger.debug("Created phase %d state → %s", phase, status)
            conn.commit()

    def get_current_phase(self) -> Dict[str, Any]:
        """
        Return the most recent phase state for this project.

        Returns:
            Dict with keys: phase, status, state_data.
            Defaults to phase=1, status='pending' if no state found.
        """
        with self._connect() as conn:
            self._set_rls_context(conn)
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT phase, status, state_data, tokens_consumed, backend_used
                    FROM mm_flow_state
                    WHERE project_id = %s
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (self.project_id,),
                )
                _raw = cur.fetchone()
                row: Optional[Dict[str, Any]] = (
                    cast(Dict[str, Any], _raw) if _raw else None
                )

        if row is None:
            return {"phase": 1, "status": "pending", "state_data": {}}
        return dict(row)

    def transition_phase(
        self,
        from_phase: int,
        to_phase: int,
        validation_result: str,
    ) -> bool:
        """
        Validate cross-phase contract and create the new phase state.

        Args:
            from_phase: Current completed phase.
            to_phase: Next phase to begin.
            validation_result: Output text to validate against the contract.

        Returns:
            True if transition succeeded, False if contract not satisfied.
        """
        with self._connect() as conn:
            contract = self._fetch_contract(conn, from_phase, to_phase)

        if contract:
            contract_dict = cast(Dict[str, Any], contract)
            if contract_dict["is_required"]:
                # Simple heuristic: validation_result must be non-empty
                if not validation_result or not validation_result.strip():
                    logger.warning(
                        "Contract %d→%d not satisfied: empty validation result.",
                        from_phase,
                        to_phase,
                    )
                    return False
                logger.info(
                    "Contract %d→%d satisfied. Contract: %s",
                    from_phase,
                    to_phase,
                    contract_dict["contract_text"][:80],
                )
            elif not contract_dict["is_required"]:
                logger.debug(
                    "Optional contract %d→%d — proceeding.", from_phase, to_phase
                )

        # Mark from_phase complete and create to_phase pending
        current_state = self.get_current_phase()
        self.set_phase_context(
            from_phase, "completed", current_state.get("state_data", {})
        )
        self.set_phase_context(to_phase, "pending", {})

        # Record phase execution in audit trail (requires async call)
        # This will be called by orchestrator after phase completion
        logger.info("Phase transition: %d → %d (pending)", from_phase, to_phase)
        return True

    def record_phase_execution(
        self,
        phase_number: int,
        status: str,
        backend_used: Optional[str] = None,
        tokens_consumed: int = 0,
        tokens_input: int = 0,
        tokens_output: int = 0,
        output_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        git_commit_hash: Optional[str] = None,
        triggered_by: str = "system",
    ) -> Optional[str]:
        """
        Record phase execution metadata to audit trail (phase_executions table).

        Called by orchestrator to persist execution history:
        - Before phase: status='in_progress'
        - After phase: status='completed' with summary/commit
        - On failure: status='failed' with error_message

        Args:
            phase_number: Phase number
            status: in_progress | completed | failed
            backend_used: Which backend was used
            tokens_consumed: Total tokens used in phase
            tokens_input: Input tokens
            tokens_output: Output tokens
            output_summary: Brief summary of phase output
            error_message: If status='failed', error details
            git_commit_hash: Commit hash at phase completion
            triggered_by: Who triggered (user, scheduler, brain_7, etc)

        Returns:
            phase_execution_id (UUID string) for linking decisions/gates
        """
        # Import here to avoid circular dependency

        with self._connect() as conn:
            self._set_rls_context(conn)
            with conn.cursor() as cur:
                # Insert into phase_executions table
                cur.execute(
                    """
                    INSERT INTO phase_executions
                        (org_id, project_id, workspace_id, phase_number,
                         status, backend_used, tokens_consumed,
                         tokens_input, tokens_output, output_summary,
                         error_message, git_commit_hash, triggered_by)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                    """,
                    (
                        self.org_id,
                        self.project_id,
                        self.workspace_id,
                        phase_number,
                        status,
                        backend_used,
                        tokens_consumed,
                        tokens_input,
                        tokens_output,
                        output_summary,
                        error_message,
                        git_commit_hash,
                        triggered_by,
                    ),
                )
                result = cur.fetchone()
                phase_exec_id = result[0] if result else None

                if phase_exec_id:
                    # Record in audit log
                    action_type = {
                        "in_progress": "phase_started",
                        "completed": "phase_completed",
                        "failed": "phase_failed",
                    }.get(status, "phase_update")

                    cur.execute(
                        """
                        INSERT INTO audit_log
                            (org_id, project_id, action_type, actor, actor_type,
                             description, phase_number, related_entity_type,
                             related_entity_id, severity)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """,
                        (
                            self.org_id,
                            self.project_id,
                            action_type,
                            triggered_by,
                            "system",
                            f"Phase {phase_number} {status}",
                            phase_number,
                            "phase_execution",
                            phase_exec_id,
                            "error" if status == "failed" else "info",
                        ),
                    )

                    logger.info(
                        f"Recorded phase {phase_number} execution: "
                        f"status={status}, tokens={tokens_consumed}, "
                        f"execution_id={phase_exec_id}"
                    )

            conn.commit()
            return str(phase_exec_id) if phase_exec_id else None

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _connect(self) -> psycopg2.extensions.connection:
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )

    def _set_rls_context(self, conn: psycopg2.extensions.connection) -> None:
        """Set session-level RLS variable so policies work correctly."""
        with conn.cursor() as cur:
            cur.execute(
                "SET LOCAL mm_flow.org_id = %s",
                (str(self.org_id),),
            )

    def _fetch_contract(
        self, conn: psycopg2.extensions.connection, from_phase: int, to_phase: int
    ) -> Optional[Dict[str, Any]]:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT from_phase, to_phase, contract_text, is_required
                FROM cross_phase_contracts
                WHERE from_phase = %s AND to_phase = %s
                """,
                (from_phase, to_phase),
            )
            row = cur.fetchone()
            return cast(Dict[str, Any], row) if row else None
