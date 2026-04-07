// Authentication endpoints: login, refresh, logout
// Matches Python FastAPI auth behavior

use axum::{extract::State, http::StatusCode, Json};
use uuid::Uuid;
use bcrypt;

use crate::auth::models::{User, LoginRequest, RefreshRequest, TokenResponse};
use crate::auth::jwt::{generate_access_token, generate_refresh_token, verify_password};
use crate::auth::rotation::{rotate_refresh_token, store_refresh_token, revoke_all_tokens};
use crate::auth::middleware::AuthenticatedRequest;
use crate::state::AppState;

/// Login endpoint - validates credentials and returns tokens
pub async fn login(
    State(state): State<AppState>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<TokenResponse>, StatusCode> {
    // Find user by username
    let row = sqlx::query!(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE username = $1",
        req.username
    )
    .fetch_optional(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    .ok_or(StatusCode::UNAUTHORIZED)?;

    let user = User {
        id: row.id,
        username: row.username,
        password_hash: row.password_hash,
        role: row.role.parse().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?,
        created_at: row.created_at.expect("created_at should not be NULL"),
    };

    // Verify password
    if !verify_password(&req.password, &user.password_hash)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    {
        return Err(StatusCode::UNAUTHORIZED);
    }

    // Generate tokens
    let access_token = generate_access_token(&user, &state.jwt_secret)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    let refresh_token = generate_refresh_token();

    // Store refresh token in sessions
    store_refresh_token(&state.pool, user.id, &refresh_token)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(TokenResponse {
        access_token,
        refresh_token,
        token_type: "Bearer".to_string(),
        expires_in: 1800, // 30 minutes
    }))
}

/// Refresh endpoint - rotates refresh token and returns new access token
pub async fn refresh(
    State(state): State<AppState>,
    Json(req): Json<RefreshRequest>,
) -> Result<Json<TokenResponse>, StatusCode> {
    // Hash provided token and find session
    let refresh_hash = bcrypt::hash(&req.refresh_token, bcrypt::DEFAULT_COST)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let session = sqlx::query!(
        "SELECT user_id FROM sessions WHERE refresh_token_hash = $1 AND expires_at > NOW()",
        refresh_hash
    )
    .fetch_optional(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    .ok_or(StatusCode::UNAUTHORIZED)?;

    // Get user
    let row = sqlx::query!(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE id = $1",
        session.user_id
    )
    .fetch_one(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let user = User {
        id: row.id,
        username: row.username,
        password_hash: row.password_hash,
        role: row.role.parse().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?,
        created_at: row.created_at.expect("created_at should not be NULL"),
    };

    // Rotate refresh token (delete old, create new)
    let new_refresh_token = generate_refresh_token();
    rotate_refresh_token(&state.pool, user.id, &refresh_hash, &new_refresh_token)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    // Generate new access token
    let access_token = generate_access_token(&user, &state.jwt_secret)
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(TokenResponse {
        access_token,
        refresh_token: new_refresh_token,
        token_type: "Bearer".to_string(),
        expires_in: 1800, // 30 minutes
    }))
}

/// Logout endpoint - revokes all refresh tokens for user
pub async fn logout(
    State(state): State<AppState>,
) -> Result<StatusCode, StatusCode> {
    // TODO: Extract user_id from request extensions
    // For now, this is a placeholder
    Err(StatusCode::NOT_IMPLEMENTED)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_login_request_deserialization() {
        let json = r#"{"username":"test","password":"pass"}"#;
        let req: LoginRequest = serde_json::from_str(json).unwrap();
        assert_eq!(req.username, "test");
        assert_eq!(req.password, "pass");
    }

    #[test]
    fn test_refresh_request_deserialization() {
        let json = r#"{"refresh_token":"abc123"}"#;
        let req: RefreshRequest = serde_json::from_str(json).unwrap();
        assert_eq!(req.refresh_token, "abc123");
    }
}
