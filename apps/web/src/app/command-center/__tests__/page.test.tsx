/**
 * Command Center Page Tests
 *
 * **Purpose:** Test Command Center page with TanStack Query
 * **Context:** Phase 06-02 - Task 1
 *
 * **TDD Phase:** RED - Failing tests first
 *
 * **Note:** Server Components are tested via integration tests.
 * This file tests the BentoGrid component which receives server-fetched data.
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BentoGrid } from '@/components/command-center/BentoGrid'

// Mock ClusterGroup component
vi.mock('@/components/command-center/ClusterGroup', () => ({
  ClusterGroup: ({ clusterConfig, brains }: { clusterConfig: any; brains: any[] }) => {
    const filteredBrains = brains.filter((brain: any) => brain.niche === clusterConfig.niche)
    return (
      <div data-testid={`cluster-${clusterConfig.id}`}>
        {clusterConfig.name}: {filteredBrains.length} brains
      </div>
    )
  },
}))

describe('BentoGrid (receives server-fetched data)', () => {
  /**
   * Test 1: BentoGrid renders without errors
   */
  it('should render BentoGrid without errors', () => {
    const brains = [
      { id: 'brain-01', name: 'Brain 1', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
      { id: 'brain-02', name: 'Brain 2', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    ]

    render(<BentoGrid brains={brains} />)
    expect(screen.getByTestId('bento-grid')).toBeInTheDocument()
  })

  /**
   * Test 2: BentoGrid displays clusters
   */
  it('should display cluster names', () => {
    const brains = [
      { id: 'brain-01', name: 'Brain 1', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
      { id: 'brain-02', name: 'Brain 2', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    ]

    render(<BentoGrid brains={brains} />)
    expect(screen.getByText(/Software Development/)).toBeInTheDocument()
  })

  /**
   * Test 3: BentoGrid handles empty brains array
   */
  it('should handle empty brains array', () => {
    render(<BentoGrid brains={[]} />)
    expect(screen.getByTestId('bento-grid')).toBeInTheDocument()
  })
})
