//! Retry worker for Dead Letter Queue
//!
//! Implements Brain #7 Condition #6: DLQ Retry Backoff Strategy
//! - Background worker runs every 30 seconds
//! - Queries DLQ for webhooks with retry_count < 3
//! - Applies exponential backoff: [1s, 5s, 30s][retry_count]
//! - Resubmits to webhook_queue after backoff delay
//! - Moves to permanent failure after 3 retries

use crate::dlq::DeadLetterQueue;
use crate::queue::WebhookQueue;
use sqlx::PgPool;
use std::sync::Arc;
use std::time::Duration;
use tokio::time::sleep;

/// Retry worker for DLQ
pub struct RetryWorker {
    db: PgPool,
    webhook_queue: Arc<WebhookQueue>,
}

impl RetryWorker {
    /// Create new retry worker
    pub fn new(db: PgPool, webhook_queue: Arc<WebhookQueue>) -> Self {
        Self {
            db,
            webhook_queue,
        }
    }

    /// Start retry worker (runs forever)
    ///
    /// This should be spawned as a background task
    pub async fn start(&self) {
        let dlq = DeadLetterQueue::new(self.db.clone());
        let mut interval = tokio::time::interval(Duration::from_secs(30));

        loop {
            interval.tick().await;

            // Query DLQ for webhooks with retry_count < 3
            match self.process_retry_batch(&dlq).await {
                Ok(count) => {
                    if count > 0 {
                        tracing::info!(count = count, "Processed retry batch");
                    }
                }
                Err(e) => {
                    tracing::error!(error = %e, "Failed to process retry batch");
                }
            }
        }
    }

    /// Process a batch of retries
    async fn process_retry_batch(&self, dlq: &DeadLetterQueue) -> anyhow::Result<usize> {
        // Get webhooks with retry_count < 3
        let webhooks = dlq.get_failed_webhooks(100, 0).await?;
        let mut processed = 0;

        for webhook in webhooks {
            // Check if we should retry
            if webhook.retry_count >= 3 {
                // Permanently failed - delete from DLQ
                dlq.delete_webhook(webhook.id).await?;
                continue;
            }

            // Calculate backoff delay: [1s, 5s, 30s][retry_count]
            let delay = Self::calculate_backoff(webhook.retry_count);
            tracing::info!(
                id = %webhook.id,
                retry_count = webhook.retry_count,
                delay_secs = delay.as_secs(),
                "Applying backoff delay"
            );

            // Apply backoff
            sleep(delay).await;

            // Resubmit to webhook_queue
            let event = crate::queue::WebhookEvent {
                channel: webhook.channel.clone(),
                payload: webhook.payload.clone(),
                trace_id: uuid::Uuid::new_v4().to_string(),
            };

            match self.webhook_queue.send_with_backpressure(event).await {
                Ok(_) => {
                    // Increment retry_count
                    dlq.retry_webhook(webhook.id).await?;
                    processed += 1;
                }
                Err(_) => {
                    tracing::warn!(
                        id = %webhook.id,
                        "Failed to resubmit webhook to queue (queue depth > 90%)"
                    );
                    // Don't increment retry_count - queue is full
                }
            }
        }

        Ok(processed)
    }

    /// Calculate exponential backoff delay
    ///
    /// Retry 0 -> 1s (transient glitch)
    /// Retry 1 -> 5s (provider throttling)
    /// Retry 2 -> 30s (provider outage)
    /// Retry 3 -> Permanent failure
    fn calculate_backoff(retry_count: i32) -> Duration {
        match retry_count {
            0 => Duration::from_secs(1),
            1 => Duration::from_secs(5),
            2 => Duration::from_secs(30),
            _ => Duration::from_secs(30), // Cap at 30s
        }
    }
}

/// Start retry worker as background task
pub fn start_retry_worker(db: PgPool, webhook_queue: Arc<WebhookQueue>) {
    let worker = RetryWorker::new(db, webhook_queue);
    tokio::spawn(async move {
        worker.start().await;
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_backoff_calculation() {
        assert_eq!(RetryWorker::calculate_backoff(0).as_secs(), 1);
        assert_eq!(RetryWorker::calculate_backoff(1).as_secs(), 5);
        assert_eq!(RetryWorker::calculate_backoff(2).as_secs(), 30);
        assert_eq!(RetryWorker::calculate_backoff(3).as_secs(), 30); // Cap at 30s
    }
}
