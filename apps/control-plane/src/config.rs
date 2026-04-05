use std::env;

pub struct Config {
    pub control_plane_url: String,
    pub agent_runtime_url: String,
    pub postgres_url: String,
}

impl Config {
    pub fn from_env() -> Result<Self, String> {
        Ok(Config {
            control_plane_url: env::var("CONTROL_PLANE_URL")
                .unwrap_or_else(|_| "http://localhost:3001".to_string()),
            agent_runtime_url: env::var("AGENT_RUNTIME_URL")
                .unwrap_or_else(|_| "http://localhost:8001".to_string()),
            postgres_url: env::var("POSTGRES_URL")
                .unwrap_or_else(|_| "postgresql://postgres:devpassword@localhost:5432/mastermind_dev".to_string()),
        })
    }
}
