-- Prevent updates and deletes on activity_log (immutable event log)
CREATE OR REPLACE FUNCTION prevent_activity_log_mutation()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION 'Cannot modify activity_log table (immutable event log)';
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_prevent_update
    BEFORE UPDATE ON activity_log
    FOR EACH ROW EXECUTE FUNCTION prevent_activity_log_mutation();

CREATE TRIGGER trigger_prevent_delete
    BEFORE DELETE ON activity_log
    FOR EACH ROW EXECUTE FUNCTION prevent_activity_log_mutation();

-- Add comment documenting immutability
COMMENT ON TABLE activity_log IS 'Immutable event log - append only, no updates or deletes allowed';
