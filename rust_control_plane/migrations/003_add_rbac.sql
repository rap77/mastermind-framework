-- RBAC Schema Migration (RCP-02)
-- Adds role field to users table for authorization
-- Simplified from 3 roles to 2 (org_admin removed - no permissions defined yet)

-- Add role column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'user';

-- Add constraint to ensure only valid roles
-- Note: IF NOT EXISTS not supported for constraints in PostgreSQL
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conname = 'valid_role') THEN
        ALTER TABLE users ADD CONSTRAINT valid_role CHECK (role IN ('admin', 'user'));
    END IF;
END $$;

-- Seed admin user for initial deployment
-- Password: 'admin123' (change immediately after first login)
-- This is a bcrypt hash with 12 rounds
INSERT INTO users (id, username, password_hash, role, created_at)
VALUES (
    gen_random_uuid(),
    'admin',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5NU7xlZjW9K0i',
    'admin',
    NOW()
)
ON CONFLICT (username) DO NOTHING;  -- Skip if admin user already exists
