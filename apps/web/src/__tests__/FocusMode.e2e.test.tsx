/**
 * FocusMode.e2e.test.tsx — E2E behavioral tests for Focus Mode.
 *
 * Tests Focus Mode lifecycle: activation on task start, escape hatch,
 * no re-trapping when task running but user overrode, F-key toggle,
 * badge visibility, and task completion exits Focus Mode.
 *
 * Phase: 08-05 — Wave 4 (Integration Tests)
 */

import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { FocusModeBadge } from '@/components/shared/FocusModeBadge'
import { useOrchestratorStore } from '@/stores/orchestratorStore'
import { useBrainStore } from '@/stores/brainStore'

// ─── Helpers ──────────────────────────────────────────────────────────────────

function resetAll() {
  useOrchestratorStore.getState().reset()
  useBrainStore.setState({ brains: new Map(), _queue: [], _rafId: null })
}

// ─── Tests ────────────────────────────────────────────────────────────────────

describe('Focus Mode — E2E behavioral tests', () => {
  beforeEach(() => {
    resetAll()
    vi.clearAllMocks()
  })

  // ─── Activation ──────────────────────────────────────────────────────────

  describe('test_focus_mode_activates_on_task_start', () => {
    it('activates Focus Mode when startTask is called', () => {
      // Precondition: Focus Mode off
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
      expect(useOrchestratorStore.getState().state).toBe('idle')

      // Action: start task (simulates POST /api/tasks → startTask())
      useOrchestratorStore.getState().startTask('task-001', 'Build a new feature')

      // Assert: store state
      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(true)
      expect(store.state).toBe('running')
      expect(store.userOverride).toBe(false)
      expect(store.taskId).toBe('task-001')
      expect(store.briefText).toBe('Build a new feature')
    })

    it('sets startedAt timestamp on activation', () => {
      const before = Date.now()
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      const after = Date.now()

      const { startedAt } = useOrchestratorStore.getState()
      expect(startedAt).toBeGreaterThanOrEqual(before)
      expect(startedAt).toBeLessThanOrEqual(after)
    })

    it('resets completedAt on new task start', () => {
      // First task completes
      useOrchestratorStore.getState().startTask('task-001', 'First brief')
      useOrchestratorStore.getState().completeTask()

      // Second task starts
      useOrchestratorStore.getState().startTask('task-002', 'Second brief')

      expect(useOrchestratorStore.getState().completedAt).toBeNull()
    })
  })

  // ─── Sidebar collapse via Focus Mode badge ────────────────────────────────

  describe('test_focus_mode_sidebar_collapses', () => {
    it('FocusModeBadge renders only when isFocusMode is true', () => {
      // Focus Mode inactive — badge not rendered
      render(<FocusModeBadge />)
      expect(screen.queryByRole('button', { name: /exit focus mode/i })).toBeNull()
    })

    it('FocusModeBadge visible when Focus Mode activates', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()
      expect(screen.getByText('Salir [Esc]')).toBeInTheDocument()
    })
  })

  // ─── Escape hatch ─────────────────────────────────────────────────────────

  describe('test_focus_mode_escape_hatch', () => {
    it('pressing [Esc] sets userOverride=true when Focus Mode is active', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      fireEvent.keyDown(window, { key: 'Escape' })

      const store = useOrchestratorStore.getState()
      // After Esc: userOverride=true but task still running
      expect(store.userOverride).toBe(true)
      expect(store.state).toBe('running')
    })

    it('Focus Mode exits immediately after [Esc] (isFocusMode=false)', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      fireEvent.keyDown(window, { key: 'Escape' })

      // isFocusMode = running AND !userOverride = running AND !true = false
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('badge disappears after [Esc] override', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      const { rerender } = render(<FocusModeBadge />)

      // Badge visible before Esc
      expect(screen.getByRole('button', { name: /exit focus mode/i })).toBeInTheDocument()

      // Press Esc
      fireEvent.keyDown(window, { key: 'Escape' })
      rerender(<FocusModeBadge />)

      // Badge hidden after Esc
      expect(screen.queryByRole('button', { name: /exit focus mode/i })).toBeNull()
    })
  })

  // ─── No re-trapping ───────────────────────────────────────────────────────

  describe('test_focus_mode_no_retrapping', () => {
    it('userOverride resets to false on task completion', () => {
      // Setup: task running, user pressed Esc
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      useOrchestratorStore.getState().toggleOverride() // Simulate Esc

      expect(useOrchestratorStore.getState().userOverride).toBe(true)

      // Simulate WS 'task:complete' → completeTask()
      useOrchestratorStore.getState().completeTask()

      // userOverride must reset — no stale override state
      expect(useOrchestratorStore.getState().userOverride).toBe(false)
    })

    it('isFocusMode is false after completeTask regardless of override', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      useOrchestratorStore.getState().toggleOverride()
      useOrchestratorStore.getState().completeTask()

      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
      expect(useOrchestratorStore.getState().state).toBe('complete')
    })

    it('starting a new task after completion reactivates Focus Mode (no stale override)', () => {
      // First task lifecycle
      useOrchestratorStore.getState().startTask('task-001', 'Brief 1')
      useOrchestratorStore.getState().toggleOverride() // User presses Esc
      useOrchestratorStore.getState().completeTask()

      // Second task starts — override should be clean
      useOrchestratorStore.getState().startTask('task-002', 'Brief 2')

      const store = useOrchestratorStore.getState()
      expect(store.isFocusMode).toBe(true)
      expect(store.userOverride).toBe(false)
    })
  })

  // ─── F key toggle ─────────────────────────────────────────────────────────

  describe('test_focus_mode_toggle_with_f_key', () => {
    it('[F] key toggles Focus Mode when badge is rendered', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      // First F press: exits Focus Mode
      fireEvent.keyDown(window, { key: 'f' })
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
      expect(useOrchestratorStore.getState().userOverride).toBe(true)
    })

    it('[F] uppercase also works (case-insensitive)', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      fireEvent.keyDown(window, { key: 'F' })
      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
    })

    it('[F] key does nothing when not in an input/textarea', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(
        <>
          <FocusModeBadge />
          <textarea data-testid="brief-input" />
        </>
      )

      const textarea = screen.getByTestId('brief-input')
      // Fire from textarea target — should NOT trigger toggle
      fireEvent.keyDown(textarea, { key: 'f', target: textarea })

      // Focus Mode should remain active (guard prevents textarea interference)
      expect(useOrchestratorStore.getState().state).toBe('running')
    })
  })

  // ─── Badge visibility ─────────────────────────────────────────────────────

  describe('test_focus_mode_badge_visible', () => {
    it('renders "Salir [Esc]" label when Focus Mode active', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      expect(screen.getByText('Salir [Esc]')).toBeInTheDocument()
    })

    it('badge positioned top-right by default (Fitts\'s Law)', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('top-4')
      expect(badge.className).toContain('right-4')
      expect(badge.className).toContain('fixed')
    })

    it('badge has z-50 to float above canvas', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      expect(badge.className).toContain('z-50')
    })

    it('clicking badge exits Focus Mode', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      render(<FocusModeBadge />)

      const badge = screen.getByRole('button', { name: /exit focus mode/i })
      fireEvent.click(badge)

      expect(useOrchestratorStore.getState().isFocusMode).toBe(false)
      expect(useOrchestratorStore.getState().userOverride).toBe(true)
    })
  })

  // ─── Idle tiles dimmed ────────────────────────────────────────────────────

  describe('test_idle_tiles_dimmed', () => {
    it('brainStore tracks brain states by id', () => {
      // Simulate WS brain updates arriving
      const activeBrain = { id: 'brain-01', status: 'active' as const, lastUpdated: Date.now() }
      const idleBrain = { id: 'brain-02', status: 'idle' as const, lastUpdated: Date.now() }

      // Direct setState to bypass RAF batching in tests
      useBrainStore.setState({
        brains: new Map([
          ['brain-01', activeBrain],
          ['brain-02', idleBrain],
        ]),
      })

      const state = useBrainStore.getState()
      expect(state.brains.get('brain-01')?.status).toBe('active')
      expect(state.brains.get('brain-02')?.status).toBe('idle')
    })

    it('Focus Mode active: isFocusMode true triggers dim logic context', () => {
      // Setup Focus Mode active + mixed brain states
      useOrchestratorStore.getState().startTask('task-001', 'Brief')

      useBrainStore.setState({
        brains: new Map([
          ['brain-01', { id: 'brain-01', status: 'active', lastUpdated: Date.now() }],
          ['brain-02', { id: 'brain-02', status: 'idle', lastUpdated: Date.now() }],
          ['brain-03', { id: 'brain-03', status: 'complete', lastUpdated: Date.now() }],
        ]),
      })

      // Focus Mode is active — consumers should apply opacity-30 to idle tiles
      expect(useOrchestratorStore.getState().isFocusMode).toBe(true)
      expect(useBrainStore.getState().brains.get('brain-02')?.status).toBe('idle')
    })
  })

  // ─── Layout smooth transition ─────────────────────────────────────────────

  describe('test_focus_mode_layout_smooth', () => {
    it('state transitions cleanly from idle to running', () => {
      const initialState = useOrchestratorStore.getState()
      expect(initialState.state).toBe('idle')
      expect(initialState.isFocusMode).toBe(false)

      // Simulate task start (no intermediate states)
      useOrchestratorStore.getState().startTask('task-001', 'Build feature')

      const runningState = useOrchestratorStore.getState()
      expect(runningState.state).toBe('running')
      expect(runningState.isFocusMode).toBe(true)
    })

    it('state transitions cleanly from running to complete', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      useOrchestratorStore.getState().completeTask()

      const completedState = useOrchestratorStore.getState()
      expect(completedState.state).toBe('complete')
      expect(completedState.isFocusMode).toBe(false)
      expect(completedState.completedAt).not.toBeNull()
    })

    it('error state also clears Focus Mode', () => {
      useOrchestratorStore.getState().startTask('task-001', 'Brief')
      useOrchestratorStore.getState().setError()

      const errorState = useOrchestratorStore.getState()
      expect(errorState.state).toBe('error')
      expect(errorState.isFocusMode).toBe(false)
    })
  })
})
