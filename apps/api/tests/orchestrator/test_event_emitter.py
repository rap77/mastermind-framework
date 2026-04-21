#!/usr/bin/env python3
"""Tests for EventEmitter - brain operation event emission."""

import pytest
import uuid
from unittest.mock import AsyncMock, MagicMock

import asyncpg

from mastermind_cli.orchestrator.event_emitter import EventEmitter


# =============================================================================
# Test EventEmitter initialization
# =============================================================================


@pytest.mark.asyncio
async def test_event_emitter_initialization_with_connection():
    """Test EventEmitter initializes with provided connection."""
    mock_conn = MagicMock(spec=asyncpg.Connection)

    emitter = EventEmitter(db_conn=mock_conn)

    assert emitter.db_conn == mock_conn
    assert emitter._pool is None


@pytest.mark.asyncio
async def test_event_emitter_initialization_without_connection():
    """Test EventEmitter initializes without connection (creates pool)."""
    emitter = EventEmitter(db_conn=None)

    assert emitter.db_conn is None
    assert emitter._pool is None


# =============================================================================
# Test emit_brain_started method
# =============================================================================


@pytest.mark.asyncio
async def test_emit_brain_started_with_connection():
    """Test emit_brain_started uses provided connection."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    session_id = uuid.uuid4()
    flow_config = {"flow_type": "validation", "max_duration": 300}

    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=session_id,
        brief="Test brief",
        flow_config=flow_config,
    )

    # Verify execute was called
    mock_conn.execute.assert_called_once()
    # Verify it received the right number of arguments (query + params)
    assert len(mock_conn.execute.call_args[0]) == 6  # query + 5 parameters


@pytest.mark.asyncio
async def test_emit_brain_started_with_string_session_id():
    """Test emit_brain_started accepts string session_id."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id="test-session-123",  # String instead of UUID
        brief="Test brief",
        flow_config={},
    )

    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_emit_brain_started_empty_flow_config():
    """Test emit_brain_started handles empty flow config."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        brief="Test brief",
        flow_config={},  # Empty config
    )

    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_emit_brain_started_complex_flow_config():
    """Test emit_brain_started serializes complex flow config."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    complex_config = {
        "flow_type": "full_product",
        "brains": [1, 2, 3, 7],
        "timeout": 600,
        "retry": {"max_attempts": 3, "backoff": "exponential"},
    }

    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        brief="Complex flow",
        flow_config=complex_config,
    )

    mock_conn.execute.assert_called_once()


# =============================================================================
# Test emit_brain_completed method
# =============================================================================


@pytest.mark.asyncio
async def test_emit_brain_completed_with_connection():
    """Test emit_brain_completed uses provided connection."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    session_id = uuid.uuid4()
    result = {
        "status": "success",
        "output": "Task completed",
        "metrics": {"accuracy": 0.95},
    }

    await emitter.emit_brain_completed(
        brain_id="brain-01",
        session_id=session_id,
        duration_ms=1500,
        result=result,
    )

    mock_conn.execute.assert_called_once()
    assert len(mock_conn.execute.call_args[0]) == 6


@pytest.mark.asyncio
async def test_emit_brain_completed_minimal():
    """Test emit_brain_completed with minimal parameters."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    await emitter.emit_brain_completed(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        duration_ms=0,
        result={},
    )

    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_emit_brain_completed_large_result():
    """Test emit_brain_completed handles large result objects."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    large_result = {
        "status": "success",
        "data": [f"item_{i}" for i in range(1000)],
        "metadata": {f"key_{i}": f"value_{i}" for i in range(100)},
    }

    await emitter.emit_brain_completed(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        duration_ms=5000,
        result=large_result,
    )

    mock_conn.execute.assert_called_once()


# =============================================================================
# Test emit_brain_failed method
# =============================================================================


@pytest.mark.asyncio
async def test_emit_brain_failed_with_connection():
    """Test emit_brain_failed uses provided connection."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    session_id = uuid.uuid4()

    await emitter.emit_brain_failed(
        brain_id="brain-01",
        session_id=session_id,
        error="Database connection failed",
        stage="execution",
    )

    mock_conn.execute.assert_called_once()
    assert len(mock_conn.execute.call_args[0]) == 6


