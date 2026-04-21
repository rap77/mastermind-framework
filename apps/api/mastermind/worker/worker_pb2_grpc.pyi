"""Type stubs for worker_pb2_grpc.py (generated gRPC code)"""

import grpc
from typing import Any
from mastermind.worker.worker_pb2 import ProcessWebhookRequest, ProcessWebhookResponse

class WorkerStub:
    """Client-side gRPC stub for Worker service"""

    ProcessWebhook: grpc.UnaryUnaryMultiCallable[
        ProcessWebhookRequest, ProcessWebhookResponse
    ]

class WorkerServicer:
    """Server-side gRPC servicer for Worker service"""

    async def ProcessWebhook(
        self,
        request: ProcessWebhookRequest,
        context: grpc.ServicerContext,
    ) -> ProcessWebhookResponse: ...

def add_WorkerServicer_to_server(
    servicer: WorkerServicer,
    server: Any,
) -> None: ...
