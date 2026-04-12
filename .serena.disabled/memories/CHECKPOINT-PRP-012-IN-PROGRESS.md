# PRP-012 In Progress - NotebookLM Setup

**Date:** 2026-03-07
**Branch:** `feature/prp-012-brain-08-notebooklm-setup`
**Status:** 10% Complete (1/10 sources created)

## What's Done

| Component | Status | File |
|-----------|--------|------|
| **Branch Created** | ✅ | `feature/prp-012-brain-08-notebooklm-setup` |
| **Sources Directory** | ✅ | `docs/software-development/08-master-interviewer-brain/sources/` |
| **FUENTE-801** | ✅ | `FUENTE-801_the-mom-test_fitzpatrick.md` |

## What's Pending

| ID | Title | Author | Status |
|----|--------|-------|--------|
| 802 | Never Split the Difference | Chris Voss | 🔴 TODO |
| 803 | The Coaching Habit | Michael Bungay Stanier | 🔴 TODO |
| 804 | Continuous Discovery Habits | Teresa Torres | 🔴 TODO |
| 805 | User Interviews | Erika Hall | 🔴 TODO |
| 806 | Thinking, Fast and Slow | Daniel Kahneman | 🔴 TODO |
| 807 | Crucial Conversations | Patterson et al. | 🔴 TODO |
| 808 | Improve Your Retrospectives | Judith Andres | 🔴 TODO |
| 809 | Ask Method | Ryan Levesque | 🔴 TODO |
| 810 | Socratic Questioning | Various | 🔴 TODO |

## Next Steps

1. Create FUENTE-802 (Never Split the Difference)
2. Create remaining 8 sources (FUENTE-803 to FUENTE-810)
3. Create NotebookLM notebook manually
4. Upload all 10 sources
5. Get notebook ID from URL
6. Update `mastermind_cli/config/brains.yaml`:
   - Set `notebook_id` to actual UUID
   - Change `status` from `pending` to `active`
7. Validate with `mm brain status`

## Template Reference

Use `FUENTE-801_the-mom-test_fitzpatrick.md` as template for all sources.

Key sections:
- YAML frontmatter with metadata
- Datos de la Fuente
- Experto Asociado
- Habilidades que Cubre
- Resumen Ejecutivo
- Conocimiento Destilado:
  - 1. Principios Fundamentales
  - 2. Frameworks y Metodologías
  - 3. Modelos Mentales
  - 4. Criterios de Decisión
  - 5. Anti-patrones

## Commands to Continue

```bash
# Verify branch
git branch  # Should be: feature/prp-012-brain-08-notebooklm-setup

# List created sources
ls -la docs/software-development/08-master-interviewer-brain/sources/

# Continue with FUENTE-802
# Use FUENTE-801 as template
```

## Validation Commands

```bash
# Validate YAML in all sources
python -c "
import yaml
from pathlib import Path

sources_dir = Path('docs/software-development/08-master-interviewer-brain/sources')
for f in sources_dir.glob('FUENTE-*.md'):
    try:
        with open(f) as file:
            yaml.safe_load_all(file)
        print(f'✅ {f.name}')
    except Exception as e:
        print(f'❌ {f.name}: {e}')
"
```

## References

- PRP: `PRPs/PRP-012-brain-08-notebooklm-setup.md`
- Spec: `docs/software-development/08-master-interviewer-brain/spec-brain-08-master-interviewer.md`
- Template: `docs/software-development/08-master-interviewer-brain/sources/FUENTE-801_the-mom-test_fitzpatrick.md`
