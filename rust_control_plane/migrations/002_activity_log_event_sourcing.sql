-- Activity Log Table for Event Sourcing (RCP-03)
-- This table stores all brain events for temporal queries and replay

CREATE TABLE IF NOT EXISTS activity_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    brain_id TEXT NOT NULL,
    event_type TEXT NOT NULL, -- 'brain_started', 'brain_completed', 'brain_routed', 'brain_failed'
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for temporal queries (RCP-03 requirement: P95 < 100ms @ 10K events)
CREATE INDEX IF NOT EXISTS idx_activity_log_brain_id ON activity_log(brain_id);
CREATE INDEX IF NOT EXISTS idx_activity_log_created_at ON activity_log(created_at);
CREATE INDEX IF NOT EXISTS idx_activity_log_event_type ON activity_log(event_type);

-- Composite index for brain-specific temporal queries
CREATE INDEX IF NOT EXISTS idx_activity_log_brain_created ON activity_log(brain_id, created_at DESC);
