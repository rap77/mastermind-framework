use axum::{extract::Request, http::StatusCode, response::Response, Extension, middleware::Next};
use uuid::Uuid;
use crate::tracing::metadata::TraceMetadata;
use crate::metrics::record_http_request;
use std::time::Instant;

pub async fn inject_trace_middleware(
    mut req: Request,
    next: Next,
) -> Response {
    let trace_id = Uuid::new_v4();
    let request_id = Uuid::new_v4();

    // Store in request extensions for handlers to access
    req.extensions_mut().insert(TraceMetadata {
        trace_id,
        request_id,
        user_id: None, // Extract from JWT if present
    });

    // Record start time
    let start = Instant::now();
    let method = req.method().to_string();
    let path = req.uri().path().to_string();

    // Process request
    let response = next.run(req).await;

    // Record metrics
    let duration = start.elapsed().as_secs_f64();
    record_http_request(&method, &path, duration);

    response
}
