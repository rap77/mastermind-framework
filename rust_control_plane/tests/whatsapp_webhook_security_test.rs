use std::sync::{
    atomic::{AtomicU64, Ordering},
    Arc,
};

use axum::{
    body::{to_bytes, Body},
    http::{HeaderValue, Request, StatusCode},
    routing::{get, post},
    Router,
};
use hmac::{Hmac, Mac};
use rust_control_plane::{
    handlers::{
        webhook::webhook_receiver,
        whatsapp_webhook::{receive_whatsapp_webhook, verify_whatsapp_subscription},
    },
    messaging::{InboundEventRepository, WhatsAppIngressConfig, WhatsAppIngressState},
    observability::LatencyTracker,
    queue::WebhookQueue,
    state::{AiWorkerRuntimeMode, AppState},
    websocket::WebSocketHub,
};
use sha2::Sha256;
use sqlx::postgres::PgPoolOptions;
use tower::ServiceExt;

const APP_SECRET: &str = "test-app-secret";

fn enabled_ingress_state() -> WhatsAppIngressState {
    let pool = PgPoolOptions::new()
        .connect_lazy("postgresql://postgres:postgres@localhost/mastermind_test")
        .expect("lazy test pool URL must be valid");
    WhatsAppIngressState::enabled(
        WhatsAppIngressConfig {
            verify_token: "test-verify-token".to_owned(),
            app_secret: APP_SECRET.to_owned(),
            phone_number_id: "test-phone-number-id".to_owned(),
            retention_days: 30,
        },
        InboundEventRepository::new(pool),
    )
}

fn app_state(whatsapp_ingress: Option<WhatsAppIngressState>) -> (AppState, Arc<AtomicU64>) {
    let pool = PgPoolOptions::new()
        .connect_lazy("postgresql://postgres:postgres@localhost/mastermind_test")
        .expect("lazy test pool URL must be valid");
    let (sender, _receiver) = tokio::sync::mpsc::channel(8);
    let pending_count = Arc::new(AtomicU64::new(0));

    (
        AppState {
            pool,
            jwt_secret: Arc::new("test-jwt-secret".to_owned()),
            websocket_hub: Arc::new(WebSocketHub::new()),
            webhook_queue: Arc::new(WebhookQueue::from_sender(sender, 8, pending_count.clone())),
            latency_tracker: Arc::new(LatencyTracker::new()),
            ai_worker_runtime: Arc::new(AiWorkerRuntimeMode::disabled("test")),
            whatsapp_ingress,
        },
        pending_count,
    )
}

fn app(state: AppState) -> Router {
    Router::new()
        .route(
            "/webhooks/whatsapp",
            get(verify_whatsapp_subscription).post(receive_whatsapp_webhook),
        )
        .route("/webhooks/:channel", post(webhook_receiver))
        .with_state(state)
}

fn signature(body: &[u8]) -> String {
    let mut mac = Hmac::<Sha256>::new_from_slice(APP_SECRET.as_bytes())
        .expect("HMAC accepts arbitrary key lengths");
    mac.update(body);
    format!("sha256={}", hex::encode(mac.finalize().into_bytes()))
}

#[tokio::test]
async fn whatsapp_webhook_security_get_echoes_challenge_for_matching_token() {
    let (state, _) = app_state(Some(enabled_ingress_state()));
    let response = app(state)
        .oneshot(
            Request::builder()
                .uri(
                    "/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=test-verify-token&hub.challenge=challenge-123",
                )
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::OK);
    let body = to_bytes(response.into_body(), 1024).await.unwrap();
    assert_eq!(body.as_ref(), b"challenge-123");
}

