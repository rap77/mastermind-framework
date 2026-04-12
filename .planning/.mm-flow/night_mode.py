"""
NightModeExecutor: autonomous 8-hour phase execution.

Runs a phase autonomously, cycling through subtasks, checkpointing context,
switching backends when tokens are low, and pausing safely when errors accumulate.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, cast

import psycopg2
import psycopg2.extras

from backend_scheduler import BackendScheduler  # type: ignore[import]
from config import BACKENDS, POSTGRES_LOCAL  # type: ignore[import]
from multi_backend_manager import MultiBackendManager  # type: ignore[import]
from token_limiter import TokenLimiter  # type: ignore[import]
from verification_gates import VerificationGates  # type: ignore[import]

logger = logging.getLogger(__name__)

# Subtask loop sleep between iterations (seconds)
LOOP_INTERVAL_SECONDS = 300  # 5 minutes
# Consecutive errors before pausing
MAX_CONSECUTIVE_ERRORS = 3
# Checkpoint every N seconds regardless of token count
PERIODIC_CHECKPOINT_SECONDS = 1800  # 30 minutes


# ---------------------------------------------------------------------------
# Subtask registry (phase → ordered list of subtask names)
# ---------------------------------------------------------------------------

_PHASE_SUBTASKS: Dict[int, List[str]] = {
    1: ["define_problem_statement", "draft_user_stories", "validate_assumptions"],
    2: ["create_technical_design", "break_down_tasks", "estimate_complexity"],
    3: ["implement_core", "write_tests", "code_review"],
    4: ["run_acceptance_tests", "verify_contracts", "sign_off"],
    19: ["design_phase_19", "implement_phase_19", "verify_phase_19"],
}


class NightModeExecutor:
    """Autonomous executor that runs a phase overnight without human intervention."""

    def __init__(
        self,
        org_id: str,
        project_id: str,
        phase: int,
        max_hours: float = 8.0,
        db_url: Optional[str] = None,
    ) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.phase = phase
        self.max_hours = max_hours
        self.db_url = db_url or POSTGRES_LOCAL.connection_string

        self._backend_mgr = MultiBackendManager(org_id, project_id, self.db_url)
        self._scheduler = BackendScheduler(org_id, project_id, self.db_url)
        self._token_limiter = TokenLimiter(org_id, project_id, self.db_url)
        self._verifier = VerificationGates(self.db_url)

        self._log_path = (
            Path.home()
            / ".mm-flow"
            / f"night-run-{datetime.now(timezone.utc).strftime('%Y-%m-%d')}.log"
        )
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def run(self) -> Dict[str, Any]:
        """
        Execute the phase autonomously for up to max_hours.

        Returns:
            Dict with: phase, status, progress_pct, completed_subtasks,
                       skipped_subtasks, paused_reason, started_at, ended_at.
        """
        started_at = datetime.now(timezone.utc)
        deadline = started_at.timestamp() + self.max_hours * 3600

        self.log(f"Night mode started — phase={self.phase} max_hours={self.max_hours}")

        # Restore from last checkpoint
        state = self._load_last_checkpoint()
        subtasks = _PHASE_SUBTASKS.get(self.phase, ["execute_phase"])

        completed: List[str] = state.get("completed_subtasks", [])
        pending = [t for t in subtasks if t not in completed]

        consecutive_errors = 0
        last_checkpoint_time = time.monotonic()
        paused_reason: Optional[str] = None

        while pending and time.monotonic() < deadline - 1:
            # Safety check: tokens
            if not self._token_limiter.is_safe_for_night_mode():
                self.log("PAUSE: all backends below MIN_TOKENS_SAFETY threshold.")
                self.checkpoint(state, "low_tokens")
                paused_reason = "low_tokens"
                break

            # Consecutive error guard
            if consecutive_errors >= MAX_CONSECUTIVE_ERRORS:
                self.log(f"PAUSE: {MAX_CONSECUTIVE_ERRORS} consecutive errors.")
                self.checkpoint(state, "max_errors")
                paused_reason = "max_errors"
                break

            # Periodic checkpoint
            now_mono = time.monotonic()
            if now_mono - last_checkpoint_time >= PERIODIC_CHECKPOINT_SECONDS:
                self.checkpoint(state, "periodic")
                last_checkpoint_time = now_mono

            # Get best backend
            backend_info = self._backend_mgr.get_best_available_backend()
            current_backend = backend_info["backend"]

            subtask = pending[0]
            self.log(f"Executing subtask '{subtask}' using backend '{current_backend}'")

            try:
                output = self._execute_subtask(subtask, state, current_backend)
            except Exception as exc:
                self.log(f"ERROR in subtask '{subtask}': {exc}")
                consecutive_errors += 1
                pending.pop(0)  # skip and try next
                continue

            # Brain #7 validation
            approved = self._verifier.validate_output(
                output_text=output,
                phase=self.phase,
                org_id=self.org_id,
                project_id=self.project_id,
                backend_used=current_backend,
            )

            if approved:
                self.log(f"Brain #7 APPROVED '{subtask}'")
                completed.append(subtask)
                state["completed_subtasks"] = completed
                state["last_output"] = output
                consecutive_errors = 0
                pending.pop(0)
            else:
                self.log(f"Brain #7 REJECTED '{subtask}' — skipping.")
                consecutive_errors += 1
                pending.pop(0)

            # Log countdown for all depleted backends before sleeping
            self._log_backend_countdowns()  # type: ignore[attr-defined]

            # Sleep between iterations
            remaining = deadline - time.monotonic()
            if remaining > LOOP_INTERVAL_SECONDS:
                time.sleep(LOOP_INTERVAL_SECONDS)

        ended_at = datetime.now(timezone.utc)
        total = len(subtasks)
        progress_pct = round(len(completed) / total * 100) if total else 100

        final_status = (
            "completed" if not pending else ("paused" if paused_reason else "partial")
        )
        self.log(
            f"Night mode ended — status={final_status} progress={progress_pct}% "
            f"completed={len(completed)}/{total}"
        )

        result = {
            "phase": self.phase,
            "status": final_status,
            "progress_pct": progress_pct,
            "completed_subtasks": completed,
            "skipped_subtasks": [t for t in subtasks if t not in completed],
            "paused_reason": paused_reason,
            "started_at": started_at.isoformat(),
            "ended_at": ended_at.isoformat(),
        }

        self.checkpoint(state | result, "night_mode_end")
        return result

    def checkpoint(self, state: Dict[str, Any], reason: str) -> None:
        """
        Persist current state to context_checkpoints.

        Args:
            state: Current state dict.
            reason: One of periodic | low_tokens | max_errors | backend_switch | night_mode_end.
        """
        backend_info = self._backend_mgr.get_best_available_backend()

        try:
            with self._connect() as conn:
                workspace_id = self._fetch_workspace_id(conn)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        INSERT INTO context_checkpoints
                            (org_id, project_id, workspace_id, phase, reason,
                             state_data, conversation_history, from_backend,
                             tokens_at_checkpoint)
                        VALUES (%s, %s, %s, %s, %s, %s, '[]', %s, %s)
                        """,
                        (
                            self.org_id,
                            self.project_id,
                            workspace_id,
                            self.phase,
                            reason,
                            psycopg2.extras.Json(state),
                            backend_info["backend"],
                            state.get("tokens_consumed", 0),
                        ),
                    )
                conn.commit()
            self.log(f"Checkpoint saved: reason={reason}")
        except Exception as exc:
            self.log(f"ERROR saving checkpoint: {exc}")

    def log(self, message: str) -> None:
        """Write a timestamped line to the nightly log file and stderr."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        line = f"[{ts}] [phase={self.phase}] {message}"
        logger.info(message)
        try:
            with self._log_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
        except OSError as exc:
            logger.warning("Could not write to log file %s: %s", self._log_path, exc)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _log_backend_countdowns(self) -> None:
        """Log reset countdowns for all configured backends."""
        for backend_name in BACKENDS:
            try:
                countdown = self._scheduler.time_until_next_reset(backend_name)
                if countdown["is_depleted"] and countdown["total_seconds"] > 0:
                    self.log(
                        f"⏳ {backend_name}: depleted — resets in {countdown['status']}"
                    )
                else:
                    self.log(
                        f"✅ {backend_name}: available (reset at {countdown['next_reset_iso']})"
                    )
            except Exception as exc:
                self.log(f"Could not get countdown for '{backend_name}': {exc}")

    def _execute_subtask(
        self, subtask_name: str, state: Dict[str, Any], backend: str
    ) -> str:
        """
        Placeholder executor — returns a synthetic output for the subtask.

        In production: delegates to the actual brain agent pipeline.
        """
        return (
            f"[{backend}] Subtask '{subtask_name}' executed for phase {self.phase}. "
            f"State keys available: {list(state.keys())}. "
            f"Output ready for Brain #7 validation."
        )

    def _load_last_checkpoint(self) -> Dict[str, Any]:
        """Restore state from the most recent checkpoint for this phase."""
        try:
            with self._connect() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT state_data
                        FROM context_checkpoints
                        WHERE project_id = %s AND phase = %s
                        ORDER BY created_at DESC
                        LIMIT 1
                        """,
                        (self.project_id, self.phase),
                    )
                    _raw = cur.fetchone()
                    row: Optional[Dict[str, Any]] = (
                        cast(Dict[str, Any], _raw) if _raw else None
                    )
            if row:
                self.log("Restored from last checkpoint.")
                return dict(row["state_data"]) if row["state_data"] else {}
        except Exception as exc:
            self.log(f"Could not load checkpoint: {exc}")
        return {}

    def _fetch_workspace_id(self, conn) -> str:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id FROM workspaces WHERE project_id = %s LIMIT 1",
                (self.project_id,),
            )
            row = cur.fetchone()
        return str(row["id"]) if row else "00000000-0000-0000-0000-000000000000"

    def _connect(self):
        return psycopg2.connect(
            self.db_url,
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
