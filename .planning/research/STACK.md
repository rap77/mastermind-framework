# Stack Research: MasterMind v2.2 Brain Agents

**Domain:** Claude Code Subagent System — per-brain autonomous agents with domain-specific BRAIN-FEED accumulation
**Researched:** 2026-03-27
**Confidence:** HIGH (subagent format verified from claude-plugins-official source; dispatch pattern verified from GSD workflows; existing mm:brain-context skill analyzed directly)

> **Note:** This replaces the v2.1 frontend STACK.md for this milestone.
> The backend/frontend stack (FastAPI, Next.js 16, etc.) is unchanged and validated.
> This document covers ONLY what changes or is added for v2.2 Brain Agents.

---

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Claude Code subagents** | `.claude/agents/mm/*.md` format | Brain consultation automation | Native Claude Code capability — zero dependencies, no new packages, intermediary protocol becomes built-in agent behavior instead of skill instructions |
| **Agent tool (`Task()`)** | Claude Code built-in | Parallel brain agent dispatch | Only mechanism for true parallel subagent execution in Claude Code; replaces sequential `mm:brain-context` skill steps |
| **NotebookLM MCP** | `mcp__notebooklm-mcp__notebook_query` | Knowledge retrieval per brain | Already integrated and functional — agents inherit the MCP tool access from their tool list |
| **Markdown + YAML frontmatter** | No version — plain text | Agent file format + BRAIN-FEED files | `.claude/agents/mm/brain-NN-*.md` files are the agents; `.planning/BRAIN-FEED-NN-domain.md` files are plain Markdown — no libraries needed |

**No new Python packages.** No new npm packages. v2.2 is entirely a Claude Code configuration and file structure change.

---

### Agent File Format (Claude Code Subagent Spec)

Claude Code agent files live at `.claude/agents/<namespace>/<name>.md`. For this project: `.claude/agents/mm/brain-NN-domain.md`.

**Required YAML frontmatter fields:**

| Field | Required | Valid Values | Notes |
|-------|----------|-------------|-------|
| `name` | Yes | lowercase, hyphens, 3-50 chars | Identifier used in `Task(subagent_type=...)` dispatch |
| `description` | Yes | String with `<example>` blocks | Defines auto-trigger conditions — must include 2-4 `<example>` blocks |
| `model` | Yes | `inherit`, `sonnet`, `opus`, `haiku` | Use `inherit` for brain agents — they run in the same context as the orchestrator |
| `color` | Yes | `blue`, `cyan`, `green`, `yellow`, `magenta`, `red` | Visual identifier only — no functional impact |
| `tools` | No (optional) | Array of tool names | If omitted, agent has all tools. Recommended: restrict to minimum needed |

**Minimal agent file structure:**

```markdown
---
name: brain-01-product
description: Use this agent when the orchestrator needs Product Strategy consultation...

<example>
Context: Moment 1 — about to create ROADMAP.md
user: "Run brain-01 for milestone context"
assistant: "I'll dispatch the brain-01-product agent to query the Product Strategy brain."
<commentary>
Orchestrator dispatching brain agent for Moment 1 roadmap context.
</commentary>
</example>

model: inherit
color: blue
tools: ["Read", "Grep", "Glob", "Bash"]
---

You are the Product Strategy brain intermediary for MasterMind Framework...
```

**System prompt constraints:**
- Write in second person ("You are...", "You will...")
- Max 10,000 characters
- Recommended: 500-3,000 characters
- Must define: responsibilities, process steps, output format

---

### Dispatch Pattern — Agent Tool (`Task()`)

The orchestrator dispatches brain agents in parallel by calling `Task()` for each agent in a single message. This is the key mechanism for DISP-01.

**Single agent dispatch:**
```
Task(
  subagent_type="brain-01-product",
  prompt="<context>[IMPLEMENTED REALITY]\n...\n\n<files_to_read>\n- .planning/BRAIN-FEED.md\n- .planning/BRAIN-FEED-01-product.md\n</files_to_read>",
  description="Brain #1: Product Strategy context for Phase N"
)
```

