# Channel Router Brain Agent

## Purpose

Selects the optimal communication channel (WhatsApp, Instagram, Email) based on message context, customer preferences, and channel performance metrics.

## Decision Logic

For MVP (Phase 18-10): Return original channel with confidence 50%.

Future phases will implement:
- Customer channel preferences (stored in database)
- Message type compatibility (some channels support specific message types)
- Channel performance metrics (delivery rate, latency)
- Fallback channels if primary is unavailable

## Examples

### MVP Behavior
```
Input:  trace_id=abc, original_channel=whatsapp
Output: suggested_channel=whatsapp, confidence=0.5
```

### Future: Complex Routing
```
Input:
  - message_type=image
  - customer_id=cust_123
  - customer_preferences={whatsapp: enabled, instagram: enabled, email: disabled}

Output:
  - suggested_channel=whatsapp (supports images)
  - confidence=0.9
  - reason="WhatsApp has 95% delivery rate, supports images, preferred by customer"
```

## Integration

Called from Rust worker after gRPC response:
```rust
let suggested_channel = response.suggested_channel;  // From AI worker
// Could enhance with Channel Router decision
```

## Metrics

- `channel_router_suggestions_total{channel}`: Total suggestions per channel
- `channel_router_fallback_rate`: % of messages needing fallback
- `channel_router_selection_confidence`: Average confidence score

## Brain Conditions

- Brain #7 Condition #4: Channel selection transparent and auditable
  - Always log suggestion, confidence, and reasoning
  - Include in trace for observability

## Future Work

- Integrate with customer preference database
- Add A/B testing for new routing strategies
- Machine learning based on success metrics
