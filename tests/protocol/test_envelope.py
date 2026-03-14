"""BrainMessage envelope tests."""

import pytest
from pydantic import ValidationError
from mastermind_cli.types.protocol import (
    BrainMessage,
    BrainEnvelope,
    BrainOutputType,
    SmartReference
)
from mastermind_cli.types.interfaces import BrainInput, Brief


def test_brain_message_validation():
    """Test BrainMessage validates from_brain, to_brain, payload, correlation_id."""
    message = BrainMessage(
        from_brain="brain-01-product-strategy",
        to_brain="brain-03-ux-research",
        type=BrainOutputType.OUTPUT,
        content={
            "summary": "Product strategy defined",
            "detail": "Full product strategy output here...",
            "assumptions": ["Market is growing", "Users need simplicity"],
            "dependencies": []
        },
        task_id="task-123",
        version="2.0.0"
    )

    assert message.from_brain == "brain-01-product-strategy"
    assert message.to_brain == "brain-03-ux-research"
    assert message.type == BrainOutputType.OUTPUT
    assert message.task_id == "task-123"
    assert message.version == "2.0.0"
    assert "summary" in message.content


def test_brain_message_missing_required_field():
    """Test BrainMessage validation fails without required fields."""
    with pytest.raises(ValidationError):
        BrainMessage(
            from_brain="brain-01",
            # Missing to_brain
            type=BrainOutputType.OUTPUT,
            content={"summary": "test"},
            task_id="task-1"
        )


def test_brain_envelope_wraps_message():
    """Test BrainEnvelope wraps BrainMessage with transport_metadata."""
    message = BrainMessage(
        from_brain="brain-01",
        to_brain="brain-03",
        type=BrainOutputType.OUTPUT,
        content={"summary": "test"},
        task_id="task-1"
    )

    envelope = BrainEnvelope(
        message=message,
        correlation_id="corr-123",
        transport_metadata={
            "created_at": "2026-03-14T16:44:44Z",
            "latency_ms": 150
        }
    )

    assert envelope.message == message
    assert envelope.correlation_id == "corr-123"
    assert envelope.transport_metadata["latency_ms"] == 150


def test_brain_output_type_enum():
    """Test BrainOutputType enum validates (output, request, rejection, approval)."""
    assert BrainOutputType.OUTPUT == "output"
    assert BrainOutputType.REQUEST == "request"
    assert BrainOutputType.REJECTION == "rejection"
    assert BrainOutputType.APPROVAL == "approval"


def test_message_serialization_deserialization():
    """Test Message serialization/deserialization works."""
    message = BrainMessage(
        from_brain="brain-01",
        to_brain="brain-03",
        type=BrainOutputType.OUTPUT,
        content={"summary": "test", "detail": "full detail"},
        task_id="task-1"
    )

    # Serialize to dict
    message_dict = message.model_dump()

    # Deserialize from dict
    message_restored = BrainMessage.model_validate(message_dict)

    assert message_restored.from_brain == message.from_brain
    assert message_restored.to_brain == message.to_brain
    assert message_restored.content == message.content


def test_envelope_factory_from_brain_input():
    """Test BrainEnvelope.create() factory from BrainInput."""
    brain_input = BrainInput(
        brief=Brief(problem_statement="Build a CRM system"),
        additional_context={"market": "SMB"},
        execution_metadata={"timestamp": "2026-03-14T16:44:44Z"}
    )

    envelope = BrainEnvelope.create(
        from_brain="brain-01",
        to_brain="orchestrator",
        payload=brain_input,
        correlation_id="corr-123",
        task_id="task-1",
        message_type=BrainOutputType.OUTPUT
    )

    assert envelope.message.from_brain == "brain-01"
    assert envelope.message.to_brain == "orchestrator"
    assert envelope.correlation_id == "corr-123"
    assert "Build a CRM system" in envelope.message.content["detail"]


def test_envelope_factory_from_brain_output():
    """Test BrainEnvelope.create() factory from BrainOutput."""
    from mastermind_cli.types.interfaces import ProductStrategy

    brain_output = ProductStrategy(
        positioning="The best CRM for small businesses",
        target_audience="Small business owners",
        key_features=["Contact management", "Sales pipeline"],
        success_metrics=["User adoption rate", "Revenue growth"]
    )

    envelope = BrainEnvelope.create(
        from_brain="brain-01",
        to_brain="orchestrator",
        payload=brain_output,
        correlation_id="corr-123",
        task_id="task-1",
        message_type=BrainOutputType.OUTPUT
    )

    assert envelope.message.from_brain == "brain-01"
    assert "best CRM" in envelope.message.content["summary"]
    assert envelope.message.content["metadata"]["positioning"] == brain_output.positioning


def test_smart_reference_stub():
    """Test SmartReference stub exists for v3.0 (lazy-loading)."""
    # SmartReference is a stub for future v3.0 implementation
    # For now, just test it can be instantiated
    ref = SmartReference(
        parent_brain_id="brain-01",
        correlation_id="corr-123"
    )

    assert ref.parent_brain_id == "brain-01"
    assert ref.correlation_id == "corr-123"
    # cached_output should be None initially
    assert ref.cached_output is None
