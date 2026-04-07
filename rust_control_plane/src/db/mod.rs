// Database module for PostgreSQL connection pool

pub mod models;
pub mod pool;

pub use models::{User, Session, ApiKey, Task, Execution, ExperienceRecord, ActivityLog};
pub use pool::{connect_pool, health_check, HealthStatus};

// Re-export PgPool for convenience
pub use sqlx::PgPool;
