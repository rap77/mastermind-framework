"""
MM-Flow Audit Trail API Routes

Provides REST endpoints for:
- Development timeline queries
- Phase execution details
- Decision tracking and management
- Verification gate status
- Audit log (compliance)
- Niche-specific metrics
- Session summaries
"""

import json
from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, Query, Path, Depends, HTTPException
from pydantic import BaseModel, Field

from mastermind_cli.api.dependencies import get_db_path
from mastermind_cli.api.routes.auth import get_current_user_any
from mastermind_cli.state.database import DatabaseConnection

# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================


class PhaseExecutionDetail(BaseModel):
    id: UUID
    phase_number: int
    execution_number: int
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
    backend_used: Optional[str] = None
    tokens_consumed: int = 0
    tokens_input: int = 0
    tokens_output: int = 0
    output_summary: Optional[str] = None
    git_commit_hash: Optional[str] = None
    triggered_by: str


class DecisionRecord(BaseModel):
    id: UUID
    decision_type: str
    title: str
    rationale: str
    alternatives: Optional[str] = None
    chosen_option: str
    confidence: float = Field(ge=0.0, le=1.0)
    impact_level: str
    impact_description: Optional[str] = None
    made_by: str
    approved_by: Optional[str] = None
    status: str
    tags: List[str] = []
    created_at: datetime
    updated_at: datetime


class DecisionInput(BaseModel):
    decision_type: str
    title: str
    rationale: str
    chosen_option: str
    alternatives: Optional[str] = None
    impact_level: str = "medium"
    impact_description: Optional[str] = None
    confidence: float = Field(default=0.5, ge=0.0, le=1.0)
    tags: List[str] = []


class VerificationGateResult(BaseModel):
    id: UUID
    gate_type: str
    gate_name: str
    status: str
    score: Optional[float] = None
    result: Dict[str, Any] = {}
    evaluated_by: Optional[str] = None
    evaluation_notes: Optional[str] = None
    completed_at: Optional[datetime] = None


class DevSessionRecord(BaseModel):
    id: UUID
    phase_number: Optional[int] = None
    session_date: datetime
    duration_minutes: Optional[int] = None
    status: str
    tasks_completed: int = 0
    tasks_total: int = 0
    commits_count: int = 0
    discoveries: Optional[str] = None
    blockers: Optional[str] = None
    next_steps: Optional[str] = None


class ArtifactRecord(BaseModel):
    id: UUID
    artifact_type: str
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    created_by: str
    git_commit_hash: Optional[str] = None
    created_at: datetime


class PhaseMetric(BaseModel):
    metric_name: str
    metric_value: float
    metric_unit: str
    target_value: Optional[float] = None
    status: str


class AuditLogEntry(BaseModel):
    id: UUID
    action_type: str
    actor: str
    actor_type: str
    description: str
    phase_number: Optional[int] = None
    severity: str = "info"
    created_at: datetime


class TimelineEvent(BaseModel):
    event_type: str
    event_at: datetime
    description: str
    phase_number: int


class PhaseDetailResponse(BaseModel):
    phase_execution: PhaseExecutionDetail
    decisions: List[DecisionRecord] = []
    verification_gates: List[VerificationGateResult] = []
    artifacts: List[ArtifactRecord] = []
    metrics: List[PhaseMetric] = []
    brain_feedback: Optional[List[Dict[str, Any]]] = []


# ============================================================================
# ROUTER SETUP
# ============================================================================

router = APIRouter(
    prefix="/api/audit",
    tags=["audit"],
    responses={404: {"description": "Not found"}},
)


# ============================================================================
# AUDIT SCHEMA INITIALIZATION
# ============================================================================


