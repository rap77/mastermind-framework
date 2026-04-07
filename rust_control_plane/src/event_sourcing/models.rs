use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use uuid::Uuid;
use chrono::{DateTime, Utc};

#[derive(Debug, Clone, Serialize, Deserialize, FromRow)]
pub struct BrainEvent {
    pub id: Uuid,
    pub brain_id: String,
    pub event_type: BrainEventType,
    pub payload: serde_json::Value,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize, sqlx::Type)]
#[sqlx(type_name = "text", rename_all = "snake_case")]
pub enum BrainEventType {
    BrainStarted,
    BrainCompleted,
    BrainRouted,
    BrainFailed,
}

impl std::fmt::Display for BrainEventType {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            BrainEventType::BrainStarted => write!(f, "brain_started"),
            BrainEventType::BrainCompleted => write!(f, "brain_completed"),
            BrainEventType::BrainRouted => write!(f, "brain_routed"),
            BrainEventType::BrainFailed => write!(f, "brain_failed"),
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainStartedPayload {
    pub session_id: Uuid,
    pub brief: String,
    pub flow_config: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainCompletedPayload {
    pub session_id: Uuid,
    pub duration_ms: u64,
    pub result: serde_json::Value,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainRoutedPayload {
    pub session_id: Uuid,
    pub from_brain: String,
    pub to_brain: String,
    pub reason: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainFailedPayload {
    pub session_id: Uuid,
    pub error: String,
    pub stage: String,
}
