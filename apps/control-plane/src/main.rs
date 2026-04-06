mod config;
mod flow;
mod grpc;
mod handlers;
mod postgres;
mod proto;

use axum::{routing::{get, post}, Router};
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

    // Initialize gRPC client (mock for VS)
    let grpc_client = grpc::BrainRuntimeClient::connect(&config.agent_runtime_url)
        .await
        .expect("Failed to connect to gRPC server");
    let grpc_client = std::sync::Arc::new(tokio::sync::Mutex::new(grpc_client));

    // Initialize PostgreSQL repository (mock for VS - no actual DB)
    // In Phase 15, we'll create real PgPool
    let pool = sqlx::PgPool::connect(&config.postgres_url)
        .await
        .expect("Failed to connect to PostgreSQL");
    let repo = std::sync::Arc::new(postgres::ExecutionRepo::new(pool));

    // Create app state
    let app_state = handlers::AppState {
        grpc_client,
        repo,
    };

    // Build our application with routes
    let app = Router::new()
        .route("/health", get(health_check))
        .route("/api/tasks/auto", post(handlers::create_auto_task))
        .with_state(app_state);

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
