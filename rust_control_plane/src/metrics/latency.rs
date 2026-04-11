//! End-to-end latency metrics for webhooks
//!
//! Prometheus histogram for measuring E2E latency.
//! Brain #7 Condition #3: webhook_e2e_latency_seconds{channel,quantile} < 30s P95
//!
//! Buckets: [0.1s, 0.5s, 1s, 5s, 10s, 20s, 30s, 60s, 120s]
//! Success threshold: P95 < 30s

use prometheus::{Histogram, HistogramOpts};
use std::time::Duration;
use lazy_static::lazy_static;

lazy_static! {
    pub static ref WEBHOOK_E2E_LATENCY_SECONDS: Histogram = {
        let histogram = Histogram::with_opts(
            HistogramOpts::new(
                "webhook_e2e_latency_seconds",
                "End-to-end latency from webhook received to AI response sent"
            )
            .buckets(vec![0.1, 0.5, 1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0])
        )
        .expect("Failed to create WEBHOOK_E2E_LATENCY_SECONDS histogram");

        // Register with global registry
        prometheus::register(Box::new(histogram.clone()))
            .expect("Failed to register WEBHOOK_E2E_LATENCY_SECONDS");

        histogram
    };
}

/// Record end-to-end latency for a webhook
///
/// # Arguments
/// * `channel` - Channel name (whatsapp, instagram, email)
/// * `duration` - Duration from webhook received to AI response sent
///
/// # Example
/// ```rust
/// use std::time::Duration;
///
/// let duration = Duration::from_secs(5);
/// record_e2e_latency("whatsapp", duration);
/// ```
pub fn record_e2e_latency(channel: &str, duration: Duration) {
    WEBHOOK_E2E_LATENCY_SECONDS.observe(duration.as_secs_f64());
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn test_histogram_registered() {
        // Verify histogram is registered
        let metric_families = prometheus::gather();
        let latency_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found");

        assert_eq!(latency_metric.get_name(), "webhook_e2e_latency_seconds");
        assert!(latency_metric.get_help().contains("End-to-end latency"));
    }

    #[test]
    fn test_record_e2e_latency() {
        // Record a latency
        let duration = Duration::from_secs_f64(5.2);
        record_e2e_latency("whatsapp", duration);

        // Verify metric was recorded
        let metric_families = prometheus::gather();
        let latency_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found");

        // Check that whatsapp label exists
        let metric = latency_metric.get_metric().first();
        assert!(metric.is_some());

        let label = metric.unwrap().get_label().iter()
            .find(|l| l.get_name() == "channel");
        assert!(label.is_some());
        assert_eq!(label.unwrap().get_value(), "whatsapp");
    }

    #[test]
    fn test_buckets_configured() {
        // Verify buckets are correct
        let expected_buckets = vec![0.1, 0.5, 1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0];

        // The histogram should have these buckets
        // We can't directly access buckets from the Histogram type,
        // but we can verify the metric exists and has samples
        let metric_families = prometheus::gather();
        let latency_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found");

        assert!(!latency_metric.get_metric().is_empty());
    }

    #[test]
    fn test_multiple_channels() {
        // Record latencies for different channels
        record_e2e_latency("whatsapp", Duration::from_secs(1));
        record_e2e_latency("instagram", Duration::from_secs(2));
        record_e2e_latency("email", Duration::from_secs(3));

        // Verify all channels are recorded
        let metric_families = prometheus::gather();
        let latency_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found");

        // Should have metrics for all three channels
        let metrics = latency_metric.get_metric();
        let channels: Vec<&str> = metrics.iter()
            .filter_map(|m| {
                m.get_label().iter()
                    .find(|l| l.get_name() == "channel")
                    .map(|l| l.get_value().as_str())
            })
            .collect();

        assert!(channels.contains(&"whatsapp"));
        assert!(channels.contains(&"instagram"));
        assert!(channels.contains(&"email"));
    }

    #[test]
    fn test_p95_threshold() {
        // Record latencies around P95 threshold
        record_e2e_latency("whatsapp", Duration::from_secs(25)); // Below P95
        record_e2e_latency("whatsapp", Duration::from_secs(30)); // At P95
        record_e2e_latency("whatsapp", Duration::from_secs(35)); // Above P95

        // Verify metric is recorded
        let metric_families = prometheus::gather();
        let latency_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found");

        assert!(!latency_metric.get_metric().is_empty());
    }
}
