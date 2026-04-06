"""
Tests for AnalyticsService (system health + outcome metrics).

Tests dashboard metrics for monitoring brain learning progress.
"""

import pytest
from datetime import datetime, timedelta

from mastermind_cli.orchestration.analytics_service import (
    AnalyticsService,
    SystemHealthMetrics,
)
from mastermind_cli.state.database import DatabaseConnection


@pytest.fixture
async def analytics_service(async_db: DatabaseConnection) -> AnalyticsService:
    """Create analytics service fixture."""
    return AnalyticsService(async_db)


@pytest.fixture
async def sample_records(async_db: DatabaseConnection) -> None:
    """Create sample experience records for testing."""
    await async_db.create_experience_schema()
    now = datetime.utcnow()

    # Insert 10 sample records with varying quality and duration
    samples = [
        # (brain_id, status, duration_ms, quality_score, expires_at)
        ("brain-001", "completed", 100, 0.85, None),  # Good, fast
        ("brain-001", "completed", 150, 0.90, None),  # Excellent
        ("brain-001", "rejected", 200, 0.30, None),  # Rejected, low quality
        ("brain-002", "completed", 300, 0.75, None),  # Slower
        ("brain-002", "completed", 400, 0.80, None),
        ("brain-003", "completed", 500, 0.70, None),
        ("brain-003", "completed", 600, 0.65, None),
        ("brain-003", "rejected", 700, 0.40, None),
        ("brain-001", "completed", 800, 0.95, None),
        ("brain-002", "completed", 900, 0.85, None),
    ]

    for brain_id, status, duration_ms, quality_score, expires_at in samples:
        await async_db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"record-{brain_id}-{duration_ms}",
                brain_id,
                f"hash-{brain_id}-{duration_ms}",
                f"Test output for {brain_id}",
                now.isoformat(),
                duration_ms,
                status,
                f'{{"quality_score": {quality_score}}}',
                expires_at,
            ),
        )
    await async_db.conn.commit()


