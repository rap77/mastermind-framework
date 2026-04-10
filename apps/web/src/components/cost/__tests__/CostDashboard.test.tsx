/**
 * CostDashboard Component Tests
 *
 * **Purpose:** Test CostDashboard with MetricCard grid and budget controls
 * **Context:** Phase 17-04 - Task 4 + Task 5d
 *
 * **Brain #7 Condition 3:** Hierarchical breakdown simplified
 * - Per brain + total ONLY (2 levels)
 * - Remove "per company" toggle/aggregation
 *
 * **Task 5d:** Connection status indicator
 * - WebSocket connection status (connected/disconnected/error)
 * - Pulsing dot animation (respects prefers-reduced-motion)
 *
 * **TDD Phase:** RED -> GREEN
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { CostDashboard } from '../CostDashboard'

// Mock costStore at module level
const mockUseCostStore = vi.fn()
const mockUseCostState = vi.fn()
vi.mock('@/stores/costStore', () => ({
  useCostStore: () => mockUseCostStore(),
  useCostState: () => mockUseCostState(),
}))

// Mock useCostWebSocket hook (Task 5d)
vi.mock('@/hooks/useCostWebSocket', () => ({
  useCostWebSocket: vi.fn(),
}))

describe('CostDashboard', () => {
  const mockMetrics = {
    'brain-01-product': {
      brainId: 'brain-01-product',
      totalTokens: 1000000,
      totalDuration: 300,
      totalCost: 5.50,
      lastActivityAt: '2026-04-10T12:00:00Z',
      successRate: 95,
    },
    'brain-02-ux': {
      brainId: 'brain-02-ux',
      totalTokens: 800000,
      totalDuration: 240,
      totalCost: 4.20,
      lastActivityAt: '2026-04-10T11:00:00Z',
      successRate: 92,
    },
  }

  const mockBrains = [
    { id: 'brain-01-product', name: 'Product Strategy', icon: '🧠' },
    { id: 'brain-02-ux', name: 'UX Research', icon: '🎨' },
  ]

  const mockSetBudget = vi.fn()

  const getDefaultMockState = (connectionStatus: 'connected' | 'disconnected' | 'error' = 'connected') => ({
    metrics: mockMetrics,
    budget: 100,
    spent: 9.70,
    connectionStatus,
    updateMetric: vi.fn(),
    setBudget: mockSetBudget,
    setConnectionStatus: vi.fn(),
    resetMetrics: vi.fn(),
    getCostState: vi.fn(),
  })

  beforeEach(() => {
    vi.clearAllMocks()
    // Mock useCostStore to return default state (including Task 5d connectionStatus)
    mockUseCostStore.mockReturnValue(getDefaultMockState())
    // Mock useCostState to return undefined (no previous metrics)
    mockUseCostState.mockReturnValue(undefined)
  })

  /**
   * Test 1: Dashboard renders with total spent/budget header
   */
  it('should render with total spent and budget in header', () => {
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.getByText(/Total Spent/i)).toBeInTheDocument()
    expect(screen.getByText(/\$9\.70/)).toBeInTheDocument()
    // Use more specific query for budget (the one in the header, not the slider label)
    expect(screen.getAllByText(/budget/i)).toHaveLength(2) // Header + slider label
  })

  /**
   * Test 2: Dashboard renders QuotaBar in header
   */
  it('should render QuotaBar in header', () => {
    render(<CostDashboard brains={mockBrains} />)

    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toBeInTheDocument()
    expect(progressBar).toHaveAttribute('aria-valuenow', '10') // 9.70/100 = ~10%
  })

  /**
   * Test 3: Dashboard renders MetricCard grid
   */
  it('should render grid of MetricCards', () => {
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.getByText('Product Strategy')).toBeInTheDocument()
    expect(screen.getByText('UX Research')).toBeInTheDocument()
  })

  /**
   * Test 4: Budget slider updates budget
   */
  it('should call setBudget when slider changes', () => {
    render(<CostDashboard brains={mockBrains} />)

    const budgetSlider = screen.getByRole('slider', { name: /adjust budget/i })
    fireEvent.change(budgetSlider, { target: { value: '150' } })

    expect(mockSetBudget).toHaveBeenCalledWith(150)
  })

  /**
   * Test 5: Export CSV button exists
   */
  it('should have export CSV button', () => {
    render(<CostDashboard brains={mockBrains} />)

    // Check for button by text content (case-insensitive)
    const exportButton = screen.getByText(/export csv/i)
    expect(exportButton).toBeInTheDocument()
    // Verify it's a button element
    expect(exportButton.tagName).toBe('BUTTON')
  })

  /**
   * Test 6: Responsive grid (1 col mobile, 6 cols desktop)
   */
  it('should render with responsive grid classes', () => {
    const { container } = render(<CostDashboard brains={mockBrains} />)

    const grid = container.querySelector('.metrics-grid')
    expect(grid).toHaveClass('grid-cols-1') // Mobile
    expect(grid).toHaveClass('md:grid-cols-2') // Tablet
    expect(grid).toHaveClass('lg:grid-cols-3') // Desktop
    expect(grid).toHaveClass('xl:grid-cols-4') // Large desktop
    expect(grid).toHaveClass('2xl:grid-cols-6') // Extra large
  })

  /**
   * Test 7: No "per company" toggle (Brain #7 simplified)
   */
  it('should not have per company toggle', () => {
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.queryByRole('checkbox', { name: /per company/i })).not.toBeInTheDocument()
  })

  /**
   * Test 8: Empty state when no brains
   */
  it('should show empty state when no brains', () => {
    render(<CostDashboard brains={[]} />)

    expect(screen.getByText(/no cost data available/i)).toBeInTheDocument()
  })

  /**
   * Test 9: MetricCard density mode defaults to normal
   */
  it('should render MetricCards with normal density mode', () => {
    render(<CostDashboard brains={mockBrains} />)

    // Normal mode shows all 3 lines (tokens, duration, cost)
    expect(screen.getByText(/1\.0M/)).toBeInTheDocument()
    expect(screen.getByText(/5m/)).toBeInTheDocument()
  })

  /**
   * Test 10: useCostStore global selector (not useCostState)
   */
  it('should use useCostStore for global state access', () => {
    render(<CostDashboard brains={mockBrains} />)

    expect(mockUseCostStore).toHaveBeenCalled()
  })

  /**
   * Test 11: Connection status indicator - connected state (Task 5d)
   */
  it('should render connection status indicator for connected state', () => {
    mockUseCostStore.mockReturnValue(getDefaultMockState('connected'))
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.getByText(/Live/i)).toBeInTheDocument()
  })

  /**
   * Test 12: Connection status indicator - disconnected state (Task 5d)
   */
  it('should render connection status indicator for disconnected state', () => {
    mockUseCostStore.mockReturnValue(getDefaultMockState('disconnected'))
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.getByText(/Offline/i)).toBeInTheDocument()
  })

  /**
   * Test 13: Connection status indicator - error state (Task 5d)
   */
  it('should render connection status indicator for error state', () => {
    mockUseCostStore.mockReturnValue(getDefaultMockState('error'))
    render(<CostDashboard brains={mockBrains} />)

    expect(screen.getByText(/Error/i)).toBeInTheDocument()
  })
})
