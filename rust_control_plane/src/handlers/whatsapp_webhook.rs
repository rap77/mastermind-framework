use axum::{
    body::Bytes,
    extract::{Query, State},
    http::{HeaderMap, StatusCode},
    response::{IntoResponse, Response},
};
use hmac::{Hmac, Mac};
use serde::Deserialize;
use sha2::{Digest, Sha256};
use subtle::ConstantTimeEq;
use uuid::Uuid;

use crate::messaging::{
    canonical_event::{
        CanonicalChannel, CanonicalDirection, CanonicalMessageType, CanonicalProcessingStatus,
        CanonicalSchemaVersion,
    },
    CanonicalInboundEventV1, InboundRepositoryError, InsertOutcome, WhatsAppIngressState,
};
use crate::metrics::{
    record_whatsapp_ingest, WhatsAppIngestOutcome, WhatsAppPersistenceFailureReason,
};

#[derive(Deserialize)]
struct WhatsAppEnvelope {
    object: String,
    entry: Vec<WhatsAppEntry>,
}

#[derive(Deserialize)]
struct WhatsAppEntry {
    changes: Vec<WhatsAppChange>,
}

#[derive(Deserialize)]
struct WhatsAppChange {
    field: String,
    value: WhatsAppValue,
}

#[derive(Deserialize)]
struct WhatsAppValue {
    metadata: Option<WhatsAppMetadata>,
    messages: Option<Vec<WhatsAppMessage>>,
    statuses: Option<Vec<serde_json::Value>>,
}

#[derive(Deserialize)]
struct WhatsAppMetadata {
    phone_number_id: Option<String>,
}

#[derive(Deserialize)]
struct WhatsAppMessage {
    #[serde(rename = "type")]
    message_type: Option<String>,
    id: Option<String>,
    from: Option<String>,
    timestamp: Option<String>,
    text: Option<WhatsAppText>,
}

#[derive(Deserialize)]
struct WhatsAppText {
    body: Option<String>,
}

enum AdaptedEvent {
    Text(CanonicalInboundEventV1),
    Unsupported,
}

enum AdaptError {
    Invalid,
    AccountMismatch,
    Unavailable,
}

#[derive(Deserialize)]
pub struct MetaVerifyQuery {
    #[serde(rename = "hub.mode")]
    mode: String,
    #[serde(rename = "hub.verify_token")]
    verify_token: String,
    #[serde(rename = "hub.challenge")]
    challenge: String,
}

pub async fn verify_whatsapp_subscription(
    State(state): State<WhatsAppIngressState>,
    Query(query): Query<MetaVerifyQuery>,
) -> Response {
    let Some(config) = state.config() else {
        return StatusCode::SERVICE_UNAVAILABLE.into_response();
    };

    let token_matches: bool = config
        .verify_token
        .as_bytes()
        .ct_eq(query.verify_token.as_bytes())
        .into();

    if query.mode == "subscribe" && token_matches {
        return (StatusCode::OK, query.challenge).into_response();
    }

    StatusCode::FORBIDDEN.into_response()
}

pub async fn receive_whatsapp_webhook(
    State(state): State<WhatsAppIngressState>,
    headers: HeaderMap,
    body: Bytes,
) -> StatusCode {
    let started_at = std::time::Instant::now();
    let Some(config) = state.config() else {
        return complete_ingest(
            started_at,
            StatusCode::SERVICE_UNAVAILABLE,
            WhatsAppIngestOutcome::Unavailable,
            None,
        );
    };

    let mut signature_values = headers.get_all("x-hub-signature-256").iter();
    let Some(signature) = signature_values.next() else {
        return complete_ingest(
            started_at,
            StatusCode::UNAUTHORIZED,
            WhatsAppIngestOutcome::InvalidSignature,
            None,
        );
    };
    if signature_values.next().is_some() {
        return complete_ingest(
            started_at,
            StatusCode::UNAUTHORIZED,
            WhatsAppIngestOutcome::InvalidSignature,
            None,
        );
    }
    let Ok(signature) = signature.to_str() else {
        return complete_ingest(
            started_at,
            StatusCode::UNAUTHORIZED,
            WhatsAppIngestOutcome::InvalidSignature,
            None,
        );
    };

    if verify_signature(&body, signature, &config.app_secret).is_err() {
        return complete_ingest(
            started_at,
            StatusCode::UNAUTHORIZED,
            WhatsAppIngestOutcome::InvalidSignature,
            None,
        );
    }

    let received_at = chrono::Utc::now();
    let event = match adapt_event(&body, config, received_at) {
        Ok(AdaptedEvent::Unsupported) => {
            return complete_ingest(
                started_at,
                StatusCode::OK,
                WhatsAppIngestOutcome::Unsupported,
                None,
            );
        }
        Ok(AdaptedEvent::Text(event)) => event,
        Err(AdaptError::Invalid) => {
            return complete_ingest(
                started_at,
                StatusCode::BAD_REQUEST,
                WhatsAppIngestOutcome::InvalidPayload,
                None,
            );
        }
        Err(AdaptError::AccountMismatch) => {
            return complete_ingest(
                started_at,
                StatusCode::FORBIDDEN,
                WhatsAppIngestOutcome::AccountMismatch,
                None,
            );
        }
        Err(AdaptError::Unavailable) => {
            return complete_ingest(
                started_at,
                StatusCode::SERVICE_UNAVAILABLE,
                WhatsAppIngestOutcome::Unavailable,
                None,
            );
        }
    };

    let Some(repository) = state.repository() else {
        return complete_ingest(
            started_at,
            StatusCode::SERVICE_UNAVAILABLE,
            WhatsAppIngestOutcome::Unavailable,
            None,
        );
    };
    match repository.insert_or_get(&event).await {
        Ok(InsertOutcome::Inserted { .. }) => complete_ingest(
            started_at,
            StatusCode::OK,
            WhatsAppIngestOutcome::Inserted,
            None,
        ),
        Ok(InsertOutcome::Duplicate { .. }) => complete_ingest(
            started_at,
            StatusCode::OK,
            WhatsAppIngestOutcome::Duplicate,
            None,
        ),
        Err(error) => complete_ingest(
            started_at,
            StatusCode::SERVICE_UNAVAILABLE,
            WhatsAppIngestOutcome::Unavailable,
            Some(match error {
                InboundRepositoryError::Unavailable => WhatsAppPersistenceFailureReason::Pool,
                InboundRepositoryError::SchemaMissing => WhatsAppPersistenceFailureReason::Schema,
                InboundRepositoryError::Database => WhatsAppPersistenceFailureReason::Database,
            }),
        ),
    }
}

