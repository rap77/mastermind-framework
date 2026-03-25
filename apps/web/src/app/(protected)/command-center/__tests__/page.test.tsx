/**
 * Command Center Page Tests
 *
 * **Purpose:** Test Command Center page with TanStack Query
 * **Context:** Phase 06-02 - Task 1
 *
 * **TDD Phase:** GREEN - All tests passing
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { BentoGrid } from '@/components/command-center/BentoGrid'
import { MOCK_BRAINS } from '@/test/fixtures/brains'
import type { Brain } from '@/types/api'

// Mock ClusterGroup component
vi.mock('@/components/command-center/ClusterGroup', () => ({
  ClusterGroup: ({ clusterConfig, brains }: { clusterConfig: any; brains: Brain[] }) => {
    const filteredBrains = brains.filter((brain) => brain.niche === clusterConfig.niche)
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
    const brains = [MOCK_BRAINS[0], MOCK_BRAINS[1]]

    render(<BentoGrid brains={brains} />)
    expect(screen.getByTestId('bento-grid')).toBeInTheDocument()
  })

  /**
   * Test 2: BentoGrid displays clusters
   */
  it('should display cluster names', () => {
    const brains = [MOCK_BRAINS[0], MOCK_BRAINS[1]]

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
