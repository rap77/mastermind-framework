# MasterMind Framework v2.0

## What This Is

A cognitive architecture framework for building specialized AI-powered solutions using expert "brains" — distilled knowledge from world-class geniuses organized by niche. v2.0 transforms the current CLI-only sequential framework into a production-ready platform with parallel execution, type safety, and graphical interface.

## Core Value

**Expert AI collaboration that scales.** The framework enables multiple specialized brains to work together on complex problems, from product strategy to marketing to software development — faster, safer, and more reliably than any single brain could achieve alone.

## Requirements

### Validated

- ✓ CLI orchestration engine (sequential) — v1.0
- ✓ 23 brains across 2 niches (Software Dev, Marketing) — v1.3.0
- ✓ Brain #8 (Master Interviewer) for discovery — v1.1.0
- ✓ NotebookLM integration for knowledge retrieval — v1.0
- ✓ E2E testing framework — v1.3.0
- ✓ Memory & Learning system — v1.1.0

### Active

- [ ] **PAR-01**: Brains execute in parallel when independent
- [ ] **PAR-02**: Dependency-aware orchestration (some brains wait for others)
- [ ] **TS-01**: Type-safe interfaces between all components (mypy strict)
- [ ] **TS-02**: Pydantic models for all data structures
- [ ] **TS-03**: Type-safe MCP integration
- [ ] **UI-01**: Web dashboard for brain orchestration
- [ ] **UI-02**: Real-time progress visualization
- [ ] **UI-03**: Multi-user session support
- [ ] **ARCH-01**: Foundation for shared memory layer (future ML)
- [ ] **ARCH-02**: Brain-to-brain communication protocol
- [ ] **ARCH-03**: Experience storage for future learning

### Out of Scope

- **Machine learning auto-improvement** — v3.0+ (requires R&D)
- **Full RAG system with vector DB** — v3.0+ (PostgreSQL + pgvector/qdrant)
- **Mobile apps** — Web-first, mobile responsive only
- **Real-time collaborative editing** — v3.0+
- **Multi-tenant SaaS** — Single-tenant deployment only for v2.0

## Context

**Current State (v1.3.0):**
- Sequential brain execution via Orchestrator
- 2 niches: Software Development (7 brains), Marketing Digital (16 brains)
- CLI-only interface (`mm` command)
- Dynamic typing (Python runtime)
- NotebookLM as knowledge backend
- Single-user sessions

**User Personas:**
1. **Developers** — Building products using expert brains
2. **Agencies/Companies** — Offering AI-powered services to clients
3. **End Users** — Non-technical users interacting through UI

**Use Cases Driving v2.0:**
- AI Agency Platform needs faster brain execution (parallel)
- Enterprise integration requires type safety (contracts)
- Client-facing applications need web UI (not CLI)
- Future ML learning needs shared memory architecture

## Constraints

- **Technology Stack**: Python 3.14+, must maintain backward compatibility with v1.x brains
- **Deployment**: Self-hosted only (no SaaS managed service in v2.0)
- **Timeline**: Quality over speed — several months acceptable
- **Team**: Solo developer + AI assistance (Claude Code)
- **Resources**: No budget for external services or paid APIs

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| **Include UI in v2.0** | End users can't use CLI; agencies need client-facing interface | — Pending |
| **Paralelization before ML** | Parallel execution benefits all users immediately; ML is R&D heavy | — Pending |
| **Type safety with Pydantic** | Validation + JSON serialization + IDE support in one package | — Pending |
| **Web dashboard over desktop app** | Cross-platform, easier deployment, browser ubiquity | — Pending |
| **Foundation for shared memory** | Don't build full ML, but design data structures for future v3.0 | — Pending |
| **Maintain CLI alongside UI** | Power users prefer CLI; UI is optional interface | — Pending |

## Vision Notes (v3.0+)

**Not building in v2.0, but designing for:**

- **Shared Memory Layer**: Centralized brain memory where experiences are stored
- **Cross-Brain Learning**: Brains learn from each other's experiences
- **Hallucination Prevention**: RAG-based fact checking across all brains
- **Auto-Improvement**: ML pipeline that fine-tunes based on successful outcomes

**v2.0 will:**
- Design data structures for experience storage
- Create brain-to-brain communication protocol
- Lay groundwork for future vector DB integration
- NOT implement actual ML training or vector databases

---
*Last updated: 2026-03-13 after project initialization*
