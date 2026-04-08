use std::collections::VecDeque;
use tokio::sync::Mutex;
use std::sync::Arc;
use uuid::Uuid;
use chrono::{DateTime, Utc};
use serde_json::Value;
use serde::{Deserialize, Serialize};

const GHOST_BUFFER_SIZE: usize = 100;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct StoredEvent {
    pub id: Uuid,
    pub event_type: BrainEventType,
    pub payload: Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum BrainEventType {
    BrainStarted,
    BrainCompleted,
    BrainFailed,
    BrainRouted,
}

pub struct GhostModeBuffer {
    events: Arc<Mutex<VecDeque<StoredEvent>>>,
}

impl GhostModeBuffer {
    pub fn new() -> Self {
        Self {
            events: Arc::new(Mutex::new(VecDeque::with_capacity(GHOST_BUFFER_SIZE))),
        }
    }

    pub async fn push(&self, event: StoredEvent) {
        let mut events = self.events.lock().await;
        if events.len() >= GHOST_BUFFER_SIZE {
            events.pop_front(); // Remove oldest
        }
        events.push_back(event);
    }

    pub async fn replay(&self) -> Vec<StoredEvent> {
        let events = self.events.lock().await;
        events.iter().cloned().collect()
    }

    pub async fn clear(&self) {
        let mut events = self.events.lock().await;
        events.clear();
    }

    pub async fn len(&self) -> usize {
        let events = self.events.lock().await;
        events.len()
    }
}

impl Default for GhostModeBuffer {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::websocket::ClientMessage;

    #[tokio::test]
    async fn test_ghost_buffer_creation() {
        let buffer = GhostModeBuffer::new();
        assert_eq!(buffer.len().await, 0);
    }

    #[tokio::test]
    async fn test_ghost_buffer_push() {
        let buffer = GhostModeBuffer::new();

        let event = StoredEvent {
            id: Uuid::new_v4(),
            event_type: BrainEventType::BrainStarted,
            payload: serde_json::json!({"test": "data"}),
            created_at: Utc::now(),
        };

        buffer.push(event.clone()).await;
        assert_eq!(buffer.len().await, 1);

        let replay = buffer.replay().await;
        assert_eq!(replay.len(), 1);
        assert_eq!(replay[0].id, event.id);
    }

    #[tokio::test]
    async fn test_ghost_buffer_eviction() {
        let buffer = GhostModeBuffer::new();

        // Add 101 events
        for i in 0..=GHOST_BUFFER_SIZE {
            let event = StoredEvent {
                id: Uuid::new_v4(),
                event_type: BrainEventType::BrainStarted,
                payload: serde_json::json!({"index": i}),
                created_at: Utc::now(),
            };
            buffer.push(event).await;
        }

        // Should still have 100 events (oldest evicted)
        assert_eq!(buffer.len().await, GHOST_BUFFER_SIZE);
    }

    #[tokio::test]
    async fn test_ghost_buffer_clear() {
        let buffer = GhostModeBuffer::new();

        let event = StoredEvent {
            id: Uuid::new_v4(),
            event_type: BrainEventType::BrainStarted,
            payload: serde_json::json!({"test": "data"}),
            created_at: Utc::now(),
        };

        buffer.push(event).await;
        assert_eq!(buffer.len().await, 1);

        buffer.clear().await;
        assert_eq!(buffer.len().await, 0);
    }
}
