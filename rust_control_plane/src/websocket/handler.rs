use axum::{
    extract::{
        ws::{WebSocket, Message},
        State, WebSocketUpgrade,
    },
    response::IntoResponse,
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
    ws.on_upgrade(|socket| handle_socket(socket, state))
}

async fn handle_socket(socket: WebSocket, state: AppState) {
    // Generate a unique ID for this connection
    let user_id = Uuid::new_v4();

    // Connect to the hub
    let mut rx = match state.websocket_hub.connect(user_id).await {
        Ok(receiver) => receiver,
        Err(_) => {
            tracing::error!("Failed to connect user {:?} to WebSocket hub", user_id);
            return;
        }
    };

    // Increment WebSocket connection gauge
    inc_websocket_connections();

    tracing::info!("WebSocket client connected: {:?}", user_id);

    // Split the socket into sender and receiver
    let (mut sender, mut receiver) = socket.split();

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