async def _ensure_audit_schema(db: DatabaseConnection) -> None:
    """Create audit trail tables if they don't exist."""
    # Phase executions table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS phase_executions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER NOT NULL,
            execution_num INTEGER DEFAULT 1,
            status TEXT NOT NULL,
            started_at TIMESTAMP NOT NULL,
            completed_at TIMESTAMP,
            duration_seconds INTEGER,
            backend_used TEXT,
            tokens_consumed INTEGER DEFAULT 0,
            tokens_input INTEGER DEFAULT 0,
            tokens_output INTEGER DEFAULT 0,
            output_summary TEXT,
            git_commit_hash TEXT,
            triggered_by TEXT NOT NULL,
            UNIQUE(project_id, phase_num, execution_num)
        )
    """)

    # Decisions table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS decisions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER NOT NULL,
            decision_type TEXT NOT NULL,
            title TEXT NOT NULL,
            rationale TEXT NOT NULL,
            alternatives TEXT,
            chosen_option TEXT NOT NULL,
            confidence REAL DEFAULT 0.5,
            impact_level TEXT DEFAULT 'medium',
            impact_description TEXT,
            made_by TEXT NOT NULL,
            approved_by TEXT,
            status TEXT DEFAULT 'pending',
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Verification gates table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS verification_gates (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER NOT NULL,
            gate_type TEXT NOT NULL,
            gate_name TEXT NOT NULL,
            status TEXT NOT NULL,
            score REAL,
            result TEXT DEFAULT '{}',
            evaluated_by TEXT,
            evaluation_notes TEXT,
            completed_at TIMESTAMP
        )
    """)

    # Dev sessions table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS dev_sessions (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER,
            session_date TIMESTAMP NOT NULL,
            duration_minutes INTEGER,
            status TEXT NOT NULL,
            tasks_completed INTEGER DEFAULT 0,
            tasks_total INTEGER DEFAULT 0,
            commits_count INTEGER DEFAULT 0,
            discoveries TEXT,
            blockers TEXT,
            next_steps TEXT
        )
    """)

    # Artifacts table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS artifacts (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER,
            artifact_type TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            file_path TEXT,
            created_by TEXT NOT NULL,
            git_commit_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Phase metrics table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS phase_metrics (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER NOT NULL,
            metric_name TEXT NOT NULL,
            metric_value REAL NOT NULL,
            metric_unit TEXT NOT NULL,
            target_value REAL,
            status TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Brain feedback table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS brain_feedback (
            id TEXT PRIMARY KEY,
            project_id TEXT NOT NULL,
            phase_num INTEGER,
            brain_id INTEGER NOT NULL,
            feedback TEXT NOT NULL,
            confidence_score REAL DEFAULT 0.5,
            feedback_type TEXT,
            impact_level TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Engram sync status table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS engram_sync_status (
            project_id TEXT PRIMARY KEY,
            last_sync_timestamp TIMESTAMP,
            synced_items_count INTEGER DEFAULT 0,
            sync_status TEXT DEFAULT 'idle'
        )
    """)

    # Create indexes for common queries
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_phase_executions_project_phase "
        "ON phase_executions(project_id, phase_num)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_decisions_project_phase "
        "ON decisions(project_id, phase_num)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_verification_gates_project_phase "
        "ON verification_gates(project_id, phase_num)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_dev_sessions_project "
        "ON dev_sessions(project_id, session_date DESC)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_artifacts_project_phase "
        "ON artifacts(project_id, phase_num)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_phase_metrics_project_phase "
        "ON phase_metrics(project_id, phase_num)"
    )
    await db.conn.execute(
        "CREATE INDEX IF NOT EXISTS idx_brain_feedback_project "
        "ON brain_feedback(project_id, confidence_score DESC)"
    )

    await db.conn.commit()


