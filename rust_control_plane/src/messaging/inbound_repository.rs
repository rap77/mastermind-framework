use sqlx::{FromRow, PgPool};
use thiserror::Error;
use uuid::Uuid;

use super::canonical_event::CanonicalInboundEventV1;

const INSERT_OR_GET: &str = r#"
WITH inserted AS (
    INSERT INTO canonical_inbound_events (
        event_id,
        schema_version,
        channel,
        account_external_id,
        external_message_id,
        direction,
        sender_external_id,
        recipient_external_id,
        message_type,
        content_text,
        occurred_at,
        received_at,
        payload_sha256,
        processing_status,
        retention_expires_at
    )
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
    ON CONFLICT (channel, account_external_id, external_message_id) DO NOTHING
    RETURNING event_id, TRUE AS inserted
)
SELECT event_id, inserted FROM inserted
UNION ALL
SELECT event_id, FALSE AS inserted
FROM canonical_inbound_events
WHERE channel = $3
  AND account_external_id = $4
  AND external_message_id = $5
  AND NOT EXISTS (SELECT 1 FROM inserted)
LIMIT 1
"#;

#[derive(Clone)]
pub struct InboundEventRepository {
    pool: PgPool,
}

#[derive(Clone, Copy, Debug, Eq, PartialEq)]
pub enum InsertOutcome {
    Inserted { event_id: Uuid },
    Duplicate { event_id: Uuid },
}

#[derive(Clone, Copy, Debug, Eq, Error, PartialEq)]
pub enum InboundRepositoryError {
    #[error("canonical persistence is unavailable")]
    Unavailable,
    #[error("canonical persistence schema is missing")]
    SchemaMissing,
    #[error("canonical persistence failed")]
    Database,
}

#[derive(FromRow)]
struct StoredOutcome {
    event_id: Uuid,
    inserted: bool,
}

impl InboundEventRepository {
    pub fn new(pool: PgPool) -> Self {
        Self { pool }
    }

    pub async fn insert_or_get(
        &self,
        event: &CanonicalInboundEventV1,
    ) -> Result<InsertOutcome, InboundRepositoryError> {
        // A conflicting uncommitted insert can be invisible to the statement snapshot.
        // Retrying the same atomic statement observes it after the conflict wait completes.
        for attempt in 0..2 {
            let result = sqlx::query_as::<_, StoredOutcome>(INSERT_OR_GET)
                .bind(event.event_id)
                .bind("messaging.inbound.v1")
                .bind("whatsapp")
                .bind(&event.account_external_id)
                .bind(&event.external_message_id)
                .bind("inbound")
                .bind(&event.sender_external_id)
                .bind(&event.recipient_external_id)
                .bind("text")
                .bind(&event.content_text)
                .bind(event.occurred_at)
                .bind(event.received_at)
                .bind(&event.payload_sha256)
                .bind("accepted")
                .bind(event.retention_expires_at)
                .fetch_one(&self.pool)
                .await;

            match result {
                Ok(stored) if stored.inserted => {
                    return Ok(InsertOutcome::Inserted {
                        event_id: stored.event_id,
                    });
                }
                Ok(stored) => {
                    return Ok(InsertOutcome::Duplicate {
                        event_id: stored.event_id,
                    });
                }
                Err(sqlx::Error::RowNotFound) if attempt == 0 => continue,
                Err(error) => return Err(normalize_error(error)),
            }
        }

        Err(InboundRepositoryError::Database)
    }
}

fn normalize_error(error: sqlx::Error) -> InboundRepositoryError {
    match error {
        sqlx::Error::PoolTimedOut
        | sqlx::Error::PoolClosed
        | sqlx::Error::WorkerCrashed
        | sqlx::Error::Io(_)
        | sqlx::Error::Tls(_) => InboundRepositoryError::Unavailable,
        sqlx::Error::Database(database_error) => {
            let code = database_error.code();
            match code.as_deref() {
                Some("42P01" | "3F000") => InboundRepositoryError::SchemaMissing,
                Some("3D000" | "57P01" | "57P02" | "57P03") => InboundRepositoryError::Unavailable,
                Some(code) if code.starts_with("08") => InboundRepositoryError::Unavailable,
                _ => InboundRepositoryError::Database,
            }
        }
        _ => InboundRepositoryError::Database,
    }
}
