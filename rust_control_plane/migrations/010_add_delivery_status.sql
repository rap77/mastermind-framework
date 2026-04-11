-- Add delivery status tracking for sent messages
-- Phase 18, Plan 18-09, Task 4

CREATE TABLE IF NOT EXISTS message_delivery_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('sent', 'delivered', 'read', 'failed')),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_message TEXT,
    provider_message_id TEXT,  -- External API message ID (e.g., WhatsApp message ID)
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),

    -- Indexes for common queries
    INDEX idx_message_delivery_status_message_id (message_id),
    INDEX idx_message_delivery_status_status (status),
    INDEX idx_message_delivery_status_timestamp (timestamp),
    INDEX idx_message_delivery_status_provider_message_id (provider_message_id)
);

COMMENT ON TABLE message_delivery_status IS 'Tracks delivery status for sent messages (sent/delivered/read)';
COMMENT ON COLUMN message_delivery_status.message_id IS 'Reference to the original message in messages table';
COMMENT ON COLUMN message_delivery_status.status IS 'Delivery status: sent, delivered, read, or failed';
COMMENT ON COLUMN message_delivery_status.provider_message_id IS 'External API message ID for tracking delivery receipts';
COMMENT ON COLUMN message_delivery_status.error_message IS 'Error details if status = failed';

-- Grant permissions (adjust as needed for your setup)
-- GRANT SELECT, INSERT, UPDATE ON message_delivery_status TO your_app_user;
-- GRANT USAGE, SELECT ON SEQUENCE message_delivery_status_id_seq TO your_app_user;
