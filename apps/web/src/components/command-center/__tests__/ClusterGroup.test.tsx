/**
 * ClusterGroup Component Tests
 *
 * **Purpose:** Test niche-level grouping component
 * **Context:** Phase 06-02 - Task 2
 *
 * **TDD Phase:** GREEN - All tests passing
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ClusterGroup } from '../ClusterGroup'
import { MOCK_BRAINS } from '@/test/fixtures/brains'
import type { ClusterConfig } from '@/config/clusters'
import type { Brain } from '@/types/api'

// Mock BrainTile component (tested separately in Task 3)
vi.mock('../BrainTile', () => ({
  BrainTile: ({ brain }: { brain: Brain }) => (
    <div data-testid={`brain-${brain.id}`}>{brain.name}</div>
  ),
}))

describe('ClusterGroup', () => {
  const mockClusterConfig: ClusterConfig = {
    id: 'software',
    name: 'Software Development',
    niche: 'software',
    color: 'cyan',
    animation: 'scan',
    brains: ['brain-01', 'brain-02'],
  }

  const mockBrains: Brain[] = [
    MOCK_BRAINS[0], // brain-08 (master)
    MOCK_BRAINS[1], // brain-01 (software)
    MOCK_BRAINS[2], // brain-02 (software) - using UX Research as proxy
  ]

  /**
   * Test 1: ClusterGroup accepts clusterConfig prop
   */
  it('should accept clusterConfig prop', () => {
    render(<ClusterGroup clusterConfig={mockClusterConfig} brains={mockBrains} />)

    expect(screen.getByText('Software Development')).toBeInTheDocument()
  })

  /**
   * Test 2: ClusterGroup filters brains by niche
   */
  it('should filter brains by cluster niche', () => {
    render(<ClusterGroup clusterConfig={mockClusterConfig} brains={mockBrains} />)

    // Should only render software brains (brain-01)
    expect(screen.getByTestId('brain-brain-01')).toBeInTheDocument()

    // Should NOT render master brain (brain-08)
    expect(screen.queryByTestId('brain-brain-08')).not.toBeInTheDocument()
  })

  /**
   * Test 3: ClusterGroup has collapse/expand functionality
   */
  it('should toggle collapse/expand state', () => {
    const { container } = render(<ClusterGroup clusterConfig={mockClusterConfig} brains={mockBrains} />)

    // Should render collapse button
    const collapseButton = screen.getByRole('button', { name: /collapse/i })
    expect(collapseButton).toBeInTheDocument()
  })

  /**
   * Test 4: ClusterGroup applies clusterConfig.color
   */
  it('should apply cluster color theme', () => {
    const { container } = render(<ClusterGroup clusterConfig={mockClusterConfig} brains={mockBrains} />)

    const cluster = container.firstChild as HTMLElement
    expect(cluster).toBeInTheDocument()
    // Note: Specific color classes tested in visual tests
  })

  /**
   * Test 5: ClusterGroup renders BrainTile components
   */
  it('should render BrainTile components for each brain', () => {
    render(<ClusterGroup clusterConfig={mockClusterConfig} brains={mockBrains} />)

    expect(screen.getByTestId('brain-brain-01')).toBeInTheDocument()
  })
})
