-- Hybrid table: relational core + JSONB for provider-specific fields
-- Required by: token-cost-quality-telemetry objective
CREATE TABLE token_usage_events (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id            TEXT        NOT NULL,
    session_id          UUID,
    model               TEXT        NOT NULL,
    input_tokens        INTEGER     NOT NULL DEFAULT 0,
    output_tokens       INTEGER     NOT NULL DEFAULT 0,
    cache_read_tokens   INTEGER     NOT NULL DEFAULT 0,
    cache_write_tokens  INTEGER     NOT NULL DEFAULT 0,
    provider_metadata   JSONB       NOT NULL DEFAULT '{}'::jsonb,
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_token_usage_brain_id   ON token_usage_events (brain_id);
CREATE INDEX idx_token_usage_session_id ON token_usage_events (session_id);
CREATE INDEX idx_token_usage_model      ON token_usage_events (model);
CREATE INDEX idx_token_usage_created_at ON token_usage_events (created_at);
