use serde::Serialize;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize)]
pub struct TraceMetadata {
    pub trace_id: Uuid,
    pub request_id: Uuid,
    pub user_id: Option<Uuid>,
}

impl TraceMetadata {
    pub fn new() -> Self {
        Self {
            trace_id: Uuid::new_v4(),
            request_id: Uuid::new_v4(),
            user_id: None,
        }
    }

    pub fn with_user(mut self, user_id: Uuid) -> Self {
        self.user_id = Some(user_id);
        self
    }
}
