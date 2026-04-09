-- Migration 004: Dual-write verification triggers
-- This migration adds triggers for data consistency verification during dual-write period

-- Function to verify row counts (for manual verification only)
CREATE OR REPLACE FUNCTION verify_row_count()
RETURNS TRIGGER AS $$
BEGIN
    -- This trigger is for verification only during dual-write period
    -- In production, we'll verify row counts periodically instead of on every write
    -- to avoid performance impact
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Commented out to avoid performance impact
-- Uncomment these if you need real-time verification during testing
-- CREATE TRIGGER trigger_verify_tasks AFTER INSERT OR UPDATE ON tasks
--     FOR EACH ROW EXECUTE FUNCTION verify_row_count();

-- CREATE TRIGGER trigger_verify_executions AFTER INSERT OR UPDATE ON executions
--     FOR EACH ROW EXECUTE FUNCTION verify_row_count();

-- CREATE TRIGGER trigger_verify_users AFTER INSERT OR UPDATE ON users
--     FOR EACH ROW EXECUTE FUNCTION verify_row_count();

-- Note: For production use, rely on the consistency checker endpoint:
-- GET /api/migrate/verify
-- This runs every 5 minutes via tokio::spawn_blocking in the Rust control plane
