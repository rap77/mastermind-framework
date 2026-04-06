-- Migration 002: Add expires_at column for TTL ceiling
-- Phase 14 - Knowledge Distillation (Plan 14-01)

-- Add expires_at column for TTL ceiling
ALTER TABLE experience_records ADD COLUMN expires_at TEXT;

-- Create index for performance
CREATE INDEX IF NOT EXISTS idx_experience_records_expires_at
ON experience_records(expires_at);

-- Set default TTL: 90 days from now for existing records
UPDATE experience_records
SET expires_at = datetime(timestamp, '+90 days')
WHERE expires_at IS NULL;