@pytest.fixture
async def sample_templates(async_db: DatabaseConnection) -> None:
    """Create sample knowledge templates for testing."""
    await async_db.create_experience_schema()
    now = datetime.utcnow()

    templates = [
        # (brain_id, template_name, success_rate, usage_count)
        ("brain-001", "Template A", 0.95, 50),
        ("brain-001", "Template B", 0.85, 30),
        ("brain-002", "Template C", 0.75, 20),
        ("brain-003", "Template D", 0.90, 40),
    ]

    for brain_id, template_name, success_rate, usage_count in templates:
        await async_db.conn.execute(
            """INSERT INTO knowledge_templates
               (id, brain_id, template_name, template_data, success_rate, usage_count, created_at, last_used_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                f"template-{brain_id}-{template_name}",
                brain_id,
                template_name,
                f'{{"pattern": "{template_name}"}}',
                success_rate,
                usage_count,
                now.isoformat(),
                now.isoformat(),
            ),
        )
    await async_db.conn.commit()


class TestAnalyticsServiceSystemHealth:
    """Test system health metrics calculation."""

    @pytest.mark.asyncio
    async def test_get_system_health_returns_all_metrics(
        self, analytics_service: AnalyticsService, sample_records
    ):
        """Test get_system_health() returns record_count, avg_quality_score, rejection_rate, p50/p90_latency_ms, t1_trend."""
        metrics = await analytics_service.get_system_health()

        assert isinstance(metrics, SystemHealthMetrics)
        assert hasattr(metrics, "record_count")
        assert hasattr(metrics, "avg_quality_score")
        assert hasattr(metrics, "rejection_rate")
        assert hasattr(metrics, "p50_latency_ms")
        assert hasattr(metrics, "p90_latency_ms")
        assert hasattr(metrics, "t1_trend")

        # Verify types
        assert isinstance(metrics.record_count, int)
        assert isinstance(metrics.avg_quality_score, float)
        assert isinstance(metrics.rejection_rate, float)
        assert isinstance(metrics.p50_latency_ms, float)
        assert isinstance(metrics.p90_latency_ms, float)
        assert isinstance(metrics.t1_trend, list)

    @pytest.mark.asyncio
    async def test_get_system_health_calculates_rejection_rate(
        self, analytics_service: AnalyticsService, sample_records
    ):
        """Test get_system_health() calculates rejection_rate = rejected_count / total_count."""
        metrics = await analytics_service.get_system_health()

        # Sample has 2 rejected out of 10 total = 0.2
        assert metrics.record_count == 10
        assert metrics.rejection_rate == 0.2

    @pytest.mark.asyncio
    @pytest.mark.asyncio
    async def test_get_system_health_filters_expired_records(
        self, analytics_service: AnalyticsService, async_db: DatabaseConnection
    ):
        """Test get_system_health() filters out expired records (expires_at < now)."""
        await async_db.create_experience_schema()
        now = datetime.utcnow()

        # Insert expired record
        await async_db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "record-expired",
                "brain-001",
                "hash-expired",
                "Expired output",
                now.isoformat(),
                1000,
                "completed",
                '{"quality_score": 0.5}',
                (now - timedelta(days=1)).isoformat(),  # Expired yesterday
            ),
        )
        await async_db.conn.commit()

        metrics = await analytics_service.get_system_health()

        # Should only count non-expired records (0 in this case, no sample_records fixture)
        assert metrics.record_count == 0


class TestAnalyticsServiceTemplates:
    """Test template retrieval with success rate tracking."""

    @pytest.mark.asyncio
    async def test_get_templates_ordered_by_success_rate(
        self, analytics_service: AnalyticsService, sample_templates
    ):
        """Test get_templates() returns templates ordered by success_rate DESC with usage_count."""
        templates = await analytics_service.get_templates()

        assert len(templates) == 4

        # Verify ordering: success_rate DESC
        assert templates[0]["success_rate"] >= templates[1]["success_rate"]
        assert templates[1]["success_rate"] >= templates[2]["success_rate"]
        assert templates[2]["success_rate"] >= templates[3]["success_rate"]

        # Verify required fields
        for template in templates:
            assert "id" in template
            assert "brain_id" in template
            assert "template_name" in template
            assert "success_rate" in template
            assert "usage_count" in template

    @pytest.mark.asyncio
    async def test_get_templates_filters_by_brain_id(
        self, analytics_service: AnalyticsService, sample_templates
    ):
        """Test get_templates() filters by brain_id when provided."""
        brain_001_templates = await analytics_service.get_templates(
            brain_id="brain-001"
        )

        assert len(brain_001_templates) == 2
        for template in brain_001_templates:
            assert template["brain_id"] == "brain-001"

    @pytest.mark.asyncio
    async def test_get_templates_filters_by_min_success_rate(
        self, analytics_service: AnalyticsService, sample_templates
    ):
        """Test get_templates() filters by min_success_rate threshold."""
        high_quality_templates = await analytics_service.get_templates(
            min_success_rate=0.90
        )

        assert len(high_quality_templates) == 2  # Template A (0.95) + Template D (0.90)
        for template in high_quality_templates:
            assert template["success_rate"] >= 0.90


class TestAnalyticsServicePatterns:
    """Test pattern extraction from experience records."""

    @pytest.mark.asyncio
    async def test_get_patterns_groups_by_brain_and_input_hash(
        self, analytics_service: AnalyticsService, async_db: DatabaseConnection
    ):
        """Test get_patterns() groups experience_records by brain_id + brief similarity."""
        await async_db.create_experience_schema()
        now = datetime.utcnow()

        # Insert records with same input_hash (same brief)
        await async_db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "record-pattern-1",
                "brain-001",
                "repeated-hash",  # Same hash
                "Response 1",
                now.isoformat(),
                100,
                "completed",
                '{"quality_score": 0.8}',
                None,
            ),
        )
        await async_db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "record-pattern-2",
                "brain-001",
                "repeated-hash",  # Same hash
                "Response 2",
                now.isoformat(),
                150,
                "completed",
                '{"quality_score": 0.9}',
                None,
            ),
        )
        await async_db.conn.commit()

        patterns = await analytics_service.get_patterns()

        # Should have brain-001 with frequency 2 for the repeated brief
        assert "brain-001" in patterns
        brain_001_patterns = patterns["brain-001"]
        assert len(brain_001_patterns) > 0

        # Find the pattern with frequency 2
        repeated_pattern = next(
            (p for p in brain_001_patterns if p["frequency"] == 2), None
        )
        assert repeated_pattern is not None
        assert repeated_pattern["avg_quality"] == 0.85  # (0.8 + 0.9) / 2

    @pytest.mark.asyncio
    async def test_get_patterns_filters_by_brain_id(
        self, analytics_service: AnalyticsService, async_db: DatabaseConnection
    ):
        """Test get_patterns() filters by brain_id when provided."""
        await async_db.create_experience_schema()
        now = datetime.utcnow()

        await async_db.conn.execute(
            """INSERT INTO experience_records
               (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                "record-filter-test",
                "brain-001",
                "test-hash",
                "Response",
                now.isoformat(),
                100,
                "completed",
                '{"quality_score": 0.8}',
                None,
            ),
        )
        await async_db.conn.commit()

        patterns = await analytics_service.get_patterns(brain_id="brain-001")

        assert "brain-001" in patterns
        assert len(patterns) == 1  # Only brain-001
        assert "brain-002" not in patterns