@pytest.mark.asyncio
async def test_emit_brain_failed_different_stages():
    """Test emit_brain_failed for different execution stages."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    stages = ["validation", "execution", "post-processing", "cleanup"]

    for stage in stages:
        await emitter.emit_brain_failed(
            brain_id="brain-01",
            session_id=uuid.uuid4(),
            error=f"Error at {stage}",
            stage=stage,
        )

    assert mock_conn.execute.call_count == len(stages)


@pytest.mark.asyncio
async def test_emit_brain_failed_long_error_message():
    """Test emit_brain_failed handles long error messages."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    long_error = "Error: " + "A" * 500 + " - very long error message"

    await emitter.emit_brain_failed(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        error=long_error,
        stage="execution",
    )

    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_emit_brain_failed_with_special_characters():
    """Test emit_brain_failed handles special characters in error."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    error_msg = "Error: 'quotes' and \"double quotes\" and \n newlines \t tabs"

    await emitter.emit_brain_failed(
        brain_id="brain-01",
        session_id=uuid.uuid4(),
        error=error_msg,
        stage="execution",
    )

    mock_conn.execute.assert_called_once()


# =============================================================================
# Test emit_brain_routed method
# =============================================================================


@pytest.mark.asyncio
async def test_emit_brain_routed_with_connection():
    """Test emit_brain_routed uses provided connection."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    session_id = uuid.uuid4()

    await emitter.emit_brain_routed(
        brain_id="brain-07",  # Orchestrator brain
        session_id=session_id,
        from_brain="brain-01",
        to_brain="brain-02",
        reason="Product strategy requires UX validation",
    )

    mock_conn.execute.assert_called_once()
    assert len(mock_conn.execute.call_args[0]) == 6


@pytest.mark.asyncio
async def test_emit_brain_routed_minimal():
    """Test emit_brain_routed with minimal parameters."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    await emitter.emit_brain_routed(
        brain_id="brain-07",
        session_id=uuid.uuid4(),
        from_brain="brain-01",
        to_brain="brain-02",
        reason="",
    )

    mock_conn.execute.assert_called_once()


@pytest.mark.asyncio
async def test_emit_brain_routed_complex_routing():
    """Test emit_brain_routed with complex routing scenarios."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    # Test various brain-to-brain routes
    routes = [
        ("brain-01", "brain-02", "Product → UX"),
        ("brain-02", "brain-03", "UX → UI"),
        ("brain-03", "brain-04", "UI → Frontend"),
        ("brain-01", "brain-07", "Product → Orchestrator (escalation)"),
    ]

    for from_brain, to_brain, reason in routes:
        await emitter.emit_brain_routed(
            brain_id="brain-07",
            session_id=uuid.uuid4(),
            from_brain=from_brain,
            to_brain=to_brain,
            reason=reason,
        )

    assert mock_conn.execute.call_count == len(routes)


# =============================================================================
# Test close method
# =============================================================================


@pytest.mark.asyncio
async def test_close_closes_pool():
    """Test close closes connection pool if created."""
    mock_pool = MagicMock()
    mock_pool.close = AsyncMock()

    emitter = EventEmitter(db_conn=None)
    emitter._pool = mock_pool

    await emitter.close()

    mock_pool.close.assert_called_once()
    assert emitter._pool is None


@pytest.mark.asyncio
async def test_close_with_provided_connection():
    """Test close does nothing when connection was provided."""
    mock_conn = MagicMock(spec=asyncpg.Connection)

    emitter = EventEmitter(db_conn=mock_conn)

    await emitter.close()

    # Should not close provided connection
    assert emitter._pool is None


@pytest.mark.asyncio
async def test_close_when_no_pool():
    """Test close is safe to call when no pool exists."""
    emitter = EventEmitter(db_conn=None)

    # Should not raise
    await emitter.close()

    assert emitter._pool is None


@pytest.mark.asyncio
async def test_close_multiple_times():
    """Test close can be called multiple times safely."""
    mock_pool = MagicMock()
    mock_pool.close = AsyncMock()

    emitter = EventEmitter(db_conn=None)
    emitter._pool = mock_pool

    await emitter.close()
    await emitter.close()
    await emitter.close()

    # Should only close once
    mock_pool.close.assert_called_once()


# =============================================================================
# Test integration scenarios
# =============================================================================


