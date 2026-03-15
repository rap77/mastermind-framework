"""
ExperienceRecord Pydantic model for full-fidelity execution logging.

This module defines the ExperienceRecord schema for storing brain executions
with PII redaction, JSONB storage, and lineage tracking for v3.0 ML readiness.
"""

from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional, Any
import hashlib
import json
import uuid


class ExperienceRecord(BaseModel):
    """Full-fidelity execution record for v3.0 ML readiness.

    This model captures complete execution context for:
    - Debugging hallucinations (exact inputs/outputs)
    - Future LoRA fine-tuning (JSON history)
    - RAG over past outputs (avoid repeating mistakes)

    Attributes:
        id: Unique record identifier (UUID4)
        brain_id: Brain being executed
        input_hash: SHA256 of input_json for deduplication
        output_json: Complete output from brain (redacted)
        timestamp: ISO 8601 timestamp (UTC)
        duration_ms: Execution duration in milliseconds
        status: Execution status (success, failure, timeout)
        parent_brain_id: Parent brain that triggered this execution
        trace_context_id: Trace context for distributed tracing
        embedding_stub: Placeholder for v3.0 pgvector embeddings
        custom_metadata: Extensible metadata for brain-specific metrics
    """

    # Required fields
    id: str = Field(..., description="Unique record identifier (UUID4)")
    brain_id: str = Field(..., description="Brain being executed")
    input_hash: str = Field(..., description="SHA256 of input_json for deduplication")
    output_json: dict[str, Any] = Field(
        ..., description="Complete output from brain (redacted)"
    )
    timestamp: str = Field(..., description="ISO 8601 timestamp (UTC)")
    duration_ms: int = Field(
        ..., ge=0, description="Execution duration in milliseconds"
    )
    status: str = Field(
        ..., pattern="^(success|failure|timeout)$", description="Execution status"
    )

    # Lineage fields
    parent_brain_id: Optional[str] = Field(
        None, description="Parent brain that triggered this execution"
    )
    trace_context_id: Optional[str] = Field(
        None, description="Trace context for distributed tracing"
    )

    # v3.0 placeholder (NULL for now, pgvector in future)
    embedding_stub: Optional[bytes] = Field(
        None, description="Placeholder for v3.0 pgvector embeddings"
    )

    # Extensible metadata for brain-specific metrics
    custom_metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Extensible metadata for brain-specific metrics",
    )

    @classmethod
    def create_hash(cls, input_json: dict[str, Any]) -> str:
        """Create SHA256 hash of input for deduplication.

        Args:
            input_json: Input dictionary to hash

        Returns:
            64-character hex string (SHA256 hash)

        Note:
            Uses sorted keys for deterministic hashing
        """
        normalized = json.dumps(input_json, sort_keys=True)
        return hashlib.sha256(normalized.encode()).hexdigest()

    @classmethod
    def create(
        cls,
        brain_id: str,
        input_json: dict[str, Any],
        output_json: dict[str, Any],
        duration_ms: int,
        status: str,
        parent_brain_id: Optional[str] = None,
        trace_context_id: Optional[str] = None,
        custom_metadata: dict[str, Any] | None = None,
        embedding_stub: Optional[bytes] = None,
    ) -> "ExperienceRecord":
        """Factory method with auto-generated fields.

        Args:
            brain_id: Brain being executed
            input_json: Input dictionary (will be hashed)
            output_json: Output dictionary
            duration_ms: Execution duration in milliseconds
            status: Execution status (success, failure, timeout)
            parent_brain_id: Optional parent brain ID
            trace_context_id: Optional trace context ID
            custom_metadata: Optional custom metadata dictionary

        Returns:
            ExperienceRecord instance with auto-generated id, input_hash, timestamp
        """
        if custom_metadata is None:
            custom_metadata = {}

        return cls(
            id=str(uuid.uuid4()),
            brain_id=brain_id,
            input_hash=cls.create_hash(input_json),
            output_json=output_json,
            timestamp=datetime.now(timezone.utc).isoformat(),
            duration_ms=duration_ms,
            status=status,
            parent_brain_id=parent_brain_id,
            trace_context_id=trace_context_id,
            custom_metadata=custom_metadata,
            embedding_stub=embedding_stub,
        )
