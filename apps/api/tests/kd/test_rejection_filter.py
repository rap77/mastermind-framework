"""Tests for rejection filter and quality_score metadata in ExperienceLogger."""

import pytest
from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
class TestQualityScoreMetadata:
    """Test quality_score parameter integration in log_execution()."""

    async def test_log_execution_accepts_quality_score_parameter(self):
        """Test 1: log_execution() accepts quality_score parameter and stores in custom_metadata."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        record_id = await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "test"},
            output_json={"result": "success"},
            duration_ms=1000,
            status="success",
            quality_score=3.5,
        )

        # Retrieve record and verify quality_score is in custom_metadata
        record = await logger.get_by_id(record_id)
        assert record is not None
        assert "quality_score" in record.custom_metadata
        assert record.custom_metadata["quality_score"] == 3.5

        await db.close()

    async def test_log_execution_merges_quality_score_with_existing_metadata(self):
        """Test 2: quality_score is merged into existing custom_metadata."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        record_id = await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "test"},
            output_json={"result": "success"},
            duration_ms=1000,
            status="success",
            custom_metadata={"user_id": "user-123", "tags": ["important"]},
            quality_score=2.8,
        )

        # Verify all metadata is preserved
        record = await logger.get_by_id(record_id)
        assert record is not None
        assert record.custom_metadata["quality_score"] == 2.8
        assert record.custom_metadata["user_id"] == "user-123"
        assert record.custom_metadata["tags"] == ["important"]

        await db.close()


@pytest.mark.asyncio
class TestRejectionFilter:
    """Test rejection filter in get_recent_by_brain()."""

    async def test_get_recent_filters_by_quality_score_and_status(self):
        """Test 3: get_recent_by_brain() filters WHERE quality_score >= 1.0 AND status != 'rejected'."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log records with different quality scores and statuses
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "high"},
            output_json={"result": "excellent"},
            duration_ms=1000,
            status="success",
            quality_score=3.5,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "medium"},
            output_json={"result": "good"},
            duration_ms=1000,
            status="success",
            quality_score=1.5,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "low"},
            output_json={"result": "poor"},
            duration_ms=1000,
            status="success",
            quality_score=0.5,  # Below threshold
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "rejected"},
            output_json={"result": "bad"},
            duration_ms=1000,
            status="rejected",
            quality_score=2.0,  # High score but rejected
        )

        # Retrieve records - should only get high and medium quality (not low or rejected)
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 2
        quality_scores = [r.custom_metadata.get("quality_score") for r in records]
        assert 3.5 in quality_scores
        assert 1.5 in quality_scores
        assert 0.5 not in quality_scores  # Low quality excluded
        assert 2.0 not in quality_scores  # Rejected excluded

        await db.close()

    async def test_rejected_records_are_excluded_from_retrieval(self):
        """Test 4: Rejected records (status='rejected') are excluded from retrieval."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log a rejected record with high quality score
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "rejected"},
            output_json={"result": "bad"},
            duration_ms=1000,
            status="rejected",
            quality_score=3.0,
        )

        # Log a normal record
        normal_id = await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "normal"},
            output_json={"result": "good"},
            duration_ms=1000,
            status="success",
            quality_score=2.0,
        )

        # Retrieve records - should only get normal record
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 1
        assert records[0].id == normal_id
        assert records[0].status != "rejected"

        await db.close()

    async def test_low_quality_records_are_excluded_from_retrieval(self):
        """Test 5: Low-quality records (quality_score < 1.0) are excluded from retrieval."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log records with different quality scores
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "high"},
            output_json={"result": "excellent"},
            duration_ms=1000,
            status="success",
            quality_score=3.0,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "low"},
            output_json={"result": "poor"},
            duration_ms=1000,
            status="success",
            quality_score=0.8,  # Below threshold
        )

        # Retrieve records - should only get high quality
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 1
        assert records[0].custom_metadata.get("quality_score") == 3.0

        await db.close()

    async def test_mixed_records_returns_only_approved_records(self):
        """Test 6: Mix of approved + rejected + low-quality returns only approved records."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log various combinations
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "approved1"},
            output_json={"result": "good"},
            duration_ms=1000,
            status="success",
            quality_score=3.5,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "approved2"},
            output_json={"result": "ok"},
            duration_ms=1000,
            status="success",
            quality_score=1.2,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "rejected_high"},
            output_json={"result": "bad"},
            duration_ms=1000,
            status="rejected",
            quality_score=4.0,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "low_quality"},
            output_json={"result": "poor"},
            duration_ms=1000,
            status="success",
            quality_score=0.5,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "rejected_low"},
            output_json={"result": "terrible"},
            duration_ms=1000,
            status="rejected",
            quality_score=0.3,
        )

        # Retrieve records - should only get 2 approved records
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 2
        for record in records:
            assert record.status != "rejected"
            assert record.custom_metadata.get("quality_score", 0) >= 1.0

        await db.close()

    async def test_get_recent_accepts_min_quality_score_parameter(self):
        """Test 7: get_recent_by_brain() accepts min_quality_score parameter for custom threshold."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log records with different quality scores
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "excellent"},
            output_json={"result": "best"},
            duration_ms=1000,
            status="success",
            quality_score=3.5,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "good"},
            output_json={"result": "good"},
            duration_ms=1000,
            status="success",
            quality_score=2.0,
        )

        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "ok"},
            output_json={"result": "ok"},
            duration_ms=1000,
            status="success",
            quality_score=1.5,
        )

        # Retrieve with min_quality_score=2.0 (template threshold)
        records = await logger.get_recent_by_brain(
            brain_id="brain-001", min_quality_score=2.0, limit=100
        )

        assert len(records) == 2
        for record in records:
            assert record.custom_metadata.get("quality_score", 0) >= 2.0

        await db.close()
