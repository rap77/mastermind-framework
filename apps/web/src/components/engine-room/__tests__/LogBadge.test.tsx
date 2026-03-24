/**
 * LogBadge Component Tests
 *
 * **Purpose:** Verify brain name/id badge rendering and click behavior
 * **Context:** Phase 08-03 — Task 3
 */

import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { LogBadge } from '../LogBadge'

describe('LogBadge', () => {
  it('renders brainName and brainId', () => {
    render(
      <LogBadge brainId="marketing-01" brainName="Marketing Strategist" level="info" />
    )
    expect(screen.getByText('Marketing Strategist')).toBeInTheDocument()
    expect(screen.getByText('(marketing-01)')).toBeInTheDocument()
  })

  it('applies blue color class for info level', () => {
    const { container } = render(
      <LogBadge brainId="x" brainName="X Brain" level="info" />
    )
    expect(container.firstChild).toHaveClass('text-blue-500')
  })

  it('applies yellow color class for warn level', () => {
    const { container } = render(
      <LogBadge brainId="x" brainName="X Brain" level="warn" />
    )
    expect(container.firstChild).toHaveClass('text-yellow-500')
  })

  it('applies red color class for error level', () => {
    const { container } = render(
      <LogBadge brainId="x" brainName="X Brain" level="error" />
    )
    expect(container.firstChild).toHaveClass('text-red-500')
  })

  it('calls onClick when clicked', () => {
    const handleClick = vi.fn()
    render(
      <LogBadge brainId="x" brainName="X Brain" level="info" onClick={handleClick} />
    )
    fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('calls onClick on Enter key press', () => {
    const handleClick = vi.fn()
    render(
      <LogBadge brainId="x" brainName="X Brain" level="info" onClick={handleClick} />
    )
    fireEvent.keyDown(screen.getByRole('button'), { key: 'Enter' })
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('has cursor-pointer class when onClick provided', () => {
    const { container } = render(
      <LogBadge brainId="x" brainName="X Brain" level="info" onClick={() => {}} />
    )
    expect(container.firstChild).toHaveClass('cursor-pointer')
  })

  it('has cursor-default class when no onClick', () => {
    const { container } = render(
      <LogBadge brainId="x" brainName="X Brain" level="info" />
    )
    expect(container.firstChild).toHaveClass('cursor-default')
  })

  it('renders with accessible aria-label', () => {
    render(
      <LogBadge brainId="marketing-01" brainName="Marketing Strategist" level="warn" />
    )
    expect(
      screen.getByLabelText('Brain: Marketing Strategist (marketing-01), level: warn')
    ).toBeInTheDocument()
  })
})