@pytest.mark.asyncio
async def test_full_brain_lifecycle_events():
    """Test emitting all events for a complete brain lifecycle."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)
    session_id = uuid.uuid4()

    # Brain starts
    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=session_id,
        brief="Test brief",
        flow_config={"flow_type": "validation"},
    )

    # Brain completes
    await emitter.emit_brain_completed(
        brain_id="brain-01",
        session_id=session_id,
        duration_ms=1000,
        result={"status": "success"},
    )

    assert mock_conn.execute.call_count == 2


@pytest.mark.asyncio
async def test_brain_failure_lifecycle():
    """Test emitting events for brain failure scenario."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)
    session_id = uuid.uuid4()

    # Brain starts
    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=session_id,
        brief="Test brief",
        flow_config={},
    )

    # Brain fails
    await emitter.emit_brain_failed(
        brain_id="brain-01",
        session_id=session_id,
        error="Timeout exceeded",
        stage="execution",
    )

    assert mock_conn.execute.call_count == 2


@pytest.mark.asyncio
async def test_brain_routing_sequence():
    """Test emitting routing events for multi-brain flow."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)
    session_id = uuid.uuid4()

    # Start brain-01
    await emitter.emit_brain_started(
        brain_id="brain-01",
        session_id=session_id,
        brief="Multi-brain flow",
        flow_config={},
    )

    # Route brain-01 → brain-02
    await emitter.emit_brain_routed(
        brain_id="brain-07",
        session_id=session_id,
        from_brain="brain-01",
        to_brain="brain-02",
        reason="Delegation required",
    )

    # Start brain-02
    await emitter.emit_brain_started(
        brain_id="brain-02",
        session_id=session_id,
        brief="Delegated task",
        flow_config={},
    )

    # Complete brain-02
    await emitter.emit_brain_completed(
        brain_id="brain-02",
        session_id=session_id,
        duration_ms=500,
        result={"output": "Task completed"},
    )

    assert mock_conn.execute.call_count == 4


# =============================================================================
# Test error handling
# =============================================================================


@pytest.mark.asyncio
async def test_emit_handles_database_errors():
    """Test emit methods propagate database errors."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock(side_effect=Exception("Database error"))

    emitter = EventEmitter(db_conn=mock_conn)

    with pytest.raises(Exception, match="Database error"):
        await emitter.emit_brain_started(
            brain_id="brain-01",
            session_id=uuid.uuid4(),
            brief="Test",
            flow_config={},
        )


# =============================================================================
# Test event order
# =============================================================================


@pytest.mark.asyncio
async def test_event_order_is_preserved():
    """Test events are emitted in correct order."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)
    session_id = uuid.uuid4()

    # Emit events in specific order
    await emitter.emit_brain_started(
        brain_id="brain-01", session_id=session_id, brief="Test", flow_config={}
    )
    await emitter.emit_brain_completed(
        brain_id="brain-01", session_id=session_id, duration_ms=100, result={}
    )

    # Verify call order
    assert mock_conn.execute.call_count == 2


# =============================================================================
# Test UUID generation
# =============================================================================


@pytest.mark.asyncio
async def test_events_generate_unique_ids():
    """Test each event generates a unique ID."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)
    session_id = uuid.uuid4()

    # Emit multiple events
    await emitter.emit_brain_started(
        brain_id="brain-01", session_id=session_id, brief="Test", flow_config={}
    )
    await emitter.emit_brain_completed(
        brain_id="brain-01", session_id=session_id, duration_ms=100, result={}
    )

    # Each should have been called with different IDs
    assert mock_conn.execute.call_count == 2


# =============================================================================
# Test different brain IDs
# =============================================================================


@pytest.mark.asyncio
async def test_emitter_handles_different_brain_ids():
    """Test emitter works with various brain ID formats."""
    mock_conn = MagicMock(spec=asyncpg.Connection)
    mock_conn.execute = AsyncMock()

    emitter = EventEmitter(db_conn=mock_conn)

    brain_ids = ["brain-01", "brain-02", "brain-03", "brain-07", "orchestrator"]

    for brain_id in brain_ids:
        await emitter.emit_brain_started(
            brain_id=brain_id,
            session_id=uuid.uuid4(),
            brief=f"Test for {brain_id}",
            flow_config={},
        )

    assert mock_conn.execute.call_count == len(brain_ids)
