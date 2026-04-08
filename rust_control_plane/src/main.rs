use anyhow::Result;
use axum::{
    routing::{get, post},
    Router,
    Json,
    response::IntoResponse,
    http::StatusCode,
    middleware,
    extract::State,
};
use std::net::SocketAddr;
use std::sync::Arc;
use std::time::Duration;
use tokio::net::TcpListener;
use tracing::{info, error};

mod db;
mod handlers;
mod auth;
mod state;
mod sqlite_reader;
mod event_sourcing;
mod tracing;
mod health;

use tracing::inject_trace_middleware;

use db::connect_pool;
use auth::auth_middleware;
use state::AppState;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing with JSON output
    tracing::init_tracing();

    // Connect to PostgreSQL with retry logic
    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgresql://postgres:devpassword@localhost:5433/mastermind_bd".to_string());

    let pool = connect_with_retry(&database_url, 3).await?;

    // Validate JWT_SECRET on startup
    let jwt_secret = std::env::var("JWT_SECRET")
        .map_err(|_| anyhow::anyhow!("JWT_SECRET environment variable not set"))?;

    if jwt_secret.len() < 32 {
        anyhow::bail!("JWT_SECRET must be at least 32 characters");
    }

    info!("JWT_SECRET validated (length: {})", jwt_secret.len());

    // Create application state
    let state = AppState {
        pool,
        jwt_secret: Arc::new(jwt_secret),
    };

    // Build our application with routes
    let app = Router::new()
        // Kubernetes-style health probes (public)
        .route("/health/live", get(health::live::liveness_probe))
        .route("/health/ready", get(health::ready::readiness_check))
        // Auth routes (public)
        .route("/api/auth/login", post(handlers::auth::login))
        .route("/api/auth/refresh", post(handlers::auth::refresh))
        // Protected auth routes (require authentication)
        .route("/api/auth/logout", post(handlers::auth::logout))
        // Audit log routes (protected, admin-only)
        .route("/api/audit/activity", get(handlers::audit::get_activity_log))
        .route("/api/audit/brain/:brain_id", get(handlers::audit::get_brain_timeline))
        .layer(middleware::from_fn_with_state(
            state.clone(),
            auth_middleware,
        ))
        .layer(inject_trace_middleware) // Add trace injection middleware
        .with_state(state);

    // Create TCP listener
    let addr = SocketAddr::from(([0, 0, 0, 0], 8080));
    let listener = TcpListener::bind(addr).await?;

    info!("Rust Control Plane listening on {}", addr);
    info!("PostgreSQL connected: {}", database_url);

    // Serve the application with graceful shutdown
    axum::serve(listener, app)
        .with_graceful_shutdown(shutdown_signal())
        .await?;

    Ok(())
}

/// Connect to PostgreSQL with exponential backoff retry
async fn connect_with_retry(database_url: &str, max_attempts: u32) -> Result<db::PgPool> {
    let mut attempt = 0;
    let mut delay = Duration::from_millis(100);

    loop {
        attempt += 1;
        match connect_pool(database_url).await {
            Ok(pool) => {
                info!("Connected to PostgreSQL (attempt {})", attempt);
                return Ok(pool);
            }
            Err(e) if attempt < max_attempts => {
                error!("Failed to connect (attempt {}/{}): {}", attempt, max_attempts, e);
                tokio::time::sleep(delay).await;
                delay *= 2; // Exponential backoff
            }
            Err(e) => {
                error!("Failed to connect after {} attempts: {}", max_attempts, e);
                return Err(e);
            }
        }
    }
}

/// Graceful shutdown handler
async fn shutdown_signal() {
    let ctrl_c = async {
        tokio::signal::ctrl_c()
            .await
            .expect("failed to install Ctrl+C handler");
    };

    #[cfg(unix)]
    let terminate = async {
        tokio::signal::unix::signal(tokio::signal::unix::SignalKind::terminate())
            .expect("failed to install signal handler")
            .recv()
            .await;
    };

    #[cfg(not(unix))]
    let terminate = std::future::pending::<()>();

    tokio::select! {
        _ = ctrl_c => {
            info!("Ctrl+C received, shutting down gracefully");
        },
        _ = terminate => {
            info!("Terminate signal received, shutting down gracefully");
        },
    }
}
