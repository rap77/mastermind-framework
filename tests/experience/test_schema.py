"""ExperienceRecord schema tests."""

import pytest
import asyncio
from mastermind_cli.experience.models import ExperienceRecord
from mastermind_cli.state.database import DatabaseConnection
from datetime import datetime, timezone


@pytest.mark.asyncio
async def test_experience_table_created():
    """Test 1: Table created with all columns."""
    db = DatabaseConnection(":memory:")
    await db.connect()

    # Create experience_records table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS experience_records (
            id TEXT PRIMARY KEY,
            brain_id TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            output_json JSONB NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            embedding_stub BLOB,
            parent_brain_id TEXT,
            trace_context_id TEXT,
            custom_metadata JSONB NOT NULL DEFAULT '{}'
        )
    """)

    # Verify table exists
    cursor = await db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='experience_records'"
    )
    result = await cursor.fetchone()
    assert result is not None
    assert result[0] == "experience_records"

    # Verify columns
    cursor = await db.conn.execute("PRAGMA table_info(experience_records)")
    columns = await cursor.fetchall()
    column_names = [col[1] for col in columns]

    expected_columns = [
        "id", "brain_id", "input_hash", "output_json", "timestamp",
        "duration_ms", "status", "embedding_stub", "parent_brain_id",
        "trace_context_id", "custom_metadata"
    ]
    for col in expected_columns:
        assert col in column_names

    await db.close()


@pytest.mark.asyncio
async def test_experience_indexes_created():
    """Test 2: Indexes created on (brain_id, timestamp DESC) and trace_context_id."""
    db = DatabaseConnection(":memory:")
    await db.connect()

    # Create table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS experience_records (
            id TEXT PRIMARY KEY,
            brain_id TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            output_json JSONB NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            embedding_stub BLOB,
            parent_brain_id TEXT,
            trace_context_id TEXT,
            custom_metadata JSONB NOT NULL DEFAULT '{}'
        )
    """)

    # Create indexes
    await db.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_experience_brain_timestamp
        ON experience_records(brain_id, timestamp DESC)
    """)

    await db.conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_experience_trace
        ON experience_records(trace_context_id)
    """)

    await db.conn.commit()

    # Verify indexes exist
    cursor = await db.conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='experience_records'"
    )
    indexes = await cursor.fetchall()
    index_names = [idx[0] for idx in indexes]

    assert "idx_experience_brain_timestamp" in index_names
    assert "idx_experience_trace" in index_names

    await db.close()


@pytest.mark.asyncio
async def test_experience_jsonb_operations():
    """Test 3: JSONB operations work on custom_metadata (SQLite JSON1 extension)."""
    db = DatabaseConnection(":memory:")
    await db.connect()

    # Create table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS experience_records (
            id TEXT PRIMARY KEY,
            brain_id TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            output_json JSONB NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            embedding_stub BLOB,
            parent_brain_id TEXT,
            trace_context_id TEXT,
            custom_metadata JSONB NOT NULL DEFAULT '{}'
        )
    """)

    # Insert test data with JSONB
    import json
    test_id = "test-123"
    metadata = {"model": "gpt-4", "tokens": 1000}
    await db.conn.execute(
        """INSERT INTO experience_records
           (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, custom_metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (test_id, "brain-01", "hash123", '{"result": "ok"}',
         datetime.now(timezone.utc).isoformat(), 100, "success", json.dumps(metadata))
    )
    await db.conn.commit()

    # Query using json_extract
    cursor = await db.conn.execute(
        """SELECT json_extract(custom_metadata, '$.model') FROM experience_records WHERE id = ?""",
        (test_id,)
    )
    result = await cursor.fetchone()
    assert result is not None
    assert result[0] == "gpt-4"

    await db.close()


@pytest.mark.asyncio
async def test_experience_embedding_stub_null():
    """Test 4: Embedding_stub accepts NULL (v3.0 placeholder)."""
    db = DatabaseConnection(":memory:")
    await db.connect()

    # Create table
    await db.conn.execute("""
        CREATE TABLE IF NOT EXISTS experience_records (
            id TEXT PRIMARY KEY,
            brain_id TEXT NOT NULL,
            input_hash TEXT NOT NULL,
            output_json JSONB NOT NULL,
            timestamp TEXT NOT NULL,
            duration_ms INTEGER NOT NULL,
            status TEXT NOT NULL,
            embedding_stub BLOB,
            parent_brain_id TEXT,
            trace_context_id TEXT,
            custom_metadata JSONB NOT NULL DEFAULT '{}'
        )
    """)

    # Insert record with NULL embedding_stub
    import json
    await db.conn.execute(
        """INSERT INTO experience_records
           (id, brain_id, input_hash, output_json, timestamp, duration_ms, status, embedding_stub, custom_metadata)
           VALUES (?, ?, ?, ?, ?, ?, ?, NULL, ?)""",
        ("test-456", "brain-02", "hash456", '{"result": "ok"}',
         datetime.now(timezone.utc).isoformat(), 200, "success", json.dumps({}))
    )
    await db.conn.commit()

    # Verify embedding_stub is NULL
    cursor = await db.conn.execute(
        "SELECT embedding_stub FROM experience_records WHERE id = ?",
        ("test-456",)
    )
    result = await cursor.fetchone()
    assert result is not None
    assert result[0] is None

    await db.close()


