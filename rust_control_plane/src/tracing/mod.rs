use tracing_subscriber::{Registry, EnvFilter};
use tracing_subscriber::fmt::layer;

pub mod metadata;

pub fn init_tracing() {
    let env_filter = EnvFilter::from_default_env()
        .add_directive(tracing::Level::INFO.into())
        .add_directive("sqlx=warn".parse().unwrap())
        .add_directive("hyper=warn".parse().unwrap())
        .add_directive("h2=warn".parse().unwrap());

    let subscriber = Registry::default()
        .with(env_filter)
        .with(layer().json());

    tracing::subscriber::set_global_default(subscriber)
        .expect("Failed to set tracing subscriber");
}
