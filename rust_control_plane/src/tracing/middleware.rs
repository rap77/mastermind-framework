use axum::{extract::Request, http::StatusCode, response::Response, Extension, Next};
use uuid::Uuid;
use crate::tracing::metadata::TraceMetadata;

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

    next.run(req).await
}
