mod support;

use std::{str::FromStr, sync::Arc, time::Duration};

use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
    routing::get,
    Router,
};
use hmac::{Hmac, Mac};
use rust_control_plane::{
    handlers::whatsapp_webhook::{receive_whatsapp_webhook, verify_whatsapp_subscription},
    messaging::{InboundEventRepository, WhatsAppIngressConfig, WhatsAppIngressState},
    observability::LatencyTracker,
    queue::WebhookQueue,
    state::{AiWorkerRuntimeMode, AppState},
    websocket::WebSocketHub,
};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions},
    ConnectOptions, PgPool, Row,
};
use tower::ServiceExt;
use uuid::Uuid;

const APP_SECRET: &str = "mcg4-test-app-secret";
const PHONE_NUMBER_ID: &str = "mcg4-test-phone-number-id";

#[tokio::test]
async fn whatsapp_canonical_ingest_endpoint_contract() {
    let pool = support::postgres::test_pool()
        .await
        .expect("dedicated PostgreSQL test harness must initialize");
    truncate_events(&pool).await;

    let state = app_state(pool.clone(), enabled_ingress(&pool));
    let queue = state.webhook_queue.clone();
    let router = app(state);
    let body = text_payload("wamid.mcg4-contract");
    let received_after = chrono::Utc::now();

    let inserted = send_signed(&router, body.clone()).await;
    assert_empty_status(inserted, StatusCode::OK).await;
    assert_eq!(queue.len(), 0);

    let row = sqlx::query("SELECT * FROM canonical_inbound_events")
        .fetch_one(&pool)
        .await
        .expect("ACKed canonical event must be durable");
    let event_id = row.get::<Uuid, _>("event_id");
    assert_eq!(event_id.get_version_num(), 4);
    assert_eq!(
        row.get::<String, _>("schema_version"),
        "messaging.inbound.v1"
    );
    assert_eq!(row.get::<String, _>("channel"), "whatsapp");
    assert_eq!(row.get::<String, _>("account_external_id"), PHONE_NUMBER_ID);
    assert_eq!(
        row.get::<String, _>("external_message_id"),
        "wamid.mcg4-contract"
    );
    assert_eq!(row.get::<String, _>("direction"), "inbound");
    assert_eq!(row.get::<String, _>("sender_external_id"), "15550001111");
    assert_eq!(
        row.get::<String, _>("recipient_external_id"),
        PHONE_NUMBER_ID
    );
    assert_eq!(row.get::<String, _>("message_type"), "text");
    assert_eq!(row.get::<String, _>("content_text"), "canonical hello");
    assert_eq!(row.get::<String, _>("processing_status"), "accepted");
    assert_eq!(
        row.get::<chrono::DateTime<chrono::Utc>, _>("occurred_at"),
        chrono::DateTime::from_timestamp(1_710_000_000, 0).unwrap()
    );
    let received_at = row.get::<chrono::DateTime<chrono::Utc>, _>("received_at");
    assert!(received_at >= received_after);
    assert_eq!(
        row.get::<chrono::DateTime<chrono::Utc>, _>("retention_expires_at"),
        received_at + chrono::Duration::days(30)
    );
    assert_eq!(
        row.get::<String, _>("payload_sha256"),
        hex::encode(Sha256::digest(&body))
    );

    let duplicate = send_signed(&router, body).await;
    assert_empty_status(duplicate, StatusCode::OK).await;
    assert_eq!(event_count(&pool).await, 1);
    assert_eq!(queue.len(), 0);

    for unsupported in [status_payload(), non_text_payload()] {
        let response = send_signed(&router, unsupported).await;
        assert_empty_status(response, StatusCode::OK).await;
    }
    assert_eq!(event_count(&pool).await, 1);
    assert_eq!(queue.len(), 0);

    for malformed in malformed_payloads() {
        let response = send_signed(&router, malformed).await;
        assert_empty_status(response, StatusCode::BAD_REQUEST).await;
    }
    assert_eq!(event_count(&pool).await, 1);

    let mismatched = send_signed(
        &router,
        text_payload("wamid.wrong-account").replace(PHONE_NUMBER_ID, "other-account"),
    )
    .await;
    assert_empty_status(mismatched, StatusCode::FORBIDDEN).await;
    assert_eq!(event_count(&pool).await, 1);

    let invalid_signature = router
        .clone()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .header("x-hub-signature-256", format!("sha256={}", "0".repeat(64)))
                .body(Body::from("{not-json"))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_empty_status(invalid_signature, StatusCode::UNAUTHORIZED).await;
    assert_eq!(event_count(&pool).await, 1);
    assert_eq!(queue.len(), 0);

    assert_persistence_failure_is_retryable().await;
}

fn app(state: AppState) -> Router {
    Router::new()
        .route(
            "/webhooks/whatsapp",
            get(verify_whatsapp_subscription).post(receive_whatsapp_webhook),
        )
        .with_state(state)
}

