mod support;

use std::{collections::BTreeMap, str::FromStr, time::Duration};

use rust_control_plane::messaging::{
    CanonicalInboundEventV1, InboundEventRepository, InboundRepositoryError, InsertOutcome,
};
use sqlx::{
    postgres::{PgConnectOptions, PgPoolOptions},
    ConnectOptions, Executor, Row,
};
use uuid::Uuid;

#[tokio::test]
async fn canonical_inbound_repository_contract() {
    let pool = support::postgres::test_pool()
        .await
        .expect("dedicated PostgreSQL test harness must initialize");

    sqlx::query("TRUNCATE TABLE canonical_inbound_events")
        .execute(&pool)
        .await
        .expect("canonical test table must be truncatable");

    assert_schema_and_data_minimization(&pool).await;

    let repository = InboundEventRepository::new(pool.clone());
    let event = canonical_event();

    assert_eq!(
        repository
            .insert_or_get(&event)
            .await
            .expect("first canonical insert must succeed"),
        InsertOutcome::Inserted {
            event_id: event.event_id
        }
    );
    let mut duplicate_event = event.clone();
    duplicate_event.event_id = Uuid::new_v4();
    assert_eq!(
        repository
            .insert_or_get(&duplicate_event)
            .await
            .expect("duplicate canonical insert must succeed"),
        InsertOutcome::Duplicate {
            event_id: event.event_id
        }
    );

    let mut event_id_collision = event.clone();
    event_id_collision.external_message_id = "wamid.different-message".to_owned();
    assert_eq!(
        repository.insert_or_get(&event_id_collision).await,
        Err(InboundRepositoryError::Database)
    );

    let stored = sqlx::query(
        "SELECT content_text, retention_expires_at FROM canonical_inbound_events WHERE event_id = $1",
    )
    .bind(event.event_id)
    .fetch_one(&pool)
    .await
    .expect("inserted canonical row must be readable");
    assert_eq!(stored.get::<String, _>("content_text"), event.content_text);
    assert_eq!(
        stored.get::<chrono::DateTime<chrono::Utc>, _>("retention_expires_at"),
        event.retention_expires_at
    );

    assert_conflicting_uncommitted_insert_is_retried(&pool, &event).await;

    sqlx::query("TRUNCATE TABLE canonical_inbound_events")
        .execute(&pool)
        .await
        .expect("canonical test table must reset before concurrency check");

    let mut requests = Vec::new();
    for _ in 0..10 {
        let repository = repository.clone();
        let mut event = event.clone();
        event.event_id = Uuid::new_v4();
        requests.push(tokio::spawn(async move {
            repository.insert_or_get(&event).await
        }));
    }

    let mut outcomes = Vec::new();
    for request in requests {
        outcomes.push(
            request
                .await
                .expect("concurrent repository task must not panic")
                .expect("concurrent duplicate must not fail"),
        );
    }

    let mut inserted = 0;
    let mut duplicates = 0;
    let persisted_event_id = outcomes
        .iter()
        .find_map(|outcome| match outcome {
            InsertOutcome::Inserted { event_id } => Some(*event_id),
            InsertOutcome::Duplicate { .. } => None,
        })
        .expect("one concurrent request must insert the row");
    for outcome in outcomes {
        match outcome {
            InsertOutcome::Inserted { event_id } => {
                assert_eq!(event_id, persisted_event_id);
                inserted += 1;
            }
            InsertOutcome::Duplicate { event_id } => {
                assert_eq!(event_id, persisted_event_id);
                duplicates += 1;
            }
        }
    }
    assert_eq!((inserted, duplicates), (1, 9));

    let row_count: i64 = sqlx::query_scalar("SELECT COUNT(*) FROM canonical_inbound_events")
        .fetch_one(&pool)
        .await
        .expect("canonical row count must be readable");
    assert_eq!(row_count, 1);

    assert_missing_schema_is_normalized(&event).await;
    assert_missing_database_is_normalized(&event).await;
}

