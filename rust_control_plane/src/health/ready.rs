use axum::{extract::State, response::IntoResponse, Json};
use serde_json::json;
use axum::http::StatusCode;
use crate::db::PgPool;

async fn check_postgres(pool: &PgPool) -> Result<(), String> {
    pool.acquire().await
        .map(|_| ())
        .map_err(|e| format!("PostgreSQL: {}", e))
}

async fn check_grpc_python() -> Result<(), String> {
    // TODO: Phase 16-07 will add actual gRPC health check
    Ok(())
}

pub async fn readiness_check(State(pool): State<PgPool>) -> impl IntoResponse {
    let checks = tokio::join!(
        check_postgres(&pool),
        check_grpc_python(),
    );

    let all_healthy = checks.0.is_ok() && checks.1.is_ok();

    if all_healthy {
        (StatusCode::OK, Json(json!({"status": "ready"})))
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, Json(json!({
            "status": "not_ready",
            "postgres": format!("{:?}", checks.0),
            "grpc_python": format!("{:?}", checks.1),
        })))
    }
}
