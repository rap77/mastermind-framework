-- Function to refresh cost_metrics_mv concurrently
CREATE OR REPLACE FUNCTION refresh_cost_metrics_mv()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY cost_metrics_mv;
END;
$$ LANGUAGE plpgsql;

-- Grant execute to application user
GRANT EXECUTE ON FUNCTION refresh_cost_metrics_mv() TO postgres;

COMMENT ON FUNCTION refresh_cost_metrics_mv() IS
    'Refresh cost metrics materialized view without blocking reads.
     Should be called every 5 minutes via cron or tokio::spawn_blocking.';