**Parallel dispatch (multiple brains simultaneously):**
```
# All Task() calls in a single orchestrator message = parallel execution
Task(subagent_type="brain-02-ux", prompt="...", description="Brain #2: UX Research")
Task(subagent_type="brain-03-ui", prompt="...", description="Brain #3: UI Design")
Task(subagent_type="brain-04-frontend", prompt="...", description="Brain #4: Frontend")
```

**Important:** Parallel execution requires all `Task()` calls to appear in the same message. If they appear in separate messages, they run sequentially.

**The `files_to_read` block in the prompt:** Each agent gets a `<files_to_read>` block in its prompt pointing to:
1. `.planning/BRAIN-FEED.md` (global project feed)
2. `.planning/BRAIN-FEED-NN-domain.md` (domain-specific feed)
3. Relevant code files for the specific query

**Agent naming → dispatch name mapping:**

| File path | `name` field | `Task(subagent_type=...)` value |
|-----------|-------------|----------------------------------|
| `.claude/agents/mm/brain-01-product.md` | `brain-01-product` | `"brain-01-product"` |
| `.claude/agents/mm/brain-02-ux.md` | `brain-02-ux` | `"brain-02-ux"` |
| `.claude/agents/mm/brain-07-growth.md` | `brain-07-growth` | `"brain-07-growth"` |

---

### BRAIN-FEED File Structure

The two-level BRAIN-FEED split (FEED-01) requires these files:

| File | Owner | Content |
|------|-------|---------|
| `.planning/BRAIN-FEED.md` | Orchestrator | Cross-domain patterns, architecture decisions, stack invariants — read by ALL agents |
| `.planning/BRAIN-FEED-01-product.md` | brain-01-product agent | Product strategy patterns, prioritization decisions, discovery insights |
| `.planning/BRAIN-FEED-02-ux.md` | brain-02-ux agent | UX research findings, user flow patterns, usability decisions |
| `.planning/BRAIN-FEED-03-ui.md` | brain-03-ui agent | Visual design decisions, component patterns, accessibility |
| `.planning/BRAIN-FEED-04-frontend.md` | brain-04-frontend agent | Frontend architecture patterns, performance decisions, state management |
| `.planning/BRAIN-FEED-05-backend.md` | brain-05-backend agent | API design patterns, data modeling, infra decisions |
| `.planning/BRAIN-FEED-06-qa.md` | brain-06-qa agent | Testing strategy, CI/CD patterns, reliability patterns |
| `.planning/BRAIN-FEED-07-growth.md` | brain-07-growth agent | Evaluation criteria, metrics, systems thinking patterns |

**Format:** Plain Markdown, no schema required. Structure: sections by pattern category, each entry with date and context. Existing `BRAIN-FEED.md` content migrates to the global file; domain-specific content extracted to per-brain files.

---

### Evaluation Criteria and Anti-patterns Files

Per AGT-02 and AGT-03, each brain domain needs two support files. These are plain Markdown — no tooling required.

**Location convention:** `.claude/agents/mm/criteria/brain-NN-evaluation-criteria.md` and `.claude/agents/mm/criteria/brain-NN-anti-patterns.md`

OR embed directly in the agent's system prompt body. Embedding is simpler (fewer files, agent always has access) and recommended for v2.2.

**Embedding vs. separate files tradeoff:**

| Approach | Pro | Con |
|----------|-----|-----|
| Embed in agent system prompt | Always available, no read step | Increases system prompt size |
| Separate files in `.claude/agents/mm/criteria/` | Editable without touching agent | Agent must `Read` them — adds latency |

**Recommendation:** Embed evaluation criteria and anti-patterns inline in the agent system prompt body. They're short (< 500 words each), and keeping them in the system prompt guarantees the agent never forgets them.

---

### Updated mm:brain-context Command (DISP-02)

