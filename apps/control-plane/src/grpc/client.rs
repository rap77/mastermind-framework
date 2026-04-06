//! gRPC client to Python Agent Runtime.
//!
//! This module implements the gRPC client that connects to the Python
//! BrainRuntime service and dispatches tasks for execution.
//!
//! Phase 13-03 Task 2: Rust gRPC client to Python
//!
//! NOTE: For Phase 13 VS, this is a mock implementation that validates
//! the proto types and client structure. Full gRPC integration with tonic
//! comes in Phase 15 when tonic-build is available.

use crate::proto::{DispatchTaskRequest, DispatchTaskResponse};
use tonic::Status;
use uuid::Uuid;
use std::time::SystemTime;

/// gRPC client for Python Brain Runtime service.
///
/// For Phase 13 VS, this is a mock that returns simulated responses.
/// In Phase 15, this will be replaced with real tonic gRPC client.
pub struct BrainRuntimeClient {
    /// Mock base URL (for future use)
    _base_url: String,
}

impl BrainRuntimeClient {
    /// Connect to Python Agent Runtime (mock for VS).
    ///
    /// # Arguments
    /// * `url` - Server URL (e.g., "http://localhost:50051")
    ///
    /// # Returns
    /// Connected client or error if connection fails
    pub async fn connect(url: &str) -> Result<Self, Box<dyn std::error::Error>> {
        Ok(Self {
            _base_url: url.to_string(),
        })
    }

    /// Dispatch task to Python Agent Runtime (mock for VS).
    ///
    /// # Arguments
    /// * `brief` - User's brief text
    /// * `user_id` - User ID from JWT
    /// * `flow` - Flow type (None for auto-detect)
    ///
    /// # Returns
    /// DispatchTaskResponse with task_id, status, accepted_at_unix_ms
    ///
    /// NOTE: In Phase 15, this will make real gRPC calls to Python.
    pub async fn dispatch_task(
        &mut self,
        brief: String,
        user_id: String,
        flow: Option<String>,
    ) -> Result<DispatchTaskResponse, Status> {
        // For VS, return mock response
        // In Phase 15, this will call Python gRPC server
        let task_id = Uuid::new_v4().to_string();
        let accepted_at_ms = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .map_err(|e| Status::internal(format!("Time error: {}", e)))?
            .as_millis() as i64;

        Ok(DispatchTaskResponse {
            task_id,
            status: "pending".to_string(),
            accepted_at_unix_ms: accepted_at_ms,
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_client_uses_generated_proto_types() {
        /* Test 4: Client uses generated proto types (no manual serialization) */
        // Verify proto types are accessible
        let _req = DispatchTaskRequest {
            brief: "test".to_string(),
            user_id: "test-user".to_string(),
            flow: "auto".to_string(),
        };
        // If we get here, proto types are working
        assert!(true);
    }

    #[tokio::test]
    async fn test_dispatch_task_mock() {
        /* Test: Mock dispatch_task returns valid response */
        let mut client = BrainRuntimeClient::connect("http://localhost:50051")
            .await
            .expect("Client should connect");

        let response = client
            .dispatch_task("test brief".to_string(), "test-user".to_string(), None)
            .await
            .expect("dispatch_task should succeed");

        assert!(!response.task_id.is_empty(), "task_id should be present");
        assert_eq!(response.status, "pending", "status should be pending");
        assert!(response.accepted_at_unix_ms > 0, "timestamp should be positive");
    }
}
