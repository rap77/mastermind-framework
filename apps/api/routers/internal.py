"""Internal gRPC server for webhook processing

This module implements the gRPC server that receives webhook processing requests
from the Rust control plane and routes them to the appropriate channel senders.

Environment Variables:
    GRPC_SERVER_HOST: gRPC server host (default: 127.0.0.1)
    GRPC_SERVER_PORT: gRPC server port (default: 50051)
"""

import asyncio
import os
from typing import Optional

import grpc
import structlog

from mastermind.worker.worker_pb2 import (
    ProcessWebhookRequest,
    ProcessWebhookResponse,
)
from mastermind.worker.worker_pb2_grpc import (
    WorkerServicer,
    add_WorkerServicer_to_server,
)

# Import channel senders
from routers.whatsapp import send_whatsapp_message, WhatsAppMessage
from routers.instagram import send_instagram_comment, InstagramComment
from routers.email import send_email, EmailMessage

logger = structlog.get_logger(__name__)


class WorkerService(WorkerServicer):
    """gRPC service for processing webhooks from Rust control plane

    Receives webhook events via gRPC from the Rust webhook worker,
    processes them (AI simulation for now), and sends to channel APIs.
    """

    async def ProcessWebhook(
        self, request: ProcessWebhookRequest, context
    ) -> ProcessWebhookResponse:
        """Process webhook from Rust control plane

        Args:
            request: ProcessWebhookRequest with trace_id, channel, payload, message_type
            context: gRPC context (RPC metadata)

        Returns:
            ProcessWebhookResponse with success status and AI response
        """
        logger.info(
            "Received gRPC webhook request",
            trace_id=request.trace_id,
            channel=request.channel,
            message_type=request.message_type,
        )

        try:
            # Route to appropriate channel sender
            if request.channel == "whatsapp":
                await self._send_whatsapp(request.payload)
            elif request.channel == "instagram":
                await self._send_instagram(request.payload)
            elif request.channel == "email":
                await self._send_email(request.payload)
            else:
                raise ValueError(f"Unsupported channel: {request.channel}")

            logger.info(
                "Webhook processed successfully",
                trace_id=request.trace_id,
                channel=request.channel,
            )

            return ProcessWebhookResponse(
                success=True,
                ai_response="Message sent successfully",
                suggested_channel=request.channel,
                processing_duration_ms=100,  # Simulated AI processing time
            )

        except Exception as e:
            logger.error(
                "Webhook processing failed",
                trace_id=request.trace_id,
                channel=request.channel,
                error=str(e),
            )
            return ProcessWebhookResponse(
                success=False,
                error_message=str(e),
                ai_response="",
                suggested_channel="",
                processing_duration_ms=0,
            )

    async def _send_whatsapp(self, payload: str):
        """Send message via WhatsApp Business Cloud API

        Args:
            payload: JSON string containing WhatsApp message data

        Raises:
            Exception: If WhatsApp API call fails
        """
        import json

        data = json.loads(payload)
        message = WhatsAppMessage(
            to=data.get("to", ""),
            message_type=data.get("message_type", "text"),
            text=data.get("text"),
            media_url=data.get("media_url"),
            caption=data.get("caption"),
        )
        await send_whatsapp_message(message)

    async def _send_instagram(self, payload: str):
        """Send message via Instagram Graph API

        Args:
            payload: JSON string containing Instagram message data

        Raises:
            Exception: If Instagram API call fails
        """
        import json

        data = json.loads(payload)
        message = InstagramComment(
            media_id=data.get("media_id", ""),
            comment_text=data.get("comment_text", ""),
            attachment_id=data.get("attachment_id"),
            access_token=data.get("access_token"),
        )
        await send_instagram_comment(message)

    async def _send_email(self, payload: str):
        """Send message via SMTP email

        Args:
            payload: JSON string containing email data

        Raises:
            Exception: If email send fails
        """
        import json

        data = json.loads(payload)
        message = EmailMessage(
            to=data.get("to", ""),
            subject=data.get("subject", ""),
            body=data.get("body", ""),
            html_body=data.get("html_body"),
        )
        await send_email(message)


async def start_grpc_server(
    host: Optional[str] = None,
    port: Optional[int] = None,
):
    """Start gRPC server in background

    Args:
        host: Server host (default: from env or 127.0.0.1)
        port: Server port (default: from env or 50051)

    Returns:
        Server instance
    """
    host = host or os.getenv("GRPC_SERVER_HOST", "127.0.0.1")
    port = port or int(os.getenv("GRPC_SERVER_PORT", "50051"))

    # Create gRPC server (grpc.aio)
    server = grpc.aio.server()
    add_WorkerServicer_to_server(WorkerService(), server)

    # Add port and start listening
    server.add_insecure_port(f"{host}:{port}")
    await server.start()

    logger.info(
        "gRPC server started",
        host=host,
        port=port,
    )

    return server


# For running server directly (useful for testing)
if __name__ == "__main__":

    async def main():
        server = await start_grpc_server()
        logger.info("Press Ctrl+C to stop")
        try:
            await server.wait_for_termination()
        except KeyboardInterrupt:
            await server.stop(grace_period=0.1)

    asyncio.run(main())