fn app_state(pool: PgPool, whatsapp_ingress: Option<WhatsAppIngressState>) -> AppState {
    AppState {
        pool,
        jwt_secret: Arc::new("mcg4-test-jwt-secret".to_owned()),
        websocket_hub: Arc::new(WebSocketHub::new()),
        webhook_queue: Arc::new(WebhookQueue::new(8)),
        latency_tracker: Arc::new(LatencyTracker::new()),
        ai_worker_runtime: Arc::new(AiWorkerRuntimeMode::disabled("test")),
        whatsapp_ingress,
    }
}

fn enabled_ingress(pool: &PgPool) -> Option<WhatsAppIngressState> {
    let config = WhatsAppIngressConfig {
        verify_token: "mcg4-test-verify-token".to_owned(),
        app_secret: APP_SECRET.to_owned(),
        phone_number_id: PHONE_NUMBER_ID.to_owned(),
        retention_days: 30,
    };
    Some(WhatsAppIngressState::enabled(
        config,
        InboundEventRepository::new(pool.clone()),
    ))
}

async fn send_signed(router: &Router, body: String) -> axum::response::Response {
    let mut mac = Hmac::<Sha256>::new_from_slice(APP_SECRET.as_bytes()).unwrap();
    mac.update(body.as_bytes());
    let signature = format!("sha256={}", hex::encode(mac.finalize().into_bytes()));

    router
        .clone()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .header("x-hub-signature-256", signature)
                .body(Body::from(body))
                .unwrap(),
        )
        .await
        .unwrap()
}

async fn assert_empty_status(response: axum::response::Response, expected: StatusCode) {
    assert_eq!(response.status(), expected);
    assert!(to_bytes(response.into_body(), 1024)
        .await
        .unwrap()
        .is_empty());
}

fn text_payload(message_id: &str) -> String {
    json!({
        "object": "whatsapp_business_account",
        "entry": [{
            "changes": [{
                "field": "messages",
                "value": {
                    "messaging_product": "whatsapp",
                    "metadata": {"phone_number_id": PHONE_NUMBER_ID},
                    "messages": [{
                        "from": "15550001111",
                        "id": message_id,
                        "timestamp": "1710000000",
                        "type": "text",
                        "text": {"body": "canonical hello"}
                    }]
                }
            }]
        }]
    })
    .to_string()
}

fn status_payload() -> String {
    json!({
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "metadata": {"phone_number_id": PHONE_NUMBER_ID},
            "statuses": [{"status": "delivered"}]
        }}]}]
    })
    .to_string()
}

fn non_text_payload() -> String {
    json!({
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "metadata": {"phone_number_id": PHONE_NUMBER_ID},
            "messages": [{"type": "image"}]
        }}]}]
    })
    .to_string()
}

fn malformed_payloads() -> Vec<String> {
    let valid: Value = serde_json::from_str(&text_payload("wamid.malformed-base")).unwrap();
    let mutation = |pointer: &str, replacement: Option<Value>| {
        let mut payload = valid.clone();
        if let Some(value) = replacement {
            *payload.pointer_mut(pointer).unwrap() = value;
        } else {
            let (parent, key) = pointer.rsplit_once('/').unwrap();
            payload
                .pointer_mut(parent)
                .unwrap()
                .as_object_mut()
                .unwrap()
                .remove(key);
        }
        payload.to_string()
    };

    let message = "/entry/0/changes/0/value/messages/0";
    let mut payloads = vec![
        "{}".to_owned(),
        json!({"object": "whatsapp_business_account", "entry": []}).to_string(),
        mutation("/entry/0/changes/0/value/metadata", None),
        mutation("/entry/0/changes/0/value/metadata/phone_number_id", None),
    ];
    for (field, replacement) in [
        ("id", None),
        ("id", Some(json!(""))),
        ("from", None),
        ("from", Some(json!(""))),
        ("type", None),
        ("timestamp", None),
        ("timestamp", Some(json!("not-a-timestamp"))),
        ("text", None),
        ("text", Some(json!({}))),
        ("text", Some(json!({"body": ""}))),
        ("text", Some(json!({"body": "x".repeat(4097)}))),
    ] {
        payloads.push(mutation(&format!("{message}/{field}"), replacement));
    }
    payloads
}

async fn truncate_events(pool: &PgPool) {
    sqlx::query("TRUNCATE TABLE canonical_inbound_events")
        .execute(pool)
        .await
        .expect("canonical test table must be truncatable");
}

async fn event_count(pool: &PgPool) -> i64 {
    sqlx::query_scalar("SELECT COUNT(*) FROM canonical_inbound_events")
        .fetch_one(pool)
        .await
        .expect("canonical row count must be readable")
}

async fn assert_persistence_failure_is_retryable() {
    let test_database_url = std::env::var("TEST_DATABASE_URL").unwrap();
    let options = PgConnectOptions::from_str(&test_database_url)
        .unwrap()
        .database(&format!("mcg4_missing_{}", Uuid::new_v4().simple()))
        .disable_statement_logging();
    let pool = PgPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(Duration::from_secs(2))
        .connect_lazy_with(options);
    let state = app_state(pool.clone(), enabled_ingress(&pool));

    let response = send_signed(&app(state), text_payload("wamid.unavailable")).await;

    assert_empty_status(response, StatusCode::SERVICE_UNAVAILABLE).await;
}
