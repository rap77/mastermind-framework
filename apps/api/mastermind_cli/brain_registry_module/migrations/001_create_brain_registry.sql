-- Migration 001: Create brain_registry table
-- Phase C1 - Central Agent Registry

CREATE TABLE IF NOT EXISTS brain_registry (
    brain_id        INTEGER     PRIMARY KEY,              -- 1-7, matches agent numbering
    name            TEXT        NOT NULL,                 -- Human-readable brain name
    model_quality   TEXT        NOT NULL,                 -- Model for quality tier (e.g. claude-opus-4-6)
    model_balanced  TEXT        NOT NULL,                 -- Model for balanced tier (e.g. claude-sonnet-4-6)
    model_budget    TEXT        NOT NULL,                 -- Model for budget tier (e.g. claude-haiku-4-5)
    capabilities    TEXT[]      NOT NULL DEFAULT '{}',    -- Array of capability strings
    trigger_conditions TEXT[]   NOT NULL DEFAULT '{}',    -- Array of trigger condition strings
    enabled         BOOLEAN     NOT NULL DEFAULT TRUE,    -- Whether brain is active
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index for enabled brains (most common query)
CREATE INDEX IF NOT EXISTS idx_brain_registry_enabled
ON brain_registry(enabled)
WHERE enabled = TRUE;

-- Index for capability lookup
CREATE INDEX IF NOT EXISTS idx_brain_registry_capabilities
ON brain_registry USING GIN(capabilities);

-- Index for trigger lookup
CREATE INDEX IF NOT EXISTS idx_brain_registry_trigger_conditions
ON brain_registry USING GIN(trigger_conditions);
