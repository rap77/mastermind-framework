-- Migration 009: Add Dead Letter Queue table for failed webhooks
-- Implements Brain #7 Condition #6: DLQ Retry Backoff Strategy

-- Create webhook_dlq table for failed webhooks
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

-- Create index for efficient retry queries
-- Used by retry worker: SELECT * FROM webhook_dlq WHERE retry_count < 3 ORDER BY created_at ASC
CREATE INDEX IF NOT EXISTS idx_dlq_retry_count ON webhook_dlq(retry_count, created_at);

-- Add comment for documentation
COMMENT ON TABLE webhook_dlq IS 'Dead Letter Queue for failed webhooks with exponential backoff retry (1s -> 5s -> 30s -> DLQ)';
COMMENT ON COLUMN webhook_dlq.retry_count IS 'Number of retry attempts (max 3 before permanent failure)';
COMMENT ON COLUMN webhook_dlq.last_retry_at IS 'Timestamp of most recent retry attempt';
