/**
 * Shared test fixtures for brain-related tests
 */

import type { BrainMetadata } from '@/types/api'
import type { Brain } from '@/lib/api'

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

/**
 * Brain fixtures for component-layer tests (ClusterGroup, BentoGrid).
 *
 * These use the Brain type from @/lib/api which has:
 * - id: string  (e.g. 'brain-01')
 * - niche: 'master' | 'software' | 'marketing' | string
 *
 * Index map:
 *   [0] brain-08  niche: 'universal'  → master cluster
 *   [1] brain-01  niche: 'software'   → software cluster
 *   [2] brain-02  niche: 'software'   → software cluster
 *   [3] brain-03  niche: 'software'   → software cluster
 *   [4] brain-08  niche: 'universal'  → master cluster (alias for index 0)
 */
export const MOCK_COMPONENT_BRAINS: Brain[] = [
  {
    id: 'brain-08',
    name: 'Master Brain',
    niche: 'universal',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-01',
    name: 'Product Strategy',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-02',
    name: 'UX Research',
    niche: 'software-development',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-03',
    name: 'UI Design',
    niche: 'software-development',
    status: 'active',
    uptime: 123,
    last_called_at: '2026-03-20T15:30:00Z',
  },
  {
    id: 'brain-08',
    name: 'Master Brain',
    niche: 'universal',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-09',
    name: 'Growth Strategy',
    niche: 'marketing-digital',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
  {
    id: 'brain-10',
    name: 'Content Marketing',
    niche: 'marketing-digital',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  },
]