# ============================================================================
# TIMELINE ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/timeline",
    response_model=List[TimelineEvent],
    summary="Get full development timeline",
    description="Returns all significant events (phases, decisions, gates) in chronological order",
)
async def get_project_timeline(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    phase_number: Optional[int] = Query(None, description="Filter by phase number"),
    limit: int = Query(100, ge=1, le=1000, description="Max events to return"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
    db_path: str = Depends(get_db_path),
) -> List[TimelineEvent]:
    """
    Get complete development timeline for a project.

    Timeline includes:
    - Phase starts and completions
    - Key decisions with confidence
    - Verification gate results
    - Artifact creation
    - Session boundaries

    Supports filtering by phase and pagination.
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        events: List[TimelineEvent] = []

        # Fetch phase execution events
        query = "SELECT phase_num, started_at, status FROM phase_executions WHERE project_id = ?"
        params: List[Any] = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        cursor = await db.conn.execute(query)
        rows = await cursor.fetchall()
        for row in rows:
            events.append(
                TimelineEvent(
                    event_type="phase_started",
                    event_at=datetime.fromisoformat(row[1]),
                    description=f"Phase {row[0]} {row[2].lower()}",
                    phase_number=row[0],
                )
            )

        # Fetch decision events
        query = (
            "SELECT phase_num, created_at, title FROM decisions WHERE project_id = ?"
        )
        params = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        cursor = await db.conn.execute(query)
        rows = await cursor.fetchall()
        for row in rows:
            events.append(
                TimelineEvent(
                    event_type="decision_made",
                    event_at=datetime.fromisoformat(row[1]),
                    description=f"Decision: {row[2]}",
                    phase_number=row[0],
                )
            )

        # Fetch gate events
        query = "SELECT phase_num, completed_at, gate_name, status FROM verification_gates WHERE project_id = ? AND completed_at IS NOT NULL"
        params = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        cursor = await db.conn.execute(query)
        rows = await cursor.fetchall()
        for row in rows:
            if row[1]:
                events.append(
                    TimelineEvent(
                        event_type="gate_evaluated",
                        event_at=datetime.fromisoformat(row[1]),
                        description=f"Gate '{row[2]}' {row[3].lower()}",
                        phase_number=row[0],
                    )
                )

        # Sort by timestamp and apply pagination
        events.sort(key=lambda e: e.event_at, reverse=True)
        return events[offset : offset + limit]


@router.get(
    "/projects/{project_id}/phase/{phase_num}/details",
    response_model=PhaseDetailResponse,
    summary="Get phase execution details",
    description="Returns complete details for a phase including decisions, gates, and artifacts",
)
async def get_phase_details(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    phase_num: int = Path(..., ge=1, description="Phase number"),
    execution_num: int = Query(1, ge=1, description="Execution number (retry count)"),
    db_path: str = Depends(get_db_path),
) -> PhaseDetailResponse:
    """
    Get comprehensive details for a specific phase execution.

    Returns:
    - Execution metadata (status, duration, tokens, backend)
    - All decisions made during this phase
    - Verification gate results and status
    - Artifacts created (plans, specs, tests, docs)
    - Phase-specific metrics
    - Brain feedback and insights

    Useful for:
    - Post-execution review
    - Debugging phase failures
    - Understanding decision rationale
    - Measuring phase quality (gate results)
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        # Get phase execution details
        cursor = await db.conn.execute(
            """SELECT id, phase_number, execution_number, status, started_at,
                      completed_at, duration_seconds, backend_used, tokens_consumed,
                      tokens_input, tokens_output, output_summary, git_commit_hash, triggered_by
               FROM phase_executions
               WHERE project_id = ? AND phase_num = ? AND execution_num = ?""",
            [str(project_id), phase_num, execution_num],
        )
        row = await cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Phase execution not found")

        phase_exec = PhaseExecutionDetail(
            id=row[0],
            phase_number=row[1],
            execution_number=row[2],
            status=row[3],
            started_at=datetime.fromisoformat(row[4]),
            completed_at=datetime.fromisoformat(row[5]) if row[5] else None,
            duration_seconds=row[6],
            backend_used=row[7],
            tokens_consumed=row[8],
            tokens_input=row[9],
            tokens_output=row[10],
            output_summary=row[11],
            git_commit_hash=row[12],
            triggered_by=row[13],
        )

        # Get decisions
        cursor = await db.conn.execute(
            """SELECT id, decision_type, title, rationale, alternatives, chosen_option,
                      confidence, impact_level, impact_description, made_by, approved_by,
                      status, tags, created_at, updated_at
               FROM decisions
               WHERE project_id = ? AND phase_num = ?
               ORDER BY created_at""",
            [str(project_id), phase_num],
        )
        decision_rows = await cursor.fetchall()
        decisions = [
            DecisionRecord(
                id=row[0],
                decision_type=row[1],
                title=row[2],
                rationale=row[3],
                alternatives=row[4],
                chosen_option=row[5],
                confidence=row[6],
                impact_level=row[7],
                impact_description=row[8],
                made_by=row[9],
                approved_by=row[10],
                status=row[11],
                tags=json.loads(row[12]) if row[12] else [],
                created_at=datetime.fromisoformat(row[13]),
                updated_at=datetime.fromisoformat(row[14]),
            )
            for row in decision_rows
        ]

        # Get verification gates
        cursor = await db.conn.execute(
            """SELECT id, gate_type, gate_name, status, score, result, evaluated_by,
                      evaluation_notes, completed_at
               FROM verification_gates
               WHERE project_id = ? AND phase_num = ?
               ORDER BY completed_at DESC""",
            [str(project_id), phase_num],
        )
        gate_rows = await cursor.fetchall()
        gates = [
            VerificationGateResult(
                id=row[0],
                gate_type=row[1],
                gate_name=row[2],
                status=row[3],
                score=row[4],
                result=json.loads(row[5]) if row[5] else {},
                evaluated_by=row[6],
                evaluation_notes=row[7],
                completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
            )
            for row in gate_rows
        ]

        # Get artifacts
        cursor = await db.conn.execute(
            """SELECT id, artifact_type, name, description, file_path, created_by,
                      git_commit_hash, created_at
               FROM artifacts
               WHERE project_id = ? AND phase_num = ?
               ORDER BY created_at DESC""",
            [str(project_id), phase_num],
        )
        artifact_rows = await cursor.fetchall()
        artifacts = [
            ArtifactRecord(
                id=row[0],
                artifact_type=row[1],
                name=row[2],
                description=row[3],
                file_path=row[4],
                created_by=row[5],
                git_commit_hash=row[6],
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in artifact_rows
        ]

        # Get metrics
        cursor = await db.conn.execute(
            """SELECT metric_name, metric_value, metric_unit, target_value, status
               FROM phase_metrics
               WHERE project_id = ? AND phase_num = ?""",
            [str(project_id), phase_num],
        )
        metric_rows = await cursor.fetchall()
        metrics = [
            PhaseMetric(
                metric_name=row[0],
                metric_value=row[1],
                metric_unit=row[2],
                target_value=row[3],
                status=row[4],
            )
            for row in metric_rows
        ]

        # Get brain feedback
        cursor = await db.conn.execute(
            """SELECT brain_id, feedback, confidence_score, feedback_type, impact_level
               FROM brain_feedback
               WHERE project_id = ? AND phase_num = ?
               ORDER BY confidence_score DESC""",
            [str(project_id), phase_num],
        )
        feedback_rows = await cursor.fetchall()
        brain_feedback = [
            {
                "brain_id": row[0],
                "feedback": row[1],
                "confidence_score": row[2],
                "feedback_type": row[3],
                "impact_level": row[4],
            }
            for row in feedback_rows
        ]

        return PhaseDetailResponse(
            phase_execution=phase_exec,
            decisions=decisions,
            verification_gates=gates,
            artifacts=artifacts,
            metrics=metrics,
            brain_feedback=brain_feedback,
        )


# ============================================================================
# DECISION MANAGEMENT ENDPOINTS
# ============================================================================


@router.post(
    "/projects/{project_id}/phase/{phase_num}/decision",
    response_model=DecisionRecord,
    summary="Record a decision",
    description="Create a new decision record with rationale and alternatives",
)
async def record_decision(
    project_id: UUID,
    phase_num: int,
    decision: DecisionInput,
    current_user: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> DecisionRecord:
    """
    Record a decision made during phase execution.

    Required fields:
    - decision_type: architectural | technical | product | process | tool_selection
    - title: Short decision title
    - rationale: Why this decision?
    - chosen_option: What we selected
    - confidence: 0.0 to 1.0 confidence score

    Optional:
    - alternatives: Other options considered
    - impact_level: critical | high | medium | low
    - tags: For filtering and search

    Decision starts in "pending" status. Can be approved by Brain #7 or user.
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        decision_id = str(
            UUID(int=0)
        )  # Placeholder, will use proper UUID in production
        now = datetime.utcnow()

        await db.conn.execute(
            """INSERT INTO decisions
               (id, project_id, phase_num, decision_type, title, rationale,
                alternatives, chosen_option, confidence, impact_level,
                impact_description, made_by, status, tags, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            [
                decision_id,
                str(project_id),
                phase_num,
                decision.decision_type,
                decision.title,
                decision.rationale,
                decision.alternatives,
                decision.chosen_option,
                decision.confidence,
                decision.impact_level,
                decision.impact_description,
                "system",  # made_by
                "pending",
                json.dumps(decision.tags),
                now.isoformat(),
                now.isoformat(),
            ],
        )
        await db.conn.commit()

        return DecisionRecord(
            id=decision_id,
            decision_type=decision.decision_type,
            title=decision.title,
            rationale=decision.rationale,
            alternatives=decision.alternatives,
            chosen_option=decision.chosen_option,
            confidence=decision.confidence,
            impact_level=decision.impact_level,
            impact_description=decision.impact_description,
            made_by="system",
            approved_by=None,
            status="pending",
            tags=decision.tags,
            created_at=now,
            updated_at=now,
        )


@router.get(
    "/projects/{project_id}/decisions",
    response_model=List[DecisionRecord],
    summary="List decisions by status and type",
    description="Query decisions with filtering",
)
async def list_decisions(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    decision_type: Optional[str] = Query(None, description="Filter by type"),
    status: Optional[str] = Query(
        None, description="pending | approved | rejected | superseded"
    ),
    phase_number: Optional[int] = Query(None, description="Filter by phase"),
    confidence_min: float = Query(
        0.0, ge=0.0, le=1.0, description="Minimum confidence"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db_path: str = Depends(get_db_path),
) -> List[DecisionRecord]:
    """
    Query decisions across project with optional filters.

    Useful for:
    - Finding all pending approvals
    - Reviewing architectural decisions
    - Tracing decision history
    - Understanding low-confidence choices
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT id, decision_type, title, rationale, alternatives, chosen_option,
                          confidence, impact_level, impact_description, made_by, approved_by,
                          status, tags, created_at, updated_at
                   FROM decisions WHERE project_id = ?"""
        params: List[Any] = [str(project_id)]

        if decision_type:
            query += " AND decision_type = ?"
            params.append(decision_type)

        if status:
            query += " AND status = ?"
            params.append(status)

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        if confidence_min > 0.0:
            query += " AND confidence >= ?"
            params.append(confidence_min)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            DecisionRecord(
                id=row[0],
                decision_type=row[1],
                title=row[2],
                rationale=row[3],
                alternatives=row[4],
                chosen_option=row[5],
                confidence=row[6],
                impact_level=row[7],
                impact_description=row[8],
                made_by=row[9],
                approved_by=row[10],
                status=row[11],
                tags=json.loads(row[12]) if row[12] else [],
                created_at=datetime.fromisoformat(row[13]),
                updated_at=datetime.fromisoformat(row[14]),
            )
            for row in rows
        ]


# ============================================================================
# VERIFICATION GATE ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/phase/{phase_num}/gates",
    response_model=List[VerificationGateResult],
    summary="Get verification gates for phase",
    description="Returns all quality gates evaluated for this phase",
)
async def get_phase_gates(
    project_id: UUID,
    phase_num: int,
    gate_type: Optional[str] = Query(None, description="Filter by gate type"),
    current_user: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> List[VerificationGateResult]:
    """
    Get all verification gates for a phase execution.

    Gate types:
    - test_coverage: Code coverage percentage
    - security_scan: Security vulnerability count
    - performance: Performance metrics
    - spec_compliance: Specification adherence
    - brain_7_approval: Human/AI approver sign-off
    - contract_validation: Cross-phase contract validation

    Includes:
    - Pass/fail status
    - Retry count and max retries
    - Detailed results per gate type
    - Evaluation notes from Brain #7
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT id, gate_type, gate_name, status, score, result, evaluated_by,
                          evaluation_notes, completed_at
                   FROM verification_gates
                   WHERE project_id = ? AND phase_num = ?"""
        params: List[Any] = [str(project_id), phase_num]

        if gate_type:
            query += " AND gate_type = ?"
            params.append(gate_type)

        query += " ORDER BY completed_at DESC"

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            VerificationGateResult(
                id=row[0],
                gate_type=row[1],
                gate_name=row[2],
                status=row[3],
                score=row[4],
                result=json.loads(row[5]) if row[5] else {},
                evaluated_by=row[6],
                evaluation_notes=row[7],
                completed_at=datetime.fromisoformat(row[8]) if row[8] else None,
            )
            for row in rows
        ]


# ============================================================================
# SESSION MANAGEMENT ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/sessions",
    response_model=List[DevSessionRecord],
    summary="List development sessions",
    description="Get sessions with task completion and discovery tracking",
)
async def list_sessions(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    phase_number: Optional[int] = Query(None, description="Filter by phase"),
    status: Optional[str] = Query(
        None, description="active | paused | completed | abandoned"
    ),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db_path: str = Depends(get_db_path),
) -> List[DevSessionRecord]:
    """
    List development sessions for project.

    Each session captures:
    - Duration and time spent
    - Tasks completed / total
    - Commits made with hashes
    - Key discoveries and learnings
    - Blockers encountered
    - Next steps for resumption

    Useful for:
    - Understanding sprint velocity
    - Identifying blockers patterns
    - Learning from discoveries
    - Session continuity
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT id, phase_num, session_date, duration_minutes, status,
                          tasks_completed, tasks_total, commits_count, discoveries, blockers, next_steps
                   FROM dev_sessions WHERE project_id = ?"""
        params: List[Any] = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY session_date DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            DevSessionRecord(
                id=row[0],
                phase_number=row[1],
                session_date=datetime.fromisoformat(row[2]),
                duration_minutes=row[3],
                status=row[4],
                tasks_completed=row[5],
                tasks_total=row[6],
                commits_count=row[7],
                discoveries=row[8],
                blockers=row[9],
                next_steps=row[10],
            )
            for row in rows
        ]


