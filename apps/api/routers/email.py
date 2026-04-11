"""Email sender (SMTP + aiosmtplib)

This module provides functions to send emails via SMTP using aiosmtplib.
Supports plain text and HTML emails with threading support.

Environment Variables:
    SMTP_HOST: SMTP server hostname
    SMTP_PORT: SMTP server port (usually 587 for TLS)
    SMTP_USERNAME: SMTP username
    SMTP_PASSWORD: SMTP password

Reference: https://aiosmtplib.readthedocs.io/
"""

import os
from email.message import EmailMessage as StdEmailMessage
from typing import Optional, Set
import aiosmtplib
import nh3
from pydantic import BaseModel, Field, field_validator
from fastapi import APIRouter, HTTPException, status

router = APIRouter()


# Allowed HTML tags and attributes for email content
ALLOWED_TAGS: Set[str] = {
    "p",
    "br",
    "a",
    "strong",
    "em",
    "b",
    "i",
    "u",
    "ul",
    "ol",
    "li",
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "blockquote",
    "code",
    "pre",
    "div",
    "span",
}

# nh3 expects a set of allowed attributes
ALLOWED_ATTRIBUTES: Set[str] = {
    "href",
    "title",
    "class",
    "id",
}


def sanitize_html(html_content: str) -> str:
    """Sanitize HTML content to prevent XSS attacks using nh3.

    Args:
        html_content: Raw HTML content

    Returns:
        Sanitized HTML content with safe tags and attributes only

    Examples:
        >>> sanitize_html("<p>Hello</p><script>alert('xss')</script>")
        '<p>Hello</p>'
        >>> sanitize_html('<a href="https://example.com">Link</a>')
        '<a href="https://example.com">Link</a>'
    """
    return nh3.clean(
        html_content,
        tags=ALLOWED_TAGS,
        # Use nh3's default safe attributes (href, src, alt, title, etc.)
        attributes=None,
        url_schemes={"http", "https", "mailto"},
    )


class EmailMessage(BaseModel):
    """Email message model"""

    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., description="Email subject")
    plain_text: Optional[str] = Field(None, description="Plain text body")
    html_body: Optional[str] = Field(None, description="HTML body")
    thread_id: Optional[str] = Field(None, description="Thread ID (References header)")
    in_reply_to: Optional[str] = Field(None, description="In-Reply-To header")

    @field_validator("html_body")
    @classmethod
    def sanitize_html_body(cls, v: Optional[str]) -> Optional[str]:
        """Sanitize HTML content to prevent XSS attacks."""
        if v is None:
            return None
        return sanitize_html(v)


class EmailError(Exception):
    """Custom exception for email sending errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


async def send_email(message: EmailMessage) -> dict:
    """Send an email via SMTP

    Args:
        message: EmailMessage with to, subject, plain_text, html_body, and threading headers

    Returns:
        dict with message_id (generated)

    Raises:
        ValueError: If SMTP environment variables are not set
        EmailError: If SMTP sending fails
    """
    # Get SMTP configuration from environment
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")

    if not smtp_host:
        raise ValueError("SMTP_HOST environment variable not set")

    if not smtp_port:
        raise ValueError("SMTP_PORT environment variable not set")

    if not smtp_username:
        raise ValueError("SMTP_USERNAME environment variable not set")

    if not smtp_password:
        raise ValueError("SMTP_PASSWORD environment variable not set")

    # Create email message
    email = StdEmailMessage()
    email["To"] = message.to
    email["Subject"] = message.subject
    email["From"] = smtp_username

    # Add threading headers if present
    if message.in_reply_to:
        email["In-Reply-To"] = message.in_reply_to

    if message.thread_id:
        email["References"] = message.thread_id

    # Add plain text body
    if message.plain_text:
        email.set_content(message.plain_text)

    # Add HTML body if present (already sanitized by validator)
    if message.html_body:
        if message.plain_text:
            # If both plain text and HTML, add as alternative
            email.add_alternative(message.html_body, subtype="html")
        else:
            # If only HTML, set as content
            email.set_content(message.html_body, subtype="html")

    # Send via SMTP
    try:
        port = int(smtp_port)
        async with aiosmtplib.SMTP(hostname=smtp_host, port=port, use_tls=True) as smtp:
            await smtp.login(smtp_username, smtp_password)
            response = await smtp.send_message(email)
            # Extract message ID from response
            message_id = (
                response.split("<")[1].split(">")[0]
                if "<" in response
                else f"sent-{os.urandom(4).hex()}"
            )
            return {"message_id": f"<{message_id}>"}
    except Exception as e:
        raise EmailError(f"Failed to send email: {str(e)}")


async def send_html_email(message: EmailMessage) -> dict:
    """Send an HTML email via SMTP

    This is a convenience function that calls send_email with HTML content.

    Args:
        message: EmailMessage with html_body set

    Returns:
        dict with message_id

    Raises:
        ValueError: If SMTP environment variables are not set
        EmailError: If SMTP sending fails
    """
    if not message.html_body:
        raise ValueError("html_body is required for send_html_email")

    return await send_email(message)


@router.post("/api/channels/email/send")
async def api_send_email(message: EmailMessage):
    """API endpoint to send an email

    Args:
        message: EmailMessage with to, subject, plain_text, html_body

    Returns:
        dict with message_id

    Raises:
        HTTPException: If email sending fails
    """
    try:
        result = await send_email(message)
        return result
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except EmailError as e:
        raise HTTPException(status_code=e.status_code, detail=e.message)
