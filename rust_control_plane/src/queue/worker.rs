//! Webhook worker for processing queued webhooks
//!
//! Consumes webhooks from the queue and processes them via AI worker.
//! Implements retry logic with exponential backoff and DLQ integration.
//! Brain #7 Condition #6: DLQ Retry Backoff Strategy

use crate::dlq::DeadLetterQueue;
use crate::observability::LatencyTracker;
use crate::queue::WebhookEvent;
use crate::state::AiWorkerRuntimeMode;
use chrono::Utc;
use serde_json::Value;
use sqlx::PgPool;
use std::sync::{Arc, atomic::{AtomicU64, Ordering}};
use std::time::Duration;
use tokio::time::sleep;
use tracing::{error, info, warn};

/// Webhook worker configuration
pub struct WebhookWorker {
    db: PgPool,
    webhook_queue: tokio::sync::mpsc::Receiver<WebhookEvent>,
    webhook_sender: tokio::sync::mpsc::Sender<WebhookEvent>,
    pending_count: Arc<AtomicU64>,
    dlq: DeadLetterQueue,
    latency_tracker: Arc<LatencyTracker>,
    ai_worker_runtime: Arc<AiWorkerRuntimeMode>,
}

impl WebhookWorker {
    fn degraded_runtime_error(mode: &str, detail: &str) -> anyhow::Error {
        anyhow::anyhow!("AI worker runtime {}: {}", mode, detail)
    }

