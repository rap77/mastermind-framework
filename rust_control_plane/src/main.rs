use anyhow::Result;
use axum::{
    routing::get,
    Router,
    Json,
    response::IntoResponse,
    http::StatusCode,
};
use std::net::SocketAddr;
use std::time::Duration;
use tokio::net::TcpListener;
use tracing::{info, error};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt};

mod db;
mod handlers;

use db::connect_pool;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize tracing
    tracing_subscriber::registry()
        .with(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "rust_control_plane=info,tower_http=debug,axum=trace".into()),
        )
        .with(tracing_subscriber::fmt::layer())
        .init();

    // Connect to PostgreSQL with retry logic
    let database_url = std::env::var("DATABASE_URL")
        .unwrap_or_else(|_| "postgresql://postgres:devpassword@localhost:5433/mastermind_bd".to_string());

    let pool = connect_with_retry(&database_url, 3).await?;

    // Build our application with routes
    let app = Router::new()
        .route("/health", get(handlers::health::health_check))
        .route("/health/db", get({
            let pool = pool.clone();
            move || handlers::health::database_health(pool)
        }));

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
