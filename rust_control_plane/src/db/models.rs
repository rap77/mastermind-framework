use chrono::{DateTime, Utc};
use serde_json::Value;
use sqlx::FromRow;
use uuid::Uuid;

/// User account with password hash
#[derive(Debug, Clone, FromRow)]
pub struct User {
    pub id: Uuid,
    pub username: String,
    pub password_hash: String,
    pub role: String, // "admin" or "user" (Brain #7 validation: removed org_admin)
    pub created_at: DateTime<Utc>,
}

/// Session for JWT refresh token rotation
#[derive(Debug, Clone, FromRow)]
pub struct Session {
    pub id: Uuid,
    pub user_id: Uuid,
    pub refresh_token_hash: String,
    pub created_at: DateTime<Utc>,
    pub expires_at: DateTime<Utc>,
    pub rotation_count: i32,
}

/// API key for CLI access
#[derive(Debug, Clone, FromRow)]
pub struct ApiKey {
    pub key_hash: String,
    pub owner: String,
    pub created_at: DateTime<Utc>,
    pub is_active: bool,
    pub scopes: Value, // JSONB stored as serde_json::Value
}

/// Task execution state
#[derive(Debug, Clone, FromRow)]
pub struct Task {
    pub id: Uuid,
    pub brain_id: String,
    pub status: String,
    pub progress: Option<Value>, // JSONB
    pub result: Option<Value>,   // JSONB
    pub error: Option<String>,
    pub created_at: DateTime<Utc>,
    pub updated_at: DateTime<Utc>,
}

/// Execution flow configuration
#[derive(Debug, Clone, FromRow)]
pub struct Execution {
    pub id: Uuid,
    pub flow_config: Value,  // JSONB
    pub brief: String,
    pub created_at: DateTime<Utc>,
    pub status: String,
    pub user_id: Option<Uuid>,
}

/// Experience record from brain execution (Phase 14)
#[derive(Debug, Clone, FromRow)]
pub struct ExperienceRecord {
    pub id: Uuid,
    pub brain_id: String,
    pub session_id: Uuid,
    pub quality_score: Option<f64>,
    pub insights: Option<Value>, // JSONB
    pub patterns: Option<Value>, // JSONB
    pub created_at: DateTime<Utc>,
}

/// Activity log event for event sourcing (RCP-03)
#[derive(Debug, Clone, FromRow)]
pub struct ActivityLog {
    pub id: Uuid,
    pub brain_id: String,
    pub event_type: String, // 'brain_started', 'brain_completed', 'brain_routed', 'brain_failed'
    pub payload: Value,     // JSONB
    pub created_at: DateTime<Utc>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_user_sync() {
        // Verify User is Send + Sync (required for async)
        fn assert_send_sync<T: Send + Sync>() {}
        assert_send_sync::<User>();
    }

    #[test]
    fn test_activity_log_sync() {
        // Verify ActivityLog is Send + Sync
        fn assert_send_sync<T: Send + Sync>() {}
        assert_send_sync::<ActivityLog>();
    }
}
