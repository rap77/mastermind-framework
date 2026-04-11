"""Tests for WhatsApp Business Cloud API sender"""

import os
import pytest
from unittest.mock import Mock, AsyncMock, patch
from httpx import Response, RequestError
from routers.whatsapp import (
    send_whatsapp_message,
    send_whatsapp_media,
    WhatsAppMessage,
    WhatsAppError,
)


@pytest.fixture
def mock_whatsapp_env():
    """Set up WhatsApp environment variables"""
    os.environ["WHATSAPP_PHONE_NUMBER_ID"] = "123456789"
    os.environ["WHATSAPP_ACCESS_TOKEN"] = "test_token"


@pytest.fixture
def whatsapp_message():
    """Sample WhatsApp message"""
    return WhatsAppMessage(to="1234567890", message_type="text", text="Hello, world!")


@pytest.fixture
def whatsapp_media_message():
    """Sample WhatsApp media message"""
    return {
        "to": "1234567890",
        "message_type": "image",
        "media_url": "https://example.com/image.jpg",
        "caption": "Check this out",
    }


class TestWhatsAppSender:
    """Test WhatsApp message sending functionality"""

    @pytest.mark.asyncio
    async def test_send_text_message_success(self, mock_whatsapp_env, whatsapp_message):
        """Test sending a text message successfully"""
        # Mock HTTPX client
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "wamid.example123"}]}

        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_http_client

            result = await send_whatsapp_message(whatsapp_message)

            assert result["message_id"] == "wamid.example123"
            mock_http_client.post.assert_called_once()

            # Verify request structure
            call_args = mock_http_client.post.call_args
            assert call_args[1]["json"]["to"] == "1234567890"
            assert call_args[1]["json"]["type"] == "text"
            assert call_args[1]["json"]["messaging_product"] == "whatsapp"

    @pytest.mark.asyncio
    async def test_send_media_message_success(
        self, mock_whatsapp_env, whatsapp_media_message
    ):
        """Test sending a media message (image) successfully"""
        # Mock HTTPX client
        mock_response = Mock(spec=Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "wamid.media456"}]}

        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_http_client

            result = await send_whatsapp_media(
                to="1234567890",
                media_type="image",
                media_url="https://example.com/image.jpg",
                caption="Check this out",
            )

            assert result["message_id"] == "wamid.media456"
            mock_http_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_message_unauthorized_error(
        self, mock_whatsapp_env, whatsapp_message
    ):
        """Test handling 401 Unauthorized error"""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 401
        mock_response.text = "Invalid access token"

        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_http_client

            with pytest.raises(WhatsAppError) as exc_info:
                await send_whatsapp_message(whatsapp_message)

            assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_send_message_not_found_error(
        self, mock_whatsapp_env, whatsapp_message
    ):
        """Test handling 404 Not Found error"""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 404
        mock_response.text = "Phone number not found"

        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_http_client

            with pytest.raises(WhatsAppError) as exc_info:
                await send_whatsapp_message(whatsapp_message)

            assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_send_message_server_error(self, mock_whatsapp_env, whatsapp_message):
        """Test handling 500 Internal Server Error"""
        mock_response = Mock(spec=Response)
        mock_response.status_code = 500
        mock_response.text = "Internal server error"

        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.return_value = mock_response
            mock_client.return_value.__aenter__.return_value = mock_http_client

            with pytest.raises(WhatsAppError) as exc_info:
                await send_whatsapp_message(whatsapp_message)

            assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_send_message_network_error(
        self, mock_whatsapp_env, whatsapp_message
    ):
        """Test handling network errors"""
        with patch("routers.whatsapp.httpx.AsyncClient") as mock_client:
            mock_http_client = AsyncMock()
            mock_http_client.post.side_effect = RequestError("Network error")
            mock_client.return_value.__aenter__.return_value = mock_http_client

            with pytest.raises(WhatsAppError) as exc_info:
                await send_whatsapp_message(whatsapp_message)

            assert exc_info.value.status_code == 503
            assert "Network error" in str(exc_info.value)
