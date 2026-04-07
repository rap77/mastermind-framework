// Database module for PostgreSQL connection pool

pub mod models;
pub mod pool;
pub mod migration;
pub mod dual_write;

pub use models::{User, Session, ApiKey, Task, Execution, ExperienceRecord, ActivityLog};
pub use pool::{connect_pool, health_check, HealthStatus};
pub use migration::{migrate_table, verify_row_counts};
pub use dual_write::{DualWriteRepository, TaskWrite, TaskRead, ConsistencyReport};

// Re-export PgPool for convenience
pub use sqlx::PgPool;
