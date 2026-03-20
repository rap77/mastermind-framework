/**
 * Shared test fixtures for brain-related tests
 *
 * Purpose: Eliminates mock data duplication across test files
 * Usage: Import MOCK_BRAINS instead of defining inline
 */

import type { Brain } from '@/types/api'

/**
 * Mock brain data with proper TypeScript types
 * All fields match the Brain interface from api.ts
 */
export const MOCK_BRAINS: Brain[] = [
  {
    id: 'brain-01',
    name: 'Product Strategy',
    niche: 'software',
    status: 'idle',
    uptime: 0.0,
    last_called_at: null,
  },
  {
    id: 'brain-02',
    name: 'UX Research',
    niche: 'software',
    status: 'idle',
    uptime: 0.0,
    last_called_at: null,
  },
  {
    id: 'brain-03',
    name: 'UI Design',
    niche: 'software',
    status: 'active',
    uptime: 123.45,
    last_called_at: '2026-03-20T15:30:00Z',
  },
  {
    id: 'brain-04',
    name: 'Frontend',
    niche: 'software',
    status: 'complete',
    uptime: 456.78,
    last_called_at: '2026-03-20T16:00:00Z',
  },
  {
    id: 'brain-08',
    name: 'Critical Evaluator',
    niche: 'master',
    status: 'idle',
    uptime: 0.0,
    last_called_at: null,
  },
  {
    id: 'brain-09',
    name: 'Marketing Digital',
    niche: 'marketing',
    status: 'error',
    uptime: 789.01,
    last_called_at: '2026-03-20T16:30:00Z',
  },
]

/**
 * Mock brain by ID for quick access
 */
export const MOCK_BRAIN_BY_ID: Record<string, Brain> = MOCK_BRAINS.reduce(
  (acc, brain) => ({ ...acc, [brain.id]: brain }),
  {}
)

/**
 * Mock brains grouped by niche
 */
export const MOCK_BRAINS_BY_NICHE: Record<string, Brain[]> = {
  master: MOCK_BRAINS.filter((b) => b.niche === 'master'),
  software: MOCK_BRAINS.filter((b) => b.niche === 'software'),
  marketing: MOCK_BRAINS.filter((b) => b.niche === 'marketing'),
  universal: MOCK_BRAINS.filter((b) => b.niche === 'universal'),
}

/**
 * Helper to create a mock brain with overrides
 */
export function createMockBrain(overrides: Partial<Brain> = {}): Brain {
  return {
    id: 'brain-test',
    name: 'Test Brain',
    niche: 'software',
    status: 'idle',
    uptime: 0.0,
    last_called_at: null,
    ...overrides,
  }
}

/**
 * Helper to create multiple mock brains
 */
export function createMockBrains(count: number, overrides?: Partial<Brain>): Brain[] {
  return Array.from({ length: count }, (_, i) =>
    createMockBrain({
      id: `brain-test-${i + 1}`,
      name: `Test Brain ${i + 1}`,
      ...overrides,
    })
  )
}
