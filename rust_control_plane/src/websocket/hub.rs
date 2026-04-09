use dashmap::DashMap;
use tokio::sync::{mpsc, broadcast, Mutex};
use std::sync::Arc;
use uuid::Uuid;
use serde::{Deserialize, Serialize};
use serde_json::Value;
use chrono::Utc;
use crate::websocket::ghost_mode::{GhostModeBuffer, StoredEvent, BrainEventType};

const MAX_CONNECTIONS: usize = 2000; // Brain #7 Condition #3
const CHANNEL_BUFFER: usize = 256;    // Brain #7 Condition #2

pub type UserId = Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum ClientMessage {
    BrainStarted(BrainStartedEvent),
    BrainCompleted(BrainCompletedEvent),
    BrainFailed(BrainFailedEvent),
    BrainRouted(BrainRoutedEvent),
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainStartedEvent {
    pub brain_id: String,
    pub trace_id: String,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainCompletedEvent {
    pub brain_id: String,
    pub trace_id: String,
    pub outcome: String,
    pub duration_ms: u64,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainFailedEvent {
    pub brain_id: String,
    pub trace_id: String,
    pub error: String,
    pub timestamp: i64,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainRoutedEvent {
    pub brain_id: String,
    pub from_brain: String,
    pub to_brain: String,
    pub trace_id: String,
    pub timestamp: i64,
}

#[derive(Debug, Clone)]
pub struct SystemEvent {
    pub event_type: String,
    pub payload: Value,
}

pub struct WebSocketHub {
    connections: Arc<DashMap<UserId, mpsc::Sender<ClientMessage>>>,
    global_events: broadcast::Sender<SystemEvent>,
    active_count: Arc<Mutex<usize>>,
    ghost_buffer: Arc<GhostModeBuffer>,
}

impl WebSocketHub {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(1000);
        Self {
            connections: Arc::new(DashMap::new()),
            global_events: tx,
            active_count: Arc::new(Mutex::new(0)),
            ghost_buffer: Arc::new(GhostModeBuffer::new()),
        }
    }

    pub async fn connect(&self, user_id: UserId) -> Result<(mpsc::Receiver<ClientMessage>, Vec<StoredEvent>), &'static str> {
        let mut count = self.active_count.lock().await;
        if *count >= MAX_CONNECTIONS {
            tracing::warn!("Connection rejected: {}/{} max connections", *count, MAX_CONNECTIONS);
            return Err("Max connections exceeded (2000 limit)");
        }
        *count += 1;
        tracing::info!("Connection accepted: {}/{} max connections", *count, MAX_CONNECTIONS);

        let (tx, rx) = mpsc::channel(CHANNEL_BUFFER);
        self.connections.insert(user_id, tx);

        // Get replay from ghost buffer
        let replay = self.ghost_buffer.replay().await;

        Ok((rx, replay))
    }

    pub async fn disconnect(&self, user_id: UserId) {
        self.connections.remove(&user_id);
        let mut count = self.active_count.lock().await;
        *count = count.saturating_sub(1);
    }

    pub async fn broadcast(&self, event: ClientMessage) {
        // Convert to StoredEvent and push to ghost buffer
        let stored_event = self.client_message_to_stored(event.clone());
        self.ghost_buffer.push(stored_event).await;

        let message_json = match serde_json::to_string(&event) {
            Ok(json) => json,
            Err(e) => {
                tracing::error!("Failed to serialize event: {}", e);
                return;
            }
        };

        // Broadcast to all connected clients
        for entry in self.connections.iter() {
            if let Err(e) = entry.value().send(event.clone()).await {
                tracing::error!("Failed to send message to client {:?}: {}", entry.key(), e);
            }
        }

        // Also broadcast to global event stream
        let system_event = SystemEvent {
            event_type: match event {
                ClientMessage::BrainStarted(_) => "brain_started".to_string(),
                ClientMessage::BrainCompleted(_) => "brain_completed".to_string(),
                ClientMessage::BrainFailed(_) => "brain_failed".to_string(),
                ClientMessage::BrainRouted(_) => "brain_routed".to_string(),
            },
            payload: serde_json::to_value(&message_json).unwrap_or(Value::Null),
        };

        let _ = self.global_events.send(system_event);
    }

    fn client_message_to_stored(&self, event: ClientMessage) -> StoredEvent {
        let (event_type, payload) = match event {
            ClientMessage::BrainStarted(e) => (
                BrainEventType::BrainStarted,
                serde_json::to_value(e).unwrap_or(Value::Null),
            ),
            ClientMessage::BrainCompleted(e) => (
                BrainEventType::BrainCompleted,
                serde_json::to_value(e).unwrap_or(Value::Null),
            ),
            ClientMessage::BrainFailed(e) => (
                BrainEventType::BrainFailed,
                serde_json::to_value(e).unwrap_or(Value::Null),
            ),
            ClientMessage::BrainRouted(e) => (
                BrainEventType::BrainRouted,
                serde_json::to_value(e).unwrap_or(Value::Null),
            ),
        };

        StoredEvent {
            id: Uuid::new_v4(),
            event_type,
            payload,
            created_at: Utc::now(),
        }
    }

    pub async fn get_connection_count(&self) -> usize {
        *self.active_count.lock().await
    }

    pub fn subscribe_global_events(&self) -> broadcast::Receiver<SystemEvent> {
        self.global_events.subscribe()
    }

    pub fn ghost_buffer(&self) -> &GhostModeBuffer {
        &self.ghost_buffer
    }
}

impl Default for WebSocketHub {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_hub_creation() {
        let hub = WebSocketHub::new();
        assert_eq!(hub.get_connection_count().await, 0);
    }

    #[tokio::test]
    async fn test_connection_limit() {
        let hub = WebSocketHub::new();

        // Should allow up to MAX_CONNECTIONS
        for i in 0..MAX_CONNECTIONS {
            let user_id = Uuid::new_v4();
            let result = hub.connect(user_id).await;
            assert!(result.is_ok(), "Connection {} failed", i);
        }

        // Should reject the (MAX_CONNECTIONS + 1)th connection
        let extra_user = Uuid::new_v4();
        assert!(hub.connect(extra_user).await.is_err());
    }

    #[tokio::test]
    async fn test_bounded_channel() {
        let hub = WebSocketHub::new();
        let user_id = Uuid::new_v4();

        let (mut rx, _replay) = hub.connect(user_id).await.unwrap();

        // Send CHANNEL_BUFFER + 1 messages
        let event = ClientMessage::BrainStarted(BrainStartedEvent {
            brain_id: "test_brain".to_string(),
            trace_id: "test_trace".to_string(),
            timestamp: chrono::Utc::now().timestamp(),
        });

        // The bounded channel should buffer up to CHANNEL_BUFFER messages
        for _ in 0..CHANNEL_BUFFER {
            hub.broadcast(event.clone()).await;
        }

        // Verify we can receive the messages
        for _ in 0..CHANNEL_BUFFER {
            rx.recv().await.unwrap();
        }

        // Channel should be empty now
        assert!(rx.try_recv().is_err());
    }
}
