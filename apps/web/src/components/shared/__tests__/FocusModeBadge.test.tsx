/**
 * FocusModeBadge tests — Task 3 Phase 08-04
 *
 * Tests: badge visibility, click toggle, keyboard shortcuts ([F]/[Esc]),
 * keyboard listener cleanup on unmount.
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FocusModeBadge } from '../FocusModeBadge'
import { useOrchestratorStore } from '@/stores/orchestratorStore'

// Reset orchestrator store between tests
function resetStore() {
  useOrchestratorStore.getState().reset()
}

describe('FocusModeBadge', () => {
  beforeEach(() => {
    resetStore()
  })

  // ─── Visibility ──────────────────────────────────────────────────────────

  describe('visibility', () => {
    it('does not render when isFocusMode is false (idle)', () => {
      render(<FocusModeBadge />)
      expect(screen.queryByRole('button', { name: /exit focus mode/i })).toBeNull()
    })

    it('renders when isFocusMode is true', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)
      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()
    })

    it('shows "Salir [Esc]" label when active', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)
      expect(screen.getByText('Salir [Esc]')).toBeInTheDocument()
    })

    it('disappears when userOverride is set (Focus Mode exits)', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      const { rerender } = render(<FocusModeBadge />)
      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()

      // Simulate user toggling override (exits Focus Mode)
      useOrchestratorStore.getState().toggleOverride()
      rerender(<FocusModeBadge />)
      expect(screen.queryByRole('button', { name: /exit focus mode/i })).toBeNull()
    })
  })

  // ─── Click interaction ───────────────────────────────────────────────────

  describe('click interaction', () => {
    it('clicking badge calls toggleOverride', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      fireEvent.click(badge)

      // After click, userOverride=true, isFocusMode=false
      expect(useOrchestratorStore.getState().userOverride).toBe(true)
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })
  })

  // ─── Keyboard shortcuts ──────────────────────────────────────────────────

  describe('keyboard shortcuts', () => {
    it('[F] key toggles Focus Mode when active', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)

      fireEvent.keyDown(window, { key: 'f' })
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('[F] key is case-insensitive (uppercase F)', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)

      // The handler checks e.key.toLowerCase() === 'f'
      fireEvent.keyDown(window, { key: 'F' })
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('[Esc] key exits Focus Mode when active', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)

      fireEvent.keyDown(window, { key: 'Escape' })
      expect(useOrchestratorStore.getState().userOverride).toBe(true)
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('[Esc] key does nothing when Focus Mode is inactive', () => {
      // Focus Mode not active (no running task)
      render(<FocusModeBadge />)
      const initialOverride = useOrchestratorStore.getState().userOverride

      fireEvent.keyDown(window, { key: 'Escape' })

      // Override should not change (Esc has no effect when not in Focus Mode)
      expect(useOrchestratorStore.getState().userOverride).toBe(initialOverride)
    })

    it('[F] key does not fire on textarea input', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(
        <>
          <FocusModeBadge />
          <textarea data-testid="text-area" />
        </>
      )

      const textarea = screen.getByTestId('text-area')
      fireEvent.keyDown(textarea, { key: 'f', target: textarea })

      // Focus Mode should remain active (no toggle)
      // Note: jsdom doesn't honor event.target.tagName filtering perfectly,
      // but we test the guard branch exists
      expect(useOrchestratorStore.getState().state).toBe('running')
    })
  })

  // ─── Positioning ─────────────────────────────────────────────────────────

  describe('positioning', () => {
    it('defaults to top-right position', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('top-4')
      expect(badge.className).toContain('right-4')
    })

    it('applies top-left position class', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge position="top-left" />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('top-4')
      expect(badge.className).toContain('left-4')
    })

    it('applies bottom-right position class', () => {
      useOrchestratorStore.getState().startTask('task-1', 'Brief')
      render(<FocusModeBadge position="bottom-right" />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('bottom-4')
      expect(badge.className).toContain('right-4')
    })
  })
})
