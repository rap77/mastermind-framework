// JWT authentication middleware for Axum
// Validates Authorization header and extracts user context

use axum::{
    extract::{Request, State, FromRequestParts},
    http::StatusCode,
    middleware::Next,
    response::Response,
};
use uuid::Uuid;

use crate::auth::models::Role;
use crate::auth::jwt::validate_access_token;

/// Authenticated request context extracted from JWT
#[derive(Clone, Debug)]
pub struct AuthenticatedRequest {
    pub user_id: Uuid,
    pub username: String,
    pub role: Role,
}

impl TryFrom<crate::auth::models::Claims> for AuthenticatedRequest {
    type Error = anyhow::Error;

    fn try_from(claims: crate::auth::models::Claims) -> Result<Self, Self::Error> {
        Ok(Self {
            user_id: Uuid::parse_str(&claims.sub)?,
            username: claims.username,
            role: claims.role,
        })
    }
}

/// JWT validation middleware - extracts and validates Bearer token
/// Public routes (no auth required): /ws, /metrics, /health, /api/auth/login, /api/auth/refresh
pub async fn auth_middleware(
    State(state): State<crate::state::AppState>,
    mut req: Request,
    next: Next,
) -> Result<Response, StatusCode> {
    // Skip authentication for public routes
    let path = req.uri().path();
    let public_routes = [
        "/ws",
        "/metrics",
        "/health/live",
        "/health/ready",
        "/api/auth/login",
        "/api/auth/refresh",
        "/api/ghost/replay",
    ];

    if public_routes.iter().any(|route| path.starts_with(route)) {
        return Ok(next.run(req).await);
    }

    let auth_header = req
        .headers()
        .get("Authorization")
        .and_then(|h| h.to_str().ok())
        .ok_or(StatusCode::UNAUTHORIZED)?;

    if !auth_header.starts_with("Bearer ") {
        return Err(StatusCode::UNAUTHORIZED);
    }

    let token = &auth_header[7..]; // Skip "Bearer "
    let claims = validate_access_token(token, &state.jwt_secret)
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    // Store authenticated request in extensions
    let auth_req = AuthenticatedRequest::try_from(claims)
        .map_err(|_| StatusCode::UNAUTHORIZED)?;
    req.extensions_mut().insert(auth_req);

    Ok(next.run(req).await)
}

/// Role-based authorization middleware factory
/// Creates middleware that checks if user has required role
pub fn require_role(required_role: Role) -> impl Fn(Request, Next) -> futures::future::BoxFuture<'static, Result<Response, StatusCode>> + Clone {
    move |req: Request, next: Next| {
        let required_role = required_role.clone();
        Box::pin(async move {
            let auth_req = req.extensions().get::<AuthenticatedRequest>()
                .ok_or(StatusCode::UNAUTHORIZED)?;

            // Admin can access everything, others need exact role match
            if auth_req.role != Role::Admin && auth_req.role != required_role {
                return Err(StatusCode::FORBIDDEN);
            }

            Ok(next.run(req).await)
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_authenticated_request_from_claims() {
        let claims = crate::auth::models::Claims {
            sub: "550e8400-e29b-41d4-a716-446655440000".to_string(),
            username: "testuser".to_string(),
            role: Role::User,
            exp: 9999999999,
            iat: 1234567890,
        };

        let auth_req = AuthenticatedRequest::try_from(claims).unwrap();
        assert_eq!(auth_req.username, "testuser");
        assert_eq!(auth_req.role, Role::User);
    }
}
