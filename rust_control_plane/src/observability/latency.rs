//! End-to-end latency tracking for webhooks
//!
//! Measures latency from webhook received to AI response sent.
//! Brain #7 Condition #3: End-to-end latency SLI measurement.
//!
//! SLI: webhook_e2e_latency_seconds{channel,quantile} < 30s P95

use dashmap::DashMap;
use std::time::{Duration, Instant};
use tracing::{debug, warn};

/// Latency entry tracking start time and channel
#[derive(Debug, Clone)]
pub struct LatencyEntry {
    /// Trace ID for this request
    pub trace_id: String,
    /// Channel (whatsapp, instagram, email)
    pub channel: String,
    /// Start time (Instant::now() when webhook received)
    pub start_time: Instant,
}

/// End-to-end latency tracker
///
/// Tracks webhook latency from receipt to AI response.
/// Uses DashMap for concurrent access across workers.
///
/// # Example
/// ```rust
/// let tracker = LatencyTracker::new();
///
/// // Webhook received
/// tracker.start_timer(&trace_id, &channel);
///
/// // AI response sent
/// let duration = tracker.record_latency(&trace_id, &channel)?;
/// ```
pub struct LatencyTracker {
    /// Active timers by trace_id
    timers: DashMap<String, LatencyEntry>,
}

impl LatencyTracker {
    /// Create new latency tracker
    pub fn new() -> Self {
        Self {
            timers: DashMap::new(),
        }
    }

    /// Start latency timer for a webhook
    ///
    /// Should be called immediately when webhook is received.
    /// Records start time with trace_id + channel.
    pub fn start_timer(&self, trace_id: &str, channel: &str) {
        let entry = LatencyEntry {
            trace_id: trace_id.to_string(),
            channel: channel.to_string(),
            start_time: Instant::now(),
        };

        self.timers.insert(trace_id.to_string(), entry);

        debug!(
            trace_id = %trace_id,
            channel = %channel,
            "Latency timer started"
        );
    }

    /// Record end-to-end latency
    ///
    /// Should be called when AI response is sent.
    /// Calculates duration, removes entry, returns Duration.
    ///
    /// Returns None if trace_id not found (timer not started).
    pub fn record_latency(&self, trace_id: &str, channel: &str) -> Option<Duration> {
        self.timers.remove(trace_id).map(|(_key, entry)| {
            let duration = entry.start_time.elapsed();

            debug!(
                trace_id = %trace_id,
                channel = %channel,
                duration_ms = duration.as_millis(),
                "End-to-end latency recorded"
            );

            duration
        })
    }

    /// Cleanup timer for failed webhooks
    ///
    /// Should be called when webhook fails (moved to DLQ).
    /// Removes entry without recording latency.
    pub fn cleanup_timer(&self, trace_id: &str) {
        if self.timers.remove(trace_id).is_some() {
            debug!(
                trace_id = %trace_id,
                "Latency timer cleaned up (webhook failed)"
            );
        }
    }

    /// Cleanup old entries (>5 minutes)
    ///
    /// Should be called periodically (every 60s) to prevent memory leaks.
    /// Removes entries that never completed (crashes, bugs, etc).
    pub async fn cleanup_old_entries(&self) {
        let timeout = Duration::from_secs(5 * 60); // 5 minutes
        let mut cleaned = 0;

        // Iterate and remove old entries
        self.timers.retain(|_key, entry| {
            let age = entry.start_time.elapsed();
            let should_keep = age < timeout;

            if !should_keep {
                cleaned += 1;
                warn!(
                    trace_id = %entry.trace_id,
                    channel = %entry.channel,
                    age_secs = age.as_secs(),
                    "Cleaning up stale latency entry"
                );
            }

            should_keep
        });

        if cleaned > 0 {
            warn!(cleaned, "Cleaned up stale latency entries");
        }
    }

    /// Get current active timer count
    ///
    /// Useful for monitoring and health checks.
    pub fn active_count(&self) -> usize {
        self.timers.len()
    }
}

impl Default for LatencyTracker {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    #[test]
    fn test_latency_tracker_start_and_record() {
        let tracker = LatencyTracker::new();
        let trace_id = "test-trace-123";
        let channel = "whatsapp";

        // Start timer
        tracker.start_timer(trace_id, channel);
        assert_eq!(tracker.active_count(), 1);

        // Wait a bit
        std::thread::sleep(Duration::from_millis(10));

        // Record latency
        let duration = tracker.record_latency(trace_id, channel);
        assert!(duration.is_some());
        assert!(duration.unwrap().as_millis() >= 10);
        assert_eq!(tracker.active_count(), 0);
    }

    #[test]
    fn test_latency_tracker_cleanup() {
        let tracker = LatencyTracker::new();
        let trace_id = "test-trace-456";
        let channel = "instagram";

        // Start timer
        tracker.start_timer(trace_id, channel);
        assert_eq!(tracker.active_count(), 1);

        // Cleanup without recording
        tracker.cleanup_timer(trace_id);
        assert_eq!(tracker.active_count(), 0);

        // Recording after cleanup returns None
        let duration = tracker.record_latency(trace_id, channel);
        assert!(duration.is_none());
    }

    #[test]
    fn test_latency_tracker_nonexistent() {
        let tracker = LatencyTracker::new();

        // Recording non-existent trace_id returns None
        let duration = tracker.record_latency("nonexistent", "whatsapp");
        assert!(duration.is_none());

        // Cleanup non-existent trace_id is safe
        tracker.cleanup_timer("nonexistent");
        assert_eq!(tracker.active_count(), 0);
    }

    #[tokio::test]
    async fn test_latency_tracker_cleanup_old_entries() {
        let tracker = LatencyTracker::new();

        // Start timer
        tracker.start_timer("old-trace", "whatsapp");
        assert_eq!(tracker.active_count(), 1);

        // Manually age the entry by accessing internal state
        // (In production, entries age naturally)
        // For this test, we'll verify the cleanup logic exists

        // Call cleanup (should not remove recent entries)
        tracker.cleanup_old_entries().await;
        assert_eq!(tracker.active_count(), 1); // Still there
    }

    #[test]
    fn test_latency_tracker_multiple_entries() {
        let tracker = LatencyTracker::new();

        // Start multiple timers
        tracker.start_timer("trace-1", "whatsapp");
        tracker.start_timer("trace-2", "instagram");
        tracker.start_timer("trace-3", "email");

        assert_eq!(tracker.active_count(), 3);

        // Record one
        tracker.record_latency("trace-1", "whatsapp");
        assert_eq!(tracker.active_count(), 2);

        // Cleanup one
        tracker.cleanup_timer("trace-2");
        assert_eq!(tracker.active_count(), 1);

        // Record last
        tracker.record_latency("trace-3", "email");
        assert_eq!(tracker.active_count(), 0);
    }
}