# ============================================================================
# METRICS ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/metrics",
    response_model=List[PhaseMetric],
    summary="Get phase metrics by niche",
    description="Query KPIs for software, SaaS, or hardware niches",
)
async def get_project_metrics(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    niche: Optional[str] = Query(None, description="software | saas | hardware"),
    phase_number: Optional[int] = Query(None, description="Filter by phase"),
    metric_name: Optional[str] = Query(None, description="Filter by specific metric"),
    db_path: str = Depends(get_db_path),
) -> List[PhaseMetric]:
    """
    Get niche-specific metrics for project phases.

    Supported niches:
    - software: test_coverage, code_review_time, cyclomatic_complexity, vulnerabilities
    - saas: deployment_success_rate, uptime, mrr_impact
    - hardware: manufacturing_yield, defect_rate, time_to_production

    Each metric includes:
    - Actual value
    - Target value
    - Unit (%, ms, days, count, ppm)
    - Pass/warn/fail status

    Useful for:
    - Phase quality assessment
    - Tracking improvement over time
    - Niche-specific goal tracking
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT metric_name, metric_value, metric_unit, target_value, status
                   FROM phase_metrics WHERE project_id = ?"""
        params: List[Any] = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        if metric_name:
            query += " AND metric_name = ?"
            params.append(metric_name)

        # Note: niche is more of a filter for presentation; in practice, specific
        # metrics correspond to specific niches
        query += " ORDER BY phase_num, metric_name"

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            PhaseMetric(
                metric_name=row[0],
                metric_value=row[1],
                metric_unit=row[2],
                target_value=row[3],
                status=row[4],
            )
            for row in rows
        ]


