# Paperclip UX Audit — Reference for MasterMind v3.0

> **Date:** 2026-04-04
> **Paperclip Version:** 0.3.1
> **Purpose:** Document UX patterns to COPY and IMPROVE for MasterMind v3.0

---

## Technology Stack (Paperclip)

| Layer | Technology |
|-------|-----------|
| Framework | React 19 + TypeScript |
| CSS | Tailwind CSS 4.0 + CSS variables |
| Components | shadcn/ui + Radix primitives |
| Routing | React Router 7 (company-prefix aware) |
| State | TanStack Query 5 (server state) |
| DnD | @dnd-kit/core |
| Icons | Lucide React |

---

## 10 UX Patterns to Replicate

### 1. Three-Column Layout (COPY)
- **Left:** CompanyRail (multi-tenant switcher, draggable)
- **Center:** Sidebar (nav: Issues, Agents, Goals, Routines, Costs)
- **Right:** Content area + Properties panel
- **Mobile:** Swipe gestures, bottom nav

### 2. Real-time Agent Monitoring (COPY)
- ActiveAgentsPanel with ping animation
- LiveRunWidget with transcript streaming
- Status badges: idle, running, completed, failed
- Compact density modes for different contexts

### 3. Company-as-Context (COPY for multi-tenant)
- Draggable company ordering via @dnd-kit
- Visual status indicators per company (live agents, unread inbox)
- Company-specific branding/icons
- Sync across tabs via localStorage

### 4. Agent Configuration Form (COPY + IMPROVE)
- AgentConfigForm: 1649 lines (too complex)
- Identity → Adapter → Permissions → Run Policy sections
- Dirty tracking with floating save button
- **IMPROVE:** Template gallery, config validation, import/export

### 5. Cost Dashboard (COPY)
- BillerSpendCard with hierarchical breakdown
- QuotaBar visual progress (percent of allocation)
- MetricCard for quick stats
- Provider-level cost tracking

### 6. Kanban Board (COPY)
- @dnd-kit for drag-and-drop
- Multi-column status workflow
- Compact cards with live run indicators
- **IMPROVE:** Swim lanes, bulk operations

### 7. Command Palette (COPY)
- Cmd/Ctrl+K trigger
- Radix Command dialog
- Search issues, agents, pages, actions
- Categorized results

### 8. Run Transcript (COPY + IMPROVE)
- Multi-density: compact, normal, detailed
- Raw vs Nice display modes
- Streaming updates
- **IMPROVE:** Search/filter, syntax highlighting, export

### 9. Onboarding Wizard (COPY + IMPROVE)
- Progressive step-by-step setup
- Goal-based company creation
- Adapter type selection
- Environment validation
- **IMPROVE:** Templates, progress save/resume

### 10. Org Chart (COPY)
- SVG-based org chart visualization
- ReportsToPicker for hierarchy
- CompanyPatternIcon per entity

---

## What Paperclip LACKS (MasterMind Opportunities)

| Gap | MasterMind Solution |
|-----|-------------------|
| **Knowledge Distillation** | 7 brain agents with expert knowledge |
| **Learning Loop** | Brain #7 evaluates → feedback → improves |
| **Template Marketplace** | Pre-built agent configurations per vertical |
| **Multi-channel** | WhatsApp + Instagram + Email gateway |
| **LATAM focus** | Regional adaptation, Spanish-first |
| **Rust performance** | Tokio async runtime, zero GC pauses |
| **gRPC type sync** | Protobuf contracts across Rust/Python/TS |

---

## MasterMind v3.0 Workflow Design

### Workflow 1: Agent Consultation
```
User brief → FlowDetector → Brain Agent → Knowledge (NotebookLM)
    → Experience Log → Brain #7 Evaluation → Output
```

### Workflow 2: Multi-Agent Orchestration
```
Canvas DAG → Brain #1 (product) → Brain #5 (backend) → Brain #4 (frontend)
    → Brain #6 (QA) → Brain #7 (validation) → APPROVED
```

### Workflow 3: Multi-Channel Dispatch
```
WhatsApp message → Channel Router → Brain Agent → Response
    → Human escalation if needed
```

### Workflow 4: Knowledge Learning Loop
```
Brain output → Brain #7 evaluates → Experience Logger
    → Anti-patterns detected → Brain memory updated
    → Templates generated from successful patterns
```

---

*Audit generated from Paperclip v0.3.1 source analysis*
*For MasterMind v3.0 Rust + Python + TypeScript architecture*
