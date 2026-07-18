mod support;

use std::{str::FromStr, time::Duration};

use axum::{
    body::{to_bytes, Body},
    http::{Request, StatusCode},
    routing::get,
    Router,
};
use rust_control_plane::health::ready::readiness_check;
use rust_control_plane::metrics::metrics_endpoint;
use serde_json::Value;
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions},
    ConnectOptions, Executor, PgPool,
};
use tower::ServiceExt;
use uuid::Uuid;

#[tokio::test]
async fn persistence_and_readiness_fail_closed_without_applying_schema() {
    let test_database_url = std::env::var("TEST_DATABASE_URL")
        .expect("TEST_DATABASE_URL must remain available for failure tests");

    let unavailable_pool = unavailable_pool(&test_database_url);
    let unavailable_state = support::whatsapp::app_state(
        unavailable_pool.clone(),
        Some(support::whatsapp::enabled_ingress(&unavailable_pool)),
    );
    let unavailable_response = support::whatsapp::send_signed(
        &support::whatsapp::app(unavailable_state.clone()),
        support::whatsapp::text_payload("wamid.mcg5-unavailable"),
    )
    .await;
    assert_safe_empty_503(unavailable_response).await;
    let unavailable_readiness = readiness_response(unavailable_state).await;
    assert_eq!(
        unavailable_readiness.status(),
        StatusCode::SERVICE_UNAVAILABLE
    );
    let unavailable_body = String::from_utf8(
        to_bytes(unavailable_readiness.into_body(), 4096)
            .await
            .unwrap()
            .to_vec(),
    )
    .unwrap();
    for forbidden in [
        test_database_url.as_str(),
        "PostgreSQL:",
        "PoolTimedOut",
        "pool timed out",
        "connection refused",
    ] {
        assert!(!unavailable_body.contains(forbidden));
    }

    let transaction_failure_pool = support::postgres::test_pool()
        .await
        .expect("transaction failure fixture database must initialize");
    support::whatsapp::truncate_events(&transaction_failure_pool).await;
    install_rejecting_trigger(&transaction_failure_pool).await;
    let transaction_failure_state = support::whatsapp::app_state(
        transaction_failure_pool.clone(),
        Some(support::whatsapp::enabled_ingress(
            &transaction_failure_pool,
        )),
    );
    let transaction_failure_response = support::whatsapp::send_signed(
        &support::whatsapp::app(transaction_failure_state),
        support::whatsapp::text_payload("wamid.mcg5-transaction-failure"),
    )
    .await;
    assert_safe_empty_503(transaction_failure_response).await;
    let partial_rows: i64 = sqlx::query_scalar(
        "SELECT COUNT(*) FROM canonical_inbound_events WHERE external_message_id = $1",
    )
    .bind("wamid.mcg5-transaction-failure")
    .fetch_one(&transaction_failure_pool)
    .await
    .expect("failed transaction row count must be readable");
    assert_eq!(partial_rows, 0);
    remove_rejecting_trigger(&transaction_failure_pool).await;

    let schema_missing_pool = schema_missing_pool(&test_database_url).await;
    assert_schema_absent(&schema_missing_pool).await;
    let schema_missing_state = support::whatsapp::app_state(
        schema_missing_pool.clone(),
        Some(support::whatsapp::enabled_ingress(&schema_missing_pool)),
    );

    let ingress_response = support::whatsapp::send_signed(
        &support::whatsapp::app(schema_missing_state.clone()),
        support::whatsapp::text_payload("wamid.mcg5-schema-missing"),
    )
    .await;
    assert_safe_empty_503(ingress_response).await;
    assert_schema_absent(&schema_missing_pool).await;

    let readiness_response = readiness_response(schema_missing_state).await;
    assert_eq!(readiness_response.status(), StatusCode::SERVICE_UNAVAILABLE);
    let readiness_body = to_bytes(readiness_response.into_body(), 4096)
        .await
        .unwrap();
    let readiness_json: Value = serde_json::from_slice(&readiness_body).unwrap();
    assert_eq!(readiness_json["status"], "not_ready");
    assert_eq!(readiness_json["whatsapp_ingress"], "not_ready");
    let rendered = String::from_utf8(readiness_body.to_vec()).unwrap();
    for forbidden in [
        &test_database_url,
        support::whatsapp::APP_SECRET,
        support::whatsapp::PHONE_NUMBER_ID,
        "canonical_inbound_events does not exist",
        "42P01",
    ] {
        assert!(!rendered.contains(forbidden));
    }
    assert_schema_absent(&schema_missing_pool).await;

    let disabled_state = support::whatsapp::app_state(schema_missing_pool, None);
    let disabled_response = support::whatsapp::send_signed(
        &support::whatsapp::app(disabled_state),
        support::whatsapp::text_payload("wamid.mcg5-disabled"),
    )
    .await;
    assert_safe_empty_503(disabled_response).await;

    let metrics = String::from_utf8(
        to_bytes(metrics_endpoint().await.into_body(), 64 * 1024)
            .await
            .unwrap()
            .to_vec(),
    )
    .unwrap();
    assert!(metrics.contains("whatsapp_ingest_persistence_failures_total{reason=\"pool\"}"));
    assert!(metrics.contains("whatsapp_ingest_persistence_failures_total{reason=\"schema\"}"));
    assert!(metrics.contains("whatsapp_ingest_persistence_failures_total{reason=\"database\"}"));
    assert!(!metrics.contains(&test_database_url));
}

