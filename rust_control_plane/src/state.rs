// Application state shared across all handlers

use std::sync::Arc;
use crate::grpc::AiWorkerClient;
use crate::websocket::WebSocketHub;
use crate::queue::WebhookQueue;
use crate::observability::LatencyTracker;

/// Runtime state for AI worker availability.
#[derive(Clone)]
pub enum AiWorkerRuntimeMode {
    Disabled { reason: Arc<String> },
    Unavailable { addr: Arc<String>, reason: Arc<String> },
    Ready { addr: Arc<String>, client: Arc<AiWorkerClient> },
}

impl AiWorkerRuntimeMode {
    /// Create a disabled AI worker runtime mode with explicit reason.
    pub fn disabled(reason: impl Into<String>) -> Self {
        Self::Disabled {
            reason: Arc::new(reason.into()),
        }
    }

    /// Create an unavailable AI worker runtime mode with target address and reason.
    pub fn unavailable(addr: impl Into<String>, reason: impl Into<String>) -> Self {
        Self::Unavailable {
            addr: Arc::new(addr.into()),
            reason: Arc::new(reason.into()),
        }
    }

    /// Create a ready AI worker runtime mode for a successfully initialized address.
    pub fn ready(addr: impl Into<String>, client: Arc<AiWorkerClient>) -> Self {
        Self::Ready {
            addr: Arc::new(addr.into()),
            client,
        }
    }

    /// Return the machine-readable mode label.
    pub fn label(&self) -> &'static str {
        match self {
            Self::Disabled { .. } => "disabled",
            Self::Unavailable { .. } => "unavailable",
            Self::Ready { .. } => "ready",
        }
    }

    /// Return the human-readable reason for the current mode.
    pub fn reason(&self) -> &str {
        match self {
            Self::Disabled { reason } => reason.as_str(),
            Self::Unavailable { reason, .. } => reason.as_str(),
            Self::Ready { .. } => "connected",
        }
    }

    /// Return the configured address when one exists.
    pub fn addr(&self) -> Option<&str> {
        match self {
            Self::Disabled { .. } => None,
            Self::Unavailable { addr, .. } | Self::Ready { addr, .. } => Some(addr.as_str()),
        }
    }

    /// Return the initialized client when the runtime is ready.
    pub fn client(&self) -> Option<Arc<AiWorkerClient>> {
        match self {
            Self::Ready { client, .. } => Some(client.clone()),
            _ => None,
        }
    }

    /// Readiness result derived from runtime mode.
    pub fn readiness_result(&self) -> Result<(), String> {
        match self {
            Self::Ready { .. } => Ok(()),
            _ => Err(format!("{}: {}", self.label(), self.reason())),
        }
    }
}

/// Application state shared across all handlers
#[derive(Clone)]
pub struct AppState {
    pub pool: sqlx::PgPool,
    pub jwt_secret: Arc<String>,
    pub websocket_hub: Arc<WebSocketHub>,
    pub webhook_queue: Arc<WebhookQueue>,
    pub latency_tracker: Arc<LatencyTracker>,
    pub ai_worker_runtime: Arc<AiWorkerRuntimeMode>,
}

#[cfg(test)]
mod tests {
    use super::AiWorkerRuntimeMode;
    use crate::grpc::AiWorkerClient;
    use std::sync::Arc;

    #[test]
    fn test_disabled_ai_worker_runtime_reports_reason() {
        let runtime = AiWorkerRuntimeMode::disabled("gRPC client intentionally disabled");

        assert_eq!(runtime.label(), "disabled");
        assert_eq!(runtime.reason(), "gRPC client intentionally disabled");
        assert_eq!(
            runtime.readiness_result(),
            Err("disabled: gRPC client intentionally disabled".to_string())
        );
    }

    #[test]
    fn test_unavailable_ai_worker_runtime_reports_addr_and_reason() {
        let runtime = AiWorkerRuntimeMode::unavailable(
            "http://127.0.0.1:50051",
            "connection refused",
        );

        assert_eq!(runtime.label(), "unavailable");
        assert_eq!(runtime.addr(), Some("http://127.0.0.1:50051"));
        assert_eq!(runtime.reason(), "connection refused");
        assert_eq!(
            runtime.readiness_result(),
            Err("unavailable: connection refused".to_string())
        );
    }

    #[tokio::test]
    async fn test_ready_ai_worker_runtime_is_ready() {
        let runtime = AiWorkerRuntimeMode::ready(
            "http://127.0.0.1:50051",
            Arc::new(AiWorkerClient::new_for_tests()),
        );

        assert_eq!(runtime.label(), "ready");
        assert_eq!(runtime.addr(), Some("http://127.0.0.1:50051"));
        assert_eq!(runtime.reason(), "connected");
        assert!(runtime.client().is_some());
        assert_eq!(runtime.readiness_result(), Ok(()));
    }
}
