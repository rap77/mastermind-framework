"""Channel Router service for optimal channel selection

MVP implementation: Returns original channel with confidence 0.5
Future: Integrate customer preferences, channel metrics, message type compatibility
"""

import structlog
from typing import NamedTuple, Optional
from enum import Enum


logger = structlog.get_logger(__name__)


class Channel(str, Enum):
    """Supported communication channels"""

    WHATSAPP = "whatsapp"
    INSTAGRAM = "instagram"
    EMAIL = "email"


class ChannelSuggestion(NamedTuple):
    """Channel routing recommendation"""

    suggested_channel: str
    confidence: float
    reason: str


def suggest_channel(
    original_channel: str,
    message_type: str = "text",
    customer_id: Optional[str] = None,
) -> ChannelSuggestion:
    """Suggest optimal channel for message delivery

    MVP: Returns original channel with confidence 0.5

    Args:
        original_channel: Channel message arrived on
        message_type: Type of message (text, image, video, etc)
        customer_id: Customer identifier for preference lookup (future)

    Returns:
        ChannelSuggestion with recommended channel and confidence
    """

    # MVP: Return original channel
    suggestion = ChannelSuggestion(
        suggested_channel=original_channel,
        confidence=0.5,
        reason="MVP: returning original channel",
    )

    logger.info(
        "Channel suggestion generated",
        original_channel=original_channel,
        suggested_channel=suggestion.suggested_channel,
        confidence=suggestion.confidence,
        reason=suggestion.reason,
        message_type=message_type,
        customer_id=customer_id,
    )

    return suggestion


async def suggest_channel_async(
    original_channel: str,
    message_type: str = "text",
    customer_id: Optional[str] = None,
) -> ChannelSuggestion:
    """Async version of suggest_channel

    Args:
        original_channel: Channel message arrived on
        message_type: Type of message (text, image, video, etc)
        customer_id: Customer identifier for preference lookup (future)

    Returns:
        ChannelSuggestion with recommended channel and confidence
    """

    return suggest_channel(
        original_channel=original_channel,
        message_type=message_type,
        customer_id=customer_id,
    )
