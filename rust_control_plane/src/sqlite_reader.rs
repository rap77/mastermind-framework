use rusqlite::{Connection, Result as SqliteResult, Row};
use anyhow::{Result, Context};
use std::collections::HashMap;

pub struct SqliteReader {
    conn: Connection,
}

impl SqliteReader {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)
            .context(format!("Failed to open SQLite database at: {}", db_path))?;
        Ok(Self { conn })
    }

    pub fn get_row_counts(&self) -> Result<Vec<(String, usize)>> {
        let mut stmt = self.conn.prepare(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
        )?;

        let table_names = stmt.query_map([], |row| {
            Ok(row.get::<_, String>(0)?)
        })?;

        let mut counts = Vec::new();
        for table_name in table_names {
            let table_name = table_name?;
            let count: usize = self.conn.query_row(
                &format!("SELECT COUNT(*) FROM {}", table_name),
                [],
                |row| row.get(0),
            )?;
            counts.push((table_name, count));
        }

        Ok(counts)
    }

    pub fn read_table(&self, table_name: &str) -> Result<Vec<SqliteRow>> {
        let mut stmt = self.conn.prepare(&format!("SELECT * FROM {}", table_name))?;

        let column_count = stmt.column_count();
        let column_names: Vec<String> = stmt
            .column_names()
            .into_iter()
            .map(String::from)
            .collect();

        let rows = stmt.query_map([], |row| {
            let mut values = HashMap::new();
            for (i, col_name) in column_names.iter().enumerate() {
                let value: String = row.get_ref(i)?.as_str()?.to_string();
                values.insert(col_name.clone(), value);
            }
            Ok(SqliteRow {
                table_name: table_name.to_string(),
                columns: column_names.clone(),
                values,
            })
        })?;

        let mut result = Vec::new();
        for row in rows {
            result.push(row?);
        }

        Ok(result)
    }
}

#[derive(Debug, Clone)]
pub struct SqliteRow {
    pub table_name: String,
    pub columns: Vec<String>,
    pub values: HashMap<String, String>,
}

impl SqliteRow {
    pub fn get(&self, column: &str) -> Option<&String> {
        self.values.get(column)
    }

    pub fn get_as_i64(&self, column: &str) -> Option<i64> {
        self.values.get(column)?.parse().ok()
    }

    pub fn get_as_f64(&self, column: &str) -> Option<f64> {
        self.values.get(column)?.parse().ok()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_sqlite_reader_connection() {
        let reader = SqliteReader::new(":memory:");
        assert!(reader.is_ok());
    }

    #[test]
    fn test_get_row_counts_empty_db() {
        let reader = SqliteReader::new(":memory:").unwrap();
        let counts = reader.get_row_counts().unwrap();
        assert_eq!(counts.len(), 0);
    }
}
