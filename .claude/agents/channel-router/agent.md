# Channel Router Brain Agent

## Purpose

The Channel Router brain agent analyzes incoming messages and recommends the optimal communication channel for responses based on:

- Message content and context
- User preferences and history
- Channel-specific capabilities
- Urgency and sensitivity of the message
- Time of day and user availability

## Decision Logic

### Channel Capabilities

| Channel | Best For | Limitations |
|---------|----------|-------------|
| **WhatsApp** | Quick responses, informal conversations, mobile users | 160 char limit for initial messages, requires phone number |
| **Instagram** | Visual content, brand interactions, younger demographics | Limited for complex discussions, no file attachments |
| **Email** | Formal communications, detailed explanations, file attachments, threading | Slower response times, may be less frequently checked |

### Routing Factors

1. **Content Analysis**
   - Length: Long messages → Email
   - Complexity: Technical explanations → Email
   - Visual content: Images/videos → Instagram/WhatsApp

2. **User Context**
   - Historical response rates per channel
   - Last successful contact channel
   - User preferences (if known)

3. **Urgency**
   - Urgent: WhatsApp (instant delivery)
   - Non-urgent: Email (can be processed later)

4. **Time of Day**
   - Business hours: All channels available
   - After hours: WhatsApp (mobile) or Email (async)

## API Contract

### Input

```python
{
    "message": {
        "content": str,
        "channel": str,  # Original channel
        "sender": str,
        "timestamp": datetime,
        "attachments": list[str]
    },
    "user_context": {
        "previous_channels": list[str],
        "response_rates": dict[str, float],
        "preferences": dict[str, any]
    }
}
```

### Output

```python
{
    "recommended_channel": str,  # "whatsapp" | "instagram" | "email"
    "confidence": float,  # 0.0 to 1.0
    "reasoning": str,
    "alternatives": list[{
        "channel": str,
        "confidence": float,
        "reason": str
    }]
}
```

## Examples

### Example 1: Long Technical Question

**Input:**
```python
{
    "message": {
        "content": "I'm having trouble configuring the API integration. The documentation says to use POST /api/webhook but I'm getting a 405 Method Not Allowed error. Here's the full request payload...",
        "channel": "whatsapp",
        "sender": "+1234567890"
    }
}
```

**Output:**
```python
{
    "recommended_channel": "email",
    "confidence": 0.9,
    "reasoning": "Long technical explanation requires detailed response with code examples. Email allows for threaded discussion and file attachments (screenshots, logs).",
    "alternatives": [
        {"channel": "whatsapp", "confidence": 0.3, "reason": "User initiated on WhatsApp, but limited for technical support"}
    ]
}
```

### Example 2: Quick Status Check

**Input:**
```python
{
    "message": {
        "content": "Is my order ready?",
        "channel": "instagram",
        "sender": "@user123"
    }
}
```

**Output:**
```python
{
    "recommended_channel": "instagram",
    "confidence": 0.85,
    "reasoning": "Quick question, user initiated on Instagram. Fast response preferred.",
    "alternatives": [
        {"channel": "whatsapp", "confidence": 0.7, "reason": "Also good for quick responses if user has WhatsApp linked"}
    ]
}
```

## Implementation Status

**Current Phase:** MVP Stub
- Returns original channel with confidence 50%
- No sophisticated routing logic yet
- TODO: Implement content analysis, user context tracking, ML-based prediction

**Future Enhancements:**
- ML model for channel prediction based on historical data
- A/B testing to optimize routing decisions
- Real-time feedback loop from response rates
- Integration with user preference settings

## Integration Points

1. **Webhook Processing:** Called when new message arrives
2. **Response Recommendations:** Suggests channel for outgoing responses
3. **Analytics:** Tracks routing decision accuracy
4. **User Settings:** Allows manual channel override

## Metrics

- `channel_router_recommendation_total`: Number of routing recommendations made
- `channel_router_recommendation_accepted`: Number of recommendations accepted by user
- `channel_router_response_rate_{channel}`: Response rate per recommended channel
- `channel_router_confidence_distribution`: Distribution of confidence scores

## Configuration

```python
# Minimum confidence threshold for automatic routing
MIN_CONFIDENCE_THRESHOLD = 0.7

# Fallback channel if confidence is below threshold
FALLBACK_CHANNEL = "email"

# Channel priorities (if multiple channels have equal confidence)
CHANNEL_PRIORITY = ["whatsapp", "instagram", "email"]
```

## References

- MasterMind Framework Phase 18: Multi-channel Gateway
- Brain #7 Critical Evaluation Protocol
- Channel-specific capability matrix
