use std::sync::{atomic::AtomicU64, Arc};

use axum::{body::Body, http::Request, routing::get, Router};
use hmac::{Hmac, Mac};
use rust_control_plane::{
    handlers::whatsapp_webhook::{receive_whatsapp_webhook, verify_whatsapp_subscription},
    messaging::{InboundEventRepository, WhatsAppIngressConfig, WhatsAppIngressState},
    observability::LatencyTracker,
    queue::{WebhookEvent, WebhookQueue},
    state::{AiWorkerRuntimeMode, AppState},
    websocket::WebSocketHub,
};
use serde_json::json;
use sha2::Sha256;
use sqlx::PgPool;
use tower::ServiceExt;

pub const APP_SECRET: &str = "mcg5-test-app-secret";
pub const PHONE_NUMBER_ID: &str = "mcg5-test-phone-number-id";

pub fn app(state: AppState) -> Router {
    Router::new()
        .route(
            "/webhooks/whatsapp",
            get(verify_whatsapp_subscription).post(receive_whatsapp_webhook),
        )
        .with_state(state)
}

pub fn app_state(pool: PgPool, whatsapp_ingress: Option<WhatsAppIngressState>) -> AppState {
    AppState {
        pool,
        jwt_secret: Arc::new("mcg5-test-jwt-secret".to_owned()),
        websocket_hub: Arc::new(WebSocketHub::new()),
        webhook_queue: Arc::new(WebhookQueue::new(8)),
        latency_tracker: Arc::new(LatencyTracker::new()),
        ai_worker_runtime: Arc::new(AiWorkerRuntimeMode::disabled("test")),
        whatsapp_ingress,
    }
}

pub fn observed_app_state(
    pool: PgPool,
    whatsapp_ingress: Option<WhatsAppIngressState>,
) -> (AppState, tokio::sync::mpsc::Receiver<WebhookEvent>) {
    let (sender, receiver) = tokio::sync::mpsc::channel(8);
    let queue = Arc::new(WebhookQueue::from_sender(
        sender,
        8,
        Arc::new(AtomicU64::new(7)),
    ));
    let mut state = app_state(pool, whatsapp_ingress);
    state.webhook_queue = queue;
    (state, receiver)
}

pub fn enabled_ingress(pool: &PgPool) -> WhatsAppIngressState {
    WhatsAppIngressState::enabled(
        WhatsAppIngressConfig {
            verify_token: "mcg5-test-verify-token".to_owned(),
            app_secret: APP_SECRET.to_owned(),
            phone_number_id: PHONE_NUMBER_ID.to_owned(),
            retention_days: 30,
        },
        InboundEventRepository::new(pool.clone()),
    )
}

pub async fn send_signed(router: &Router, body: String) -> axum::response::Response {
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

pub fn text_payload(message_id: &str) -> String {
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

pub async fn truncate_events(pool: &PgPool) {
    sqlx::query("TRUNCATE TABLE canonical_inbound_events")
        .execute(pool)
        .await
        .expect("canonical test table must be truncatable");
}
