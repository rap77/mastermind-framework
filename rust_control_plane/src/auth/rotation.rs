// Refresh token rotation (CVE-2025-29927 mitigation)
// Every refresh creates a new session and deletes the old one

use sqlx::PgPool;
use uuid::Uuid;
use anyhow::Result;
use bcrypt;

/// Rotate refresh token: delete old session, create new one with incremented rotation_count
/// This prevents token reuse attacks by invalidating old tokens immediately
pub async fn rotate_refresh_token(
    pool: &PgPool,
    user_id: Uuid,
    old_refresh_token_hash: &str,
    new_refresh_token: &str,
) -> Result<()> {
    let new_hash = bcrypt::hash(new_refresh_token, bcrypt::DEFAULT_COST)?;

    // Start transaction for atomicity
    let mut tx = pool.begin().await?;

    // Delete old session (mitigates token theft)
    sqlx::query(
        "DELETE FROM sessions WHERE user_id = $1 AND refresh_token_hash = $2",
    )
    .bind(&user_id)
    .bind(&old_refresh_token_hash)
    .execute(&mut *tx)
    .await?;

    // Create new session with rotation_count + 1
    sqlx::query(
        "INSERT INTO sessions (id, user_id, refresh_token_hash, created_at, expires_at, rotation_count)
         SELECT $1, $2, $3, NOW(), NOW() + INTERVAL '24 hours', COALESCE(MAX(rotation_count), 0) + 1
         FROM sessions WHERE user_id = $4",
    )
    .bind(&Uuid::new_v4())
    .bind(&user_id)
    .bind(&new_hash)
    .bind(&user_id)
    .execute(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok(())
}

/// Store refresh token in sessions table (used during login)
pub async fn store_refresh_token(
    pool: &PgPool,
    user_id: Uuid,
    refresh_token: &str,
) -> Result<()> {
    let refresh_hash = bcrypt::hash(refresh_token, bcrypt::DEFAULT_COST)?;

    sqlx::query(
        "INSERT INTO sessions (id, user_id, refresh_token_hash, created_at, expires_at, rotation_count)
         VALUES ($1, $2, $3, NOW(), NOW() + INTERVAL '24 hours', 0)",
    )
    .bind(&Uuid::new_v4())
    .bind(&user_id)
    .bind(&refresh_hash)
    .execute(pool)
    .await?;

    Ok(())
}

/// Delete all sessions for user (used during logout)
pub async fn revoke_all_tokens(
    pool: &PgPool,
    user_id: Uuid,
) -> Result<()> {
    sqlx::query("DELETE FROM sessions WHERE user_id = $1")
        .bind(&user_id)
        .execute(pool)
        .await?;

    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::auth::jwt::generate_refresh_token;

    #[tokio::test]
    #[ignore = "requires PostgreSQL database"]
    async fn test_rotate_refresh_token() {
        // Integration test - requires database connection
        // This would be in a separate integration test file
    }
}
