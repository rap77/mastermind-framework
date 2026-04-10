/**
 * QuotaBar Component Tests
 *
 * **Purpose:** Test QuotaBar with color coding and Brain #2/#3 fixes
 * **Context:** Phase 17-04 - Task 3
 *
 * **Brain #2 Fix:** Color-only coding violation
 * - Add percentage text: "80%"
 * - Add icons: ✓ (green), ⚠ (yellow), ⚠ (red)
 *
 * **Brain #3 Fix:** Animation easing
 * - cubic-bezier(0.645, 0.045, 0.355, 1)
 * - 200ms duration
 *
 * **TDD Phase:** RED - Writing tests first
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { QuotaBar } from '../QuotaBar'
import type { QuotaBarProps } from '../types'

describe('QuotaBar', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Test 1: Green quota bar (< 80%)
   */
  it('should show green quota bar when below 80%', () => {
    const props: QuotaBarProps = {
      spent: 50,
      budget: 100,
      threshold: 0.8,
    }

    render(<QuotaBar {...props} />)

    expect(screen.getByText('50%')).toBeInTheDocument()
    expect(screen.getByLabelText(/quota status/i)).toHaveTextContent(/^✓/)
  })

  /**
   * Test 2: Yellow quota bar (80-99%)
   */
  it('should show yellow quota bar when between 80-99%', () => {
    const props: QuotaBarProps = {
      spent: 85,
      budget: 100,
      threshold: 0.8,
    }

    render(<QuotaBar {...props} />)

    expect(screen.getByText('85%')).toBeInTheDocument()
    expect(screen.getByLabelText(/quota status/i)).toHaveTextContent(/^⚠/)
  })

  /**
   * Test 3: Red quota bar (≥ 100%)
   */
  it('should show red quota bar when at or above 100%', () => {
    const props: QuotaBarProps = {
      spent: 100,
      budget: 100,
      threshold: 0.8,
    }

    render(<QuotaBar {...props} />)

    expect(screen.getByText('100%')).toBeInTheDocument()
    expect(screen.getByLabelText(/quota status/i)).toHaveTextContent(/^⚠/)
  })

  /**
   * Test 4: ARIA attributes for accessibility
   */
  it('should have proper ARIA attributes', () => {
    const props: QuotaBarProps = {
      spent: 50,
      budget: 100,
    }

    render(<QuotaBar {...props} />)

    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('aria-valuenow', '50')
    expect(progressBar).toHaveAttribute('aria-valuemin', '0')
    expect(progressBar).toHaveAttribute('aria-valuemax', '100')
    expect(progressBar).toHaveAttribute('aria-live', 'polite')
  })

  /**
   * Test 5: Custom threshold (default 0.8)
   */
  it('should use custom threshold when provided', () => {
    const props: QuotaBarProps = {
      spent: 60,
      budget: 100,
      threshold: 0.5, // Custom threshold: 50%
    }

    render(<QuotaBar {...props} />)

    // Should show warning because 60% > 50% threshold
    expect(screen.getByLabelText(/quota status/i)).toHaveTextContent(/^⚠/)
  })

  /**
   * Test 6: Tooltip on hover
   */
  it('should show tooltip with spent/budget details', () => {
    const props: QuotaBarProps = {
      spent: 75,
      budget: 100,
    }

    render(<QuotaBar {...props} />)

    const progressBar = screen.getByRole('progressbar')
    expect(progressBar).toHaveAttribute('title', '$75.00 / $100.00')
  })

  /**
   * Test 7: Zero spent shows 0%
   */
  it('should show 0% when spent is zero', () => {
    const props: QuotaBarProps = {
      spent: 0,
      budget: 100,
    }

    render(<QuotaBar {...props} />)

    expect(screen.getByText('0%')).toBeInTheDocument()
    expect(screen.getByLabelText(/quota status/i)).toHaveTextContent(/^✓/)
  })
})
