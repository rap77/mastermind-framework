"""Tests for Email sender (SMTP + aiosmtplib)"""

import os
import pytest
from unittest.mock import AsyncMock, patch
from routers.email import (
    send_email,
    send_html_email,
    EmailMessage as EmailModel,
    EmailError,
)


@pytest.fixture
def mock_smtp_env():
    """Set up SMTP environment variables"""
    os.environ["SMTP_HOST"] = "smtp.example.com"
    os.environ["SMTP_PORT"] = "587"
    os.environ["SMTP_USERNAME"] = "test@example.com"
    os.environ["SMTP_PASSWORD"] = "test_password"


@pytest.fixture
def email_message():
    """Sample email message"""
    return EmailModel(
        to="recipient@example.com",
        subject="Test Email",
        plain_text="This is a plain text email",
        html_body=None,
        thread_id=None,
        in_reply_to=None,
    )


@pytest.fixture
def html_email_message():
    """Sample HTML email message"""
    return EmailModel(
        to="recipient@example.com",
        subject="HTML Email",
        plain_text="Plain text fallback",
        html_body="<h1>HTML Email</h1><p>This is HTML content</p>",
        thread_id="thread123@example.com",
        in_reply_to="parent@example.com",
    )


class TestEmailSender:
    """Test email sending functionality"""

    @pytest.mark.asyncio
    async def test_send_plain_text_email_success(self, mock_smtp_env, email_message):
        """Test sending a plain text email successfully"""
        # Mock aiosmtplib SMTP client
        mock_smtp_client = AsyncMock()
        # send_message returns tuple[dict[str, SMTPResponse], str]
        mock_smtp_client.send_message.return_value = ({}, "<message-id@example.com>")

        with patch("routers.email.aiosmtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__aenter__.return_value = mock_smtp_client

            result = await send_email(email_message)

            assert result["message_id"] == "<message-id@example.com>"
            mock_smtp_client.send_message.assert_called_once()

            # Verify email structure
            call_args = mock_smtp_client.send_message.call_args
            email = call_args[0][0]
            assert email["To"] == "recipient@example.com"
            assert email["Subject"] == "Test Email"
            assert email["From"] == "test@example.com"

    @pytest.mark.asyncio
    async def test_send_html_email_success(self, mock_smtp_env, html_email_message):
        """Test sending an HTML email successfully"""
        mock_smtp_client = AsyncMock()
        mock_smtp_client.send_message.return_value = (
            {},
            "<html-message-id@example.com>",
        )

        with patch("routers.email.aiosmtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__aenter__.return_value = mock_smtp_client

            result = await send_html_email(html_email_message)

            assert result["message_id"] == "<html-message-id@example.com>"
            mock_smtp_client.send_message.assert_called_once()

            # Verify HTML content
            call_args = mock_smtp_client.send_message.call_args
            email = call_args[0][0]
            assert email["To"] == "recipient@example.com"
            assert email["Subject"] == "HTML Email"

    @pytest.mark.asyncio
    async def test_email_threading_headers(self, mock_smtp_env, html_email_message):
        """Test that threading headers (In-Reply-To, References) are preserved"""
        mock_smtp_client = AsyncMock()
        mock_smtp_client.send_message.return_value = ({}, "<threaded@example.com>")

        with patch("routers.email.aiosmtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__aenter__.return_value = mock_smtp_client

            result = await send_email(html_email_message)

            assert result["message_id"] == "<threaded@example.com>"

            # Verify threading headers
            call_args = mock_smtp_client.send_message.call_args
            email = call_args[0][0]
            assert email["In-Reply-To"] == "parent@example.com"
            assert email["References"] == "thread123@example.com"

    @pytest.mark.asyncio
    async def test_send_email_missing_env_vars(self, email_message):
        """Test that missing SMTP environment variables raise an error"""
        # Clear environment variables
        os.environ.pop("SMTP_HOST", None)
        os.environ.pop("SMTP_PORT", None)
        os.environ.pop("SMTP_USERNAME", None)
        os.environ.pop("SMTP_PASSWORD", None)

        with pytest.raises(ValueError, match="SMTP_HOST environment variable not set"):
            await send_email(email_message)

    @pytest.mark.asyncio
    async def test_send_email_smtp_error(self, mock_smtp_env, email_message):
        """Test handling SMTP errors"""
        mock_smtp_client = AsyncMock()
        mock_smtp_client.send_message.side_effect = Exception("SMTP connection failed")

        with patch("routers.email.aiosmtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__aenter__.return_value = mock_smtp_client

            with pytest.raises(EmailError, match="Failed to send email"):
                await send_email(email_message)

    @pytest.mark.asyncio
    async def test_send_html_email_without_plain_text(
        self, mock_smtp_env, html_email_message
    ):
        """Test sending HTML email without plain text fallback"""
        html_only = EmailModel(
            to="recipient@example.com",
            subject="HTML Only",
            plain_text=None,
            html_body="<h1>HTML Only</h1>",
            thread_id=None,
            in_reply_to=None,
        )

        mock_smtp_client = AsyncMock()
        mock_smtp_client.send_message.return_value = ({}, "<html-only@example.com>")

        with patch("routers.email.aiosmtplib.SMTP") as mock_smtp:
            mock_smtp.return_value.__aenter__.return_value = mock_smtp_client

            result = await send_html_email(html_only)

            assert result["message_id"] == "<html-only@example.com>"
            mock_smtp_client.send_message.assert_called_once()
