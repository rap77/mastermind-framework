use axum::{extract::Request, response::Response, middleware::Next};
use uuid::Uuid;
use tracing::Instrument;
use crate::tracing::metadata::TraceMetadata;
use crate::metrics::record_http_request;
use std::time::Instant;

/// Axum middleware that extracts (or generates) a distributed `trace_id`.
///
/// Priority:
/// 1. `X-Trace-ID` request header, if present and non-empty
/// 2. Fresh UUID v4 generated for this request
///
/// The resolved `trace_id` is:
/// - Stored in request extensions as [`TraceMetadata`]
/// - Used to open a tracing span for the full request lifecycle
pub async fn inject_trace_middleware(
    mut req: Request,
    next: Next,
) -> Response {
    // Extract X-Trace-ID header or fall back to a new UUID v4
    let trace_id = req
        .headers()
        .get("x-trace-id")
        .and_then(|v| v.to_str().ok())
        .filter(|s| !s.is_empty())
        .map(|s| s.to_string())
        .unwrap_or_else(|| Uuid::new_v4().to_string());

    // Record start time and request metadata
    let start = Instant::now();
    let method = req.method().to_string();
    let path = req.uri().path().to_string();

    // Attach metadata to request extensions so downstream handlers and the
    // gRPC interceptor can read the trace_id without touching headers again.
    req.extensions_mut().insert(TraceMetadata::with_trace_id(trace_id.clone()));

    // Create a span for the request so all log events inside carry trace_id
    let span = tracing::info_span!(
        "http_request",
        trace_id = %trace_id,
        method = %method,
        path = %path,
    );

    // Process request inside the span
    let response = next.run(req).instrument(span).await;

    // Record metrics
    let duration = start.elapsed().as_secs_f64();
    record_http_request(&method, &path, duration);

    response
}