The existing `/mm:brain-context` slash command at `.claude/commands/mm/brain-context.md` gets updated to dispatch agents via `Task()` instead of reading skill workflow files. The command becomes an orchestration coordinator — it determines which brains to activate, builds the shared context block, and dispatches agents in parallel.

**What changes in the command:**
- Remove: `${CLAUDE_SKILL_DIR}/workflows/moment-N.md` references (manual workflow steps)
- Add: `Task(subagent_type="brain-NN-domain", prompt="...", description="...")` calls
- Keep: moment routing logic (1, 2, 3, feed)
- Keep: intermediary protocol principles (read codebase first, build context block)

**The orchestrator context block** (built before dispatch) contains:
```
[IMPLEMENTED REALITY]
[CORRECTED ASSUMPTIONS]
[WHAT I NEED]
```

This block becomes the `prompt` argument passed to each dispatched agent. Agents receive context, not instructions to build context.

---

## Installation

No new packages to install. v2.2 is pure file creation.

```bash
# Create agent files directory
mkdir -p /home/rpadron/proy/mastermind/.claude/agents/mm

# Create BRAIN-FEED per-domain files
touch .planning/BRAIN-FEED-01-product.md
touch .planning/BRAIN-FEED-02-ux.md
touch .planning/BRAIN-FEED-03-ui.md
touch .planning/BRAIN-FEED-04-frontend.md
touch .planning/BRAIN-FEED-05-backend.md
touch .planning/BRAIN-FEED-06-qa.md
touch .planning/BRAIN-FEED-07-growth.md

# Create agent files (7 total)
# .claude/agents/mm/brain-01-product.md
# .claude/agents/mm/brain-02-ux.md
# .claude/agents/mm/brain-03-ui.md
# .claude/agents/mm/brain-04-frontend.md
# .claude/agents/mm/brain-05-backend.md
# .claude/agents/mm/brain-06-qa.md
# .claude/agents/mm/brain-07-growth.md

# Create baseline documentation directory
mkdir -p docs/baselines
```

---

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| **`.claude/agents/mm/` (project-level)** | `~/.claude/agents/` (global) | If brain agents should work across all projects on the machine — not appropriate here, these agents are MasterMind-specific |
| **`Task()` dispatch from updated mm:brain-context** | New separate command (`/mm:dispatch-brains`) | Only if the existing command's routing logic becomes too complex to modify cleanly |
| **Embed criteria/anti-patterns in agent system prompt** | Separate `.md` files in `.claude/agents/mm/criteria/` | Separate files if criteria are long (>1000 words) or need frequent editing by non-developers |
| **`model: inherit`** | `model: sonnet` explicit | Explicit model only if agents need to be pinned regardless of what the orchestrator uses |
| **Plain Markdown BRAIN-FEED** | YAML-structured BRAIN-FEED | YAML schema adds value at v3.0 when CLI parses feeds programmatically — overkill for manual curation in v2.2 |

---

## What NOT to Add

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **New Python packages for agent orchestration** (LangChain, CrewAI, AutoGen) | Overkill — Claude Code's native Agent tool handles parallel dispatch with zero infrastructure | `Task()` dispatch in agent prompts |
| **Vector stores / embeddings** (ChromaDB, Qdrant) | v3.0 scope — requires architecture decision on chunking, indexing, retrieval. Manual BRAIN-FEED is sufficient for v2.2 | Plain Markdown BRAIN-FEED files |
| **Inter-agent YAML coordination protocol** | v2.3 scope (REQUIREMENTS.md explicitly deferred) — agents reading each other's feeds is simpler and validate-first | Agents write to own domain feed; orchestrator synthesizes |
| **Agent auto-discovery via config** (registry pattern, YAML agent manifest) | Adds indirection without benefit at 7 agents — files in `.claude/agents/mm/` are already auto-discovered by Claude Code | Direct file naming convention |
| **Separate evaluation runner** (Python script to grade agent outputs) | v2.2 scope is manual baselines only; auto-evaluation is v2.3+ | Human evaluation against `evaluation-criteria.md` |
| **`tools: ["*"]` in agent frontmatter** | Grants MCP tools including NotebookLM to all agents unconditionally — prefer explicit tool list | `tools: ["Read", "Grep", "Glob", "Bash"]` + `mcp__notebooklm-mcp__notebook_query` for brain agents |
| **Underscores in agent names** (`brain_01_product`) | Invalid per Claude Code naming rules (lowercase, hyphens only) | `brain-01-product` |

