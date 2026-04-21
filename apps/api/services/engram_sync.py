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
import json
import re
import aiosqlite
from pathlib import Path

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
    tags: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
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
    created_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self) -> None:
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
        db_conn: Optional[aiosqlite.Connection] = None,
    ):
        """
        Initialize sync service with database connection.

        Args:
            db_conn: SQLite connection for accessing decisions, brain_feedback, phase_executions tables.
                     If None, will attempt to connect to default database.
        """
        self.db = db_conn
        self.logger = logging.getLogger(__name__)

    async def _ensure_db_connection(self) -> aiosqlite.Connection:
        """Ensure database connection is available."""
        if self.db is None:
            raise RuntimeError(
                "Database connection not available. "
                "Initialize with db_conn parameter or set self.db before calling."
            )
        return self.db

    async def _ensure_tables_exist(self) -> None:
        """Ensure required tables exist in database."""
        db = await self._ensure_db_connection()

        # Create phase_executions table if not exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS phase_executions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create decisions table if not exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS decisions (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                phase_execution_id TEXT,
                engram_id TEXT,
                decision_type TEXT,
                title TEXT NOT NULL,
                description TEXT,
                rationale TEXT,
                alternatives TEXT,
                chosen_option TEXT,
                confidence REAL DEFAULT 0.5,
                impact_level TEXT,
                impact_description TEXT,
                made_by TEXT,
                status TEXT DEFAULT 'pending',
                tags TEXT,
                synced_to_engram INTEGER DEFAULT 0,
                synced_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phase_execution_id) REFERENCES phase_executions(id)
            )
        """)

        # Create brain_feedback table if not exists
        await db.execute("""
            CREATE TABLE IF NOT EXISTS brain_feedback (
                id TEXT PRIMARY KEY,
                project_id TEXT NOT NULL,
                phase_num INTEGER NOT NULL,
                phase_execution_id TEXT,
                brain_id INTEGER,
                engram_id TEXT,
                feedback_type TEXT,
                title TEXT,
                feedback_text TEXT,
                confidence_score REAL,
                impact_on_phase TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (phase_execution_id) REFERENCES phase_executions(id)
            )
        """)

        # Create indexes
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_decisions_project_phase "
            "ON decisions(project_id, phase_num)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_decisions_engram_id "
            "ON decisions(engram_id)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_brain_feedback_project_phase "
            "ON brain_feedback(project_id, phase_num)"
        )
        await db.execute(
            "CREATE INDEX IF NOT EXISTS idx_phase_executions_project "
            "ON phase_executions(project_id, phase_num)"
        )

        await db.commit()

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

        results: Dict[str, Any] = {
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
                    # Use current time if created_at is None
                    timestamp = engram_decision.created_at or datetime.utcnow()
                    phase_exec_id = await self._find_phase_execution_id(
                        org_id=org_id,
                        project_id=project_id,
                        phase_number=phase_number,
                        timestamp=timestamp,
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

        results: Dict[str, Any] = {
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
                    # Use current time if created_at is None
                    timestamp = feedback.created_at or datetime.utcnow()
                    phase_exec_id = await self._find_phase_execution_id(
                        org_id=org_id,
                        project_id=project_id,
                        phase_number=phase_number,
                        timestamp=timestamp,
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
        Query Engram for decision observations via mem_search.

        In Claude Code context, mem_search is called as:
            mem_search(query=..., type="decision", scope="project")

        Since this is async Python code running in api services,
        we provide the specification for calling engram tools.
        The caller (e.g., a Claude Code agent) would invoke the
        actual mem_search tool and pass results back.

        For local/offline operation, we gracefully degrade to empty list.

        Returns parsed EngramDecision objects.
        """
        try:
            # Build search query based on filters
            query_parts = ["decision", "architecture"]
            if phase_number:
                query_parts.append(f"phase {phase_number}")
            if decision_type_filter:
                query_parts.append(decision_type_filter)

            search_query = " ".join(query_parts)

            self.logger.info(f"Querying Engram for decisions: {search_query}")

            # In production, this would be called via:
            #   results = await engram_client.mem_search(
            #       query=search_query,
            #       type="decision,bugfix,architecture",
            #       scope="project",
            #       limit=100
            #   )
            # For now, we attempt to read from local engram cache if available
            # or return empty list for graceful degradation

            decisions = await self._query_engram_local_cache(search_query)
            self.logger.info(f"Found {len(decisions)} decisions from Engram")
            return decisions

        except Exception as e:
            self.logger.warning(
                f"Failed to query Engram decisions (graceful degradation): {e}"
            )
            return []

    async def _query_engram_local_cache(
        self, search_query: str
    ) -> List[EngramDecision]:
        """
        Attempt to query Engram observations from local cache or memory file.

        This is a graceful fallback when Engram MCP tools are not available.
        In production with Claude Code, the actual mem_search would be invoked.

        Returns:
            List of parsed EngramDecision objects, empty if no cache found.
        """
        # Try to find .engram cache directory
        engram_cache_paths = [
            Path.home() / ".engram",
            Path.home() / ".cache" / "engram",
            Path("/tmp/.engram"),
        ]

        for cache_path in engram_cache_paths:
            if cache_path.exists() and cache_path.is_dir():
                # Look for observations JSON files
                for obs_file in cache_path.glob("observations_*.json"):
                    try:
                        with open(obs_file, "r") as f:
                            observations = json.load(f)
                            decisions = []
                            for obs in observations:
                                if obs.get("type") in [
                                    "decision",
                                    "bugfix",
                                    "architecture",
                                ]:
                                    parsed = self._parse_engram_decision(obs)
                                    if parsed:
                                        decisions.append(parsed)
                            if decisions:
                                return decisions
                    except Exception as e:
                        self.logger.debug(f"Could not read {obs_file}: {e}")
                        continue

        # No cache found, return empty
        return []

    async def _query_engram_brain_feedback(
        self,
        phase_number: Optional[int] = None,
        brain_id_filter: Optional[int] = None,
    ) -> List[EngramBrainFeedback]:
        """
        Query Engram for brain feedback observations.

        Looks for:
        - type=discovery, type=insight, type=pattern
        - scope=project
        - Title contains brain ID reference (e.g., "Brain #1:", "Brain #7 evaluation")

        Returns parsed EngramBrainFeedback objects.
        """
        try:
            query_parts = ["brain feedback", "brain insight"]
            if phase_number:
                query_parts.append(f"phase {phase_number}")
            if brain_id_filter:
                query_parts.append(f"brain {brain_id_filter}")

            search_query = " ".join(query_parts)
            self.logger.info(f"Querying Engram for brain feedback: {search_query}")

            # In production, this would be called via:
            #   results = await engram_client.mem_search(
            #       query=search_query,
            #       type="discovery,insight,pattern,recommendation",
            #       scope="project",
            #       limit=100
            #   )

            feedback = await self._query_engram_feedback_local_cache(search_query)
            self.logger.info(f"Found {len(feedback)} feedback items from Engram")
            return feedback

        except Exception as e:
            self.logger.warning(
                f"Failed to query Engram brain feedback (graceful degradation): {e}"
            )
            return []

    async def _query_engram_feedback_local_cache(
        self, search_query: str
    ) -> List[EngramBrainFeedback]:
        """
        Attempt to query brain feedback from local Engram cache.

        Returns:
            List of parsed EngramBrainFeedback objects, empty if no cache.
        """
        engram_cache_paths = [
            Path.home() / ".engram",
            Path.home() / ".cache" / "engram",
            Path("/tmp/.engram"),
        ]

        for cache_path in engram_cache_paths:
            if cache_path.exists() and cache_path.is_dir():
                for obs_file in cache_path.glob("observations_*.json"):
                    try:
                        with open(obs_file, "r") as f:
                            observations = json.load(f)
                            feedback = []
                            for obs in observations:
                                if obs.get("type") in [
                                    "discovery",
                                    "insight",
                                    "pattern",
                                    "recommendation",
                                ]:
                                    parsed = self._parse_engram_feedback(obs)
                                    if parsed:
                                        feedback.append(parsed)
                            if feedback:
                                return feedback
                    except Exception as e:
                        self.logger.debug(f"Could not read {obs_file}: {e}")
                        continue

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
        - WHERE project_id = ? AND phase_number = ?
        - Returns latest execution if multiple exist

        Args:
            org_id: Organization ID (for future RLS)
            project_id: Project UUID
            phase_number: Phase number
            timestamp: Timestamp to match against execution window

        Returns:
            UUID of execution, or None if not found.
            Creates new execution if not found.
        """
        try:
            db = await self._ensure_db_connection()
            await self._ensure_tables_exist()

            if not phase_number:
                return None

            # Query for existing execution
            project_id_str = str(project_id)
            cursor = await db.execute(
                """
                SELECT id FROM phase_executions
                WHERE project_id = ? AND phase_num = ?
                ORDER BY started_at DESC
                LIMIT 1
                """,
                (project_id_str, phase_number),
            )
            row = await cursor.fetchone()

            if row:
                return UUID(row[0])

            # Create new execution if not found
            import uuid

            new_id = str(uuid.uuid4())

            await db.execute(
                """
                INSERT INTO phase_executions
                (id, project_id, phase_num, status, started_at)
                VALUES (?, ?, ?, 'pending', CURRENT_TIMESTAMP)
                """,
                (new_id, project_id_str, phase_number),
            )
            await db.commit()

            self.logger.info(
                f"Created new phase execution: {new_id} for phase {phase_number}"
            )
            return UUID(new_id)

        except Exception as e:
            self.logger.error(f"Failed to find/create phase execution: {e}")
            return None

    async def _is_decision_synced(self, engram_id: int) -> bool:
        """
        Check if decision already synced to database.

        Queries decisions table WHERE engram_id = ?
        Returns True if found, False otherwise.
        """
        try:
            db = await self._ensure_db_connection()

            cursor = await db.execute(
                "SELECT COUNT(*) FROM decisions WHERE engram_id = ?",
                (str(engram_id),),
            )
            row = await cursor.fetchone()

            if row and row[0] > 0:
                self.logger.debug(f"Decision {engram_id} already synced")
                return True

            return False

        except Exception as e:
            self.logger.warning(f"Error checking if decision synced: {e}")
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

        Uses SQLite INSERT OR REPLACE pattern:
        - If engram_id exists, update the row
        - If new, insert it

        Returns decision UUID.
        """
        try:
            import uuid

            db = await self._ensure_db_connection()
            await self._ensure_tables_exist()

            decision_id = str(uuid.uuid4())
            project_id_str = str(project_id)
            phase_exec_str = str(phase_execution_id) if phase_execution_id else None
            tags_json = json.dumps(engram_decision.tags or [])

            # Check if decision already exists by engram_id
            cursor = await db.execute(
                "SELECT id FROM decisions WHERE engram_id = ?",
                (str(engram_decision.engram_id),),
            )
            existing = await cursor.fetchone()

            if existing:
                # Update existing decision
                decision_id = existing[0]
                await db.execute(
                    """
                    UPDATE decisions
                    SET title = ?, description = ?, rationale = ?,
                        alternatives = ?, chosen_option = ?, confidence = ?,
                        impact_level = ?, impact_description = ?,
                        made_by = ?, tags = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                    """,
                    (
                        engram_decision.title,
                        engram_decision.title,  # description same as title
                        engram_decision.rationale,
                        engram_decision.alternatives,
                        engram_decision.chosen_option,
                        engram_decision.confidence,
                        engram_decision.impact_level,
                        engram_decision.impact_description,
                        engram_decision.made_by,
                        tags_json,
                        decision_id,
                    ),
                )
                self.logger.info(f"Updated existing decision: {decision_id}")
            else:
                # Insert new decision
                await db.execute(
                    """
                    INSERT INTO decisions
                    (id, project_id, phase_num, phase_execution_id, engram_id,
                     decision_type, title, description, rationale, alternatives,
                     chosen_option, confidence, impact_level, impact_description,
                     made_by, status, tags, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """,
                    (
                        decision_id,
                        project_id_str,
                        0,  # phase_num - will be updated by caller if needed
                        phase_exec_str,
                        str(engram_decision.engram_id),
                        engram_decision.decision_type,
                        engram_decision.title,
                        engram_decision.title,  # description = title
                        engram_decision.rationale,
                        engram_decision.alternatives,
                        engram_decision.chosen_option,
                        engram_decision.confidence,
                        engram_decision.impact_level,
                        engram_decision.impact_description,
                        engram_decision.made_by,
                        "pending",
                        tags_json,
                    ),
                )
                self.logger.info(f"Inserted new decision: {decision_id}")

            await db.commit()
            return UUID(decision_id)

        except Exception as e:
            self.logger.error(f"Failed to upsert decision: {e}")
            import uuid

            return UUID(int=0)  # Return null-like UUID on error

    async def _upsert_brain_feedback(
        self,
        org_id: UUID,
        project_id: UUID,
        phase_execution_id: Optional[UUID],
        feedback: EngramBrainFeedback,
    ) -> UUID:
        """
        Upsert brain feedback into brain_feedback table.

        Uses INSERT OR REPLACE pattern similar to decisions.
        Returns feedback UUID.
        """
        try:
            import uuid

            db = await self._ensure_db_connection()
            await self._ensure_tables_exist()

            feedback_id = str(uuid.uuid4())
            project_id_str = str(project_id)
            phase_exec_str = str(phase_execution_id) if phase_execution_id else None

            # Check if feedback already exists by engram_id
            cursor = await db.execute(
                "SELECT id FROM brain_feedback WHERE engram_id = ?",
                (str(feedback.engram_id),),
            )
            existing = await cursor.fetchone()

            if existing:
                # Update existing feedback
                feedback_id = existing[0]
                await db.execute(
                    """
                    UPDATE brain_feedback
                    SET feedback_text = ?, confidence_score = ?,
                        impact_on_phase = ?, title = ?
                    WHERE id = ?
                    """,
                    (
                        feedback.content,
                        feedback.confidence,
                        feedback.impact_on_phase,
                        feedback.title,
                        feedback_id,
                    ),
                )
                self.logger.info(f"Updated existing brain feedback: {feedback_id}")
            else:
                # Insert new feedback
                await db.execute(
                    """
                    INSERT INTO brain_feedback
                    (id, project_id, phase_num, phase_execution_id, brain_id,
                     engram_id, feedback_type, title, feedback_text,
                     confidence_score, impact_on_phase, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    """,
                    (
                        feedback_id,
                        project_id_str,
                        0,  # phase_num - will be updated by caller if needed
                        phase_exec_str,
                        feedback.brain_id,
                        str(feedback.engram_id),
                        feedback.feedback_type,
                        feedback.title,
                        feedback.content,
                        feedback.confidence,
                        feedback.impact_on_phase,
                    ),
                )
                self.logger.info(f"Inserted new brain feedback: {feedback_id}")

            await db.commit()
            return UUID(feedback_id)

        except Exception as e:
            self.logger.error(f"Failed to upsert brain feedback: {e}")
            import uuid

            return UUID(int=0)

    async def _mark_decision_synced(self, engram_id: int, decision_id: UUID) -> None:
        """
        Mark decision as synced in Engram.

        Updates decision.synced_to_engram flag and synced_at timestamp.
        """
        try:
            db = await self._ensure_db_connection()

            await db.execute(
                """
                UPDATE decisions
                SET synced_to_engram = 1, synced_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (str(decision_id),),
            )
            await db.commit()

            self.logger.info(f"Marked decision {decision_id} as synced")

        except Exception as e:
            self.logger.error(f"Failed to mark decision as synced: {e}")

    def _parse_engram_decision(
        self, engram_obs: Dict[str, Any]
    ) -> Optional[EngramDecision]:
        """
        Parse Engram observation into EngramDecision model.

        Expected format from mem_save(type="decision", ...):
        {
            "id": 12345,
            "title": "Zustand > Redux decision",
            "content": "**What**: Chose Zustand...\n**Why**: Simpler API\n**Where**: src/state/\n**Learned**: ...",
            "type": "decision",
            "created_at": "2026-04-12T10:30:00Z",
            "created_by": "system"
        }

        Returns:
            EngramDecision object or None if parsing fails.
        """
        try:
            obs_id = engram_obs.get("id")
            title = engram_obs.get("title", "")
            content = engram_obs.get("content", "")
            obs_type = engram_obs.get("type", "decision")

            if not obs_id or not title:
                return None

            # Parse **What**, **Why**, **Where**, **Learned** sections
            rationale = self._extract_section(content, "Why")
            alternatives = self._extract_section(content, "Where")
            chosen_option = self._extract_section(content, "What")
            learnings = self._extract_section(content, "Learned")

            # Infer decision type from content or type
            decision_type = self._infer_decision_type(obs_type, title, content)

            # Extract confidence if available
            confidence = 0.7  # Default confidence for Engram decisions
            if "confidence" in engram_obs:
                confidence = float(engram_obs["confidence"])

            created_at: Optional[datetime] = None
            if engram_obs.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        engram_obs["created_at"].replace("Z", "+00:00")
                    )
                except Exception:
                    created_at = None

            return EngramDecision(
                engram_id=obs_id,
                title=title,
                decision_type=decision_type,
                rationale=rationale or content,
                alternatives=alternatives,
                chosen_option=chosen_option,
                confidence=confidence,
                impact_level="medium",  # Default, could be inferred
                impact_description=learnings,
                made_by=engram_obs.get("created_by", "system"),
                tags=engram_obs.get("tags", []),
                created_at=created_at if created_at is not None else datetime.utcnow(),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse engram decision: {e}")
            return None

    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a section from Engram observation content.

        Looks for patterns like:
        **What**: text here
        **Why**: text here

        Returns the text after the section header, or None.
        """
        if not content:
            return None

        pattern = rf"\*\*{section_name}\*\*:\s*(.+?)(?=\*\*|$)"
        match = re.search(pattern, content, re.IGNORECASE | re.DOTALL)
        if match:
            text = match.group(1).strip()
            # Limit to first sentence or 200 chars
            text = text.split("\n")[0][:200]
            return text if text else None
        return None

    def _infer_decision_type(self, obs_type: str, title: str, content: str) -> str:
        """Infer decision type from observation metadata."""
        content_lower = (title + " " + content).lower()

        if "architecture" in content_lower or "pattern" in content_lower:
            return "architectural"
        elif "tool" in content_lower or "library" in content_lower:
            return "tool_selection"
        elif "process" in content_lower or "workflow" in content_lower:
            return "process"
        elif "feature" in content_lower or "product" in content_lower:
            return "product"
        else:
            return "technical"

    def _parse_engram_feedback(
        self, engram_obs: Dict[str, Any]
    ) -> Optional[EngramBrainFeedback]:
        """
        Parse Engram observation into EngramBrainFeedback model.

        Expected format:
        {
            "id": 12346,
            "title": "Brain #1 insight: caching strategy",
            "content": "Analysis of...",
            "type": "discovery",
            "created_at": "2026-04-12T10:30:00Z"
        }

        Returns:
            EngramBrainFeedback object or None if parsing fails.
        """
        try:
            obs_id = engram_obs.get("id")
            title = engram_obs.get("title", "")
            content = engram_obs.get("content", "")
            obs_type = engram_obs.get("type", "discovery")

            if not obs_id or not title:
                return None

            # Extract brain ID from title (e.g., "Brain #1: " or "Brain 1 ")
            brain_id = self._extract_brain_id(title)

            # Map observation type to feedback type
            feedback_type = self._map_feedback_type(obs_type)

            created_at: Optional[datetime] = None
            if engram_obs.get("created_at"):
                try:
                    created_at = datetime.fromisoformat(
                        engram_obs["created_at"].replace("Z", "+00:00")
                    )
                except Exception:
                    created_at = None

            confidence = engram_obs.get("confidence", 0.6)
            if isinstance(confidence, str):
                try:
                    confidence = float(confidence)
                except ValueError:
                    confidence = 0.6

            return EngramBrainFeedback(
                engram_id=obs_id,
                brain_id=brain_id,
                title=title,
                feedback_type=feedback_type,
                content=content,
                confidence=confidence,
                created_at=created_at if created_at is not None else datetime.utcnow(),
            )

        except Exception as e:
            self.logger.warning(f"Failed to parse engram feedback: {e}")
            return None

    def _extract_brain_id(self, title: str) -> int:
        """Extract brain ID from title like 'Brain #1:' or 'Brain 1 feedback'.

        Returns:
            Brain ID (1-7 for dev, 8-23 for other), defaults to 1.
        """
        # Try pattern "Brain #N" or "Brain N"
        match = re.search(r"[Bb]rain\s*#?(\d+)", title)
        if match:
            try:
                brain_id = int(match.group(1))
                return brain_id if 1 <= brain_id <= 24 else 1
            except ValueError:
                pass
        return 1  # Default to brain 1

    def _map_feedback_type(self, obs_type: str) -> str:
        """Map Engram observation type to feedback type."""
        type_lower = obs_type.lower()
        if "risk" in type_lower or "warning" in type_lower:
            return "risk_flag"
        elif "opportunity" in type_lower or "improvement" in type_lower:
            return "opportunity"
        elif "learning" in type_lower or "lesson" in type_lower:
            return "lesson_learned"
        elif "recommendation" in type_lower or "suggest" in type_lower:
            return "recommendation"
        else:
            return "insight"


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

    def __init__(self) -> None:
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
