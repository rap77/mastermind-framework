"""Tests for canonical inbound multi-channel event normalization."""

from __future__ import annotations

import pytest

from routers.canonical_events import CanonicalInboundEvent, normalize_inbound_event


def test_normalize_whatsapp_text_webhook_to_canonical_event() -> None:
    """WhatsApp webhook payloads normalize to the canonical internal contract."""
    payload = {
        "entry": [
            {
                "changes": [
                    {
                        "value": {
                            "messages": [
                                {
                                    "from": "15551234567",
                                    "to": "15557654321",
                                    "id": "wamid.example123",
                                    "timestamp": "1712829600",
                                    "text": {"body": "Hello from WhatsApp"},
                                }
                            ]
                        }
                    }
                ]
            }
        ]
    }

    event = normalize_inbound_event("whatsapp", payload)

    assert isinstance(event, CanonicalInboundEvent)
    assert event.channel == "whatsapp"
    assert event.external_message_id == "wamid.example123"
    assert event.sender_id == "15551234567"
    assert event.recipient_id == "15557654321"
    assert event.message_type == "text"
    assert event.content_text == "Hello from WhatsApp"
    assert event.occurred_at_epoch_ms == 1712829600000


def test_normalize_instagram_comment_webhook_to_canonical_event() -> None:
    """Instagram comment payloads normalize to the canonical contract."""
    payload = {
        "changes": [
            {
                "value": {
                    "id": "comment_123",
                    "media": {
                        "id": "media_456",
                        "image_url": "https://instagram.example/image.jpg",
                    },
                    "from": {"username": "jane_doe"},
                    "text": "Nice post!",
                    "timestamp": 1712829700,
                }
            }
        ]
    }

    event = normalize_inbound_event("instagram", payload)

    assert event.channel == "instagram"
    assert event.external_message_id == "comment_123"
    assert event.sender_id == "jane_doe"
    assert event.recipient_id == "media_456"
    assert event.message_type == "comment"
    assert event.content_text == "Nice post!"
    assert event.media_url == "https://instagram.example/image.jpg"
    assert event.occurred_at_epoch_ms == 1712829700000
    assert event.metadata["webhook_type"] == "comment"


def test_normalize_sendgrid_email_webhook_to_canonical_event() -> None:
    """SendGrid-style email webhook payloads normalize to the canonical contract."""
    payload = {
        "events": [
            {
                "sg_message_id": "sendgrid-msg-001",
                "email": "sender@example.com",
                "to": "ops@example.com",
                "subject": "Hello",
                "text": "Plain text body",
                "timestamp": 1712829800,
                "headers": {"References": "<thread@example.com>"},
            }
        ]
    }

    event = normalize_inbound_event("email", payload)

    assert event.channel == "email"
    assert event.external_message_id == "sendgrid-msg-001"
    assert event.sender_id == "sender@example.com"
    assert event.recipient_id == "ops@example.com"
    assert event.message_type == "email"
    assert event.content_text == "Plain text body"
    assert event.thread_id == "<thread@example.com>"
    assert event.occurred_at_epoch_ms == 1712829800000
    assert event.metadata["provider"] == "sendgrid"


def test_normalize_fallback_payload_uses_synthetic_message_id() -> None:
    """Fallback payloads still normalize deterministically for current bridge paths."""
    payload = {
        "to": "recipient@example.com",
        "subject": "Outbound-style payload",
        "body": "Hello bridge",
    }

    event = normalize_inbound_event(
        "email",
        payload,
        sender_id="bridge-user",
        message_type="email",
    )

    assert event.channel == "email"
    assert event.external_message_id.startswith("synthetic:email:")
    assert event.sender_id == "bridge-user"
    assert event.recipient_id == "recipient@example.com"
    assert event.content_text == "Hello bridge"


def test_normalize_rejects_unsupported_channel() -> None:
    """Unsupported channels fail fast with a descriptive error."""
    with pytest.raises(ValueError, match="Unsupported channel"):
        normalize_inbound_event("sms", {})
