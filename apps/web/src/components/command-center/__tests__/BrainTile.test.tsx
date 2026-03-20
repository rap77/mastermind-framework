/**
 * BrainTile Component Tests
 *
 * **Purpose:** Test BrainTile with ICE-validated status animations
 * **Context:** Phase 06-02 - Task 3
 *
 * **TDD Phase:** GREEN - Tests passing
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BrainTile } from '../BrainTile'
import type { Brain } from '@/lib/api'
import { useBrainState } from '@/stores/brainStore'

// Mock brainStore
vi.mock('@/stores/brainStore', () => ({
  useBrainState: vi.fn(),
}))

// Mock Check icon from lucide-react
vi.mock('lucide-react', () => ({
  Check: () => <svg data-testid="check-icon" />,
}))

describe('BrainTile', () => {
  const mockBrain: Brain = {
    id: 'brain-01',
    name: 'Product Strategy',
    niche: 'software',
    status: 'idle',
    uptime: 0,
    last_called_at: null,
  }

  beforeEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Test 1: BrainTile displays brain name and status
   */
  it('should display brain name and status', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'idle', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    expect(screen.getByText('Product Strategy')).toBeInTheDocument()
    expect(screen.getByText(/idle/i)).toBeInTheDocument()
  })

  /**
   * Test 2: Status color changes - idle (gray)
   */
  it('should apply opacity-60 for idle status', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'idle', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    expect(screen.getByTestId('brain-brain-01')).toHaveClass('opacity-60')
  })

  /**
   * Test 3: Active status triggers pulse animation (ICE-validated)
   */
  it('should apply pulse animation for active status', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'active', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    const tile = screen.getByTestId('brain-brain-01')
    expect(tile).toHaveClass('animate-pulse')
  })

  /**
   * Test 4: Complete status shows checkmark (ICE-validated)
   */
  it('should show checkmark icon for complete status', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'complete', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    expect(screen.getByTestId('check-icon')).toBeInTheDocument()
  })

  /**
   * Test 5: Error status triggers shake animation (ICE-validated)
   */
  it('should apply shake animation for error status', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'error', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    const tile = screen.getByTestId('brain-brain-01')
    expect(tile).toHaveClass('animate-shake')
  })

  /**
   * Test 6: useBrainState selector prevents re-renders on other brain updates
   */
  it('should use useBrainState selector for targeted updates', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'idle', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    // Verify useBrainState was called with brain ID
    expect(useBrainState).toHaveBeenCalledWith('brain-01')
  })

  /**
   * Test 7: No cluster-level animations (glow, scan) per ICE Scoring
   */
  it('should not have cluster-level decorative animations', () => {
    vi.mocked(useBrainState).mockReturnValue({ status: 'idle', uptime: 0, lastUpdated: 0 })

    render(<BrainTile brain={mockBrain} />)

    const tile = screen.getByTestId('brain-brain-01')

    // Should NOT have glow or scan animations (deferred per ICE Scoring)
    expect(tile).not.toHaveClass('animate-glow')
    expect(tile).not.toHaveClass('animate-scan')
  })
})
