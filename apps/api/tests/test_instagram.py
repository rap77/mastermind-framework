"""Instagram Graph API sender tests

Tests for sending comments and direct messages via Instagram Graph API.
Environment Variables:
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Instagram Business Account ID
    INSTAGRAM_ACCESS_TOKEN: Instagram Graph API access token

Reference: https://developers.facebook.com/docs/instagram-api/reference/comment
"""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from routers.instagram import (
    InstagramComment,
    send_instagram_comment,
    send_instagram_direct,
    InstagramError,
)


@pytest.fixture
def mock_env_vars():
    """Set required environment variables for testing"""
    os.environ["INSTAGRAM_BUSINESS_ACCOUNT_ID"] = "123456789"
    os.environ["INSTAGRAM_ACCESS_TOKEN"] = "test_access_token"


@pytest.fixture
def mock_httpx_client():
    """Mock HTTPX async client"""
    with patch("routers.instagram.httpx.AsyncClient") as mock_client:
        async_mock = AsyncMock()
        mock_client.return_value.__aenter__.return_value = async_mock
        yield async_mock


class TestInstagramComment:
    """Test InstagramComment pydantic model"""

    def test_instagram_comment_model_text_only(self):
        """Test InstagramComment with text only"""
        comment = InstagramComment(
            media_id="987654321",
            comment_text="Great post!",
        )
        assert comment.media_id == "987654321"
        assert comment.comment_text == "Great post!"

    def test_instagram_comment_model_with_text(self):
        """Test InstagramComment with attachment_id"""
        comment = InstagramComment(
            media_id="987654321",
            comment_text="Check this out!",
            attachment_id="attachment_123",
        )
        assert comment.media_id == "987654321"
        assert comment.comment_text == "Check this out!"
        assert comment.attachment_id == "attachment_123"


class TestSendInstagramComment:
    """Test send_instagram_comment function"""

    @pytest.mark.asyncio
    async def test_send_text_comment_success(self, mock_env_vars, mock_httpx_client):
        """Test sending text comment successfully"""
        # Mock API response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "comment_123"}
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Great post!",
        )

        result = await send_instagram_comment(comment)

        assert result["comment_id"] == "comment_123"
        mock_httpx_client.post.assert_called_once()

        # Verify request
        call_args = mock_httpx_client.post.call_args
        assert "instagram.com" in call_args[0][0]
        assert call_args[1]["headers"]["Authorization"] == "Bearer test_access_token"

    @pytest.mark.asyncio
    async def test_send_comment_with_media(self, mock_env_vars, mock_httpx_client):
        """Test sending comment with media attachment"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"id": "comment_456"}
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Nice photo!",
            attachment_id="attachment_789",
        )

        result = await send_instagram_comment(comment)

        assert result["comment_id"] == "comment_456"

    @pytest.mark.asyncio
    async def test_send_comment_unauthorized(self, mock_env_vars, mock_httpx_client):
        """Test sending comment with invalid token (401)"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Invalid OAuth token"
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Test",
        )

        with pytest.raises(InstagramError) as exc_info:
            await send_instagram_comment(comment)

        assert exc_info.value.status_code == 401
        assert "Unauthorized" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_send_comment_not_found(self, mock_env_vars, mock_httpx_client):
        """Test sending comment to non-existent media (404)"""
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.text = "Media not found"
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="invalid_id",
            comment_text="Test",
        )

        with pytest.raises(InstagramError) as exc_info:
            await send_instagram_comment(comment)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_send_comment_rate_limit(self, mock_env_vars, mock_httpx_client):
        """Test hitting rate limit (429)"""
        mock_response = MagicMock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Test",
        )

        with pytest.raises(InstagramError) as exc_info:
            await send_instagram_comment(comment)

        assert exc_info.value.status_code == 429

    @pytest.mark.asyncio
    async def test_send_comment_server_error(self, mock_env_vars, mock_httpx_client):
        """Test Instagram API error (500)"""
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_httpx_client.post.return_value = mock_response

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Test",
        )

        with pytest.raises(InstagramError) as exc_info:
            await send_instagram_comment(comment)

        assert exc_info.value.status_code == 500

    @pytest.mark.asyncio
    async def test_send_comment_missing_env_var(self, mock_httpx_client):
        """Test missing environment variables"""
        # Remove env vars
        os.environ.pop("INSTAGRAM_BUSINESS_ACCOUNT_ID", None)
        os.environ.pop("INSTAGRAM_ACCESS_TOKEN", None)

        comment = InstagramComment(
            media_id="987654321",
            comment_text="Test",
        )

        with pytest.raises(ValueError, match="INSTAGRAM_BUSINESS_ACCOUNT_ID"):
            await send_instagram_comment(comment)


class TestSendInstagramDirect:
    """Test send_instagram_direct function"""

    @pytest.mark.asyncio
    async def test_send_direct_message_success(self, mock_env_vars, mock_httpx_client):
        """Test sending direct message successfully"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"messages": [{"id": "message_123"}]}
        mock_httpx_client.post.return_value = mock_response

        result = await send_instagram_direct(
            recipient_id="recipient_456",
            message_text="Hello via DM!",
        )

        assert result["message_id"] == "message_123"
        mock_httpx_client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_direct_message_unauthorized(
        self, mock_env_vars, mock_httpx_client
    ):
        """Test sending DM with invalid token"""
        mock_response = MagicMock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_httpx_client.post.return_value = mock_response

        with pytest.raises(InstagramError) as exc_info:
            await send_instagram_direct(
                recipient_id="recipient_456",
                message_text="Test",
            )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_send_direct_message_missing_env(self, mock_httpx_client):
        """Test missing environment variable"""
        os.environ.pop("INSTAGRAM_ACCESS_TOKEN", None)

        with pytest.raises(ValueError, match="INSTAGRAM_ACCESS_TOKEN"):
            await send_instagram_direct(
                recipient_id="recipient_456",
                message_text="Test",
            )


class TestInstagramError:
    """Test InstagramError custom exception"""

    def test_instagram_error_creation(self):
        """Test creating InstagramError"""
        error = InstagramError("Test error", 404)
        assert error.message == "Test error"
        assert error.status_code == 404
        assert str(error) == "Test error"
