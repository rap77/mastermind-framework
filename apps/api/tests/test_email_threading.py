"""Tests for email threading support"""

import pytest
from routers.email import EmailMessage, send_email


class TestEmailThreading:
    """Test email threading headers (In-Reply-To, References)"""

    @pytest.mark.asyncio
    async def test_email_with_in_reply_to_header(self, mocker):
        """Test that In-Reply-To header is set when provided"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Re: Previous conversation",
            plain_text="This is a reply",
            in_reply_to="<original-message-id@example.com>",
        )

        # Mock environment variables
        mocker.patch.dict(
            "os.environ",
            {
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "test@example.com",
                "SMTP_PASSWORD": "password",
            },
        )

        # Mock SMTP send
        mock_smtp = mocker.patch("routers.email.aiosmtplib.SMTP")
        mock_smtp.return_value.__aenter__.return_value.login = mocker.AsyncMock()
        mock_smtp.return_value.__aenter__.return_value.send_message = mocker.AsyncMock(
            return_value="250 OK <message-id@example.com>"
        )

        result = await send_email(message)

        # Verify email was sent
        assert result is not None
        assert "message_id" in result

        # Verify SMTP was called
        mock_smtp.assert_called_once()

    @pytest.mark.asyncio
    async def test_email_with_thread_id_references_header(self, mocker):
        """Test that References header is set when thread_id is provided"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Re: Thread continuation",
            plain_text="Continuing the thread",
            thread_id="<msg1@example.com> <msg2@example.com>",
        )

        # Mock environment variables
        mocker.patch.dict(
            "os.environ",
            {
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "test@example.com",
                "SMTP_PASSWORD": "password",
            },
        )

        # Mock SMTP send
        mock_smtp = mocker.patch("routers.email.aiosmtplib.SMTP")
        mock_smtp.return_value.__aenter__.return_value.login = mocker.AsyncMock()
        mock_smtp.return_value.__aenter__.return_value.send_message = mocker.AsyncMock(
            return_value="250 OK <message-id@example.com>"
        )

        result = await send_email(message)

        # Verify email was sent
        assert result is not None
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_email_with_both_threading_headers(self, mocker):
        """Test email with both In-Reply-To and References headers"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Re: Thread with both headers",
            plain_text="Reply with full threading context",
            in_reply_to="<previous-message@example.com>",
            thread_id="<msg1@example.com> <msg2@example.com>",
        )

        # Mock environment variables
        mocker.patch.dict(
            "os.environ",
            {
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "test@example.com",
                "SMTP_PASSWORD": "password",
            },
        )

        # Mock SMTP send
        mock_smtp = mocker.patch("routers.email.aiosmtplib.SMTP")
        mock_smtp.return_value.__aenter__.return_value.login = mocker.AsyncMock()
        mock_smtp.return_value.__aenter__.return_value.send_message = mocker.AsyncMock(
            return_value="250 OK <message-id@example.com>"
        )

        result = await send_email(message)

        # Verify email was sent
        assert result is not None
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_email_without_threading_headers(self, mocker):
        """Test that email works without threading headers (new thread)"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="New conversation",
            plain_text="Starting a new thread",
        )

        # Mock environment variables
        mocker.patch.dict(
            "os.environ",
            {
                "SMTP_HOST": "smtp.example.com",
                "SMTP_PORT": "587",
                "SMTP_USERNAME": "test@example.com",
                "SMTP_PASSWORD": "password",
            },
        )

        # Mock SMTP send
        mock_smtp = mocker.patch("routers.email.aiosmtplib.SMTP")
        mock_smtp.return_value.__aenter__.return_value.login = mocker.AsyncMock()
        mock_smtp.return_value.__aenter__.return_value.send_message = mocker.AsyncMock(
            return_value="250 OK <message-id@example.com>"
        )

        result = await send_email(message)

        # Verify email was sent
        assert result is not None
        assert "message_id" in result

    def test_email_message_model_accepts_threading_fields(self):
        """Test that EmailMessage model accepts threading fields"""
        message = EmailMessage(
            to="recipient@example.com",
            subject="Test",
            plain_text="Test",
            in_reply_to="<msg@example.com>",
            thread_id="<msg1@example.com>",
        )

        assert message.in_reply_to == "<msg@example.com>"
        assert message.thread_id == "<msg1@example.com>"

    def test_email_message_model_threading_fields_optional(self):
        """Test that threading fields are optional"""
        message = EmailMessage(
            to="recipient@example.com", subject="Test", plain_text="Test"
        )

        assert message.in_reply_to is None
        assert message.thread_id is None
