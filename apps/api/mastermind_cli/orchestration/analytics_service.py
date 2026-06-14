"""
Analytics service for dashboard metrics.

Calculates system health and outcome metrics for monitoring brain learning progress.
"""

from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
import json
from typing import Any, Dict, List, Optional

from pydantic import BaseModel

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


@dataclass(frozen=True)
class _ExperienceRecord:
    """Minimal analytics projection for an experience record."""

    brain_id: str
    input_hash: str
    timestamp: str
    duration_ms: Optional[int]
    status: str
    quality_score: Optional[float]


class AnalyticsService:
    """Analytics service for dashboard metrics."""

    def __init__(self, db: DatabaseConnection):
        self.db = db

    async def get_system_health(self) -> SystemHealthMetrics:
        """Calculate system health metrics.

        Monitors:
        - Record count (unbounded growth detection)
        - Quality drift (avg quality_score trend)
        - Brain degradation (rejection rate)
        - Retrieval latency (P50/P90, ceiling detection)
        - T1 trend (learning validation)
        """
        records = await self._get_active_records()
        record_count = len(records)

        quality_scores = [
            record.quality_score
            for record in records
            if record.quality_score is not None
        ]
        avg_quality_score = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )

        rejected_count = sum(1 for record in records if record.status == "rejected")
        rejection_rate = rejected_count / record_count if record_count else 0.0

        durations = sorted(
            record.duration_ms for record in records if record.duration_ms is not None
        )
        p50_latency_ms = self._percentile_value(durations, 0.5)
        p90_latency_ms = self._percentile_value(durations, 0.9)

        t1_trend = self._build_t1_trend(records)

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
        records = await self._get_active_records(brain_id=brain_id)
        grouped: Dict[tuple[str, str], List[_ExperienceRecord]] = defaultdict(list)
        for record in records:
            grouped[(record.brain_id, record.input_hash)].append(record)

        ranked_groups = sorted(
            grouped.items(),
            key=lambda item: len(item[1]),
            reverse=True,
        )[:limit]

        patterns: Dict[str, List[Dict[str, Any]]] = {}
        for (brain, input_hash), group_records in ranked_groups:
            if brain not in patterns:
                patterns[brain] = []

            quality_scores = [
                record.quality_score
                for record in group_records
                if record.quality_score is not None
            ]
            avg_quality = (
                sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
            )

            patterns[brain].append(
                {
                    "input_hash": input_hash,
                    "frequency": len(group_records),
                    "avg_quality": round(avg_quality, 2),
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
        records = await self._get_active_records()

        # Delta-velocity: Compare T1 of first vs second consultation (simplified)
        # For now: Use avg duration_ms as proxy (real delta-velocity requires session grouping)
        durations = [
            record.duration_ms for record in records if record.duration_ms is not None
        ]
        avg_t1_ms = sum(durations) / len(durations) if durations else 0.0
        delta_velocity = (
            avg_t1_ms  # Placeholder: Real delta-velocity = T1(first) - T1(second)
        )

        # Knowledge yield: Template reuse rate
        cursor = await self.db.conn.execute("SELECT COUNT(*) FROM knowledge_templates")
        row = await cursor.fetchone()
        template_count = row[0] if row and row[0] is not None else 0
        knowledge_yield = template_count / len(records) if records else 0.0

        # Planning accuracy: Avg quality_score
        quality_scores = [
            record.quality_score
            for record in records
            if record.quality_score is not None
        ]
        planning_accuracy = (
            sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        )

        return OutcomeMetrics(
            delta_velocity=round(delta_velocity, 2),
            knowledge_yield=round(knowledge_yield, 3),
            planning_accuracy=round(planning_accuracy, 2),
        )

    async def _get_active_records(
        self, brain_id: Optional[str] = None
    ) -> List[_ExperienceRecord]:
        if brain_id:
            cursor = await self.db.conn.execute(
                """SELECT brain_id, input_hash, timestamp, duration_ms, status, custom_metadata, expires_at
                   FROM experience_records
                   WHERE brain_id = ?""",
                (brain_id,),
            )
        else:
            cursor = await self.db.conn.execute(
                """SELECT brain_id, input_hash, timestamp, duration_ms, status, custom_metadata, expires_at
                   FROM experience_records"""
            )

        rows = await cursor.fetchall()
        records: List[_ExperienceRecord] = []
        for row in rows:
            if not self._is_active(row[6]):
                continue
            records.append(
                _ExperienceRecord(
                    brain_id=row[0],
                    input_hash=row[1],
                    timestamp=row[2],
                    duration_ms=row[3],
                    status=row[4],
                    quality_score=self._extract_quality_score(row[5]),
                )
            )
        return records

    @staticmethod
    def _extract_quality_score(custom_metadata: Any) -> Optional[float]:
        if not custom_metadata:
            return None
        if isinstance(custom_metadata, dict):
            value = custom_metadata.get("quality_score")
        else:
            try:
                value = json.loads(custom_metadata).get("quality_score")
            except (TypeError, ValueError, json.JSONDecodeError):
                return None
        if value is None:
            return None
        try:
            return float(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _is_active(expires_at: Any) -> bool:
        if not expires_at:
            return True
        expires_at_dt = AnalyticsService._parse_timestamp(expires_at)
        if expires_at_dt is None:
            return True
        return expires_at_dt > datetime.now(UTC)

    @staticmethod
    def _parse_timestamp(value: Any) -> Optional[datetime]:
        if not value or not isinstance(value, str):
            return None
        normalized = value.replace("Z", "+00:00")
        try:
            parsed = datetime.fromisoformat(normalized)
        except ValueError:
            return None
        if parsed.tzinfo is None:
            return parsed.replace(tzinfo=UTC)
        return parsed.astimezone(UTC)

    @staticmethod
    def _percentile_value(values: List[int], percentile: float) -> float:
        if not values:
            return 0.0
        index = int(len(values) * percentile)
        if index >= len(values):
            index = len(values) - 1
        return float(values[index])

    @staticmethod
    def _build_t1_trend(records: List[_ExperienceRecord]) -> List[Dict[str, Any]]:
        cutoff = datetime.now(UTC) - timedelta(days=7)
        trend_buckets: Dict[str, List[int]] = defaultdict(list)
        for record in records:
            if record.duration_ms is None:
                continue
            timestamp = AnalyticsService._parse_timestamp(record.timestamp)
            if timestamp is None or timestamp < cutoff:
                continue
            trend_buckets[timestamp.date().isoformat()].append(record.duration_ms)

        trend: List[Dict[str, Any]] = []
        for day in sorted(trend_buckets.keys(), reverse=True):
            durations = trend_buckets[day]
            trend.append({"day": day, "avg_t1_ms": sum(durations) / len(durations)})
        return trend
