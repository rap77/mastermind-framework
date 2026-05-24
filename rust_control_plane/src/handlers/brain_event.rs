/// Handler for `POST /internal/brain-event`.
///
/// Receives brain lifecycle events from the Python dispatch engine and
/// publishes them to the `BrainStateEvent` broadcast channel for fan-out
/// to all connected `/ws/events` WebSocket clients.
///
/// This endpoint is internal — it should not be exposed publicly.
/// In production, restrict it via network policy / ingress rules.
use axum::{
    extract::State,
    http::StatusCode,
    response::IntoResponse,
    Json,
};
use crate::state::AppState;
use crate::websocket::brain_state_event::BrainStateEvent;

/// Receive a BrainStateEvent from Python and publish it to the WS fan-out.
///
/// # Errors
/// Returns 400 if the JSON body is malformed (handled by Axum extractor).
pub async fn brain_event_handler(
    State(state): State<AppState>,
    Json(event): Json<BrainStateEvent>,
) -> impl IntoResponse {
    tracing::info!(
        trace_id = %event.trace_id,
        brain_id = %event.brain_id,
        status = ?event.status,
        "Received brain event from Python"
    );

    let receivers = state.websocket_hub.publish_brain_event(event);

    tracing::debug!("Brain event published to {} WebSocket subscribers", receivers);

    StatusCode::NO_CONTENT
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::websocket::WebSocketHub;
    use std::sync::Arc;

    /// Verifies the hub publish/subscribe logic used by the handler.
    ///
    /// The full HTTP handler path (Axum extractor → State → handler) requires a
    /// real PgPool which is not available in unit tests.  The hub round-trip is
    /// the critical behaviour; the HTTP plumbing is covered by integration tests.
    #[tokio::test]
    async fn test_brain_event_publish_subscribe() {
        let hub = Arc::new(WebSocketHub::new());
        let mut rx = hub.subscribe_brain_events();

        let event = BrainStateEvent::dispatched("trace-handler-test", "brain-5");
        let receivers = hub.publish_brain_event(event);
        // One receiver is subscribed
        assert_eq!(receivers, 1);

        let received = rx.recv().await.unwrap();
        assert_eq!(received.trace_id, "trace-handler-test");
        assert_eq!(received.brain_id, "brain-5");
    }

    /// Publishing with no subscribers returns 0 (not an error).
    #[tokio::test]
    async fn test_brain_event_no_subscribers_ok() {
        let hub = Arc::new(WebSocketHub::new());
        let event = BrainStateEvent::completed("trace-no-sub", "brain-2");
        let receivers = hub.publish_brain_event(event);
        assert_eq!(receivers, 0);
    }
}
