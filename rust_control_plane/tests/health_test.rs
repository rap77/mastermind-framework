/// Unit tests for the GET /health endpoint.
///
/// Validates:
/// - B3.4: GET /health returns 200 OK
/// - B3.4: Response body contains {"status": "ok", "service": "rust-control-plane"}
use axum::{routing::get, Router};
use axum_test::TestServer;
use rust_control_plane::handlers::health_check;

fn build_test_server() -> TestServer {
    let app: Router = Router::new().route("/health", get(health_check));
    TestServer::new(app).unwrap()
}

/// B3.4: GET /health returns HTTP 200 OK
#[tokio::test]
async fn test_health_returns_200() {
    let server = build_test_server();

    let response = server.get("/health").await;

    response.assert_status_ok();
}

/// B3.4: GET /health body contains required fields
#[tokio::test]
async fn test_health_response_body() {
    let server = build_test_server();

    let response = server.get("/health").await;

    response.assert_status_ok();

    let body: serde_json::Value = response.json();
    assert_eq!(
        body["status"], "ok",
        "status field must be 'ok'"
    );
    assert_eq!(
        body["service"], "rust-control-plane",
        "service field must be 'rust-control-plane'"
    );
}
