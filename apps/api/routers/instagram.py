"""Instagram Graph API sender

This module provides functions to send messages via the Instagram Graph API.
Supports:
- Comments on media posts
- Direct messages (DMs)

Environment Variables:
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Instagram Business Account ID from Meta for Developers
    INSTAGRAM_ACCESS_TOKEN: Access token for Instagram Graph API

Reference: https://developers.facebook.com/docs/instagram-api/reference/comment
"""

import os
from typing import Any, Optional
import httpx
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException

router = APIRouter()


class InstagramComment(BaseModel):
    """Instagram comment model for posting comments

    Attributes:
        media_id: Media ID where to post the comment
        comment_text: Comment text content
        attachment_id: Optional attachment ID for media comments
        access_token: Instagram access token (overrides env var)
    """

    media_id: str = Field(..., description="Media ID where to post the comment")
    comment_text: str = Field(..., description="Comment text content")
    attachment_id: Optional[str] = Field(None, description="Optional attachment ID")
    access_token: Optional[str] = Field(None, description="Override access token")


class InstagramDirectMessage(BaseModel):
    """Instagram direct message model

    Attributes:
        recipient_id: Recipient user ID
        message_text: Message text content
    """

    recipient_id: str = Field(..., description="Recipient user ID")
    message_text: str = Field(..., description="Message text content")


class InstagramError(Exception):
    """Custom exception for Instagram API errors

    Attributes:
        message: Error message
        status_code: HTTP status code from API
    """

    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message


async def send_instagram_comment(comment: InstagramComment) -> dict[str, Any]:
    """Send a comment via Instagram Graph API

    Posts a comment on an Instagram media post.

    Args:
        comment: InstagramComment with media_id and comment_text

    Returns:
        dict with comment_id from Instagram API response

    Raises:
        ValueError: If INSTAGRAM_BUSINESS_ACCOUNT_ID or INSTAGRAM_ACCESS_TOKEN not set
        InstagramError: If API request fails with 4xx/5xx status
        httpx.RequestError: If network error occurs
    """
    business_account_id = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID")
    access_token = comment.access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not business_account_id:
        raise ValueError("INSTAGRAM_BUSINESS_ACCOUNT_ID environment variable not set")

    if not access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")

    # Instagram Graph API endpoint for posting comments
    url = f"https://graph.facebook.com/v19.0/{business_account_id}/comments"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Build request body
    body = {
        "message": comment.comment_text,
    }

    # Add media attachment if provided
    if comment.attachment_id:
        body["attachment_id"] = comment.attachment_id
        # For media comments, post to media endpoint
        url = f"https://graph.facebook.com/v19.0/{comment.media_id}/comments"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=body, timeout=10.0)

            # Handle error responses
            if response.status_code >= 400:
                error_msg = response.text or f"HTTP {response.status_code}"
                # Provide user-friendly error messages
                if response.status_code == 401:
                    error_msg = "Unauthorized: Invalid or expired access token"
                elif response.status_code == 404:
                    error_msg = "Not found: Media or account not found"
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded: Too many requests"
                raise InstagramError(error_msg, response.status_code)

            response_data = response.json()

            # Return comment ID
            return {"comment_id": response_data.get("id", "")}

        except httpx.RequestError as e:
            raise InstagramError(f"Network error: {str(e)}", 503)


async def send_instagram_direct(recipient_id: str, message_text: str) -> dict[str, Any]:
    """Send a direct message via Instagram Graph API

    Sends a direct message to an Instagram user.

    Args:
        recipient_id: Recipient Instagram user ID
        message_text: Message text content

    Returns:
        dict with message_id from Instagram API response

    Raises:
        ValueError: If INSTAGRAM_ACCESS_TOKEN not set
        InstagramError: If API request fails with 4xx/5xx status
        httpx.RequestError: If network error occurs
    """
    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")

    if not access_token:
        raise ValueError("INSTAGRAM_ACCESS_TOKEN environment variable not set")

    # Instagram Graph API endpoint for direct messages
    url = "https://graph.facebook.com/v19.0/me/messages"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Build request body for DM
    body = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, headers=headers, json=body, timeout=10.0)

            # Handle error responses
            if response.status_code >= 400:
                error_msg = response.text or f"HTTP {response.status_code}"
                # Provide user-friendly error messages
                if response.status_code == 401:
                    error_msg = "Unauthorized: Invalid or expired access token"
                elif response.status_code == 404:
                    error_msg = "Not found: Recipient not found"
                elif response.status_code == 429:
                    error_msg = "Rate limit exceeded: Too many requests"
                raise InstagramError(error_msg, response.status_code)

            response_data = response.json()

            # Extract message ID from response
            messages = response_data.get("messages", [])
            if messages and len(messages) > 0:
                return {"message_id": messages[0].get("id", "")}

            return {"message_id": ""}

        except httpx.RequestError as e:
            raise InstagramError(f"Network error: {str(e)}", 503)


@router.post("/api/channels/instagram/send")
async def send_comment_endpoint(comment: InstagramComment) -> dict[str, Any]:
    """FastAPI endpoint for sending Instagram comments

    Args:
        comment: InstagramComment model

    Returns:
        dict with comment_id

    Raises:
        HTTPException: If value error or Instagram error occurs
    """
    try:
        return await send_instagram_comment(comment)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InstagramError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)


@router.post("/api/channels/instagram/direct")
async def send_direct_endpoint(message: InstagramDirectMessage) -> dict[str, Any]:
    """FastAPI endpoint for sending Instagram direct messages

    Args:
        message: InstagramDirectMessage model

    Returns:
        dict with message_id

    Raises:
        HTTPException: If value error or Instagram error occurs
    """
    try:
        return await send_instagram_direct(
            recipient_id=message.recipient_id,
            message_text=message.message_text,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except InstagramError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
