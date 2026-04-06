"""
Analytics service for dashboard metrics.

Calculates system health and outcome metrics for monitoring brain learning progress.
"""

from typing import List, Dict, Any, Optional

from pydantic import BaseModel

from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection


class SystemHealthMetrics(BaseModel):
    """System health metrics for dashboard monitoring."""

    record_count: int  # Total non-expired records
    avg_quality_score: float  # Avg quality_score across all records
    rejection_rate: float  # % of records with status='rejected'
    p50_latency_ms: float  # Median retrieval latency
    p90_latency_ms: float  # P90 retrieval latency
    t1_trend: List[Dict[str, Any]]  # T1 over time (last 7 days)


class OutcomeMetrics(BaseModel):
    """Outcome metrics for learning validation."""

    delta_velocity: float  # T1(first) - T1(second) improvement
    knowledge_yield: float  # Template reuse rate (templates_created / total_records)
    planning_accuracy: float  # Avg quality_score across all records


class AnalyticsService:
    """Analytics service for dashboard metrics."""

    def __init__(self, db: DatabaseConnection):
        self.db = db
        self.logger = ExperienceLogger(db)

    async def get_system_health(self) -> SystemHealthMetrics:
        """Calculate system health metrics.

        Monitors:
        - Record count (unbounded growth detection)
        - Quality drift (avg quality_score trend)
        - Brain degradation (rejection rate)
        - Retrieval latency (P50/P90, ceiling detection)
        - T1 trend (learning validation)
        """
        # Record count (non-expired only)
        cursor = await self.db.conn.execute(
            """SELECT COUNT(*) FROM experience_records
               WHERE expires_at IS NULL OR expires_at > datetime('now')"""
        )
        row = await cursor.fetchone()
        record_count = row[0] if row else 0

        # Avg quality_score
        cursor = await self.db.conn.execute(
            """SELECT AVG(json_extract(custom_metadata, '$.quality_score'))
               FROM experience_records
               WHERE custom_metadata IS NOT NULL
                 AND json_extract(custom_metadata, '$.quality_score') IS NOT NULL
                 AND (expires_at IS NULL OR expires_at > datetime('now'))"""
        )
        row = await cursor.fetchone()
        avg_quality_score = row[0] if row and row[0] is not None else 0.0

        # Rejection rate
        cursor = await self.db.conn.execute(
            """SELECT
                 COUNT(*) FILTER (WHERE status = 'rejected') * 1.0 / COUNT(*) as rejection_rate
               FROM experience_records
               WHERE expires_at IS NULL OR expires_at > datetime('now')"""
        )
        row = await cursor.fetchone()
        rejection_rate = row[0] if row and row[0] is not None else 0.0

        # P50/P90 latency (from duration_ms)
        # SQLite doesn't have percentile() function — fetch all, calculate in Python
        cursor = await self.db.conn.execute(
            """SELECT duration_ms
               FROM experience_records
               WHERE duration_ms IS NOT NULL
                 AND (expires_at IS NULL OR expires_at > datetime('now'))
               ORDER BY duration_ms"""
        )
        duration_rows = await cursor.fetchall()
        durations = [row[0] for row in duration_rows if row[0] is not None]

        # Calculate percentiles in Python (simple approach for v1)
        if durations:
            p50_idx = int(len(durations) * 0.5)
            p90_idx = int(len(durations) * 0.9)
            p50_latency_ms = durations[p50_idx]
            p90_latency_ms = durations[p90_idx]
        else:
            p50_latency_ms = 0.0
            p90_latency_ms = 0.0

        # T1 trend (last 7 days)
        cursor = await self.db.conn.execute(
            """SELECT
                 date(timestamp) as day,
                 AVG(duration_ms) as avg_t1_ms
               FROM experience_records
               WHERE duration_ms IS NOT NULL
                 AND (expires_at IS NULL OR expires_at > datetime('now'))
                 AND timestamp >= datetime('now', '-7 days')
               GROUP BY day
               ORDER BY day DESC"""
        )
        t1_trend_rows = await cursor.fetchall()
        t1_trend = [{"day": row[0], "avg_t1_ms": row[1]} for row in t1_trend_rows]

        return SystemHealthMetrics(
            record_count=record_count,
            avg_quality_score=round(avg_quality_score, 2),
            rejection_rate=round(rejection_rate, 3),
            p50_latency_ms=round(p50_latency_ms, 2),
            p90_latency_ms=round(p90_latency_ms, 2),
            t1_trend=t1_trend,
        )

    async def get_templates(
        self,
        brain_id: Optional[str] = None,
        limit: int = 20,
        min_success_rate: float = 0.5,
    ) -> List[Dict[str, Any]]:
        """Retrieve templates with success rate tracking.

        Args:
            brain_id: Filter by brain (optional)
            limit: Max templates to return
            min_success_rate: Minimum success rate threshold
        """
        if brain_id:
            cursor = await self.db.conn.execute(
                """SELECT * FROM knowledge_templates
                   WHERE brain_id = ?
                     AND success_rate >= ?
                   ORDER BY success_rate DESC, usage_count DESC
                   LIMIT ?""",
                (brain_id, min_success_rate, limit),
            )
        else:
            cursor = await self.db.conn.execute(
                """SELECT * FROM knowledge_templates
                   WHERE success_rate >= ?
                   ORDER BY success_rate DESC, usage_count DESC
                   LIMIT ?""",
                (min_success_rate, limit),
            )

        rows = await cursor.fetchall()

        templates = []
        for row in rows:
            templates.append(
                {
                    "id": row[0],
                    "brain_id": row[1],
                    "template_name": row[2],
                    "success_rate": row[4],
                    "usage_count": row[5],
                    "created_at": row[6],
                    "last_used_at": row[7],
                }
            )

        return templates

    async def get_patterns(
        self,
        brain_id: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Extract recurring patterns per brain.

        Groups experience_records by brain_id + brief similarity (input_hash).
        Shows which brief patterns recur most frequently.
        """
        if brain_id:
            cursor = await self.db.conn.execute(
                """SELECT
                     brain_id,
                     input_hash,
                     COUNT(*) as frequency,
                     AVG(json_extract(custom_metadata, '$.quality_score')) as avg_quality
                   FROM experience_records
                   WHERE brain_id = ?
                     AND (expires_at IS NULL OR expires_at > datetime('now'))
                   GROUP BY brain_id, input_hash
                   ORDER BY frequency DESC
                   LIMIT ?""",
                (brain_id, limit),
            )
        else:
            cursor = await self.db.conn.execute(
                """SELECT
                     brain_id,
                     input_hash,
                     COUNT(*) as frequency,
                     AVG(json_extract(custom_metadata, '$.quality_score')) as avg_quality
                   FROM experience_records
                   WHERE expires_at IS NULL OR expires_at > datetime('now')
                   GROUP BY brain_id, input_hash
                   ORDER BY frequency DESC
                   LIMIT ?""",
                (limit,),
            )

        rows = await cursor.fetchall()

        patterns: Dict[str, List[Dict[str, Any]]] = {}
        for row in rows:
            brain = row[0]
            if brain not in patterns:
                patterns[brain] = []

            patterns[brain].append(
                {
                    "input_hash": row[1],
                    "frequency": row[2],
                    "avg_quality": round(row[3], 2) if row[3] is not None else 0.0,
                }
            )

        return patterns

    async def get_outcome_metrics(self) -> OutcomeMetrics:
        """Calculate outcome metrics for learning validation.

        Returns:
            - delta_velocity: T1 improvement (first consultation - second consultation)
            - knowledge_yield: Template reuse rate (templates / total_records)
            - planning_accuracy: Avg quality_score across all records
        """
        # Delta-velocity: Compare T1 of first vs second consultation (simplified)
        # For now: Use avg duration_ms as proxy (real delta-velocity requires session grouping)
        cursor = await self.db.conn.execute(
            """SELECT AVG(duration_ms) FROM experience_records
               WHERE duration_ms IS NOT NULL
                 AND (expires_at IS NULL OR expires_at > datetime('now'))"""
        )
        row = await cursor.fetchone()
        avg_t1_ms = row[0] if row and row[0] is not None else 0.0
        delta_velocity = (
            avg_t1_ms  # Placeholder: Real delta-velocity = T1(first) - T1(second)
        )

        # Knowledge yield: Template reuse rate
        cursor = await self.db.conn.execute(
            """SELECT
                 (SELECT COUNT(*) FROM knowledge_templates) * 1.0 /
                 (SELECT COUNT(*) FROM experience_records
                  WHERE expires_at IS NULL OR expires_at > datetime('now')) as yield"""
        )
        row = await cursor.fetchone()
        knowledge_yield = row[0] if row and row[0] is not None else 0.0

        # Planning accuracy: Avg quality_score
        cursor = await self.db.conn.execute(
            """SELECT AVG(json_extract(custom_metadata, '$.quality_score'))
               FROM experience_records
               WHERE custom_metadata IS NOT NULL
                 AND (expires_at IS NULL OR expires_at > datetime('now'))"""
        )
        row = await cursor.fetchone()
        planning_accuracy = row[0] if row and row[0] is not None else 0.0

        return OutcomeMetrics(
            delta_velocity=round(delta_velocity, 2),
            knowledge_yield=round(knowledge_yield, 3),
            planning_accuracy=round(planning_accuracy, 2),
        )