fn complete_ingest(
    started_at: std::time::Instant,
    status: StatusCode,
    outcome: WhatsAppIngestOutcome,
    persistence_reason: Option<WhatsAppPersistenceFailureReason>,
) -> StatusCode {
    record_whatsapp_ingest(outcome, persistence_reason, started_at.elapsed());
    status
}

fn adapt_event(
    body: &[u8],
    config: &crate::messaging::WhatsAppIngressConfig,
    received_at: chrono::DateTime<chrono::Utc>,
) -> Result<AdaptedEvent, AdaptError> {
    let envelope: WhatsAppEnvelope =
        serde_json::from_slice(body).map_err(|_| AdaptError::Invalid)?;
    if envelope.object != "whatsapp_business_account" {
        return Err(AdaptError::Invalid);
    }

    let change = envelope
        .entry
        .first()
        .and_then(|entry| entry.changes.first())
        .filter(|change| change.field == "messages")
        .ok_or(AdaptError::Invalid)?;
    let phone_number_id = change
        .value
        .metadata
        .as_ref()
        .and_then(|metadata| metadata.phone_number_id.as_deref())
        .filter(|id| !id.is_empty())
        .ok_or(AdaptError::Invalid)?;
    if phone_number_id != config.phone_number_id {
        return Err(AdaptError::AccountMismatch);
    }

    let Some(messages) = change.value.messages.as_ref() else {
        return if change
            .value
            .statuses
            .as_ref()
            .is_some_and(|statuses| !statuses.is_empty())
        {
            Ok(AdaptedEvent::Unsupported)
        } else {
            Err(AdaptError::Invalid)
        };
    };
    let message = messages.first().ok_or(AdaptError::Invalid)?;
    let message_type = message.message_type.as_deref().ok_or(AdaptError::Invalid)?;
    if message_type != "text" {
        return Ok(AdaptedEvent::Unsupported);
    }

    let external_message_id = required(message.id.as_deref())?;
    let sender_external_id = required(message.from.as_deref())?;
    let content_text = message
        .text
        .as_ref()
        .and_then(|text| text.body.as_deref())
        .filter(|body| !body.is_empty() && body.chars().count() <= 4096)
        .ok_or(AdaptError::Invalid)?;
    let occurred_at = required(message.timestamp.as_deref())?
        .parse::<i64>()
        .ok()
        .and_then(|timestamp| chrono::DateTime::from_timestamp(timestamp, 0))
        .ok_or(AdaptError::Invalid)?;
    let retention_expires_at = received_at
        .checked_add_days(chrono::Days::new(config.retention_days.into()))
        .ok_or(AdaptError::Unavailable)?;

    Ok(AdaptedEvent::Text(CanonicalInboundEventV1 {
        schema_version: CanonicalSchemaVersion::V1,
        event_id: Uuid::new_v4(),
        channel: CanonicalChannel::WhatsApp,
        account_external_id: phone_number_id.to_owned(),
        external_message_id: external_message_id.to_owned(),
        direction: CanonicalDirection::Inbound,
        sender_external_id: sender_external_id.to_owned(),
        recipient_external_id: phone_number_id.to_owned(),
        message_type: CanonicalMessageType::Text,
        content_text: content_text.to_owned(),
        occurred_at,
        received_at,
        payload_sha256: hex::encode(Sha256::digest(body)),
        processing_status: CanonicalProcessingStatus::Accepted,
        retention_expires_at,
    }))
}

fn required(value: Option<&str>) -> Result<&str, AdaptError> {
    value
        .filter(|value| !value.is_empty())
        .ok_or(AdaptError::Invalid)
}

fn verify_signature(body: &[u8], signature: &str, app_secret: &str) -> Result<(), ()> {
    let encoded = signature.strip_prefix("sha256=").ok_or(())?;
    if encoded.len() != 64 {
        return Err(());
    }

    let signature = hex::decode(encoded).map_err(|_| ())?;
    if signature.len() != 32 {
        return Err(());
    }

    let mut mac = Hmac::<Sha256>::new_from_slice(app_secret.as_bytes()).map_err(|_| ())?;
    mac.update(body);
    mac.verify_slice(&signature).map_err(|_| ())
}