#[tokio::test]
async fn whatsapp_webhook_security_get_rejects_mismatched_token() {
    let (state, _) = app_state(Some(enabled_ingress_state()));
    let router = app(state);
    let response = router
        .clone()
        .oneshot(
            Request::builder()
                .uri(
                    "/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=wrong&hub.challenge=challenge-123",
                )
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::FORBIDDEN);

    let wrong_mode_response = router
        .oneshot(
            Request::builder()
                .uri(
                    "/webhooks/whatsapp?hub.mode=unsubscribe&hub.verify_token=test-verify-token&hub.challenge=challenge-123",
                )
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(wrong_mode_response.status(), StatusCode::FORBIDDEN);
}

#[tokio::test]
async fn whatsapp_webhook_security_disabled_exact_route_returns_503() {
    let (state, _) = app_state(None);
    let router = app(state);
    let response = router
        .clone()
        .oneshot(
            Request::builder()
                .uri(
                    "/webhooks/whatsapp?hub.mode=subscribe&hub.verify_token=test-verify-token&hub.challenge=challenge-123",
                )
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);

    let post_response = router
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .body(Body::from("{}"))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(post_response.status(), StatusCode::SERVICE_UNAVAILABLE);
}

#[tokio::test]
async fn whatsapp_webhook_security_post_rejects_missing_or_malformed_signature() {
    let (state, _) = app_state(Some(enabled_ingress_state()));
    let router = app(state);
    let non_hex_signature = format!("sha256={}", "g".repeat(64));

    for signature in [
        None,
        Some("sha1=00"),
        Some("sha256=00"),
        Some(non_hex_signature.as_str()),
    ] {
        let mut request = Request::builder().method("POST").uri("/webhooks/whatsapp");
        if let Some(signature) = signature {
            request = request.header("x-hub-signature-256", signature);
        }
        let response = router
            .clone()
            .oneshot(request.body(Body::from("{not-json")).unwrap())
            .await
            .unwrap();

        assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
    }
}

#[tokio::test]
async fn whatsapp_webhook_security_post_rejects_duplicate_signature_headers() {
    let (state, _) = app_state(Some(enabled_ingress_state()));
    let body = b"{not-json";
    let valid_signature = HeaderValue::from_str(&signature(body)).unwrap();
    let mut request = Request::builder()
        .method("POST")
        .uri("/webhooks/whatsapp")
        .body(Body::from(body.as_slice()))
        .unwrap();
    request
        .headers_mut()
        .append("x-hub-signature-256", valid_signature.clone());
    request
        .headers_mut()
        .append("x-hub-signature-256", valid_signature);

    let response = app(state).oneshot(request).await.unwrap();

    assert_eq!(response.status(), StatusCode::UNAUTHORIZED);
}

#[tokio::test]
async fn whatsapp_webhook_security_post_verifies_exact_raw_bytes() {
    let (state, pending_count) = app_state(Some(enabled_ingress_state()));
    let router = app(state);
    let signed_body = b"{not-json";
    let signature = signature(signed_body);

    let valid_response = router
        .clone()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .header("x-hub-signature-256", &signature)
                .body(Body::from(signed_body.as_slice()))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(valid_response.status(), StatusCode::BAD_REQUEST);

    let altered_response = router
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .header("x-hub-signature-256", signature)
                .body(Body::from(b"{not-json ".as_slice()))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(altered_response.status(), StatusCode::UNAUTHORIZED);
    assert_eq!(pending_count.load(Ordering::Relaxed), 0);
}

#[tokio::test]
async fn whatsapp_webhook_security_static_route_wins_and_legacy_rejects_whatsapp() {
    let (state, pending_count) = app_state(Some(enabled_ingress_state()));

    let exact_response = app(state.clone())
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .body(Body::from("{}"))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(exact_response.status(), StatusCode::UNAUTHORIZED);

    let legacy_response = Router::new()
        .route("/legacy/:channel", post(webhook_receiver))
        .with_state(state)
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/legacy/whatsapp")
                .header("content-type", "application/json")
                .body(Body::from("{}"))
                .unwrap(),
        )
        .await
        .unwrap();
    assert_eq!(legacy_response.status(), StatusCode::BAD_REQUEST);
    assert_eq!(pending_count.load(Ordering::Relaxed), 0);
}
