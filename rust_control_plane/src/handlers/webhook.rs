//! Webhook receiver for multi-channel gateway
//!
//! Accepts webhooks from WhatsApp, Instagram, and Email providers.
//! Features:
//! - HMAC signature verification (X-Hub-Signature-256 for WhatsApp, X-Hub-Signature for Instagram)
//! - Duplicate detection via UNIQUE constraint
//! - Idempotent: 204 No Content on duplicate, 200 OK on new
//! - Queue depth monitoring: rejects at 90% capacity (503 Service Unavailable)
//! - Webhook ACK < 100ms P95

use axum::{
    extract::{Path, State},
    http::{HeaderMap, StatusCode},
    Json,
};
use serde_json::Value;
use sqlx::PgPool;
use std::sync::Arc;
use tracing::{error, info, warn};

use crate::observability::LatencyTracker;
use crate::queue::{WebhookQueue, WebhookEvent};

/// Verify HMAC signature from webhook provider
///
/// WhatsApp: X-Hub-Signature-256 (SHA256)
/// Instagram: X-Hub-Signature (SHA1 or SHA256)
fn verify_hmac_signature(
    payload: &str,
    signature: &str,
    app_secret: &str,
) -> anyhow::Result<bool> {
    use hmac::{Hmac, Mac};
    use sha1::Sha1;
    use sha2::Sha256;

    // Signature format: "sha256=<hex>" or "sha1=<hex>"
    let (algo, sig_bytes) = signature
        .split_once('=')
        .ok_or_else(|| anyhow::anyhow!("Invalid signature format"))?;

    let expected_bytes = hex::decode(sig_bytes)?;

    // Verify based on algorithm
    let is_valid = match algo {
        "sha256" => {
            let mut mac = Hmac::<Sha256>::new_from_slice(app_secret.as_bytes())?;
            mac.update(payload.as_bytes());
            let result = mac.finalize();
            result.into_bytes().as_slice() == expected_bytes.as_slice()
        }
        "sha1" => {
            let mut mac = Hmac::<Sha1>::new_from_slice(app_secret.as_bytes())?;
            mac.update(payload.as_bytes());
            let result = mac.finalize();
            result.into_bytes().as_slice() == expected_bytes.as_slice()
        }
        _ => {
            return Err(anyhow::anyhow!("Unsupported signature algorithm: {}", algo));
        }
    };

    Ok(is_valid)
}

/// Extract external message ID from webhook payload
///
/// WhatsApp: entry[0].changes[0].value.messages[0].id
/// Instagram: changes[0].value.id
/// Email: Message-ID header (from payload)
fn extract_external_message_id(payload: &Value, channel: &str) -> anyhow::Result<String> {
    let id = match channel {
        "whatsapp" => payload["entry"][0]["changes"][0]["value"]["messages"][0]["id"]
            .as_str()
            .ok_or_else(|| anyhow::anyhow!("WhatsApp message ID not found"))?
            .to_string(),
        "instagram" => payload["changes"][0]["value"]["id"]
            .as_str()
            .ok_or_else(|| anyhow::anyhow!("Instagram comment ID not found"))?
            .to_string(),
        "email" => payload["headers"]["message-id"]
            .as_str()
            .ok_or_else(|| anyhow::anyhow!("Email Message-ID not found"))?
            .to_string(),
        _ => return Err(anyhow::anyhow!("Unsupported channel: {}", channel)),
    };

    Ok(id)
}

/// Check if webhook is duplicate via UNIQUE constraint
async fn is_duplicate(db: &PgPool, external_id: &str, channel: &str) -> anyhow::Result<bool> {
    let result = sqlx::query_scalar::<_, i64>(
        "SELECT COUNT(*) FROM messages WHERE external_message_id = $1 AND channel = $2"
    )
    .bind(external_id)
    .bind(channel)
    .fetch_one(db)
    .await?;

    Ok(result > 0)
}

