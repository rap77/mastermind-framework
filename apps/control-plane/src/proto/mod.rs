// Auto-generated proto types (placeholder until protoc is available)
// TODO: Generate from proto/mastermind/v1/brain_runtime.proto using tonic-build
// Setup blocker: protoc not available in environment, documented in velocity-baseline.md

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DispatchTaskRequest {
    pub brief: String,
    pub user_id: String,
    pub flow: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DispatchTaskResponse {
    pub task_id: String,
    pub status: String,
    pub accepted_at_unix_ms: i64,
}
