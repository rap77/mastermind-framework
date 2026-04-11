-- Migration: Add messages table for multi-channel webhook processing
-- Phase 18 - Plan 18-01: Multi-channel Gateway
-- This table stores incoming webhooks from WhatsApp, Instagram, and Email

-- Create messages table with idempotency via UNIQUE constraint
CREATE TABLE IF NOT EXISTS messages (
    -- Primary key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- External message identifier (from provider)
    -- WhatsApp: entry[0].changes[0].value.messages[0].id
    -- Instagram: changes[0].value.id
    -- Email: Message-ID header
    external_message_id TEXT NOT NULL,

    -- Channel source: 'whatsapp', 'instagram', 'email'
    channel TEXT NOT NULL CHECK (channel IN ('whatsapp', 'instagram', 'email')),

    -- Raw webhook payload (JSONB for efficient querying)
    payload JSONB NOT NULL,

    -- Processing status: pending, processing, completed, failed
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed')),

    -- Error message (if status = 'failed')
    error_message TEXT,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Idempotency: prevent duplicate processing of same webhook
    CONSTRAINT messages_external_channel_unique UNIQUE (external_message_id, channel)
);

-- Create index for fast duplicate detection (used by is_duplicate query)
CREATE INDEX IF NOT EXISTS idx_messages_external_channel
    ON messages(external_message_id, channel);

-- Create index for status-based queries (used by worker)
CREATE INDEX IF NOT EXISTS idx_messages_status
    ON messages(status) WHERE status IN ('pending', 'processing');

-- Create index for time-based queries (cleanup, monitoring)
CREATE INDEX IF NOT EXISTS idx_messages_created_at
    ON messages(created_at DESC);

-- Add trigger to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_messages_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_messages_updated_at
    BEFORE UPDATE ON messages
    FOR EACH ROW
    EXECUTE FUNCTION update_messages_updated_at();

-- Add comment for documentation
COMMENT ON TABLE messages IS 'Stores incoming webhooks from WhatsApp, Instagram, and Email with idempotency protection';
COMMENT ON CONSTRAINT messages_external_channel_unique ON messages IS 'Prevents duplicate processing of same webhook from same channel';
COMMENT ON INDEX idx_messages_external_channel IS 'Fast lookup for duplicate detection (O(log n) via B-tree)';
COMMENT ON INDEX idx_messages_status IS 'Worker queue: pending/processing messages only';
COMMENT ON INDEX idx_messages_created_at IS 'Time-based queries: monitoring, cleanup, SLI tracking';
