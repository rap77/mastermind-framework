CREATE TABLE canonical_inbound_events (
    event_id UUID PRIMARY KEY,
    schema_version TEXT NOT NULL CHECK (schema_version = 'messaging.inbound.v1'),
    channel TEXT NOT NULL CHECK (channel = 'whatsapp'),
    account_external_id TEXT NOT NULL CHECK (account_external_id <> ''),
    external_message_id TEXT NOT NULL CHECK (external_message_id <> ''),
    direction TEXT NOT NULL CHECK (direction = 'inbound'),
    sender_external_id TEXT NOT NULL CHECK (sender_external_id <> ''),
    recipient_external_id TEXT NOT NULL CHECK (recipient_external_id <> ''),
    message_type TEXT NOT NULL CHECK (message_type = 'text'),
    content_text TEXT NOT NULL CHECK (char_length(content_text) BETWEEN 1 AND 4096),
    occurred_at TIMESTAMPTZ NOT NULL,
    received_at TIMESTAMPTZ NOT NULL,
    payload_sha256 TEXT NOT NULL CHECK (payload_sha256 ~ '^[0-9a-f]{64}$'),
    processing_status TEXT NOT NULL CHECK (processing_status = 'accepted'),
    retention_expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (channel, account_external_id, external_message_id)
);
