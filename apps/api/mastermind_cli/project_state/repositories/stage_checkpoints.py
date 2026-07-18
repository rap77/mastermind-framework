"""Atomic repository for stage results, checkpoints, and projection outbox."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
from typing import TYPE_CHECKING, Any, cast

from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from mastermind_cli.orchestrator.runtime_contracts.models import (
    RunCheckpoint,
    StageResult,
)
from mastermind_cli.project_state.models.stage_checkpoint import (
    StageCheckpointRecord,
    StageTransitionOutbox,
    StageTransitionRecord,
)

if TYPE_CHECKING:
    from mastermind_cli.orchestrator.runtime_contracts.models import StageResultStatus


class CheckpointVersionConflict(RuntimeError):
    """Raised when a transition targets a stale checkpoint version."""


class BundleHashMismatch(RuntimeError):
    """Raised when resume targets a different immutable RunBundle."""


class CheckpointNotFound(LookupError):
    """Raised when a run has no authoritative checkpoint to resume."""


@dataclass(frozen=True, slots=True)
class CommittedStageTransition:
    """Persisted transition aggregate returned for commits and safe replays."""

    transition_id: str
    stage_result: StageResult
    checkpoint: RunCheckpoint
    outbox_events: tuple[StageTransitionOutbox, ...]
    replayed: bool


class StageCheckpointRepository:
    """Own the authoritative atomic transition boundary in project state."""

    def __init__(self, session: Session) -> None:
        """Initialize the repository with one shared SQLAlchemy session."""
        self.session = session

    def commit_transition(
        self,
        *,
        stage_result: StageResult,
        checkpoint: RunCheckpoint,
        expected_version: int,
        transition_sequence: int,
    ) -> CommittedStageTransition:
        """Atomically append a result, advance its checkpoint, and enqueue projections."""
        transition_id = self._transition_id(
            checkpoint=checkpoint,
            stage_result=stage_result,
            transition_sequence=transition_sequence,
        )
        try:
            committed: CommittedStageTransition | None = None
            with self.session.begin():
                committed = self.stage_transition(
                    stage_result=stage_result,
                    checkpoint=checkpoint,
                    expected_version=expected_version,
                    transition_sequence=transition_sequence,
                )
        except IntegrityError as error:
            self.session.rollback()
            replay = self._load_committed(transition_id, replayed=True)
            if replay is not None:
                self.session.commit()
                return replay
            current = self.get_checkpoint(checkpoint.run_id)
            if current is not None and current.version != expected_version:
                actual_version = current.version
                self.session.rollback()
                raise self._version_conflict(
                    expected_version, actual_version
                ) from error
            self.session.rollback()
            raise

        if committed is None:
            raise RuntimeError("committed stage transition could not be read back")
        return committed

    def stage_transition(
        self,
        *,
        stage_result: StageResult,
        checkpoint: RunCheckpoint,
        expected_version: int,
        transition_sequence: int,
    ) -> CommittedStageTransition:
        """Stage a transition in an existing caller-owned transaction."""
        if expected_version < 0:
            raise ValueError("expected_version must not be negative")
        if checkpoint.version != expected_version + 1:
            raise ValueError("checkpoint version must equal expected_version + 1")
        if stage_result.stage_id == "":
            raise ValueError("stage_result.stage_id must not be empty")

        transition_id = self._transition_id(
            checkpoint=checkpoint,
            stage_result=stage_result,
            transition_sequence=transition_sequence,
        )
        replay = self._load_committed(transition_id, replayed=True)
        if replay is not None:
            return replay
        self._append_result(
            transition_id=transition_id,
            checkpoint=checkpoint,
            stage_result=stage_result,
            transition_sequence=transition_sequence,
        )
        self._advance_checkpoint(checkpoint, expected_version)
        self._append_outbox(transition_id, checkpoint, stage_result)
        self.session.flush()
        committed = self._load_committed(transition_id, replayed=False)
        if committed is None:
            raise RuntimeError("staged transition could not be read back")
        return committed

    def get_checkpoint(self, run_id: str) -> RunCheckpoint | None:
        """Return the current authoritative checkpoint for a run."""
        record = self.session.get(StageCheckpointRecord, run_id)
        if record is None:
            return None
        return self._checkpoint_from_payload(record.checkpoint_payload)

    def get_committed_transition(
        self,
        *,
        stage_result: StageResult,
        checkpoint: RunCheckpoint,
        transition_sequence: int,
    ) -> CommittedStageTransition | None:
        """Return a committed transition for the canonical idempotency key."""
        transition_id = self._transition_id(
            checkpoint=checkpoint,
            stage_result=stage_result,
            transition_sequence=transition_sequence,
        )
        return self._load_committed(transition_id, replayed=True)

    def resume(self, *, run_id: str, bundle_content_hash: str) -> RunCheckpoint:
        """Load resumable state only when its immutable bundle hash still matches."""
        checkpoint = self.get_checkpoint(run_id)
        if checkpoint is None:
            raise CheckpointNotFound(f"no checkpoint exists for run {run_id}")
        if checkpoint.bundle_content_hash != bundle_content_hash:
            raise BundleHashMismatch(
                f"run {run_id} checkpoint uses {checkpoint.bundle_content_hash}; "
                f"requested bundle is {bundle_content_hash}"
            )
        return checkpoint

    def _append_result(
        self,
        *,
        transition_id: str,
        checkpoint: RunCheckpoint,
        stage_result: StageResult,
        transition_sequence: int,
    ) -> None:
        """Stage an immutable transition result in the current transaction."""
        self.session.add(
            StageTransitionRecord(
                transition_id=transition_id,
                run_id=checkpoint.run_id,
                bundle_hash=checkpoint.bundle_content_hash,
                stage_id=stage_result.stage_id,
                attempt=stage_result.attempt,
                transition_sequence=transition_sequence,
                result_payload=asdict(stage_result),
                checkpoint_payload=asdict(checkpoint),
                evidence_refs=list(stage_result.evidence_refs),
                artifact_refs=list(stage_result.artifact_refs),
            )
        )

    def _advance_checkpoint(
        self, checkpoint: RunCheckpoint, expected_version: int
    ) -> None:
        """Create or compare-and-swap the checkpoint inside the transaction."""
        payload = asdict(checkpoint)
        if expected_version == 0:
            self.session.add(
                StageCheckpointRecord(
                    run_id=checkpoint.run_id,
                    checkpoint_id=checkpoint.checkpoint_id,
                    bundle_id=checkpoint.bundle_id,
                    objective_id=checkpoint.objective_id,
                    bundle_hash=checkpoint.bundle_content_hash,
                    version=checkpoint.version,
                    checkpoint_payload=payload,
                )
            )
            return

        result = cast(
            CursorResult[Any],
            self.session.execute(
                update(StageCheckpointRecord)
                .where(
                    StageCheckpointRecord.run_id == checkpoint.run_id,
                    StageCheckpointRecord.version == expected_version,
                )
                .values(
                    checkpoint_id=checkpoint.checkpoint_id,
                    bundle_id=checkpoint.bundle_id,
                    objective_id=checkpoint.objective_id,
                    bundle_hash=checkpoint.bundle_content_hash,
                    version=checkpoint.version,
                    checkpoint_payload=payload,
                )
            ),
        )
        if result.rowcount != 1:
            current = self.session.get(StageCheckpointRecord, checkpoint.run_id)
            actual_version = current.version if current is not None else 0
            raise self._version_conflict(expected_version, actual_version)

    def _append_outbox(
        self,
        transition_id: str,
        checkpoint: RunCheckpoint,
        stage_result: StageResult,
    ) -> None:
        """Stage planning and memory projection events in the same transaction."""
        payload = {
            "transition_id": transition_id,
            "run_id": checkpoint.run_id,
            "bundle_hash": checkpoint.bundle_content_hash,
            "stage_result": asdict(stage_result),
            "checkpoint": asdict(checkpoint),
        }
        for destination in ("planning", "memory"):
            self.session.add(
                StageTransitionOutbox(
                    event_id=f"{transition_id}:{destination}",
                    transition_id=transition_id,
                    destination=destination,
                    payload=payload,
                )
            )

    def _load_committed(
        self, transition_id: str, *, replayed: bool
    ) -> CommittedStageTransition | None:
        """Load the persisted aggregate for one canonical idempotency key."""
        transition = self.session.get(StageTransitionRecord, transition_id)
        if transition is None:
            return None
        outbox_events = tuple(
            self.session.scalars(
                select(StageTransitionOutbox)
                .where(StageTransitionOutbox.transition_id == transition_id)
                .order_by(StageTransitionOutbox.destination)
            )
        )
        return CommittedStageTransition(
            transition_id=transition_id,
            stage_result=self._stage_result_from_payload(transition.result_payload),
            checkpoint=self._checkpoint_from_payload(transition.checkpoint_payload),
            outbox_events=outbox_events,
            replayed=replayed,
        )

    @staticmethod
    def _transition_id(
        *,
        checkpoint: RunCheckpoint,
        stage_result: StageResult,
        transition_sequence: int,
    ) -> str:
        """Derive a stable ID from the canonical transition idempotency key."""
        key = "\x1f".join(
            (
                checkpoint.run_id,
                checkpoint.bundle_content_hash,
                stage_result.stage_id,
                str(stage_result.attempt),
                str(transition_sequence),
            )
        )
        return f"stage-transition:{sha256(key.encode()).hexdigest()}"

    @staticmethod
    def _stage_result_from_payload(payload: dict[str, object]) -> StageResult:
        """Restore a typed stage result from its JSON representation."""
        attempt = payload["attempt"]
        if not isinstance(attempt, int):
            raise ValueError("stage result attempt must be an integer")
        return StageResult(
            stage_id=str(payload["stage_id"]),
            status=cast("StageResultStatus", payload["status"]),
            attempt=attempt,
            artifact_refs=tuple(payload["artifact_refs"]),  # type: ignore[arg-type]
            evidence_refs=tuple(payload["evidence_refs"]),  # type: ignore[arg-type]
            finding_refs=tuple(payload["finding_refs"]),  # type: ignore[arg-type]
            started_at=str(payload["started_at"]),
            completed_at=str(payload["completed_at"]),
            next_stage_ids=tuple(payload["next_stage_ids"]),  # type: ignore[arg-type]
        )

    @staticmethod
    def _checkpoint_from_payload(payload: dict[str, object]) -> RunCheckpoint:
        """Restore a typed run checkpoint from its JSON representation."""
        tuple_fields = (
            "completed_stage_ids",
            "skipped_stage_ids",
            "blocked_stage_ids",
            "artifact_refs",
            "evidence_refs",
            "pending_approval_ids",
            "next_eligible_stage_ids",
        )
        restored: dict[str, Any] = dict(payload)
        for field in tuple_fields:
            restored[field] = tuple(restored[field])
        return RunCheckpoint(**restored)

    @staticmethod
    def _version_conflict(
        expected_version: int, actual_version: int
    ) -> CheckpointVersionConflict:
        """Create the stable optimistic-concurrency error."""
        return CheckpointVersionConflict(
            f"expected checkpoint version {expected_version}, found {actual_version}"
        )
