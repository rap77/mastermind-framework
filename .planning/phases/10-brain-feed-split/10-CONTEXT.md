# Phase 10: BRAIN-FEED Split - Context

**Gathered:** 2026-03-28
**Status:** Ready for planning

<domain>
## Phase Boundary

Migrate monolithic `.planning/BRAIN-FEED.md` to a two-level architecture: 1 global feed (cross-domain, product/UX decisions only) + 7 domain feeds (one per brain). The global feed retains only what ALL brains need equally. Domain feeds are initialized with seed content via archaeology + Brain #8 validation. No agent files are modified in this phase — domain feed file paths are already locked in 21 agent files from Phase 09.

**Target:** Global feed < 20 entries after cleanup. If it stays at 50+, there's still "technical fat" that belongs in domain feeds.

</domain>

<decisions>
## Implementation Decisions

### Feeds Vacíos (#1-product, #2-ux, #7-growth)
- **Strategic Anchor approach** — not empty, not full archaeology.
- Process: Archaeology of Phase 01-08 SUMMARYs → extract 3-5 Architecture Facts per domain → Brain #8 validation ("Is there a critical business decision missing that would bias this brain?") → write refined anchors.
- Max 3 "Strategic Anchors" per feed: the facts that, if missing, cause the brain to hallucinate generic responses.
- Brain #2 UX specific anchors required: "War Room = IDE, not SaaS dashboard", "4-panel layout (Command Center, Nexus, Vault, Engine Room)", "ICE Scoring ≥ 15 for animations".
- Brain #1 Product specific anchors: "Builder IS the user", "T1 reduction = ROI metric (not generic conversion)", "v2.2 — not greenfield, mature system".
- Brain #7 Growth anchors: "Delta-Velocity scale (1-5)", "T1 Profitability Threshold: > 300s = agent-unprofitable".

### Global Feed Strictness — Ownership-First
- **Global feed = EXCLUSIVELY product decisions, UX decisions, and phase milestones affecting ALL 7 brains equally.**
- Zero technical entries in global, even if they affect 2 domains.
- Every technical entry has one "Owner Principal" (the brain that knows it best).
- Rule: "Which brain, if it got this wrong, would cause the biggest production failure?" → that's the owner.
- Examples: Auth & Security → Brain #5 Backend (owner). WS token handoff → Brain #5 Backend (owner), pointer in Brain #4 Frontend.
- Stack (Locked) table: stays in global — it's a product/architecture decision, not a technical pattern.
- Brain Agent Architecture section: stays in global — meta-architecture all brains need equally.
- Delta-Velocity Measurement: stays in global — cross-domain measurement framework.

### Migration Approach — Niche-Validation Loop (3 plans)
- **Plan 10-01: Engineering Niche** — #4 Frontend + #5 Backend + #6 QA feeds. Includes quick smoke test within the plan (ask Brain #4 to explain Auth protocol from its new local feed only — if it hallucinates, adjust ambiguity rule immediately).
- **Plan 10-02: Strategy Niche** — #1 Product + #2 UX + #3 UI + #7 Growth feeds. Brain #8 validates strategic anchors before finalizing seed content.
- **Plan 10-03: Global Consolidation** — Cleanup of global BRAIN-FEED.md (remove all domain entries). Apply purity linter. Run integrity verification script (hash/count assertion).
- Advantage: if Engineering niche smoke test fails, we adjust the ownership rule BEFORE migrating the Strategy niche.

### Cross-Reference — Pointer Explícito + SYNC Tags (Phase 12 hook)
- When domain B needs info owned by domain A: add a one-liner in domain B's feed.
- Format: `Sync: [Entry description] — [SYNC: BF-05-WS-PROTOCOL] → BRAIN-FEED-05-backend.md`
- The `[SYNC: BF-NN-ID]` tag is the hook for Phase 12 Context Proxy automation (orchestrator parses tags, clones entry into temporal context at dispatch time).
- Do NOT create bidirectional cross-links — only the secondary consumer gets the pointer, the owner file stays clean.
- Phase 10 implements pointers manually. Phase 12 automates injection.

