# Phase 4 Context Complete - 2026-03-14

**Status:** ✅ CONTEXT.md created for Phase 4
**File:** `.planning/phases/04-experience-store-production/04-CONTEXT.md`

## Decisions Captured

### Experience Logging Strategy
- **Granularidad:** JSON Completo (full fidelity para debugging, fine-tuning, RAG)
- **PII/Secrets:** Auto-filtrado regex + Semantic Redaction (Pydantic SecretStr)
- **Retención:** Archive JSONL (30 días en DB, luego .jsonl.gz comprimidos)
- **Schema:** Extensible JSONB + Lineage (parent_brain_id, trace_context_id)

### Brain-to-Brain Protocol
- **Ejecución:** State-Machine Orchestrator + Hybrid Pulse (Event-Bus + 500ms check-in fallback)
- **Payload:** Typed Interfaces (Pydantic) con Smart Reference (Lazy Loading)
- **Formato:** Wrapped Envelope (sobre simple + contenido YAML-based del ROADMAP)
- **Routing:** Orchestrator-directed DAG (Conditional Branching para evolución)

### Backward Compatibility
- **Versioning:** Snapshot Pinning (prompt hash en flow.yaml, avisa si cambia)
- **Breaking changes:** Additive Only = OK (agregar campos es safe, borrar = breaking)
- **Testing:** Hybrid (Core brains #1, #7, #8 automated; resto manual quarterly)
- **Regression:** Semantic Similarity (embeddings, score > 90% para deploy)

### CI Pipeline
- **Levels:** Tiered (Nivel 1: mypy+ruff todos PRs | Nivel 2: tests PRs | Nivel 3: semantic releases)
- **Environment:** Runner-native con uv (uv run pytest, uv.lock para paridad WSL2)
- **Security:** Secrets Only (Trufflehog CI) + Git-Hook Shield (pre-commit local)
- **Deployment:** Docker Registry (git push + docker registry + docker pull)

## Next Steps

### Option A: Plan Phase 4
```bash
/gsd:plan-phase 04
```
Creates 5 execution plans:
- 04-01: ExperienceRecord schema and JSONB storage
- 04-02: Brain-to-brain communication protocol
- 04-03: Backward compatibility verification
- 04-04: Comprehensive E2E test suite
- 04-05: CI pipeline setup

### Option B: Skip to Planning
```bash
/gsd:plan-phase 04 --skip-research
```
Create plans without research phase (faster, less depth)

### Option C: Review/Edit Context First
Edit `.planning/phases/04-experience-store-production/04-CONTEXT.md` before planning

---

*Created: 2026-03-14*
*Phase: 04-experience-store-production*
