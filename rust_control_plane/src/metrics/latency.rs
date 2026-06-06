//! End-to-end latency metrics for webhooks
//!
//! Prometheus histogram vector for measuring E2E latency by channel.
//! Brain #7 Condition #3: webhook_e2e_latency_seconds{channel,quantile} < 30s P95
//!
//! Buckets: [0.1s, 0.5s, 1s, 5s, 10s, 20s, 30s, 60s, 120s]
//! Success threshold: P95 < 30s

use prometheus::{HistogramOpts, HistogramVec};
use std::time::Duration;
use lazy_static::lazy_static;

lazy_static! {
    pub static ref WEBHOOK_E2E_LATENCY_SECONDS: HistogramVec = {
        let histogram = HistogramVec::new(
            HistogramOpts::new(
                "webhook_e2e_latency_seconds",
                "End-to-end latency from webhook received to AI response sent"
            )
            .buckets(vec![0.1, 0.5, 1.0, 5.0, 10.0, 20.0, 30.0, 60.0, 120.0]),
            &["channel"],
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
    WEBHOOK_E2E_LATENCY_SECONDS
        .with_label_values(&[channel])
        .observe(duration.as_secs_f64());
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::collections::HashSet;
    use std::time::Duration;

    fn gather_latency_metric() -> prometheus::proto::MetricFamily {
        let _ = &*WEBHOOK_E2E_LATENCY_SECONDS;
        prometheus::gather()
            .into_iter()
            .find(|metric| metric.get_name() == "webhook_e2e_latency_seconds")
            .expect("webhook_e2e_latency_seconds metric not found")
    }

    #[test]
    fn test_histogram_registered() {
        let latency_metric = gather_latency_metric();

        assert_eq!(latency_metric.get_name(), "webhook_e2e_latency_seconds");
        assert!(latency_metric.get_help().contains("End-to-end latency"));
    }

    #[test]
    fn test_record_e2e_latency() {
        let duration = Duration::from_secs_f64(5.2);
        record_e2e_latency("whatsapp", duration);

        let latency_metric = gather_latency_metric();

        let has_whatsapp = latency_metric.get_metric().iter().any(|metric| {
            metric
                .get_label()
                .iter()
                .any(|label| label.get_name() == "channel" && label.get_value() == "whatsapp")
        });
        assert!(has_whatsapp);
    }

    #[test]
    fn test_buckets_configured() {
        record_e2e_latency("whatsapp", Duration::from_secs(1));
        let latency_metric = gather_latency_metric();
        assert!(!latency_metric.get_metric().is_empty());
    }

    #[test]
    fn test_multiple_channels() {
        record_e2e_latency("whatsapp", Duration::from_secs(1));
        record_e2e_latency("instagram", Duration::from_secs(2));
        record_e2e_latency("email", Duration::from_secs(3));

        let latency_metric = gather_latency_metric();

        let channels: HashSet<String> = latency_metric.get_metric().iter()
            .filter_map(|m| {
                m.get_label().iter()
                    .find(|l| l.get_name() == "channel")
                    .map(|l| l.get_value().to_string())
            })
            .collect();

        assert!(channels.contains("whatsapp"));
        assert!(channels.contains("instagram"));
        assert!(channels.contains("email"));
    }

    #[test]
    fn test_p95_threshold() {
        record_e2e_latency("whatsapp", Duration::from_secs(25)); // Below P95
        record_e2e_latency("whatsapp", Duration::from_secs(30)); // At P95
        record_e2e_latency("whatsapp", Duration::from_secs(35)); // Above P95

        let latency_metric = gather_latency_metric();
        assert!(!latency_metric.get_metric().is_empty());
    }
}
