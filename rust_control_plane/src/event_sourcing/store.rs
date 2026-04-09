use sqlx::PgPool;
use anyhow::Result;
use crate::event_sourcing::{BrainEvent, BrainEventType};
use uuid::Uuid;
use chrono::{DateTime, Utc};

pub struct EventStore {
    pool: PgPool,
}

impl EventStore {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    pub async fn append_event(
        &self,
        brain_id: &str,
        event_type: BrainEventType,
        payload: serde_json::Value,
    ) -> Result<BrainEvent> {
        let id = Uuid::new_v4();
        let created_at = Utc::now();
        let event_type_clone = event_type.clone();

        sqlx::query!(
            "INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
             VALUES ($1, $2, $3, $4, $5)",
            id,
            brain_id,
            event_type as BrainEventType,
            payload,
            created_at,
        )
        .execute(&self.pool)
        .await?;

        Ok(BrainEvent {
            id,
            brain_id: brain_id.to_string(),
            event_type: event_type_clone,
            payload,
            created_at: Some(created_at),
        })
    }

    pub async fn read_events(
        &self,
        brain_id: Option<&str>,
        event_type: Option<BrainEventType>,
        start_time: Option<DateTime<Utc>>,
        end_time: Option<DateTime<Utc>>,
        limit: usize,
    ) -> Result<Vec<BrainEvent>> {
        let events = sqlx::query_as!(
            BrainEvent,
            "SELECT id, brain_id, event_type as \"event_type: BrainEventType\", payload, created_at
             FROM activity_log
             WHERE ($1::text IS NULL OR brain_id = $1)
               AND ($2::text IS NULL OR event_type = $2)
               AND ($3::timestamptz IS NULL OR created_at >= $3)
               AND ($4::timestamptz IS NULL OR created_at <= $4)
             ORDER BY created_at DESC
             LIMIT $5",
            brain_id,
            event_type.map(|t| t.to_string()),
            start_time,
            end_time,
            limit as i64,
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(events)
    }

    pub async fn replay_events(
        &self,
        session_id: Uuid,
    ) -> Result<Vec<BrainEvent>> {
        let events = sqlx::query_as!(
            BrainEvent,
            "SELECT id, brain_id, event_type as \"event_type: BrainEventType\", payload, created_at
             FROM activity_log
             WHERE payload->>'session_id' = $1
             ORDER BY created_at ASC",
            session_id.to_string(),
        )
        .fetch_all(&self.pool)
        .await?;

        Ok(events)
    }
}