---

## Stack Patterns by Agent Type

**For brain consultation agents (brain-01 through brain-07):**
- `model: inherit` — runs with whatever model the orchestrator uses
- `tools: ["Read", "Grep", "Glob", "Bash"]` — codebase reading + NotebookLM MCP access inherited
- Color convention: blue (analysis) for all brain agents — consistent visual identity
- System prompt structure: role → feed reading instructions → intermediary protocol → output format

**For Brain #7 (Growth/Data — the Evaluator):**
- Same agent format as others
- Dispatched LAST, always — after domain brains complete (Moment 3)
- Its `prompt` from orchestrator includes: all domain brain outputs as context + PLAN.md
- Returns: APPROVED / APPROVED_WITH_CONDITIONS / REJECTED + gap list

**For the mm:brain-context orchestrator command:**
- NOT an agent file — stays as `.claude/commands/mm/brain-context.md` (slash command)
- Builds shared context block first, then dispatches brain agents via `Task()`
- Brain #7 is always a second dispatch (after collecting domain brain outputs), never parallel with domain brains

---

## Version Compatibility

| Component | Compatibility | Notes |
|-----------|--------------|-------|
| Agent name field | Must be `lowercase-hyphens`, 3-50 chars | Validated by Claude Code — `brain-01-product` is valid, `brain_01` is not |
| `subagent_type` in `Task()` | Must exactly match `name` field in agent frontmatter | Case-sensitive, no namespace prefix needed in call |
| Agent files in subdirectory | `.claude/agents/mm/*.md` | Subdirectories are supported — `mm/` becomes namespace prefix automatically |
| `files_to_read` block in Task prompt | Plain Markdown block — not a Claude Code API feature | GSD convention, not native API — agents parse it as part of their prompt instructions |
| NotebookLM MCP in agents | Available if parent session has MCP configured | Agents inherit MCP tool access from the session — no extra configuration |
| `model: inherit` | Inherits orchestrator's model | If orchestrator is claude-sonnet-4-6, agents are also claude-sonnet-4-6 |

---

## Sources

- `.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/skills/agent-development/SKILL.md` — Claude Code subagent format spec (frontmatter fields, validation rules, system prompt design) — HIGH confidence (first-party plugin tooling from Claude plugins marketplace)
- `.claude/plugins/marketplaces/claude-plugins-official/plugins/plugin-dev/agents/agent-creator.md` — Working agent example showing complete format + `model: sonnet, color: magenta, tools: [...]` — HIGH confidence
- `.claude/plugins/marketplaces/claude-plugins-official/plugins/feature-dev/agents/code-architect.md` — Minimal agent example (no description examples, short system prompt) — HIGH confidence
- `/home/rpadron/.claude/get-shit-done/workflows/execute-phase.md` — `Task(subagent_type=..., model=..., prompt=...)` dispatch pattern — HIGH confidence (GSD production usage)
- `/home/rpadron/.claude/get-shit-done/workflows/diagnose-issues.md` — Parallel `Task()` dispatch: "All agents spawn in single message" — HIGH confidence
- `.claude/skills/mm/brain-context/SKILL.md` + `references/intermediary-protocol.md` + `references/brain-selection.md` — Current mm:brain-context skill architecture, NotebookLM IDs, intermediary protocol (6 steps), cascade rules — HIGH confidence (v2.1 production)
- `.planning/PROJECT.md` + `.planning/REQUIREMENTS.md` — v2.2 scope, acceptance criteria, deferred items — HIGH confidence (approved requirements)

---

*Stack research for: MasterMind Framework v2.2 Brain Agents*
*Researched: 2026-03-27*
*Confidence: HIGH*
