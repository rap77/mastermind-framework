# Spec: Cerebro #8 - Master Interviewer / Discovery Brain

**Version:** 1.0.0
**Status:** Draft
**Date:** 2026-03-07
**Author:** MasterMind Framework Team
**PRP:** PRP-010 (pending)

---

## Table of Contents

1. [Overview](#overview)
2. [Problem Statement](#problem-statement)
3. [Goals & Non-Goals](#goals--non-goals)
4. [User Stories & Use Cases](#user-stories--use-cases)
5. [Technical Design](#technical-design)
6. [Architecture](#architecture)
7. [Data Flow](#data-flow)
8. [API Design](#api-design)
9. [Integration Points](#integration-points)
10. [Error Handling](#error-handling)
11. [Security Considerations](#security-considerations)
12. [Performance Considerations](#performance-considerations)
13. [Testing Strategy](#testing-strategy)
14. [Edge Cases](#edge-cases)
15. [Decisions Log](#decisions-log)
16. [Dependency Graph](#dependency-graph)
17. [Implementation Plan](#implementation-plan)

---

## Overview

**Cerebro #8: Master Interviewer / Discovery Brain** is a specialized brain with expertise in information extraction through structured interviews. Unlike brains #1-7 (domain experts), Brain #8 is a **facilitator** that knows HOW to interview, structure information, and orchestrate other brains to extract comprehensive requirements.

**Key Differentiator:** Brain #8 does not contain domain knowledge itself—it leverages brains #1-7 for domain expertise while focusing on interview methodology, question structuring, and information synthesis.

---

## Problem Statement

The MasterMind Framework has three critical gaps:

1. **Ambiguous Briefs:** Users provide vague inputs like "quiero una app moderna" which fail in Brain #1 without structured clarification
2. **No Discovery Process:** There's no systematic way to extract requirements from users who don't know technical terminology or what they want
3. **No Gap Detection:** When knowledge is missing (e.g., SEO, marketing), the system cannot recommend creating new brains

**Current State:**
```
User Input → Brain #1 (fails if vague) → Manual intervention required
```

**Desired State:**
```
User Input → Brain #8 (discovers & clarifies) → Structured brief → Brain #1-7 (execute)
```

---

## Goals & Non-Goals

### Goals ✅

1. **Extract structured information** from users who cannot clearly express requirements
2. **Conduct iterative interviews** where domain brains (#1-7) can dynamically probe based on responses
3. **Detect knowledge gaps** and recommend new brains to be created
4. **Generate interview documents** in JSON (API communication), YAML (logging), and Markdown (human-readable)
5. **Integrate with PRP-009** learning system to improve interview quality over time
6. **Provide AskUserQuestion interface** for rich, guided user experience

### Non-Goals ❌

1. **Contain domain expertise** — that's what brains #1-7 are for
2. **Generate final specs** — it outputs Q&A documents, not PRDs
3. **Replace human interviews** — it augments, not replaces, human facilitation
4. **Work without MCP** — it requires NotebookLM for knowledge retrieval
5. **Store all interview data permanently** — retention policy applies

---

## User Stories & Use Cases

### Use Case 1: Client Onboarding (Marketing Agency)

**Actor:** Account Manager at a marketing agency
**Goal:** Generate a technical brief from a non-technical client

**Flow:**
```
1. Client: "Necesito una app para mi negocio"
2. Brain #8 interviewer launches
3. Iterative Q&A with Brain #1 (Product) guidance:
   - "¿Qué tipo de negocio?" → "Restaurantes de comida rápida"
   - "¿Qué problemas resolvés hoy?" → "Paper-based orders, lost tickets"
   - "¿Quiénes son los usuarios?" → "Cajeros, gerentes, clientes"
4. Brain #8 generates structured Q&A document
5. Orquestador distributes to relevant brains (#1, #3, #4, #5)
6. Final technical brief generated
```

**Output:** Technical brief with clear requirements, personas, and success metrics

### Use Case 2: Brief Clarification

**Actor:** Product Manager with vague feature idea
**Goal:** Transform "quiero una app moderna" into actionable requirements

**Flow:**
```
Input: "quiero una app moderna"
   ↓
Brain #8 detects ambiguity
   ↓
Iterative interview:
   Q: "¿Qué significa 'moderno' para vos?"
   A: "Dark mode, gestures, animations"
   Q: "¿Qué problema resuelve?"
   A: "Necesito controlar inventory desde móvil"
   Q: "¿Quiénes son los usuarios?"
   A: "Warehouse staff, field technicians"
   ↓
Structured Q&A document
```

**Output:** Clarified brief with specific UI/UX requirements and user personas

### Use Case 3: Technical Specification

**Actor:** Tech Lead needing to architect a new feature
**Goal:** Generate complete spec for "OAuth integration"

**Flow:**
```
Input: "Necesitamos OAuth login"
   ↓
Brain #8 interviews:
   - Providers: Google, Microsoft, GitHub
   - Flows: Authorization code, PKCE
   - Token storage, refresh strategy
   - Error handling, revoked tokens
   ↓
Q&A document categorized by domain
   ↓
Brains #5 (Backend), #4 (Frontend), #6 (QA) receive relevant questions
   ↓
Each brain generates domain-specific recommendations
   ↓
Orquestador synthesizes complete technical spec
```

**Output:** Technical spec with API design, security requirements, and test cases

---

## Technical Design

### Core Knowledge Areas (Brain #8 Own Expertise)

Brain #8 must have direct knowledge (not delegated) in these areas:

#### 1. Interview Methodologies
- **The Mom Test** (Rob Fitzpatrick) — Discover real needs, not stated wants
- **Socratic Questioning** — Deepen understanding through probing
- **Active Listening** — Detect contradictions and gaps
- **Critical Inquiry** — Challenge assumptions constructively

#### 2. Anti-Patterns & Biases
- **Confirmation Bias** — Avoiding leading questions
- **Recency Bias** — Not focusing only on last statement
- **Halo Effect** — Not assuming one good answer means all are good
- **Leading Questions** — "¿No te parece que X?" → ❌
- **Binary Thinking** — Avoiding forced yes/no questions

#### 3. Facilitation Techniques
- **Probing**: "¿Podés dar un ejemplo específico?"
- **Elucidation**: "¿A qué te referís exactamente con X?"
- **Connection**: "¿Cómo se relaciona esto con Y que mencionaste antes?"
- **Summarization**: "Entonces, hasta ahora entendí que X. ¿Correcto?"
- **Handling Non-Responsive Users**: Techniques when user doesn't know what to say

#### 4. Document Structuring
- **Templates** for different interview types (onboarding, feature spec, technical design)
- **Categorization** of questions by domain (ux, ui, frontend, backend, qa, product)
- **Confidence Scoring** of answers (high, medium, low)
- **Follow-Up Flags** for questions needing deeper exploration

### Expert Sources for Brain #8

#### Primary Sources (Must Load in NotebookLM)

1. **The Mom Test** — Rob Fitzpatrick
   - ISBN: 978-0993181515
   - Expert ID: EXP-801
   - Focus: Discovering real needs vs polite lies

2. **Never Split the Difference** — Chris Voss
   - ISBN: 978-0062407803
   - Expert ID: EXP-802
   - Focus: Negotiation & information extraction techniques

3. **The Coaching Habit** — Michael Bungay Stanier
   - ISBN: 978-0978440749
   - Expert ID: EXP-803
   - Focus: Powerful questions that trigger insight

4. **Continuous Discovery Habits** — Teresa Torres
   - ISBN: 978-1734313504
   - Expert ID: EXP-804
   - Focus: Interview-based product discovery

5. **User Interviews** — Erika Hall
   - Expert ID: EXP-805
   - Focus: Interview methodology for user research

6. **Thinking, Fast and Slow** — Daniel Kahneman
   - ISBN: 978-0374533557
   - Expert ID: EXP-806
   - Focus: How people actually think (system 1 vs system 2)

7. **Crucial Conversations** — Patterson, Grenny, et al.
   - ISBN: 978-1469266824
   - Expert ID: EXP-807
   - Focus: Questions in high-stakes situations

8. **Fifty Quick Ideas to Improve Your Retrospectives** — Judith Andres
   - Expert ID: EXP-808
   - Focus: Reflective questioning techniques

#### Secondary Sources (Optional)

9. **Ask: The Counterintuitive Online Method to Discover** — Ryan Levesque
10. **The Art of Debugging Interviews** — Patterns for extracting technical info

### Brain Registry Entry

```yaml
# mastermind_cli/brain_registry.py
BRAIN_REGISTRY = {
    # ... existing brains #1-7 ...

    8: {
        "name": "Master Interviewer / Discovery",
        "notebook_id": "BRAIN-08-ID-PENDING",  # To be assigned after NotebookLM creation
        "expertise": [
            "Interview methodology",
            "Information extraction",
            "Question structuring",
            "Gap detection",
            "Facilitation techniques"
        ],
        "status": "active",
        "version": "1.0.0"
    }
}
```

---

## Architecture

### Component Diagram

```
┌──────────────────────────────────────────────────────────────┐
│                     User Interface                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  AskUserQuestion UI (Tabbed, Multiple Choice)        │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│                  Orchestrator (Improved)                    │
│  • Detects when interview is needed                         │
│  • Routes questions to appropriate brains                   │
│  • Manages interview state (current category, progress)     │
│  • Paginates long interviews                                │
└──────────────────────────────────────────────────────────────┘
                            ↓
        ┌───────────────────┴───────────────────┐
        │                                       │
┌───────▼────────┐                    ┌────────▼──────┐
│  Brain #8       │                    │  Brains #1-7  │
│  (NotebookLM)   │◄──── Delegation ────│  (Domain      │
│                 │      Consultation    │   Experts)    │
│  Interview      │     (per question)   │               │
│  Methodology    │                    │  #1: Product   │
│  Question       │                    │  #2: UX        │
│  Structuring    │                    │  #3: UI        │
│  Gap Detection  │                    │  #4: Frontend  │
└─────────────────┘                    │  #5: Backend   │
        │                              │  #6: QA/DevOps │
        │                              └────────────────┘
        ↓                                         ↓
┌─────────────────────────────────────────────────────────┐
│           Interview Document (Multi-Format)             │
│  • JSON (API communication)                              │
│  • YAML (logging in PRP-009)                            │
│  • Markdown (human-readable)                            │
└─────────────────────────────────────────────────────────┘
        ↓
┌─────────────────────────────────────────────────────────┐
│              PRP-009 Learning System                    │
│  • Logs all interviews                                   │
│  • Tracks question effectiveness                         │
│  • Enables retrieval of similar interviews               │
│  • Improves Brain #8 prompts over time                   │
└─────────────────────────────────────────────────────────┘
```

### Iterative Interview Flow

```
┌──────────────────────────────────────────────────────────────┐
│  Phase 1: Interview Start                                    │
│  1. User provides input (brief, problem statement)           │
│  2. Orchestrator detects need for interview                 │
│  3. Orchestrator calls Brain #8: "Design interview for X"    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Phase 2: Category Selection                                 │
│  Brain #8: "We'll cover these categories:"                   │
│    - Users (UX)                                              │
│    - Platforms (Frontend)                                    │
│    - Architecture (Backend)                                  │
│    - Success Metrics (Product)                               │
│    "Let's start with Users."                                 │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Phase 3: Iterative Questioning (Loop per category)          │
│                                                              │
│  Brain #8: "What type of users?"                             │
│    ↓                                                         │
│  User: "SMBs, 10-50 employees"                               │
│    ↓                                                         │
│  Orchestrator: category=ux → Brain #2                        │
│    ↓                                                         │
│  Brain #2 (sees user's answer): "Can you describe a          │
│    typical day for these users?"                             │
│    ↓                                                         │
│  User: [Describes workflow]                                  │
│    ↓                                                         │
│  Brain #2: "What tools do they use today?"                   │
│    ↓                                                         │
│  User: [Lists tools]                                         │
│    ↓                                                         │
│  Brain #2: "I have enough context. Moving to next category." │
│    ↓                                                         │
│  Orchestrator: category=platforms → Brain #4                 │
│    ↓                                                         │
│  [Loop repeats for each category]                            │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Phase 4: Document Generation                                │
│  Brain #8 synthesizes all Q&A into structured document:      │
│    • JSON for API communication                              │
│    • YAML for logging                                        │
│    • Markdown for display                                    │
└──────────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────────────────────────────────────────────────┐
│  Phase 5: Distribution & Execution                           │
│  Orchestrator parses document, distributes to brains #1-7    │
│  Each brain generates domain-specific recommendations         │
│  Orchestrator synthesizes final output                       │
└──────────────────────────────────────────────────────────────┘
```

### Brain #8 Internal Structure

```
Cerebro #8: Master Interviewer
├── Base Conceptual
│   ├── Principios: The Mom Test, Socratic questioning
│   ├── Psicología: System 1 vs System 2 thinking
│   └── Anti-patrones: Confirmation bias, leading questions
│
├── Frameworks Operativos
│   ├── Question Templates: User types, use cases, constraints
│   ├── Interview Patterns: Onboarding, feature spec, technical design
│   └── Categorization: Mapping questions to domains (#1-7)
│
├── Modelos Mentales
│   ├── Information Gap Theory: What don't we know?
│   ├── Cone of Abstraction: Specific → General → Specific
│   └── 5 Whys: Root cause discovery
│
├── Criterios de Decisión
│   ├── ¿Cuándo hacer follow-up? (Confidence < medium)
│   ├── ¿Cuándo cambiar de categoría? (Brain signals "enough")
│   ├── ¿Cuándo detectar gap? (No matching brain for category)
│   └── ¿Cuándo recomendar nuevo cerebro? (Gap confirmed)
│
└── Mecanismo de Retroalimentación
    ├── Aprende de interviews previas (via PRP-009)
    ├── Ajusta preguntas según effectiveness rate
    └── Recupera patrones de interviews similares
```

---

## Data Flow

### Sequence Diagram: Complete Interview Flow

```
User    Orchestrator    Brain #8    Brain #2 (UX)    Brain #4 (Front)
 │           │              │              │                 │
 │ Input:    │              │              │                 │
 │ "Login    │              │              │                 │
 │  feature" │              │              │                 │
 ├──────────►│              │              │                 │
 │           │ Detect need  │              │                 │
 │           │ for interview│              │                 │
 │           ├─────────────►│              │                 │
 │           │              │ Design       │                 │
 │           │              │ interview    │                 │
 │           │              │ plan         │                 │
 │           │◄─────────────┤              │                 │
 │           │              │              │                 │
 │           │ Q1: "What    │              │                 │
 │           │  users?"     │              │                 │
 │◄──────────┤              │              │                 │
 │ Answer:   │              │              │                 │
 │ "SMBs     │              │              │                 │
 │  10-50"   │              │              │                 │
 ├──────────►│              │              │                 │
 │           │ Route to UX  │              │                 │
 │           ├─────────────────────────────►│                 │
 │           │              │    See:      │                 │
 │           │              │    "SMBs"    │                 │
 │           │              │              │                 │
 │           │              │    Follow-up:│                 │
 │           │              │    "Describe │                 │
 │           │              │     typical  │                 │
 │           │              │     day"     │                 │
 │           │◄─────────────────────────────┤                 │
 │           │ Follow-up Q │              │                 │
 │◄──────────┤              │              │                 │
 │ [Answer]  │              │              │                 │
 ├──────────►│              │              │                 │
 │           │ Route to UX  │              │                 │
 │           ├─────────────────────────────►│                 │
 │           │              │  "Enough,    │                 │
 │           │              │   next cat"  │                 │
 │           │◄─────────────────────────────┤                 │
 │           │ Next: Web/Mobile            │                 │
 │           ├─────────────────────────────────────────────► │
 │           │              │              │    See: prev    │
 │           │              │              │    Q: "What     │
 │           │              │              │     users?"     │
 │           │              │              │    Follow-up:   │
 │           │              │              │    "Web or      │
 │           │              │              │     mobile?"    │
 │           │◄─────────────────────────────────────────────┤
 │           │ Q: "Web or Mobile?"             │             │
 │◄──────────┤              │              │                 │
 │ [Continue answering...]
 │           │              │              │                 │
 │           │   [Loop for all categories]  │                 │
 │           │              │              │                 │
 │           │ Interview complete           │                 │
 │           ├─────────────►│              │                 │
 │           │              │ Generate Q&A │                 │
 │           │              │ document     │                 │
 │           │◄─────────────┤              │                 │
 │           │              │              │                 │
 │           │ Distribute to brains for recommendations      │
 │           ├─────────────────────────────────────────────►│
 │           │              │              │                 │
 │           │  [Each brain generates domain recommendations]│
 │           │              │              │                 │
 │           │◄─────────────────────────────────────────────┤
 │           │ Synthesize final output      │                 │
 │◄──────────┤              │              │                 │
 │ [Final brief/spec]              │              │                 │
```

---

## API Design

### 1. JSON Schema for Interview Document (API Communication)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "MasterMind Interview Document",
  "type": "object",
  "required": ["version", "type", "metadata", "document"],
  "properties": {
    "version": {
      "type": "string",
      "const": "1.0",
      "description": "Document schema version"
    },
    "type": {
      "type": "string",
      "const": "qa_document",
      "description": "Document type identifier"
    },
    "metadata": {
      "type": "object",
      "required": ["timestamp", "context", "interviewer", "session_id"],
      "properties": {
        "timestamp": {
          "type": "string",
          "format": "date-time",
          "description": "ISO 8601 timestamp of interview start"
        },
        "context": {
          "type": "string",
          "description": "Brief problem statement or feature description"
        },
        "context_type": {
          "type": "string",
          "enum": ["feature_spec", "technical_design", "client_onboarding", "gap_analysis"],
          "description": "Type of interview context"
        },
        "interviewer": {
          "type": "string",
          "const": "brain-08",
          "description": "Brain ID conducting the interview"
        },
        "session_id": {
          "type": "string",
          "description": "Unique session identifier for tracking"
        },
        "duration_minutes": {
          "type": "integer",
          "description": "Total interview duration in minutes"
        },
        "industry": {
          "type": "string",
          "description": "Industry context (e.g., 'saas_b2b', 'ecommerce', 'fintech')"
        }
      }
    },
    "document": {
      "type": "object",
      "required": ["categories", "qa"],
      "properties": {
        "categories": {
          "type": "array",
          "description": "Categories covered in interview",
          "items": {
            "type": "object",
            "properties": {
              "id": {"type": "string"},
              "name": {"type": "string"},
              "target_brain": {"type": "integer"},
              "questions_count": {"type": "integer"},
              "status": {
                "type": "string",
                "enum": ["pending", "in_progress", "completed"]
              }
            }
          }
        },
        "qa": {
          "type": "array",
          "description": "Questions and answers",
          "items": {
            "type": "object",
            "required": ["id", "question", "answer", "category", "target_brain"],
            "properties": {
              "id": {
                "type": "string",
                "description": "Unique question identifier (e.g., q001)",
                "pattern": "^q[0-9]{3}$"
              },
              "question": {
                "type": "string",
                "description": "The question asked"
              },
              "answer": {
                "type": "string",
                "description": "User's response"
              },
              "category": {
                "type": "string",
                "description": "Category identifier (maps to categories array)"
              },
              "target_brain": {
                "type": "integer",
                "minimum": 1,
                "maximum": 7,
                "description": "Brain ID that should process this question"
              },
              "follow_up_questions": {
                "type": "array",
                "description": "Follow-up questions asked by domain brain",
                "items": {
                  "type": "object",
                  "properties": {
                    "question": {"type": "string"},
                    "answer": {"type": "string"},
                    "asked_by": {"type": "integer"}
                  }
                }
              },
              "confidence": {
                "type": "string",
                "enum": ["high", "medium", "low"],
                "description": "Confidence level in the answer"
              },
              "follow_up_needed": {
                "type": "boolean",
                "description": "Whether this question needs follow-up"
              },
              "notes": {
                "type": "string",
                "description": "Additional notes or context"
              }
            }
          }
        },
        "gaps_detected": {
          "type": "array",
          "description": "Knowledge gaps detected during interview",
          "items": {
            "type": "object",
            "properties": {
              "category": {"type": "string"},
              "missing_expertise": {"type": "string"},
              "suggested_brain_id": {"type": "integer"},
              "suggested_brain_name": {"type": "string"},
              "priority": {
                "type": "string",
                "enum": ["low", "medium", "high"]
              },
              "rationale": {"type": "string"}
            }
          }
        }
      }
    },
    "outcome": {
      "type": "object",
      "description": "Interview outcome and metrics",
      "properties": {
        "questions_asked": {"type": "integer"},
        "categories_covered": {"type": "integer"},
        "gaps_identified": {"type": "integer"},
        "completion_status": {
          "type": "string",
          "enum": ["complete", "partial", "needs_followup"]
        },
        "user_satisfaction": {
          "type": "string",
          "enum": ["low", "medium", "high"],
          "description": "User satisfaction score (if provided)"
        }
      }
    }
  }
}
```

### 2. YAML Schema for Logging (PRP-009 Integration)

```yaml
---
# Interview Log Entry (stored in logs/interviews/hot/YYYY-MM/)
interview_id: "INTERVIEW-2026-03-07-001"
timestamp: "2026-03-07T10:30:00Z"
brain: "brain-08"
session_id: "sess-abc123"

context:
  brief_original: "quiero una app moderna"
  context_type: "feature_spec"
  industry: "saas_b2b"

interview:
  questions_asked: 15
  duration_minutes: 12
  categories_covered: 5
  questions_with_followup: 3
  gaps_identified: 1

outcome:
  user_satisfaction: "high"
  useful_questions: ["q001", "q005", "q012"]
  failed_questions: ["q008"]
  final_output_quality: "approved"

qa_document:
  # Reference to JSON document
  json_path: "interviews/2026-03/INTERVIEW-2026-03-07-001.json"

  # Human-readable summary (for quick log inspection)
  summary: |
    Interview for feature specification
    - Users: SMBs 10-50 employees, B2B SaaS
    - Platforms: Web + iOS/Android
    - Key features: Real-time sync, offline mode
    - Gaps: No SEO/Marketing expertise

# Learning metrics (for PRP-009 analysis)
learning_metrics:
  question_effectiveness_rate: 0.87  # 13/15 questions were useful
  user_satisfaction_score: 5
  avg_confidence_score: "medium"
  followup_rate: 0.20  # 20% of questions needed followup
```

### 3. Markdown Template for Human Display

```markdown
# Interview Document: [Context]

**Date:** March 7, 2026
**Session ID:** sess-abc123
**Interviewer:** Brain #8 (Master Interviewer)
**Duration:** 12 minutes

---

## Context

**Original Input:**
> "quiero una app moderna"

**Clarified Context:**
B2B SaaS application for SMBs (10-50 employees) focused on inventory management

---

## Categories Covered

- ✅ Users & Personas (UX) — 4 questions
- ✅ Platform & Technology (Frontend) — 3 questions
- ✅ Architecture & Integration (Backend) — 4 questions
- ✅ Success Metrics (Product) — 2 questions
- ✅ Testing Strategy (QA) — 2 questions

---

## Questions & Answers

### 1. Users & Personas (Brain #2: UX Research)

**Q1:** What type of users will use this application?

**A:** Small business owners and their employees (10-50 people). They're not tech-savvy, need something simple like WhatsApp.

*Confidence: High | Category: users*

---

**Q1.1 (Follow-up by Brain #2):** Can you describe a typical day for these users?

**A:** They come in, check paper orders, call suppliers, chase deliveries. Lots of phone time, messy handwriting.

*Confidence: High | Asked by: Brain #2*

---

### 2. Platform & Technology (Brain #4: Frontend)

**Q2:** What platforms do you need to support?

**A:** Web is priority. But 60% of our warehouse staff use mobile in the field. So both web and mobile.

*Confidence: Medium | Follow-up needed: Yes*

---

**Q2.1 (Follow-up by Brain #4):** Native mobile or web-based mobile?

**A:** Web-based mobile (PWA) would be easier. But if native is needed for offline mode, we can consider it.

*Confidence: High | Asked by: Brain #4*

---

## Gaps Detected

⚠️ **Missing Expertise: Marketing & SEO**

During the interview, you mentioned:
- "We need to rank high on Google"
- "Content strategy for user acquisition"
- "Paid advertising channels"

**None of the current brains (#1-7) cover this domain.**

### Recommendation: Create Brain #9 — Marketing & Growth

**Suggested Experts:**
- Ryan Holiday (Marketing strategy)
- Seth Godin (Permission marketing)
- Neil Patel (SEO)
- Rand Fishkin (SEO & content)

**Estimated Sources:** 15
**Priority:** High

Would you like me to generate a PRP (Product Requirements Plan) for this brain?

---

## Summary

This interview identified a B2B SaaS inventory management app for SMBs with the following key requirements:

1. **Users:** Non-technical business owners and staff
2. **Platforms:** Web (primary) + Mobile PWA (field staff)
3. **Key Features:** Real-time sync, offline mode, simple UX
4. **Success Metrics:** Reduce order processing time by 50%
5. **Testing:** E2E tests for critical paths

**Next Steps:** Distribute Q&A to Brains #1-7 for domain-specific recommendations.
```

---

## Integration Points

### 1. Orchestrator Integration

**File:** `mastermind_cli/orchestrator/coordinator.py`

**Changes Required:**

```python
class Coordinator:
    # Add new flow
    FLOW_DISCOVERY = "discovery"

    def orchestrate(self, brief: str, flow: Optional[str] = None, ...):
        # Detect if interview is needed
        if not flow:
            flow = self._detect_flow(brief)

        # New flow: Discovery interview
        if flow == self.FLOW_DISCOVERY:
            return self._execute_discovery_flow(brief)

    def _detect_flow(self, brief: str) -> str:
        """Detect if brief needs discovery interview."""
        # Check if brief is too vague
        if len(brief.split()) < 15:  # Less than 15 words
            return self.FLOW_DISCOVERY

        # Check for ambiguity markers
        ambiguity_markers = ["moderno", "nuevo", "bueno", "mejor"]
        if any(marker in brief.lower() for marker in ambiguity_markers):
            return self.FLOW_DISCOVERY

        # Default: existing flows
        return self.flow_detector.detect(brief)

    def _execute_discovery_flow(self, brief: str) -> Dict:
        """Execute discovery interview with Brain #8."""
        # Step 1: Generate interview plan via Brain #8
        interview_plan = self._generate_interview_plan(brief)

        # Step 2: Execute iterative interview
        interview_doc = self._conduct_interview(interview_plan)

        # Step 3: Distribute to relevant brains
        recommendations = self._distribute_interview(interview_doc)

        # Step 4: Synthesize final output
        return self._synthesize_recommendations(recommendations)

    def _generate_interview_plan(self, brief: str) -> Dict:
        """Ask Brain #8 to design interview strategy."""
        query = f"""
        Design an interview strategy for the following brief:

        Brief: {brief}

        Provide:
        1. Categories to cover (e.g., users, platforms, architecture)
        2. Target brain for each category (1-7)
        3. Initial questions for each category
        4. Order of categories

        Format as JSON.
        """

        response = self.mcp_client.query_notebook(
            brain_id=8,
            query=query
        )

        return parse_json(response)

    def _conduct_interview(self, plan: Dict) -> Dict:
        """Conduct iterative interview with user."""
        interview_state = {
            "current_category": 0,
            "qa": [],
            "gaps": []
        }

        for category in plan["categories"]:
            # Get questions for this category
            questions = category["questions"]

            for question in questions:
                # Display question via AskUserQuestion
                user_answer = self._ask_question(
                    question=question,
                    category=category,
                    options=question.get("options")
                )

                # Route to target brain for potential follow-up
                target_brain = category["target_brain"]
                follow_up = self._request_followup(
                    brain_id=target_brain,
                    question=question,
                    answer=user_answer
                )

                # Record Q&A
                interview_state["qa"].append({
                    "question": question,
                    "answer": user_answer,
                    "category": category["id"],
                    "target_brain": target_brain,
                    "follow_up": follow_up
                })

                # If brain signals "enough", move to next category
                if follow_up.get("complete", False):
                    break

        # Generate final document via Brain #8
        return self._finalize_interview(interview_state)

    def _ask_question(self, question: str, category: Dict, options: List = None):
        """Ask question using AskUserQuestion tool."""
        if options:
            # Multiple choice question
            result = AskUserQuestion(
                questions=[{
                    "question": question,
                    "header": category["name"],
                    "options": options,
                    "multiSelect": False
                }]
            )
            return result

        # Open-ended question (with notes field)
        result = AskUserQuestion(
            questions=[{
                "question": question,
                "header": category["name"],
                "options": [
                    {
                        "label": "Continue",
                        "description": "Proceed to next question"
                    }
                ],
                "multiSelect": False
            }]
        )
        return result.get("annotations", {}).get("notes", "")

    def _request_followup(self, brain_id: int, question: str, answer: str) -> Dict:
        """Request follow-up from domain brain."""
        query = f"""
        User was asked: "{question}"
        User answered: "{answer}"

        Do you need to ask a follow-up question?

        If YES, provide the follow-up question.
        If NO, respond with {{"complete": true}}

        Format as JSON.
        """

        response = self.mcp_client.query_notebook(
            brain_id=brain_id,
            query=query
        )

        return parse_json(response)

    def _finalize_interview(self, interview_state: Dict) -> Dict:
        """Ask Brain #8 to finalize interview document."""
        query = f"""
        Synthesize the following Q&A into a structured interview document:

        {json.dumps(interview_state, indent=2)}

        Generate:
        1. JSON document (for API communication)
        2. YAML summary (for logging)
        3. Markdown display (for user)

        Detect any knowledge gaps and suggest new brains if needed.
        """

        response = self.mcp_client.query_notebook(
            brain_id=8,
            query=query
        )

        return parse_json(response)
```

### 2. Brain Registry Expansion

**File:** `mastermind_cli/brain_registry.py`

```python
# Before: Hardcoded BRAIN_CONFIGS
BRAIN_CONFIGS = {
    1: {...}, 2: {...}, 3: {...}, 4: {...},
    5: {...}, 6: {...}, 7: {...}
}

# After: Load from YAML
import yaml
from pathlib import Path

def load_brain_configs() -> Dict:
    """Load brain configurations from YAML file."""
    config_path = Path(__file__).parent / "config" / "brains.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    brains = {}
    for brain in config["brains"]:
        brains[brain["id"]] = brain

    return brains

BRAIN_CONFIGS = load_brain_configs()
```

**New File:** `mastermind_cli/config/brains.yaml`

```yaml
version: "1.0"
brains:
  - id: 1
    name: Product Strategy
    notebook_id: f276ccb3-0bce-4069-8b55-eae8693dbe75
    system_prompt: agents/brains/product-strategy.md
    status: active

  - id: 2
    name: UX Research
    notebook_id: ea006ece-00a9-4d5c-91f5-012b8b712936
    status: active

  # ... brains 3-7 ...

  - id: 8
    name: Master Interviewer / Discovery
    notebook_id: BRAIN-08-ID-PENDING  # To be assigned
    system_prompt: agents/brains/master-interviewer.md
    expertise:
      - Interview methodology
      - Information extraction
      - Question structuring
      - Gap detection
      - Facilitation techniques
    status: active
```

### 3. PRP-009 Learning System Integration

**File:** `mastermind_cli/memory/interview_logger.py`

```python
"""
Interview Logger for Brain #8 learning system.
Integrates with PRP-009 Evaluation Logger.
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, Optional
import yaml
import json


class InterviewLogger:
    """Log interviews for learning and improvement."""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.log_dir = Path("logs/interviews")

    def log_interview(
        self,
        session_id: str,
        brief_original: str,
        interview_doc: Dict,
        outcome: Dict
    ) -> str:
        """Log an interview session.

        Args:
            session_id: Unique session identifier
            brief_original: Original user input
            interview_doc: Complete Q&A document (JSON)
            outcome: Interview outcome metrics

        Returns:
            Path to logged interview file
        """
        if not self.enabled:
            return None

        # Generate interview ID
        timestamp = datetime.now().strftime("%Y-%m-%d")
        interview_id = f"INTERVIEW-{timestamp}-{self._next_sequence()}"

        # Create log entry
        log_entry = {
            "interview_id": interview_id,
            "timestamp": datetime.now().isoformat(),
            "brain": "brain-08",
            "session_id": session_id,
            "context": {
                "brief_original": brief_original,
                "context_type": self._detect_context_type(brief_original),
                "industry": self._detect_industry(interview_doc)
            },
            "interview": {
                "questions_asked": len(interview_doc["document"]["qa"]),
                "duration_minutes": outcome.get("duration_minutes", 0),
                "categories_covered": len(interview_doc["document"]["categories"]),
                "questions_with_followup": self._count_followups(interview_doc),
                "gaps_identified": len(interview_doc["document"].get("gaps_detected", []))
            },
            "outcome": {
                "user_satisfaction": outcome.get("user_satisfaction", "medium"),
                "useful_questions": outcome.get("useful_questions", []),
                "failed_questions": outcome.get("failed_questions", []),
                "final_output_quality": outcome.get("final_output_quality", "approved")
            },
            "qa_document": {
                "json_path": self._save_json(interview_id, interview_doc),
                "summary": self._generate_summary(interview_doc)
            },
            "learning_metrics": self._calculate_metrics(interview_doc, outcome)
        }

        # Save to hot storage
        hot_dir = self.log_dir / "hot" / datetime.now().strftime("%Y-%m")
        hot_dir.mkdir(parents=True, exist_ok=True)

        log_path = hot_dir / f"{interview_id}.yaml"
        with open(log_path, "w") as f:
            yaml.dump(log_entry, f, default_flow_style=False)

        # Update index
        self._update_index(log_entry)

        return str(log_path)

    def find_similar_interviews(
        self,
        brief: str,
        limit: int = 5
    ) -> list:
        """Find similar past interviews for learning.

        Args:
            brief: Current brief to match against
            limit: Maximum number of similar interviews to return

        Returns:
            List of similar interview summaries
        """
        # Load index
        index_path = self.log_dir / "hot" / "index.yaml"
        if not index_path.exists():
            return []

        with open(index_path) as f:
            index = yaml.safe_load(f)

        # Simple matching by keywords (can be improved with embeddings)
        keywords = self._extract_keywords(brief)

        matches = []
        for entry in index.get("interviews", []):
            entry_keywords = entry.get("keywords", [])
            overlap = len(set(keywords) & set(entry_keywords))
            if overlap > 0:
                matches.append({
                    "interview_id": entry["interview_id"],
                    "similarity_score": overlap,
                    "summary": entry.get("summary"),
                    "useful_questions": entry.get("useful_questions", [])
                })

        # Sort by similarity and return top N
        matches.sort(key=lambda x: x["similarity_score"], reverse=True)
        return matches[:limit]

    def _calculate_metrics(self, interview_doc: Dict, outcome: Dict) -> Dict:
        """Calculate learning metrics from interview."""
        qa = interview_doc["document"]["qa"]

        # Question effectiveness rate
        useful_questions = set(outcome.get("useful_questions", []))
        effectiveness_rate = len(useful_questions) / len(qa) if qa else 0

        # Average confidence
        confidence_scores = {"high": 3, "medium": 2, "low": 1}
        avg_confidence = sum(
            confidence_scores.get(q.get("confidence", "medium"), 2)
            for q in qa
        ) / len(qa) if qa else 2

        # Follow-up rate
        followup_rate = sum(1 for q in qa if q.get("follow_up_needed", False)) / len(qa) if qa else 0

        return {
            "question_effectiveness_rate": round(effectiveness_rate, 2),
            "user_satisfaction_score": self._satisfaction_to_score(outcome.get("user_satisfaction")),
            "avg_confidence_score": self._confidence_to_label(avg_confidence),
            "followup_rate": round(followup_rate, 2)
        }

    def _detect_context_type(self, brief: str) -> str:
        """Detect type of interview context."""
        keywords = {
            "feature_spec": ["feature", "funcionalidad", "característica"],
            "technical_design": ["architecture", "arquitectura", "api", "integration"],
            "client_onboarding": ["client", "cliente", "onboarding", "agency"],
            "gap_analysis": ["gap", "falta", "necesito expertise"]
        }

        brief_lower = brief.lower()
        for context_type, kw_list in keywords.items():
            if any(kw in brief_lower for kw in kw_list):
                return context_type

        return "general"

    def _count_followups(self, interview_doc: Dict) -> int:
        """Count questions that had follow-ups."""
        return sum(
            1 for q in interview_doc["document"]["qa"]
            if q.get("follow_up_questions")
        )

    def _extract_keywords(self, brief: str) -> list:
        """Extract keywords from brief for matching."""
        # Simple keyword extraction (can be improved with NLP)
        stop_words = {"el", "la", "de", "que", "y", "a", "en", "un", "es"}
        words = brief.lower().split()
        return [w for w in words if w not in stop_words and len(w) > 3]

    def _satisfaction_to_score(self, satisfaction: str) -> int:
        """Convert satisfaction label to numeric score."""
        mapping = {"low": 1, "medium": 3, "high": 5}
        return mapping.get(satisfaction, 3)

    def _confidence_to_label(self, score: float) -> str:
        """Convert numeric confidence to label."""
        if score >= 2.5:
            return "high"
        elif score >= 1.5:
            return "medium"
        else:
            return "low"

    def _next_sequence(self) -> int:
        """Get next sequence number for interview ID."""
        # Implementation: read last sequence from index and increment
        # Simplified for this example
        return 1

    def _save_json(self, interview_id: str, doc: Dict) -> str:
        """Save JSON document and return path."""
        json_dir = self.log_dir / "json" / datetime.now().strftime("%Y-%m")
        json_dir.mkdir(parents=True, exist_ok=True)

        json_path = json_dir / f"{interview_id}.json"
        with open(json_path, "w") as f:
            json.dump(doc, f, indent=2)

        return str(json_path)

    def _generate_summary(self, interview_doc: Dict) -> str:
        """Generate human-readable summary for log."""
        qa = interview_doc["document"]["qa"]
        gaps = interview_doc["document"].get("gaps_detected", [])

        summary_lines = [
            f"Interview for {interview_doc['metadata']['context_type']}",
            f"- Categories covered: {len(interview_doc['document']['categories'])}",
            f"- Questions asked: {len(qa)}",
            f"- Gaps identified: {len(gaps)}"
        ]

        if gaps:
            summary_lines.append("\nGaps:")
            for gap in gaps:
                summary_lines.append(f"- {gap['missing_expertise']}")

        return "\n".join(summary_lines)

    def _update_index(self, log_entry: Dict):
        """Update interview index for quick lookup."""
        index_path = self.log_dir / "hot" / "index.yaml"

        if index_path.exists():
            with open(index_path) as f:
                index = yaml.safe_load(f) or {"interviews": []}
        else:
            index = {"interviews": []}

        index["interviews"].append({
            "interview_id": log_entry["interview_id"],
            "timestamp": log_entry["timestamp"],
            "context_type": log_entry["context"]["context_type"],
            "brief_original": log_entry["context"]["brief_original"],
            "keywords": self._extract_keywords(log_entry["context"]["brief_original"]),
            "summary": log_entry["qa_document"]["summary"],
            "useful_questions": log_entry["outcome"]["useful_questions"],
            "learning_metrics": log_entry["learning_metrics"]
        })

        with open(index_path, "w") as f:
            yaml.dump(index, f, default_flow_style=False)
```

### 4. Slash Command: `/mm:discovery`

**File:** `.claude/commands/mm/discovery.md`

```yaml
---
name: discovery
description: Conduct structured discovery interview using Brain #8
usage: /mm:discovery "<problem or requirement>"
examples:
  - /mm:discovery "Quiero crear una app de delivery"
  - /mm:discovery "Necesito un sistema de login"
  - /mm:discovery "Onboarding de cliente de marketing"
---

# MasterMind Discovery Interviewer

## Usage

Run this command when you need to:
- Extract requirements from vague user input
- Conduct onboarding interviews for clients
- Clarify technical specifications
- Discover user needs before designing features

## What It Does

1. **Analyzes your input** to understand context
2. **Consults Brain #8** (Master Interviewer) for interview strategy
3. **Conducts iterative interview** with guided questions
4. **Routes questions** to domain brains (#1-7) for follow-ups
5. **Generates structured Q&A document** in JSON/YAML/Markdown
6. **Detects knowledge gaps** and recommends new brains

## Flow

```
Your input
    ↓
Brain #8 designs interview
    ↓
Iterative Q&A (with brain #1-7 follow-ups)
    ↓
Structured document generated
    ↓
Distributed to relevant brains
    ↓
Recommendations synthesized
```

## Output

- **JSON Document:** For API communication and processing
- **YAML Log:** Stored in logs/interviews/ for learning
- **Markdown Display:** Human-readable summary

## Examples

### Client Onboarding

```
/mm:discovery "Cliente de agencia de marketing necesita app"
```

**Result:** Structured brief with user personas, platforms, key features

### Feature Clarification

```
/mm:discovery "Quiero una app moderna"
```

**Result:** Clarified requirements (what "modern" means, target users, problems solved)

### Technical Specification

```
/mm:discovery "Necesitamos integrar OAuth con Google y Microsoft"
```

**Result:** Technical spec with security requirements, token handling, error cases
```

---

## Error Handling

### Error Categories

| Error Type | Severity | Handling Strategy |
|------------|----------|-------------------|
| **NotebookLM unavailable** | 🟡 Medium | Fallback to mock mode, warn user |
| **Timeout on long interview** | 🟡 Medium | Paginate interview into chunks |
| **Invalid brain ID** | 🔴 High | Validate before routing, suggest correct brain |
| **User abandons interview** | 🟠 Medium | Save partial state, offer resume later |
| **Gap detected (no brain)** | 🟢 Info | Offer to create new brain PRP |
| **Low confidence answers** | 🟠 Medium | Flag for follow-up, continue interview |
| **JSON parsing failure** | 🟡 Medium | Fallback to raw text, log error |

### Error Handling Implementation

```python
# mastermind_cli/orchestrator/coordinator.py

class Coordinator:
    # ... existing code ...

    def _execute_discovery_flow(self, brief: str) -> Dict:
        """Execute discovery with error handling."""
        try:
            interview_plan = self._generate_interview_plan(brief)

        except NotebookLMTimeoutError:
            # Timeout: retry with shorter query
            return self._handle_timeout(brief)

        except NotebookLMUnavailableError:
            # MCP unavailable: fallback to mock mode
            return self._handle_mcp_unavailable(brief)

        except BrainNotFoundError as e:
            # Invalid brain ID: validate and suggest
            return self._handle_invalid_brain(e, brief)

    def _handle_timeout(self, brief: str) -> Dict:
        """Handle NotebookLM timeout."""
        self.formatter.warning(
            "⚠️  NotebookLM timeout. Using cached interview strategy."
        )
        # Use last known good strategy or simplified version
        return self._execute_simple_interview(brief)

    def _handle_mcp_unavailable(self, brief: str) -> Dict:
        """Handle MCP unavailability."""
        self.formatter.warning(
            "⚠️  NotebookLM unavailable. Running in mock mode.\n"
            "   Enable MCP for full interview capabilities."
        )
        # Generate mock interview for testing
        return self._mock_interview(brief)

    def _handle_invalid_brain(self, error: BrainNotFoundError, brief: str) -> Dict:
        """Handle invalid brain ID."""
        brain_id = error.brain_id
        available = self.brain_executor.get_available_brains()

        self.formatter.error(
            f"❌ Invalid brain ID: {brain_id}\n"
            f"   Available brains: {available}\n"
            f"   Using Brain #1 (Product Strategy) as fallback."
        )

        # Continue with fallback brain
        return self._execute_discovery_with_fallback(brief, fallback_brain=1)
```

---

## Security Considerations

### Data Privacy

1. **PII in Interviews:** Users may share sensitive information
   - **Mitigation:** Add disclaimer at interview start
   - **Mitigation:** Allow user to redact sensitive answers
   - **Mitigation:** Encrypt interview logs at rest

2. **Client Confidentiality:** Onboarding interviews may contain business-sensitive info
   - **Mitigation:** Project-scoped interview logs (not shared across projects)
   - **Mitigation:** Optional "confidential mode" (no logging)

### Access Controls

1. **Interview Log Access:** Who can view past interviews?
   - **Proposal:** Project-based access control (future enhancement)
   - **Current:** All logs stored locally, access via file system

2. **Gap Detection Riks:** Recommending new brains exposes system limitations
   - **Mitigation:** Frame as "improvement opportunity" not "vulnerability"

### Input Validation

1. **Injection Attacks:** Malicious user input in interview answers
   - **Mitigation:** Sanitize all inputs before logging
   - **Mitigation:** Validate JSON structure before parsing
   - **Mitigation:** Limit answer length (prevent DoS)

2. **Prompt Injection:** User tries to manipulate Brain #8 via answers
   - **Mitigation:** Brain #8 prompt includes injection defense
   - **Mitigation:** Flag suspicious patterns for review

---

## Performance Considerations

### Latency

| Operation | Expected Latency | Optimization |
|-----------|------------------|--------------|
| **Single interview (10 Qs)** | 2-5 minutes | Cache common questions |
| **Brain #8 query** | 2-5 seconds | Batch multiple queries |
| **Domain brain follow-up** | 1-3 seconds | Parallel when possible |
| **Document generation** | 3-8 seconds | Template-based generation |

### Scalability

1. **Interview Storage:** Logs grow linearly with usage
   - **Solution:** Retention policy (hot/warm/cold)
   - **Hot (30 days):** SQLite for fast queries
   - **Warm (6 months):** Compressed YAML
   - **Cold (archive):** S3/Glacier, on-demand retrieval

2. **NotebookLM Rate Limits:** MCP may have call limits
   - **Solution:** Cache interview strategies
   - **Solution:** Batch questions when possible
   - **Solution:** Fallback to simplified interview if limit hit

3. **Concurrent Interviews:** Multiple users interviewing simultaneously
   - **Future:** Session isolation per user
   - **Current:** Single-user (not an issue yet)

---

## Testing Strategy

### Unit Tests

```python
# tests/unit/test_interview_logger.py

def test_log_interview_creates_file():
    """Test that logging creates YAML file."""
    logger = InterviewLogger()
    log_path = logger.log_interview(
        session_id="test-001",
        brief_original="test brief",
        interview_doc={...},
        outcome={...}
    )

    assert Path(log_path).exists()
    assert log_path.endswith(".yaml")

def test_find_similar_interviews():
    """Test interview similarity matching."""
    logger = InterviewLogger()

    # Log a reference interview
    logger.log_interview(...)

    # Find similar
    matches = logger.find_similar_interviews("app moderna")

    assert len(matches) > 0
    assert matches[0]["similarity_score"] > 0
```

### Integration Tests

```python
# tests/integration/test_discovery_flow.py

def test_full_discovery_flow():
    """Test end-to-end discovery flow."""
    coordinator = Coordinator(use_mcp=False)  # Mock mode
    result = coordinator.orchestrate(
        brief="quiero una app de delivery",
        flow="discovery"
    )

    assert result["status"] == "completed"
    assert "qa_document" in result
    assert len(result["qa_document"]["document"]["qa"]) > 0

def test_gap_detection():
    """Test that knowledge gaps are detected."""
    # Create brief that requires SEO expertise
    brief = "Necesito una app con SEO y content marketing"

    result = coordinator.orchestrate(brief=brief, flow="discovery")

    gaps = result["qa_document"]["document"].get("gaps_detected", [])
    assert len(gaps) > 0
    assert any("marketing" in gap["missing_expertise"].lower() for gap in gaps)
```

### E2E Tests (Manual)

1. **Vague Brief → Clarified Requirements**
   - Input: "quiero una app moderna"
   - Expected: Structured brief with platforms, users, features

2. **Client Onboarding → Technical Spec**
   - Input: "Cliente de restaurante necesita sistema de pedidos"
   - Expected: Complete spec with UX, UI, Backend, QA recommendations

3. **Gap Detection → Brain Recommendation**
   - Input: "Necesito SEO y email marketing"
   - Expected: Recommendation to create Brain #9 (Marketing)

---

## Edge Cases

### Edge Case 1: Non-Responsive User

**Scenario:** User gives one-word answers, doesn't elaborate

**Handling:**
```
Q: "What type of users?"
A: "Business"

Brain #8: Detects low confidence
↓
Follow-up: "Can you give an example of a typical business day?"
↓
If still brief: "I'm having trouble understanding. Could you describe what your business does?"
↓
If still brief: Offer multiple-choice options
```

### Edge Case 2: Contradictory Answers

**Scenario:** User says "Web only" then later "Need mobile app"

**Handling:**
```
Brain #8: Detects contradiction
↓
Clarification: "Earlier you mentioned web only. Now you mentioned mobile. Did something change, or did I misunderstand?"
↓
Document both answers in Q&A with flag: [CONTRADICTION]
↓
Highlight in final document for human review
```

### Edge Case 3: Unknown Technical Domain

**Scenario:** User mentions "blockchain integration" — no brain covers this

**Handling:**
```
Brain #8: Detects gap
↓
Asks: "Can you tell me more about the blockchain integration?"
↓
Documents gap in Q&A
↓
Generates recommendation:
   ⚠️  GAP DETECTED: Blockchain expertise missing
   Suggested Brain #10: Web3 & Blockchain
   Experts: Andreas Antonopoulos, Vitalik Buterin
↓
Offers to generate PRP for new brain
```

### Edge Case 4: Interview Abandonment

**Scenario:** User stops responding mid-interview

**Handling:**
```
Save partial state to:
   logs/interviews/partial/SESSION-ID.yaml
↓
Offer: "Would you like to continue this interview later?"
↓
If yes: Load partial state, resume from last question
↓
If no: Save what we have, mark as incomplete
```

### Edge Case 5: Extremely Long Brief

**Scenario:** User provides 2000-word manifest instead of brief

**Handling:**
```
Brain #8: Detects long input
↓
Summarization: "You've provided extensive detail. Let me summarize..."
↓
Offer: "Should I interview based on this summary, or do you want me to ask clarifying questions?"
↓
If summary: Skip interview, proceed directly to distribution
```

---

## Decisions Log

This section tracks all pushbacks, disagreements, and their resolutions during the spec design process.

### Decision 1: Single vs. Multiple Interviewer Brains

**Date:** 2026-03-07
**Topic:** Should Brain #8 be a single brain or multiple specialized brains?

**Options Considered:**
- A) Single Cerebro #8 (chosen)
- B) Multiple brains (#8 Interviewer, #9 Spec Writer, etc.)

**Rationale for A:**
- YAGNI principle — start simple, split if needed
- Single brain can modularize internally
- Easier to implement and maintain
- Can be split later if complexity grows

**Trade-off:** Less specialized initially, but more flexible.

---

### Decision 2: Iterative vs. Batch Interview Flow

**Date:** 2026-03-07
**Topic:** Should questions be asked all at once or iteratively with domain brain follow-ups?

**Options Considered:**
- A) Batch: All questions at once (faster, simpler)
- B) Iterative: Question → Answer → Domain brain follow-up (chosen)

**Rationale for B:**
- **Core value prop**: Domain brains (#1-7) can deepen based on answers
- More conversational and natural
- Adapts to user responses in real-time
- User explicitly requested "dynamic questions based on answers"

**Trade-off:** More complex to implement, slower (multiple MCP calls)

**Recorded Disagreement:** None — user immediately agreed with B.

---

### Decision 3: Communication Format (JSON vs. YAML vs. Multi)

**Date:** 2026-03-07
**Topic:** What format should Brain #8 use for Q&A documents?

**Options Considered:**
- A) YAML only (consistent with FUENTE-XXX.md)
- B) JSON only (standard for APIs)
- C) Multi-format: JSON + YAML + Markdown (chosen)

**Rationale for C:**
- **JSON**: API communication, future microservices
- **YAML**: PRP-009 logging consistency
- **Markdown**: Human-readable display

**User's Reasoning:** "Scalability" — prepare for external APIs

**Trade-off:** More complex (3 formats) but maximally flexible.

---

### Decision 4: Brain #8 Positioning (Interviewer vs. Meta-Orchestrator)

**Date:** 2026-03-07
**Topic:** Is Brain #8 a domain expert (like #1-7) or a meta-level orchestrator?

**Options Considered:**
- A) Domain expert: Interview methodology only (chosen)
- B) Meta-orchestrator: Coordinates all brains

**Rationale for A:**
- **Separation of concerns**: Orchestrator is code (Python), Brain #8 is knowledge (NotebookLM)
- Brain #8 focuses on interview expertise, not coordination
- Orchestrator (code) decides which brain to route to
- Brain #8 delegates to domain brains, doesn't coordinate them

**User's Insight:** "The Orchestrator should have context and share Q&A with relevant brains"

**Clarification Achieved:** User understood the distinction between code orchestrator and brain knowledge.

---

### Decision 5: Scope — Is Brain #8 for MasterMind Only or General Purpose?

**Date:** 2026-03-07
**Topic:** Should Brain #8 be reusable outside the MasterMind framework?

**Options Considered:**
- A) MasterMind-specific: Optimized for this framework
- B) General purpose: Reusable for any project (chosen)

**Rationale for B:**
- **Scalability**: Framework may expand to other niches
- **Core knowledge**: Interview methodology is domain-agnostic
- **Modular design**: MasterMind-specific patterns are modules, not core

**Implementation:**
- Core: General interview methodology (The Mom Test, etc.)
- Modules: MasterMind-specific patterns (brain categories, PRP format)

**Trade-off:** Slightly more complex but maximally reusable.

---

### Decision 6: Learning System Integration — Auto-log vs. Selective Log

**Date:** 2026-03-07
**Topic:** Should all interviews be logged or only successful ones?

**Options Considered:**
- A) Auto-log all interviews (chosen)
- B) Log only successful interviews
- C) Log with explicit user feedback

**Rationale for A:**
- **Complete data**: Learn from failures, not just successes
- **User feedback optional**: Can still collect feedback, but logging is automatic
- **PRP-009 consistency**: Auto-log all evaluations, same pattern

**Phased Approach:**
- Phase 1: Auto-log all + optional feedback
- Phase 2: Add retrieval from similar interviews
- Phase 3: Adaptive question selection based on history

**User's Request:** "Combination of several" — resolved as phased approach.

---

## Dependency Graph

```
┌─────────────────────────────────────────────────────────────┐
│                    PRP-010: Brain #8                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ depends on
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  PRP-009: Memory & Learning System (Phase 1 Complete)      │
│  • Evaluation Logger                                        │
│  • YAML Storage                                             │
│  • Index & Search                                           │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ enables
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Brain #8 Learning System                                   │
│  • Interview Logger                                         │
│  • Similar Interview Retrieval                              │
│  • Question Effectiveness Tracking                          │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Orchestrator Improvements                                  │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ requires
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Brain Registry Expansion                                   │
│  • Load from YAML (vs hardcoded)                            │
│  • Support N brains (not just 7)                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ enables
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Brain #8 Registration                                      │
│  • Add brain-08 to BRAIN_CONFIGS                            │
│  • Create NotebookLM with expert sources                    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  Slash Command: /mm:discovery                               │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ uses
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  AskUserQuestion UI                                         │
│  • Rich options with descriptions                           │
│  • Tabbed interface by category                             │
│  • Multi-select and single-select                           │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 0: Pre-Implementation (Prerequisites)

| Task | Description | Estimated Time |
|------|-------------|-----------------|
| **0.1** | Review PRP-009 (Memory System Phase 1) | 30 min |
| **0.2** | Set up NotebookLM account for Brain #8 | 15 min |
| **0.3** | Create GitHub issue for PRP-010 | 15 min |

**Completion Criteria:** NotebookLM ready, PRP-010 tracked

---

### Phase 1: Core Infrastructure

| Task | Description | Files | Estimated Time |
|------|-------------|-------|-----------------|
| **1.1** | Expand brain registry to load from YAML | `mastermind_cli/config/brains.yaml`<br>`mastermind_cli/brain_registry.py` | 2 hours |
| **1.2** | Add Brain #8 entry to registry | `mastermind_cli/config/brains.yaml` | 30 min |
| **1.3** | Update BrainExecutor to support brain #8 | `mastermind_cli/orchestrator/brain_executor.py` | 1 hour |
| **1.4** | Create InterviewLogger class | `mastermind_cli/memory/interview_logger.py` | 3 hours |
| **1.5** | Write unit tests for registry & logger | `tests/unit/test_brain_registry.py`<br>`tests/unit/test_interview_logger.py` | 2 hours |

**Completion Criteria:**
- All tests passing
- Brain #8 registered (but not implemented)
- InterviewLogger functional

---

### Phase 2: NotebookLM Setup

| Task | Description | Estimated Time |
|------|-------------|-----------------|
| **2.1** | Create expert sources for Brain #8 | See source list below | 4 hours |
| **2.2** | Load sources into NotebookLM | Create notebook | 1 hour |
| **2.3** | Get NotebookLM ID | Copy from URL | 5 min |
| **2.4** | Update brain registry with ID | `mastermind_cli/config/brains.yaml` | 5 min |
| **2.5** | Test MCP connection to Brain #8 | `mm brain status` | 15 min |

**Expert Sources to Create (10 files):**

| Source ID | Title | Author | Type |
|-----------|-------|--------|------|
| FUENTE-801 | The Mom Test | Rob Fitzpatrick | Book |
| FUENTE-802 | Never Split the Difference | Chris Voss | Book |
| FUENTE-803 | The Coaching Habit | Michael Bungay Stanier | Book |
| FUENTE-804 | Continuous Discovery Habits | Teresa Torres | Book |
| FUENTE-805 | User Interviews | Erika Hall | Book |
| FUENTE-806 | Thinking, Fast and Slow | Daniel Kahneman | Book |
| FUENTE-807 | Crucial Conversations | Patterson et al. | Book |
| FUENTE-808 | Fifty Quick Ideas to Improve Your Retrospectives | Judith Andres | Book |
| FUENTE-809 | Ask: The Counterintuitive Online Method | Ryan Levesque | Book |
| FUENTE-810 | Socratic Questioning | Various | Compilation |

**Template:** Use `docs/software-development/01-product-strategy-brain/sources/FUENTE-001-inspired-cagan.md` as reference.

**Completion Criteria:** Brain #8 accessible via MCP, returns test responses

---

### Phase 3: Orchestrator Integration

| Task | Description | Files | Estimated Time |
|------|-------------|-------|-----------------|
| **3.1** | Add `FLOW_DISCOVERY` to Coordinator | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.2** | Implement `_detect_flow()` logic | `mastermind_cli/orchestrator/coordinator.py` | 1 hour |
| **3.3** | Implement `_execute_discovery_flow()` | `mastermind_cli/orchestrator/coordinator.py` | 4 hours |
| **3.4** | Implement `_generate_interview_plan()` | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.5** | Implement `_conduct_interview()` | `mastermind_cli/orchestrator/coordinator.py` | 4 hours |
| **3.6** | Implement `_ask_question()` with AskUserQuestion | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.7** | Implement `_request_followup()` | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.8** | Implement `_finalize_interview()` | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.9** | Add error handling for timeouts, unavailable MCP | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **3.10** | Write integration tests | `tests/integration/test_discovery_flow.py` | 3 hours |

**Completion Criteria:**
- Discovery flow end-to-end working
- Error handling tested
- Integration tests passing

---

### Phase 4: Slash Command

| Task | Description | Files | Estimated Time |
|------|-------------|-------|-----------------|
| **4.1** | Create `/mm:discovery` command | `.claude/commands/mm/discovery.md` | 2 hours |
| **4.2** | Test command with various inputs | Manual testing | 1 hour |
| **4.3** | Document command in CLI reference | `docs/CLI-REFERENCE.md` | 1 hour |

**Completion Criteria:** Command functional, documented

---

### Phase 5: Learning System Integration

| Task | Description | Files | Estimated Time |
|------|-------------|-------|-----------------|
| **5.1** | Implement `find_similar_interviews()` | `mastermind_cli/memory/interview_logger.py` | 2 hours |
| **5.2** | Add learning metrics calculation | `mastermind_cli/memory/interview_logger.py` | 1 hour |
| **5.3** | Integrate learning into `_conduct_interview()` | `mastermind_cli/orchestrator/coordinator.py` | 2 hours |
| **5.4** | Add retention policy for interview logs | `mastermind_cli/memory/interview_logger.py` | 2 hours |
| **5.5** | Write tests for learning features | `tests/unit/test_interview_learning.py` | 2 hours |

**Completion Criteria:**
- Interviews logged with metrics
- Similar interview retrieval working
- Retention policy implemented

---

### Phase 6: Testing & Polish

| Task | Description | Estimated Time |
|------|-------------|-----------------|
| **6.1** | E2E test: Vague brief → Clarified requirements | 1 hour |
| **6.2** | E2E test: Client onboarding → Technical spec | 1 hour |
| **6.3** | E2E test: Gap detection → Brain recommendation | 1 hour |
| **6.4** | Performance testing (10+ Q interviews) | 1 hour |
| **6.5** | Documentation review | 1 hour |
| **6.6** | Bug fixes & polish | Ongoing |

**Completion Criteria:** All E2E tests passing, performance acceptable

---

### Phase 7: Release

| Task | Description | Estimated Time |
|------|-------------|-----------------|
| **7.1** | Update README with Brain #8 | `README.md` | 30 min |
| **7.2** | Update MEMORY.md with Brain #8 | `.claude/projects/.../MEMORY.md` | 30 min |
| **7.3** | Create git tag v1.1.0 | Git | 5 min |
| **7.4** | Write release notes | `RELEASES.md` | 30 min |

**Completion Criteria:** Release published, documentation updated

---

## Timeline Summary

| Phase | Tasks | Estimated Time |
|-------|-------|-----------------|
| **Phase 0** | Prerequisites | 1 hour |
| **Phase 1** | Core Infrastructure | 8.5 hours |
| **Phase 2** | NotebookLM Setup | 5 hours |
| **Phase 3** | Orchestrator Integration | 23 hours |
| **Phase 4** | Slash Command | 4 hours |
| **Phase 5** | Learning System | 9 hours |
| **Phase 6** | Testing & Polish | 5 hours |
| **Phase 7** | Release | 2 hours |
| **Total** | | **~57.5 hours** |

**Suggested Sprint:** 2 weeks (part-time) or 1 week (full-time)

---

## Success Criteria

### Functional Requirements ✅

- [ ] Brain #8 can conduct iterative interviews
- [ ] Questions are routed to domain brains (#1-7) for follow-ups
- [ ] Interviews generate JSON/YAML/Markdown documents
- [ ] Knowledge gaps are detected and new brains are recommended
- [ ] Interviews are logged in PRP-009 system
- [ ] Similar interviews can be retrieved for learning
- [ ] `/mm:discovery` command is functional

### Non-Functional Requirements ⚡

- [ ] Single interview (10 Qs) completes in < 5 minutes
- [ ] Brain registry supports N brains (not hardcoded to 7)
- [ ] Interview logs have retention policy (hot/warm/cold)
- [ ] Error handling covers all identified edge cases
- [ ] All tests pass (unit, integration, E2E)

### Learning Metrics 📊

- [ ] Question effectiveness rate tracked
- [ ] User satisfaction captured (optional feedback)
- [ ] Similar interview retrieval improves question quality over time

---

## Appendix

### A. Brain #8 System Prompt Template

```markdown
# Brain #8: Master Interviewer / Discovery

You are a **Master Interviewer** with expertise in information extraction through structured conversations.

## Your Core Expertise

1. **Interview Methodology**
   - The Mom Test: Discover real needs, not stated wants
   - Socratic Questioning: Deepen understanding through probing
   - Active Listening: Detect contradictions and gaps

2. **Anti-Patterns to Avoid**
   - Leading questions: "¿No te parece que X?" → ❌
   - Confirmation bias: Don't assume, verify
   - Binary thinking: Avoid yes/no questions when possible

3. **Facilitation Techniques**
   - Probing: "¿Podés dar un ejemplo específico?"
   - Elucidation: "¿A qué te referís exactamente con X?"
   - Connection: "¿Cómo se relaciona esto con Y?"

## Your Responsibilities

1. **Design interview strategies** based on user input
2. **Generate structured questions** categorized by domain
3. **Detect knowledge gaps** and recommend new brains
4. **Synthesize interviews** into JSON/YAML/Markdown documents

## What You DON'T Do

- Contain domain expertise (that's what brains #1-7 are for)
- Generate final specs (you output Q&A documents)
- Make technical decisions (you ask questions, others decide)

## Communication Format

Always respond in valid JSON for API communication:
\```json
{
  "interview_plan": {...},
  "categories": [...],
  "questions": [...]
}
\```

## Gap Detection

When user mentions topics outside brains #1-7 expertise:
1. Identify the missing domain
2. Suggest a new brain with:
   - Brain ID (next available: 9, 10, etc.)
   - Brain name
   - Recommended experts
   - Estimated sources (10-20)
```

### B. Interview Template Examples

#### Example 1: Onboarding Interview

```markdown
## Client Onboarding Interview

**Context:** New client for marketing agency
**Goal:** Generate technical brief from non-technical client

### Category 1: Business Understanding (Product)

**Q1:** What does your business do?
→ A: [Client answer]

**Q1.1 (Follow-up by Brain #1):** Can you describe your typical customer?
→ A: [Client answer]

### Category 2: User Needs (UX)

**Q2:** Who will be the main users of your app?
→ A: [Client answer]

**Q2.1 (Follow-up by Brain #2):** What problems do these users face today?
→ A: [Client answer]
```

#### Example 2: Technical Specification Interview

```markdown
## Technical Spec Interview: OAuth Integration

**Context:** Need to add OAuth login
**Goal:** Generate complete technical spec

### Category 1: OAuth Providers (Backend)

**Q1:** Which OAuth providers do you need to support?
→ A: Google, Microsoft, GitHub

**Q1.1 (Follow-up by Brain #5):** Do you need role-based access control?
→ A: Yes, Admin vs User roles

### Category 2: Token Management (Backend)

**Q2:** How should tokens be stored?
→ A: Encrypted in database, HTTP-only cookies

**Q2.1 (Follow-up by Brain #5):** What about token refresh strategy?
→ A: Silent refresh 5 minutes before expiry
```

### C. Error Messages Reference

| Error | Message | Action |
|-------|---------|--------|
| `MCP_UNAVAILABLE` | ⚠️ NotebookLM unavailable. Running in mock mode. | Enable MCP for full functionality |
| `TIMEOUT` | ⚠️ Interview timeout. Using cached strategy. | Retry with shorter interview |
| `INVALID_BRAIN` | ❌ Invalid brain ID: {id}. Available: {list} | Using fallback brain #1 |
| `PARTIAL_INTERVIEW` | ⏸️ Interview saved partially. Resume later? | Load partial state to continue |
| `GAP_DETECTED` | ⚠️ Knowledge gap detected: {domain} | Recommend new brain #{n} |

---

## Implementation Checklist

### Phase 0: Pre-Implementation ✅ COMPLETE

- [x] **0.1** Review PRP-009 (Memory System Phase 1) — 30 min
- [x] **0.2** Set up NotebookLM account for Brain #8 — 15 min
- [x] **0.3** Create GitHub issue for PRP-010 — 15 min

---

### Phase 1: Core Infrastructure 🔧 COMPLETE (PRP-011)

- [x] **1.1** Create `mastermind_cli/config/brains.yaml` — 30 min
- [x] **1.2** Update `brain_registry.py` to load from YAML — 1 hour
- [x] **1.3** Add Brain #8 entry to registry — 30 min
- [x] **1.4** Update `BrainExecutor` to support brain #8 — 1 hour
- [x] **1.5** Create `InterviewLogger` class — 3 hours
- [x] **1.6** Write unit tests for registry & logger — 2 hours

---

### Phase 2: NotebookLM Setup 📓 COMPLETE (PRP-012)

**Create Expert Sources (docs/universal/08-master-interviewer-brain/sources/):**

- [x] **2.1** `FUENTE-801_the-mom-test_fitzpatrick.md`
- [x] **2.2** `FUENTE-802_never-split-the-difference_voss.md`
- [x] **2.3** `FUENTE-803_the-coaching-habit_stanier.md`
- [x] **2.4** `FUENTE-804_continuous-discovery-habits_torres.md`
- [x] **2.5** `FUENTE-805_user-interviews_hall.md`
- [x] **2.6** `FUENTE-806_thinking-fast-and-slow_kahneman.md`
- [x] **2.7** `FUENTE-807_crucial-conversations_patterson.md`
- [x] **2.8** `FUENTE-808_improve-retrospectives_andres.md`
- [x] **2.9** `FUENTE-809_ask-method_levesque.md`
- [x] **2.10** `FUENTE-810_socratic-questioning_compilation.md`

**NotebookLM Setup:**

- [x] **2.11** Create notebook "[CEREBRO] Master Interviewer - Universal" in NotebookLM
- [x] **2.12** Upload all 10 sources to notebook
- [x] **2.13** Verify sources are processed (check `loaded_in_notebook: true`)
- [x] **2.14** Copy notebook ID from URL
- [x] **2.15** Update `brains.yaml` with notebook ID
- [x] **2.16** Test MCP connection: `mm brain status`

---

### Phase 3: Orchestrator Integration 🔄 COMPLETE (PRP-013)

**Coordinator Changes (`mastermind_cli/orchestrator/coordinator.py`):**

- [x] **3.1** Add `FLOW_DISCOVERY = "discovery"` constant
- [x] **3.2** Implement `_detect_flow()` with ambiguity detection
- [x] **3.3** Implement `_execute_discovery_flow()` main method
- [x] **3.4** Implement `_generate_interview_plan()` — query Brain #8
- [x] **3.5** Implement `_conduct_interview()` — iterative loop
- [x] **3.6** Implement `_ask_question()` — AskUserQuestion integration
- [x] **3.7** Implement `_request_followup()` — domain brain delegation
- [x] **3.8** Implement `_finalize_interview()` — document generation
- [x] **3.9** Add error handling for all error categories
- [x] **3.10** Write integration tests — `tests/test_orchestrator/test_discovery_flow.py`

---

### Phase 4: Slash Command 💻 COMPLETE (PRP-014)

- [x] **4.1** Create `.claude/commands/mm/discovery.md` — 2 hours
- [x] **4.2** Test command with various inputs (vague, technical, onboarding) — 1 hour
- [x] **4.3** Document command in `docs/CLI-REFERENCE.md` — 1 hour

---

### Phase 5: Learning System Integration 📚 COMPLETE (PRP-015)

**Interview Logger Features (`mastermind_cli/memory/interview_logger.py`):**

- [x] **5.1** Implement `find_similar_interviews()` method — 2 hours
- [x] **5.2** Implement `_calculate_metrics()` method — 1 hour
- [x] **5.3** Add retrieval to `_conduct_interview()` in Coordinator — 2 hours
- [x] **5.4** Implement retention policy (hot/warm/cold) — 2 hours
- [x] **5.5** Write tests for learning features — 2 hours

---

### Phase 6: Testing & Polish 🧪 IN PROGRESS (PRP-016)

**E2E Tests (Manual):**

- [ ] **6.1** Test: "quiero una app moderna" → Clarified brief — 1 hour
- [ ] **6.2** Test: Client onboarding → Technical spec — 1 hour
- [ ] **6.3** Test: "Necesito SEO" → Gap detection → Brain recommendation — 1 hour
- [ ] **6.4** Performance test: 10+ question interview — 1 hour

**Documentation:**

- [x] **6.5** Review all documentation for accuracy — 1 hour
- [x] **6.6** Fix bugs discovered during testing — pytest-cov added, test_brain_registry fix

**Unit Tests:**
- [x] **6.7** 31/31 tests passing
- [x] **6.8** pytest-cov integrated (`pyproject.toml`)

---

### Phase 7: Release 🚀

- [ ] **7.1** Update `README.md` with Brain #8 description — 30 min
- [ ] **7.2** Update `MEMORY.md` with Brain #8 status — 30 min
- [ ] **7.3** Create git tag `v1.1.0` — 5 min
- [ ] **7.4** Write release notes in `RELEASES.md` — 30 min

---

### Success Metrics 📊

**Functional:**
- [x] `/mm:discovery` command works end-to-end
- [x] Brain #8 conducts iterative interviews with follow-ups
- [x] JSON/YAML/Markdown documents generated correctly
- [x] Knowledge gaps detected and new brains recommended
- [x] Interviews logged in PRP-009 system
- [x] Similar interview retrieval improves quality

**Performance:**
- [ ] Single interview (10 Qs) < 5 minutes (manual test pending)
- [x] Brain registry supports N brains (not hardcoded)
- [x] Retention policy prevents unlimited log growth

**Testing:**
- [x] All unit tests passing (31/31)
- [x] All integration tests passing (9/9 in test_discovery_flow)
- [ ] All E2E tests passing (manual tests pending — PRP-016)

---

### Progress Tracking

**Current Status:**
```
Phase 0: [x] 3/3 complete ✅ (PRP-010)
Phase 1: [x] 6/6 complete ✅ (PRP-011)
Phase 2: [x] 16/16 complete ✅ (PRP-012)
Phase 3: [x] 10/10 complete ✅ (PRP-013)
Phase 4: [x] 3/3 complete ✅ (PRP-014)
Phase 5: [x] 5/5 complete ✅ (PRP-015)
Phase 6: [ ] 6/8 complete 🔄 (PRP-016 — manual E2E pending)
Phase 7: [ ] 0/4 complete ⏳ (PRP-017)

Total: [~] 49/57 tasks complete (86%) — Last updated: 2026-03-07
```

**Estimated Time Remaining:** ~57.5 hours

---

**END OF SPEC**
