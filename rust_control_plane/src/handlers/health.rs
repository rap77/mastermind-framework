use axum::{Json, extract::State, response::IntoResponse, http::StatusCode};
use serde_json::{json, Value};

use crate::db::health_check as db_health_check;
use crate::state::AppState;

fn realtime_hub_snapshot(active_connections: usize, active_latency_timers: usize) -> Value {
    json!({
        "status": "healthy",
        "service": "rust-control-plane",
        "realtime_hub": {
            "active_connections": active_connections,
            "active_latency_timers": active_latency_timers
        }
    })
}

/// Basic health check endpoint (does not query database)
///
/// B3.1: Returns {"status": "ok", "service": "rust-control-plane"}
pub async fn health_check() -> impl IntoResponse {
    Json(json!({
        "status": "ok",
        "service": "rust-control-plane"
    }))
}

/// Database health check endpoint (queries PostgreSQL and returns pool metrics)
///
/// Returns 503 Service Unavailable if PostgreSQL is down.
/// Returns 200 OK with pool statistics if PostgreSQL is healthy.
pub async fn db_health(State(state): State<AppState>) -> impl IntoResponse {
    match db_health_check(&state.pool).await {
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

/// Real-time hub health endpoint (WebSocket + latency observability)
pub async fn realtime_health(State(state): State<AppState>) -> impl IntoResponse {
    let active_connections = state.websocket_hub.get_connection_count().await;
    let active_latency_timers = state.latency_tracker.active_count();

    Json(realtime_hub_snapshot(active_connections, active_latency_timers))
}

#[cfg(test)]
mod tests {
    use super::realtime_hub_snapshot;

    #[test]
    fn test_realtime_hub_snapshot_shape() {
        let snapshot = realtime_hub_snapshot(7, 3);

        assert_eq!(snapshot["status"], "healthy");
        assert_eq!(snapshot["service"], "rust-control-plane");
        assert_eq!(snapshot["realtime_hub"]["active_connections"], 7);
        assert_eq!(snapshot["realtime_hub"]["active_latency_timers"], 3);
    }
}
