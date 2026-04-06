"""Tests for knowledge_templates table and template extraction.

Plan 14-03: Template storage + extraction system for reusable patterns.
"""

import pytest
from datetime import datetime, timezone
from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.experience.models import ExperienceRecord
from mastermind_cli.state.database import DatabaseConnection


class TestKnowledgeTemplatesTable:
    """Test knowledge_templates table structure and constraints."""

    @pytest.mark.asyncio
    async def test_template_table_created(self):
        """Test 1: Migration creates knowledge_templates table with all required columns."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='knowledge_templates'"
        )
        result = await cursor.fetchone()
        assert result is not None, "knowledge_templates table should exist"

        # Verify columns exist
        cursor = await db.conn.execute("PRAGMA table_info(knowledge_templates)")
        columns = {row[1]: row[2] for row in await cursor.fetchall()}

        required_columns = {
            "id": "TEXT",
            "brain_id": "TEXT",
            "template_name": "TEXT",
            "template_data": "TEXT",
            "success_rate": "REAL",
            "usage_count": "INTEGER",
            "created_at": "TEXT",
            "last_used_at": "TEXT",
        }

        for col_name, col_type in required_columns.items():
            assert col_name in columns, f"Column {col_name} should exist"
            assert (
                columns[col_name] == col_type
            ), f"Column {col_name} should be {col_type}"

        await db.close()

    @pytest.mark.asyncio
    async def test_template_table_has_brain_id_index(self):
        """Test 2: Migration creates index on brain_id for fast retrieval."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_knowledge_templates_brain_id'"
        )
        result = await cursor.fetchone()
        assert result is not None, "Index idx_knowledge_templates_brain_id should exist"

        await db.close()

    @pytest.mark.asyncio
    async def test_template_table_has_success_rate_index(self):
        """Test 3: Migration creates index on success_rate DESC for ranking."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_knowledge_templates_success_rate'"
        )
        result = await cursor.fetchone()
        assert (
            result is not None
        ), "Index idx_knowledge_templates_success_rate should exist"

        await db.close()

    @pytest.mark.asyncio
    async def test_template_can_be_inserted_and_retrieved(self):
        """Test 4: Template can be inserted and retrieved successfully."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        # Insert a test template
        template_id = "test-template-001"
        brain_id = "brain-01-product"
        template_name = "Test Template"
        template_data = '{"brief_pattern": "test", "response_pattern": "test"}'
        success_rate = 1.0
        usage_count = 0
        created_at = datetime.now(timezone.utc).isoformat()

        await db.conn.execute(
            """INSERT INTO knowledge_templates
               (id, brain_id, template_name, template_data, success_rate, usage_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                template_id,
                brain_id,
                template_name,
                template_data,
                success_rate,
                usage_count,
                created_at,
            ),
        )
        await db.conn.commit()

        # Retrieve template
        cursor = await db.conn.execute(
            "SELECT * FROM knowledge_templates WHERE id = ?", (template_id,)
        )
        row = await cursor.fetchone()

        assert row is not None, "Template should be retrievable"
        assert row[0] == template_id, "Template ID should match"
        assert row[1] == brain_id, "Brain ID should match"
        assert row[2] == template_name, "Template name should match"
        assert row[4] == success_rate, "Success rate should match"
        assert row[5] == usage_count, "Usage count should match"

        await db.close()


class TestTemplateExtractor:
    """Test TemplateExtractor service for pattern extraction."""

    @pytest.mark.asyncio
    async def test_extractor_returns_none_for_low_quality(self):
        """Test 1: extract_template_from_record() returns None for quality_score < 3.0."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Insert a dummy template to avoid cold start mode
        await db.conn.execute(
            """INSERT INTO knowledge_templates
               (id, brain_id, template_name, template_data, success_rate, usage_count, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                "dummy-tmpl",
                "brain-01",
                "Dummy",
                "{}",
                1.0,
                0,
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        await db.conn.commit()

        # Create low-quality record (quality_score = 2.5)
        record = ExperienceRecord(
            id="rec-001",
            brain_id="brain-01-product",
            input_hash="abc123",
            output_json={"summary": "Low quality output"},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=1000,
            status="success",
            custom_metadata={"quality_score": 2.5},
        )

        result = await extractor.extract_and_store_template(record)
        assert result is None, "Should return None for quality_score < 3.0"

        await db.close()

    @pytest.mark.asyncio
    async def test_extractor_extracts_high_quality_template(self):
        """Test 2: extract_template_from_record() extracts template for quality_score >= 3.0."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Create high-quality record (quality_score = 3.5)
        record = ExperienceRecord(
            id="rec-002",
            brain_id="brain-01-product",
            input_hash="xyz789",
            output_json={"summary": "High quality output that should be templated"},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=2000,
            status="success",
            custom_metadata={"quality_score": 3.5},
        )

        template_id = await extractor.extract_and_store_template(record)
        assert (
            template_id is not None
        ), "Should extract template for quality_score >= 3.0"

        # Verify template was stored
        cursor = await db.conn.execute(
            "SELECT * FROM knowledge_templates WHERE id = ?", (template_id,)
        )
        row = await cursor.fetchone()
        assert row is not None, "Template should be stored in database"

        await db.close()

    @pytest.mark.asyncio
    async def test_extracted_template_contains_patterns(self):
        """Test 3: Extracted template contains brief_pattern and response_pattern."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor
        import json

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Create high-quality record
        record = ExperienceRecord(
            id="rec-003",
            brain_id="brain-01-product",
            input_hash="hash456",
            output_json={
                "summary": "Test pattern extraction",
                "sections": ["Section 1", "Section 2"],
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=3000,
            status="success",
            custom_metadata={"quality_score": 3.0},
        )

        template_id = await extractor.extract_and_store_template(record)

        # Retrieve template and verify structure
        cursor = await db.conn.execute(
            "SELECT template_data FROM knowledge_templates WHERE id = ?", (template_id,)
        )
        row = await cursor.fetchone()
        template_data = json.loads(row[0])

        assert "brief_pattern" in template_data, "Template should contain brief_pattern"
        assert (
            "response_pattern" in template_data
        ), "Template should contain response_pattern"
        assert (
            template_data["brief_pattern"] == "hash456"
        ), "Brief pattern should be input_hash"
        assert template_data["response_pattern"]["summary"] == "Test pattern extraction"

        await db.close()

    @pytest.mark.asyncio
    async def test_template_name_auto_generation(self):
        """Test 4: Template name is auto-generated from brain_id + brief_summary[:50]."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Create record with long summary
        record = ExperienceRecord(
            id="rec-004",
            brain_id="brain-01-product",
            input_hash="hash789",
            output_json={
                "summary": "This is a very long summary that should be truncated to exactly fifty characters max",
            },
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=4000,
            status="success",
            custom_metadata={"quality_score": 3.0},
        )

        template_id = await extractor.extract_and_store_template(record)

        # Verify template name format
        cursor = await db.conn.execute(
            "SELECT template_name FROM knowledge_templates WHERE id = ?", (template_id,)
        )
        row = await cursor.fetchone()
        template_name = row[0]

        assert template_name.startswith(
            "brain-01-product:"
        ), "Template name should start with brain_id"
        assert (
            len(template_name) <= len("brain-01-product: ") + 50
        ), "Template name should be truncated"

        await db.close()

    @pytest.mark.asyncio
    async def test_template_success_rate_initializes_to_1_0(self):
        """Test 5: Template success_rate initializes to 1.0 (100% for new templates)."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Create high-quality record
        record = ExperienceRecord(
            id="rec-005",
            brain_id="brain-01-product",
            input_hash="hash101",
            output_json={"summary": "New template"},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=5000,
            status="success",
            custom_metadata={"quality_score": 3.0},
        )

        template_id = await extractor.extract_and_store_template(record)

        # Verify success_rate = 1.0
        cursor = await db.conn.execute(
            "SELECT success_rate FROM knowledge_templates WHERE id = ?", (template_id,)
        )
        row = await cursor.fetchone()
        assert row[0] == 1.0, "New templates should start with success_rate = 1.0"

        await db.close()

    @pytest.mark.asyncio
    async def test_cold_start_fallback_quality_threshold(self):
        """Test 6: Cold start fallback — if zero templates exist after 50 sessions, threshold lowers to 2.0 with warning."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor
        import warnings

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Ensure no templates exist (cold start)
        await db.conn.execute("DELETE FROM knowledge_templates")
        await db.conn.commit()

        # Create medium-quality record (2.0 <= quality_score < 3.0)
        record = ExperienceRecord(
            id="rec-006",
            brain_id="brain-01-product",
            input_hash="hash202",
            output_json={"summary": "Cold start template"},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=6000,
            status="success",
            custom_metadata={"quality_score": 2.5},
        )

        # Should extract template with warning (cold start mode)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            template_id = await extractor.extract_and_store_template(record)

            # Verify warning was issued
            assert len(w) == 1, "Should issue warning about cold start"
            assert "Cold start" in str(
                w[0].message
            ), "Warning should mention cold start"

        assert template_id is not None, "Should extract template in cold start mode"

        await db.close()


class TestTemplateRetrieval:
    """Test template retrieval and ranking."""

    @pytest.mark.asyncio
    async def test_get_templates_for_brain_ordered_by_success_rate(self):
        """Test templates are ordered by success_rate DESC (best first)."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor

        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)
        extractor = TemplateExtractor(logger)

        # Insert 3 templates with different success rates
        templates = [
            ("tmpl-001", "brain-01-product", 0.8, "Template C"),
            ("tmpl-002", "brain-01-product", 1.0, "Template A"),
            ("tmpl-003", "brain-01-product", 0.9, "Template B"),
        ]

        for tmpl_id, brain_id, success_rate, name in templates:
            await db.conn.execute(
                """INSERT INTO knowledge_templates
                   (id, brain_id, template_name, template_data, success_rate, usage_count, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    tmpl_id,
                    brain_id,
                    name,
                    "{}",
                    success_rate,
                    0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
        await db.conn.commit()

        # Retrieve templates
        templates = await extractor.get_templates_for_brain(
            "brain-01-product", limit=10
        )

        assert len(templates) == 3, "Should retrieve all templates"
        assert (
            templates[0]["template_name"] == "Template A"
        ), "Highest success_rate should be first"
        assert (
            templates[1]["template_name"] == "Template B"
        ), "Second highest should be second"
        assert templates[2]["template_name"] == "Template C", "Lowest should be last"

        await db.close()


class TestDistillationIntegration:
    """Test KnowledgeDistillationService integration with template extraction."""

    @pytest.mark.asyncio
    async def test_template_extraction_integration(self):
        """Test KnowledgeDistillationService extracts templates after high-value sessions."""
        from mastermind_cli.experience.template_extractor import TemplateExtractor
        from mastermind_cli.orchestration.distillation_service import (
            KnowledgeDistillationService,
            DistillationTask,
        )

        # Use file-based database so KnowledgeDistillationService can access it
        import tempfile
        import os

        fd, db_path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        try:
            db = DatabaseConnection(db_path)
            await db.connect()
            await db.create_experience_schema()

            logger = ExperienceLogger(db)

            # Create high-quality experience records
            await logger.log_execution(
                brain_id="brain-01-product",
                input_json={"brief": "Test brief"},
                output_json={
                    "summary": "High quality session",
                    "sections": ["S1", "S2"],
                },
                duration_ms=600000,  # 10 minutes (high-value)
                status="success",
                custom_metadata={"quality_score": 3.5},
            )

            # Trigger distillation (service uses same database)
            service = KnowledgeDistillationService(db_path=db_path)
            task = DistillationTask(
                session_id="sess-001",
                brain_ids=["brain-01-product"],
                brief_summary="Test session",
                execution_start_ms=0,
                execution_end_ms=600000,
                invocation_method="mm:execute-phase",
            )

            await service.trigger_evaluation_and_distillation(task)

            # Verify template was extracted
            extractor = TemplateExtractor(logger)
            templates = await extractor.get_templates_for_brain("brain-01-product")

            assert len(templates) > 0, "Should have extracted at least one template"
            assert (
                templates[0]["success_rate"] >= 0.5
            ), "Templates should meet minimum success rate"

            await db.close()
        finally:
            # Cleanup temp file
            if os.path.exists(db_path):
                os.unlink(db_path)
