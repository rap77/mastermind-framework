//! PostgreSQL models for executions table.
//!
//! This module defines the data structures that map to the PostgreSQL
//! executions table created in Phase 13-01.
//!
//! Phase 13-03 Task 3: PostgreSQL repository in Rust

use serde::{Deserialize, Serialize};
use sqlx::FromRow;

/// Execution record from PostgreSQL executions table.
///
/// Represents a single task execution in the system.
#[derive(Debug, Serialize, Deserialize, FromRow)]
pub struct Execution {
    /// Execution ID (UUID)
    pub id: String,
    /// User's brief text
    pub brief: String,
    /// Flow configuration (JSON or flow name)
    pub flow_config: String,
    /// User ID from JWT
    pub user_id: String,
    /// Execution status (pending, running, completed, failed)
    pub status: String,
    /// Creation timestamp
    pub created_at: chrono::DateTime<chrono::Utc>,
}
