// JWT token generation and validation
// Matches Python implementation (30min access, 24h refresh tokens)

use anyhow::Result;
use chrono::{Duration, Utc};
use jsonwebtoken::{decode, encode, DecodingKey, EncodingKey, Validation, Header};
use uuid::Uuid;

use crate::auth::models::{User, Claims};

const ACCESS_TOKEN_EXPIRY: i64 = 1800;  // 30 minutes (matches Python)
const REFRESH_TOKEN_EXPIRY: i64 = 86400;  // 24 hours (matches Python)

/// Generate JWT access token for user
pub fn generate_access_token(user: &User, secret: &str) -> Result<String> {
    let expiration = Utc::now()
        .checked_add_signed(Duration::seconds(ACCESS_TOKEN_EXPIRY))
        .expect("valid timestamp")
        .timestamp();

    let claims = Claims {
        sub: user.id.to_string(),
        username: user.username.clone(),
        role: user.role.clone(),
        exp: expiration,
        iat: Utc::now().timestamp(),
    };

    let token = encode(
        &Header::default(),
        &claims,
        &EncodingKey::from_secret(secret.as_ref())
    )?;
    Ok(token)
}

/// Generate refresh token (random UUID)
pub fn generate_refresh_token() -> String {
    Uuid::new_v4().to_string()
}

/// Validate JWT access token and return claims
pub fn validate_access_token(token: &str, secret: &str) -> Result<Claims> {
    let token_data = decode::<Claims>(
        token,
        &DecodingKey::from_secret(secret.as_ref()),
        &Validation::default()
    )?;
    Ok(token_data.claims)
}

/// Hash password using bcrypt (matches Python bcrypt)
pub fn hash_password(password: &str) -> Result<String> {
    let hash = bcrypt::hash(password, bcrypt::DEFAULT_COST)?;
    Ok(hash)
}

/// Verify password against hash
pub fn verify_password(password: &str, hash: &str) -> Result<bool> {
    Ok(bcrypt::verify(password, hash)?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::auth::models::Role;

    #[test]
    fn test_generate_and_validate_token() {
        let secret = "test_secret";
        let user = User {
            id: Uuid::new_v4(),
            username: "testuser".to_string(),
            password_hash: "hash".to_string(),
            role: Role::User,
            created_at: Utc::now(),
        };

        let token = generate_access_token(&user, secret).unwrap();
        let claims = validate_access_token(&token, secret).unwrap();

        assert_eq!(claims.sub, user.id.to_string());
        assert_eq!(claims.username, user.username);
        assert_eq!(claims.role, user.role);
    }

    #[test]
    fn test_hash_and_verify_password() {
        let password = "test_password";
        let hash = hash_password(password).unwrap();
        assert!(verify_password(password, &hash).unwrap());
        assert!(!verify_password("wrong_password", &hash).unwrap());
    }

    #[test]
    fn test_generate_refresh_token() {
        let token1 = generate_refresh_token();
        let token2 = generate_refresh_token();
        assert_ne!(token1, token2); // Should be random
        assert_eq!(token1.len(), 36); // UUID format
    }
}
