use sqlx::PgPool;
use rusqlite::{Connection, params};
use anyhow::{Result, Context};
use std::sync::{Arc, Mutex};
use tokio::task;
use uuid::Uuid;
use serde::Serialize;

pub struct DualWriteRepository {
    pg_pool: Arc<PgPool>,
    sqlite_conn: Arc<Mutex<Connection>>,
}

impl DualWriteRepository {
    pub fn new(pg_pool: Arc<PgPool>, sqlite_path: &str) -> Result<Self> {
        let sqlite_conn = Connection::open(sqlite_path)
            .context("Failed to open SQLite connection")?;
        Ok(Self {
            pg_pool,
            sqlite_conn: Arc::new(Mutex::new(sqlite_conn)),
        })
    }

    /// Write task to both PostgreSQL and PostgreSQL (Saga pattern)
    pub async fn write_task(&self, task: &TaskWrite) -> Result<()> {
        // Write to PostgreSQL first (async, primary source)
        let pg_result = sqlx::query(
            "INSERT INTO tasks (id, brain_id, status, progress, result, error, created_at, updated_at)
             VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
             ON CONFLICT (id) DO UPDATE SET
                brain_id = EXCLUDED.brain_id,
                status = EXCLUDED.status,
                progress = EXCLUDED.progress,
                result = EXCLUDED.result,
                error = EXCLUDED.error,
                updated_at = NOW()",
        )
        .bind(task.id)
        .bind(&task.brain_id)
        .bind(&task.status)
        .bind(task.progress)
        .bind(&task.result)
        .bind(&task.error)
        .execute(&*self.pg_pool)
        .await;

        // If PostgreSQL write fails, abort early (Saga pattern)
        let pg_result = pg_result?;
        let pg_rows_affected = pg_result.rows_affected();

        // Write to SQLite in blocking thread (compensating transaction)
        let sqlite_result = task::spawn_blocking({
            let sqlite_conn = self.sqlite_conn.clone();
            let task = task.clone();
            move || {
                let conn = sqlite_conn.lock().unwrap();
                conn.execute(
                    "INSERT OR REPLACE INTO tasks (id, brain_id, status, progress, result, error, created_at, updated_at)
                     VALUES (?1, ?2, ?3, ?4, ?5, ?6, datetime('now'), datetime('now'))",
                    params![
                        task.id.to_string(),
                        &task.brain_id,
                        &task.status,
                        task.progress.map(|p| p.to_string()),
                        task.result.as_deref(),
                        task.error.as_deref(),
                    ],
                )
            }
        })
        .await
        .map_err(|e| anyhow::anyhow!("SQLite write task failed: {}", e))??;

        // If SQLite write fails, compensate by rolling back PostgreSQL
        if sqlite_result == 0 && pg_rows_affected > 0 {
            // Compensating transaction: remove from PostgreSQL
            sqlx::query("DELETE FROM tasks WHERE id = $1")
                .bind(task.id)
                .execute(&*self.pg_pool)
                .await?;
            return Err(anyhow::anyhow!("SQLite write failed, PostgreSQL write compensated"));
        }

        // Verify both writes succeeded
        if pg_rows_affected == 0 && sqlite_result == 0 {
            return Err(anyhow::anyhow!("Both writes failed (no rows affected)"));
        }

        Ok(())
    }

    /// Read task from PostgreSQL (primary source after migration)
    pub async fn read_task(&self, id: Uuid) -> Result<Option<TaskRead>> {
        let task = sqlx::query_as::<_, TaskRead>(
            "SELECT id, brain_id, status, progress, result, error, created_at, updated_at
             FROM tasks WHERE id = $1",
        )
        .bind(id)
        .fetch_optional(&*self.pg_pool)
        .await?;

        Ok(task)
    }

    /// Verify data consistency between SQLite and PostgreSQL
    pub async fn verify_data_consistency(&self) -> Result<ConsistencyReport> {
        let start = std::time::Instant::now();
        let tables = vec!["tasks", "executions"];
        let mut inconsistencies = Vec::new();
        let mut table_reports = Vec::new();

        for table in tables {
            let pg_count: i64 = sqlx::query_scalar(&format!("SELECT COUNT(*) FROM {}", table))
                .fetch_one(&*self.pg_pool)
                .await?;

            let conn = self.sqlite_conn.lock().unwrap();
            let sqlite_count: i64 = conn
                .query_row(&format!("SELECT COUNT(*) FROM {}", table), [], |row| {
                    row.get(0)
                })
                .unwrap_or(0);

            let is_consistent = pg_count == sqlite_count;
            if !is_consistent {
                inconsistencies.push(format!(
                    "{}: PostgreSQL={}, SQLite={}",
                    table, pg_count, sqlite_count
                ));
            }

            table_reports.push(TableConsistency {
                table_name: table.to_string(),
                pg_count,
                sqlite_count,
                is_consistent,
            });
        }

        let duration_ms = start.elapsed().as_millis();
        let is_healthy = inconsistencies.is_empty();

        Ok(ConsistencyReport {
            tables: table_reports,
            inconsistencies,
            duration_ms,
            is_healthy,
        })
    }
}

#[derive(Debug, Clone, Serialize)]
pub struct TaskWrite {
    pub id: Uuid,
    pub brain_id: String,
    pub status: String,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub progress: Option<f64>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub result: Option<String>,
    #[serde(skip_serializing_if = "Option::is_none")]
    pub error: Option<String>,
}

#[derive(Debug, Serialize, sqlx::FromRow)]
pub struct TaskRead {
    pub id: Uuid,
    pub brain_id: String,
    pub status: String,
    pub progress: Option<serde_json::Value>,
    pub result: Option<serde_json::Value>,
    pub error: Option<String>,
    pub created_at: chrono::DateTime<chrono::Utc>,
    pub updated_at: chrono::DateTime<chrono::Utc>,
}

#[derive(Debug, Serialize)]
pub struct ConsistencyReport {
    pub tables: Vec<TableConsistency>,
    pub inconsistencies: Vec<String>,
    pub duration_ms: u128,
    pub is_healthy: bool,
}

#[derive(Debug, Serialize)]
pub struct TableConsistency {
    pub table_name: String,
    pub pg_count: i64,
    pub sqlite_count: i64,
    pub is_consistent: bool,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_task_write_serialization() {
        let task = TaskWrite {
            id: Uuid::new_v4(),
            brain_id: "brain-01".to_string(),
            status: "pending".to_string(),
            progress: Some(0.5),
            result: None,
            error: None,
        };

        let json = serde_json::to_string(&task).unwrap();
        assert!(json.contains("brain-01"));
    }
}
