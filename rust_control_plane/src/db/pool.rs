use anyhow::Result;
use sqlx::{postgres::PgPoolOptions, PgPool};
use std::time::Duration;

/// Connect to PostgreSQL with proper connection pooling
///
/// Connection pool configuration:
/// - max_connections: 20 (prevents connection exhaustion)
/// - acquire_timeout: 5s (fail fast if PostgreSQL unavailable)
///
/// # Errors
/// Returns error if:
/// - DATABASE_URL is invalid
/// - PostgreSQL is unreachable
/// - Connection pool cannot be established
pub async fn connect_pool(database_url: &str) -> Result<PgPool> {
    let pool = PgPoolOptions::new()
        .max_connections(20) // Prevent connection exhaustion (Brain #7 validation)
        .acquire_timeout(Duration::from_secs(5)) // Fail fast if PostgreSQL unavailable
        .connect(database_url)
        .await?;

    Ok(pool)
}

/// Health check status for PostgreSQL connection pool
#[derive(Debug, Clone, serde::Serialize)]
pub struct HealthStatus {
    /// Number of active connections in the pool
    pub active_connections: u32,
    /// Number of idle connections in the pool
    pub idle_connections: u32,
}

/// Check PostgreSQL health with pool metrics
///
/// Executes SELECT 1 to verify connectivity and returns pool statistics.
///
/// # Errors
/// Returns error if:
/// - Query execution fails
/// - Connection is broken
pub async fn health_check(pool: &PgPool) -> Result<HealthStatus> {
    let _ = sqlx::query("SELECT 1").execute(pool).await?;

    Ok(HealthStatus {
        active_connections: pool.size() as u32,
        idle_connections: pool.num_idle() as u32,
    })
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_connect_pool_invalid_url() {
        let result = connect_pool("postgresql://invalid:invalid@localhost:9999/invalid").await;
        assert!(result.is_err());
    }

    #[tokio::test]
    async fn test_health_check_query() {
        // This test requires a running PostgreSQL instance
        // Skip in CI if DATABASE_URL not set
        let database_url = std::env::var("DATABASE_URL");
        if database_url.is_err() {
            return;
        }

        let pool = connect_pool(&database_url.unwrap()).await;
        if pool.is_err() {
            return; // Skip if PostgreSQL not running
        }

        let pool = pool.unwrap();
        let status = health_check(&pool).await.unwrap();
        assert_eq!(status.active_connections, 1); // Only this test connection
    }
}
