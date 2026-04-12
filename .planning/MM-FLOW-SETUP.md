# MM-Flow Setup Guide

**Status:** READY FOR IMPLEMENTATION (Apr 15, 2026)

---

## Prerequisites

### 1. Docker PostgreSQL (✅ Already Running)

```bash
$ docker ps | grep postgres
16be6f51a50d mastermind-postgres-1 (pgvector:pg16) [5433:5432]
```

**Connection details:**
- Host: `localhost`
- Port: `5433` (forwarded from 5432 in container)
- Database: `mastermind_bd`
- User: `postgres`
- Password: `devpassword`

**Test connection:**
```bash
psql -h localhost -p 5433 -U postgres -d mastermind_bd -c "SELECT version();"
```

### 2. API Keys (✅ Already Configured)

**Location:** `~/.claude/zai.sh` + `settings.local.json`

**Required env vars:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."          # Claude API key
export OPENROUTER_API_KEY="sk-or-..."          # OpenRouter key
export ZAI_API_KEY="zai-..."                    # z.ai key
```

**Load credentials:**
```bash
# Create ~/.claude/backends.sh
source ~/.claude/backends.sh && export_claude_credentials
source ~/.claude/backends.sh && export_openrouter_credentials
source ~/.claude/backends.sh && export_zai_credentials
```

---

## Phase A: Implementation Checklist

### Day 1: PostgreSQL Schema (Apr 15)

**1. Create tables in PostgreSQL**

```bash
cd /home/rpadron/proy/mastermind

# Connect to PostgreSQL
psql -h localhost -p 5433 -U postgres -d mastermind_bd

# Run schema creation (create file: docker/postgres/mm-flow-schema.sql)
\i docker/postgres/mm-flow-schema.sql

# Verify tables created
\dt
```

**2. Schema file content** (`docker/postgres/mm-flow-schema.sql`):

```sql
-- Organizations
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name VARCHAR NOT NULL,
  slug VARCHAR UNIQUE NOT NULL,
  environment VARCHAR DEFAULT 'local',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Projects
CREATE TABLE projects (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  name VARCHAR NOT NULL,
  slug VARCHAR NOT NULL,
  type VARCHAR DEFAULT 'software',
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(organization_id, slug)
);

-- Workspaces
CREATE TABLE workspaces (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  project_id UUID NOT NULL REFERENCES projects(id),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  name VARCHAR NOT NULL,
  branch VARCHAR DEFAULT 'master',
  created_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(project_id, branch)
);

-- MM-Flow State
CREATE TABLE mm_flow_state (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  project_id UUID NOT NULL,
  workspace_id UUID NOT NULL,
  phase INTEGER NOT NULL,
  status VARCHAR NOT NULL,
  state_data JSONB NOT NULL,
  brain_outputs_embedding vector(1536),
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
  INDEX idx_org_project_phase (organization_id, project_id, phase)
);

-- Backend Sessions
CREATE TABLE backend_sessions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  project_id UUID NOT NULL,
  workspace_id UUID NOT NULL,
  backend VARCHAR NOT NULL,
  tokens_used INTEGER DEFAULT 0,
  tokens_limit INTEGER NOT NULL,
  phase INTEGER,
  wave INTEGER,
  session_started TIMESTAMP DEFAULT NOW(),
  session_ended TIMESTAMP,
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
  INDEX idx_org_project_backend (organization_id, project_id, backend)
);

-- Backend Capabilities (discovered limits)
CREATE TABLE backend_capabilities (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  backend VARCHAR NOT NULL,
  organization_id UUID,
  token_limit INTEGER,
  tokens_per_minute INTEGER,
  requests_per_day INTEGER,
  reset_cycle_hours FLOAT,
  reset_times_per_day INTEGER,
  discovered_at TIMESTAMP DEFAULT NOW(),
  last_verified TIMESTAMP,
  notes TEXT,
  UNIQUE(backend, organization_id)
);

-- Context Checkpoints
CREATE TABLE context_checkpoints (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  project_id UUID NOT NULL,
  workspace_id UUID NOT NULL,
  phase INTEGER NOT NULL,
  state JSONB NOT NULL,
  conversation_history TEXT NOT NULL,
  checkpoint_reason VARCHAR,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
  INDEX idx_org_project_phase_ts (organization_id, project_id, phase, created_at DESC)
);

-- Brain Consultations
CREATE TABLE brain_consultations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  project_id UUID NOT NULL,
  workspace_id UUID NOT NULL,
  phase INTEGER NOT NULL,
  brain_id INTEGER NOT NULL,
  consultation_input TEXT NOT NULL,
  consultation_output TEXT NOT NULL,
  output_embedding vector(1536),
  confidence FLOAT,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id),
  INDEX idx_org_project_brain (organization_id, project_id, brain_id)
);

-- Cross-Phase Contracts
CREATE TABLE cross_phase_contracts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL,
  project_id UUID NOT NULL,
  workspace_id UUID NOT NULL,
  from_phase INTEGER NOT NULL,
  to_phase INTEGER NOT NULL,
  contract_text TEXT NOT NULL,
  contract_embedding vector(1536),
  validated BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW(),
  FOREIGN KEY (organization_id) REFERENCES organizations(id),
  FOREIGN KEY (project_id) REFERENCES projects(id),
  FOREIGN KEY (workspace_id) REFERENCES workspaces(id)
);

-- Row-Level Security (RLS)
ALTER TABLE mm_flow_state ENABLE ROW LEVEL SECURITY;
ALTER TABLE backend_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE context_checkpoints ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY select_own_org ON mm_flow_state
  FOR SELECT USING (organization_id = current_setting('mm_flow.org_id')::uuid);
