mod support;

use axum::{body::to_bytes, http::StatusCode};
use sqlx::Row;
use tokio::sync::Barrier;
use uuid::Uuid;

#[tokio::test]
async fn ten_concurrent_duplicates_and_restart_preserve_one_durable_record() {
    let pool = support::postgres::test_pool()
        .await
        .expect("dedicated PostgreSQL test harness must initialize");
    support::whatsapp::truncate_events(&pool).await;

    let (initial_state, mut initial_queue_receiver) = support::whatsapp::observed_app_state(
        pool.clone(),
        Some(support::whatsapp::enabled_ingress(&pool)),
    );
    let initial_queue = initial_state.webhook_queue.clone();
    let initial_queue_pending = initial_queue.len();
    let initial_router = support::whatsapp::app(initial_state);
    let body = support::whatsapp::text_payload("wamid.mcg5-concurrent");

    let barrier = std::sync::Arc::new(Barrier::new(11));
    let mut requests = Vec::new();
    for _ in 0..10 {
        let barrier = barrier.clone();
        let router = initial_router.clone();
        let body = body.clone();
        requests.push(tokio::spawn(async move {
            barrier.wait().await;
            support::whatsapp::send_signed(&router, body).await
        }));
    }
    barrier.wait().await;
    let mut responses = Vec::new();
    for request in requests {
        responses.push(request.await.expect("concurrent request must not panic"));
    }

    assert_eq!(responses.len(), 10);
    for response in responses {
        assert_eq!(response.status(), StatusCode::OK);
        assert!(to_bytes(response.into_body(), 1024)
            .await
            .unwrap()
            .is_empty());
    }
    assert_eq!(initial_queue.len(), initial_queue_pending);
    assert_eq!(initial_queue.rejection_count(), 0);
    assert!(matches!(
        initial_queue_receiver.try_recv(),
        Err(tokio::sync::mpsc::error::TryRecvError::Empty)
    ));

    let row = sqlx::query(
        "SELECT event_id, processing_status FROM canonical_inbound_events \
         WHERE channel = 'whatsapp' AND account_external_id = $1 AND external_message_id = $2",
    )
    .bind(support::whatsapp::PHONE_NUMBER_ID)
    .bind("wamid.mcg5-concurrent")
    .fetch_one(&pool)
    .await
    .expect("exactly one ACKed row must remain durable");
    let accepted_event_id = row.get::<Uuid, _>("event_id");
    assert_eq!(row.get::<String, _>("processing_status"), "accepted");
    let row_count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM canonical_inbound_events")
        .fetch_one(&pool)
        .await
        .expect("canonical row count must be readable");
    assert_eq!(row_count, 1);

    drop(initial_router);
    pool.close().await;
    let restarted_pool = support::postgres::test_pool()
        .await
        .expect("restart must reconnect to the same dedicated database");
    let (restarted_state, mut restarted_queue_receiver) = support::whatsapp::observed_app_state(
        restarted_pool.clone(),
        Some(support::whatsapp::enabled_ingress(&restarted_pool)),
    );
    let restarted_queue = restarted_state.webhook_queue.clone();
    let restarted_queue_pending = restarted_queue.len();
    let restarted_router = support::whatsapp::app(restarted_state);

    let duplicate = support::whatsapp::send_signed(&restarted_router, body).await;

    assert_eq!(duplicate.status(), StatusCode::OK);
    assert!(to_bytes(duplicate.into_body(), 1024)
        .await
        .unwrap()
        .is_empty());
    let restarted_event_id: Uuid = sqlx::query_scalar(
        "SELECT event_id FROM canonical_inbound_events WHERE external_message_id = $1",
    )
    .bind("wamid.mcg5-concurrent")
    .fetch_one(&restarted_pool)
    .await
    .expect("reconstructed repository must find the ACKed record");
    assert_eq!(restarted_event_id, accepted_event_id);
    assert_eq!(restarted_queue.len(), restarted_queue_pending);
    assert_eq!(restarted_queue.rejection_count(), 0);
    assert!(matches!(
        restarted_queue_receiver.try_recv(),
        Err(tokio::sync::mpsc::error::TryRecvError::Empty)
    ));
}