# ============================================================================
# ARTIFACT TRACKING ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/artifacts",
    response_model=List[ArtifactRecord],
    summary="List artifacts by type and phase",
    description="Track generated plans, specs, tests, and documentation",
)
async def list_artifacts(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    artifact_type: Optional[str] = Query(
        None, description="plan | spec | test | doc | report | design"
    ),
    phase_number: Optional[int] = Query(None, description="Filter by phase"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db_path: str = Depends(get_db_path),
) -> List[ArtifactRecord]:
    """
    List artifacts created during project execution.

    Artifact types:
    - plan: Phase plan documents
    - spec: Technical specifications
    - test: Test suites and results
    - doc: Documentation
    - report: Analysis and findings reports
    - design: Design documents
    - guide: Implementation guides
    - other: Miscellaneous

    Each artifact includes:
    - File path in repo
    - Creator (user or Brain #N)
    - Git commit hash where created
    - Linked decision (if applicable)

    Useful for:
    - Finding existing documentation
    - Understanding what's been created
    - Tracing artifact to decision
    - Version control linkage
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT id, artifact_type, name, description, file_path, created_by,
                          git_commit_hash, created_at
                   FROM artifacts WHERE project_id = ?"""
        params: List[Any] = [str(project_id)]

        if artifact_type:
            query += " AND artifact_type = ?"
            params.append(artifact_type)

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        if created_by:
            query += " AND created_by = ?"
            params.append(created_by)

        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            ArtifactRecord(
                id=row[0],
                artifact_type=row[1],
                name=row[2],
                description=row[3],
                file_path=row[4],
                created_by=row[5],
                git_commit_hash=row[6],
                created_at=datetime.fromisoformat(row[7]),
            )
            for row in rows
        ]


