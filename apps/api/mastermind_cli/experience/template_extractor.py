"""Template extraction service for reusable patterns from high-quality experience records.

Plan 14-03: Template storage + extraction system for reusable patterns.
"""

from typing import Optional, Dict, Any
from mastermind_cli.experience.models import ExperienceRecord
from mastermind_cli.experience.logger import ExperienceLogger
import uuid
import json
from datetime import datetime


class TemplateExtractor:
    """Extract reusable templates from high-quality experience records.

    A template = brief_pattern → response_pattern mapping that can be reused
    for similar future briefs. Only records with quality_score >= 3.0 are
    considered template candidates.
    """

    MIN_QUALITY_SCORE = 3.0

    def __init__(self, logger: ExperienceLogger):
        self.logger = logger

    async def extract_and_store_template(
        self,
        record: ExperienceRecord,
    ) -> Optional[str]:
        """Extract template from high-quality record and store in knowledge_templates.

        Args:
            record: Experience record with quality_score >= 3.0 (or >= 2.0 in cold start mode)

        Returns:
            Template ID if extracted, None if quality too low
        """
        # Check quality score threshold
        quality_score = (
            record.custom_metadata.get("quality_score", 0.0)
            if record.custom_metadata
            else 0.0
        )

        # Cold start fallback: if zero templates exist, lower threshold to 2.0
        threshold = self.MIN_QUALITY_SCORE
        if quality_score < threshold:
            # Check if we're in cold start (zero templates)
            cursor = await self.logger.db.conn.execute(
                "SELECT COUNT(*) FROM knowledge_templates"
            )
            row = await cursor.fetchone()
            template_count = row[0] if row else 0

            if template_count == 0 and quality_score >= 2.0:
                # Cold start mode: accept lower quality to bootstrap
                import warnings

                warnings.warn(
                    f"Cold start: extracting template with quality_score={quality_score} (threshold lowered to 2.0)"
                )
            else:
                return None

        # Extract template data
        template_data = self._extract_template_data(record)
        template_name = self._generate_template_name(record)

        # Store template
        template_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        await self.logger.db.conn.execute(
            """INSERT INTO knowledge_templates
               (id, brain_id, template_name, template_data, success_rate, usage_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                template_id,
                record.brain_id,
                template_name,
                json.dumps(template_data),
                1.0,  # New templates start with 100% success rate
                0,  # Never used
                created_at,
            ),
        )
        await self.logger.db.conn.commit()

        return template_id

    def _extract_template_data(self, record: ExperienceRecord) -> Dict[str, Any]:
        """Extract template pattern from record.

        Template data = {
            "brief_pattern": "hashed or simplified input",
            "response_pattern": "structured output (sections, bullets, etc.)",
            "metadata": {...}
        }
        """
        # For now: Store full output_json as response_pattern
        # Future: Use pgvector embeddings for semantic clustering (Phase 15)

        return {
            "brief_pattern": record.input_hash,  # Hashed input for privacy
            "response_pattern": record.output_json,  # Full output structure
            "metadata": {
                "source_record_id": record.id,
                "original_quality_score": (
                    record.custom_metadata.get("quality_score")
                    if record.custom_metadata
                    else None
                ),
                "duration_ms": record.duration_ms,
                "status": record.status,
            },
        }

    def _generate_template_name(self, record: ExperienceRecord) -> str:
        """Auto-generate template name from brain_id + brief summary."""
        # Extract brief summary from output_json if available
        brief_summary = (
            record.output_json.get("summary", "untitled")
            if isinstance(record.output_json, dict)
            else "untitled"
        )

        # Truncate to 50 chars
        brief_summary = brief_summary[:50] if len(brief_summary) > 50 else brief_summary

        return f"{record.brain_id}: {brief_summary}"

    async def get_templates_for_brain(
        self,
        brain_id: str,
        limit: int = 10,
        min_success_rate: float = 0.5,
    ) -> list[Dict[str, Any]]:
        """Retrieve best templates for a brain.

        Returns templates ordered by success_rate DESC (best first).
        """
        cursor = await self.logger.db.conn.execute(
            """SELECT * FROM knowledge_templates
               WHERE brain_id = ?
                 AND success_rate >= ?
               ORDER BY success_rate DESC, usage_count DESC
               LIMIT ?""",
            (brain_id, min_success_rate, limit),
        )
        rows = await cursor.fetchall()

        templates = []
        for row in rows:
            templates.append(
                {
                    "id": row[0],
                    "brain_id": row[1],
                    "template_name": row[2],
                    "template_data": json.loads(row[3]),
                    "success_rate": row[4],
                    "usage_count": row[5],
                    "created_at": row[6],
                    "last_used_at": row[7],
                }
            )

        return templates
