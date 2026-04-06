//! Axum handlers for task endpoints.
//!
//! This module implements the HTTP handlers for task-related endpoints,
//! including POST /api/tasks/auto which dispatches tasks to the Python
//! Agent Runtime via gRPC.
//!
//! Phase 13-03 Task 4: Axum handler for POST /api/tasks/auto

use axum::{
    extract::State,
    Json,
    http::{HeaderMap, StatusCode},
};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::grpc::client::BrainRuntimeClient;
use crate::postgres::repo::ExecutionRepo;

/// Request body for POST /api/tasks/auto.
#[derive(Debug, Deserialize)]
pub struct AutoTaskRequest {
    /// User's brief text
    pub brief: String,
}

/// Response body for POST /api/tasks/auto.
#[derive(Debug, Serialize)]
pub struct AutoTaskResponse {
    /// Task ID (UUID)
    pub task_id: String,
    /// Task status
    pub status: String,
    /// Flow type
    pub flow: String,
}

/// Shared state for handlers.
///
/// Contains gRPC client and PostgreSQL repository.
#[derive(Clone)]
pub struct AppState {
    /// gRPC client to Python Agent Runtime
    pub grpc_client: Arc<tokio::sync::Mutex<BrainRuntimeClient>>,
    /// PostgreSQL repository
    pub repo: Arc<ExecutionRepo>,
}

/// POST /api/tasks/auto handler.
///
/// Dispatches task to Python Agent Runtime via gRPC and creates
/// execution record in PostgreSQL.
///
/// # Arguments
/// * `State(state)` - Application state with gRPC client and repo
/// * `headers` - HTTP headers (for JWT extraction)
/// * `Json(request)` - Request body with brief
///
/// # Returns
/// JSON response with task_id, status, flow
pub async fn create_auto_task(
    State(state): State<AppState>,
    headers: HeaderMap,
    Json(request): Json<AutoTaskRequest>,
) -> Result<Json<AutoTaskResponse>, StatusCode> {
    // TODO: JWT validation (Phase 15)
    // For VS, extract user_id from mock header
    let user_id = headers
        .get("x-mock-user-id")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("test-user");

    // Call Python via gRPC
    let mut grpc_client = state.grpc_client.lock().await;
    let grpc_response = grpc_client
        .dispatch_task(request.brief.clone(), user_id.to_string(), None)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // Create execution in PostgreSQL
    let repo = state.repo.as_ref();
    repo.create_execution(
        &request.brief,
        user_id,
        &grpc_response.task_id, // Using task_id as flow for now
    )
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(AutoTaskResponse {
        task_id: grpc_response.task_id,
        status: grpc_response.status,
        flow: "auto".to_string(), // TODO: Extract from response
    }))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_request_struct() {
        /* Test: Request struct is valid */
        let req = AutoTaskRequest {
            brief: "test brief".to_string(),
        };
        assert_eq!(req.brief, "test brief");
    }

    #[tokio::test]
    async fn test_response_struct() {
        /* Test: Response struct is valid */
        let resp = AutoTaskResponse {
            task_id: "123".to_string(),
            status: "pending".to_string(),
            flow: "auto".to_string(),
        };
        assert_eq!(resp.task_id, "123");
        assert_eq!(resp.status, "pending");
        assert_eq!(resp.flow, "auto");
    }
}
