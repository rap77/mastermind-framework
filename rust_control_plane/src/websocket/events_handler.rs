/// WebSocket handler for `GET /ws/events`.
///
/// Upgrades the HTTP connection to a WebSocket and streams
/// `BrainStateEvent` messages from the fan-out broadcast channel.
/// Clients receive events in real-time as Python publishes brain lifecycle
/// updates via `POST /internal/brain-event`.
use axum::{
    extract::{State, WebSocketUpgrade},
    response::IntoResponse,
};
use axum::extract::ws::{Message, WebSocket};
use futures_util::{SinkExt, StreamExt};
use crate::state::AppState;

/// Upgrade HTTP → WebSocket for brain state event streaming.
pub async fn ws_events_handler(
    ws: WebSocketUpgrade,
    State(state): State<AppState>,
) -> impl IntoResponse {
    ws.on_upgrade(|socket| handle_events_socket(socket, state))
}

async fn handle_events_socket(socket: WebSocket, state: AppState) {
    let mut rx = state.websocket_hub.subscribe_brain_events();
    let (mut sender, mut receiver) = socket.split();

    tracing::info!("WebSocket /ws/events client connected");

    // Forward brain events to the WebSocket client.
    // Also handle incoming pings / close frames from the client side.
    loop {
        tokio::select! {
            result = rx.recv() => {
                match result {
                    Ok(event) => {
                        let json = match serde_json::to_string(&event) {
                            Ok(j) => j,
                            Err(e) => {
                                tracing::error!("Failed to serialize BrainStateEvent: {}", e);
                                continue;
                            }
                        };
                        if sender.send(Message::Text(json.into())).await.is_err() {
                            // Client disconnected
                            break;
                        }
                    }
                    Err(tokio::sync::broadcast::error::RecvError::Lagged(n)) => {
                        tracing::warn!(
                            "/ws/events client lagged — {} events dropped",
                            n
                        );
                        // Continue receiving — do not close the connection
                    }
                    Err(tokio::sync::broadcast::error::RecvError::Closed) => {
                        tracing::info!("/ws/events broadcast channel closed — disconnecting client");
                        break;
                    }
                }
            }
            msg = receiver.next() => {
                match msg {
                    Some(Ok(Message::Close(_))) | None => {
                        tracing::info!("WebSocket /ws/events client disconnected");
                        break;
                    }
                    Some(Ok(Message::Ping(payload))) => {
                        // Respond to Ping with Pong to keep the connection alive
                        if sender.send(Message::Pong(payload)).await.is_err() {
                            break;
                        }
                    }
                    _ => {}
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::websocket::brain_state_event::BrainStateEvent;

    /// Verifies that a BrainStateEvent published to the hub
    /// is received by a subscriber.
    #[tokio::test]
    async fn test_brain_event_round_trip() {
        use crate::websocket::WebSocketHub;
        use std::sync::Arc;

        let hub = Arc::new(WebSocketHub::new());
        let mut rx = hub.subscribe_brain_events();

        let event = BrainStateEvent::dispatched("trace-001", "brain-1");
        hub.publish_brain_event(event.clone());

        let received = rx.recv().await.unwrap();
        assert_eq!(received.trace_id, "trace-001");
        assert_eq!(received.brain_id, "brain-1");
    }
}
