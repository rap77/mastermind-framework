"""WhatsApp Business Cloud API sender

This module provides functions to send messages via the WhatsApp Business Cloud API.
Supports text messages and media messages (images, documents, audio, video).

Environment Variables:
    WHATSAPP_PHONE_NUMBER_ID: Phone number ID from WhatsApp Business App
    WHATSAPP_ACCESS_TOKEN: Access token for WhatsApp Business Cloud API

Reference: https://developers.facebook.com/docs/whatsapp/cloud-api/messages/send
"""

import os
from typing import Any, Optional
import httpx
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


class WhatsAppMessage(BaseModel):
    """WhatsApp message model"""

    to: str = Field(..., description="Recipient phone number (international format)")
    message_type: str = Field(
        ..., description="Message type: text, image, document, audio, video"
    )
    text: Optional[str] = Field(None, description="Text content for text messages")
    media_url: Optional[str] = Field(None, description="Media URL for media messages")
    caption: Optional[str] = Field(None, description="Caption for media messages")


class WhatsAppError(Exception):
    """Custom exception for WhatsApp API errors"""

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def send_whatsapp_message(message: WhatsAppMessage) -> dict[str, Any]:
    """Send a text message via WhatsApp Business Cloud API

    Args:
        message: WhatsAppMessage with to, message_type, and text fields

    Returns:
        dict with message_id from WhatsApp API response

    Raises:
        WhatsAppError: If API request fails with 4xx/5xx status
        httpx.RequestError: If network error occurs
    """
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")

    if not phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID environment variable not set")

    if not access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN environment variable not set")

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Build request body based on message type
    if message.message_type == "text":
        body = {
            "messaging_product": "whatsapp",
            "to": message.to,
            "type": "text",
            "text": {"body": message.text or ""},
        }
    else:
        raise ValueError(
            f"Unsupported message type for send_whatsapp_message: {message.message_type}"
        )

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=body, headers=headers, timeout=30.0)

            # Handle error responses
            if response.status_code >= 400:
                error_msg = response.text or f"HTTP {response.status_code}"
                raise WhatsAppError(error_msg, response.status_code)

            response_data = response.json()

            # Extract message ID from response
            if "messages" in response_data and len(response_data["messages"]) > 0:
                message_id = response_data["messages"][0]["id"]
                return {"message_id": message_id}
            else:
                raise WhatsAppError("No message ID in response", response.status_code)

        except httpx.RequestError as e:
            raise WhatsAppError(f"Network error: {str(e)}", 503) from e


async def send_whatsapp_media(
    to: str, media_type: str, media_url: str, caption: Optional[str] = None
) -> dict[str, Any]:
    """Send a media message via WhatsApp Business Cloud API

    Args:
        to: Recipient phone number (international format)
        media_type: Type of media: image, document, audio, video
        media_url: URL of the media file
        caption: Optional caption for the media

    Returns:
        dict with message_id from WhatsApp API response

    Raises:
        WhatsAppError: If API request fails with 4xx/5xx status
        httpx.RequestError: If network error occurs
    """
    phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    access_token = os.getenv("WHATSAPP_ACCESS_TOKEN")

    if not phone_number_id:
        raise ValueError("WHATSAPP_PHONE_NUMBER_ID environment variable not set")

    if not access_token:
        raise ValueError("WHATSAPP_ACCESS_TOKEN environment variable not set")

    url = f"https://graph.facebook.com/v19.0/{phone_number_id}/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Build media-specific request body
    media_type_map = {
        "image": "image",
        "document": "document",
        "audio": "audio",
        "video": "video",
    }

    if media_type not in media_type_map:
        raise ValueError(f"Unsupported media type: {media_type}")

    body: dict[str, Any] = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": media_type,
        media_type: {"link": media_url},
    }

    # Add caption for image/document/video
    if caption and media_type in ["image", "document", "video"]:
        body[media_type]["caption"] = caption

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=body, headers=headers, timeout=30.0)

            # Handle error responses
            if response.status_code >= 400:
                error_msg = response.text or f"HTTP {response.status_code}"
                raise WhatsAppError(error_msg, response.status_code)

            response_data = response.json()

            # Extract message ID from response
            if "messages" in response_data and len(response_data["messages"]) > 0:
                message_id = response_data["messages"][0]["id"]
                return {"message_id": message_id}
            else:
                raise WhatsAppError("No message ID in response", response.status_code)

        except httpx.RequestError as e:
            raise WhatsAppError(f"Network error: {str(e)}", 503) from e


@router.post("/api/channels/whatsapp/send")
async def send_whatsapp_endpoint(message: WhatsAppMessage) -> dict[str, Any]:
    """FastAPI endpoint to send WhatsApp messages

    Args:
        message: WhatsAppMessage with to, message_type, text/media_url

    Returns:
        dict with message_id

    Raises:
        HTTPException: If message sending fails
    """
    try:
        if message.message_type == "text":
            return await send_whatsapp_message(message)
        elif message.message_type in ["image", "document", "audio", "video"]:
            return await send_whatsapp_media(
                to=message.to,
                media_type=message.message_type,
                media_url=message.media_url or "",
                caption=message.caption,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported message type: {message.message_type}",
            )
    except WhatsAppError as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=e.message,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Network error: {str(e)}",
        )
