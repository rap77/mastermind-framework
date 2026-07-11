// Authentication endpoints: login, refresh, logout
// Matches Python FastAPI auth behavior

use axum::{extract::{Request, State}, http::StatusCode, Json};
use uuid::Uuid;

use crate::auth::models::{User, LoginRequest, RefreshRequest, TokenResponse};
use crate::auth::jwt::{generate_access_token, generate_refresh_token, hash_refresh_token, verify_password};
use crate::auth::rotation::{rotate_refresh_token, store_refresh_token, revoke_all_tokens};
use crate::auth::middleware::AuthenticatedRequest;
use crate::state::AppState;

#[cfg(test)]
use axum::body::Body;

#[derive(Debug, sqlx::FromRow)]
struct ActiveSessionRow {
    user_id: Uuid,
    refresh_token_hash: String,
}

fn extract_authenticated_request(
    req: &Request,
) -> Result<&AuthenticatedRequest, StatusCode> {
    req.extensions()
        .get::<AuthenticatedRequest>()
        .ok_or(StatusCode::UNAUTHORIZED)
}

/// Login endpoint - validates credentials and returns tokens
pub async fn login(
    State(state): State<AppState>,
    Json(req): Json<LoginRequest>,
) -> Result<Json<TokenResponse>, StatusCode> {
    // Find user by username
    let row: (Uuid, String, String, String, Option<chrono::DateTime<chrono::Utc>>) = sqlx::query_as(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE username = $1",
    )
    .bind(&req.username)
    .fetch_optional(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    .ok_or(StatusCode::UNAUTHORIZED)?;

    let user = User {
        id: row.0,
        username: row.1,
        password_hash: row.2,
        role: row.3.parse().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?,
        created_at: row.4.expect("created_at should not be NULL"),
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
    let refresh_token_hash = hash_refresh_token(&req.refresh_token);

    let matching_session: ActiveSessionRow = sqlx::query_as(
        "SELECT user_id, refresh_token_hash FROM sessions WHERE refresh_token_hash = $1 AND expires_at > NOW()",
    )
    .bind(&refresh_token_hash)
    .fetch_optional(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?
    .ok_or(StatusCode::UNAUTHORIZED)?;

    let user_id = matching_session.user_id;

    // Get user
    let row: (Uuid, String, String, String, Option<chrono::DateTime<chrono::Utc>>) = sqlx::query_as(
        "SELECT id, username, password_hash, role, created_at FROM users WHERE id = $1",
    )
    .bind(&user_id)
    .fetch_one(&state.pool)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    let user = User {
        id: row.0,
        username: row.1,
        password_hash: row.2,
        role: row.3.parse().map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?,
        created_at: row.4.expect("created_at should not be NULL"),
    };

    // Rotate refresh token (delete old, create new)
    let new_refresh_token = generate_refresh_token();
    rotate_refresh_token(
        &state.pool,
        user.id,
        &matching_session.refresh_token_hash,
        &new_refresh_token,
    )
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
    req: Request,
) -> Result<StatusCode, StatusCode> {
    let auth_req = extract_authenticated_request(&req)?;
    revoke_all_tokens(&state.pool, auth_req.user_id)
        .await
        .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;
    Ok(StatusCode::NO_CONTENT)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::auth::jwt::{generate_refresh_token, hash_refresh_token};

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

    #[test]
    fn test_hash_refresh_token_matches_deterministically() {
        let token = generate_refresh_token();

        assert_eq!(hash_refresh_token(&token), hash_refresh_token(&token));
    }

    #[test]
    fn test_extract_authenticated_request_reads_extensions() {
        let mut req = Request::new(Body::empty());
        let auth_req = AuthenticatedRequest {
            user_id: Uuid::new_v4(),
            username: "testuser".to_string(),
            role: crate::auth::models::Role::User,
        };
        req.extensions_mut().insert(auth_req.clone());

        let extracted = extract_authenticated_request(&req).unwrap();
        assert_eq!(extracted.user_id, auth_req.user_id);
        assert_eq!(extracted.username, auth_req.username);
    }

    #[test]
    fn test_extract_authenticated_request_rejects_missing_extensions() {
        let req = Request::new(Body::empty());
        let result = extract_authenticated_request(&req);
        assert_eq!(result.unwrap_err(), StatusCode::UNAUTHORIZED);
    }
}
