# ARCHITECTURE.md - System Architecture

**MasterMind Framework** - Cognitive architecture for expert knowledge consultation

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLI Layer                               │
│  (click commands: source, brain, orchestrate, eval, framework)  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      Orchestrator Layer                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │   Flow      │  │   Brain     │  │   NotebookLM        │    │
│  │  Detector   │→│  Executor   │→│   Client (MCP)      │    │
│  └─────────────┘  └─────────────┘  └─────────────────────┘    │
│         ↓                ↓                      ↓               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐    │
│  │   Plan      │  │  Evaluator  │  │  Output Formatter   │    │
│  │  Generator  │  │  (Brain #7) │  │  (Rich Terminal)    │    │
│  └─────────────┘  └─────────────┘  └─────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Knowledge Layer                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────┐  │
│  │  Software Dev   │  │  Marketing      │  │  Universal    │  │
│  │  (7 brains)     │  │  (16 brains)    │  │  (Brain #8)   │  │
│  └─────────────────┘  └─────────────────┘  └───────────────┘  │
│            ↓                    ↓                    ↓          │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │              NotebookLM (MCP)                            │  │
│  │  23 Notebooks × 10 sources = 230 expert sources         │  │
│  └─────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Memory Layer                                │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐      │
│  │ Interview     │  │  Evaluation   │  │  Serena       │      │
│  │ Logger        │  │  Storage      │  │  Memories     │      │
│  └───────────────┘  └───────────────┘  └───────────────┘      │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI Layer (`mastermind_cli/commands/`)

**Entry point:** `mastermind_cli/main.py:cli()`

**Commands:**
- `source` - Manage expert knowledge sources
- `brain` - Brain status and validation
- `orchestrate` - Process briefs through brains
- `eval` - Evaluation and interview management
- `framework` - Framework status and releases

**Pattern:** Click framework with command groups, subcommands, options

### 2. Orchestrator Layer (`mastermind_cli/orchestrator/`)

**Coordinator** (`coordinator.py`)
- Central orchestration engine
- Routes briefs to appropriate brains
- Manages brain execution sequence
- Handles evaluation iteration

**Flow Detector** (`flow_detector.py`)
- Analyzes brief complexity
- Selects flow type:
  - `full_product` - Complete product (1→2→3→4→5→6→7)
  - `validation_only` - Idea validation (1→7)
  - `design_sprint` - Design without build (1→2→3→7)
  - `build_feature` - Implement feature (4→5→6→7)
  - `optimization` - Optimize existing (7→1)
  - `technical_review` - Technical review (5→6→7)

**Brain Executor** (`brain_executor.py`)
- Executes individual brain queries
- Calls NotebookLM MCP
- Returns structured outputs

**Evaluator** (`evaluator.py`)
- Brain #7/#16 (meta-evaluator)
- Validates output quality
- Iterates up to 3 times for improvement
- Escalates to human if failed

**Plan Generator** (`plan_generator.py`)
- Creates execution plans
- Task decomposition
- Timeline estimation

**Output Formatter** (`output_formatter.py`)
- Formats brain outputs for display
- Rich terminal output
- JSON/YAML export options

### 3. Knowledge Layer

**Brains per niche:**

| Nicho | Cerebros | Meta-Evaluator | Total |
|-------|----------|----------------|-------|
| Software Development | 7 (M1-M7) | M7 | 7 |
| Marketing Digital | 16 (M1-M16) | M16 | 16 |
| Universal | 1 (Brain #8) | - | 1 |

**Brain structure:**
```
BRAIN-XX-NAME/
├── sources/
│   ├── FUENTE-XXX.md  (YAML frontmatter + content)
│   └── ...
└── notebook-config.json  (NotebookLM settings)
```

**System prompts:** `agents/brains/{niche}-{number}-{name}.md`

### 4. Memory Layer (`mastermind_cli/memory/`)

**Interview Logger** (`interview_logger.py`)
- Discovery interview logging
- Similar interview finding
- Learning statistics
- Retention policy (hot/warm/cold)

**Storage** (`storage.py`)
- File-based storage for interviews
- JSON serialization
- Date-based organization

**Models** (`models.py`)
- Pydantic data models
- Interview, Evaluation, Memory schemas

## Data Flow Patterns

### 1. Brief Processing Flow

```
User Input → CLI → Coordinator
    → Flow Detector (select flow)
    → Plan Generator (decompose into tasks)
    → Brain Executor (execute each brain)
    → NotebookLM MCP (query knowledge base)
    → Evaluator (quality check)
    → Output Formatter (display)
```

### 2. Discovery Interview Flow (Brain #8)

```
Vague Brief → CLI → Coordinator
    → Ambiguity Detection (3-tier check)
    → Interview Planning (via Brain #8)
    → Domain Brain Routing (M1-M7 or M1-M16)
    → Follow-up Generation
    → Learning System (save for future)
```

### 3. Evaluation Flow

```
Brain Output → Evaluator
    → Quality Check (criteria-based)
    → Approval/Rejection
    → If rejected: Iteration (max 3)
    → If failed: Escalate to human
    → Save to Storage (JSON)
```

## Abstractions

### Brain Interface
- **Input:** Brief + Context + Task
- **Output:** Structured response (JSON) + Content (Markdown)
- **Protocol:** YAML-based communication

### MCP Wrapper
- **Purpose:** Abstract MCP server interactions
- **Methods:** Query, source add, artifact generation
- **Error handling:** Timeout, retry, fallback

### Configuration System
- **brains.yaml** - Software development brains
- **brains-marketing.yaml** - Marketing digital brains
- **Multi-niche support** - Single config per niche

## Entry Points

| Entry Point | Purpose | File |
|-------------|---------|------|
| `mm` / `mastermind` | Main CLI | `mastermind_cli/main.py` |
| `mm orchestrate run` | Process briefs | `commands/orchestrate.py` |
| `mm source new` | Add source | `commands/source.py` |
| `/mm:discovery` | Discovery interviews | `.claude/commands/mm/discovery.md` |

## Design Patterns

| Pattern | Where Used | Purpose |
|---------|------------|---------|
| **Strategy** | Flow Detector | Select appropriate orchestration flow |
| **Chain of Responsibility** | Brain execution | Sequential brain processing |
| **Evaluator** | Brain #7/#16 | Meta-evaluation pattern |
| **Repository** | Storage | Abstract file operations |
| **Factory** | Brain registry | Brain instantiation |
| **Observer** | Output formatter | Progress reporting |

## Scalability Considerations

**Current state:**
- 2 nichos × ~10 brains = ~20 brains
- 23 NotebookLM notebooks
- 230+ expert sources

**Future expansion:**
- Add new niches via `brains-{niche}.yaml`
- Each niche = 7-16 brains
- NotebookLM MCP scales horizontally
- File-based storage = simple backup/migration

## Performance

**Bottlenecks:**
- NotebookLM MCP calls (network I/O)
- Large source file parsing
- Sequential brain execution

**Optimizations:**
- Parallel MCP calls where possible
- Source file caching
- Flow-based pruning (skip unnecessary brains)
