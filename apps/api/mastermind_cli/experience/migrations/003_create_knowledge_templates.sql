-- Create knowledge_templates table (separate from experience_records)
-- Per Screaming Architecture: templates are domain concepts, logs are infrastructure

CREATE TABLE IF NOT EXISTS knowledge_templates (
    id TEXT PRIMARY KEY,  -- UUID
    brain_id TEXT NOT NULL,  -- Which brain created this template
    template_name TEXT NOT NULL,  -- Human-readable name
    template_data TEXT NOT NULL,  -- JSON: {brief_pattern, response_pattern, metadata}
    success_rate REAL DEFAULT 1.0,  -- 0.0 to 1.0 (how often this template succeeds)
    usage_count INTEGER DEFAULT 0,  -- How many times this template was used
    created_at TEXT NOT NULL,  -- ISO timestamp
    last_used_at TEXT,  -- ISO timestamp (null if never used)

    -- Foreign key reference (soft - brain_agents table doesn't exist yet)
    -- brain_id REFERENCES brain_agents(brain_id) ON DELETE CASCADE
);

-- Index for brain-specific template retrieval
CREATE INDEX IF NOT EXISTS idx_knowledge_templates_brain_id
ON knowledge_templates(brain_id);

-- Index for success rate ranking (best templates first)
CREATE INDEX IF NOT EXISTS idx_knowledge_templates_success_rate
ON knowledge_templates(success_rate DESC);

-- Index for last-used tracking
CREATE INDEX IF NOT EXISTS idx_knowledge_templates_last_used_at
ON knowledge_templates(last_used_at DESC);
