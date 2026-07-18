mod support;

use std::{
    io::{self, Write},
    sync::{Arc, Mutex},
};

use axum::{
    body::{to_bytes, Body},
    http::Request,
};
use rust_control_plane::metrics::metrics_endpoint;
use serde_json::json;
use sha2::{Digest, Sha256};
use tower::ServiceExt;
use tracing_subscriber::fmt::MakeWriter;

#[derive(Clone, Default)]
struct LogCapture(Arc<Mutex<Vec<u8>>>);

struct LogWriter(Arc<Mutex<Vec<u8>>>);

impl Write for LogWriter {
    fn write(&mut self, bytes: &[u8]) -> io::Result<usize> {
        self.0.lock().unwrap().extend_from_slice(bytes);
        Ok(bytes.len())
    }

    fn flush(&mut self) -> io::Result<()> {
        Ok(())
    }
}

impl<'a> MakeWriter<'a> for LogCapture {
    type Writer = LogWriter;

    fn make_writer(&'a self) -> Self::Writer {
        LogWriter(self.0.clone())
    }
}

#[tokio::test(flavor = "current_thread")]
async fn whatsapp_observability_uses_only_safe_fixed_dimensions() {
    let pool = support::postgres::test_pool()
        .await
        .expect("dedicated PostgreSQL test harness must initialize");
    support::whatsapp::truncate_events(&pool).await;
    let (state, mut queue_receiver) = support::whatsapp::observed_app_state(
        pool.clone(),
        Some(support::whatsapp::enabled_ingress(&pool)),
    );
    let queue = state.webhook_queue.clone();
    let queue_pending_before = queue.len();
    let router = support::whatsapp::app(state);
    let capture = LogCapture::default();
    let subscriber = tracing_subscriber::fmt()
        .json()
        .with_writer(capture.clone())
        .with_max_level(tracing::Level::INFO)
        .finish();
    let _guard = tracing::subscriber::set_default(subscriber);

    let sensitive_payload = support::whatsapp::text_payload("wamid.mcg5-sensitive-id");
    let payload_digest = hex::encode(Sha256::digest(sensitive_payload.as_bytes()));
    support::whatsapp::send_signed(&router, sensitive_payload.clone()).await;
    support::whatsapp::send_signed(&router, sensitive_payload.clone()).await;
    support::whatsapp::send_signed(&router, unsupported_payload()).await;
    support::whatsapp::send_signed(&router, "{malformed-json".to_owned()).await;
    support::whatsapp::send_signed(
        &router,
        sensitive_payload.replace(
            support::whatsapp::PHONE_NUMBER_ID,
            "mcg5-other-phone-number",
        ),
    )
    .await;
    router
        .clone()
        .oneshot(
            Request::builder()
                .method("POST")
                .uri("/webhooks/whatsapp")
                .header("x-hub-signature-256", format!("sha256={}", "0".repeat(64)))
                .body(Body::from("mcg5-raw-secret-body"))
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(queue.len(), queue_pending_before);
    assert_eq!(queue.rejection_count(), 0);
    assert!(matches!(
        queue_receiver.try_recv(),
        Err(tokio::sync::mpsc::error::TryRecvError::Empty)
    ));
    let metrics = String::from_utf8(
        to_bytes(metrics_endpoint().await.into_body(), 64 * 1024)
            .await
            .unwrap()
            .to_vec(),
    )
    .unwrap();
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"inserted\"}"));
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"duplicate\"}"));
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"unsupported\"}"));
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"invalid_signature\"}"));
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"invalid_payload\"}"));
    assert!(metrics.contains("whatsapp_ingest_requests_total{outcome=\"account_mismatch\"}"));
    assert!(metrics.contains("whatsapp_ingest_latency_seconds_count"));

    let logs = String::from_utf8(capture.0.lock().unwrap().clone()).unwrap();
    assert!(logs.contains("whatsapp_ingest"));
    assert!(logs.contains("\"channel\":\"whatsapp\""));
    for forbidden in [
        "15550001111",
        support::whatsapp::PHONE_NUMBER_ID,
        "mcg5-other-phone-number",
        "canonical hello",
        "mcg5-raw-secret-body",
        "wamid.mcg5-sensitive-id",
        support::whatsapp::APP_SECRET,
        "mcg5-test-verify-token",
        &payload_digest,
        "x-hub-signature-256",
        "sha256=",
    ] {
        assert!(!logs.contains(forbidden));
        assert!(!metrics.contains(forbidden));
    }

    for line in metrics
        .lines()
        .filter(|line| line.starts_with("whatsapp_ingest_") && !line.starts_with('#'))
    {
        if let Some((_, labels_and_value)) = line.split_once('{') {
            let labels = labels_and_value.split_once('}').unwrap().0;
            let fixed_business_label =
                labels.starts_with("outcome=\"") || labels.starts_with("reason=\"");
            let histogram_bucket = line.starts_with("whatsapp_ingest_latency_seconds_bucket{")
                && labels.starts_with("le=\"");
            assert!(fixed_business_label || histogram_bucket);
            assert!(!labels.contains(','), "only one fixed dimension is allowed");
        }
    }

    let ingress_state_source = include_str!("../src/messaging/state.rs");
    let ingress_handler_source = include_str!("../src/handlers/whatsapp_webhook.rs");
    for forbidden_capability in [
        "WebhookQueue",
        "crate::queue",
        "crate::grpc",
        "AiWorker",
        "outbound",
    ] {
        assert!(!ingress_state_source.contains(forbidden_capability));
        assert!(!ingress_handler_source.contains(forbidden_capability));
    }
}

fn unsupported_payload() -> String {
    json!({
        "object": "whatsapp_business_account",
        "entry": [{"changes": [{"field": "messages", "value": {
            "metadata": {"phone_number_id": support::whatsapp::PHONE_NUMBER_ID},
            "statuses": [{"status": "delivered"}]
        }}]}]
    })
    .to_string()
}