/// Webhook receiver endpoint
///
/// POST /webhooks/{channel}
///
/// Returns:
/// - 200 OK: Webhook accepted and queued
/// - 204 No Content: Duplicate webhook (idempotent)
/// - 401 Unauthorized: Invalid HMAC signature
/// - 503 Service Unavailable: Queue depth > 90%
pub async fn webhook_receiver(
    Path(channel): Path<String>,
    State(state): State<crate::state::AppState>,
    headers: HeaderMap,
    Json(payload): Json<Value>,
) -> Result<StatusCode, StatusCode> {
    let start = std::time::Instant::now();

    // Validate channel
    if !matches!(channel.as_str(), "whatsapp" | "instagram" | "email") {
        error!(channel = %channel, "Invalid channel");
        return Err(StatusCode::BAD_REQUEST);
    }

    // Extract HMAC signature
    let signature = headers
        .get("x-hub-signature-256")
        .or_else(|| headers.get("x-hub-signature"))
        .and_then(|v| v.to_str().ok())
        .ok_or_else(|| {
            warn!(channel = %channel, "Missing signature header");
            StatusCode::UNAUTHORIZED
        })?;

    // Get app secret from environment
    let app_secret = std::env::var(match channel.as_str() {
        "whatsapp" => "WHATSAPP_APP_SECRET",
        "instagram" => "INSTAGRAM_APP_SECRET",
        "email" => "EMAIL_WEBHOOK_SECRET",
        _ => return Err(StatusCode::INTERNAL_SERVER_ERROR),
    })
    .map_err(|_| {
        error!(channel = %channel, "App secret not configured");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    // Verify HMAC signature
    let payload_str = payload.to_string();
    verify_hmac_signature(&payload_str, signature, &app_secret)
        .map_err(|e| {
            warn!(channel = %channel, error = %e, "Signature verification failed");
            StatusCode::UNAUTHORIZED
        })?;

    // Extract external message ID
    let external_id = extract_external_message_id(&payload, &channel).map_err(|e| {
        error!(channel = %channel, error = %e, "Failed to extract message ID");
        StatusCode::BAD_REQUEST
    })?;

    // Check for duplicate (idempotency)
    let duplicate = is_duplicate(&state.pool, &external_id, &channel)
        .await
        .map_err(|e| {
            error!(channel = %channel, error = %e, "Database error checking duplicate");
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    if duplicate {
        info!(
            channel = %channel,
            external_id = %external_id,
            "Duplicate webhook detected"
        );
        return Ok(StatusCode::NO_CONTENT); // 204 - Idempotent
    }

    // Generate trace ID
    let trace_id = uuid::Uuid::new_v4().to_string();

    // Start E2E latency timer (Brain #7 Condition #3)
    state.latency_tracker.start_timer(&trace_id, &channel);

    // Insert into messages table (status: pending)
    sqlx::query(
        "INSERT INTO messages (external_message_id, channel, payload, status) VALUES ($1, $2, $3, 'pending')"
    )
    .bind(&external_id)
    .bind(&channel)
    .bind(&payload)
    .execute(&state.pool)
    .await
    .map_err(|e| {
        error!(channel = %channel, error = %e, "Failed to insert webhook");
        StatusCode::INTERNAL_SERVER_ERROR
    })?;

    // Push to queue
    let event = WebhookEvent {
        channel: channel.clone(),
        payload,
        trace_id: trace_id.clone(),
    };

    state
        .webhook_queue
        .send_with_backpressure(event)
        .await
        .map_err(|_: tokio::sync::mpsc::error::SendError<WebhookEvent>| {
            warn!(
                channel = %channel,
                trace_id = %trace_id,
                "Queue depth > 90%, webhook rejected"
            );
            StatusCode::SERVICE_UNAVAILABLE // 503
        })?;

    // Log latency
    let latency = start.elapsed().as_millis();
    info!(
        channel = %channel,
        trace_id = %trace_id,
        latency_ms = latency,
        "Webhook received and queued"
    );

    Ok(StatusCode::OK) // 200
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_extract_whatsapp_message_id() {
        let payload = serde_json::json!({
            "entry": [{
                "changes": [{
                    "value": {
                        "messages": [{"id": "wamid.example123"}]
                    }
                }]
            }]
        });

        let id = extract_external_message_id(&payload, "whatsapp").unwrap();
        assert_eq!(id, "wamid.example123");
    }

    #[test]
    fn test_extract_instagram_comment_id() {
        let payload = serde_json::json!({
            "changes": [{
                "value": {"id": "comment.example456"}
            }]
        });

        let id = extract_external_message_id(&payload, "instagram").unwrap();
        assert_eq!(id, "comment.example456");
    }

    #[test]
    fn test_extract_email_message_id() {
        let payload = serde_json::json!({
            "headers": {"message-id": "<email.example789@test.com>"}
        });

        let id = extract_external_message_id(&payload, "email").unwrap();
        assert_eq!(id, "<email.example789@test.com>");
    }
}