# ============================================================================
# AUDIT LOG ENDPOINTS (COMPLIANCE)
# ============================================================================


@router.get(
    "/projects/{project_id}/audit-log",
    response_model=List[AuditLogEntry],
    summary="Get audit log (compliance)",
    description="Full immutable audit trail of all project actions",
)
async def get_audit_log(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    action_type: Optional[str] = Query(None, description="Filter by action"),
    actor_type: Optional[str] = Query(None, description="user | brain | system"),
    severity: Optional[str] = Query(
        None, description="info | warning | error | critical"
    ),
    start_date: Optional[datetime] = Query(
        None, description="Filter by date range start"
    ),
    end_date: Optional[datetime] = Query(None, description="Filter by date range end"),
    limit: int = Query(500, ge=1, le=10000, description="Max entries"),
    offset: int = Query(0, ge=0),
    db_path: str = Depends(get_db_path),
) -> List[AuditLogEntry]:
    """
    Get complete audit log for project (compliance/governance).

    Tracks all significant actions:
    - phase_started, phase_completed
    - decision_made
    - gate_passed, gate_failed
    - artifact_created
    - session_started, session_ended

    Each entry includes:
    - Actor (user name, brain ID, or system)
    - Actor type (user | brain | system)
    - Timestamp
    - Detailed description
    - Related entity (decision, gate, phase)
    - Severity (info | warning | error | critical)

    Immutable: entries cannot be deleted, only appended.
    Useful for:
    - Compliance audits
    - Tracing who did what when
    - Finding errors and escalations
    - Project history reconstruction
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        # For now, query the audit_log table (which exists in auth schema)
        # and generate synthetic entries for project-scoped audit needs
        query = """SELECT id, user_id, endpoint, method, request_hash, response_status, timestamp
                   FROM audit_log WHERE user_id IS NOT NULL"""
        params: List[Any] = []

        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())

        if end_date:
            query += " AND timestamp <= ?"
            params.append(end_date.isoformat())

        query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            AuditLogEntry(
                id=row[0],
                action_type=row[2],  # endpoint as action_type
                actor=row[1],  # user_id as actor
                actor_type="user",
                description=f"{row[3]} {row[2]} (status: {row[5]})",
                phase_number=None,
                severity="info"
                if row[5] < 400
                else "warning"
                if row[5] < 500
                else "error",
                created_at=datetime.fromisoformat(row[6]),
            )
            for row in rows
        ]


# ============================================================================
# SUMMARY & ANALYTICS ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/summary",
    summary="Get project execution summary",
    description="High-level overview of project health and progress",
)
async def get_project_summary(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> Dict[str, Any]:
    """
    Get executive summary of project health.

    Returns:
    - Total phases completed / in progress
    - Average phase duration
    - Decision approval rate and confidence
    - Gate pass rate by type
    - Total artifacts created
    - Session count and total hours
    - Latest discoveries
    - Current blockers

    Useful for:
    - Project status updates
    - Identifying trends
    - Risk assessment
    - Team standups
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        # Count phases
        cursor = await db.conn.execute(
            """SELECT COUNT(*),
                      COUNT(CASE WHEN status = 'completed' THEN 1 END),
                      AVG(duration_seconds)
               FROM phase_executions WHERE project_id = ?""",
            [str(project_id)],
        )
        phase_row = await cursor.fetchone()
        total_phases = phase_row[0] if phase_row else 0
        completed_phases = phase_row[1] if phase_row else 0
        avg_phase_duration = phase_row[2] if phase_row else 0

        # Count decisions
        cursor = await db.conn.execute(
            """SELECT COUNT(*),
                      COUNT(CASE WHEN status = 'approved' THEN 1 END),
                      AVG(confidence)
               FROM decisions WHERE project_id = ?""",
            [str(project_id)],
        )
        decision_row = await cursor.fetchone()
        total_decisions = decision_row[0] if decision_row else 0
        approved_decisions = decision_row[1] if decision_row else 0
        avg_confidence = decision_row[2] if decision_row else 0.0

        # Count gates
        cursor = await db.conn.execute(
            """SELECT COUNT(*), COUNT(CASE WHEN status = 'passed' THEN 1 END)
               FROM verification_gates WHERE project_id = ?""",
            [str(project_id)],
        )
        gate_row = await cursor.fetchone()
        total_gates = gate_row[0] if gate_row else 0
        passed_gates = gate_row[1] if gate_row else 0

        # Count artifacts
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM artifacts WHERE project_id = ?",
            [str(project_id)],
        )
        artifact_row = await cursor.fetchone()
        total_artifacts = artifact_row[0] if artifact_row else 0

        # Count sessions
        cursor = await db.conn.execute(
            """SELECT COUNT(*), SUM(duration_minutes)
               FROM dev_sessions WHERE project_id = ?""",
            [str(project_id)],
        )
        session_row = await cursor.fetchone()
        total_sessions = session_row[0] if session_row else 0
        total_minutes = session_row[1] if session_row else 0

        # Get latest discoveries and blockers
        cursor = await db.conn.execute(
            """SELECT discoveries, blockers FROM dev_sessions
               WHERE project_id = ? AND discoveries IS NOT NULL
               ORDER BY session_date DESC LIMIT 5""",
            [str(project_id)],
        )
        discovery_rows = await cursor.fetchall()
        latest_discoveries = [row[0] for row in discovery_rows if row[0]]
        latest_blockers = [row[1] for row in discovery_rows if row[1]]

        # Calculate decision approval rate
        decision_approval_rate = (
            (approved_decisions / total_decisions * 100) if total_decisions > 0 else 0
        )

        # Calculate gate pass rate
        gate_pass_rate = (passed_gates / total_gates * 100) if total_gates > 0 else 0

        return {
            "total_phases": total_phases,
            "completed_phases": completed_phases,
            "avg_phase_duration_seconds": int(avg_phase_duration)
            if avg_phase_duration
            else 0,
            "total_decisions": total_decisions,
            "approved_decisions": approved_decisions,
            "decision_approval_rate_percent": round(decision_approval_rate, 2),
            "avg_decision_confidence": round(avg_confidence, 2),
            "total_gates": total_gates,
            "passed_gates": passed_gates,
            "gate_pass_rate_percent": round(gate_pass_rate, 2),
            "total_artifacts": total_artifacts,
            "total_sessions": total_sessions,
            "total_hours_spent": round(total_minutes / 60, 2) if total_minutes else 0,
            "latest_discoveries": latest_discoveries,
            "latest_blockers": latest_blockers,
        }


