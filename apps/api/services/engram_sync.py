"""
Engram ↔ PostgreSQL Synchronization Service

Syncs decisions and brain feedback from Engram persistent memory
into PostgreSQL audit trail for integrated governance.

Architecture:
1. Query Engram for decisions (type=decision, type=bugfix, etc)
2. Parse metadata: title, rationale, alternatives, confidence
3. Link to phase_executions by timestamp and phase_number
4. Upsert into decisions table with engram_link reference
5. Mark as synced in Engram

Also handles:
- Brain feedback synchronization
- Cross-session wisdom capture
- Niche-specific decision metadata
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from uuid import UUID
import logging

# In real implementation, these would be actual DB and API clients
# from sqlalchemy import Session
# from sqlalchemy.dialects.postgresql import insert
# from engram_sdk import EngramClient

logger = logging.getLogger(__name__)


# ============================================================================
# DOMAIN MODELS
# ============================================================================


class DecisionType(str, Enum):
    """Decision classification per MM-Flow governance"""

    ARCHITECTURAL = "architectural"
    TECHNICAL = "technical"
    PRODUCT = "product"
    PROCESS = "process"
    TOOL_SELECTION = "tool_selection"


class DecisionStatus(str, Enum):
    """Decision lifecycle states"""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUPERSEDED = "superseded"
    ARCHIVED = "archived"


class FeedbackType(str, Enum):
    """Brain feedback classification"""

    INSIGHT = "insight"
    RISK_FLAG = "risk_flag"
    OPPORTUNITY = "opportunity"
    LESSON_LEARNED = "lesson_learned"
    RECOMMENDATION = "recommendation"


@dataclass
class EngramDecision:
    """Parsed decision from Engram memory"""

    engram_id: int  # Engram observation ID
    title: str
    decision_type: str
    rationale: str
    alternatives: Optional[str] = None
    chosen_option: Optional[str] = None
    confidence: float = 0.5
    impact_level: str = "medium"
    impact_description: Optional[str] = None
    made_by: str = "system"
    tags: List[str] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class EngramBrainFeedback:
    """Parsed brain feedback from Engram"""

    engram_id: int
    brain_id: int  # 1-7, 8-23, etc
    title: str
    feedback_type: str
    content: str
    confidence: Optional[float] = None
    impact_on_phase: Optional[str] = None
    created_at: datetime = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.created_at is None:
            self.created_at = datetime.utcnow()


# ============================================================================
# ENGRAM SYNC SERVICE
# ============================================================================


class EngramSyncService:
    """
    Synchronizes decisions and brain feedback from Engram to PostgreSQL.

    Usage:
        sync_service = EngramSyncService(db_session, engram_client)
        results = await sync_service.sync_decisions_to_db(
            org_id=org_uuid,
            project_id=project_uuid,
            since_timestamp=datetime(...),
            phase_number=18
        )
    """

    def __init__(
        self,
        # db_session: Session,  # SQLAlchemy session
        # engram_client: EngramClient,  # Engram API client
        # org_id: UUID,
        # project_id: UUID,
    ):
        """Initialize sync service with DB and Engram clients"""
        # self.db = db_session
        # self.engram = engram_client
        # self.org_id = org_id
        # self.project_id = project_id
        self.logger = logging.getLogger(__name__)

    # ========================================================================
    # DECISION SYNCHRONIZATION
    # ========================================================================

    async def sync_decisions_to_db(
        self,
        org_id: UUID,
        project_id: UUID,
        since_timestamp: Optional[datetime] = None,
        phase_number: Optional[int] = None,
        decision_type_filter: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Sync decisions from Engram to PostgreSQL.

        Args:
            org_id: Organization ID for RLS isolation
            project_id: Project ID
            since_timestamp: Only sync decisions after this time
            phase_number: Filter by phase number (optional)
            decision_type_filter: Filter by decision type (optional)

        Returns:
            {
                "synced_count": 42,
                "failed_count": 2,
                "errors": [...],
                "new_decisions": [...],
                "updated_decisions": [...],
                "skipped_count": 5  # Already synced
            }
        """

        results = {
            "synced_count": 0,
            "failed_count": 0,
            "errors": [],
            "new_decisions": [],
            "updated_decisions": [],
            "skipped_count": 0,
        }

        try:
            # Step 1: Query Engram for decisions
            decisions = await self._query_engram_decisions(
                since_timestamp=since_timestamp,
                phase_number=phase_number,
                decision_type_filter=decision_type_filter,
            )

            self.logger.info(f"Found {len(decisions)} decisions in Engram for sync")

            # Step 2: Process each decision
            for engram_decision in decisions:
                try:
                    # Check if already synced
                    if await self._is_decision_synced(engram_decision.engram_id):
                        results["skipped_count"] += 1
                        continue

                    # Parse and link to phase execution
                    phase_exec_id = await self._find_phase_execution_id(
                        org_id=org_id,
                        project_id=project_id,
                        phase_number=phase_number,
                        timestamp=engram_decision.created_at,
                    )

                    # Upsert into decisions table
                    decision_id = await self._upsert_decision(
                        org_id=org_id,
                        project_id=project_id,
                        phase_execution_id=phase_exec_id,
                        engram_decision=engram_decision,
                    )

                    # Mark as synced in Engram
                    await self._mark_decision_synced(
                        engram_decision.engram_id, decision_id
                    )

                    if phase_exec_id:
                        results["new_decisions"].append(
                            {
                                "decision_id": str(decision_id),
                                "title": engram_decision.title,
                                "engram_id": engram_decision.engram_id,
                            }
                        )
                    results["synced_count"] += 1

                except Exception as e:
                    results["failed_count"] += 1
                    error_msg = (
                        f"Failed to sync decision {engram_decision.engram_id}: {str(e)}"
                    )
                    results["errors"].append(error_msg)
                    self.logger.error(error_msg)

        except Exception as e:
            results["errors"].append(f"Sync operation failed: {str(e)}")
            self.logger.error(f"Decision sync failed: {e}")

        return results

    async def sync_brain_feedback_to_db(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_number: Optional[int] = None,
        brain_id_filter: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Sync brain feedback from Engram to PostgreSQL.

        Args:
            org_id: Organization ID
            project_id: Project ID
            phase_number: Filter by phase (optional)
            brain_id_filter: Filter by brain ID (optional)

        Returns:
            {
                "synced_count": 15,
                "failed_count": 0,
                "errors": [],
                "feedback_synced": [...]
            }
        """

        results = {
            "synced_count": 0,
            "failed_count": 0,
            "errors": [],
            "feedback_synced": [],
        }

        try:
            # Query Engram for brain feedback
            feedback_items = await self._query_engram_brain_feedback(
                phase_number=phase_number,
                brain_id_filter=brain_id_filter,
            )

            self.logger.info(
                f"Found {len(feedback_items)} brain feedback items in Engram"
            )

            for feedback in feedback_items:
                try:
                    # Find phase execution
                    phase_exec_id = await self._find_phase_execution_id(
                        org_id=org_id,
                        project_id=project_id,
                        phase_number=phase_number,
                        timestamp=feedback.created_at,
                    )

                    # Upsert feedback
                    feedback_id = await self._upsert_brain_feedback(
                        org_id=org_id,
                        project_id=project_id,
                        phase_execution_id=phase_exec_id,
                        feedback=feedback,
                    )

                    results["synced_count"] += 1
                    results["feedback_synced"].append(
                        {
                            "feedback_id": str(feedback_id),
                            "brain_id": feedback.brain_id,
                            "title": feedback.title,
                        }
                    )

                except Exception as e:
                    results["failed_count"] += 1
                    results["errors"].append(
                        f"Failed to sync feedback {feedback.engram_id}: {str(e)}"
                    )
                    self.logger.error(f"Feedback sync error: {e}")

        except Exception as e:
            results["errors"].append(f"Feedback sync failed: {str(e)}")
            self.logger.error(f"Brain feedback sync failed: {e}")

        return results

    # ========================================================================
    # PRIVATE HELPER METHODS
    # ========================================================================

    async def _query_engram_decisions(
        self,
        since_timestamp: Optional[datetime] = None,
        phase_number: Optional[int] = None,
        decision_type_filter: Optional[str] = None,
    ) -> List[EngramDecision]:
        """
        Query Engram for decision observations.

        Uses Engram mem_search API with filters:
        - type=decision or type=bugfix (fix is a decision)
        - scope=project (not personal)
        - created_at > since_timestamp

        Returns parsed EngramDecision objects.
        """
        # In real implementation:
        # results = await self.engram.mem_search(
        #     query="decision OR bugfix",
        #     type="decision",
        #     scope="project",
        #     limit=100
        # )
        # return [self._parse_engram_decision(r) for r in results]

        # Stub: return empty list
        return []

    async def _query_engram_brain_feedback(
        self,
        phase_number: Optional[int] = None,
        brain_id_filter: Optional[int] = None,
    ) -> List[EngramBrainFeedback]:
        """
        Query Engram for brain feedback observations.

        Looks for:
        - type=discovery
        - scope=project
        - Title contains brain ID reference

        Returns parsed EngramBrainFeedback objects.
        """
        # In real implementation:
        # results = await self.engram.mem_search(
        #     query="brain insight OR brain feedback",
        #     type="discovery",
        #     scope="project",
        #     limit=100
        # )
        # return [self._parse_engram_feedback(r) for r in results]

        # Stub: return empty list
        return []

    async def _find_phase_execution_id(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_number: Optional[int],
        timestamp: datetime,
    ) -> Optional[UUID]:
        """
        Find phase_execution_id for a given phase/timestamp.

        Queries phase_executions table:
        - WHERE org_id = ? AND project_id = ? AND phase_number = ?
        - AND started_at <= timestamp <= completed_at
        - Returns latest execution if multiple exist

        Returns UUID of execution, or None if not found.
        """
        # In real implementation:
        # exec = db.query(PhaseExecution).filter(
        #     PhaseExecution.org_id == org_id,
        #     PhaseExecution.project_id == project_id,
        #     PhaseExecution.phase_number == phase_number,
        #     PhaseExecution.started_at <= timestamp,
        #     PhaseExecution.completed_at >= timestamp
        # ).order_by(PhaseExecution.created_at.desc()).first()
        # return exec.id if exec else None

        # Stub
        return None

    async def _is_decision_synced(self, engram_id: int) -> bool:
        """
        Check if decision already synced.

        Queries decisions table WHERE engram_link = ?
        Returns True if found, False otherwise.
        """
        # In real implementation:
        # count = db.query(Decision).filter(
        #     Decision.engram_link == str(engram_id)
        # ).count()
        # return count > 0

        # Stub
        return False

    async def _upsert_decision(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_execution_id: Optional[UUID],
        engram_decision: EngramDecision,
    ) -> UUID:
        """
        Upsert decision into decisions table.

        Uses PostgreSQL UPSERT (INSERT ... ON CONFLICT):
        - Conflict key: (org_id, project_id, engram_link)
        - Updates if exists, inserts if new

        Returns decision UUID.
        """
        # In real implementation:
        # stmt = insert(Decision).values(
        #     org_id=org_id,
        #     project_id=project_id,
        #     phase_execution_id=phase_execution_id,
        #     decision_type=engram_decision.decision_type,
        #     title=engram_decision.title,
        #     rationale=engram_decision.rationale,
        #     alternatives=engram_decision.alternatives,
        #     chosen_option=engram_decision.chosen_option,
        #     confidence=engram_decision.confidence,
        #     impact_level=engram_decision.impact_level,
        #     made_by=engram_decision.made_by,
        #     status="pending",
        #     engram_link=str(engram_decision.engram_id),
        #     tags=engram_decision.tags
        # ).on_conflict_do_update(
        #     index_elements=['org_id', 'project_id', 'engram_link'],
        #     set_=dict(
        #         title=engram_decision.title,
        #         rationale=engram_decision.rationale,
        #         updated_at=datetime.utcnow()
        #     )
        # )
        # result = db.execute(stmt)
        # return result.inserted_primary_key[0]

        # Stub
        return UUID("00000000-0000-0000-0000-000000000000")

    async def _upsert_brain_feedback(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_execution_id: Optional[UUID],
        feedback: EngramBrainFeedback,
    ) -> UUID:
        """
        Upsert brain feedback into brain_feedback table.

        Uses similar UPSERT pattern as decisions.
        Returns feedback UUID.
        """
        # In real implementation:
        # stmt = insert(BrainFeedback).values(
        #     org_id=org_id,
        #     project_id=project_id,
        #     phase_execution_id=phase_execution_id,
        #     brain_id=feedback.brain_id,
        #     feedback_type=feedback.feedback_type,
        #     title=feedback.title,
        #     content=feedback.content,
        #     confidence=feedback.confidence,
        #     engram_sync_id=str(feedback.engram_id)
        # ).on_conflict_do_update(...)
        # result = db.execute(stmt)
        # return result.inserted_primary_key[0]

        # Stub
        return UUID("00000000-0000-0000-0000-000000000000")

    async def _mark_decision_synced(self, engram_id: int, decision_id: UUID) -> None:
        """
        Mark decision as synced in Engram.

        Updates decision.engram_link with engram_id reference
        and engram_synced_at timestamp.
        """
        # In real implementation:
        # db.query(Decision).filter(
        #     Decision.id == decision_id
        # ).update({
        #     Decision.engram_link: str(engram_id),
        #     Decision.updated_at: datetime.utcnow()
        # })
        # db.commit()

        pass

    def _parse_engram_decision(self, engram_obs: Dict[str, Any]) -> EngramDecision:
        """Parse Engram observation into EngramDecision model"""
        # Extract metadata from engram observation title and content
        # Expected format from mem_save(type="decision", ...):
        # title: "Zustand > Redux decision"
        # content: "**What**: Chose Zustand...\n**Why**: Simpler API\n..."

        return EngramDecision(
            engram_id=engram_obs.get("id"),
            title=engram_obs.get("title", ""),
            decision_type="technical",  # Infer from context
            rationale=engram_obs.get("content", ""),
            created_at=engram_obs.get("created_at"),
            made_by=engram_obs.get("created_by", "system"),
        )

    def _parse_engram_feedback(self, engram_obs: Dict[str, Any]) -> EngramBrainFeedback:
        """Parse Engram observation into EngramBrainFeedback model"""
        # Extract brain ID and feedback from observation
        return EngramBrainFeedback(
            engram_id=engram_obs.get("id"),
            brain_id=1,  # Extract from title
            title=engram_obs.get("title", ""),
            feedback_type="insight",
            content=engram_obs.get("content", ""),
            created_at=engram_obs.get("created_at"),
        )


# ============================================================================
# PHASE EXECUTION RECORD SERVICE
# ============================================================================


class PhaseExecutionRecorder:
    """
    Records phase execution metadata to PostgreSQL.

    Used by state_machine.py to persist phase completion data.

    Usage:
        recorder = PhaseExecutionRecorder(db_session)
        await recorder.record_phase_completion(
            org_id=org_uuid,
            project_id=project_uuid,
            phase_number=18,
            backend_used="claude",
            tokens_consumed=25000,
            git_commit_hash="abc123...",
            output_summary="Phase 18 Wave 3 complete..."
        )
    """

    def __init__(self):
        # db_session: Session
        self.logger = logging.getLogger(__name__)

    async def record_phase_execution(
        self,
        org_id: UUID,
        project_id: UUID,
        workspace_id: Optional[UUID],
        phase_number: int,
        status: str,  # pending | in_progress | completed | failed
        backend_used: Optional[str] = None,
        tokens_consumed: int = 0,
        tokens_input: int = 0,
        tokens_output: int = 0,
        output_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        git_commit_hash: Optional[str] = None,
        triggered_by: str = "system",
    ) -> UUID:
        """
        Record phase execution to database.

        Called by state_machine.py on phase transitions:
        - Before phase starts: status='in_progress'
        - After phase completes: status='completed'
        - On failure: status='failed' with error_message

        Returns phase_execution_id for linking decisions/gates/artifacts.
        """
        # In real implementation:
        # exec = PhaseExecution(
        #     org_id=org_id,
        #     project_id=project_id,
        #     workspace_id=workspace_id,
        #     phase_number=phase_number,
        #     status=status,
        #     backend_used=backend_used,
        #     tokens_consumed=tokens_consumed,
        #     tokens_input=tokens_input,
        #     tokens_output=tokens_output,
        #     output_summary=output_summary,
        #     error_message=error_message,
        #     git_commit_hash=git_commit_hash,
        #     triggered_by=triggered_by
        # )
        # db.add(exec)
        # db.commit()
        # return exec.id

        # Stub
        execution_id = UUID("00000000-0000-0000-0000-000000000000")
        self.logger.info(
            f"Recorded phase execution: org={org_id}, project={project_id}, "
            f"phase={phase_number}, status={status}"
        )
        return execution_id

    async def record_verification_gate(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_execution_id: UUID,
        gate_type: str,
        gate_name: str,
        status: str,
        result: Dict[str, Any],
        score: Optional[float] = None,
        evaluated_by: str = "system",
    ) -> UUID:
        """
        Record verification gate result.

        Called during VERIFICATION phase.
        """
        # In real implementation: INSERT into verification_gates
        # Stub
        return UUID("00000000-0000-0000-0000-000000000000")

    async def record_artifact(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_execution_id: Optional[UUID],
        artifact_type: str,
        name: str,
        file_path: str,
        git_commit_hash: Optional[str] = None,
        created_by: str = "system",
    ) -> UUID:
        """
        Record artifact creation.

        Called when phase creates plans, specs, tests, docs.
        """
        # In real implementation: INSERT into artifacts
        # Stub
        return UUID("00000000-0000-0000-0000-000000000000")

    async def record_audit_log_entry(
        self,
        org_id: UUID,
        project_id: UUID,
        action_type: str,
        actor: str,
        description: str,
        phase_number: Optional[int] = None,
        severity: str = "info",
        related_entity_type: Optional[str] = None,
        related_entity_id: Optional[UUID] = None,
    ) -> UUID:
        """
        Record high-level audit log entry.

        Used for compliance tracking.
        """
        # In real implementation: INSERT into audit_log
        # Stub
        return UUID("00000000-0000-0000-0000-000000000000")


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================


async def sync_session_decisions(
    org_id: UUID,
    project_id: UUID,
    phase_number: int,
) -> Dict[str, Any]:
    """
    Convenience function: sync all decisions for a phase from Engram.

    Typically called at end of phase execution.
    """
    sync_service = EngramSyncService()
    return await sync_service.sync_decisions_to_db(
        org_id=org_id,
        project_id=project_id,
        phase_number=phase_number,
    )


async def sync_brain_insights(
    org_id: UUID,
    project_id: UUID,
    phase_number: int,
) -> Dict[str, Any]:
    """
    Convenience function: sync brain feedback for a phase.
    """
    sync_service = EngramSyncService()
    return await sync_service.sync_brain_feedback_to_db(
        org_id=org_id,
        project_id=project_id,
        phase_number=phase_number,
    )


__all__ = [
    "EngramSyncService",
    "PhaseExecutionRecorder",
    "EngramDecision",
    "EngramBrainFeedback",
    "sync_session_decisions",
    "sync_brain_insights",
]