```

**3. Seed initial organizations**

```bash
psql -h localhost -p 5433 -U postgres -d mastermind_bd

INSERT INTO organizations (name, slug, environment) VALUES
  ('Acme Corp', 'acme-corp', 'local'),
  ('Prosell SaaS', 'prosell-sass', 'local');

INSERT INTO projects (organization_id, name, slug, type) VALUES
  (
    (SELECT id FROM organizations WHERE slug = 'acme-corp'),
    'MasterMind Framework',
    'mastermind',
    'software'
  ),
  (
    (SELECT id FROM organizations WHERE slug = 'prosell-sass'),
    'Paperclip Clone v3.0',
    'paperclip-v3',
    'software'
  );

INSERT INTO workspaces (project_id, organization_id, name, branch) VALUES
  (
    (SELECT id FROM projects WHERE slug = 'mastermind'),
    (SELECT id FROM organizations WHERE slug = 'acme-corp'),
    'Master Workspace',
    'master'
  ),
  (
    (SELECT id FROM projects WHERE slug = 'paperclip-v3'),
    (SELECT id FROM organizations WHERE slug = 'prosell-sass'),
    'Master Workspace',
    'master'
  );

-- Verify
SELECT * FROM organizations;
SELECT * FROM projects;
SELECT * FROM workspaces;
```

### Day 2-3: MM-Flow Python Modules

**Create directory structure:**
```bash
mkdir -p .planning/.mm-flow/
touch .planning/.mm-flow/__init__.py
touch .planning/.mm-flow/multi_backend_manager.py
touch .planning/.mm-flow/backend_scheduler.py
touch .planning/.mm-flow/token_limiter.py
touch .planning/.mm-flow/state_machine.py
touch .planning/.mm-flow/brain_router.py
touch .planning/.mm-flow/verification_gates.py
```

**Stub files** (to be filled in during implementation):

```python
# .planning/.mm-flow/multi_backend_manager.py

import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List

class MultiBackendManager:
    """Smart backend selection based on available tokens"""

    BACKENDS = {
        "claude": {"limit": 100_000, "cycles_per_day": 1, "priority": 1},
        "openrouter": {"limit": 128_000, "cycles_per_day": 1, "priority": 2},
        "z_ai": {"limit": 200_000, "cycles_per_day": 5, "priority": 3}
    }

    def __init__(self, org_id: str, project_id: str, db_url: str):
        self.org_id = org_id
        self.project_id = project_id
        self.db = psycopg2.connect(db_url)

    def get_best_available_backend(self) -> Dict:
        """Get backend with MOST available credits RIGHT NOW"""
        # Implementation in Phase A Day 2
        pass

    def switch_backend(self, from_backend: str, to_backend: str) -> Dict:
        """Switch from one backend to another"""
        # Implementation in Phase A Day 2
        pass

    def checkpoint_before_switch(self):
        """Save full context to PostgreSQL before switching"""
        # Implementation in Phase A Day 2
        pass
```

### Day 4: CLI Commands

**Create CLI structure:**
```bash
mkdir -p .planning/.mm-flow/cli/
touch .planning/.mm-flow/cli/__init__.py
touch .planning/.mm-flow/cli/commands.py
touch .planning/.mm-flow/cli/context.py
```

**Stub** (to be filled in):

```python
# .planning/.mm-flow/cli/commands.py

import click
import json
from pathlib import Path

@click.group()
def cli():
    """MM-Flow: Multi-project workflow orchestrator"""
    pass

@cli.command()
@click.option('--org', required=True)
@click.option('--project', required=True)
def init(org, project):
    """Initialize project in MM-Flow"""
    # Create org/project/workspace in PostgreSQL
    # Save context to ~/.mm-flow/.context.json
    click.echo(f"✅ Initialized {org}/{project}")

@cli.command()
@click.option('--phase', required=True, type=int)
def execute_phase(phase):
    """Execute a phase using current context"""
    # Load context from ~/.mm-flow/.context.json
    # Execute phase with MM-Flow pipeline
    click.echo(f"✅ Phase {phase} complete")

if __name__ == '__main__':
    cli()
```

---

## Post-Phase A: Next Steps

### Phase B: Piloting (Apr 22-26)

- Run Phase 18 Wave 3 with MM-Flow
- Test backend switcheo scenarios
- Discover actual token limits
- Verify z.ai reset cycles

### Phase C: Scaling (post v3.0)

- Agentify marketing brains (8-23)
- Prepare Projects 3-4 for Phase 19+
- Test multi-project isolation
- Prepare for multi-user security (future)

---

## Troubleshooting

### PostgreSQL Connection Issues

```bash
# Test connection
psql -h localhost -p 5433 -U postgres -d mastermind_bd -c "SELECT 1;"

# If fails, check Docker:
docker ps | grep postgres
docker logs mastermind-postgres-1
```

### API Key Issues

```bash
# Verify env vars
echo $ANTHROPIC_API_KEY
echo $OPENROUTER_API_KEY
echo $ZAI_API_KEY

# Reload credentials
source ~/.claude/backends.sh && export_claude_credentials
```

### RLS Issues

```bash
# Check RLS policies
SELECT * FROM pg_policies WHERE tablename = 'mm_flow_state';

# Set context for testing
SET mm_flow.org_id = 'uuid-value';
SET mm_flow.project_id = 'uuid-value';
```

---

## Ready to Start?

✅ Docker PostgreSQL running
✅ API keys configured
✅ Schema designed
✅ Roadmap finalized

**Next: Monday, Apr 15 @ 9:00 AM — Phase A Kickoff**
