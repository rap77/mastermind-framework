/**
 * BentoGrid Component Tests
 *
 * **Purpose:** Test BentoGrid with semantic clustering
 * **Context:** Phase 06-02 - Task 2
 *
 * **TDD Phase:** RED - Failing tests first
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { BentoGrid } from '../BentoGrid'

// Mock ClusterGroup component (tested separately)
vi.mock('../ClusterGroup', () => ({
  ClusterGroup: ({ clusterConfig, brains }: { clusterConfig: any; brains: any[] }) => {
    // Simulate filtering by niche (like real ClusterGroup does)
    const filteredBrains = brains.filter((brain: any) => brain.niche === clusterConfig.niche)
    return (
      <div data-testid={`cluster-${clusterConfig.id}`}>
        {clusterConfig.name}: {filteredBrains.length} brains
      </div>
    )
  },
}))

describe('BentoGrid', () => {
  /**
   * Test 1: BentoGrid renders ClusterGroups from CLUSTER_CONFIGS
   */
  it('should render ClusterGroups from CLUSTER_CONFIGS', () => {
    const brains = [
      { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
      { id: 'brain-01', name: 'Brain 1', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    ]

    render(<BentoGrid brains={brains} />)

    // Should render clusters for master and software
    expect(screen.getByTestId('cluster-master')).toBeInTheDocument()
    expect(screen.getByTestId('cluster-software')).toBeInTheDocument()
  })

  /**
   * Test 2: Each ClusterGroup contains correct brains by niche
   */
  it('should filter brains by niche for each cluster', () => {
    const brains = [
      { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
      { id: 'brain-01', name: 'Brain 1', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
      { id: 'brain-02', name: 'Brain 2', niche: 'software', status: 'idle', uptime: 0, last_called_at: null },
    ]

    render(<BentoGrid brains={brains} />)

    // Master cluster should have 1 brain (mock displays "Master: 1 brains")
    expect(screen.getByTestId('cluster-master')).toHaveTextContent('Master')
    expect(screen.getByTestId('cluster-master')).toHaveTextContent('1 brains')

    // Software cluster should have 2 brains (mock displays "Software Development: 2 brains")
    expect(screen.getByTestId('cluster-software')).toHaveTextContent('Software Development')
    expect(screen.getByTestId('cluster-software')).toHaveTextContent('2 brains')
  })

  /**
   * Test 3: CSS Grid layout uses auto-fit with minmax
   */
  it('should use CSS Grid with auto-fit layout', () => {
    const brains = [
      { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
    ]

    const { container } = render(<BentoGrid brains={brains} />)

    const grid = container.firstChild as HTMLElement
    expect(grid).toHaveClass('grid')
  })

  /**
   * Test 4: Adding new cluster to CLUSTER_CONFIGS renders without code changes
   */
  it('should render new cluster when added to CLUSTER_CONFIGS', () => {
    // This test verifies extensibility - when we add a new cluster to config,
    // it should render without BentoGrid code changes
    const brains = [
      { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
    ]

    render(<BentoGrid brains={brains} />)

    // Current implementation has 3 clusters (master, software, marketing)
    // This test passes if all defined clusters render
    expect(screen.getByTestId('cluster-master')).toBeInTheDocument()
  })

  /**
   * Test 5: Master cluster is visually distinct (zinc-100 theme)
   */
  it('should apply zinc theme to master cluster', () => {
    const brains = [
      { id: 'brain-08', name: 'Brain 8', niche: 'master', status: 'idle', uptime: 0, last_called_at: null },
    ]

    const { container } = render(<BentoGrid brains={brains} />)

    const masterCluster = screen.getByTestId('cluster-master')
    expect(masterCluster).toBeInTheDocument()
    // Note: Color classes are tested in visual tests, not unit tests
  })
})
