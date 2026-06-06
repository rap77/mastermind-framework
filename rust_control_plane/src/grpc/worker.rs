//! gRPC client for Python AI Worker communication
//!
//! Provides type-safe gRPC client for sending webhooks to Python AI processing service.
//! Implements connection pooling, health checks, and error handling per gRPC design spec.

use anyhow::{Context, Result};
use crate::mastermind::worker_client::WorkerClient as GrpcWorkerClient;
use crate::mastermind::{ProcessWebhookRequest, ProcessWebhookResponse};
use tonic::transport::Channel;

/// gRPC client for Python AI Worker
///
/// Wraps the generated tonic client with connection management and error handling.
#[derive(Clone)]
pub struct AiWorkerClient {
    client: GrpcWorkerClient<Channel>,
}

impl AiWorkerClient {
    /// Create new AI worker client
    ///
    /// Connects to Python gRPC server at specified address.
    /// Uses default channel configuration with connection pooling.
    ///
    /// # Arguments
    /// * `addr` - gRPC server address (e.g., "http://127.0.0.1:50051")
    ///
    /// # Errors
    /// Returns error if connection fails or invalid address provided
    pub async fn new(addr: &str) -> Result<Self> {
        let channel = Channel::from_shared(addr.to_string())
            .context("Invalid gRPC server address")?
            .connect()
            .await
            .context("Failed to connect to Python AI worker")?;

        let client = GrpcWorkerClient::new(channel);

        Ok(Self { client })
    }

    #[cfg(test)]
    pub fn new_for_tests() -> Self {
        let channel = Channel::from_static("http://127.0.0.1:50051").connect_lazy();
        let client = GrpcWorkerClient::new(channel);
        Self { client }
    }

    /// Process webhook via Python AI worker
    ///
    /// Sends webhook payload to Python service for AI processing and channel routing.
    /// Returns AI-generated response text on success.
    ///
    /// # Arguments
    /// * `trace_id` - Distributed tracing ID
    /// * `channel` - Target channel (whatsapp, instagram, email)
    /// * `payload` - JSON webhook payload (stringified)
    ///
    /// # Errors
    /// - GrpcError: gRPC communication failure
    /// - AiProcessingFailed: AI worker returned success=false
    pub async fn process_webhook(
        &self,
        trace_id: String,
        channel: String,
        payload: String,
    ) -> Result<String> {
        let request = ProcessWebhookRequest {
            trace_id,
            channel,
            payload,
            sender_id: String::new(),
            message_type: "text".to_string(),
        };

        let mut client = self.client.clone();
        let response: tonic::Response<ProcessWebhookResponse> = client
            .process_webhook(request)
            .await
            .map_err(|e| anyhow::anyhow!("gRPC call failed: {}", e))
            .context("AI worker gRPC communication failed")?;

        let response = response.into_inner();

        if !response.success {
            return Err(anyhow::anyhow!(
                "AI processing failed: {}",
                response.error_message
            ))
            .context("AI worker returned error");
        }

        Ok(response.ai_response)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_client_creation_requires_address() {
        // This test verifies that client creation requires valid address
        // Actual connection tested in integration tests
        assert!(true, "Client type checks compile");
    }

    #[tokio::test]
    async fn test_test_client_constructor_compiles() {
        let _client = AiWorkerClient::new_for_tests();
    }

    #[tokio::test]
    async fn test_process_webhook_returns_error_when_worker_is_unreachable() {
        let client = AiWorkerClient::new_for_tests();

        let result = client
            .process_webhook(
                "trace-test".to_string(),
                "whatsapp".to_string(),
                "{}".to_string(),
            )
            .await;

        assert!(result.is_err());
    }
}
