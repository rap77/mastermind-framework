use axum::{
    extract::{
        ws::{WebSocket, Message},
        State, WebSocketUpgrade,
    },
    response::IntoResponse,
    http::StatusCode,
};
use futures_util::{stream::StreamExt, SinkExt};
use uuid::Uuid;
use crate::state::AppState;
use crate::websocket::ClientMessage;
use crate::metrics::{inc_websocket_connections, dec_websocket_connections};

pub async fn websocket_handler(
    ws: WebSocketUpgrade,
    State(state): State<AppState>,
) -> impl IntoResponse {
    // Connection limit is enforced in WebSocketHub::connect() with proper mutex locking
    // This avoids race conditions from checking here before the upgrade
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(socket: WebSocket, state: AppState) {
    // Generate a unique ID for this connection
    let user_id = Uuid::new_v4();

    // Connect to the hub (enforces MAX_CONNECTIONS limit)
    let (mut rx, replay) = match state.websocket_hub.connect(user_id).await {
        Ok(result) => result,
        Err(e) => {
            tracing::warn!("Connection rejected for user {:?}: {}", user_id, e);
            // Close the connection immediately - limit exceeded
            let mut socket = socket;
            let _ = socket.close().await;
            return;
        }
    };

    // Increment WebSocket connection gauge
    inc_websocket_connections();

    // Split the socket into sender and receiver
    let (mut sender, mut receiver) = socket.split();

    // Send replay events first
    for stored_event in replay {
        let client_message = match stored_event.event_type {
            crate::websocket::ghost_mode::BrainEventType::BrainStarted => {
                serde_json::from_value(stored_event.payload)
                    .ok()
                    .map(ClientMessage::BrainStarted)
            }
            crate::websocket::ghost_mode::BrainEventType::BrainCompleted => {
                serde_json::from_value(stored_event.payload)
                    .ok()
                    .map(ClientMessage::BrainCompleted)
            }
            crate::websocket::ghost_mode::BrainEventType::BrainFailed => {
                serde_json::from_value(stored_event.payload)
                    .ok()
                    .map(ClientMessage::BrainFailed)
            }
            crate::websocket::ghost_mode::BrainEventType::BrainRouted => {
                serde_json::from_value(stored_event.payload)
                    .ok()
                    .map(ClientMessage::BrainRouted)
            }
        };

        if let Some(msg) = client_message {
            if let Ok(json) = serde_json::to_string(&msg) {
                if sender.send(Message::Text(json.into())).await.is_err() {
                    tracing::error!("Failed to send replay event to client");
                    dec_websocket_connections();
                    return;
                }
            }
        }
    }

    tracing::info!("WebSocket client connected: {:?}", user_id);

    // Task to receive messages from the hub and send to the client
    let mut send_task = tokio::spawn(async move {
        while let Some(msg) = rx.recv().await {
            let json = match serde_json::to_string(&msg) {
                Ok(json) => json,
                Err(e) => {
                    tracing::error!("Failed to serialize message: {}", e);
                    continue;
                }
            };

            if sender.send(Message::Text(json.into())).await.is_err() {
                break;
            }
        }
    });

    // Task to receive messages from the client
    let mut recv_task = tokio::spawn(async move {
        while let Some(Ok(msg)) = receiver.next().await {
            match msg {
                Message::Text(text) => {
                    tracing::debug!("Received message from client: {}", text);
                    // Handle client messages if needed
                }
                Message::Close(_) => {
                    tracing::info!("Client {:?} requested close", user_id);
                    break;
                }
                _ => {}
            }
        }
    });

    // Wait for either task to complete
    tokio::select! {
        _ = &mut send_task => {
            recv_task.abort();
        }
        _ = &mut recv_task => {
            send_task.abort();
        }
    }

    // Disconnect from the hub
    state.websocket_hub.disconnect(user_id).await;
    dec_websocket_connections();
    tracing::info!("WebSocket client disconnected: {:?}", user_id);
}
