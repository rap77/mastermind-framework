// DLQ Repository Tests - TDD RED phase
// These tests verify the Dead Letter Queue functionality

use chrono::Utc;
use rust_control_plane::dlq::{DeadLetterQueue, FailedWebhook};
use serde_json::json;
use sqlx::PgPool;
use uuid::Uuid;

#[sqlx::test]
async fn test_dlq_repository_insert() {
    // This test should FAIL initially - TDD RED phase
    let pool = setup_test_db().await;

    let dlq = DeadLetterQueue::new(pool.clone());

    let external_id = "test-msg-123";
    let channel = "whatsapp";
    let payload = json!({"from": "1234567890", "message": "Hello"});
    let error = "Connection timeout";

    // Test: move_to_dlq inserts failed webhook
    let result = dlq
        .move_to_dlq(external_id, channel, payload.clone(), error)
        .await;

    assert!(result.is_ok(), "move_to_dlq should succeed");

    // Verify webhook was inserted
    let failed_webhooks = dlq.get_failed_webhooks(10, 0).await.unwrap();
    assert_eq!(failed_webhooks.len(), 1, "Should have 1 failed webhook");

    let webhook = &failed_webhooks[0];
    assert_eq!(webhook.external_message_id, external_id);
    assert_eq!(webhook.channel, channel);
    assert_eq!(webhook.retry_count, 0);
}

#[sqlx::test]
async fn test_dlq_repository_retry() {
    let pool = setup_test_db().await;
    let dlq = DeadLetterQueue::new(pool.clone());

    // Insert a failed webhook
    let external_id = "test-msg-456";
    let channel = "instagram";
    let payload = json!({"media_id": "abc123"});
    let error = "Rate limit exceeded";

    dlq.move_to_dlq(external_id, channel, payload, error)
        .await
        .unwrap();

    let failed_webhooks = dlq.get_failed_webhooks(10, 0).await.unwrap();
    let webhook_id = failed_webhooks[0].id;

    // Test: retry_webhook increments retry_count and updates last_retry_at
    let result = dlq.retry_webhook(webhook_id).await;
    assert!(result.is_ok(), "retry_webhook should succeed");

    // Verify retry_count incremented
    let updated_webhooks = dlq.get_failed_webhooks(10, 0).await.unwrap();
    assert_eq!(updated_webhooks[0].retry_count, 1, "retry_count should be 1");
    assert!(
        updated_webhooks[0].last_retry_at.is_some(),
        "last_retry_at should be set"
    );
}

#[sqlx::test]
async fn test_dlq_repository_pagination() {
    let pool = setup_test_db().await;
    let dlq = DeadLetterQueue::new(pool.clone());

    // Insert 25 failed webhooks
    for i in 0..25 {
        let external_id = format!("msg-{}", i);
        let channel = if i % 2 == 0 { "whatsapp" } else { "email" };
        let payload = json!({"index": i});
        let error = "Test error";

        dlq.move_to_dlq(&external_id, channel, payload, error)
            .await
            .unwrap();
    }

    // Test pagination with limit=10, offset=0
    let page1 = dlq.get_failed_webhooks(10, 0).await.unwrap();
    assert_eq!(page1.len(), 10, "First page should have 10 webhooks");

    // Test pagination with limit=10, offset=10
    let page2 = dlq.get_failed_webhooks(10, 10).await.unwrap();
    assert_eq!(page2.len(), 10, "Second page should have 10 webhooks");

    // Verify different webhooks
    assert_ne!(
        page1[0].external_message_id,
        page2[0].external_message_id,
        "Pages should have different webhooks"
    );
}

#[sqlx::test]
async fn test_dlq_get_retry_count() {
    let pool = setup_test_db().await;
    let dlq = DeadLetterQueue::new(pool.clone());

    let external_id = "test-msg-retry-count";
    let channel = "email";
    let payload = json!({"subject": "Test"});
    let error = "SMTP error";

    dlq.move_to_dlq(external_id, channel, payload, error)
        .await
        .unwrap();

    let failed_webhooks = dlq.get_failed_webhooks(10, 0).await.unwrap();
    let webhook_id = failed_webhooks[0].id;

    // Test initial retry_count is 0
    let retry_count = dlq.get_retry_count(webhook_id).await.unwrap();
    assert_eq!(retry_count, 0, "Initial retry_count should be 0");

    // Retry twice
    dlq.retry_webhook(webhook_id).await.unwrap();
    dlq.retry_webhook(webhook_id).await.unwrap();

    // Verify retry_count is now 2
    let retry_count = dlq.get_retry_count(webhook_id).await.unwrap();
    assert_eq!(retry_count, 2, "retry_count should be 2 after 2 retries");
}

// Helper function to set up test database
async fn setup_test_db() -> PgPool {
    // Use environment variable for test database URL
    let database_url = std::env::var("TEST_DATABASE_URL")
        .unwrap_or_else(|_| "postgresql://postgres:postgres@localhost:5432/mastermind_test".to_string());

    let pool = PgPool::connect(&database_url)
        .await
        .expect("Failed to connect to test database");

    // Run migrations for DLQ table
    sqlx::query(
        r#"
        CREATE TABLE IF NOT EXISTS webhook_dlq (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            external_message_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            payload JSONB NOT NULL,
            error_message TEXT NOT NULL,
            retry_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT NOW(),
            last_retry_at TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_dlq_retry_count ON webhook_dlq(retry_count, created_at);

        TRUNCATE TABLE webhook_dlq;
        "#,
    )
    .execute(&pool)
    .await
    .expect("Failed to create DLQ table");

    pool
}
