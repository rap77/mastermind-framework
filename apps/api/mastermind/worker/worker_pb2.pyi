"""Type stubs for worker_pb2.py (generated protobuf code)"""

from google.protobuf.descriptor import FileDescriptor
from google.protobuf.message import Message

# Generated message classes
class ProcessWebhookRequest(Message):
    """Webhook processing request from Rust control plane"""

    trace_id: str
    channel: str
    payload: str
    sender_id: str
    message_type: str

    def __init__(
        self,
        trace_id: str = ...,
        channel: str = ...,
        payload: str = ...,
        sender_id: str = ...,
        message_type: str = ...,
    ) -> None: ...
    def SerializeToString(self, *, deterministic: bool = ...) -> bytes: ...
    @classmethod
    def FromString(cls, data: bytes) -> "ProcessWebhookRequest": ...

class ProcessWebhookResponse(Message):
    """Webhook processing response"""

    success: bool
    error_message: str
    ai_response: str
    suggested_channel: str
    processing_duration_ms: float

    def __init__(
        self,
        success: bool = ...,
        error_message: str = ...,
        ai_response: str = ...,
        suggested_channel: str = ...,
        processing_duration_ms: float = ...,
    ) -> None: ...
    def SerializeToString(self, *, deterministic: bool = ...) -> bytes: ...
    @classmethod
    def FromString(cls, data: bytes) -> "ProcessWebhookResponse": ...

# Module-level descriptor
DESCRIPTOR: FileDescriptor
