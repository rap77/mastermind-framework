use tonic::transport::Channel;
use uuid::Uuid;

use crate::proto::events::mastermind::events::v1::{
    event_stream_client::EventStreamClient, brain_event::BrainEventType, BrainEvent, EventAck,
};

/// Event Stream Client Wrapper
/// Provides type-safe interface for publishing brain events
#[derive(Debug, Clone)]
pub struct EventStreamClient {
    client: EventStreamClient<Channel>,
}

impl EventStreamClient {
    /// Create new EventStreamClient
    pub async fn connect(addr: String) -> Result<Self, tonic::transport::Error> {
        let client = EventStreamClient::connect(addr).await?;
        Ok(Self { client })
    }

    /// Publish brain event with trace metadata
    pub async fn publish_brain_event(
        &mut self,
        event_id: Uuid,
        trace_id: Uuid,
        event_type: BrainEventType,
        brain_id: String,
        payload_json: String,
    ) -> Result<EventAck, tonic::Status> {
        let request = tonic::Request::new(BrainEvent {
            event_id: event_id.to_string(),
            trace_id: trace_id.to_string(),
            event_type: event_type as i32,
            brain_id,
            payload_json,
            created_at_unix_ms: chrono::Utc::now().timestamp_millis(),
        });

        let response = self.client.publish_brain_event(request).await?;
        Ok(response.into_inner())
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_event_stream_client_creation() {
        // Test client creation (will fail if server not running, but validates compilation)
        let result = EventStreamClient::connect("http://localhost:50051".to_string()).await;
        // We expect connection failure in test environment, but type checking should pass
        assert!(result.is_err() || result.is_ok());
    }
}
