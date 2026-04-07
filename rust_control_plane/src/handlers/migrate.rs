use axum::{Json, extract::State, http::StatusCode};
use serde::Serialize;
use std::sync::Arc;
use sqlx::PgPool;
use crate::sqlite_reader::SqliteReader;
use crate::db::migration::{migrate_table, verify_row_counts};
use crate::db::dual_write::{DualWriteRepository, ConsistencyReport};

#[derive(Debug, Serialize)]
pub struct MigrationStats {
    pub sqlite_path: String,
    pub tables: Vec<TableStats>,
    pub total_rows: usize,
}

#[derive(Debug, Serialize)]
pub struct TableStats {
    pub table_name: String,
    pub sqlite_rows: usize,
    pub postgresql_rows: usize,
    pub status: String,  // "migrated", "partial", "pending"
}

/// Inspect SQLite database and return table statistics
pub async fn inspect_sqlite(
    State(pool): State<Arc<PgPool>>,
    State(sqlite_path): State<String>,
) -> Result<Json<MigrationStats>, StatusCode> {
    let reader = SqliteReader::new(&sqlite_path)
        .map_err(|e| {
            tracing::error!("Failed to open SQLite database: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    let tables = reader.get_row_counts()
        .map_err(|e| {
            tracing::error!("Failed to get row counts: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    let mut table_stats = Vec::new();

    for (table_name, sqlite_count) in &tables {
        // Check PostgreSQL count
        let pg_count: i64 = sqlx::query_scalar(
            &format!("SELECT COUNT(*) FROM {}", table_name)
        )
        .fetch_one(&*pool)
        .await
        .map_err(|e| {
            tracing::error!("Failed to count PostgreSQL rows for {}: {}", table_name, e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

        let status = if pg_count as usize == *sqlite_count {
            "migrated".to_string()
        } else if pg_count > 0 {
            "partial".to_string()
        } else {
            "pending".to_string()
        };

        table_stats.push(TableStats {
            table_name: table_name.clone(),
            sqlite_rows: *sqlite_count,
            postgresql_rows: pg_count as usize,
            status,
        });
    }

    let total_rows = tables.iter().map(|t| t.1).sum();

    Ok(Json(MigrationStats {
        sqlite_path,
        tables: table_stats,
        total_rows,
    }))
}

/// Verify data consistency between SQLite and PostgreSQL
pub async fn verify_consistency(
    State(pool): State<Arc<PgPool>>,
    State(sqlite_path): State<String>,
) -> Result<Json<ConsistencyReport>, StatusCode> {
    let dual_write = DualWriteRepository::new(pool, &sqlite_path)
        .map_err(|e| {
            tracing::error!("Failed to create dual-write repo: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    let report = dual_write.verify_data_consistency()
        .await
        .map_err(|e| {
            tracing::error!("Consistency check failed: {}", e);
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    // Log if unhealthy (for alerting)
    if !report.is_healthy {
        tracing::error!(
            "Data inconsistency detected: {:?}",
            report.inconsistencies
        );
    }

    Ok(Json(report))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_table_stats_serialization() {
        let stats = TableStats {
            table_name: "tasks".to_string(),
            sqlite_rows: 100,
            postgresql_rows: 100,
            status: "migrated".to_string(),
        };

        let json = serde_json::to_string(&stats).unwrap();
        assert!(json.contains("tasks"));
        assert!(json.contains("migrated"));
    }
}