@pytest.mark.asyncio
async def test_experience_record_creation():
    """Test 5: ExperienceRecord can be created with valid data."""
    record = ExperienceRecord(
        id="test-id-123",
        brain_id="brain-01-product-strategy",
        input_hash="abc123",
        output_json={"result": "success"},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=100,
        status="success"
    )
    assert record.id == "test-id-123"
    assert record.brain_id == "brain-01-product-strategy"
    assert record.input_hash == "abc123"
    assert record.output_json == {"result": "success"}
    assert record.duration_ms == 100
    assert record.status == "success"


@pytest.mark.asyncio
async def test_experience_record_optional_fields():
    """Test 6: Optional fields work (parent_brain_id, trace_context_id, embedding_stub)."""
    record = ExperienceRecord(
        id="test-id-456",
        brain_id="brain-02-ux-research",
        input_hash="def456",
        output_json={"insights": []},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=200,
        status="success",
        parent_brain_id="brain-01-product-strategy",
        trace_context_id="trace-123",
        embedding_stub=None
    )
    assert record.parent_brain_id == "brain-01-product-strategy"
    assert record.trace_context_id == "trace-123"
    assert record.embedding_stub is None


@pytest.mark.asyncio
async def test_experience_record_custom_metadata():
    """Test 7: custom_metadata accepts arbitrary JSONB data."""
    record = ExperienceRecord(
        id="test-id-789",
        brain_id="brain-03-ui-design",
        input_hash="ghi789",
        output_json={"design": "modern"},
        timestamp=datetime.now(timezone.utc).isoformat(),
        duration_ms=300,
        status="success",
        custom_metadata={
            "model_version": "gpt-4",
            "tokens_used": 1500,
            "confidence": 0.95,
            "tags": ["ui", "design", "modern"]
        }
    )
    assert record.custom_metadata["model_version"] == "gpt-4"
    assert record.custom_metadata["tokens_used"] == 1500
    assert record.custom_metadata["confidence"] == 0.95
    assert record.custom_metadata["tags"] == ["ui", "design", "modern"]


@pytest.mark.asyncio
async def test_experience_record_input_hash_deterministic():
    """Test 8: input_hash is SHA256 of input_json (deterministic)."""
    import json
    input_json = {"query": "test", "context": "data"}
    hash1 = ExperienceRecord.create_hash(input_json)
    hash2 = ExperienceRecord.create_hash(input_json)
    assert hash1 == hash2
    # SHA256 should be 64 hex characters
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


@pytest.mark.asyncio
async def test_experience_record_timestamp_iso8601():
    """Test 9: timestamp is ISO 8601 format (datetime.now(timezone.utc))."""
    record = ExperienceRecord.create(
        brain_id="brain-04-frontend",
        input_json={"test": "data"},
        output_json={"result": "ok"},
        duration_ms=50,
        status="success"
    )
    # Should be valid ISO 8601
    assert "T" in record.timestamp
    assert "Z" in record.timestamp or "+" in record.timestamp
    # Should be parseable
    datetime.fromisoformat(record.timestamp.replace("Z", "+00:00"))


@pytest.mark.asyncio
async def test_experience_record_factory_method():
    """Test 10: ExperienceRecord.create() factory generates all fields."""
    record = ExperienceRecord.create(
        brain_id="brain-05-backend",
        input_json={"framework": "fastapi"},
        output_json={"architecture": "layered"},
        duration_ms=250,
        status="success",
        parent_brain_id="brain-04-frontend",
        trace_context_id="trace-abc",
        custom_metadata={"version": "1.0"}
    )
    assert record.id is not None
    assert len(record.id) > 0
    assert record.brain_id == "brain-05-backend"
    assert record.input_hash is not None
    assert record.output_json == {"architecture": "layered"}
    assert record.timestamp is not None
    assert record.duration_ms == 250
    assert record.status == "success"
    assert record.parent_brain_id == "brain-04-frontend"
    assert record.trace_context_id == "trace-abc"
    assert record.custom_metadata == {"version": "1.0"}


@pytest.mark.asyncio
async def test_experience_record_duration_validation():
    """Test 11: duration_ms must be >= 0."""
    with pytest.raises(ValueError):
        ExperienceRecord(
            id="test-id",
            brain_id="brain-01",
            input_hash="hash",
            output_json={},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=-1,  # Invalid: negative
            status="success"
        )


@pytest.mark.asyncio
async def test_experience_record_status_validation():
    """Test 12: status must be one of: success, failure, timeout."""
    # Valid status values
    for status in ["success", "failure", "timeout"]:
        record = ExperienceRecord(
            id=f"test-{status}",
            brain_id="brain-01",
            input_hash="hash",
            output_json={},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=100,
            status=status
        )
        assert record.status == status

    # Invalid status value
    with pytest.raises(ValueError):
        ExperienceRecord(
            id="test-invalid",
            brain_id="brain-01",
            input_hash="hash",
            output_json={},
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=100,
            status="invalid"  # Invalid status
        )