async fn install_rejecting_trigger(pool: &PgPool) {
    remove_rejecting_trigger(pool).await;
    sqlx::query(
        "CREATE FUNCTION mcg5_reject_canonical_insert() RETURNS trigger AS $$ \
         BEGIN \
             IF NEW.external_message_id = 'wamid.mcg5-transaction-failure' THEN \
                 RAISE EXCEPTION 'injected canonical persistence failure' USING ERRCODE = 'P0001'; \
             END IF; \
             RETURN NEW; \
         END; \
         $$ LANGUAGE plpgsql",
    )
    .execute(pool)
    .await
    .expect("rejecting trigger function must be created");
    sqlx::query(
        "CREATE TRIGGER mcg5_reject_canonical_insert \
         BEFORE INSERT ON canonical_inbound_events \
         FOR EACH ROW EXECUTE FUNCTION mcg5_reject_canonical_insert()",
    )
    .execute(pool)
    .await
    .expect("rejecting trigger must be created");
}

async fn remove_rejecting_trigger(pool: &PgPool) {
    sqlx::query("DROP TRIGGER IF EXISTS mcg5_reject_canonical_insert ON canonical_inbound_events")
        .execute(pool)
        .await
        .expect("rejecting trigger cleanup must succeed");
    sqlx::query("DROP FUNCTION IF EXISTS mcg5_reject_canonical_insert()")
        .execute(pool)
        .await
        .expect("rejecting trigger function cleanup must succeed");
}

async fn readiness_response(
    state: rust_control_plane::state::AppState,
) -> axum::response::Response {
    Router::new()
        .route("/health/ready", get(readiness_check))
        .with_state(state)
        .oneshot(
            Request::builder()
                .uri("/health/ready")
                .body(Body::empty())
                .unwrap(),
        )
        .await
        .unwrap()
}

fn unavailable_pool(test_database_url: &str) -> PgPool {
    let options = PgConnectOptions::from_str(test_database_url)
        .expect("TEST_DATABASE_URL must be valid")
        .database(&format!("mcg5_missing_{}", Uuid::new_v4().simple()))
        .disable_statement_logging();
    PgPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(Duration::from_secs(2))
        .connect_lazy_with(options)
}

async fn schema_missing_pool(test_database_url: &str) -> PgPool {
    let options = PgConnectOptions::from_str(test_database_url)
        .expect("TEST_DATABASE_URL must be valid")
        .disable_statement_logging();
    PgPoolOptions::new()
        .max_connections(2)
        .after_connect(|connection, _| {
            Box::pin(async move {
                connection.execute("SET search_path TO pg_catalog").await?;
                Ok(())
            })
        })
        .connect_with(options)
        .await
        .expect("missing-schema pool must connect")
}

async fn assert_schema_absent(pool: &PgPool) {
    let relation: Option<String> =
        sqlx::query_scalar("SELECT to_regclass('canonical_inbound_events')::text")
            .fetch_one(pool)
            .await
            .expect("schema absence must be queryable");
    assert!(relation.is_none(), "runtime must not auto-apply migrations");
}

async fn assert_safe_empty_503(response: axum::response::Response) {
    assert_eq!(response.status(), StatusCode::SERVICE_UNAVAILABLE);
    assert!(to_bytes(response.into_body(), 4096)
        .await
        .unwrap()
        .is_empty());
}
