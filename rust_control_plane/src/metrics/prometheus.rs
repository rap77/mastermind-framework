use prometheus::{Counter, Histogram, Gauge, Registry, TextEncoder, Opts, HistogramOpts, IntGauge};
use lazy_static::lazy_static;
use axum::{
    response::{IntoResponse, Response},
    http::{StatusCode, header},
    body::Body,
};
use std::sync::Mutex;

lazy_static! {
    static ref REGISTRY: Registry = Registry::new();
    static ref HTTP_REQUESTS_TOTAL: Counter = {
        let opts = Opts::new("http_requests_total", "Total HTTP requests");
        let counter = Counter::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(counter.clone())).unwrap();
        counter
    };
    static ref HTTP_REQUEST_DURATION: Histogram = {
        let opts = HistogramOpts::new("http_request_duration_seconds", "HTTP request latency");
        let histogram = Histogram::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(histogram.clone())).unwrap();
        histogram
    };
    static ref WEBSOCKET_CONNECTIONS: Gauge = {
        let opts = Opts::new("websocket_connections_active", "Active WebSocket connections");
        let gauge = Gauge::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(gauge.clone())).unwrap();
        gauge
    };

    // Brain #7 Condition #2: Queue Depth Monitoring
    static ref WEBHOOK_QUEUE_DEPTH_PERCENT: IntGauge = {
        let opts = Opts::new("webhook_queue_depth_percent", "Webhook queue depth as percentage (0-100)");
        let gauge = IntGauge::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(gauge.clone())).unwrap();
        gauge
    };
    static ref WEBHOOK_QUEUE_CAPACITY: IntGauge = {
        let opts = Opts::new("webhook_queue_capacity", "Webhook queue total capacity");
        let gauge = IntGauge::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(gauge.clone())).unwrap();
        gauge
    };
    static ref WEBHOOK_QUEUE_REJECTION_TOTAL: IntGauge = {
        let opts = Opts::new("webhook_queue_rejection_total", "Total webhooks rejected due to queue depth > 90%");
        let gauge = IntGauge::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(gauge.clone())).unwrap();
        gauge
    };
    static ref WEBHOOK_PENDING_TOTAL: IntGauge = {
        let opts = Opts::new("webhook_pending_total", "Number of webhooks pending in memory queue");
        let gauge = IntGauge::with_opts(opts).unwrap();
        REGISTRY.register(Box::new(gauge.clone())).unwrap();
        gauge
    };
}

/// Record an HTTP request
pub fn record_http_request(method: &str, path: &str, duration: f64) {
    HTTP_REQUESTS_TOTAL.inc();
    HTTP_REQUEST_DURATION.observe(duration);
}

/// Increment WebSocket connection count
pub fn inc_websocket_connections() {
    WEBSOCKET_CONNECTIONS.inc();
}

/// Decrement WebSocket connection count
pub fn dec_websocket_connections() {
    WEBSOCKET_CONNECTIONS.dec();
}

/// Update queue depth metrics (Brain #7 Condition #2)
pub fn update_queue_metrics(depth_percent: f64, capacity: usize, pending: usize) {
    WEBHOOK_QUEUE_DEPTH_PERCENT.set(depth_percent as i64);
    WEBHOOK_QUEUE_CAPACITY.set(capacity as i64);
    WEBHOOK_PENDING_TOTAL.set(pending as i64);
}

/// Increment rejection counter (Brain #7 Condition #2)
pub fn increment_rejection_counter() {
    WEBHOOK_QUEUE_REJECTION_TOTAL.inc();
}

/// Metrics endpoint handler
pub async fn metrics_endpoint() -> Response {
    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();

    match encoder.encode_to_string(&metric_families) {
        Ok(metrics_text) => {
            Response::builder()
                .status(StatusCode::OK)
                .header(header::CONTENT_TYPE, "text/plain; version=0.0.4; charset=utf-8")
                .body(Body::from(metrics_text))
                .unwrap()
        }
        Err(e) => {
            tracing::error!("Failed to encode metrics: {}", e);
            Response::builder()
                .status(StatusCode::INTERNAL_SERVER_ERROR)
                .header(header::CONTENT_TYPE, "text/plain")
                .body(Body::from(format!("Failed to encode metrics: {}", e)))
                .unwrap()
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_metrics_registry() {
        // Verify metrics are registered
        let metrics = REGISTRY.gather();
        assert!(!metrics.is_empty());
    }

    #[test]
    fn test_http_request_metrics() {
        // Record a request
        record_http_request("GET", "/api/test", 0.123);

        // Verify counter incremented
        let metric_families = REGISTRY.gather();
        let http_metric = metric_families
            .iter()
            .find(|m| m.get_name() == "http_requests_total")
            .expect("http_requests_total metric not found");

        assert!(http_metric.get_metric().len() > 0);
    }

    #[test]
    fn test_websocket_gauge() {
        let initial = WEBSOCKET_CONNECTIONS.get();

        // Increment
        inc_websocket_connections();
        assert_eq!(WEBSOCKET_CONNECTIONS.get(), initial + 1.0);

        // Decrement
        dec_websocket_connections();
        assert_eq!(WEBSOCKET_CONNECTIONS.get(), initial);
    }
}
