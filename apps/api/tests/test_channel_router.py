"""Tests for Channel Router service"""

import pytest
from datetime import datetime
from services.channel_router import (
    ChannelRouter,
    MessageContext,
    UserContext,
    RoutingDecision,
    ChannelRecommendation,
    suggest_channel,
    get_channel_router,
)


class TestChannelRouter:
    """Test ChannelRouter service"""

    def test_singleton_instance(self):
        """Test that get_channel_router returns the same instance"""
        router1 = get_channel_router()
        router2 = get_channel_router()
        assert router1 is router2

    def test_suggest_channel_returns_original_channel_mvp(self):
        """Test that MVP stub returns original channel"""
        router = ChannelRouter()
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        decision = router.suggest_channel(msg)

        assert decision.recommended_channel == "whatsapp"
        assert decision.confidence == 0.5
        assert "MVP stub" in decision.reasoning

    def test_suggest_channel_with_whatsapp(self):
        """Test routing for WhatsApp messages"""
        msg = MessageContext(
            content="Quick question", channel="whatsapp", sender="+1234567890"
        )
        decision = suggest_channel(msg)

        assert decision.recommended_channel == "whatsapp"
        assert isinstance(decision.confidence, float)
        assert 0.0 <= decision.confidence <= 1.0

    def test_suggest_channel_with_instagram(self):
        """Test routing for Instagram messages"""
        msg = MessageContext(
            content="Nice post!", channel="instagram", sender="@user123"
        )
        decision = suggest_channel(msg)

        assert decision.recommended_channel == "instagram"
        assert isinstance(decision.confidence, float)

    def test_suggest_channel_with_email(self):
        """Test routing for email messages"""
        msg = MessageContext(
            content="Technical question about API",
            channel="email",
            sender="user@example.com",
        )
        decision = suggest_channel(msg)

        assert decision.recommended_channel == "email"
        assert isinstance(decision.confidence, float)

    def test_suggest_channel_generates_alternatives(self):
        """Test that alternatives are generated for other channels"""
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        decision = suggest_channel(msg)

        assert len(decision.alternatives) == 2  # instagram and email
        alternative_channels = {alt.channel for alt in decision.alternatives}
        assert "instagram" in alternative_channels
        assert "email" in alternative_channels

    def test_alternatives_have_lower_confidence(self):
        """Test that alternative recommendations have lower confidence"""
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        decision = suggest_channel(msg)

        for alt in decision.alternatives:
            assert alt.confidence < decision.confidence
            assert alt.confidence == 0.3  # MVP stub value

    def test_should_use_fallback_with_low_confidence(self):
        """Test fallback logic when confidence is below threshold"""
        router = ChannelRouter()
        low_confidence_decision = RoutingDecision(
            recommended_channel="whatsapp", confidence=0.5, reasoning="Low confidence"
        )

        assert router.should_use_fallback(low_confidence_decision) is True

    def test_should_not_use_fallback_with_high_confidence(self):
        """Test that fallback is not used when confidence is high"""
        router = ChannelRouter()
        high_confidence_decision = RoutingDecision(
            recommended_channel="whatsapp", confidence=0.8, reasoning="High confidence"
        )

        assert router.should_use_fallback(high_confidence_decision) is False

    def test_message_context_with_attachments(self):
        """Test message context with attachments"""
        msg = MessageContext(
            content="Check out this image",
            channel="instagram",
            sender="@user123",
            attachments=["https://example.com/image.jpg"],
        )
        decision = suggest_channel(msg)

        assert isinstance(decision, RoutingDecision)

    def test_message_context_timestamp_defaults_to_now(self):
        """Test that timestamp defaults to current time"""
        before = datetime.now()
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        after = datetime.now()

        assert before <= msg.timestamp <= after

    def test_user_context_with_empty_data(self):
        """Test routing with empty user context"""
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        user_context = UserContext()
        decision = suggest_channel(msg, user_context)

        assert isinstance(decision, RoutingDecision)

    def test_user_context_with_response_rates(self):
        """Test routing with user response rate data"""
        msg = MessageContext(content="Hello", channel="whatsapp", sender="+1234567890")
        user_context = UserContext(response_rates={"whatsapp": 0.8, "email": 0.3})
        decision = suggest_channel(msg, user_context)

        # MVP stub doesn't use user_context yet, but should accept it
        assert isinstance(decision, RoutingDecision)

    def test_routing_decision_model_validation(self):
        """Test that RoutingDecision validates confidence range"""
        with pytest.raises(ValueError):
            RoutingDecision(
                recommended_channel="whatsapp",
                confidence=1.5,
                reasoning="Invalid confidence",
            )

        with pytest.raises(ValueError):
            RoutingDecision(
                recommended_channel="whatsapp",
                confidence=-0.1,
                reasoning="Invalid confidence",
            )

    def test_channel_recommendation_model_validation(self):
        """Test that ChannelRecommendation validates confidence range"""
        with pytest.raises(ValueError):
            ChannelRecommendation(
                channel="whatsapp", confidence=1.1, reason="Invalid confidence"
            )
