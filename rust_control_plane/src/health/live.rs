use axum::{response::IntoResponse, Json};
use serde_json::json;
use axum::http::StatusCode;

pub async fn liveness_probe() -> impl IntoResponse {
    // Check Tokio event loop responsiveness
    let start = std::time::Instant::now();
    tokio::task::yield_now().await;
    let elapsed = start.elapsed();

    if elapsed.as_secs() < 1 {
        (StatusCode::OK, Json(json!({"status": "alive"})))
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, Json(json!({"status": "degraded"})))
    }
}
