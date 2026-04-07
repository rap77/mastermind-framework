-- Partition activity_log by month for efficient time-series queries
-- This replaces BRIN indexes which are optimal only for > 1M rows

-- First, convert existing activity_log to a partitioned table
CREATE TABLE activity_log_partitioned (
    id UUID NOT NULL,
    brain_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (id, created_at)
) PARTITION BY RANGE (created_at);

-- Create partitions for current and next month
CREATE TABLE activity_log_2026_04 PARTITION OF activity_log_partitioned
    FOR VALUES FROM ('2026-04-01') TO ('2026-05-01');

CREATE TABLE activity_log_2026_05 PARTITION OF activity_log_partitioned
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

-- Migrate existing data to partitioned table
INSERT INTO activity_log_partitioned SELECT * FROM activity_log;

-- Drop old table and rename
DROP TABLE activity_log;
ALTER TABLE activity_log_partitioned RENAME TO activity_log;

-- Create indexes on partitioned table
CREATE INDEX idx_activity_log_brain_id ON activity_log (brain_id);
CREATE INDEX idx_activity_log_event_type ON activity_log (event_type);

-- Composite indexes for common query patterns
-- Query by brain_id + time range (most common)
CREATE INDEX idx_activity_log_brain_id_created_at
    ON activity_log (brain_id, created_at DESC);

-- Query by event_type + time range (analytics)
CREATE INDEX idx_activity_log_event_type_created_at
    ON activity_log (event_type, created_at DESC);

-- Query by brain_id + event_type (specific brain events)
CREATE INDEX idx_activity_log_brain_id_event_type
    ON activity_log (brain_id, event_type);

-- Partial indexes for specific event types
-- Fast query for failed brains (error tracking)
CREATE INDEX idx_activity_log_failed
    ON activity_log (brain_id, created_at DESC)
    WHERE event_type = 'brain_failed';

-- Fast query for completed brains (performance metrics)
CREATE INDEX idx_activity_log_completed
    ON activity_log (brain_id, created_at DESC)
    WHERE event_type = 'brain_completed';

-- Analyze table for query planner
ANALYZE activity_log;
