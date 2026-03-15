"""
Brain-to-Brain Communication Protocol Types.

This module defines the message passing protocol for inter-brain communication.
Implements the "Sistema Nervioso" pattern with typed envelopes and content.

Architecture:
- BrainMessage: Internal content (YAML-based from ROADMAP specification)
- BrainEnvelope: Transport wrapper with metadata (Hybrid pattern)
- BrainOutputType: Message type enum (output, request, rejection, approval)
- SmartReference: Lazy-loading reference to parent brain output (v3.0 stub)
"""

from pydantic import BaseModel, Field
from typing import Any, Optional, Dict, Union
from enum import Enum
from datetime import datetime, timezone

from mastermind_cli.types.interfaces import BrainInput, BrainOutput


# =============================================================================
# MESSAGE TYPE ENUM
# =============================================================================


class BrainOutputType(str, Enum):
    """Message types from ROADMAP YAML specification.

    These types correspond to the communication patterns between brains:
    - OUTPUT: Normal brain output (most common)
    - REQUEST: Asking another brain for input (rare)
    - REJECTION: Brain #7 rejection of previous output
    - APPROVAL: Brain #7 approval of previous output
    """

    OUTPUT = "output"
    REQUEST = "request"
    REJECTION = "rejection"
    APPROVAL = "approval"


# =============================================================================
# INTERNAL MESSAGE CONTENT
# =============================================================================


class BrainMessage(BaseModel):
    """Internal message content (YAML-based from ROADMAP).

    This is the actual data being passed between brains, following the
    format specified in the ROADMAP documentation.

    Attributes:
        from_brain: Source brain ID
        to_brain: Destination brain ID
        type: Message type (output, request, rejection, approval)
        content: Message payload (summary, detail, assumptions, dependencies)
        task_id: Unique task identifier
        version: Protocol version (default: "2.0.0")
    """

    from_brain: str = Field(..., description="Source brain ID")
    to_brain: str = Field(..., description="Destination brain ID")
    type: BrainOutputType = Field(..., description="Message type")
    content: Dict[str, Any] = Field(
        ..., description="Message payload (summary, detail, assumptions, dependencies)"
    )
    task_id: str = Field(..., description="Unique task identifier")
    version: str = Field(default="2.0.0", description="Protocol version")


# =============================================================================
# TRANSPORT ENVELOPE
# =============================================================================


class BrainEnvelope(BaseModel):
    """Transport envelope with metadata (Hybrid pattern).

    This wrapper separates transport concerns (correlation, latency, retries)
    from the actual message content. Enables message tracking without
    polluting the BrainMessage contract.

    Attributes:
        message: The actual BrainMessage being transported
        correlation_id: Links related messages in a flow
        transport_metadata: Transport-level metadata (latency, retries, timestamps)
    """

    message: BrainMessage = Field(..., description="Internal message content")
    correlation_id: str = Field(..., description="Links related messages in flow")
    transport_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Transport metadata (latency, retries, timestamps)",
    )

    @classmethod
    def create(
        cls,
        from_brain: str,
        to_brain: str,
        payload: Union[BrainInput, BrainOutput],
        correlation_id: str,
        task_id: str,
        message_type: BrainOutputType = BrainOutputType.OUTPUT,
    ) -> "BrainEnvelope":
        """Factory to create envelope from brain payload.

        This method handles conversion between brain input/output models
        and the standardized message content format.

        Args:
            from_brain: Source brain ID
            to_brain: Destination brain ID
            payload: BrainInput or BrainOutput to convert
            correlation_id: Flow correlation ID
            task_id: Task identifier
            message_type: Type of message (default: OUTPUT)

        Returns:
            BrainEnvelope with converted content

        Example:
            >>> envelope = BrainEnvelope.create(
            ...     from_brain="brain-01",
            ...     to_brain="brain-03",
            ...     payload=brain_output,
            ...     correlation_id="corr-123",
            ...     task_id="task-1"
            ... )
        """
        # Convert BrainInput/Output to content dict
        if isinstance(payload, BrainInput):
            content = {
                "summary": f"Input from {from_brain}",
                "detail": payload.brief.problem_statement,
                "context": payload.additional_context,
            }
        elif isinstance(payload, BrainOutput):
            # Extract first 200 chars for summary
            content_preview = str(payload.model_dump())[:200]

            content = {
                "summary": content_preview,
                "detail": payload.model_dump_json(),
                "metadata": payload.model_dump(),
            }
        else:
            # Fallback for unknown types
            content = {"data": str(payload)}

        message = BrainMessage(
            from_brain=from_brain,
            to_brain=to_brain,
            type=message_type,
            content=content,
            task_id=task_id,
        )

        return cls(
            message=message,
            correlation_id=correlation_id,
            transport_metadata={"created_at": datetime.now(timezone.utc).isoformat()},
        )


# =============================================================================
# SMART REFERENCE (v3.0 STUB)
# =============================================================================


class SmartReference(BaseModel):
    """Lazy-loading reference to parent brain output.

    This is a STUB for v3.0 implementation. In the future, this will
    resolve parent outputs on-demand from the experience store to
    prevent unnecessary API calls and enable efficient caching.

    Attributes:
        parent_brain_id: Parent brain ID to reference
        correlation_id: Flow correlation ID for lookup
        cached_output: Cached output (private field, excluded from serialization)
    """

    parent_brain_id: str = Field(..., description="Parent brain ID")
    correlation_id: str = Field(..., description="Flow correlation ID")
    cached_output: Optional[BrainOutput] = Field(
        default=None, exclude=True, description="Cached output (not serialized)"
    )

    async def get_parent_output(self, mcp_client: Any) -> BrainOutput:
        """Resolve parent output on-demand (prevents unnecessary API calls).

        NOTE: This is a stub implementation for v3.0.
        In production, this will query the experience_records table.

        Args:
            mcp_client: MCP client for API calls

        Returns:
            Parent brain output

        Raises:
            NotImplementedError: Until v3.0 experience store is ready
        """
        # TODO: Implement in v3.0 with experience store integration
        # Query experience_records table by brain_id + correlation_id
        raise NotImplementedError(
            "SmartReference.get_parent_output() will be implemented in v3.0 "
            "with experience store integration."
        )
