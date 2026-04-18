/**
 * LoadingSpinner tests
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { LoadingSpinner } from '@/components/ui/LoadingSpinner'

describe('LoadingSpinner', () => {
  it('renders with default size (md)', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('[role="status"]')
    expect(spinner).toBeInTheDocument()
    expect(spinner).toHaveClass('w-6', 'h-6', 'border-2')
  })

  it('renders with small size', () => {
    const { container } = render(<LoadingSpinner size="sm" />)
    const spinner = container.querySelector('[role="status"]')
    expect(spinner).toHaveClass('w-4', 'h-4', 'border-2')
  })

  it('renders with large size', () => {
    const { container } = render(<LoadingSpinner size="lg" />)
    const spinner = container.querySelector('[role="status"]')
    expect(spinner).toHaveClass('w-8', 'h-8', 'border-4')
  })

  it('applies custom className', () => {
    const { container } = render(<LoadingSpinner className="text-primary" />)
    const spinner = container.querySelector('[role="status"]')
    expect(spinner).toHaveClass('text-primary')
  })

  it('has proper accessibility attributes', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('[role="status"]')

    expect(spinner).toHaveAttribute('role', 'status')
    expect(spinner).toHaveAttribute('aria-live', 'polite')
    expect(spinner).toHaveAttribute('aria-label', 'Loading...')
  })

  it('renders custom aria-label', () => {
    const { container } = render(<LoadingSpinner ariaLabel="Processing data..." />)
    const spinner = container.querySelector('[role="status"]')

    expect(spinner).toHaveAttribute('aria-label', 'Processing data...')

    // Check screen reader text
    const srText = screen.getByText('Processing data...')
    expect(srText).toHaveClass('sr-only')
  })

  it('has screen reader only text', () => {
    render(<LoadingSpinner />)
    const srText = screen.getByText('Loading...')
    expect(srText).toHaveClass('sr-only')
  })

  it('has animation classes', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('[role="status"]')

    expect(spinner).toHaveClass('animate-spin', 'border-t-transparent')
  })

  it('has motion reduce for accessibility', () => {
    const { container } = render(<LoadingSpinner />)
    const spinner = container.querySelector('[role="status"]')

    expect(spinner).toHaveClass('motion-reduce:animate-[spin_1.5s_linear_infinite]')
  })
})
