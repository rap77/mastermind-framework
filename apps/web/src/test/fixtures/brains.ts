/**
 * Shared test fixtures for brain-related tests
 */

import type { BrainMetadata } from '@/types/api'

export const MOCK_BRAINS: BrainMetadata[] = [
  {
    id: 1,
    name: 'Product Strategy',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 2,
    name: 'UX Research',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 3,
    name: 'UI Design',
    niche: 'software-development',
    status: 'active',
    uptime: 123,
    last_called_at: '2026-03-20T15:30:00Z',
  },
  {
    id: 4,
    name: 'Frontend',
    niche: 'software-development',
    status: 'complete',
    uptime: 456,
    last_called_at: '2026-03-20T16:00:00Z',
  },
]

export const MOCK_BRAIN_BY_ID: Record<number, BrainMetadata> = MOCK_BRAINS.reduce(
  (acc, brain) => ({ ...acc, [brain.id]: brain }),
  {}
)

export function createMockBrain(overrides: Partial<BrainMetadata> = {}): BrainMetadata {
  return {
    id: 1,
    name: 'Test Brain',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
    ...overrides,
  }
}