    fn successful_ai_dispatch_message_status() -> &'static str {
        "completed"
    }

    fn successful_ai_dispatch_delivery_status() -> Option<&'static str> {
        None
    }

    fn ai_worker_audit_brain_id() -> &'static str {
        "ai_worker"
    }

    fn ai_worker_success_event_type() -> &'static str {
        "brain_completed"
    }

    fn ai_worker_failure_event_type() -> &'static str {
        "brain_failed"
    }

    fn build_ai_worker_success_payload(
        message_id: uuid::Uuid,
        event: &WebhookEvent,
        ai_response: &str,
    ) -> Value {
        serde_json::json!({
            "message_id": message_id.to_string(),
            "trace_id": event.trace_id,
            "channel": event.channel,
            "ai_response": ai_response,
        })
    }

    fn build_ai_worker_failure_payload(
        message_id: uuid::Uuid,
        event: &WebhookEvent,
        error: &str,
        retry_count: i32,
        terminal: bool,
    ) -> Value {
        serde_json::json!({
            "message_id": message_id.to_string(),
            "trace_id": event.trace_id,
            "channel": event.channel,
            "error": error,
            "retry_count": retry_count,
            "terminal": terminal,
        })
    }

    /// Create new webhook worker
    pub fn new(
        db: PgPool,
        webhook_queue: tokio::sync::mpsc::Receiver<WebhookEvent>,
        webhook_sender: tokio::sync::mpsc::Sender<WebhookEvent>,
        pending_count: Arc<AtomicU64>,
        latency_tracker: Arc<LatencyTracker>,
        ai_worker_runtime: Arc<AiWorkerRuntimeMode>,
    ) -> Self {
        let dlq = DeadLetterQueue::new(db.clone());
        Self {
            db,
            webhook_queue,
            webhook_sender,
            pending_count,
            dlq,
            latency_tracker,
            ai_worker_runtime,
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

        // The event left the in-memory queue, so release its pending slot.
        self.pending_count.fetch_update(Ordering::Relaxed, Ordering::Relaxed, |current| {
            Some(current.saturating_sub(1))
        }).ok();

        // Extract external message ID
        let external_id = self.extract_external_id(&event.payload, &event.channel)?;

        // Update messages status: 'processing'
        sqlx::query("UPDATE messages SET status = 'processing' WHERE external_message_id = $1")
            .bind(&external_id)
            .execute(&self.db)
            .await?;

        // Process webhook (send to AI worker via gRPC)
        match self.process_webhook_with_retry(&event, &external_id).await {
            Ok(ai_response) => {
                // Record E2E latency AFTER actual AI processing (Brain #7 Condition #3)
                if let Some(duration) = self.latency_tracker.record_latency(&event.trace_id, &event.channel) {
                    crate::metrics::record_e2e_latency(&event.channel, duration);
                }

                // Get message_id for logging and any future delivery-state hooks.
                let message_id: uuid::Uuid = sqlx::query_scalar(
                    "SELECT id FROM messages WHERE external_message_id = $1"
                )
                .bind(&external_id)
                .fetch_one(&self.db)
                .await?;

                self.record_successful_ai_worker_response(message_id, &event, &ai_response)
                    .await?;

                if let Some(delivery_status) = Self::successful_ai_dispatch_delivery_status() {
                    self.update_delivery_status(message_id, delivery_status, None, None).await?;
                }

                // Success here means the AI worker accepted and processed the webhook.
                // It does not imply an outbound provider delivery event already happened.
                sqlx::query("UPDATE messages SET status = $1 WHERE external_message_id = $2")
                    .bind(Self::successful_ai_dispatch_message_status())
                    .bind(&external_id)
                    .execute(&self.db)
                    .await?;

                info!(
                    channel = %event.channel,
                    trace_id = %event.trace_id,
                    external_id = %external_id,
                    message_id = %message_id,
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
    ) -> anyhow::Result<String> {
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

            self.send_to_ai_worker(event).await
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

        let message_id: uuid::Uuid = sqlx::query_scalar(
            "SELECT id FROM messages WHERE external_message_id = $1"
        )
        .bind(external_id)
        .fetch_one(&self.db)
        .await?;

        if retry_count < 3 {
            self.record_failed_ai_worker_response(message_id, event, error, retry_count, false)
                .await?;

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
            let pending_count = Arc::clone(&self.pending_count);
            pending_count.fetch_add(1, Ordering::Relaxed);
            self.webhook_sender
                .send(event.clone())
                .await
                .map_err(|_| {
                    pending_count.fetch_sub(1, Ordering::Relaxed);
                    anyhow::anyhow!("Failed to re-queue webhook")
                })?;
        } else {
            self.record_failed_ai_worker_response(message_id, event, error, retry_count, true)
                .await?;

            // Move to DLQ
            warn!(
                external_id = %external_id,
                retry_count = retry_count,
                error = %error,
                "Webhook failed after 3 retries, moving to DLQ"
            );

            // Update delivery status to 'failed'
            self.update_delivery_status(message_id, "failed", None, Some(error)).await?;

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

    /// Send webhook to Python AI worker via gRPC.
    ///
    /// In the current slice the runtime seam is explicit, but dispatch stays fail-closed.
    async fn send_to_ai_worker(&self, event: &WebhookEvent) -> anyhow::Result<String> {
        match self.ai_worker_runtime.as_ref() {
            AiWorkerRuntimeMode::Disabled { reason } => {
                warn!(
                    trace_id = %event.trace_id,
                    channel = %event.channel,
                    ai_worker_mode = %self.ai_worker_runtime.label(),
                    ai_worker_reason = %reason,
                    "AI worker processing disabled"
                );

                Err(Self::degraded_runtime_error(
                    self.ai_worker_runtime.label(),
                    reason,
                ))
            }
            AiWorkerRuntimeMode::Unavailable { addr, reason } => {
                warn!(
                    trace_id = %event.trace_id,
                    channel = %event.channel,
                    ai_worker_mode = %self.ai_worker_runtime.label(),
                    ai_worker_addr = %addr,
                    ai_worker_reason = %reason,
                    "AI worker runtime unavailable; webhook dispatch remains disabled"
                );

                Err(Self::degraded_runtime_error(
                    self.ai_worker_runtime.label(),
                    &format!("{} ({})", reason, addr),
                ))
            }
            AiWorkerRuntimeMode::Ready { addr, client } => {
                let ai_response = client
                    .process_webhook(
                        event.trace_id.clone(),
                        event.channel.clone(),
                        event.payload.to_string(),
                    )
                    .await?;

                info!(
                    trace_id = %event.trace_id,
                    channel = %event.channel,
                    ai_worker_mode = %self.ai_worker_runtime.label(),
                    ai_worker_addr = %addr,
                    ai_response = %ai_response,
                    "AI worker processing successful"
                );

                Ok(ai_response)
            }
        }
    }

    async fn record_successful_ai_worker_response(
        &self,
        message_id: uuid::Uuid,
        event: &WebhookEvent,
        ai_response: &str,
    ) -> anyhow::Result<()> {
        let already_recorded: bool = sqlx::query_scalar(
            "SELECT EXISTS(
                SELECT 1
                FROM activity_log
                WHERE brain_id = $1
                  AND event_type = $2
                  AND payload->>'message_id' = $3
            )",
        )
        .bind(Self::ai_worker_audit_brain_id())
        .bind(Self::ai_worker_success_event_type())
        .bind(message_id.to_string())
        .fetch_one(&self.db)
        .await?;

        if already_recorded {
            return Ok(());
        }

        sqlx::query(
            "INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
             VALUES ($1, $2, $3, $4, $5)",
        )
        .bind(uuid::Uuid::new_v4())
        .bind(Self::ai_worker_audit_brain_id())
        .bind(Self::ai_worker_success_event_type())
        .bind(Self::build_ai_worker_success_payload(
            message_id,
            event,
            ai_response,
        ))
        .bind(Utc::now())
        .execute(&self.db)
        .await?;

        Ok(())
    }

    async fn record_failed_ai_worker_response(
        &self,
        message_id: uuid::Uuid,
        event: &WebhookEvent,
        error: &str,
        retry_count: i32,
        terminal: bool,
    ) -> anyhow::Result<()> {
        sqlx::query(
            "INSERT INTO activity_log (id, brain_id, event_type, payload, created_at)
             VALUES ($1, $2, $3, $4, $5)",
        )
        .bind(uuid::Uuid::new_v4())
        .bind(Self::ai_worker_audit_brain_id())
        .bind(Self::ai_worker_failure_event_type())
        .bind(Self::build_ai_worker_failure_payload(
            message_id,
            event,
            error,
            retry_count,
            terminal,
        ))
        .bind(Utc::now())
        .execute(&self.db)
        .await?;

        Ok(())
    }


    /// Update delivery status for a message
    ///
    /// Records delivery status (sent/delivered/read/failed) in message_delivery_status table.
    async fn update_delivery_status(
        &self,
        message_id: uuid::Uuid,
        status: &str,
        provider_message_id: Option<&str>,
        error_message: Option<&str>,
    ) -> anyhow::Result<()> {
        sqlx::query(
            "INSERT INTO message_delivery_status (message_id, status, provider_message_id, error_message)
             VALUES ($1, $2, $3, $4)"
        )
        .bind(message_id)
        .bind(status)
        .bind(provider_message_id)
        .bind(error_message)
        .execute(&self.db)
        .await?;

        Ok(())
    }
}

/// Start webhook worker as background task
pub fn start_worker(
    db: PgPool,
    receiver: tokio::sync::mpsc::Receiver<WebhookEvent>,
    sender: tokio::sync::mpsc::Sender<WebhookEvent>,
    pending_count: Arc<AtomicU64>,
    latency_tracker: Arc<LatencyTracker>,
    ai_worker_runtime: Arc<AiWorkerRuntimeMode>,
) {
    tokio::spawn(async move {
        let mut worker = WebhookWorker::new(db, receiver, sender, pending_count, latency_tracker, ai_worker_runtime);
        worker.start().await;
    });
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::grpc::AiWorkerClient;
    use crate::state::AiWorkerRuntimeMode;

    #[test]
    fn test_backoff_calculation() {
        assert_eq!(WebhookWorker::calculate_backoff(0).as_secs(), 1);
        assert_eq!(WebhookWorker::calculate_backoff(1).as_secs(), 5);
        assert_eq!(WebhookWorker::calculate_backoff(2).as_secs(), 30);
        assert_eq!(WebhookWorker::calculate_backoff(3).as_secs(), 30); // Cap at 30s
    }

    #[test]
    fn test_ai_worker_runtime_disabled_reason_is_explicit() {
        let runtime = AiWorkerRuntimeMode::disabled("gRPC module is intentionally disabled");

        assert_eq!(runtime.label(), "disabled");
        assert_eq!(runtime.reason(), "gRPC module is intentionally disabled");
    }

    #[test]
    fn test_degraded_runtime_error_mentions_mode_and_detail() {
        let error = WebhookWorker::degraded_runtime_error("disabled", "AI_WORKER_MODE=disabled");

        assert_eq!(
            error.to_string(),
            "AI worker runtime disabled: AI_WORKER_MODE=disabled"
        );
    }

    #[test]
    fn test_successful_ai_dispatch_only_marks_processing_complete() {
        assert_eq!(
            WebhookWorker::successful_ai_dispatch_message_status(),
            "completed"
        );
        assert_eq!(
            WebhookWorker::successful_ai_dispatch_delivery_status(),
            None
        );
    }

    #[test]
    fn test_ai_worker_success_payload_contains_minimum_audit_fields() {
        let event = WebhookEvent {
            channel: "whatsapp".to_string(),
            payload: serde_json::json!({"message": "hello"}),
            trace_id: "trace-123".to_string(),
        };
        let message_id = uuid::Uuid::nil();
        let payload = WebhookWorker::build_ai_worker_success_payload(
            message_id,
            &event,
            "drafted response",
        );

        assert_eq!(payload["message_id"], message_id.to_string());
        assert_eq!(payload["trace_id"], "trace-123");
        assert_eq!(payload["channel"], "whatsapp");
        assert_eq!(payload["ai_response"], "drafted response");
    }

    #[test]
    fn test_ai_worker_failure_payload_contains_retry_and_terminal_state() {
        let event = WebhookEvent {
            channel: "email".to_string(),
            payload: serde_json::json!({"message": "hello"}),
            trace_id: "trace-999".to_string(),
        };
        let message_id = uuid::Uuid::nil();
        let payload = WebhookWorker::build_ai_worker_failure_payload(
            message_id,
            &event,
            "worker unavailable",
            2,
            true,
        );

        assert_eq!(payload["message_id"], message_id.to_string());
        assert_eq!(payload["trace_id"], "trace-999");
        assert_eq!(payload["channel"], "email");
        assert_eq!(payload["error"], "worker unavailable");
        assert_eq!(payload["retry_count"], 2);
        assert_eq!(payload["terminal"], true);
    }

    #[tokio::test]
    async fn test_ai_worker_runtime_ready_mode_is_distinct() {
        let runtime = AiWorkerRuntimeMode::ready(
            "http://127.0.0.1:50051",
            Arc::new(AiWorkerClient::new_for_tests()),
        );

        assert_eq!(runtime.label(), "ready");
        assert_eq!(runtime.addr(), Some("http://127.0.0.1:50051"));
        assert!(runtime.client().is_some());
    }
}
