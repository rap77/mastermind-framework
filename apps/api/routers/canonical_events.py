"""Canonical inbound multi-channel event normalization.

This module defines a backend-authoritative event shape for inbound
multi-channel payloads and provides normalization helpers that translate raw
provider payloads (or narrower fallback payloads already flowing through the
system) into that contract.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class CanonicalInboundEvent(BaseModel):
    """Canonical internal representation of an inbound multi-channel event."""

    channel: Literal["whatsapp", "instagram", "email"]
    external_message_id: str
    sender_id: str
    recipient_id: str | None = None
    message_type: str
    content_text: str | None = None
    media_url: str | None = None
    thread_id: str | None = None
    occurred_at_epoch_ms: int | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


def normalize_inbound_event(
    channel: str,
    payload: str | dict[str, Any],
    *,
    sender_id: str | None = None,
    message_type: str | None = None,
) -> CanonicalInboundEvent:
    """Normalize an inbound payload into the canonical event contract.

    Args:
        channel: Channel name (`whatsapp`, `instagram`, or `email`).
        payload: Raw JSON string or parsed dict payload.
        sender_id: Optional fallback sender identifier from the outer transport
            envelope.
        message_type: Optional fallback message type from the outer transport
            envelope.

    Returns:
        Canonical inbound event.

    Raises:
        ValueError: If the channel is unsupported or the payload string is not
            valid JSON.
    """
    parsed_payload = _coerce_payload_dict(payload)
    normalized_channel = channel.strip().lower()

    if normalized_channel == "whatsapp":
        return _normalize_whatsapp_event(
            parsed_payload,
            sender_id=sender_id,
            message_type=message_type,
        )
    if normalized_channel == "instagram":
        return _normalize_instagram_event(
            parsed_payload,
            sender_id=sender_id,
            message_type=message_type,
        )
    if normalized_channel == "email":
        return _normalize_email_event(
            parsed_payload,
            sender_id=sender_id,
            message_type=message_type,
        )

    raise ValueError(
        "Unsupported channel for canonical normalization: "
        f"{channel!r}. Expected whatsapp, instagram, or email."
    )


def _coerce_payload_dict(payload: str | dict[str, Any]) -> dict[str, Any]:
    """Return a payload as a dictionary."""
    if isinstance(payload, dict):
        return payload

    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid JSON payload for canonical normalization: {exc}"
        ) from exc

    if not isinstance(decoded, dict):
        raise ValueError("Canonical normalization requires a JSON object payload")

    return decoded


def _mapping_or_empty(value: Any) -> dict[str, Any]:
    """Return a mapping-like payload block as a typed dict or an empty dict."""
    return value if isinstance(value, dict) else {}


def _normalize_whatsapp_event(
    payload: dict[str, Any],
    *,
    sender_id: str | None,
    message_type: str | None,
) -> CanonicalInboundEvent:
    """Normalize a WhatsApp inbound payload."""
    message = _dig(
        payload, "entry", 0, "changes", 0, "value", "messages", 0, default=None
    )
    if isinstance(message, dict):
        detected_type = _detect_whatsapp_message_type(message)
        content_text, media_url = _extract_whatsapp_content(message, detected_type)
        external_message_id = _require_str(
            message.get("id"),
            default=_synthetic_message_id("whatsapp", payload),
        )
        sender = _require_str(message.get("from"), default=sender_id or "unknown")
        recipient = _optional_str(message.get("to"))
        timestamp_ms = _normalize_timestamp_to_ms(message.get("timestamp"))
        return CanonicalInboundEvent(
            channel="whatsapp",
            external_message_id=external_message_id,
            sender_id=sender,
            recipient_id=recipient,
            message_type=detected_type,
            content_text=content_text,
            media_url=media_url,
            occurred_at_epoch_ms=timestamp_ms,
            metadata={},
        )

    fallback_type = (
        _optional_str(payload.get("message_type")) or message_type or "unknown"
    )
    fallback_content = _optional_str(payload.get("text")) or _optional_str(
        payload.get("body")
    )
    fallback_media_url = _optional_str(payload.get("media_url"))
    return CanonicalInboundEvent(
        channel="whatsapp",
        external_message_id=_require_str(
            payload.get("message_id"),
            default=_synthetic_message_id("whatsapp", payload),
        ),
        sender_id=_require_str(
            payload.get("from"),
            default=sender_id or _optional_str(payload.get("to")) or "unknown",
        ),
        recipient_id=_optional_str(payload.get("to")),
        message_type=fallback_type,
        content_text=fallback_content,
        media_url=fallback_media_url,
        occurred_at_epoch_ms=None,
        metadata={},
    )


def _normalize_instagram_event(
    payload: dict[str, Any],
    *,
    sender_id: str | None,
    message_type: str | None,
) -> CanonicalInboundEvent:
    """Normalize an Instagram inbound payload."""
    value = _dig(payload, "changes", 0, "value", default=None)
    if isinstance(value, dict):
        webhook_type = (
            "message" if value.get("conversation_id") is not None else "comment"
        )
        media = _mapping_or_empty(value.get("media"))
        from_block = _mapping_or_empty(value.get("from"))
        return CanonicalInboundEvent(
            channel="instagram",
            external_message_id=_require_str(
                value.get("id"),
                default=_synthetic_message_id("instagram", payload),
            ),
            sender_id=_require_str(
                from_block.get("username"),
                default=sender_id or "unknown",
            ),
            recipient_id=_optional_str(value.get("conversation_id"))
            or _optional_str(media.get("id")),
            message_type=message_type or webhook_type,
            content_text=_optional_str(value.get("text")),
            media_url=_optional_str(media.get("image_url")),
            thread_id=_optional_str(value.get("parent_comment_id")),
            occurred_at_epoch_ms=_normalize_timestamp_to_ms(value.get("timestamp")),
            metadata={
                "media_id": _optional_str(media.get("id")),
                "webhook_type": webhook_type,
            },
        )

    recipient_id = _optional_str(payload.get("recipient_id")) or _optional_str(
        payload.get("media_id")
    )
    fallback_type = message_type or ("message" if recipient_id else "comment")
    return CanonicalInboundEvent(
        channel="instagram",
        external_message_id=_require_str(
            payload.get("message_id") or payload.get("comment_id"),
            default=_synthetic_message_id("instagram", payload),
        ),
        sender_id=_require_str(payload.get("from"), default=sender_id or "unknown"),
        recipient_id=recipient_id,
        message_type=fallback_type,
        content_text=_optional_str(payload.get("message_text"))
        or _optional_str(payload.get("comment_text")),
        media_url=_optional_str(payload.get("attachment_id")),
        occurred_at_epoch_ms=None,
        metadata={},
    )


def _normalize_email_event(
    payload: dict[str, Any],
    *,
    sender_id: str | None,
    message_type: str | None,
) -> CanonicalInboundEvent:
    """Normalize an email inbound payload across supported providers."""
    if isinstance(payload.get("events"), list):
        raw_event = payload["events"][0] if payload["events"] else {}
        event = raw_event if isinstance(raw_event, dict) else {}
        headers = _mapping_or_empty(event.get("headers"))
        return CanonicalInboundEvent(
            channel="email",
            external_message_id=_require_str(
                event.get("sg_message_id"),
                default=_synthetic_message_id("email", payload),
            ),
            sender_id=_require_str(
                event.get("email") or event.get("from"),
                default=sender_id or "unknown",
            ),
            recipient_id=_optional_str(event.get("to_email"))
            or _optional_str(event.get("to")),
            message_type=message_type or "email",
            content_text=_optional_str(event.get("text"))
            or _optional_str(event.get("html")),
            thread_id=_extract_email_thread_id(headers),
            occurred_at_epoch_ms=_normalize_timestamp_to_ms(event.get("timestamp")),
            metadata={
                "provider": "sendgrid",
                "subject": _optional_str(event.get("subject")),
            },
        )

    event_data = payload.get("event-data")
    if isinstance(event_data, dict):
        message = _mapping_or_empty(event_data.get("message"))
        headers = _mapping_or_empty(message.get("headers"))
        return CanonicalInboundEvent(
            channel="email",
            external_message_id=_require_str(
                _dig(message, "headers", "message-id", default=None)
                or message.get("message_id"),
                default=_synthetic_message_id("email", payload),
            ),
            sender_id=_require_str(message.get("from"), default=sender_id or "unknown"),
            recipient_id=_optional_str(message.get("to")),
            message_type=message_type or "email",
            content_text=_optional_str(message.get("body-plain"))
            or _optional_str(message.get("body-html")),
            thread_id=_extract_email_thread_id(headers),
            occurred_at_epoch_ms=_normalize_timestamp_to_ms(
                event_data.get("timestamp")
            ),
            metadata={
                "provider": "mailgun",
                "subject": _optional_str(message.get("subject")),
            },
        )

    if payload.get("MessageID") is not None or payload.get("From") is not None:
        headers = _mapping_or_empty(payload.get("Headers"))
        return CanonicalInboundEvent(
            channel="email",
            external_message_id=_require_str(
                payload.get("MessageID"),
                default=_synthetic_message_id("email", payload),
            ),
            sender_id=_require_str(payload.get("From"), default=sender_id or "unknown"),
            recipient_id=_optional_str(payload.get("To")),
            message_type=message_type or "email",
            content_text=_optional_str(payload.get("TextBody"))
            or _optional_str(payload.get("HtmlBody")),
            thread_id=_optional_str(headers.get("References"))
            or _optional_str(headers.get("In-Reply-To")),
            occurred_at_epoch_ms=_normalize_timestamp_to_ms(payload.get("Timestamp")),
            metadata={
                "provider": "postmark",
                "subject": _optional_str(payload.get("Subject")),
            },
        )

    return CanonicalInboundEvent(
        channel="email",
        external_message_id=_require_str(
            payload.get("message_id"),
            default=_synthetic_message_id("email", payload),
        ),
        sender_id=_require_str(
            payload.get("from_email") or payload.get("from"),
            default=sender_id or "unknown",
        ),
        recipient_id=_optional_str(payload.get("to_email"))
        or _optional_str(payload.get("to")),
        message_type=message_type or "email",
        content_text=_optional_str(payload.get("plain_text"))
        or _optional_str(payload.get("body"))
        or _optional_str(payload.get("html_body")),
        thread_id=_optional_str(payload.get("thread_id"))
        or _optional_str(payload.get("in_reply_to")),
        occurred_at_epoch_ms=None,
        metadata={"subject": _optional_str(payload.get("subject"))},
    )


def _detect_whatsapp_message_type(message: dict[str, Any]) -> str:
    """Detect the WhatsApp message type from a provider payload."""
    for key in (
        "text",
        "image",
        "audio",
        "document",
        "video",
        "location",
        "contacts",
    ):
        if message.get(key) is not None:
            return key

    interactive = message.get("interactive")
    if isinstance(interactive, dict):
        interactive_type = _optional_str(interactive.get("type")) or "unknown"
        return f"interactive_{interactive_type}"

    return "unknown"


def _extract_whatsapp_content(
    message: dict[str, Any], message_type: str
) -> tuple[str | None, str | None]:
    """Extract text/media fields from a normalized WhatsApp message payload."""
    if message_type == "text":
        text_block = _mapping_or_empty(message.get("text"))
        return _optional_str(text_block.get("body")), None

    if message_type in {"image", "document", "video"}:
        media_block = message.get(message_type)
        if isinstance(media_block, dict):
            return _optional_str(media_block.get("caption")), _optional_str(
                media_block.get("url")
            )
        return None, None

    if message_type == "audio":
        audio_block = message.get("audio")
        if isinstance(audio_block, dict):
            return None, _optional_str(audio_block.get("url"))
        return None, None

    if message_type == "location":
        location_block = _mapping_or_empty(message.get("location"))
        latitude = location_block.get("latitude")
        longitude = location_block.get("longitude")
        if latitude is not None and longitude is not None:
            return f"{latitude},{longitude}", None

    return None, None


def _extract_email_thread_id(headers: dict[str, Any]) -> str | None:
    """Extract a thread identifier from email headers."""
    references = _optional_str(headers.get("References"))
    if references:
        return references
    return _optional_str(headers.get("In-Reply-To"))


def _normalize_timestamp_to_ms(raw_value: Any) -> int | None:
    """Normalize heterogeneous timestamps to epoch milliseconds."""
    if raw_value is None:
        return None

    if isinstance(raw_value, (int, float)):
        numeric = int(raw_value)
        return numeric * 1000 if numeric < 1_000_000_000_000 else numeric

    if isinstance(raw_value, str):
        stripped = raw_value.strip()
        if not stripped:
            return None
        if stripped.isdigit():
            numeric = int(stripped)
            return numeric * 1000 if numeric < 1_000_000_000_000 else numeric

        try:
            dt = parsedate_to_datetime(stripped)
        except (TypeError, ValueError, IndexError):
            try:
                dt = datetime.fromisoformat(stripped.replace("Z", "+00:00"))
            except ValueError:
                return None

        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return int(dt.timestamp() * 1000)

    return None


def _optional_str(value: Any) -> str | None:
    """Return a stripped string or None."""
    if not isinstance(value, str):
        return None
    stripped = value.strip()
    return stripped or None


def _require_str(value: Any, *, default: str | None = None) -> str:
    """Return a non-empty string, using a default when needed."""
    normalized = _optional_str(value)
    if normalized:
        return normalized
    if default is not None:
        return default
    raise ValueError("Expected a non-empty string value during canonical normalization")


def _synthetic_message_id(channel: str, payload: dict[str, Any]) -> str:
    """Build a deterministic synthetic message id for fallback envelopes."""
    normalized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:12]
    return f"synthetic:{channel}:{digest}"


def _dig(payload: Any, *path: Any, default: Any = None) -> Any:
    """Safely traverse nested dict/list payloads."""
    current = payload
    for key in path:
        if isinstance(key, int):
            if not isinstance(current, list) or len(current) <= key:
                return default
            current = current[key]
            continue
        if not isinstance(current, dict):
            return default
        current = current.get(key, default)
        if current is default:
            return default
    return current
