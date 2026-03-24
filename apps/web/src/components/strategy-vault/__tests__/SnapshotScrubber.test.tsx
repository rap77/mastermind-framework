/**
 * SnapshotScrubber Component Tests
 *
 * **Purpose:** Verify timeline scrubber UI and milestone navigation
 * **Context:** Phase 08-02 - Task 3
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { SnapshotScrubber } from '../SnapshotScrubber'
import type { SnapshotMilestone } from '@/stores/replayStore'

// ─── Fixtures ─────────────────────────────────────────────────────────────────

const MILESTONES: SnapshotMilestone[] = [
  { index: 0, timestamp: 1000, label: '0% (0 active)', brainCount: 0 },
  { index: 2, timestamp: 1200, label: '25% (3 active)', brainCount: 3 },
  { index: 4, timestamp: 1400, label: '50% (6 active)', brainCount: 6 },
  { index: 6, timestamp: 1600, label: '75% (8 active)', brainCount: 8 },
  { index: 8, timestamp: 1800, label: '100% (5 active)', brainCount: 5 },
]

describe('SnapshotScrubber', () => {
  const mockOnScrub = vi.fn()
  const mockOnMilestoneHover = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders the scrubber container', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    expect(screen.getByTestId('snapshot-scrubber')).toBeInTheDocument()
  })

  it('renders all milestone markers', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    for (const m of MILESTONES) {
      expect(screen.getByTestId(`milestone-${m.index}`)).toBeInTheDocument()
    }
  })

  it('calls onScrub when milestone button is clicked', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    fireEvent.click(screen.getByTestId('milestone-4'))
    expect(mockOnScrub).toHaveBeenCalledWith(4)
  })

  it('calls onScrub on ArrowRight key', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    const slider = screen.getByRole('slider')
    fireEvent.keyDown(slider, { key: 'ArrowRight' })
    // Should move to next milestone (index 2)
    expect(mockOnScrub).toHaveBeenCalledWith(2)
  })

  it('calls onScrub on ArrowLeft key', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={4} // 3rd milestone
        onScrub={mockOnScrub}
      />
    )
    const slider = screen.getByRole('slider')
    fireEvent.keyDown(slider, { key: 'ArrowLeft' })
    // Should move to previous milestone (index 2)
    expect(mockOnScrub).toHaveBeenCalledWith(2)
  })

  it('does not go below first milestone on ArrowLeft', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    const slider = screen.getByRole('slider')
    fireEvent.keyDown(slider, { key: 'ArrowLeft' })
    // Already at first milestone — stays at index 0
    expect(mockOnScrub).toHaveBeenCalledWith(0)
  })

  it('does not go above last milestone on ArrowRight', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={8}
        onScrub={mockOnScrub}
      />
    )
    const slider = screen.getByRole('slider')
    fireEvent.keyDown(slider, { key: 'ArrowRight' })
    // Already at last milestone — stays at index 8
    expect(mockOnScrub).toHaveBeenCalledWith(8)
  })

  it('shows current milestone label', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={4}
        onScrub={mockOnScrub}
      />
    )
    expect(screen.getByTestId('scrubber-label')).toHaveTextContent('50% (6 active)')
  })

  it('calls onMilestoneHover on milestone mouse enter', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
        onMilestoneHover={mockOnMilestoneHover}
      />
    )
    fireEvent.mouseEnter(screen.getByTestId('milestone-4'))
    expect(mockOnMilestoneHover).toHaveBeenCalledWith(MILESTONES[2])
  })

  it('calls onMilestoneHover with null on mouse leave', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
        onMilestoneHover={mockOnMilestoneHover}
      />
    )
    fireEvent.mouseLeave(screen.getByTestId('milestone-4'))
    expect(mockOnMilestoneHover).toHaveBeenCalledWith(null)
  })

  it('renders scrubber thumb element', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    expect(screen.getByTestId('scrubber-thumb')).toBeInTheDocument()
  })

  it('renders 0% when empty milestones', () => {
    render(
      <SnapshotScrubber
        milestones={[]}
        currentIndex={0}
        onScrub={mockOnScrub}
      />
    )
    expect(screen.getByTestId('scrubber-percentage')).toHaveTextContent('0%')
  })

  it('has ARIA slider role with correct attributes', () => {
    render(
      <SnapshotScrubber
        milestones={MILESTONES}
        currentIndex={4}
        onScrub={mockOnScrub}
      />
    )
    const slider = screen.getByRole('slider')
    expect(slider).toHaveAttribute('aria-valuemin', '0')
    expect(slider).toHaveAttribute('aria-valuemax', '4')
    expect(slider).toHaveAttribute('aria-valuetext', '50% (6 active)')
  })
})