### Verification Protocol
- **Hash/count script** (Python, idempotent): parse original BRAIN-FEED.md → count N entries → after migration count entries across all 8 files → assert N_original == N_new, no duplicates.
- **Path existence validation**: parse all `.claude/agents/mm/**/*.md` → extract `BRAIN-FEED-NN-domain.md` paths → assert each exists on disk. Silent failure (non-existent path = no error + empty context) must be caught before Phase 11.
- **Global purity linter**: grep global BRAIN-FEED.md for domain vocabulary (`Zustand`, `NODE_TYPES`, `dagre`, `FastAPI`, `SQLAlchemy`, `asyncio`, `pytest`, `Vitest`) — assert zero matches (excluding Stack table).
- All three checks must pass before Plan 10-03 is marked complete.

### Claude's Discretion
- Exact format/structure of each domain feed file (headers, sections, markdown style)
- Which specific anti-patterns from the old feed go to which brain (follows classification rule mechanically)
- ID numbering scheme for SYNC tags (e.g., BF-05-001, BF-05-002, etc.)
- Whether to use Python or bash for verification scripts

</decisions>

<specifics>
## Specific Ideas

- Target metric: global BRAIN-FEED.md < 20 entries after cleanup. > 20 = still has technical fat.
- Brain #4 (Frontend) will likely fail its first cross-reference test if the pointer to Backend WS Protocol isn't ultra-clear. This failure is expected and diagnostic — it tells us exactly how much needs to be cloned.
- SYNC tag format `[SYNC: BF-NN-ID]` doubles as Phase 12 automation hook — design for future even while implementing manually now.
- Engineering Niche smoke test within Plan 10-01 is a "pre-Phase 11" — double value from the validation step.

</specifics>

<code_context>
## Existing Code Insights

### Reusable Assets
- `.planning/BRAIN-FEED.md` (157 lines): the source of truth for migration. All entries classified and mapped.
- `.claude/agents/mm/` (21 files): domain feed paths locked, no modification needed.
- `tests/baselines/*.md`: QA-relevant entries (baseline anchors, delta-velocity schema) → `BRAIN-FEED-06-qa.md`

### Established Patterns
- Brain Bundle 3-file pattern (agent + criteria + warnings): domain feed is a 4th file per domain — same directory pattern
- `brain-selection.md` as single source of truth for notebook IDs: same decoupling philosophy applies to feed content ownership

### Integration Points
- All 7 agent system prompts already reference domain feed paths — Phase 10 creates the files, agents start reading them immediately
- Phase 11 smoke tests will validate feed content quality end-to-end — Phase 10 must produce feeds that Phase 11 can test

</code_context>

<brain_enrichment>
## Brain #4 + #5 Enrichment (re-run 2026-03-28)

### Frontend Feed Architecture (Brain #4)

**Confirmed: ALL listed global entries belong exclusively to Frontend domain:**
NODE_TYPES/EDGE_TYPES module-level, dagre once via useState, React Flow CSS @layer base, React Compiler DISABLED, useBrainState(id) selector, RAF batching, ICE ≥ 15 for animations, CLUSTER_CONFIGS data-driven, TanStack Query staleTime: 30s.

**Minimum viable BRAIN-FEED-04-frontend.md structure (4 sections):**
1. **State & Rendering Engine** — Zustand Map + Immer, useBrainState(id), RAF batching
2. **React Flow Internals** — NODE_TYPES module-level, dagre once, @layer base CSS
3. **Performance & Quality Radar** — React Compiler DISABLED, animation policy (opacity + transform ONLY — width/height causes layout reflow and will be rejected), TanStack Query as server state source of truth
4. **Security Boundaries** — No localStorage, DOMPurify on dynamic content, SYNC pointers to Backend

**SYNC cross-references required in BRAIN-FEED-04-frontend.md (4 entries):**
- `[SYNC: BF-05-WS-AUTH]` — WS token handoff protocol (Frontend must know the handshake — cannot hallucinate)
- `[SYNC: BF-05-COOKIE-POLICY]` — httpOnly confirmation (Frontend must NOT attempt JS cookie read)
- `[SYNC: BF-05-API-CONTRACTS]` — Zod schemas ✅ confirmed (`apps/web/src/types/api.ts`, `login/actions.ts`) — Frontend validates API responses with Zod, needs contract shape
- `[SYNC: BF-05-ERROR-SCHEMA]` — Error response standard (Frontend maps 500/429 to user messages — needs the shape)

### Backend Feed Architecture (Brain #5)

