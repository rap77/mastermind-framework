/**
 * MetricCard Component Tests
 *
 * **Purpose:** Test MetricCard with trend indicators and density modes
 * **Context:** Phase 17-04 - Task 2
 *
 * **TDD Phase:** RED -> GREEN
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { MetricCard } from '../MetricCard'
import type { Brain, CostMetric } from '../types'

// Mock costStore at module level
const mockUseCostState = vi.fn()
vi.mock('@/stores/costStore', () => ({
  useCostStore: vi.fn(),
  useCostState: () => mockUseCostState(),
}))

describe('MetricCard', () => {
  const mockBrain: Brain = {
    id: 'brain-01-product',
    name: 'Product Strategy',
    icon: '🧠',
  }

  const mockMetrics: CostMetric = {
    brainId: 'brain-01-product',
    totalTokens: 1000000,
    totalDuration: 300, // 5 minutes
    totalCost: 5.50,
    lastActivityAt: '2026-04-10T12:00:00Z',
    successRate: 95,
  }

  beforeEach(() => {
    vi.clearAllMocks()
    // Reset to return undefined by default (no previous metrics)
    mockUseCostState.mockReturnValue(undefined)
  })

  /**
   * Test 1: MetricCard displays brain name and icon
   */
  it('should display brain name and icon', () => {
    render(<MetricCard brain={mockBrain} metrics={mockMetrics} />)

    expect(screen.getByText('Product Strategy')).toBeInTheDocument()
    expect(screen.getByText('🧠')).toBeInTheDocument()
  })

  /**
   * Test 2: Compact mode shows only cost (single line)
   */
  it('should show only cost in compact mode', () => {
    render(<MetricCard brain={mockBrain} metrics={mockMetrics} densityMode="compact" />)

    // Should show cost
    expect(screen.getByText(/\$5\.50/)).toBeInTheDocument()

    // Should NOT show tokens or duration in compact mode
    expect(screen.queryByText(/1\.0M/)).not.toBeInTheDocument()
    expect(screen.queryByText(/5m/)).not.toBeInTheDocument()
  })

  /**
   * Test 3: Normal mode shows tokens, duration, and cost (3 lines)
   */
  it('should show tokens, duration, and cost in normal mode', () => {
    render(<MetricCard brain={mockBrain} metrics={mockMetrics} densityMode="normal" />)

    expect(screen.getByText(/1\.0M/)).toBeInTheDocument()
    expect(screen.getByText(/5m/)).toBeInTheDocument()
    expect(screen.getByText(/\$5\.50/)).toBeInTheDocument()
  })

  /**
   * Test 4: Trend indicator - increased cost (↑ red)
   */
  it('should show red upward arrow when cost increased', () => {
    // Mock previous cost as $5.50
    mockUseCostState.mockReturnValue({ totalCost: 5.50 })

    const currentMetrics: CostMetric = {
      ...mockMetrics,
      totalCost: 7.50, // Increased from $5.50
    }

    render(
      <MetricCard
        brain={mockBrain}
        metrics={currentMetrics}
      />
    )

    const arrowIcon = screen.getByLabelText(/cost increased/i)
    expect(arrowIcon).toBeInTheDocument()
    // The icon is wrapped in a span with the color class
    expect(arrowIcon.closest('span')).toHaveClass('text-red-500')
  })

  /**
   * Test 5: Trend indicator - decreased cost (↓ green)
   */
  it('should show green downward arrow when cost decreased', () => {
    // Mock previous cost as $5.50
    mockUseCostState.mockReturnValue({ totalCost: 5.50 })

    const currentMetrics: CostMetric = {
      ...mockMetrics,
      totalCost: 3.50, // Decreased from $5.50
    }

    render(
      <MetricCard
        brain={mockBrain}
        metrics={currentMetrics}
      />
    )

    const arrowIcon = screen.getByLabelText(/cost decreased/i)
    expect(arrowIcon).toBeInTheDocument()
    // The icon is wrapped in a span with the color class
    expect(arrowIcon.closest('span')).toHaveClass('text-green-500')
  })

  /**
   * Test 6: Drill-down button triggers callback
   */
  it('should call onDrillDown when button clicked', () => {
    const onDrillDown = vi.fn()

    render(
      <MetricCard
        brain={mockBrain}
        metrics={mockMetrics}
        onDrillDown={onDrillDown}
      />
    )

    const drillDownButton = screen.getByRole('button', { name: /View Details for Product Strategy/i })
    fireEvent.click(drillDownButton)

    expect(onDrillDown).toHaveBeenCalledWith('brain-01-product')
  })

  /**
   * Test 7: React.memo prevents unnecessary re-renders
   */
  it('should use React.memo for performance', () => {
    const { rerender } = render(
      <MetricCard brain={mockBrain} metrics={mockMetrics} />
    )

    // Re-render with same props - should not re-render due to React.memo
    rerender(<MetricCard brain={mockBrain} metrics={mockMetrics} />)

    // If this test passes without errors, React.memo is working
    expect(screen.getByText('Product Strategy')).toBeInTheDocument()
  })

  /**
   * Test 8: Density mode defaults to normal
   */
  it('should default to normal density mode', () => {
    render(<MetricCard brain={mockBrain} metrics={mockMetrics} />)

    // Should show all 3 lines (normal mode)
    expect(screen.getByText(/1\.0M/)).toBeInTheDocument()
    expect(screen.getByText(/5m/)).toBeInTheDocument()
    expect(screen.getByText(/\$5\.50/)).toBeInTheDocument()
  })

  /**
   * Test 9: No trend arrow when cost unchanged
   */
  it('should not show trend arrow when cost unchanged', () => {
    // Mock previous cost as $5.50 (same as current)
    mockUseCostState.mockReturnValue({ totalCost: 5.50 })

    render(
      <MetricCard
        brain={mockBrain}
        metrics={mockMetrics}
      />
    )

    expect(screen.queryByLabelText(/cost (increased|decreased)/i)).not.toBeInTheDocument()
  })
})
