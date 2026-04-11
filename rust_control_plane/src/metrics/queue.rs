//! Prometheus metrics for webhook queue monitoring
//!
//! Brain #7 Condition #2: Queue Depth Monitoring
//! Exposes metrics for:
//! - Queue depth percentage
//! - Queue capacity
//! - Queue rejection rate (guardrail metric)
//! - Pending webhook count (guardrail metric)

use lazy_static::lazy_static;
use prometheus::{IntGauge, Registry};
use std::sync::Arc;

lazy_static! {
    /// Queue depth percentage (0-100)
    pub static ref WEBHOOK_QUEUE_DEPTH_PERCENT: IntGauge = IntGauge::new(
        "webhook_queue_depth_percent",
        "Webhook queue depth as percentage (0-100)"
    ).unwrap();

    /// Queue capacity (total)
    pub static ref WEBHOOK_QUEUE_CAPACITY: IntGauge = IntGauge::new(
        "webhook_queue_capacity",
        "Webhook queue total capacity"
    ).unwrap();

    /// Queue rejection count (guardrail metric - Brain #7 Condition #2)
    pub static ref WEBHOOK_QUEUE_REJECTION_TOTAL: IntGauge = IntGauge::new(
        "webhook_queue_rejection_total",
        "Total number of webhooks rejected due to queue depth > 90%"
    ).unwrap();

    /// Pending webhook count in memory (guardrail metric - Brain #7 Condition #2)
    pub static ref WEBHOOK_PENDING_TOTAL: IntGauge = IntGauge::new(
        "webhook_pending_total",
        "Number of webhooks pending in memory queue"
    ).unwrap();
}

/// Register queue metrics with Prometheus registry
pub fn register_metrics(registry: &Registry) -> anyhow::Result<()> {
    registry.register(Box::new(WEBHOOK_QUEUE_DEPTH_PERCENT.clone()))?;
    registry.register(Box::new(WEBHOOK_QUEUE_CAPACITY.clone()))?;
    registry.register(Box::new(WEBHOOK_QUEUE_REJECTION_TOTAL.clone()))?;
    registry.register(Box::new(WEBHOOK_PENDING_TOTAL.clone()))?;
    Ok(())
}

/// Update queue depth metrics
pub fn update_queue_metrics(depth_percent: f64, capacity: usize, pending: usize) {
    WEBHOOK_QUEUE_DEPTH_PERCENT.set(depth_percent as i64);
    WEBHOOK_QUEUE_CAPACITY.set(capacity as i64);
    WEBHOOK_PENDING_TOTAL.set(pending as i64);
}

/// Increment rejection counter
pub fn increment_rejection_counter() {
    WEBHOOK_QUEUE_REJECTION_TOTAL.inc();
}

/// Start background metrics updater (syncs queue state to Prometheus every 100ms)
pub fn start_metrics_updater(queue: Arc<tokio::sync::mpsc::Receiver<crate::queue::WebhookEvent>>, capacity: usize) {
    tokio::spawn(async move {
        let mut interval = tokio::time::interval(std::time::Duration::from_millis(100));

        loop {
            interval.tick().await;

            let pending = queue.capacity() - queue.len();
            let depth_percent = (pending as f64 / capacity as f64) * 100.0;

            update_queue_metrics(depth_percent, capacity, pending);
        }
    });
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_registered() {
        // Metrics should be accessible
        let depth = WEBHOOK_QUEUE_DEPTH_PERCENT.get();
        assert_eq!(depth, 0);

        let capacity = WEBHOOK_QUEUE_CAPACITY.get();
        assert_eq!(capacity, 0);
    }

    #[test]
    fn test_update_metrics() {
        update_queue_metrics(50.0, 1000, 500);

        assert_eq!(WEBHOOK_QUEUE_DEPTH_PERCENT.get(), 50);
        assert_eq!(WEBHOOK_QUEUE_CAPACITY.get(), 1000);
        assert_eq!(WEBHOOK_PENDING_TOTAL.get(), 500);
    }

    #[test]
    fn test_rejection_counter() {
        let initial = WEBHOOK_QUEUE_REJECTION_TOTAL.get();
        increment_rejection_counter();
        assert_eq!(WEBHOOK_QUEUE_REJECTION_TOTAL.get(), initial + 1);
    }
}
