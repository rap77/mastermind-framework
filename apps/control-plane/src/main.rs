mod config;
mod proto;

use axum::{routing::get, Router};
use tokio::net::TcpListener;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    // Initialize tracing
    tracing_subscriber::fmt()
        .with_env_filter(
            tracing_subscriber::EnvFilter::try_from_default_env()
                .unwrap_or_else(|_| "mastermind_control_plane=debug,tower_http=debug".into()),
        )
        .init();

    // Load configuration
    let config = config::Config::from_env()?;
    tracing::info!("Config loaded: control_plane={}, agent_runtime={}, postgres={}",
        config.control_plane_url, config.agent_runtime_url, config.postgres_url);

    // Build our application with a single route
    let app = Router::new().route("/health", get(health_check));

    // Create a TCP listener
    let listener = TcpListener::bind("0.0.0.0:3001").await?;
    tracing::info!("Control Plane listening on {}", listener.local_addr()?);

    // Serve the application
    axum::serve(listener, app).await?;
    Ok(())
}

async fn health_check() -> &'static str {
    "OK"
}
