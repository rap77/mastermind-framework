use axum::{
    extract::{Path, Query, State},
    http::StatusCode,
    Json,
    response::IntoResponse,
};
use serde::{Deserialize, Serialize};
use crate::state::AppState;

#[derive(Debug, Serialize, Deserialize)]
pub struct FailedWebhook {
    id: String,
    channel: String,
    payload: serde_json::Value,
    error_message: String,
    failed_at: String,
    retry_count: u32,
}

#[derive(Debug, Deserialize)]
pub struct ListQueryParams {
    #[serde(default = "default_limit")]
    limit: usize,
    #[serde(default)]
    offset: usize,
}

fn default_limit() -> usize {
    100
}

#[derive(Debug, Serialize)]
pub struct ListResponse {
    webhooks: Vec<FailedWebhook>,
    total: usize,
}

/// List failed webhooks from DLQ with pagination
pub async fn list_failed_webhooks(
    State(state): State<AppState>,
    Query(params): Query<ListQueryParams>,
) -> Result<Json<ListResponse>, StatusCode> {
    // TODO: Implement actual DLQ query from database
    // For now, return empty list as stub
    ::tracing::info!("Listing DLQ webhooks: limit={}, offset={}", params.limit, params.offset);

    let response = ListResponse {
        webhooks: vec![],
        total: 0,
    };

    Ok(Json(response))
}

#[derive(Debug, Serialize)]
pub struct RetryResponse {
    message: String,
    webhook_id: String,
}

/// Retry a failed webhook from DLQ
pub async fn retry_webhook(
    State(state): State<AppState>,
    Path(id): Path<String>,
) -> Result<Json<RetryResponse>, StatusCode> {
    // TODO: Implement actual retry logic
    // 1. Fetch webhook from DLQ by ID
    // 2. Validate it exists (return 404 if not)
    // 3. Resubmit to processing queue
    // 4. Return 202 Accepted on success

    ::tracing::info!("Retrying webhook: id={}", id);

    // Stub: always return 404 for now
    Err(StatusCode::NOT_FOUND)
}
