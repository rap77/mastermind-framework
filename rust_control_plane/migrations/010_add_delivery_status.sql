-- Add delivery status tracking for sent messages
-- Tracks sent/delivered/read/failed status separate from processing status

CREATE TABLE IF NOT EXISTS message_delivery_status (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    status TEXT NOT NULL CHECK (status IN ('sent', 'delivered', 'read', 'failed')),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    error_message TEXT,
    provider_message_id TEXT,
    CONSTRAINT unique_delivery_status UNIQUE(message_id, status, timestamp)
);

-- Create indices for efficient querying
CREATE INDEX IF NOT EXISTS idx_message_delivery_status_message_id
    ON message_delivery_status(message_id);

CREATE INDEX IF NOT EXISTS idx_message_delivery_status_status
    ON message_delivery_status(status);

CREATE INDEX IF NOT EXISTS idx_message_delivery_status_timestamp
    ON message_delivery_status(timestamp DESC);

-- Add comment documenting the table
COMMENT ON TABLE message_delivery_status IS 'Tracks delivery status for sent messages (sent/delivered/read/failed), separate from processing status (pending/processing/completed/failed)';

COMMENT ON COLUMN message_delivery_status.message_id IS 'Foreign key to messages table';

COMMENT ON COLUMN message_delivery_status.status IS 'Delivery status: sent (accepted by provider), delivered (reached recipient), read (recipient saw it), failed (delivery failed)';

COMMENT ON COLUMN message_delivery_status.provider_message_id IS 'External message ID from provider API (WhatsApp, Instagram, etc)';

COMMENT ON COLUMN message_delivery_status.error_message IS 'Error details if status=failed';
