"""Tests for TTL ceiling (expires_at column) in experience records."""

import pytest
from datetime import datetime, timedelta, timezone
from mastermind_cli.experience.logger import ExperienceLogger
from mastermind_cli.state.database import DatabaseConnection


@pytest.mark.asyncio
class TestTTLMigration:
    """Test expires_at column migration."""

    async def test_schema_includes_expires_at_column(self):
        """Test 1: Schema includes expires_at column in experience_records table."""
        db = DatabaseConnection(":memory:")
        await db.connect()

        # Create schema (should include expires_at by default)
        await db.create_experience_schema()

        # Verify column exists
        cursor = await db.conn.execute("PRAGMA table_info(experience_records)")
        columns = await cursor.fetchall()
        column_names = [col[1] for col in columns]

        assert "expires_at" in column_names

        await db.close()

    async def test_schema_includes_index_on_expires_at(self):
        """Test 2: Schema includes index on expires_at for query performance."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        # Verify index exists
        cursor = await db.conn.execute(
            "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_experience_expires_at'"
        )
        index = await cursor.fetchone()

        assert index is not None

        await db.close()

    async def test_log_execution_sets_default_90_day_ttl(self):
        """Test 3: log_execution() sets default 90-day TTL when expires_at not provided."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Create record without expires_at
        record_id = await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "test"},
            output_json={"result": "success"},
            duration_ms=1000,
            status="success",
        )

        # Verify expires_at was set to ~90 days from now
        record = await logger.get_by_id(record_id)
        assert record is not None
        assert "expires_at" in record.custom_metadata

        # Parse expires_at
        expires_at = datetime.fromisoformat(record.custom_metadata.get("expires_at"))
        created_at = datetime.fromisoformat(record.timestamp)

        # Should be approximately 90 days difference
        difference = (expires_at - created_at).days
        assert 89 <= difference <= 91  # Allow small timing variance

        await db.close()


@pytest.mark.asyncio
class TestTTLFiltering:
    """Test TTL filtering in get_recent_by_brain()."""

    async def test_get_recent_filters_expired_records(self):
        """Test 4: get_recent_by_brain() filters WHERE expires_at > datetime('now')."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log record that expires in future (valid)
        future_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "future"},
            output_json={"result": "valid"},
            duration_ms=1000,
            status="success",
            quality_score=2.0,
            expires_at=future_expiry,
        )

        # Log record that expires in past (expired)
        past_expiry = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "past"},
            output_json={"result": "expired"},
            duration_ms=1000,
            status="success",
            quality_score=2.0,
            expires_at=past_expiry,
        )

        # Log record with NULL expires_at (uses default 90 days, so valid)
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "null"},
            output_json={"result": "no expiry"},
            duration_ms=1000,
            status="success",
            quality_score=2.0,
            expires_at=None,
        )

        # Retrieve records - should only get future and null (not past)
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 2

        await db.close()

    async def test_expired_records_are_excluded_from_retrieval(self):
        """Test 5: Expired records (expires_at < now) are excluded from retrieval."""
        db = DatabaseConnection(":memory:")
        await db.connect()
        await db.create_experience_schema()

        logger = ExperienceLogger(db)

        # Log expired record
        past_expiry = (datetime.now(timezone.utc) - timedelta(days=10)).isoformat()
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "expired"},
            output_json={"result": "old"},
            duration_ms=1000,
            status="success",
            quality_score=3.0,
            expires_at=past_expiry,
        )

        # Log valid record
        future_expiry = (datetime.now(timezone.utc) + timedelta(days=90)).isoformat()
        await logger.log_execution(
            brain_id="brain-001",
            input_json={"task": "valid"},
            output_json={"result": "new"},
            duration_ms=1000,
            status="success",
            quality_score=3.0,
            expires_at=future_expiry,
        )

        # Retrieve records - should only get valid record
        records = await logger.get_recent_by_brain(brain_id="brain-001", limit=100)

        assert len(records) == 1

        await db.close()
