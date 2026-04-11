//! Webhook worker for processing queued webhooks
//!
//! Consumes webhooks from the queue and processes them via AI worker.
//! Implements retry logic with exponential backoff and DLQ integration.
//! Brain #7 Condition #6: DLQ Retry Backoff Strategy

use crate::dlq::DeadLetterQueue;
use crate::observability::LatencyTracker;
use crate::queue::WebhookEvent;
use serde_json::Value;
use sqlx::PgPool;
use std::sync::Arc;
use std::time::Duration;
use tokio::time::sleep;
use tracing::{error, info, warn};

/// Webhook worker configuration
pub struct WebhookWorker {
    db: PgPool,
    webhook_queue: tokio::sync::mpsc::Receiver<WebhookEvent>,
    webhook_sender: tokio::sync::mpsc::Sender<WebhookEvent>,
    dlq: DeadLetterQueue,
    latency_tracker: Arc<LatencyTracker>,
}

impl WebhookWorker {
    /// Create new webhook worker
    pub fn new(
        db: PgPool,
        webhook_queue: tokio::sync::mpsc::Receiver<WebhookEvent>,
        webhook_sender: tokio::sync::mpsc::Sender<WebhookEvent>,
        latency_tracker: Arc<LatencyTracker>,
    ) -> Self {
        let dlq = DeadLetterQueue::new(db.clone());
        Self {
            db,
            webhook_queue,
            webhook_sender,
            dlq,
            latency_tracker,
        }
    }

    /// Start worker (runs forever)
    ///
    /// This should be spawned as a background task
    pub async fn start(&mut self) {
        info!("Webhook worker started");

        loop {
            match self.process_next_webhook().await {
                Ok(Some(())) => {
                    // Successfully processed webhook
                }
                Ok(None) => {
                    // No webhook to process, wait a bit
                    sleep(Duration::from_millis(100)).await;
                }
                Err(e) => {
                    error!(error = %e, "Error processing webhook");
                }
            }
        }
    }

    /// Process next webhook from queue
    ///
    /// Returns Ok(Some(())) if webhook was processed
    /// Returns Ok(None) if queue is empty
    /// Returns Err if processing failed
    async fn process_next_webhook(&mut self) -> anyhow::Result<Option<()>> {
        // Non-blocking receive
        let event = match self.webhook_queue.try_recv() {
            Ok(event) => event,
            Err(tokio::sync::mpsc::error::TryRecvError::Empty) => return Ok(None),
            Err(tokio::sync::mpsc::error::TryRecvError::Disconnected) => {
                return Err(anyhow::anyhow!("Webhook queue disconnected"));
            }
        };

        // Extract external message ID
        let external_id = self.extract_external_id(&event.payload, &event.channel)?;

        // Update messages status: 'processing'
        sqlx::query("UPDATE messages SET status = 'processing' WHERE external_message_id = $1")
            .bind(&external_id)
            .execute(&self.db)
            .await?;

        // Process webhook (send to AI worker via gRPC)
        match self.process_webhook_with_retry(&event, &external_id).await {
            Ok(_) => {
                // Record E2E latency (Brain #7 Condition #3)
                if let Some(duration) = self.latency_tracker.record_latency(&event.trace_id, &event.channel) {
                    crate::metrics::record_e2e_latency(&event.channel, duration);
                }

                // Success: update status to 'completed'
                sqlx::query("UPDATE messages SET status = 'completed' WHERE external_message_id = $1")
                    .bind(&external_id)
                    .execute(&self.db)
                    .await?;

                info!(
                    channel = %event.channel,
                    trace_id = %event.trace_id,
                    external_id = %external_id,
                    "Webhook processed successfully"
                );

                Ok(Some(()))
            }
            Err(e) => {
                // Cleanup latency timer on failure
                self.latency_tracker.cleanup_timer(&event.trace_id);

                // Failure: handle retry or move to DLQ
                self.handle_retry_or_dlq(&event, &external_id, &e.to_string()).await?;
                Ok(Some(()))
            }
        }
    }

    /// Process webhook with retry logic
    async fn process_webhook_with_retry(
        &mut self,
        event: &WebhookEvent,
        external_id: &str,
    ) -> anyhow::Result<()> {
        // Get current retry count from messages table
        let retry_count: i32 = sqlx::query_scalar(
            "SELECT COALESCE(retry_count, 0) FROM messages WHERE external_message_id = $1"
        )
        .bind(external_id)
        .fetch_one(&self.db)
        .await?;

        // If retry_count < 3, apply backoff and retry
        if retry_count < 3 {
            // Calculate backoff delay: [1s, 5s, 30s][retry_count]
            let delay = Self::calculate_backoff(retry_count);

            if retry_count > 0 {
                info!(
                    external_id = %external_id,
                    retry_count = retry_count,
                    delay_secs = delay.as_secs(),
                    "Applying backoff delay before retry"
                );
                sleep(delay).await;
            }

            // Increment retry_count
            sqlx::query("UPDATE messages SET retry_count = retry_count + 1 WHERE external_message_id = $1")
                .bind(external_id)
                .execute(&self.db)
                .await?;

            // TODO: Send to Python AI worker via gRPC
            // For now, simulate success/failure
            self.send_to_ai_worker(event).await?;

            Ok(())
        } else {
            // retry_count >= 3: permanent failure
            Err(anyhow::anyhow!("Max retries exceeded"))
        }
    }

