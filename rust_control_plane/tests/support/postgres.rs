use std::env;

use anyhow::{bail, Context, Result};
use sqlx::{postgres::PgPoolOptions, PgPool};

pub async fn test_pool() -> Result<PgPool> {
    let test_database_url = env::var("TEST_DATABASE_URL")
        .context("TEST_DATABASE_URL must name a dedicated disposable PostgreSQL database")?;

    if test_database_url.trim().is_empty() {
        bail!("TEST_DATABASE_URL must not be empty");
    }

    if env::var("DATABASE_URL").as_deref() == Ok(test_database_url.as_str()) {
        bail!("TEST_DATABASE_URL must differ from DATABASE_URL");
    }

    let pool = PgPoolOptions::new()
        .max_connections(5)
        .connect(&test_database_url)
        .await
        .context("failed to connect to TEST_DATABASE_URL")?;

    sqlx::migrate!("./migrations/messaging")
        .run(&pool)
        .await
        .context("failed to apply checked-in messaging migrations to TEST_DATABASE_URL")?;

    Ok(pool)
}
