-- Central Agent Registry — MM-Flow
-- Run once after mm-flow-audit.sql
-- IDEMPOTENT: safe to run multiple times (ON CONFLICT DO NOTHING)

CREATE TABLE IF NOT EXISTS agent_registry (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  project_id UUID NOT NULL REFERENCES projects(id),
  brain_id INTEGER NOT NULL,
  name VARCHAR NOT NULL,
  role VARCHAR NOT NULL,
  capabilities TEXT[],
  model_quality VARCHAR DEFAULT 'balanced',
  model_budget VARCHAR DEFAULT 'haiku',
  applies_in TEXT[],
  is_barrier BOOLEAN DEFAULT FALSE,
  token_budget_per_phase INTEGER DEFAULT 10000,
  tokens_consumed_total INTEGER DEFAULT 0,
  status VARCHAR DEFAULT 'available',
  last_heartbeat TIMESTAMP,
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(organization_id, project_id, brain_id)
);

-- Seed 7 dev brains for (RAP-software, mastermind)
-- Pre-check: verify slugs exist before inserting
DO $$
DECLARE
  v_org_id UUID;
  v_proj_id UUID;
BEGIN
  SELECT id INTO v_org_id FROM organizations WHERE slug = 'RAP-software';
  SELECT id INTO v_proj_id FROM projects WHERE slug = 'mastermind';

  IF v_org_id IS NULL THEN
    RAISE EXCEPTION 'Organization slug RAP-software not found in organizations table';
  END IF;
  IF v_proj_id IS NULL THEN
    RAISE EXCEPTION 'Project slug mastermind not found in projects table';
  END IF;

  INSERT INTO agent_registry (organization_id, project_id, brain_id, name, role, capabilities, model_quality, applies_in, is_barrier) VALUES
    (v_org_id, v_proj_id, 1, 'Brain #1 Product Strategy', 'product_strategy',
     ARRAY['vision','prioritization','roadmap'], 'quality', ARRAY['DISCUSSION'], FALSE),
    (v_org_id, v_proj_id, 2, 'Brain #2 UX Research', 'ux_research',
     ARRAY['user_flows','wireframes','usability'], 'balanced', ARRAY['DISCUSSION'], FALSE),
    (v_org_id, v_proj_id, 3, 'Brain #3 UI Design', 'ui_design',
     ARRAY['components','tokens','visual_design'], 'balanced', ARRAY['DISCUSSION'], FALSE),
    (v_org_id, v_proj_id, 4, 'Brain #4 Frontend', 'frontend',
     ARRAY['react','typescript','state_management'], 'balanced', ARRAY['PLANNING'], FALSE),
    (v_org_id, v_proj_id, 5, 'Brain #5 Backend', 'backend',
     ARRAY['api_design','database','architecture'], 'balanced', ARRAY['PLANNING'], FALSE),
    (v_org_id, v_proj_id, 6, 'Brain #6 QA DevOps', 'qa_devops',
     ARRAY['testing','ci_cd','reliability'], 'balanced', ARRAY['PLANNING'], FALSE),
    (v_org_id, v_proj_id, 7, 'Brain #7 Growth Evaluator', 'meta_evaluator',
     ARRAY['synthesis','critique','risk_assessment'], 'quality',
     ARRAY['DISCUSSION','PLANNING','VERIFICATION'], TRUE)
  ON CONFLICT DO NOTHING;
END $$;
