"""ExperienceRecord schema tests."""

import pytest
from mastermind_cli.experience.models import ExperienceRecord
from datetime import datetime, timezone


def test_experience_record_required_fields():
    """Test 1: ExperienceRecord validates all required fields."""
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


def test_experience_record_optional_fields():
    """Test 2: Optional fields work (parent_brain_id, trace_context_id, embedding_stub)."""
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


def test_experience_record_custom_metadata():
    """Test 3: custom_metadata accepts arbitrary JSONB data."""
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


def test_experience_record_input_hash_deterministic():
    """Test 4: input_hash is SHA256 of input_json (deterministic)."""
    input_json = {"query": "test", "context": "data"}
    hash1 = ExperienceRecord.create_hash(input_json)
    hash2 = ExperienceRecord.create_hash(input_json)
    assert hash1 == hash2
    # SHA256 should be 64 hex characters
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_experience_record_timestamp_iso8601():
    """Test 5: timestamp is ISO 8601 format (datetime.now(timezone.utc))."""
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


def test_experience_record_factory_method():
    """Test 6: ExperienceRecord.create() factory generates all fields."""
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


def test_experience_record_duration_validation():
    """Test 7: duration_ms must be >= 0."""
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


def test_experience_record_status_validation():
    """Test 8: status must be one of: success, failure, timeout."""
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
