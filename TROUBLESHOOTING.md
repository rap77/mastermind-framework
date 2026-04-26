# MasterMind Framework — Troubleshooting Guide

**Solutions to common issues**

---

## Table of Contents

- [Installation Issues](#installation-issues)
- [PostgreSQL Issues](#postgresql-issues)
- [Command Issues](#command-issues)
- [Brain Consultation Issues](#brain-consultation-issues)
- [Performance Issues](#performance-issues)
- [Getting Help](#getting-help)

---

## Installation Issues

### Problem: `psycopg2 not installed — database operations disabled`

**Error Message:**
```
/home/user/project/.claude/commands/mm/db_client.py:57: UserWarning: psycopg2 not installed — database operations disabled
```

**Cause:** Python PostgreSQL adapter not installed

**Solution:**
```bash
# Option 1: Install with pip
pip install psycopg2-binary

# Option 2: Install with uv (recommended)
uv add psycopg2-binary

# Option 3: Install system package
sudo apt-get install python3-psycopg2
```

**Verify:**
```bash
python3 -c "import psycopg2; print(psycopg2.__version__)"
```

---

### Problem: `STATUS: not-installed` after init

**Symptoms:**
```bash
python3 .claude/commands/mm/init-handler.py --check
# Output: STATUS: not-installed
```

**Cause:** Installation didn't complete or files are missing

**Diagnosis:**
```bash
# Check if files exist
ls -la .mastermind/
ls -la .claude/commands/mm/
ls -la .claude/skills/mm/
ls -la .claude/agents/mm/
```

**Solution:**
```bash
# Re-run installation with force flag
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target . --force
```

**If still failing:**
```bash
# Check permissions
ls -la .claude/

# Manually create directories
mkdir -p .claude/commands/mm
mkdir -p .claude/skills/mm
mkdir -p .claude/agents/mm

# Re-run init
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target . --force
```

---

### Problem: `Permission denied` when creating files

**Error Message:**
```
PermissionError: [Errno 13] Permission denied: '.mastermind/config.yaml'
```

**Cause:** Insufficient permissions to create files

**Solution:**
```bash
# Check directory permissions
ls -la .

# Fix permissions
chmod 755 .
chmod u+w .mastermind 2>/dev/null || mkdir -p .mastermind

# Re-run init
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target . --force
```

---

## PostgreSQL Issues

### Problem: `connection refused` to PostgreSQL

**Error Message:**
```
psycopg2.OperationalError: could not connect to server: Connection refused
    Is the server running on host "localhost" and accepting
    TCP/IP connections on port 5433?
```

**Cause:** PostgreSQL container not running

**Diagnosis:**
```bash
# Check if PostgreSQL is running
docker compose ps

# Check if port 5433 is listening
netstat -an | grep 5433
# OR
ss -tlnp | grep 5433
```

**Solution:**
```bash
# Start PostgreSQL
cd /path/to/mastermind
docker compose up -d

# Verify
docker compose ps | grep postgres
```

**Expected Output:**
```
mastermind-postgres-1   /docker-entrypoint.sh...   Up   0.0.0.0:5433->5432/tcp
```

---

### Problem: `database "mastermind_bd" does not exist`

**Error Message:**
```
psycopg2.OperationalError: database "mastermind_bd" does not exist
```

**Cause:** Database not created

**Solution:**
```bash
# Create database
docker exec -it mastermind-postgres-1 psql -U postgres -c "CREATE DATABASE mastermind_bd;"

# Verify
docker exec -it mastermind-postgres-1 psql -U postgres -l | grep mastermind_bd
```

---

### Problem: `FATAL: password authentication failed`

**Error Message:**
```
psycopg2.OperationalError: FATAL: password authentication failed for user "postgres"
```

**Cause:** Incorrect password in configuration

**Diagnosis:**
```bash
# Check current config
cat .mastermind/config.yaml | grep -A 5 database

# Check docker-compose.yml credentials
cd /path/to/mastermind
grep -A 10 "POSTGRES_PASSWORD" docker-compose.yml
```

**Solution:**
```bash
# Update config with correct credentials
vim .mastermind/config.yaml

# Ensure password matches docker-compose.yml
database:
  password: devpassword  # Default from docker-compose.yml
```

---

### Problem: PostgreSQL using too much memory

**Symptoms:** System slows down when PostgreSQL is running

**Diagnosis:**
```bash
# Check PostgreSQL memory usage
docker stats mastermind-postgres-1

# Check shared_buffers setting
docker exec -it mastermind-postgres-1 psql -U postgres -c "SHOW shared_buffers;"
```

**Solution:**
```bash
# Limit PostgreSQL memory in docker-compose.yml
services:
  postgres:
    environment:
      - POSTGRES_SHARED_BUFFERS=256MB
      - POSTGRES_WORK_MEM=16MB
    deploy:
      resources:
        limits:
          memory: 1G
```

**Restart:**
```bash
docker compose down
docker compose up -d
```

---

## Command Issues

### Problem: Discover doesn't generate files

**Symptoms:**
```bash
python3 .claude/commands/mm/discover-handler.py "Add feature"
# No tasks/ directory created
```

**Diagnosis:**
```bash
# Check if discover-planner agent exists
ls -la .claude/agents/mm/discover-planner/

# Check handler output
python3 .claude/commands/mm/discover-handler.py "Test" 2>&1 | grep -E "(ERROR|WARNING|STATUS)"
```

**Solution:**
```bash
# Re-install MasterMind
python3 /path/to/mastermind/.claude/commands/mm/init-handler.py --target . --force

# Verify agents copied
ls -la .claude/agents/mm/discover-planner/
```

---

### Problem: Review fails with "no changes detected"

**Symptoms:**
```bash
python3 .claude/commands/mm/review-handler.py
# Output: MODE: review, SCOPE: uncommitted
# But says "no files to review"
```

**Diagnosis:**
```bash
# Check git status
git status

# Check if there are actual changes
git diff
```

**Solution:**
```bash
# Make some changes first
echo "// new code" >> src/file.js

# Then review
python3 .claude/commands/mm/review-handler.py

# OR review staged changes
git add .
python3 .claude/commands/mm/review-handler.py --staged
```

---

### Problem: Ship fails with "preconditions failed"

**Error Message:**
```
PRECONDITIONS: fail
WARNING: Preconditions failed:
  - Tests are not passing
  - There are uncommitted changes
```

**Diagnosis:**
```bash
# Check which preconditions failed
python3 .claude/commands/mm/ship-handler.py --verify

# Check uncommitted changes
git status

# Check if tests pass
pytest  # or npm test
```

**Solution:**
```bash
# 1. Fix failing tests
pytest  # Identify failures
vim failing_test.py  # Fix
pytest  # Verify

# 2. Commit or stash uncommitted changes
git add .
git commit -m "fix: test failures"

# 3. Verify again
python3 .claude/commands/mm/ship-handler.py --verify
```

---

### Problem: Ship fails with "SPEC.md does not exist"

**Error Message:**
```
WARNING: Preconditions failed:
  - SPEC.md does not exist
```

**Cause:** No specification document found

**Diagnosis:**
```bash
# Check for SPEC.md
find . -name "SPEC.md"

# Check expected location
ls -la tasks/SPEC.md
ls -la .planning/tasks/SPEC.md
```

**Solution:**
```bash
# Run discover first to generate SPEC.md
python3 .claude/commands/mm/discover-handler.py "Your feature idea"

# Verify SPEC.md created
cat tasks/SPEC.md

# Now ship
python3 .claude/commands/mm/ship-handler.py --verify
```

---

## Brain Consultation Issues

### Problem: Brain consultations not saving to database

**Symptoms:**
- Commands run but no records in PostgreSQL
- `brain_consultations` table empty

**Diagnosis:**
```bash
# Check if brain consultations table exists
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "\dt brain_consultations"

# Check if records exist
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "SELECT COUNT(*) FROM brain_consultations;"
```

**Solution:**
```bash
# Verify db_client can connect
python3 -c "from .claude.commands.mm.db_client import MasterMindDB; db = MasterMindDB(); print(db.ping())"

# Check connection string
cat .mastermind/config.yaml | grep -A 5 database

# Test insertion manually
python3 -c "
from .claude.commands.mm.db_client import MasterMindDB
db = MasterMindDB()
db.save_brain_consultation('brain-01-product', 'test', 'test response', 0.9, 'test-session')
print('Saved successfully')
"
```

---

### Problem: Brain #7 always rejects ideas

**Symptoms:**
- All discover requests rejected by Brain #7
- Low quality scores

**Diagnosis:**
```bash
# Check recent Brain #7 feedback
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
SELECT * FROM brain_feedback
WHERE brain_id = 'brain-07-growth'
ORDER BY created_at DESC
LIMIT 5;
"
```

**Possible Causes:**
1. Ideas lack business context
2. No clear problem statement
3. Missing success metrics

**Solution:**
```bash
# Provide more context in discover requests
python3 .claude/commands/mm/discover-handler.py \
  "Add user authentication to reduce support costs by 40% and improve conversion by 15%"
  # ↑ Added business impact and metrics
```

---

## Performance Issues

### Problem: Slow brain consultations (>10 seconds)

**Diagnosis:**
```bash
# Check PostgreSQL query performance
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
SELECT query, mean_exec_time, calls
FROM pg_stat_statements
ORDER BY mean_exec_time DESC
LIMIT 10;
"
```

**Solution:**
```bash
# Add indexes if missing
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
CREATE INDEX IF NOT EXISTS idx_brain_consultations_brain_id
ON brain_consultations(brain_id);

CREATE INDEX IF NOT EXISTS idx_brain_consultations_session_id
ON brain_consultations(session_id);
"

# Vacuum database
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "VACUUM ANALYZE;"
```

---

### Problem: Database growing too large

**Diagnosis:**
```bash
# Check database size
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
SELECT pg_size_pretty(pg_database_size('mastermind_bd'));
"

# Check largest tables
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
SELECT
  schemaname,
  tablename,
  pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**Solution:**
```bash
# Archive old brain consultations
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
INSERT INTO brain_consultations_archive
SELECT * FROM brain_consultations
WHERE created_at < NOW() - INTERVAL '90 days';

DELETE FROM brain_consultations
WHERE created_at < NOW() - INTERVAL '90 days';
"

# Vacuum
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "VACUUM FULL;"
```

---

## Getting Help

### Enable Debug Mode

```bash
export MASTERMIND_DEBUG=1
python3 .claude/commands/mm/discover-handler.py "Test"
```

### Check Logs

```bash
# Runtime state
cat .planning/.mm-flow/runtime-state.json

# Recent brain consultations
docker exec -it mastermind-postgres-1 psql -U postgres -d mastermind_bd -c "
SELECT * FROM brain_consultations
ORDER BY created_at DESC
LIMIT 10;
"
```

### Export Diagnostic Info

```bash
# Create diagnostic bundle
mkdir -p mm-diagnostic
cp -r .mastermind mm-diagnostic/
cp -r .planning mm-diagnostic/
docker exec -it mastermind-postgres-1 pg_dump -U postgres mastermind_bd > mm-diagnostic/db.sql

# Create tarball
tar czf mm-diagnostic-$(date +%Y%m%d).tar.gz mm-diagnostic/
```

### Report Issues

When reporting issues, include:

1. **Error message** (full stack trace)
2. **Command used** (exact command with arguments)
3. **Environment info:**
   ```bash
   python3 --version
   docker --version
   docker compose ps
   ```
4. **Diagnostic bundle** (from above)

---

## Quick Reference

| Issue | Quick Fix |
|-------|-----------|
| psycopg2 missing | `pip install psycopg2-binary` |
| PostgreSQL not running | `docker compose up -d` |
| Installation failed | Re-run with `--force` |
| Discover no files | Check agent exists |
| Review no changes | `git add` first |
| Ship preconditions | Run `--verify` first |
| Slow queries | Add indexes, VACUUM |
| DB too large | Archive old data |

---

**Still stuck?** Check [DEPLOYMENT.md](DEPLOYMENT.md) or open a GitHub issue.