async fn assert_conflicting_uncommitted_insert_is_retried(
    pool: &sqlx::PgPool,
    event: &CanonicalInboundEventV1,
) {
    let mut pending_event = event.clone();
    pending_event.event_id = Uuid::new_v4();
    pending_event.external_message_id = "wamid.pending-conflict".to_owned();

    let mut transaction = pool
        .begin()
        .await
        .expect("conflict fixture transaction must begin");
    sqlx::query(
        "INSERT INTO canonical_inbound_events (\
             event_id, schema_version, channel, account_external_id, external_message_id, \
             direction, sender_external_id, recipient_external_id, message_type, content_text, \
             occurred_at, received_at, payload_sha256, processing_status, retention_expires_at\
         ) VALUES (\
             $1, 'messaging.inbound.v1', 'whatsapp', $2, $3, 'inbound', $4, $5, 'text', $6, \
             $7, $8, $9, 'accepted', $10\
         )",
    )
    .bind(pending_event.event_id)
    .bind(&pending_event.account_external_id)
    .bind(&pending_event.external_message_id)
    .bind(&pending_event.sender_external_id)
    .bind(&pending_event.recipient_external_id)
    .bind(&pending_event.content_text)
    .bind(pending_event.occurred_at)
    .bind(pending_event.received_at)
    .bind(&pending_event.payload_sha256)
    .bind(pending_event.retention_expires_at)
    .execute(&mut *transaction)
    .await
    .expect("uncommitted conflict fixture must insert");

    let test_database_url = std::env::var("TEST_DATABASE_URL")
        .expect("TEST_DATABASE_URL must remain available for concurrency tests");
    let application_name = format!("mcg3-conflict-{}", Uuid::new_v4().simple());
    let options = PgConnectOptions::from_str(&test_database_url)
        .expect("TEST_DATABASE_URL must be a valid PostgreSQL URL")
        .application_name(&application_name)
        .disable_statement_logging();
    let conflict_pool = PgPoolOptions::new()
        .max_connections(1)
        .connect_with(options)
        .await
        .expect("conflict repository pool must connect");
    let repository = InboundEventRepository::new(conflict_pool);
    let repository_event = pending_event.clone();
    let request = tokio::spawn(async move { repository.insert_or_get(&repository_event).await });

    tokio::time::timeout(Duration::from_secs(2), async {
        loop {
            let waiting_on_lock: bool = sqlx::query_scalar(
                "SELECT EXISTS (\
                     SELECT 1 FROM pg_stat_activity \
                     WHERE application_name = $1 \
                       AND wait_event_type = 'Lock' \
                       AND wait_event = 'transactionid'\
                 )",
            )
            .bind(&application_name)
            .fetch_one(pool)
            .await
            .expect("conflict wait state must be observable");
            if waiting_on_lock {
                break;
            }
            tokio::task::yield_now().await;
        }
    })
    .await
    .expect("repository must block on the uncommitted conflicting row");

    transaction
        .commit()
        .await
        .expect("conflict fixture transaction must commit");
    let outcome = tokio::time::timeout(Duration::from_secs(2), request)
        .await
        .expect("repository must finish after the conflicting commit")
        .expect("conflict repository task must not panic")
        .expect("conflict retry must succeed");
    assert_eq!(
        outcome,
        InsertOutcome::Duplicate {
            event_id: pending_event.event_id
        }
    );
}