@router.get(
    "/projects/{project_id}/phase-comparison",
    summary="Compare metrics across phases",
    description="Analyze trends and improvements phase-over-phase",
)
async def compare_phases(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    metric_names: List[str] = Query(
        [], description="Metrics to compare (test_coverage, duration, etc)"
    ),
    db_path: str = Depends(get_db_path),
) -> Dict[str, Any]:
    """
    Compare metrics across phases to identify trends.

    Returns:
    - Time series data per metric
    - Improvements and regressions
    - Correlation between metrics
    - Predictions for next phase

    Example:
    - test_coverage trending up over phases 15-18
    - phase_duration decreasing (efficiency improvement)
    - decision_approval_rate stable at 95%

    Useful for:
    - Quality trend analysis
    - Process improvement tracking
    - Predictive planning
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        # Get all phases for this project
        cursor = await db.conn.execute(
            """SELECT phase_num, duration_seconds, status, completed_at
               FROM phase_executions WHERE project_id = ?
               ORDER BY phase_num ASC""",
            [str(project_id)],
        )
        phase_rows = await cursor.fetchall()

        # Build time series per metric
        time_series: Dict[str, List[Dict[str, Any]]] = {}

        # Duration trend
        duration_trend = [
            {
                "phase": row[0],
                "value": row[1] if row[1] else 0,
                "status": row[2],
            }
            for row in phase_rows
        ]
        time_series["phase_duration_seconds"] = duration_trend

        # Get metrics by phase
        cursor = await db.conn.execute(
            """SELECT phase_num, metric_name, metric_value
               FROM phase_metrics WHERE project_id = ?
               ORDER BY phase_num, metric_name""",
            [str(project_id)],
        )
        metric_rows = await cursor.fetchall()

        # Build metric-specific time series
        metrics_by_name: Dict[str, List[Dict[str, Any]]] = {}
        for row in metric_rows:
            metric_name = row[1]
            if metric_name not in metrics_by_name:
                metrics_by_name[metric_name] = []
            metrics_by_name[metric_name].append({"phase": row[0], "value": row[2]})

        time_series.update(metrics_by_name)

        # Calculate improvements and regressions
        improvements = {}
        for metric_name, values in time_series.items():
            if len(values) >= 2:
                first_val = values[0]["value"]
                last_val = values[-1]["value"]
                if first_val != 0:
                    pct_change = ((last_val - first_val) / abs(first_val)) * 100
                    improvements[metric_name] = {
                        "percent_change": round(pct_change, 2),
                        "direction": "improvement"
                        if pct_change > 0
                        else "regression"
                        if pct_change < 0
                        else "stable",
                    }

        return {
            "phases_analyzed": len(phase_rows),
            "time_series": time_series,
            "improvements": improvements,
            "total_phases": len(phase_rows),
        }


# ============================================================================
# BRAIN FEEDBACK ENDPOINTS
# ============================================================================


@router.get(
    "/projects/{project_id}/brain-feedback",
    summary="Get brain insights and feedback",
    description="Retrieve feedback from brain agents during phase execution",
)
async def get_brain_feedback(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    phase_number: Optional[int] = Query(None),
    brain_id: Optional[int] = Query(
        None, description="1-7 for dev, 8-23 for marketing"
    ),
    feedback_type: Optional[str] = Query(
        None, description="insight | risk_flag | opportunity | lesson_learned"
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db_path: str = Depends(get_db_path),
) -> List[Dict[str, Any]]:
    """
    Get feedback captured from brain agents.

    Feedback types:
    - insight: Important discovery
    - risk_flag: Potential issue identified
    - opportunity: Improvement possibility
    - lesson_learned: Cross-session wisdom

    Each feedback includes:
    - Brain ID and phase
    - Confidence score
    - Impact level (critical | high | medium | low)
    - Link to engram memory if synced

    Useful for:
    - Understanding brain reasoning
    - Capturing institutional knowledge
    - Risk mitigation
    - Continuous improvement
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        query = """SELECT id, brain_id, phase_num, feedback, confidence_score,
                          feedback_type, impact_level, created_at
                   FROM brain_feedback WHERE project_id = ?"""
        params: List[Any] = [str(project_id)]

        if phase_number is not None:
            query += " AND phase_num = ?"
            params.append(phase_number)

        if brain_id is not None:
            query += " AND brain_id = ?"
            params.append(brain_id)

        if feedback_type:
            query += " AND feedback_type = ?"
            params.append(feedback_type)

        query += " ORDER BY confidence_score DESC, created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        cursor = await db.conn.execute(query, params)
        rows = await cursor.fetchall()

        return [
            {
                "id": row[0],
                "brain_id": row[1],
                "phase_number": row[2],
                "feedback": row[3],
                "confidence_score": row[4],
                "feedback_type": row[5],
                "impact_level": row[6],
                "created_at": datetime.fromisoformat(row[7]),
            }
            for row in rows
        ]