class TestAnalyticsEndpoints:
    """Test analytics API endpoints."""

    @pytest.mark.asyncio
    async def test_system_health_endpoint(
        self, async_db: DatabaseConnection, sample_records
    ):
        """Test GET /api/analytics/system-health returns system health metrics."""
        from fastapi.testclient import TestClient
        from mastermind_cli.api.app import create_app
        from mastermind_cli.api.dependencies import get_db_path
        import tempfile

        # Use file-based database to persist data across test
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create schema and insert data
        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            # Re-insert sample records
            now = datetime.utcnow()
            samples = [
                ("brain-001", "completed", 100, 0.85, None),
                ("brain-001", "completed", 150, 0.90, None),
                ("brain-001", "rejected", 200, 0.30, None),
            ]
            for brain_id, status, duration_ms, quality_score, expires_at in samples:
                await db.conn.execute(
                    """INSERT INTO experience_records
                       (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"record-{brain_id}-{duration_ms}",
                        brain_id,
                        f"hash-{brain_id}-{duration_ms}",
                        f"Test output for {brain_id}",
                        now.isoformat(),
                        duration_ms,
                        status,
                        f'{{"quality_score": {quality_score}}}',
                        expires_at,
                    ),
                )
            await db.conn.commit()

        app = create_app(db_path)
        app.dependency_overrides[get_db_path] = lambda: db_path
        client = TestClient(app)
        response = client.get("/api/analytics/system-health")

        assert response.status_code == 200
        data = response.json()
        assert "record_count" in data
        assert "avg_quality_score" in data
        assert "rejection_rate" in data
        assert "p50_latency_ms" in data
        assert "p90_latency_ms" in data
        assert "t1_trend" in data

    @pytest.mark.asyncio
    async def test_templates_endpoint(
        self, async_db: DatabaseConnection, sample_templates
    ):
        """Test GET /api/analytics/templates returns templates ordered by success_rate."""
        from fastapi.testclient import TestClient
        from mastermind_cli.api.app import create_app
        from mastermind_cli.api.dependencies import get_db_path
        import tempfile

        # Use file-based database to persist data across test
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create schema and insert data
        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            # Re-insert sample templates
            now = datetime.utcnow()
            templates = [
                ("brain-001", "Template A", 0.95, 50),
                ("brain-001", "Template B", 0.85, 30),
                ("brain-002", "Template C", 0.75, 20),
                ("brain-003", "Template D", 0.90, 40),
            ]
            for brain_id, template_name, success_rate, usage_count in templates:
                await db.conn.execute(
                    """INSERT INTO knowledge_templates
                       (id, brain_id, template_name, template_data, success_rate, usage_count, created_at, last_used_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        f"template-{brain_id}-{template_name}",
                        brain_id,
                        template_name,
                        f'{{"pattern": "{template_name}"}}',
                        success_rate,
                        usage_count,
                        now.isoformat(),
                        now.isoformat(),
                    ),
                )
            await db.conn.commit()

        app = create_app(db_path)
        app.dependency_overrides[get_db_path] = lambda: db_path
        client = TestClient(app)
        response = client.get("/api/analytics/templates")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 4  # All 4 templates

        # Verify ordering by success_rate DESC
        if len(data) > 1:
            assert data[0]["success_rate"] >= data[1]["success_rate"]

    @pytest.mark.asyncio
    async def test_patterns_endpoint(
        self, async_db: DatabaseConnection, sample_records
    ):
        """Test GET /api/analytics/patterns returns patterns grouped by brain."""
        from fastapi.testclient import TestClient
        from mastermind_cli.api.app import create_app
        from mastermind_cli.api.dependencies import get_db_path
        import tempfile

        # Use file-based database to persist data across test
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create schema and insert data
        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            now = datetime.utcnow()
            await db.conn.execute(
                """INSERT INTO experience_records
                   (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "record-pattern-test",
                    "brain-001",
                    "test-hash",
                    "Response",
                    now.isoformat(),
                    100,
                    "completed",
                    '{"quality_score": 0.8}',
                    None,
                ),
            )
            await db.conn.commit()

        app = create_app(db_path)
        app.dependency_overrides[get_db_path] = lambda: db_path
        client = TestClient(app)
        response = client.get("/api/analytics/patterns")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)

        # Should have patterns for at least one brain
        if data:
            assert "brain-001" in data or "brain-002" in data or "brain-003" in data

    @pytest.mark.asyncio
    async def test_outcome_metrics_endpoint(
        self, async_db: DatabaseConnection, sample_records
    ):
        """Test GET /api/analytics/outcome-metrics returns outcome metrics."""
        from fastapi.testclient import TestClient
        from mastermind_cli.api.app import create_app
        from mastermind_cli.api.dependencies import get_db_path
        import tempfile

        # Use file-based database to persist data across test
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name

        # Create schema and insert data
        async with DatabaseConnection(db_path) as db:
            await db.create_experience_schema()
            now = datetime.utcnow()
            await db.conn.execute(
                """INSERT INTO experience_records
                   (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata, expires_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    "record-outcome-test",
                    "brain-001",
                    "test-hash",
                    "Response",
                    now.isoformat(),
                    100,
                    "completed",
                    '{"quality_score": 0.8}',
                    None,
                ),
            )
            await db.conn.commit()

        app = create_app(db_path)
        app.dependency_overrides[get_db_path] = lambda: db_path
        client = TestClient(app)
        response = client.get("/api/analytics/outcome-metrics")

        assert response.status_code == 200
        data = response.json()
        assert "delta_velocity" in data
        assert "knowledge_yield" in data
        assert "planning_accuracy" in data