    /// Handle retry or move to DLQ
    async fn handle_retry_or_dlq(
        &mut self,
        event: &WebhookEvent,
        external_id: &str,
        error: &str,
    ) -> anyhow::Result<()> {
        // Get current retry count
        let retry_count: i32 = sqlx::query_scalar(
            "SELECT COALESCE(retry_count, 0) FROM messages WHERE external_message_id = $1"
        )
        .bind(external_id)
        .fetch_one(&self.db)
        .await?;

        if retry_count < 3 {
            // Retry: increment retry_count and re-queue
            info!(
                external_id = %external_id,
                retry_count = retry_count,
                error = %error,
                "Webhook failed, will retry"
            );

            sqlx::query("UPDATE messages SET retry_count = retry_count + 1 WHERE external_message_id = $1")
                .bind(external_id)
                .execute(&self.db)
                .await?;

            // Re-queue event
            self.webhook_sender
                .send(event.clone())
                .await
                .map_err(|_| anyhow::anyhow!("Failed to re-queue webhook"))?;
        } else {
            // Move to DLQ
            warn!(
                external_id = %external_id,
                retry_count = retry_count,
                error = %error,
                "Webhook failed after 3 retries, moving to DLQ"
            );

            self.dlq
                .move_to_dlq(external_id, &event.channel, &event.payload, error)
                .await?;

            // Update messages status to 'failed'
            sqlx::query("UPDATE messages SET status = 'failed' WHERE external_message_id = $1")
                .bind(external_id)
                .execute(&self.db)
                .await?;
        }

        Ok(())
    }

    /// Calculate exponential backoff delay
    ///
    /// Retry 0 → 1s (transient glitch)
    /// Retry 1 → 5s (provider throttling)
    /// Retry 2 → 30s (provider outage)
    /// Retry 3 → Permanent failure
    fn calculate_backoff(retry_count: i32) -> Duration {
        match retry_count {
            0 => Duration::from_secs(1),
            1 => Duration::from_secs(5),
            2 => Duration::from_secs(30),
            _ => Duration::from_secs(30), // Cap at 30s
        }
    }

    /// Extract external message ID from payload
    fn extract_external_id(&self, payload: &Value, channel: &str) -> anyhow::Result<String> {
        let id = match channel {
            "whatsapp" => payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"]
                .as_str()
                .ok_or_else(|| anyhow::anyhow!("WhatsApp message ID not found"))?
                .to_string(),
            "instagram" => payload["changes"][0]["value"]["id"]
                .as_str()
                .ok_or_else(|| anyhow::anyhow!("Instagram comment ID not found"))?
                .to_string(),
            "email" => payload["headers"]["message-id"]
                .as_str()
                .ok_or_else(|| anyhow::anyhow!("Email Message-ID not found"))?
                .to_string(),
            _ => return Err(anyhow::anyhow!("Unsupported channel: {}", channel)),
        };

        Ok(id)
    }

    /// Send webhook to Python AI worker via gRPC
    async fn send_to_ai_worker(&self, event: &WebhookEvent) -> anyhow::Result<()> {
        info!(
            channel = %event.channel,
            trace_id = %event.trace_id,
            "Sending to AI worker via gRPC"
        );

        // For now, simulate success (gRPC client integration in next step)
        // TODO: Add ai_worker_client field to WebhookWorker struct
        // let response = self.ai_worker_client
        //     .process_webhook(
        //         event.trace_id.clone(),
        //         event.channel.clone(),
        //         event.payload.to_string(),
        //     )
        //     .await
        //     .map_err(|e| anyhow::anyhow!("AI worker communication failed: {}", e))?;

        // info!(ai_response = %response, "AI worker processing complete");

        Ok(())
    }
}

/// Start webhook worker as background task
pub fn start_worker(
    db: PgPool,
    receiver: tokio::sync::mpsc::Receiver<WebhookEvent>,
    sender: tokio::sync::mpsc::Sender<WebhookEvent>,
    latency_tracker: Arc<LatencyTracker>,
) {
    tokio::spawn(async move {
        let mut worker = WebhookWorker::new(db, receiver, sender, latency_tracker);
        worker.start().await;
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_backoff_calculation() {
        assert_eq!(WebhookWorker::calculate_backoff(0).as_secs(), 1);
        assert_eq!(WebhookWorker::calculate_backoff(1).as_secs(), 5);
        assert_eq!(WebhookWorker::calculate_backoff(2).as_secs(), 30);
        assert_eq!(WebhookWorker::calculate_backoff(3).as_secs(), 30); // Cap at 30s
    }
}
