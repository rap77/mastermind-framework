# Phase 07 Testing Patterns & Lessons

## Lesson: Mock Data Must Match Real Data Contracts
**Pattern:** Test fixtures (MOCK_COMPONENT_BRAINS) must have identical structure to real API responses.

**Incident:** MOCK_COMPONENT_BRAINS lacked marketing brains (niche='marketing-digital'). Real BentoGrid filtered 0 marketing brains because cluster niche comparison failed.

**Fix:** Added marketing brains to fixture:
```typescript
export const MOCK_COMPONENT_BRAINS = [
  // ...existing
  { id: 'brain-09', niche: 'marketing-digital', ... },
  { id: 'brain-10', niche: 'marketing-digital', ... },
]
```

**How to apply:** After fixing a component test, verify:
1. Does fixture have ALL clusters represented?
2. Do fixture niches match CLUSTER_CONFIGS exactly?
3. Test all clusters render before merging.

## Lesson: Component Layer vs API Layer Tests Have Different Import Sources
**Pattern:** Component tests (testing-library) import from different locations than API layer.

**Incident:** BentoGrid/ClusterGroup tests imported `Brain` type from `@/types/api` (doesn't exist). Real code imports from `@/lib/api`.

**Fix:** Updated imports:
```typescript
// ❌ WRONG
import type { Brain } from '@/types/api'

// ✅ CORRECT
import type { Brain } from '@/lib/api'
```

**How to apply:** When fixing component test imports:
- Component layer types: `@/lib/api`
- API route types: `@/types/api` or route-specific types
- Server Action types: from `'use server'` action files

## Lesson: Server Action Tests Must Import from Action File, Not Route Handler
**Pattern:** Server Actions are in separate files (app/actions/*.ts), not in route handlers (app/api/*/route.ts).

**Incident:** createTask tests imported from `../route` (the POST handler), which only exports the handler function, not createTask.

**Fix:** Updated import path:
```typescript
// ❌ WRONG
import { createTask } from '../route'  // Route handler, not action

// ✅ CORRECT
import { createTask } from '@/app/actions/tasks'  // Server Action file
```

**How to apply:** For Server Action tests:
1. Verify the action has `'use server'` directive
2. Import from `app/actions/` directory
3. Never import from route handlers

## Lesson: XSS Sanitization Must Remove Content, Not Just Tags
**Pattern:** stripHtml regex must remove both tag syntax AND tag content.

**Incident:** `stripHtml` regex `/<[^>]*>/g` removed `<script>` tags but left content. Input `<script>alert("XSS")</script>...` became `alert("XSS")...`

**Fix:** Two-pass sanitization:
```typescript
export function stripHtml(html: string): string {
  // Pass 1: Remove full script blocks
  let result = html.replace(/<script[^>]*>.*?<\/script>/gi, '')

  // Pass 2: Remove remaining tags
  result = result.replace(/<[^>]*>/g, '')

  return result
}
```

**How to apply:** For HTML sanitization:
1. Remove dangerous block elements first (script, iframe, etc.)
2. Then remove all remaining tags
3. Test with XSS payloads: `<script>alert(1)</script>`, `<img onerror=alert(1)>`, etc.

## Lesson: Wave Execution Model Requires Full Wave Completion Before Proceeding
**Pattern:** Each wave establishes foundation for next wave. Don't split waves across sessions.

**Evidence:** Wave 1 (07-01) established graph contract. Wave 2 (07-02) built frontend canvas consuming that contract. Wave 3 (07-03) illuminates Wave 2 structure with WS events.

**How to apply:** For future phases:
- Complete full wave before pausing session
- If mid-wave: checkpoint with `<next_action>` that resumes wave
- Don't start next wave until prior wave verified (testing or human checkpoint)

## Lesson: Context Limits Don't Scale to Wave 3 Task 3
**Pattern:** Task 3 (integration testing + visual verification) is heavy. Don't execute Tasks 1-2-3 in same session.

**Evidence:** Session reached 86% context after Wave 3 Tasks 1-2. Task 3 (full integration test + visual checks) would hit limit mid-execution.

**How to apply:** For large phases:
- Execute Tasks 1-2 (infrastructure)
- Checkpoint with clear `<next_action>` for Task 3
- Next session: fresh context for Task 3 integration & testing

## Test Coverage Strategy for Phase 07
1. **Unit tests** (components): node rendering, selector logic, prop handling
2. **Integration tests** (brainStore + HybridFlowEdge): state transitions, WS event handling
3. **E2E / Visual tests** (human checkpoint): animations, glow effects, Cooldown Mode behavior

Why three levels:
- Unit tests catch regressions quickly (fast CI)
- Integration tests verify data flow end-to-end
- Visual tests validate user perception (animations can break without test coverage)
