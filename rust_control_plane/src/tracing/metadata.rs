use serde::Serialize;
use uuid::Uuid;

/// Distributed tracing metadata attached to each request.
///
/// `trace_id` is propagated from the incoming `X-Trace-ID` header when
/// present; otherwise a fresh UUID v4 is generated for the request.
#[derive(Debug, Clone, Serialize)]
pub struct TraceMetadata {
    /// Stable trace identifier, propagated across service boundaries.
    pub trace_id: String,
    /// Per-request identifier (always freshly generated).
    pub request_id: Uuid,
    pub user_id: Option<Uuid>,
}

impl TraceMetadata {
    /// Create metadata with a caller-supplied `trace_id`.
    pub fn with_trace_id(trace_id: impl Into<String>) -> Self {
        Self {
            trace_id: trace_id.into(),
            request_id: Uuid::new_v4(),
            user_id: None,
        }
    }

    /// Create metadata generating a fresh UUID v4 as `trace_id`.
    pub fn new() -> Self {
        Self::with_trace_id(Uuid::new_v4().to_string())
    }

    pub fn with_user(mut self, user_id: Uuid) -> Self {
        self.user_id = Some(user_id);
        self
    }
}
