# MasterMind CLI Protocol — Momento 2 Brain Consultation

## Patrón Correcto para Consultar Brains Técnicos

**Working directory:** `apps/api/` (donde está pyproject.toml del mm CLI)

**Command pattern:**
```bash
cd apps/api
export $(cat ../.env | grep -v '^#' | xargs) && uv run mm orchestrate run "[BRIEF]" --brains [BRAIN_IDS] --use-mcp --parallel
```

**Por qué `../.env`:**
- El `.env` está en la raíz del proyecto (`/home/rpadron/proy/mastermind/.env`)
- El CLI se ejecuta desde `apps/api/`
- Por lo tanto, el path relativo es `../.env`

**Notebook IDs (Software Development niche):**
| Brain | ID | Domain |
|-------|-----|---------|
| brain-01 | f276ccb3-0bce-4069-8b55-eae8693dbe75 | Product Strategy |
| brain-02 | ea006ece-00a9-4d5c-91f5-012b8b712936 | UX Research |
| brain-03 | 8d544475-6860-4cd7-9037-8549325493dd | UI Design |
| brain-04 | 85e47142-0a65-41d9-9848-49b8b5d2db33 | Frontend |
| brain-05 | c6befbbc-b7dd-4ad0-a677-314750684208 | Backend |
| brain-06 | 74cd3a81-1350-4927-af14-c0c4fca41a8e | QA/DevOps |
| brain-07 | d8de74d6-7028-44ed-b4d5-784d6a9256e6 | Growth/Data (Evaluator) |
| brain-08 | 5330e845-29dc-4219-9d7e-c1ccb4851bb3 | Master Interviewer |

**Workflow:**
1. Momento 1: discuss-phase (UX) ✅
2. Momento 2: brains técnicos (Frontend/Backend/QA/UX) ⏳ AHORA
3. Momento 3: brain-07 evalúa TODO el conjunto ⏳ DESPUÉS
4. → /gsd:plan-phase N

**Brief structure for Momento 2:**
- Context: Phase goal + tech stack + prior decisions
- Key questions por domain (4 questions por brain)
- Expected output: Technical patterns, implementation recommendations, risk assessment
