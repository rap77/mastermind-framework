use sqlx::{PgPool, postgres::PgRow};
use anyhow::{Result, Context};
use uuid::Uuid;
use chrono::{DateTime, Utc};
use crate::sqlite_reader::SqliteRow;

pub async fn migrate_table(
    pool: &PgPool,
    table_name: &str,
    sqlite_rows: Vec<SqliteRow>,
) -> Result<usize> {
    let mut count = 0;

    for row in sqlite_rows {
        match table_name {
            "users" => {
                // Skip users table for now (handled by RBAC migration)
                continue;
            }
            "sessions" => {
                // Skip sessions table (will be recreated with new auth)
                continue;
            }
            "api_keys" => {
                // Skip api_keys table (not in SQLite)
                continue;
            }
            "tasks" => {
                let brain_id: String = row.get("brain_id").map(|s| s.clone()).unwrap_or_default();
                let status: String = row.get("status").map(|s| s.clone()).unwrap_or_default();
                let progress: Option<f64> = row.get_as_f64("progress");
                let result: Option<String> = row.get("result").map(|s| s.clone());
                let error: Option<String> = row.get("error").map(|s| s.clone());

                sqlx::query(
                    "INSERT INTO tasks (id, brain_id, status, progress, result, error, created_at, updated_at)
                     VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
                     ON CONFLICT (id) DO NOTHING",
                )
                .bind(Uuid::new_v4())
                .bind(&brain_id)
                .bind(&status)
                .bind(progress)
                .bind(&result)
                .bind(&error)
                .execute(pool)
                .await
                .context("Failed to insert task")?;
            }
            "executions" => {
                let id: String = row.get("id").map(|s| s.clone()).unwrap_or_else(|| Uuid::new_v4().to_string());
                let brief: String = row.get("brief").map(|s| s.clone()).unwrap_or_default();
                let flow_config: String = row.get("flow_config").map(|s| s.clone()).unwrap_or_else(|| serde_json::json!({}).to_string());
                let user_id: String = row.get("user_id").map(|s| s.clone()).unwrap_or_default();
                let status: String = row.get("status").map(|s| s.clone()).unwrap_or_default();

                sqlx::query(
                    "INSERT INTO executions (id, brief, flow_config, user_id, status, created_at)
                     VALUES ($1, $2, $3, $4, $5, NOW())
                     ON CONFLICT (id) DO NOTHING",
                )
                .bind(&id)
                .bind(&brief)
                .bind(&flow_config)
                .bind(&user_id)
                .bind(&status)
                .execute(pool)
                .await
                .context("Failed to insert execution")?;
            }
            "experience_records" => {
                // Skip experience_records migration (schema incompatibility)
                // SQLite has: brain_id, source_type, source_id, content, metadata
                // PostgreSQL has: brain_id, session_id, quality_score, insights, patterns
                continue;
            }
            _ => {
                return Err(anyhow::anyhow!("Unknown table: {}", table_name));
            }
        }
        count += 1;
    }

    Ok(count)
}

pub async fn verify_row_counts(
    pool: &PgPool,
    table_name: &str,
    expected_count: usize,
) -> Result<bool> {
    let pg_count: i64 = sqlx::query_scalar(&format!("SELECT COUNT(*) FROM {}", table_name))
        .fetch_one(pool)
        .await?;

    Ok(pg_count as usize == expected_count)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_uuid_generation() {
        let uuid = Uuid::new_v4();
        assert!(uuid.to_string().len() > 0);
    }
}