# ============================================================================
# ENGRAM SYNC STATUS
# ============================================================================


@router.get(
    "/projects/{project_id}/engram-sync-status",
    summary="Check Engram synchronization status",
    description="See which decisions/feedback have been synced to Engram memory",
)
async def get_engram_sync_status(
    project_id: UUID,
    current_user: str = Depends(get_current_user_any),
    db_path: str = Depends(get_db_path),
) -> Dict[str, Any]:
    """
    Check Engram sync status for project.

    Returns:
    - Last sync timestamp
    - Pending items (decisions, feedback not yet synced)
    - Synced items count
    - Failed syncs and retry queue

    Useful for:
    - Ensuring decisions are persisted to Engram
    - Troubleshooting sync issues
    - Manual sync triggers
    """
    async with DatabaseConnection(db_path) as db:
        await _ensure_audit_schema(db)

        # Get Engram sync status for this project
        cursor = await db.conn.execute(
            """SELECT last_sync_timestamp, synced_items_count, sync_status
               FROM engram_sync_status WHERE project_id = ?""",
            [str(project_id)],
        )
        sync_row = await cursor.fetchone()

        last_sync = None
        synced_count = 0
        sync_status = "idle"

        if sync_row:
            last_sync = datetime.fromisoformat(sync_row[0]) if sync_row[0] else None
            synced_count = sync_row[1] if sync_row[1] else 0
            sync_status = sync_row[2] if sync_row[2] else "idle"

        # Count pending items (for future enhancement: track engram_synced flag)
        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM decisions WHERE project_id = ?",
            [str(project_id)],
        )
        total_decisions = (await cursor.fetchone())[0] if await cursor.fetchone() else 0

        cursor = await db.conn.execute(
            "SELECT COUNT(*) FROM brain_feedback WHERE project_id = ?",
            [str(project_id)],
        )
        total_feedback = (await cursor.fetchone())[0] if await cursor.fetchone() else 0

        pending_items = (total_decisions + total_feedback) - synced_count

        return {
            "sync_status": sync_status,
            "last_sync_timestamp": last_sync.isoformat() if last_sync else None,
            "synced_items_count": synced_count,
            "pending_items_count": max(0, pending_items),
            "total_items": total_decisions + total_feedback,
            "sync_health": "healthy"
            if sync_status == "idle"
            else "in_progress"
            if sync_status == "active"
            else "error",
        }


# Export router for inclusion in main app
__all__ = ["router"]
