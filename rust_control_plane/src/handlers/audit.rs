use axum::{Json, extract::{Query, State, Path, Request}, http::StatusCode};
use serde::Deserialize;
use chrono::{DateTime, Utc};

use crate::event_sourcing::{BrainEvent, BrainEventType, EventStore};
use crate::auth::{middleware::AuthenticatedRequest, models::Role};
use crate::state::AppState;

#[derive(Deserialize)]
pub struct ActivityLogQuery {
    pub brain_id: Option<String>,
    pub event_type: Option<String>,
    pub start_time: Option<DateTime<Utc>>,
    pub end_time: Option<DateTime<Utc>>,
    pub limit: Option<usize>,
}

pub async fn get_activity_log(
    State(state): State<AppState>,
    Query(params): Query<ActivityLogQuery>,
    req: Request,
) -> Result<Json<Vec<BrainEvent>>, StatusCode> {
    // Extract authenticated request from extensions
    let auth_req = req.extensions().get::<AuthenticatedRequest>()
        .ok_or(StatusCode::UNAUTHORIZED)?;

    // Authorization check: only admins can see all activity
    if auth_req.role != Role::Admin {
        return Err(StatusCode::FORBIDDEN);
    }

    let event_type = params.event_type
        .and_then(|t| match t.as_str() {
            "brain_started" => Some(BrainEventType::BrainStarted),
            "brain_completed" => Some(BrainEventType::BrainCompleted),
            "brain_routed" => Some(BrainEventType::BrainRouted),
            "brain_failed" => Some(BrainEventType::BrainFailed),
            _ => None,
        });

    let store = EventStore::new(state.pool.clone());

    let events = store.read_events(
        params.brain_id.as_deref(),
        event_type,
        params.start_time,
        params.end_time,
        params.limit.unwrap_or(100),
    )
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(events))
}

pub async fn get_brain_timeline(
    State(state): State<AppState>,
    Path(brain_id): Path<String>,
    req: Request,
) -> Result<Json<Vec<BrainEvent>>, StatusCode> {
    // Extract authenticated request from extensions
    let auth_req = req.extensions().get::<AuthenticatedRequest>()
        .ok_or(StatusCode::UNAUTHORIZED)?;

    // Authorization check: only admins can see brain timelines
    if auth_req.role != Role::Admin {
        return Err(StatusCode::FORBIDDEN);
    }

    let store = EventStore::new(state.pool.clone());

    let events = store.read_events(
        Some(&brain_id),
        None,
        None,
        None,
        1000,
    )
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    Ok(Json(events))
}

// NOTE: replay_session endpoint DEFERRED to Phase 16 (Observability)
// Reason: No current use case, adds complexity without user requirement
