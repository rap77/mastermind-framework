/// Unified brain state event for the fan-out WebSocket hub.
///
/// Used by:
/// - `POST /internal/brain-event` to receive events from Python
/// - `GET /ws/events` to broadcast to connected frontend clients
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};

/// Status values for a brain dispatch lifecycle.
#[derive(Debug, Clone, PartialEq, Eq, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum BrainStatus {
    Dispatched,
    Running,
    Completed,
    Failed,
}

/// Event emitted by the Python dispatch engine and fanned-out to all
/// WebSocket clients via the broadcast channel.
///
/// `model` and `provider` are optional to maintain backward compatibility with
/// events sent by older Python dispatch engine versions that do not include them.
/// Frontend consumers should treat None/null as "unknown".
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct BrainStateEvent {
    /// Distributed trace identifier (UUID v4 string).
    pub trace_id: String,
    /// Brain identifier (1-7).
    pub brain_id: String,
    /// Lifecycle status of the brain dispatch.
    pub status: BrainStatus,
    /// UTC timestamp when the event was created.
    pub timestamp: DateTime<Utc>,
    /// Provider-qualified model string used for this brain dispatch.
    /// Format: "provider:model_id" (e.g. "anthropic:claude-opus-4-6").
    /// None if not provided by the dispatch engine.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub model: Option<String>,
    /// Provider name (e.g. "anthropic", "openrouter", "z_ai").
    /// None if not provided by the dispatch engine.
    #[serde(skip_serializing_if = "Option::is_none")]
    pub provider: Option<String>,
}

impl BrainStateEvent {
    pub fn dispatched(trace_id: impl Into<String>, brain_id: impl Into<String>) -> Self {
        Self {
            trace_id: trace_id.into(),
            brain_id: brain_id.into(),
            status: BrainStatus::Dispatched,
            timestamp: Utc::now(),
            model: None,
            provider: None,
        }
    }

    pub fn completed(trace_id: impl Into<String>, brain_id: impl Into<String>) -> Self {
        Self {
            trace_id: trace_id.into(),
            brain_id: brain_id.into(),
            status: BrainStatus::Completed,
            timestamp: Utc::now(),
            model: None,
            provider: None,
        }
    }

    pub fn failed(trace_id: impl Into<String>, brain_id: impl Into<String>) -> Self {
        Self {
            trace_id: trace_id.into(),
            brain_id: brain_id.into(),
            status: BrainStatus::Failed,
            timestamp: Utc::now(),
            model: None,
            provider: None,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_brain_state_event_serialization() {
        let event = BrainStateEvent::dispatched("trace-abc-123", "brain-1");
        let json = serde_json::to_string(&event).unwrap();
        assert!(json.contains("trace-abc-123"));
        assert!(json.contains("brain-1"));
        assert!(json.contains("dispatched"));
    }

    #[test]
    fn test_brain_state_event_deserialization() {
        let json = r#"{
            "trace_id": "trace-xyz",
            "brain_id": "brain-3",
            "status": "completed",
            "timestamp": "2026-04-28T12:00:00Z"
        }"#;
        let event: BrainStateEvent = serde_json::from_str(json).unwrap();
        assert_eq!(event.trace_id, "trace-xyz");
        assert_eq!(event.brain_id, "brain-3");
        assert_eq!(event.status, BrainStatus::Completed);
        // model and provider are optional — absent from old payloads
        assert!(event.model.is_none());
        assert!(event.provider.is_none());
    }

    #[test]
    fn test_brain_state_event_with_model_and_provider() {
        let json = r#"{
            "trace_id": "trace-model",
            "brain_id": "brain-1",
            "status": "dispatched",
            "timestamp": "2026-05-01T10:00:00Z",
            "model": "anthropic:claude-opus-4-6",
            "provider": "anthropic"
        }"#;
        let event: BrainStateEvent = serde_json::from_str(json).unwrap();
        assert_eq!(event.model.as_deref(), Some("anthropic:claude-opus-4-6"));
        assert_eq!(event.provider.as_deref(), Some("anthropic"));
    }

    #[test]
    fn test_brain_state_event_model_omitted_when_none() {
        let event = BrainStateEvent::dispatched("trace-omit", "brain-2");
        let json = serde_json::to_string(&event).unwrap();
        // model and provider should not appear in JSON when None
        assert!(!json.contains("\"model\""));
        assert!(!json.contains("\"provider\""));
    }

    #[test]
    fn test_brain_state_event_with_z_ai_provider() {
        let json = r#"{
            "trace_id": "trace-zai",
            "brain_id": "brain-7",
            "status": "running",
            "timestamp": "2026-05-01T10:00:00Z",
            "model": "z_ai:claude-3-7-sonnet",
            "provider": "z_ai"
        }"#;
        let event: BrainStateEvent = serde_json::from_str(json).unwrap();
        assert_eq!(event.model.as_deref(), Some("z_ai:claude-3-7-sonnet"));
        assert_eq!(event.provider.as_deref(), Some("z_ai"));
    }

    #[test]
    fn test_all_statuses_serialize() {
        for status in [
            BrainStatus::Dispatched,
            BrainStatus::Running,
            BrainStatus::Completed,
            BrainStatus::Failed,
        ] {
            let event = BrainStateEvent {
                trace_id: "t".into(),
                brain_id: "b".into(),
                status,
                timestamp: Utc::now(),
                model: None,
                provider: None,
            };
            assert!(serde_json::to_string(&event).is_ok());
        }
    }
}
