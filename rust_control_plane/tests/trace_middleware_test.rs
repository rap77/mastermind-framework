/// Unit tests for the distributed trace middleware.
///
/// Validates:
/// - B1.2: Request with `X-Trace-ID` header → TraceMetadata stores that id
/// - B1.3: Request without header → TraceMetadata stores a fresh UUID v4
use axum::{
    http::header::{HeaderName, HeaderValue},
    middleware,
    response::IntoResponse,
    routing::get,
    Router,
};
use axum_test::TestServer;

use rust_control_plane::tracing::{inject_trace_middleware, metadata::TraceMetadata};

/// Leaf handler that reads the injected TraceMetadata from extensions and
/// returns the `trace_id` as the response body.
async fn echo_trace_id_handler(req: axum::extract::Request) -> impl IntoResponse {
    let trace_id = req
        .extensions()
        .get::<TraceMetadata>()
        .map(|md| md.trace_id.clone())
        .unwrap_or_else(|| "missing".to_string());
    trace_id
}

fn build_test_server() -> TestServer {
    let app: Router = Router::new()
        .route("/ping", get(echo_trace_id_handler))
        .layer(middleware::from_fn(inject_trace_middleware));
    TestServer::new(app).unwrap()
}

/// B1.2 + B1.3: When `X-Trace-ID: test-abc` header is present, the middleware
/// must extract it and make it available via TraceMetadata extensions.
#[tokio::test]
async fn test_trace_id_extracted_from_header() {
    let server = build_test_server();

    let response = server
        .get("/ping")
        .add_header(
            HeaderName::from_static("x-trace-id"),
            HeaderValue::from_static("test-abc"),
        )
        .await;

    response.assert_status_ok();
    let body = response.text();
    assert_eq!(body, "test-abc", "trace_id must equal the X-Trace-ID header value");
}

/// B1.3: When no `X-Trace-ID` header is present, the middleware must generate
/// a fresh UUID v4 (non-empty, valid UUID format).
#[tokio::test]
async fn test_trace_id_generated_when_no_header() {
    let server = build_test_server();

    let response = server.get("/ping").await;

    response.assert_status_ok();
    let body = response.text();

    // Must be a valid UUID v4
    let parsed = uuid::Uuid::parse_str(&body);
    assert!(
        parsed.is_ok(),
        "auto-generated trace_id must be a valid UUID v4, got: {body}"
    );
    assert_eq!(
        parsed.unwrap().get_version(),
        Some(uuid::Version::Random),
        "auto-generated trace_id must be UUID version 4"
    );
}

/// B1.2: Empty string in X-Trace-ID header must be treated as absent →
/// the middleware should generate a fresh UUID instead of using an empty string.
#[tokio::test]
async fn test_empty_trace_id_header_falls_back_to_uuid() {
    let server = build_test_server();

    let response = server
        .get("/ping")
        .add_header(
            HeaderName::from_static("x-trace-id"),
            HeaderValue::from_static(""),
        )
        .await;

    response.assert_status_ok();
    let body = response.text();

    let parsed = uuid::Uuid::parse_str(&body);
    assert!(
        parsed.is_ok(),
        "empty X-Trace-ID must fall back to a valid UUID, got: {body}"
    );
}
