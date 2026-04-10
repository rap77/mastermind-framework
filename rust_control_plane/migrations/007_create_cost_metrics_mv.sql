-- Materialized view: Cost metrics aggregation per brain
-- Refresh strategy: Concurrent refresh every 5 minutes
-- Performance target: P50 < 10ms, P99 < 50ms

DROP MATERIALIZED VIEW IF EXISTS cost_metrics_mv CASCADE;

CREATE MATERIALIZED VIEW cost_metrics_mv AS
SELECT
    brain_id,
    COUNT(*) as total_requests,
    SUM(CASE WHEN event_type = 'brain_completed' THEN 1 ELSE 0 END) as completed_requests,
    SUM(CASE WHEN event_type = 'brain_failed' THEN 1 ELSE 0 END) as failed_requests,
    MAX(created_at) as last_activity_at,
    CASE
        WHEN COUNT(*) > 0 THEN (SUM(CASE WHEN event_type = 'brain_completed' THEN 1 ELSE 0 END)::float / COUNT(*)::float)
        ELSE 0
    END as success_rate
FROM activity_log
GROUP BY brain_id
WITH DATA;

-- Create unique index for concurrent refresh
CREATE UNIQUE INDEX cost_metrics_mv_brain_id_idx
    ON cost_metrics_mv (brain_id);

-- Create indexes for common queries
CREATE INDEX cost_metrics_mv_last_activity_idx
    ON cost_metrics_mv (last_activity_at DESC);

-- Create index for success rate sorting
CREATE INDEX cost_metrics_mv_success_rate_idx
    ON cost_metrics_mv (success_rate DESC);

COMMENT ON MATERIALIZED VIEW cost_metrics_mv IS
    'Aggregated cost metrics per brain, refreshed every 5 minutes.
     success_rate = completed_requests / total_requests';