async fn assert_schema_and_data_minimization(pool: &sqlx::PgPool) {
    let columns = sqlx::query(
        "SELECT column_name, udt_name, is_nullable \
         FROM information_schema.columns \
         WHERE table_schema = current_schema() AND table_name = 'canonical_inbound_events'",
    )
    .fetch_all(pool)
    .await
    .expect("canonical schema metadata must be readable");

    let actual = columns
        .into_iter()
        .map(|row| {
            (
                row.get::<String, _>("column_name"),
                (
                    row.get::<String, _>("udt_name"),
                    row.get::<String, _>("is_nullable"),
                ),
            )
        })
        .collect::<BTreeMap<_, _>>();

    let expected = BTreeMap::from([
        ("account_external_id", ("text", "NO")),
        ("channel", ("text", "NO")),
        ("content_text", ("text", "NO")),
        ("created_at", ("timestamptz", "NO")),
        ("direction", ("text", "NO")),
        ("event_id", ("uuid", "NO")),
        ("external_message_id", ("text", "NO")),
        ("message_type", ("text", "NO")),
        ("occurred_at", ("timestamptz", "NO")),
        ("payload_sha256", ("text", "NO")),
        ("processing_status", ("text", "NO")),
        ("received_at", ("timestamptz", "NO")),
        ("recipient_external_id", ("text", "NO")),
        ("retention_expires_at", ("timestamptz", "NO")),
        ("schema_version", ("text", "NO")),
        ("sender_external_id", ("text", "NO")),
    ]);
    let actual = actual
        .iter()
        .map(|(name, (data_type, nullable))| {
            (name.as_str(), (data_type.as_str(), nullable.as_str()))
        })
        .collect::<BTreeMap<_, _>>();
    assert_eq!(actual, expected);
    assert!(!actual.contains_key("raw_body"));
    assert!(!actual.contains_key("provider_metadata"));

    let unique_constraint: String = sqlx::query_scalar(
        "SELECT pg_get_constraintdef(oid) \
         FROM pg_constraint \
         WHERE conrelid = 'canonical_inbound_events'::regclass AND contype = 'u'",
    )
    .fetch_one(pool)
    .await
    .expect("canonical unique constraint must exist");
    assert_eq!(
        unique_constraint,
        "UNIQUE (channel, account_external_id, external_message_id)"
    );
}

async fn assert_missing_schema_is_normalized(event: &CanonicalInboundEventV1) {
    let test_database_url = std::env::var("TEST_DATABASE_URL")
        .expect("TEST_DATABASE_URL must remain available for error normalization tests");
    let pool = PgPoolOptions::new()
        .max_connections(1)
        .after_connect(|connection, _| {
            Box::pin(async move {
                connection.execute("SET search_path TO pg_catalog").await?;
                Ok(())
            })
        })
        .connect(&test_database_url)
        .await
        .expect("missing-schema test pool must connect");

    let error = InboundEventRepository::new(pool)
        .insert_or_get(event)
        .await
        .expect_err("missing canonical schema must fail");
    assert_eq!(error, InboundRepositoryError::SchemaMissing);
}

async fn assert_missing_database_is_normalized(event: &CanonicalInboundEventV1) {
    let test_database_url = std::env::var("TEST_DATABASE_URL")
        .expect("TEST_DATABASE_URL must remain available for error normalization tests");
    let missing_database = format!("mastermind_missing_{}", Uuid::new_v4().simple());
    let options = PgConnectOptions::from_str(&test_database_url)
        .expect("TEST_DATABASE_URL must be a valid PostgreSQL URL")
        .database(&missing_database)
        .disable_statement_logging();
    let pool = PgPoolOptions::new()
        .max_connections(1)
        .acquire_timeout(Duration::from_secs(2))
        .connect_lazy_with(options);

    let error = InboundEventRepository::new(pool)
        .insert_or_get(event)
        .await
        .expect_err("missing PostgreSQL database must fail");
    assert_eq!(error, InboundRepositoryError::Unavailable);
}

fn canonical_event() -> CanonicalInboundEventV1 {
    serde_json::from_str(include_str!(
        "../../docs/contracts/messaging/fixtures/canonical-inbound-event-v1.valid.json"
    ))
    .expect("shared valid canonical fixture must deserialize")
}
