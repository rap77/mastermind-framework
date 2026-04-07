// Authentication and authorization module

pub mod models;
pub mod jwt;
pub mod rotation;

pub use models::{User, Role, Claims, LoginRequest, TokenResponse, RefreshRequest};
pub use jwt::{generate_access_token, generate_refresh_token, validate_access_token, hash_password, verify_password};
pub use rotation::{rotate_refresh_token, store_refresh_token, revoke_all_tokens};
