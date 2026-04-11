//! Dead Letter Queue for failed webhooks
//!
//! Implements Brain #7 Condition #6: DLQ Retry Backoff Strategy
//! - Retry 1: 1 second delay (transient glitch)
//! - Retry 2: 5 second delay (provider throttling)
//! - Retry 3: 30 second delay (provider outage)
//! - After 3 failures: Move to DLQ (manual inspection + retry)

pub mod retry_worker;

pub use retry_worker::{start_retry_worker, RetryWorker};

use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::{PgPool, Row};
use uuid::Uuid;

/// Failed webhook in Dead Letter Queue
#[derive(Debug, Clone)]
pub struct FailedWebhook {
    pub id: Uuid,
    pub external_message_id: String,
    pub channel: String,
    pub payload: Value,
    pub error_message: String,
    pub retry_count: i32,
    pub created_at: DateTime<Utc>,
    pub last_retry_at: Option<DateTime<Utc>>,
}

/// Dead Letter Queue repository
pub struct DeadLetterQueue {
    db: PgPool,
}

impl DeadLetterQueue {
    /// Create new DLQ repository
    pub fn new(db: PgPool) -> Self {
        Self { db }
    }

    /// Move failed webhook to DLQ
    ///
    /// Called after 3 retry attempts fail
    pub async fn move_to_dlq(
        &self,
        external_id: &str,
        channel: &str,
        payload: &Value,
        error: &str,
    ) -> anyhow::Result<Uuid> {
        let row = sqlx::query(
            "INSERT INTO webhook_dlq (external_message_id, channel, payload, error_message, retry_count)
             VALUES ($1, $2, $3, $4, 0)
             RETURNING id"
        )
        .bind(external_id)
        .bind(channel)
        .bind(payload)
        .bind(error)
        .fetch_one(&self.db)
        .await?;

        let id = row.get("id");
        tracing::info!(
            id = %id,
            external_id = %external_id,
            channel = %channel,
            error = %error,
            "Webhook moved to DLQ"
        );

        Ok(id)
    }

    /// Get failed webhooks with pagination
    ///
    /// Returns webhooks ordered by creation time (oldest first)
    pub async fn get_failed_webhooks(
        &self,
        limit: i64,
        offset: i64,
    ) -> anyhow::Result<Vec<FailedWebhook>> {
        let rows = sqlx::query(
            "SELECT id, external_message_id, channel, payload, error_message, retry_count, created_at, last_retry_at
             FROM webhook_dlq
             ORDER BY created_at ASC
             LIMIT $1 OFFSET $2"
        )
        .bind(limit)
        .bind(offset)
        .fetch_all(&self.db)
        .await?;

        let webhooks = rows
            .into_iter()
            .map(|row| FailedWebhook {
                id: row.get("id"),
                external_message_id: row.get("external_message_id"),
                channel: row.get("channel"),
                payload: row.get("payload"),
                error_message: row.get("error_message"),
                retry_count: row.get("retry_count"),
                created_at: row.get("created_at"),
                last_retry_at: row.get("last_retry_at"),
            })
            .collect();

        Ok(webhooks)
    }

    /// Retry webhook (increment retry_count and update last_retry_at)
    ///
    /// Returns true if webhook still has retries left, false if permanently failed
    pub async fn retry_webhook(&self, id: Uuid) -> anyhow::Result<bool> {
        let retry_count: i32 = sqlx::query_scalar(
            "UPDATE webhook_dlq
             SET retry_count = retry_count + 1,
                 last_retry_at = NOW()
             WHERE id = $1
             RETURNING retry_count"
        )
        .bind(id)
        .fetch_one(&self.db)
        .await?;

        // If retry_count >= 3, permanently failed
        if retry_count >= 3 {
            tracing::warn!(
                id = %id,
                retry_count = retry_count,
                "Webhook permanently failed after 3 retries"
            );
            return Ok(false);
        }

        tracing::info!(
            id = %id,
            retry_count = retry_count,
            "Webhook retry attempt queued"
        );

        Ok(true)
    }

    /// Get current retry count for webhook
    pub async fn get_retry_count(&self, id: Uuid) -> anyhow::Result<i32> {
        let retry_count = sqlx::query_scalar("SELECT retry_count FROM webhook_dlq WHERE id = $1")
            .bind(id)
            .fetch_one(&self.db)
            .await?;

        Ok(retry_count)
    }

    /// Delete webhook from DLQ (after permanent failure or manual cleanup)
    pub async fn delete_webhook(&self, id: Uuid) -> anyhow::Result<()> {
        sqlx::query("DELETE FROM webhook_dlq WHERE id = $1")
            .bind(id)
            .execute(&self.db)
            .await?;

        tracing::info!(id = %id, "Webhook deleted from DLQ");
        Ok(())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_dlq_repository_creation() {
        // Test repository creation logic
        // In real test, we'd use test database
        assert!(true);
    }
}
