use axum::{Json, response::IntoResponse, http::StatusCode};
use serde_json::json;
use sqlx::PgPool;

use crate::db::health_check as db_health_check;

/// Basic health check endpoint (does not query database)
pub async fn health_check() -> impl IntoResponse {
    Json(json!({
        "status": "healthy",
        "service": "rust-control-plane",
        "database": "postgresql"
    }))
}

/// Database health check endpoint (queries PostgreSQL and returns pool metrics)
///
/// Returns 503 Service Unavailable if PostgreSQL is down.
/// Returns 200 OK with pool statistics if PostgreSQL is healthy.
pub async fn database_health(pool: PgPool) -> impl IntoResponse {
    match db_health_check(&pool).await {
        Ok(status) => Json(json!({
            "status": "healthy",
            "database": "postgresql",
            "pool": {
                "active_connections": status.active_connections,
                "idle_connections": status.idle_connections
            }
        })).into_response(),
        Err(e) => {
            tracing::error!("Database health check failed: {}", e);
            (
                StatusCode::SERVICE_UNAVAILABLE,
                Json(json!({
                    "status": "unhealthy",
                    "error": "database_connection_failed",
                    "message": e.to_string()
                }))
            ).into_response()
        }
    }
}
