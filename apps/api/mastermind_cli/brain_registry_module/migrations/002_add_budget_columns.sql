-- Migration 002: Add budget tracking columns to brain_registry

ALTER TABLE brain_registry
    ADD COLUMN IF NOT EXISTS token_budget_per_phase INTEGER NOT NULL DEFAULT 10000,
    ADD COLUMN IF NOT EXISTS tokens_consumed_total INTEGER NOT NULL DEFAULT 0;
