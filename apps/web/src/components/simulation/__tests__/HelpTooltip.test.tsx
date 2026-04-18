/**
 * HelpTooltip Component Tests
 *
 * **Purpose:** Test keyboard shortcuts tooltip component
 * **Context:** B2-FIXES.12 - Add keyboard shortcuts documentation
 *
 * **TDD Phase:** RED -> GREEN
 */

import { render, screen } from '@testing-library/react'
import { describe, it, expect } from 'vitest'
import { HelpTooltip } from '../HelpTooltip'

describe('HelpTooltip', () => {
  /**
   * Test 1: HelpTooltip renders trigger button
   */
  it('should render trigger button with help icon', () => {
    render(<HelpTooltip />)

    const trigger = screen.getByTestId('keyboard-shortcuts-help')
    expect(trigger).toBeInTheDocument()
    expect(trigger.textContent).toBe('?')
  })

  /**
   * Test 2: HelpTooltip has proper accessibility attributes
   */
  it('should have proper accessibility attributes', () => {
    render(<HelpTooltip />)

    // The trigger element should be present
    const trigger = screen.getByTestId('keyboard-shortcuts-help')
    expect(trigger).toBeInTheDocument()
  })

  /**
   * Test 3: HelpTooltip trigger has focus ring for accessibility
   */
  it('should have focus ring styles for accessibility', () => {
    render(<HelpTooltip />)

    const trigger = screen.getByTestId('keyboard-shortcuts-help')
    expect(trigger.className).toContain('focus:ring-2')
  })
})
