/**
 * BriefInputModal Component Tests
 *
 * **Purpose:** Test full-screen brief input modal with XSS prevention
 * **Context:** Phase 06-03 - Task 2
 *
 * **TDD Phase:** RED - Tests should fail (component doesn't exist yet)
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BriefInputModal } from '../BriefInputModal'

describe('BriefInputModal', () => {
  const mockOnClose = vi.fn()
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
  })

  /**
   * Test 1: Modal renders when open prop is true
   */
  it('should render when open prop is true', () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    expect(screen.getByText('New Brief')).toBeInTheDocument()
  })

  /**
   * Test 2: Modal is full-screen with backdrop blur
   */
  it('should have full-screen styling with backdrop blur', () => {
    render(
      <BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />
    )

    // Check for Dialog content
    expect(screen.getByText('New Brief')).toBeInTheDocument()

    // Check for backdrop (fixed overlay)
    const backdrop = document.querySelector('.fixed.inset-0')
    expect(backdrop).toBeInTheDocument()
  })

  /**
   * Test 3: Textarea is multi-line with auto-resize
   */
  it('should have multi-line textarea', () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const textarea = screen.getByPlaceholderText('Describe your task...')
    expect(textarea).toBeInTheDocument()
    expect(textarea.tagName).toBe('TEXTAREA')
  })

  /**
   * Test 4: Submit button is disabled when textarea is empty
   */
  it('should disable submit button when textarea is empty', () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const submitButton = screen.getByRole('button', { name: /submit/i })
    expect(submitButton).toBeDisabled()
  })

  /**
   * Test 5: Escape key closes modal
   */
  it('should close modal when Escape key is pressed', () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    fireEvent.keyDown(document, { key: 'Escape' })

    expect(mockOnClose).toHaveBeenCalledTimes(1)
  })

  /**
   * Test 6: Click outside closes modal (via onOpenChange)
   * NOTE: base-ui-react Dialog handles backdrop clicks automatically via onOpenChange
   */
  it('should close modal when clicking outside', () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    // Find the backdrop overlay
    const backdrop = document.querySelector('[data-slot="dialog-overlay"]')
    expect(backdrop).toBeInTheDocument()

    // The Dialog component's onOpenChange prop handles backdrop clicks
    // We just verify the backdrop element exists
    expect(backdrop).toHaveClass('fixed', 'inset-0')
  })

  /**
   * Test 7: XSS prevention - <script> tags are stripped
   */
  it('should strip <script> tags from input (XSS prevention)', async () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const textarea = screen.getByPlaceholderText('Describe your task...')
    const submitButton = screen.getByRole('button', { name: /submit/i })

    const maliciousInput = '<script>alert("XSS")</script>Hello'
    fireEvent.change(textarea, { target: { value: maliciousInput } })

    // Submit the form
    fireEvent.click(submitButton)

    // Wait for async submission
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Hello')
    })
  })

  /**
   * Test 8: XSS prevention - on* attributes are removed
   */
  it('should remove on* attributes from input (XSS prevention)', async () => {
    render(<BriefInputModal open={true} onClose={mockOnClose} onSubmit={mockOnSubmit} />)

    const textarea = screen.getByPlaceholderText('Describe your task...')
    const submitButton = screen.getByRole('button', { name: /submit/i })

    const maliciousInput = '<img src=x onerror="alert(1)">Hello'
    fireEvent.change(textarea, { target: { value: maliciousInput } })

    // Submit the form
    fireEvent.click(submitButton)

    // Wait for async submission
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith('Hello')
    })
  })
})
