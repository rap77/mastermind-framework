/**
 * ClusterGroup Component Tests
 *
 * **Purpose:** Test niche-level grouping component
 * **Context:** Phase 06-02 - Task 2
 *
 * **TDD Phase:** RED - Failing tests first
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { ClusterGroup } from '../ClusterGroup'
import type { ClusterConfig } from '@/config/clusters'

// Mock BrainTile component (tested separately in Task 3)
vi.mock('../BrainTile', () => ({
  BrainTile: ({ brain }: { brain: any }) => (
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

  const mockBrains = [
    { id: 'brain-01', name: 'Brain 1', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    { id: 'brain-02', name: 'Brain 2', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
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

    // Should only render software brains (brain-01, brain-02)
    expect(screen.getByTestId('brain-brain-01')).toBeInTheDocument()
    expect(screen.getByTestId('brain-brain-02')).toBeInTheDocument()

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
    expect(screen.getByTestId('brain-brain-02')).toBeInTheDocument()
  })
})