**Confirmed Backend-exclusive entries (migrate to BRAIN-FEED-05-backend.md):**
- Auth & Security: JWT at Server Components + Route Handlers (CVE-2025-29927), httpOnly cookies, /api/auth/token WS handoff, DOMPurify + html.escape
- API Design: pagination (page_size default 24, max 100), IDOR protection pattern (`WHERE id = :id AND user_id = :current_user_id`), eager loading (`selectinload` for one-to-many — N+1 prevention) [⚠️ selectinload not yet in codebase — include as required pattern in feed]
- DevOps: uv only (never pip), `cd apps/api && uv run pytest` (never from root)

**Guardrail-first feed structure** — Critical Constraints MUST appear at top of Step 1 read:
```
## Critical Constraints (Non-Negotiable)
- uv only, never pip
- pytest from apps/api/ only
- JWT in httpOnly cookies only — never client bundle
- WS auth via /api/auth/token handoff pattern
```
Reason: Brain #5 without these constraints defaults to Node.js patterns or root-level Python.

### Script Implementation Specifics (Brain #5)

**Hash/count verification:**
- Parse by **bullet points** (`^- `), NOT by headers — headers group multiple decisions that may split across domain feeds
- Assert set equality: `set(original_entries) == union(all_domain_entries)` — conservation law

**Path existence validation:**
- `pathlib.Path.glob("**/*.md")` on `.claude/agents/mm/`
- Regex: `BRAIN-FEED-\d{2}-[\w-]+\.md` to extract expected paths
- Assert `path.exists()` for every extracted path

**Global purity linter:**
- Use **word boundaries** (`\bFastAPI\b`, `\bZustand\b`) — prevents false positives in Stack table rows
- **Verbose fail output**: when match found, print line number + 2-line context for rapid manual fixing
- Silent pass (no output = clean) — CI-friendly

### UX Feed Architecture (Brain #2)

**Strategic Anchors expanded (6 total, not 3):**

The 3 original anchors are INSUFFICIENT. Brain #2 would give generic SaaS dashboard advice without these additions:

**Original 3 (still valid):**
1. War Room = IDE, not SaaS dashboard
2. 4-panel layout (Command Center, Nexus, Vault, Engine Room)
3. ICE Scoring ≥ 15 for animations

**New anchors #4-6 (CRITICAL additions):**
4. **Efficiency > Learnability:** Expert speed (Time-on-task) > new user success. No "onboarding tours" — those are SaaS patterns, not IDE patterns
5. **High Information Density:** Use Chunking (Miller's Law) to organize data, NOT "minimalism" that removes necessary context
6. **Engine Status Feedback (H1):** Every uv/pnpm action needs immediate visual feedback (loading states, mini-consolas) — close the Gulf of Evaluation

**War Room = IDE (elaborated):**
- Mental Model: "Tool" not "Product" — user builds strategy, doesn't consume content
- Direct Manipulation: In Nexus, moving a node must feel PHYSICAL (natural mapping)
- Anti-patterns Brain #2 would suggest WITHOUT these anchors:
  - "Reduce Command Center options" → WRONG: Experts prefer categorized many-options (Hick's Law correctly applied)
  - "Add helpful tooltips" → WRONG: If you need a label for basic interaction, design failed (Norman)
  - "Make it mobile-friendly" → WRONG: React Flow DAG = Desktop First (Fitts's Law precision requirement)

**Code verification:**
- Command Palette: ❌ not implemented yet → aspirational pattern for feed
- 8px baseline grid: ❌ not explicitly verified → include as aspirational
- Engine Room status feedback: ✅ Phase 08 implemented — anchor validated

### UI Feed Architecture (Brain #3)

**Inferred seeds are INSUFFICIENT.** Brain #3 needs explicit architectural invariants:

**Design System (OKLCH + Nova Preset):**
- **Perceptual Uniformity:** All color tokens via OKLCH → WCAG 2.1 AA auto-compliance ✅ confirmed (`globals.css`)
- **3-Tier Token Architecture:** Global → Semantic → Component (e.g., `color-action-primary` → `brain-tile-border`)
- **Dark Mode Desaturation:** Brand colors desaturated in dark mode, background `#121212` (never `#000000`)
- **Anti-pattern:** Hardcoded hex values → use tokens only

**Component Patterns (Atomic Design):**
- `BrainTile` = Molecule, `BentoGrid` = Organism/Template
- **Rule of 5 States:** Every component MUST define: Default, Hover, Active, Disabled, Error/Loading
- **Layout Grid:** Command Center aligns to 8px baseline + 12-column system (breaking grid = functional narrative choice, not whim)
- **Touch Targets:** Mobile Nexus = 44x44px minimum hit area

**Animation (Beyond ICE ≥ 15):**
- **Functional Purpose:** Every animation serves Orientation, Feedback, Continuity, or Narrative — no "noise"
- **Duration Standards:** Micro-interactions 100-300ms, Modal/Canvas 300-600ms
- **Easing Invariant:** Never linear — use physically-inspired easing (ease-out entrance, ease-in exit)
- **Accessibility:** `prefers-reduced-motion` support mandatory (high-risk = >25% screen coverage)

**WCAG 2.1 AA Hard Floor:**
- **No Color Only:** ICE scores and errors MUST include icon or text (8% daltonism users)
- **Focus Ring Invariant:** `outline: none` forbidden unless replaced by custom 3:1 focus-visible ring
- **Prohibited:** Using placeholders as labels, truncating Y-axis in charts

**Code verification:**
- OKLCH ✅ confirmed in `globals.css`
- 12-column grid ❌ not explicitly found in Command Center — aspirational pattern
- Atomic Design levels ❌ not explicitly enforced — aspirational pattern

### Product Strategy Feed Architecture (Brain #1)

**Roadmap Anchors (v2.x Current State — Maturity Filter):**
- v2.2 = Brain Agents activo. Cualquier feature nueva debe pasar por la arquitectura de agentes, no ser un script aislado.
- 4 fases de v2 completadas — sistema maduro. Sugerir EVOLUCIONES, no revoluciones.
- Horizon visible: v3.0 = Custom Framework, v3.1 = OpenClaw. Filtrar libs externas que bloqueen esa migración.
- 575 backend tests = activo. Cambio estructural requiere advertencia de ruptura de contrato de tests.

**ICP Hard Constraint (Single-User — Builder IS the User):**
- Solo un usuario: Rafael. Prohibido sugerir RBAC complejo, comentarios multi-user, flujos de aprobación.
- Zero onboarding: el usuario construyó el sistema, ya lo conoce.
- UI de alta densidad: no espacios en blanco innecesarios ni botones "para principiantes".
- Feature válida solo si reduce T1 O aumenta Delta-Velocity.

**ROI Metric — T1 Reduction primario:**
- T1 = tiempo desde idea hasta código ejecutable.
- T1 > 300s = agente-unprofitable = descartar feature.
- Filtro binario: "¿Me ahorrás tiempo? Si no, no te construyo."

**Anti-patterns (Generic SaaS — bloqueo total):**
- Prohibido: feature flags, A/B testing, NPS surveys, trial flows, multi-tenant auth, SEO optimization, email marketing, onboarding tours, guided tours.
- Razón: Mastermind es un arma de ingeniería, no un producto de consumo.
- Sustituto para cada patrón bloqueado: Delta-Velocity Benchmarking (vs. A/B), local host auth (vs. multi-tenant), keyboard shortcuts (vs. tooltips).

### QA/DevOps Feed Architecture (Brain #6)

**Environment State (Hybrid-Bridge — Full Infra Aware):**
- Runtime Mapping: código en `//wsl$/Ubuntu/home/...`, permisos de ejecución pueden chocar con filesystem Windows.
- Network Topology: Docker Desktop corre en VM separada — port mapping entre apps/api (8000) y apps/web (3000) debe ser explícito en docker-compose.yml.
- Resource Awareness: Acer Predator tiene potencia para múltiples contenedores, pero monitorear vmmem RAM.
- Cross-OS constraints: `uv` desde apps/api/, `pnpm` desde apps/web/ — paths absolutos, nunca root execution.

**Test Regressions (Baseline Anchors + Delta Threshold):**
- Health Baseline: 575 backend / 407 frontend (instalación limpia post-Windows 11 reset).
- Delta Tolerance para Environment Flakiness: Timeout + Connection failures < 2% desde baseline = `wsl --shutdown` o reiniciar Docker, NO tocar código.
- Hard Failure: errores de Assertion (lógica) = protocolo de corrección de bugs, tolerancia cero.
- Hybrid rule: Delta threshold se aplica solo a categoría Infraestructura; Lógica tiene tolerancia 0%.

**Deployment Protocol (Exit Codes + Smoke Test — 3 pasos obligatorios):**
1. `docker compose up -d` → assert exit 0
2. `curl -f localhost:8000/health` (Backend) + `curl -f localhost:3000` (Frontend) → assert 200
3. Scan últimas 20 líneas de logs buscando `Traceback` o `Error` ignorado por el proceso principal
- Regla: "Never assume success without HTTP 200 from the service."
- Solo si 3/3 pasos pasan → Brain #6 marca deploy como "Verified Successful".

**Toxic Tooling Block (Anti-patterns — rechazo incondicional):**
| Categoría | Acción Prohibida | Herramienta Correcta |
|-----------|-----------------|---------------------|
| Python | `pip install` | `uv add` |
| Node.js | `npm install` / `yarn` | `pnpm install` |
| Testing | `pytest .` (root) | `cd apps/api && uv run pytest` |
| Seguridad | `sudo` sin justificación de infra | Solicitar permiso explícito |

### Growth/Data Feed Architecture (Brain #7)

**Token Efficiency Metric (Context Window Consumption Ratio):**
- Baseline X = tokens promedio cargados por agente con GLOBAL-FEED monolítico.
- Post-Split Y = tokens promedio por agente con DOMAIN-FEED + GLOBAL-PURIFIED.
- Success threshold: Ratio Y/X < 0.7 (reducción ≥ 30% del ruido de contexto).
- Brain #7 mide este ratio en cada smoke test de Fase 11. Si ratio ≥ 0.7 → "Global Feed sigue con grasa técnica, el split fue insuficiente."

**Velocity Trends (Micro + Macro en paralelo):**
- **T1 Trend por brain (Micro — Termómetro):** Track T1 individual por brain fase a fase. T1 de Brain #4 subiendo 70s+ → feed de Frontend saturado → refactorizar .md. Baselines documentadas en Fase 09 (T1 210-270s, todos < 300s).
- **Delta-Velocity por milestone (Macro — Brújula):** DV promedio del sistema por milestone completo. Si DV baja en v2.2 vs v2.1 → la arquitectura de agentes añade más burocracia que valor.
- **Correlación válida:** T1 sube + DV sube = trade-off aceptable (IA piensa más pero código de mayor calidad).
- Para Fase 10 específicamente: foco en T1 Trend por brain (validar que el split aislamiento funcionó).

**Regression Protocol (Diagnose-before-escalate):**
1. **Detección:** monitoreo T1 y DV en tiempo real, transparente.
2. **Diagnóstico:** clasificar causa — ¿sube T1 en todos los agentes? (ruido WSL2) vs ¿solo en uno? (feed saturado).
3. **Mitigación:** 2 ciclos de auto-limpieza de feeds/ajuste de prompt. Notificar "Optimización en curso".
4. **Escalación:** si persiste tras 2 intentos → informe de diagnóstico completo + sugerencia técnica → Rafael decide.
- Filtrar outliers: ignorar picos aislados < 3 interacciones (evita falsos positivos de procesos background Windows).

**Hard Stop Thresholds (Non-Negotiable):**
| Estado | Umbral | Acción |
|--------|--------|--------|
| Óptimo | T1 < 120s | Flujo continuo |
| Warning | 120s < T1 < 300s | Auto-limpieza background |
| CRÍTICO | T1 > 300s OR DV < 1 | Abortar plan + intervención arquitecto |
- DV < 1 = inversión negativa = se pierde más tiempo corrigiendo al agente que escribiendo a mano.
- Hard stop congela Fase 11 hasta que el diagnóstico resuelva el cuello de botella.

</brain_enrichment>

<deferred>
## Deferred Ideas

- **Context Proxy automation** (full implementation) — Phase 12. SYNC tags are the design hook planted in Phase 10.
- **Feed auto-pruning script** ("stale entry detection") — mentioned in Brain #1 criteria.md as a Rating 5 leverage point. Not Phase 10 scope.
- **24-brain niche expansion** (Marketing, etc.) — v3.x. Phase 10 only handles the 7 software development brains.

</deferred>

---

*Phase: 10-brain-feed-split*
*Context gathered: 2026-03-28 (enriched: Brain #4+#5 first pass, Brain #2+#3 second pass, Brain #1+#6+#7 third pass — all 7 domain feeds fully specified with architecture, anti-patterns, and metrics)*
